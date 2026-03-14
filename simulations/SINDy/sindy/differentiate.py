import numpy as np
from scipy.signal import savgol_filter


def finite_difference(t, y):
    """
    Estimate dy/dt from time-series data using numpy.gradient.

    Parameters
    ----------
    t : array-like, shape (n_samples,)
        Time values.
    y : array-like, shape (n_samples,) or (n_samples, n_features)
        State values.

    Returns
    -------
    dydt : ndarray, same shape as y
        Estimated time derivative.
    """
    t = np.asarray(t)
    y = np.asarray(y)

    if y.ndim == 1:
        return np.gradient(y, t)

    dydt = np.zeros_like(y, dtype=float)
    for i in range(y.shape[1]):
        dydt[:, i] = np.gradient(y[:, i], t)

    return dydt


def savgol_derivative(t, y, window_length=11, polyorder=3):
    """
    Estimate dy/dt using Savitzky-Golay smoothing + derivative.

    Fits a polynomial in each sliding window and returns its derivative at the
    center point, giving smoothed derivatives that are robust to noise.

    Notes
    -----
    Assumes the time array ``t`` is uniformly spaced (e.g. as produced by
    ``solve_ivp(..., t_eval=np.linspace(...))``). Non-uniform ``t`` will
    give incorrect derivative scaling.

    Parameters
    ----------
    t : array-like, shape (n_samples,)
        Time values (used for spacing; uniform spacing assumed for delta).
    y : array-like, shape (n_samples,) or (n_samples, n_states)
        State values.
    window_length : int
        Length of the filter window (must be odd, > polyorder).
    polyorder : int
        Order of the polynomial used to fit the samples.

    Returns
    -------
    dydt : ndarray, same shape as y
        Smoothed time derivative estimate.
    """
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)

    if t.size < window_length:
        raise ValueError(
            f"Need at least window_length={window_length} samples, got {t.size}"
        )
    if window_length % 2 == 0:
        raise ValueError("window_length must be odd")
    if polyorder >= window_length:
        raise ValueError("polyorder must be less than window_length")

    # uniform spacing for derivative scaling
    dt = (t[-1] - t[0]) / (len(t) - 1) if len(t) > 1 else 1.0

    if y.ndim == 1:
        return savgol_filter(y, window_length, polyorder, deriv=1, delta=dt)

    dydt = np.zeros_like(y, dtype=float)
    for i in range(y.shape[1]):
        dydt[:, i] = savgol_filter(
            y[:, i], window_length, polyorder, deriv=1, delta=dt
        )
    return dydt


def estimate_derivative(t, y, method="savgol", **kwargs):
    """
    Estimate dy/dt from time-series data.

    Dispatches to finite_difference or savgol_derivative. Use this in
    experiments to easily switch derivative methods.

    Parameters
    ----------
    t : array-like, shape (n_samples,)
        Time values.
    y : array-like, shape (n_samples,) or (n_samples, n_states)
        State values.
    method : str
        "finite_difference" or "savgol". Default "savgol".
    **kwargs
        Passed to savgol_derivative: window_length, polyorder (ignored for
        finite_difference).

    Returns
    -------
    dydt : ndarray, same shape as y
        Estimated time derivative.
    """
    if method == "finite_difference":
        return finite_difference(t, y)
    if method == "savgol":
        return savgol_derivative(t, y, **kwargs)
    raise ValueError(f"method must be 'finite_difference' or 'savgol', got {method!r}")