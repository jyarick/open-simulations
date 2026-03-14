# helpers/transform.py
import numpy as np


def transform_data_using_params(
    data,
    params,
    minutes_per_step=15,
    rng=None,
    gaussian_filter1d=None
):
    """
    Apply parameter transformations to a daily data array (kWh per interval).

    Returns a same-length array, clipped to >= 0.
    """
    x = np.asarray(data, dtype=float)
    y = x.copy()

    # --- validate timestep geometry (prevents silent weighting bugs) ---
    m = int(minutes_per_step)
    if m <= 0:
        raise ValueError("minutes_per_step must be positive.")
    if 60 % m != 0:
        raise ValueError(f"minutes_per_step={m} must evenly divide 60 for hourly weighting.")
    points_per_hour = 60 // m
    expected_len = 24 * points_per_hour
    if len(y) != expected_len:
        raise ValueError(
            f"Expected a full-day array of length {expected_len} for minutes_per_step={m}, "
            f"but got len(data)={len(y)}."
        )

    # 1) scale + shift
    y = y * float(params.get("scale", 1.0)) + float(params.get("shift", 0.0))

    # 2) noise (relative to magnitude)
    noise_level = float(params.get("noise", 0.0))
    if noise_level > 0:
        mag = float(np.mean(np.abs(y))) + 1e-12
        if rng is None:
            y = y + np.random.normal(0.0, noise_level * mag, size=len(y))
        else:
            y = y + rng.normal(0.0, noise_level * mag, size=len(y))

    # 3) deviation about mean
    f = float(params.get("f", 1.0))
    mu = float(np.mean(y))
    y = mu + (y - mu) * f

    # 4) hourly weights
    tw = params.get("time_weights", [1.0] * 24)
    y2 = y.copy()
    for hour in range(24):
        w = float(tw[hour]) if hour < len(tw) else 1.0
        s = hour * points_per_hour
        e = s + points_per_hour
        y2[s:e] *= w
    y = y2

    # 5) smoothing (optional)
    sigma = int(params.get("smooth", 0))
    if sigma > 0:
        if gaussian_filter1d is None:
            raise ImportError(
                "Smoothing requested (smooth>0) but gaussian_filter1d not provided. "
                "Pass scipy.ndimage.gaussian_filter1d."
            )
        y = gaussian_filter1d(y, sigma=sigma)

    # 6) circular time shift
    shift_steps = int(params.get("time_shift", 0))
    if shift_steps != 0:
        y = np.roll(y, shift_steps)

    # 7) clip once at the end
    y = np.clip(y, 0.0, None)

    return y
