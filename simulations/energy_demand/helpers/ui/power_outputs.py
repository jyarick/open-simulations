# helpers/ui/power_outputs.py

import os
import tempfile
from pathlib import Path

import IPython.display as ipd
import pandas as pd
import numpy as np

from helpers.metrics import build_power_dataframe, max_power_summary_table
from helpers.tools import export_power_excel
from helpers.render import save_dataframe_as_png


def _display_dataframe_as_matplotlib_table(df, body_font_size=10, header_font_size=11):
    """
    Display a matplotlib-rendered table (NOT pandas Styler).
    This is for display-mode only (no file dependency).
    """
    import matplotlib.pyplot as plt

    df_disp = df.copy()
    for c in df_disp.columns:
        df_disp[c] = df_disp[c].astype(str)

    n_rows, n_cols = df_disp.shape
    fig_w = max(12, 1.9 * n_cols)
    fig_h = max(3.0, 0.5 * (n_rows + 1))

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.axis("off")

    table = ax.table(
        cellText=df_disp.values,
        colLabels=df_disp.columns,
        cellLoc="center",
        loc="center",
    )

    table.auto_set_font_size(False)
    table.set_fontsize(body_font_size)
    table.scale(1.15, 1.35)

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight="bold", fontsize=header_font_size)
            cell.set_height(cell.get_height() * 1.4)

    plt.show()
    plt.close(fig)


def _hr_title():
    ipd.display(ipd.HTML("<hr style='margin:14px 0;'>"))
    ipd.display(ipd.HTML(
        "<div style='color:#666; font-size:13px; margin:0px 0 10px 0;'>"
        "<b>Max power summary</b></div>"
    ))


def run_power_outputs(
    state,
    all_users,
    start_time,
    end_time,
    minutes_per_step=15,
    excel_filename="act4_power.xlsx",
    table_png="max_power_table.png",
    export=False,                 # side effects only when requested
    show_saved_messages=True,     # only matters if export=True
    display_table=False,          # pandas table
    display_png=True              # display-mode: matplotlib table; export-mode: saved PNG
):
    """
    Behavior you want:

    Display mode (export=False):
      - Shows the matplotlib table (NO file dependency).
      - Does NOT write PNG/Excel.

    Export mode (export=True):
      - Writes Excel + PNG to deterministic path.
      - Displays the saved PNG (and never crashes if missing).
      - Shows ✅ Saved messages under the PNG.
    """

    # ---- Build df_power (silent) ----
    df_power = build_power_dataframe(
        all_users=all_users,
        modified_data=state.modified_data,
        counts=state.counts,
        start_time=start_time,
        end_time=end_time,
        minutes_per_step=minutes_per_step,
    )

    # ---- Summary table (silent) ----
    max_table = max_power_summary_table(
        df_power,
        list(state.modified_data.keys()),
        total_col="Total Grid",
    ).copy()

    # Numeric rounding without FutureWarning
    for c in max_table.columns:
        if c in ("Time of Max", "User"):
            continue
        try:
            max_table[c] = pd.to_numeric(max_table[c]).astype(float).round(2)
        except Exception:
            pass

    # ---- Optional pandas display (usually OFF) ----
    if display_table:
        _hr_title()

        def _fmt2(x):
            if isinstance(x, (int, float, np.number)) and not (isinstance(x, float) and np.isnan(x)):
                return f"{float(x):.2f}"
            return x

        sty = (
            max_table.style
                .format(_fmt2, subset=[c for c in max_table.columns if c not in ("Time of Max", "User")])
                .set_properties(**{"text-align": "center"})
                .set_table_styles([
                    {"selector": "th", "props": [("text-align", "center")]},
                    {"selector": "td", "props": [("text-align", "center")]},
                ])
        )
        ipd.display(sty)

    # ---- EXPORT MODE ----
    if export:
        export_power_excel(df_power, excel_filename)

        # Deterministic path: always save into current working directory unless absolute path supplied
        png_path = Path(table_png).expanduser()
        if not png_path.is_absolute():
            png_path = Path.cwd() / png_path
        png_path.parent.mkdir(parents=True, exist_ok=True)

        # Save PNG
        save_dataframe_as_png(max_table, filename=str(png_path), dpi=300)

        # Display: never crash
        if display_png:
            _hr_title()
            if png_path.exists():
                ipd.display(ipd.Image(filename=str(png_path)))
            else:
                # Fallback: generate a temp PNG just to display (export still attempted)
                fd, tmp_path = tempfile.mkstemp(prefix="max_power_table_", suffix=".png")
                os.close(fd)
                save_dataframe_as_png(max_table, filename=tmp_path, dpi=300)
                ipd.display(ipd.Image(filename=tmp_path))

        if show_saved_messages:
            ipd.display(ipd.HTML(
                f"<div style='color:green; margin-top:6px;'><b>✅ Saved:</b> <code>{png_path.name}</code></div>"
            ))
            ipd.display(ipd.HTML(
                f"<div style='color:green; margin-top:4px;'><b>✅ Saved:</b> <code>{excel_filename}</code></div>"
            ))

        return df_power, max_table

    # ---- DISPLAY MODE (NO EXPORT) ----
    if display_png:
        _hr_title()
        _display_dataframe_as_matplotlib_table(max_table)

    return df_power, max_table


def export_power_outputs(
    state,
    all_users,
    start_time,
    end_time,
    minutes_per_step=15,
    excel_filename="act4_power.xlsx",
    table_png="max_power_table.png",
):
    """
    Save-only power outputs (NO display side effects).
    Writes:
      - Excel df_power
      - PNG max-power summary table
    """
    df_power = build_power_dataframe(
        all_users=all_users,
        modified_data=state.modified_data,
        counts=state.counts,
        start_time=start_time,
        end_time=end_time,
        minutes_per_step=minutes_per_step,
    )

    max_table = max_power_summary_table(
        df_power,
        list(state.modified_data.keys()),
        total_col="Total Grid",
    ).copy()

    for c in max_table.columns:
        if c in ("Time of Max", "User"):
            continue
        try:
            max_table[c] = pd.to_numeric(max_table[c]).astype(float).round(2)
        except Exception:
            pass

    export_power_excel(df_power, excel_filename)

    png_path = Path(table_png).expanduser()
    if not png_path.is_absolute():
        png_path = Path.cwd() / png_path
    png_path.parent.mkdir(parents=True, exist_ok=True)

    save_dataframe_as_png(max_table, filename=str(png_path), dpi=300)

    return df_power, max_table
