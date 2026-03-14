# helpers/data.py

from pathlib import Path
import pandas as pd


DEFAULT_USER_MAP = {
    "Hospital": "hospital",
    "Full Service Restaurant": "restaurant",
    "Medical Clinic": "clinic",
    "Hotel": "hotel",
    "Commercial Office Building": "commercial_office",
    "K12 School": "k12_school",
    "Grocery Store": "grocery",
    "Fast Food Restaurant": "fast_food",
    "Post Office": "post_office",
    "College Campus": "college",
    "Shopping Mall": "shopping_mall",
    "Library": "library",
    "Warehouse": "warehouse",
    "Police Station": "police_station",
    "Fitness Center": "fitness_center",
    "Bus Station": "bus_station",
    "Fire Station": "fire_station",
    "Gas Station": "gas_station",
    "Movie Theater": "movie_theater",
}


def load_all_users_energy_csv(data_path="all_users_energy.csv"):
    """
    Load the all_users_energy CSV (expected next to the notebook).
    """
    data_path = Path(data_path)
    if not data_path.exists():
        raise FileNotFoundError(
            f"Could not find {data_path}. Put the CSV in the same folder as this notebook."
        )
    return pd.read_csv(data_path)


def validate_user_map(all_users, user_map):
    """
    Validate that all expected '<prefix>_kWh' columns exist.
    """
    expected_cols = [f"{k}_kWh" for k in user_map.values()]
    missing_cols = [c for c in expected_cols if c not in all_users.columns]

    if missing_cols:
        kwh_cols = [c for c in all_users.columns if c.endswith("_kWh")]
        raise ValueError(
            f"CSV missing expected columns: {missing_cols}\n\n"
            f"Available *_kWh columns:\n{kwh_cols}"
        )


def select_day_window(all_users, start_time, points_per_day=96):
    """
    Slice a 24-hour window (default 96 points at 15-min resolution).
    Returns (window, end_time).
    """
    end_time = int(start_time) + int(points_per_day)
    window = all_users.iloc[int(start_time):int(end_time)].copy()

    if len(window) != int(points_per_day):
        raise ValueError(
            f"Window length must be {points_per_day} rows. Got {len(window)} rows. "
            f"Check start_time/end_time."
        )

    return window, end_time


def load_energy_data_bundle(
    data_path="all_users_energy.csv",
    start_time=6048,
    points_per_day=96,
    user_map=None,
):
    """
    One-call loader used by the notebook.
    Returns: all_users, window, start_time, end_time, user_map
    """
    all_users = load_all_users_energy_csv(data_path)
    user_map = DEFAULT_USER_MAP if user_map is None else user_map
    validate_user_map(all_users, user_map)
    window, end_time = select_day_window(all_users, start_time, points_per_day=points_per_day)
    return all_users, window, int(start_time), int(end_time), user_map
