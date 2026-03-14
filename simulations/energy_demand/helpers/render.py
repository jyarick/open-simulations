# helpers/render.py

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker


def save_dataframe_as_png(
    df,
    filename="max_power_table.png",
    dpi=300,
    body_font_size=10,
    header_font_size=11
):
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
        loc="center"
    )

    table.auto_set_font_size(False)
    table.set_fontsize(body_font_size)
    table.scale(1.15, 1.35)

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight="bold", fontsize=header_font_size)
            cell.set_height(cell.get_height() * 1.4)

    from pathlib import Path
    
    p = Path(filename)
    p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(p), bbox_inches="tight", dpi=dpi)

    plt.close(fig)


# ---------------------------------------------------------------------
# Styling helpers
# ---------------------------------------------------------------------

def add_day_night_bands(ax, minutes_per_step=15):
    step_per_hour = int(60 / minutes_per_step)
    ax.axvspan(0, 6 * step_per_hour, alpha=0.08)                   # night
    ax.axvspan(18 * step_per_hour, 24 * step_per_hour, alpha=0.08) # evening


def format_y_units(ax, unit="kWh", decimals=2, max_ticks=6):
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:.{decimals}f} {unit}"))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(max_ticks))


def format_x_day(ax, points_per_day=96, minutes_per_step=15, tick_hours=4, show_24=False):
    step_per_hour = int(60 / minutes_per_step)
    tick_every = tick_hours * step_per_hour

    max_tick = points_per_day if show_24 else points_per_day - 1
    x_ticks = np.arange(0, max_tick + 1, tick_every)

    ax.set_xticks(x_ticks)

    labels = []
    for x in x_ticks:
        hour = int(x / step_per_hour)
        if show_24 and x == points_per_day:
            labels.append("24:00")
        else:
            labels.append(f"{hour}:00")
    ax.set_xticklabels(labels)

    ax.set_xlim(0, points_per_day if show_24 else points_per_day - 1)


# ---------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------

def plot_profiles_grid(
    profiles_dict,
    title="Modified Daily Energy Profiles for Power Users",
    unit="kWh",
    points_per_day=96,
    minutes_per_step=15,
    cols=3,
    figsize_per_row=(20, 4.4),
    dpi=120,
    savepath=None,
    color=None,
    linewidth=2.5,
    decimals=2,
    max_ticks=6,
    tick_hours=4,
    show_24=False
):
    """
    Energy profile grid plotter.
    Fix: prevent suptitle overlap when there is only 1 row.
    """
    if not profiles_dict:
        return

    names = list(profiles_dict.keys())
    n_plots = len(names)

    n_rows = (n_plots + cols - 1) // cols
    time_range = np.arange(points_per_day)

    fig, ax = plt.subplots(
        n_rows, cols,
        figsize=(figsize_per_row[0], figsize_per_row[1] * n_rows),
        constrained_layout=False,
        dpi=dpi
    )
    ax = np.array(ax).reshape(-1)

    for i, name in enumerate(names):
        ax_i = ax[i]
        y = np.asarray(profiles_dict[name], dtype=float)

        add_day_night_bands(ax_i, minutes_per_step=minutes_per_step)
        ax_i.plot(time_range[:len(y)], y, linewidth=linewidth, color=color)
        ax_i.set_title(name, fontsize=16, fontweight="bold")

        format_y_units(ax_i, unit=unit, decimals=decimals, max_ticks=max_ticks)
        format_x_day(
            ax_i,
            points_per_day=points_per_day,
            minutes_per_step=minutes_per_step,
            tick_hours=tick_hours,
            show_24=show_24
        )
        ax_i.grid(True, alpha=0.12)

    for j in range(n_plots, len(ax)):
        fig.delaxes(ax[j])

    fig.suptitle(title, fontsize=28, fontweight="bold")

    # fix spacing when only one row
    top = 0.78 if n_rows == 1 else 0.90
    fig.subplots_adjust(top=top, hspace=0.55, wspace=0.25)

    if savepath:
        fig.savefig(savepath, bbox_inches="tight", dpi=180)

    plt.show()


def plot_power_profiles_grid(
    df_power,
    user_names,
    title="Daily Power Consumption (kW) for User Types & Total Grid",
    total_col="Total Grid",
    points_per_day=96,
    minutes_per_step=15,
    cols=3,
    figsize_per_row=(20, 4.4),
    dpi=120,
    savepath=None,
    linewidth=2.5,
    decimals=2,
    max_ticks=6,
    tick_hours=4,
    show_24=True,
    scaled_users=True,
    pad_frac=0.05,
    add_day_night_bands=None,
    format_x_day=None
):
    """
    Power profile grid plotter.
    Fix: prevent suptitle overlap when there is only 1 row.
    """
    
    # --- Ensure power plots use the SAME axis formatting as energy plots ---
    if add_day_night_bands is None:
        from helpers.render import add_day_night_bands as add_day_night_bands

    if format_x_day is None:
        from helpers.render import format_x_day as format_x_day

    
    def format_y_power(ax, decimals=2, max_ticks=6):
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:.{decimals}f} kW"))
        ax.yaxis.set_major_locator(ticker.MaxNLocator(max_ticks))

    user_names = [u for u in list(user_names) if u in df_power.columns and u != total_col]
    titles = user_names + ([total_col] if total_col in df_power.columns else [])
    if not titles:
        raise ValueError("No valid power columns found to plot.")

    n_plots = len(titles)
    n_rows = (n_plots + cols - 1) // cols
    time_range = np.arange(points_per_day)

    fig, ax = plt.subplots(
        n_rows, cols,
        figsize=(figsize_per_row[0], figsize_per_row[1] * n_rows),
        constrained_layout=False,
        dpi=dpi
    )
    ax = np.array(ax).reshape(-1)

    user_ylim_global = None
    if user_names:
        max_user = np.nanmax(df_power[user_names].to_numpy(dtype=float))
        user_ylim_global = (1 + pad_frac) * max_user

    grid_ylim = None
    if total_col in df_power.columns:
        max_grid = np.nanmax(df_power[total_col].to_numpy(dtype=float))
        grid_ylim = (1 + pad_frac) * max_grid

    for i, name in enumerate(titles):
        ax_i = ax[i]
        y = np.asarray(df_power[name].to_numpy(dtype=float), dtype=float)

        if add_day_night_bands is not None:
            add_day_night_bands(ax_i, minutes_per_step=minutes_per_step)

        ax_i.plot(time_range[:len(y)], y, linewidth=linewidth)
        ax_i.set_title(name, fontsize=16, fontweight="bold")

        format_y_power(ax_i, decimals=decimals, max_ticks=max_ticks)

        if format_x_day is not None:
            format_x_day(
                ax_i,
                points_per_day=points_per_day,
                minutes_per_step=minutes_per_step,
                tick_hours=tick_hours,
                show_24=show_24
            )

        ax_i.grid(True, alpha=0.12)

        if name == total_col and grid_ylim and np.isfinite(grid_ylim) and grid_ylim > 0:
            ax_i.set_ylim(0, grid_ylim)
        elif name != total_col:
            if scaled_users and user_ylim_global and np.isfinite(user_ylim_global) and user_ylim_global > 0:
                ax_i.set_ylim(0, user_ylim_global)
            else:
                ymax = (1 + pad_frac) * np.nanmax(y)
                if np.isfinite(ymax) and ymax > 0:
                    ax_i.set_ylim(0, ymax)

    for j in range(n_plots, len(ax)):
        fig.delaxes(ax[j])

    fig.suptitle(title, fontsize=28, fontweight="bold")

    # fix spacing when only one row
    top = 0.78 if n_rows == 1 else 0.90
    fig.subplots_adjust(top=top, hspace=0.55, wspace=0.25)

    if savepath:
        fig.savefig(savepath, bbox_inches="tight", dpi=180)

    plt.show()
