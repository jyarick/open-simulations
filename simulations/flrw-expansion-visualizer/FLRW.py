#!/usr/bin/env python3
"""
FLRW Expansion Visualizer (v1.5)

Adds:
- Photon as a Gaussian wave packet (localized pulse), not an infinite sine wave.
- Packet wavelength stretches: lambda_phys(t) = a(t) * lambda0
- Packet width also stretches with expansion (comoving width fixed):
    sigma_phys(t) = a(t) * sigma0
- Wave readout box is placed top-right and packet is kept away from it.

Controls:
- space: pause/play
- r: reset
- c: toggle physical <-> comoving view
- h: toggle Hubble radius circle
- p: flip packet travel direction
- q/esc: quit
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--omega_m", type=float, default=None,
                   help="Matter density parameter Omega_m in [0,1] (flat enforced). Example: 0.3")
    p.add_argument("--fps", type=float, default=30.0)
    p.add_argument("--frames", type=int, default=900)
    p.add_argument("--a_min", type=float, default=0.2)
    p.add_argument("--a_max", type=float, default=2.0)

    # galaxies
    p.add_argument("--n_gal", type=int, default=450, help="Number of galaxies (random comoving points).")
    p.add_argument("--seed", type=int, default=7, help="Random seed for reproducibility.")
    p.add_argument("--box", type=float, default=2.0,
                   help="Half-size of comoving galaxy box: galaxies uniform in [-box, box]^2.")

    # photon wave packet
    p.add_argument("--lambda0", type=float, default=0.35,
                   help="Comoving wavelength scale (lambda_phys = a * lambda0).")
    p.add_argument("--packet_amp", type=float, default=0.80,
                   help="Wave packet amplitude in wave-axis units.")
    p.add_argument("--sigma0", type=float, default=0.55,
                   help="Comoving packet width (sigma_phys = a * sigma0).")
    p.add_argument("--packet_speed", type=float, default=0.65,
                   help="Packet center speed in physical x units per second (visual).")
    p.add_argument("--carrier_speed", type=float, default=2.5,
                   help="Carrier phase speed multiplier (visual).")
    return p.parse_args()


def get_omega_m(cli_value):
    if cli_value is not None:
        om = float(cli_value)
    else:
        raw = input("Choose Omega_m in [0,1] (flat enforced; Omega_L=1-Omega_m). Example 0.3: ").strip()
        om = float(raw) if raw else 0.3

    if not np.isfinite(om):
        raise ValueError("Omega_m must be a finite number.")
    if om < 0.0 or om > 1.0:
        raise ValueError("Omega_m must be in [0, 1] for this toy model.")
    return om


def H_of_a(a, omega_m):
    omega_l = 1.0 - omega_m
    return np.sqrt(omega_m * a**(-3) + omega_l)


def a_of_s(s, a_min, a_max):
    return a_min * (a_max / a_min) ** s


def make_comoving_grid(xmin=-2.0, xmax=2.0, dx=0.25):
    xs = np.arange(xmin, xmax + 1e-12, dx)
    ys = np.arange(xmin, xmax + 1e-12, dx)
    return xs, ys


def make_random_galaxies(n, box, seed):
    rng = np.random.default_rng(seed)
    x = rng.uniform(-box, box, size=n)
    y = rng.uniform(-box, box, size=n)
    return x, y


def main():
    args = parse_args()
    omega_m = get_omega_m(args.omega_m)
    omega_l = 1.0 - omega_m

    a_min, a_max = args.a_min, args.a_max
    if not (a_min > 0 and a_max > a_min):
        raise ValueError("Require a_min > 0 and a_max > a_min.")

    # a(t) schedule for animation (uniform in ln a)
    s_vals = np.linspace(0.0, 1.0, args.frames)
    a_vals = a_of_s(s_vals, a_min, a_max)

    # comoving geometry
    grid_xs, grid_ys = make_comoving_grid(xmin=-2.0, xmax=2.0, dx=0.25)
    gx_min, gx_max = grid_xs[0], grid_xs[-1]
    gy_min, gy_max = grid_ys[0], grid_ys[-1]

    gal_xc, gal_yc = make_random_galaxies(args.n_gal, args.box, args.seed)

    # camera (both axes share xlim)
    cam_lim = 2.6
    xlim = (-cam_lim, cam_lim)
    ylim = (-cam_lim, cam_lim)

    # figure layout: top strip for photon, bottom for universe
    fig = plt.figure(figsize=(10, 6.2))
    gs = fig.add_gridspec(nrows=2, ncols=1, height_ratios=[1, 7], hspace=0.22)
    ax_wave = fig.add_subplot(gs[0, 0])
    ax = fig.add_subplot(gs[1, 0])
    fig.subplots_adjust(top=0.94, bottom=0.12, left=0.07, right=0.985, hspace=0.22)

    # state toggles
    view_mode = {"mode": "physical"}  # physical/comoving
    paused = {"value": False}
    show_hubble = {"value": True}

    # main axis style
    def apply_main_axis_style():
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_aspect("equal", adjustable="box")
        if view_mode["mode"] == "physical":
            ax.set_xlabel("physical x (arb. units)")
            ax.set_ylabel("physical y (arb. units)")
            ax.set_title("FLRW Expansion: physical view  (r = a x)", pad=10)
        else:
            ax.set_xlabel("comoving x (arb. units)")
            ax.set_ylabel("comoving y (arb. units)")
            ax.set_title("FLRW Expansion: comoving view  (x fixed; scale factor shown separately)", pad=10)

    apply_main_axis_style()

    # photon axis style
    ax_wave.set_xlim(*xlim)
    ax_wave.set_ylim(-1.0, 1.0)
    ax_wave.set_yticks([])
    ax_wave.set_xticks([])
    for sp in ("left", "right", "top"):
        ax_wave.spines[sp].set_visible(False)
    ax_wave.spines["bottom"].set_alpha(0.25)
    ax_wave.set_title("Photon packet stretches: $\\lambda_{phys}(t)=a(t)\\,\\lambda_0$", fontsize=10, pad=2)

    # grid
    grid_lines = []
    a0 = float(a_vals[0])
    grid_color, grid_alpha, grid_lw = "0.75", 0.35, 0.8

    for x_c in grid_xs:
        (ln,) = ax.plot([a0 * x_c, a0 * x_c], [a0 * gy_min, a0 * gy_max],
                        linewidth=grid_lw, alpha=grid_alpha, color=grid_color, zorder=1)
        grid_lines.append(("v", x_c, ln))
    for y_c in grid_ys:
        (ln,) = ax.plot([a0 * gx_min, a0 * gx_max], [a0 * y_c, a0 * y_c],
                        linewidth=grid_lw, alpha=grid_alpha, color=grid_color, zorder=1)
        grid_lines.append(("h", y_c, ln))

    # reference box at a=1
    box = args.box
    ref_box_x = np.array([-box, box, box, -box, -box])
    ref_box_y = np.array([-box, -box, box, box, -box])
    ref_box_line, = ax.plot(ref_box_x, ref_box_y, linestyle="--", linewidth=1.2, alpha=0.45, zorder=2)
    ref_box_label = ax.text(box + 0.05, box + 0.05, "a=1 ref box",
                            fontsize=9, alpha=0.55, ha="left", va="bottom")

    # galaxies
    gal_scatter = ax.scatter(a0 * gal_xc, a0 * gal_yc, s=10, alpha=0.9, zorder=3)

    # info overlay
    info = ax.text(
        0.02, 0.98, "", transform=ax.transAxes, va="top", ha="left",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.3", alpha=0.75)
    )

    # scale bar
    L_c = 0.8
    bar_y = ylim[0] + 0.22
    bar_x0 = xlim[1] - 1.85
    scale_bar, = ax.plot([bar_x0, bar_x0 + a0 * L_c], [bar_y, bar_y],
                         linewidth=3.0, alpha=0.9, zorder=4)
    scale_label = ax.text(bar_x0, bar_y + 0.12, "", fontsize=9, alpha=0.85, ha="left", va="bottom")

    # hubble radius circle
    theta = np.linspace(0, 2*np.pi, 400)
    hubble_circle, = ax.plot([], [], linestyle="--", linewidth=1.2, alpha=0.35, zorder=2)
    hubble_label = ax.text(0.02, 0.02, "", transform=ax.transAxes, fontsize=9, alpha=0.75,
                           bbox=dict(boxstyle="round,pad=0.25", alpha=0.55))

    # ---- Photon packet ----
    wave_x = np.linspace(xlim[0], xlim[1], 1600)
    wave_line, = ax_wave.plot(wave_x, np.zeros_like(wave_x), linewidth=2.2, alpha=0.95)

    # Readout box: top-right to avoid overlap; packet is centered away from it
    wave_text = ax_wave.text(
        0.99, 0.86, "", transform=ax_wave.transAxes,
        ha="right", va="top",
        fontsize=8, alpha=0.92,
        bbox=dict(boxstyle="round,pad=0.2", alpha=0.55)
    )

    # disclaimer
    fig.text(
        0.5, 0.06,
        "Toy model: comoving test particles in FLRW (flat, matter+Λ). "
        "No local gravity/structure formation, no bound systems, no peculiar velocities.",
        ha="center", va="center", fontsize=9, alpha=0.9
    )

    # animation state
    frame_state = {"i": 0}
    packet = {
        # keep packet center away from the readout on the right: start on left-middle
        "x0": xlim[0] + 0.9,  # initial physical center
        "dir": +1.0,          # travel direction (+1 right, -1 left)
        "phi": 0.0            # carrier phase
    }

    def reset_animation():
        frame_state["i"] = 0
        packet["x0"] = xlim[0] + 0.9
        packet["phi"] = 0.0

    def toggle_pause(ani):
        paused["value"] = not paused["value"]
        if paused["value"]:
            ani.event_source.stop()
        else:
            ani.event_source.start()

    def toggle_view():
        view_mode["mode"] = "comoving" if view_mode["mode"] == "physical" else "physical"
        apply_main_axis_style()

    def toggle_hubble():
        show_hubble["value"] = not show_hubble["value"]
        if not show_hubble["value"]:
            hubble_circle.set_data([], [])
            hubble_label.set_text("")

    def flip_packet_direction():
        packet["dir"] *= -1.0

    def on_key(event, ani):
        if event.key == " ":
            toggle_pause(ani)
        elif event.key in ("r", "R"):
            reset_animation()
        elif event.key in ("c", "C"):
            toggle_view()
        elif event.key in ("h", "H"):
            toggle_hubble()
        elif event.key in ("p", "P"):
            flip_packet_direction()
        elif event.key in ("q", "Q", "escape"):
            plt.close(fig)

    # we bind after ani exists, so stash callback and connect later
    key_handler = {"cid": None}

    def update(_):
        i = frame_state["i"]
        i = min(i, args.frames - 1)

        a = float(a_vals[i])
        z = 1.0 / a - 1.0
        H = float(H_of_a(a, omega_m))

        # Main axis: physical vs comoving drawing scale
        s_pos = a if view_mode["mode"] == "physical" else 1.0

        # Grid
        for kind, cval, ln in grid_lines:
            if kind == "v":
                x = s_pos * cval
                ln.set_data([x, x], [s_pos * gy_min, s_pos * gy_max])
            else:
                yv = s_pos * cval
                ln.set_data([s_pos * gx_min, s_pos * gx_max], [yv, yv])

        # Galaxies
        gal_scatter.set_offsets(np.column_stack([s_pos * gal_xc, s_pos * gal_yc]))

        # Info
        info.set_text(
            f"$\\Omega_m$={omega_m:.2f}, $\\Omega_\\Lambda$={omega_l:.2f} (flat)\n"
            f"$a$={a:.3f}    $z$={z:.3f}\n"
            f"$H(a)/H_0$={H:.3f}"
        )

        # Scale bar
        if view_mode["mode"] == "physical":
            bar_len = a * L_c
            scale_label.set_text(f"comoving {L_c:.1f} → physical {a * L_c:.2f}")
        else:
            bar_len = L_c
            scale_label.set_text(f"comoving {L_c:.1f} (fixed)   ⇒ physical {a * L_c:.2f}")
        scale_bar.set_data([bar_x0, bar_x0 + bar_len], [bar_y, bar_y])

        # Hubble radius
        if show_hubble["value"]:
            R_H_phys = 1.0 / H
            R_draw = R_H_phys if view_mode["mode"] == "physical" else (R_H_phys / a)
            hubble_circle.set_data(R_draw * np.cos(theta), R_draw * np.sin(theta))
            hubble_label.set_text(f"Hubble radius: $R_H=1/H$  →  {R_H_phys:.2f} (physical)")
        else:
            hubble_circle.set_data([], [])

        # ---- Photon wave packet ----
        # wavelength stretching
        lambda_phys = a * args.lambda0

        # packet width stretching (keep comoving width fixed)
        sigma_phys = a * args.sigma0

        # move the packet center in physical x (visual)
        dt = 1.0 / max(args.fps, 1e-6)
        packet["x0"] += packet["dir"] * args.packet_speed * dt

        # keep packet away from readout box: bounce before it hits the far right
        # and also bounce off left edge
        right_guard = xlim[1] - 0.55   # keep away from right side readout region
        left_guard = xlim[0] + 0.25
        if packet["x0"] > right_guard:
            packet["x0"] = right_guard
            packet["dir"] *= -1.0
        elif packet["x0"] < left_guard:
            packet["x0"] = left_guard
            packet["dir"] *= -1.0

        # carrier phase advance (visual only; tied to wavelength so it looks photon-like)
        # A simple choice: angular frequency proportional to (carrier_speed / lambda_phys)
        packet["phi"] += 2*np.pi * (args.carrier_speed / max(lambda_phys, 1e-9)) * dt

        # Gaussian envelope centered at x0 with width sigma_phys
        envelope = np.exp(-0.5 * ((wave_x - packet["x0"]) / max(sigma_phys, 1e-9))**2)

        # carrier wave
        carrier = np.cos(2*np.pi * (wave_x / max(lambda_phys, 1e-9)) - packet["phi"])

        y = args.packet_amp * envelope * carrier
        wave_line.set_data(wave_x, y)

        wave_text.set_text(
            f"$\\lambda_{{phys}}$ = {lambda_phys:.3f}   "
            f"$\\sigma_{{phys}}$ = {sigma_phys:.3f}   "
            f"(press 'p' to flip direction)"
        )

        # advance frame
        if not paused["value"]:
            frame_state["i"] = min(frame_state["i"] + 1, args.frames - 1)

        return (
            [gal_scatter, info, scale_bar, scale_label, wave_line, wave_text,
             ref_box_line, ref_box_label, hubble_circle, hubble_label]
            + [ln for _, _, ln in grid_lines]
        )

    interval_ms = 1000.0 / max(args.fps, 1e-6)
    ani = FuncAnimation(fig, update, frames=args.frames, interval=interval_ms, blit=False)

    # connect key handler now that ani exists
    key_handler["cid"] = fig.canvas.mpl_connect("key_press_event", lambda e: on_key(e, ani))

    #ani.save("flrw_demo.gif", writer="pillow", fps=args.fps)

    plt.show()


if __name__ == "__main__":
    main()