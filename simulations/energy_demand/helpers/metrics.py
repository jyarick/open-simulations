# helpers/metrics.py

import pandas as pd
import numpy as np


def build_power_dataframe(
    all_users,
    modified_data,
    counts,
    start_time,
    end_time,
    minutes_per_step=15
):
    """
    Build df_power with per-user kW and Total Grid.
    Silent (no prints).
    """

    df_power = pd.DataFrame({
        "time": all_users["time"].astype(str).str[-5:].iloc[start_time:end_time].reset_index(drop=True)
    })

    time_interval_hr = minutes_per_step / 60.0  # 15 min -> 0.25 hr

    for user_name, user_energy in modified_data.items():
        n_buildings = int(counts.get(user_name, 1))
        arr = np.asarray(user_energy, dtype=float)
        df_power[user_name] = n_buildings * (arr / time_interval_hr)

    user_cols = [c for c in df_power.columns if c != "time"]
    if not user_cols:
        raise ValueError("No user power data available to compute Total Grid.")

    df_power["Total Grid"] = df_power[user_cols].sum(axis=1)
    return df_power


def max_power_summary_table(df_power, user_names, total_col="Total Grid"):
    """
    Build the max-power summary table (time of peak + kW + % of total-grid peak).
    Used by helpers.ui.power_outputs import max_power_summary_table.
    """
    cols = list(user_names) + [total_col]

    missing = [c for c in cols if c not in df_power.columns]
    if missing:
        raise KeyError(f"Missing columns in df_power: {missing}")

    long = (
        df_power[["time"] + cols]
        .melt(id_vars="time", var_name="User", value_name="Power_kW")
        .dropna(subset=["Power_kW"])
    )

    idx = long.groupby("User", sort=False)["Power_kW"].idxmax()
    summary = long.loc[idx].copy()

    tg_rows = summary[summary["User"] == total_col]
    if tg_rows.empty:
        raise ValueError(f"Could not find '{total_col}' peak row. Check df_power generation.")

    max_total_power = float(tg_rows["Power_kW"].iloc[0])
    if max_total_power <= 0:
        raise ValueError(f"'{total_col}' peak is {max_total_power:.3f} kW; cannot compute percentages.")

    summary["Percent_of_TotalGrid_Peak"] = 100.0 * summary["Power_kW"] / max_total_power

    out = (
        summary.rename(columns={"time": "Time of Max", "Power_kW": "Max Power Usage (kW)"})
        .sort_values("Percent_of_TotalGrid_Peak", ascending=False)
        .reset_index(drop=True)
    )

    out["Max Power Usage (kW)"] = out["Max Power Usage (kW)"].round(2)
    out["Percent_of_TotalGrid_Peak"] = out["Percent_of_TotalGrid_Peak"].round(2)
    out = out.rename(columns={"Percent_of_TotalGrid_Peak": "Percent Max Total Power (%)"})
    return out
