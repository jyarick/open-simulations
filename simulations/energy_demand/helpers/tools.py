# helpers/tools.py
import numpy as np


def solve_scale_shift(E0_min, E0_max, E1_min, E1_max):
    """Solve (a, b) in E1 = a*E0 + b using two endpoints."""
    E0_min = float(E0_min)
    E0_max = float(E0_max)
    E1_min = float(E1_min)
    E1_max = float(E1_max)

    if np.isclose(E0_max, E0_min):
        raise ValueError("E_0_max and E_0_min are equal — division by zero.")

    a = (E1_max - E1_min) / (E0_max - E0_min)
    b = E1_min - a * E0_min
    return a, b


# ---------------------------------------------------------------------
# Time-step utilities
# ---------------------------------------------------------------------

MINUTES_PER_STEP_DEFAULT = 15


def steps_per_day(minutes_per_step=MINUTES_PER_STEP_DEFAULT):
    """Return number of timesteps in a 24-hour day (requires 1440 divisible)."""
    m = int(minutes_per_step)
    if m <= 0:
        raise ValueError("minutes_per_step must be positive.")
    if 1440 % m != 0:
        raise ValueError(f"minutes_per_step={m} does not evenly divide 1440 minutes/day.")
    return 1440 // m


def step_hours(minutes_per_step=MINUTES_PER_STEP_DEFAULT):
    """Return timestep duration in hours."""
    return float(minutes_per_step) / 60.0


def interval_kwh_to_avg_kw(E_kwh, minutes_per_step=MINUTES_PER_STEP_DEFAULT):
    """Convert interval energy (kWh per timestep) to average power (kW)."""
    dt_hr = float(minutes_per_step) / 60.0
    return np.asarray(E_kwh) / dt_hr


# ---------------------------------------------------------------------
# Array safety helpers
# ---------------------------------------------------------------------

def clip_nonnegative(arr):
    """Enforce physical non-negativity."""
    a = np.asarray(arr)
    return np.maximum(a, 0.0)


def validate_no_nan_or_inf(arr, name="array"):
    """Raise if array contains NaN or infinite values."""
    a = np.asarray(arr)
    if not np.isfinite(a).all():
        raise ValueError(f"{name} contains NaN or Inf.")


# ---------------------------------------------------------------------
# Randomness utilities
# ---------------------------------------------------------------------

def get_rng(seed=None, locked=False):
    """
    RNG factory.

    - locked=True and seed provided -> deterministic RNG seeded with `seed`
    - otherwise -> fresh RNG (non-deterministic) each call
    """
    if locked and seed is not None:
        return np.random.default_rng(int(seed))
    return np.random.default_rng()


# ---------------------------------------------------------------------
# Time-domain operations
# ---------------------------------------------------------------------

def circular_shift(arr, shift_steps):
    """Circularly shift an array by an integer number of timesteps."""
    a = np.asarray(arr)
    if len(a) == 0:
        return a
    s = int(shift_steps) % len(a)
    return np.roll(a, s)


# ---------------------------------------------------------------------
# Export helpers
# ---------------------------------------------------------------------

def export_power_excel(df_power, filename="act4_power.xlsx"):
    """Export the Activity 4 power dataframe to an Excel file."""
    import pandas as pd

    if df_power is None:
        raise ValueError("df_power is None")
    if not hasattr(df_power, "to_excel"):
        raise TypeError("df_power must be a pandas DataFrame")

    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        df_power.to_excel(writer, index=False, sheet_name="power_kW")
