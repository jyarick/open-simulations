#!/usr/bin/env python3
"""
Build the interactive Lagrangian Lab notebook.
Run this script to regenerate lagrangian_lab.ipynb with ipywidgets controls.
"""

import json
from pathlib import Path


def make_cell(cell_type, source, outputs=None):
    lines = source.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    cell_source = [ln + "\n" for ln in lines]
    cell = {"cell_type": cell_type, "metadata": {}, "source": cell_source}
    if cell_type == "code":
        cell["outputs"] = outputs if outputs is not None else []
        cell["execution_count"] = None
    return cell

def main():
    cells = []

    # --- Cell 0: Overview ---
    cells.append(make_cell("markdown", """# Lagrangian Mechanics Lab

An interactive Jupyter lab for learning classical mechanics through symbolic derivation and numerical simulation.

---

## 1. Overview

This notebook walks you through the full Lagrangian mechanics pipeline. Choose a system in the **Control Panel** below, set parameters and initial conditions, then click **Run Simulation** to see:

- **Symbolic derivation** — coordinates, energies, Lagrangian, and equations of motion
- **Numerical solution** — integration with `scipy.integrate.solve_ivp`
- **Visualization** — time series, energy diagnostics, phase space, and animation

**The pipeline:** System definition → Energies ($T$, $V$) → Lagrangian ($L = T - V$) → Euler–Lagrange equations → Numerical integration → Plots and animation

**Key equations:**

$$L = T - V \\quad \\text{(Lagrangian)}$$

$$\\frac{d}{dt}\\left(\\frac{\\partial L}{\\partial \\dot{q}}\\right) - \\frac{\\partial L}{\\partial q} = 0 \\quad \\text{(Euler–Lagrange, for each coordinate } q \\text{)}$$"""))

    # --- Cell 1: Setup ---
    cells.append(make_cell("markdown", """---
## 2. Setup

Run the cell below to load the lab. Then use the Control Panel to select a system and run a simulation."""))

    # --- Cell 2: Imports and helpers ---
    imports_and_helpers = '''import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from sympy import init_printing, simplify
import ipywidgets as widgets
from IPython.display import display, HTML, Markdown

from lagrangian_lab.core.solver import solve_second_order
from lagrangian_lab.core.display import animate_pendulum, animate_mass_spring, animate_double_pendulum

init_printing(use_unicode=True)


def _print_run_summary(system_name, params, ics, t_max, n_samples):
    """Print a concise summary of the selected system and settings."""
    names = {"pendulum": "Simple pendulum", "mass_spring": "Mass-spring oscillator", "double_pendulum": "Double pendulum"}
    display(Markdown(f"**{names[system_name]}** — $t_{{max}} = {t_max}$ s, $n = {n_samples}$ samples"))
    if system_name == "pendulum":
        display(Markdown(f"$m = {params['m']}$, $l = {params['l']}$, $g = {params['g']}$ | $\\\\theta_0 = {ics['theta0']:.3f}$, $\\\\omega_0 = {ics['omega0']:.3f}$"))
    elif system_name == "mass_spring":
        display(Markdown(f"$m = {params['m']}$, $k = {params['k']}$ | $x_0 = {ics['x0']:.3f}$, $v_0 = {ics['v0']:.3f}$"))
    else:
        display(Markdown(f"$m_1 = {params['m1']}$, $m_2 = {params['m2']}$, $l_1 = {params['l1']}$, $l_2 = {params['l2']}$, $g = {params['g']}$"))
        display(Markdown(f"$\\\\theta_1(0) = {ics['theta1_0']:.3f}$, $\\\\theta_2(0) = {ics['theta2_0']:.3f}$, $\\\\omega_1(0) = {ics['omega1_0']:.3f}$, $\\\\omega_2(0) = {ics['omega2_0']:.3f}$"))


def load_system_module(system_name):
    """Load and return the system module."""
    if system_name == "pendulum":
        from lagrangian_lab.systems import pendulum as mod
    elif system_name == "mass_spring":
        from lagrangian_lab.systems import mass_spring as mod
    elif system_name == "double_pendulum":
        from lagrangian_lab.systems import double_pendulum as mod
    else:
        raise ValueError(f"Unknown system: {system_name}")
    return mod


def run_selected_system(system_name, params, ics, t_max, n_samples, out):
    """Run simulation and render all outputs into the output widget."""
    out.clear_output(wait=True)
    with out:
        _print_run_summary(system_name, params, ics, t_max, n_samples)
        mod = load_system_module(system_name)
        T = mod.T
        V = mod.V
        L = mod.L
        residuals = mod.residuals
        accel_expr = mod.accel_expr
        make_rhs = mod.make_rhs
        make_energy_funcs = mod.make_energy_funcs
        n_dof = getattr(mod, "n_dof", 1)

        if system_name == "pendulum":
            m_val, l_val, g_val = params["m"], params["l"], params["g"]
            q0 = ics["theta0"]
            q_dot0 = ics["omega0"]
            rhs = make_rhs(m_val, l_val, g_val)
        elif system_name == "mass_spring":
            m_val, k_val = params["m"], params["k"]
            q0 = ics["x0"]
            q_dot0 = ics["v0"]
            rhs = make_rhs(m_val, k_val)
        else:  # double_pendulum
            m1_val, m2_val = params["m1"], params["m2"]
            l1_val, l2_val = params["l1"], params["l2"]
            g_val = params["g"]
            q0 = np.array([ics["theta1_0"], ics["theta2_0"]])
            q_dot0 = np.array([ics["omega1_0"], ics["omega2_0"]])
            rhs = make_rhs(m1_val, m2_val, l1_val, l2_val, g_val)

        y0 = np.concatenate([np.atleast_1d(q0), np.atleast_1d(q_dot0)])
        t_span = (0, t_max)
        t_eval = np.linspace(0, t_max, n_samples)

        sol = solve_second_order(rhs, t_span, y0, t_eval=t_eval)
        q_sol = sol.y[:n_dof]
        q_dot_sol = sol.y[n_dof : 2 * n_dof]

        render_symbolics(mod, system_name, T, V, L, residuals, accel_expr)
        render_plots(system_name, params, sol, q_sol, q_dot_sol, n_dof, make_energy_funcs)
        render_animation(system_name, params, sol, q_sol, n_dof)


def render_symbolics(mod, system_name, T, V, L, residuals, accel_expr):
    """Display sections 3–6: system definition, energies, Lagrangian, Euler–Lagrange."""
    display(Markdown("---\\n### 3. System Definition\\n\\nA **generalized coordinate** is a minimal set of variables that fully describes the configuration. We express Cartesian positions in terms of these coordinates."))
    if system_name == "pendulum":
        display(Markdown("**Pendulum:** Bob position $(x, y)$ in terms of angle $\\\\theta$:"))
        display(mod.x)
        display(mod.y)
    elif system_name == "mass_spring":
        display(Markdown("**Mass-spring:** The mass moves along the $x$-axis ($y = 0$):"))
        display(mod.x)
    else:
        display(Markdown("**Double pendulum:** Positions of mass 1 and mass 2:"))
        display(mod.x1)
        display(mod.y1)
        display(mod.x2)
        display(mod.y2)

    display(Markdown("---\\n### 4. Energies\\n\\n**Kinetic energy** $T$ comes from motion; **potential energy** $V$ from position in a conservative field. Together they determine the dynamics."))
    display(Markdown("**Kinetic energy $T$:**"))
    display(simplify(T))
    display(Markdown("**Potential energy $V$:**"))
    display(simplify(V))

    display(Markdown("---\\n### 5. Lagrangian\\n\\nThe **Lagrangian** $L = T - V$ encodes the system. Why this form? The Euler–Lagrange equations derived from $L$ yield the correct equations of motion for conservative systems."))
    display(Markdown("**$L = T - V$:**"))
    display(simplify(L))

    display(Markdown("---\\n### 6. Euler–Lagrange Equations\\n\\nFor each generalized coordinate $q$, we require $\\\\frac{d}{dt}(\\\\partial L / \\\\partial \\\\dot{q}) - \\\\partial L / \\\\partial q = 0$. This **residual** must vanish; solving for $\\\\ddot{q}$ gives the equations of motion."))
    for i, r in enumerate(residuals):
        if len(residuals) > 1:
            display(Markdown(f"**Residual {i+1}** (for coordinate $q_{i+1}$):"))
        else:
            display(Markdown("**Residual** (set to zero):"))
        display(simplify(r))
    display(Markdown("**Solved accelerations:**"))
    if isinstance(accel_expr, tuple):
        for i, a in enumerate(accel_expr):
            display(Markdown(f"$\\\\ddot{{q}}_{i+1}$:"))
            display(a)
    else:
        display(accel_expr)


def render_plots(system_name, params, sol, q_sol, q_dot_sol, n_dof, make_energy_funcs):
    """Display section 5: simulation plots (coords, energy, phase space)."""
    if system_name == "pendulum":
        T_func, V_func = make_energy_funcs(params["m"], params["l"], params["g"])
    elif system_name == "mass_spring":
        T_func, V_func = make_energy_funcs(params["m"], params["k"])
    else:
        T_func, V_func = make_energy_funcs(
            params["m1"], params["m2"], params["l1"], params["l2"], params["g"]
        )

    if n_dof == 1:
        T_vals = T_func(q_sol[0], q_dot_sol[0])
        V_vals = V_func(q_sol[0], q_dot_sol[0])
    else:
        T_vals = T_func(q_sol[0], q_sol[1], q_dot_sol[0], q_dot_sol[1])
        V_vals = V_func(q_sol[0], q_sol[1], q_dot_sol[0], q_dot_sol[1])
    E_vals = T_vals + V_vals

    display(Markdown("---\\n### 7. Numerical Simulation & Diagnostics\\n\\nThe equations of motion are integrated with `solve_ivp`. **Energy conservation:** For conservative systems, $E = T + V$ is constant — the flat total-energy line confirms the integration is accurate. **Phase space** ($q$ vs $\\\\dot{q}$) shows how the state evolves; closed curves indicate periodic motion."))

    if n_dof == 1:
        fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    else:
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    if n_dof == 1:
        ax = axes[0]
        ax.plot(sol.t, q_sol[0], "b-")
        ax.set_ylabel("θ (rad)" if system_name == "pendulum" else "x (m)")
        ax.set_title("Angular displacement vs time" if system_name == "pendulum" else "Position vs time")
        ax.set_xlabel("Time (s)")
        ax.grid(True, alpha=0.3)

        ax = axes[1]
        ax.plot(sol.t, T_vals, label="Kinetic T")
        ax.plot(sol.t, V_vals, label="Potential V")
        ax.plot(sol.t, E_vals, label="Total E", linestyle="--", color="k")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Energy (J)")
        ax.set_title("Energy conservation")
        ax.legend()
        ax.grid(True, alpha=0.3)

        ax = axes[2]
        ax.plot(q_sol[0], q_dot_sol[0], "b-")
        ax.set_xlabel("θ (rad)" if system_name == "pendulum" else "x (m)")
        ax.set_ylabel("ω (rad/s)" if system_name == "pendulum" else "v (m/s)")
        ax.set_title("Phase space")
        ax.grid(True, alpha=0.3)
    else:
        ax = axes[0, 0]
        ax.plot(sol.t, q_sol[0], "b-", label="θ₁")
        ax.plot(sol.t, q_sol[1], "r-", label="θ₂")
        ax.set_ylabel("θ (rad)")
        ax.set_title("Angles vs time")
        ax.legend()
        ax.set_xlabel("Time (s)")
        ax.grid(True, alpha=0.3)

        ax = axes[0, 1]
        ax.plot(sol.t, T_vals, label="Kinetic T")
        ax.plot(sol.t, V_vals, label="Potential V")
        ax.plot(sol.t, E_vals, label="Total E", linestyle="--", color="k")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Energy (J)")
        ax.set_title("Energy conservation")
        ax.legend()
        ax.grid(True, alpha=0.3)

        ax = axes[1, 0]
        ax.plot(q_sol[0], q_dot_sol[0], "b-")
        ax.set_xlabel("θ₁ (rad)")
        ax.set_ylabel("ω₁ (rad/s)")
        ax.set_title("Phase space: θ₁ vs ω₁")
        ax.grid(True, alpha=0.3)

        ax = axes[1, 1]
        ax.plot(q_sol[1], q_dot_sol[1], "r-")
        ax.set_xlabel("θ₂ (rad)")
        ax.set_ylabel("ω₂ (rad/s)")
        ax.set_title("Phase space: θ₂ vs ω₂")
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def render_animation(system_name, params, sol, q_sol, n_dof):
    """Display section 8: animation."""
    display(Markdown("---\\n### 8. Animation — motion in physical space"))
    fig, ax = plt.subplots(figsize=(6, 6))
    if system_name == "pendulum":
        anim = animate_pendulum(ax, sol.t, q_sol[0], params["l"])
        ax.set_title("Simple pendulum")
    elif system_name == "mass_spring":
        anim = animate_mass_spring(ax, sol.t, q_sol[0])
        ax.set_title("Mass-spring oscillator")
    else:
        anim = animate_double_pendulum(
            ax, sol.t, q_sol[0], q_sol[1], params["l1"], params["l2"]
        )
        ax.set_title("Double pendulum")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    plt.tight_layout()
    html = anim.to_jshtml()
    plt.close(fig)
    display(HTML(html))'''
    cells.append(make_cell("code", imports_and_helpers))

    # --- Cell 3: Control panel markdown ---
    cells.append(make_cell("markdown", """---
## Control Panel

Select a system, adjust parameters and initial conditions, then click **Run Simulation**. Output appears below."""))

    # --- Cell 4: Build controls ---
    build_controls = '''# Control panel: system selection, parameters, initial conditions, simulation
# Educational defaults: pendulum ~40°, mass-spring moderate displacement, double pendulum interesting but not chaotic

# Pendulum: moderate angle (0.7 rad ≈ 40°), visible oscillation
m_p = widgets.FloatSlider(value=1.0, min=0.1, max=5.0, step=0.1, description="m (kg)")
l_p = widgets.FloatSlider(value=1.0, min=0.1, max=3.0, step=0.1, description="l (m)")
g_p = widgets.FloatSlider(value=9.81, min=1.0, max=20.0, step=0.1, description="g (m/s²)")
theta0_p = widgets.FloatSlider(value=0.7, min=-1.6, max=1.6, step=0.05, description="θ₀ (rad)")
omega0_p = widgets.FloatSlider(value=0.0, min=-5.0, max=5.0, step=0.1, description="ω₀ (rad/s)")

# Mass-spring: nontrivial displacement, simple oscillation
m_ms = widgets.FloatSlider(value=1.0, min=0.1, max=5.0, step=0.1, description="m (kg)")
k_ms = widgets.FloatSlider(value=10.0, min=0.5, max=50.0, step=0.5, description="k (N/m)")
x0_ms = widgets.FloatSlider(value=0.5, min=-2.0, max=2.0, step=0.1, description="x₀ (m)")
v0_ms = widgets.FloatSlider(value=0.0, min=-5.0, max=5.0, step=0.1, description="v₀ (m/s)")

# Double pendulum: both arms ~35°, shows coupling without immediate chaos
m1_dp = widgets.FloatSlider(value=1.0, min=0.1, max=5.0, step=0.1, description="m₁ (kg)")
m2_dp = widgets.FloatSlider(value=1.0, min=0.1, max=5.0, step=0.1, description="m₂ (kg)")
l1_dp = widgets.FloatSlider(value=1.0, min=0.1, max=2.0, step=0.1, description="l₁ (m)")
l2_dp = widgets.FloatSlider(value=1.0, min=0.1, max=2.0, step=0.1, description="l₂ (m)")
g_dp = widgets.FloatSlider(value=9.81, min=1.0, max=20.0, step=0.1, description="g (m/s²)")
theta1_0_dp = widgets.FloatSlider(value=0.6, min=-1.6, max=1.6, step=0.05, description="θ₁₀ (rad)")
theta2_0_dp = widgets.FloatSlider(value=0.6, min=-1.6, max=1.6, step=0.05, description="θ₂₀ (rad)")
omega1_0_dp = widgets.FloatSlider(value=0.0, min=-5.0, max=5.0, step=0.1, description="ω₁₀ (rad/s)")
omega2_0_dp = widgets.FloatSlider(value=0.0, min=-5.0, max=5.0, step=0.1, description="ω₂₀ (rad/s)")

# Simulation: reasonable defaults, guardrails to avoid sluggishness
t_max = widgets.FloatSlider(value=10.0, min=1.0, max=30.0, step=1.0, description="t_max (s)")
n_samples = widgets.IntSlider(value=500, min=100, max=1500, step=100, description="samples")

system_dropdown = widgets.Dropdown(
    options=[("Simple pendulum", "pendulum"), ("Mass-spring", "mass_spring"), ("Double pendulum", "double_pendulum")],
    value="pendulum",
    description="System:",
)

params_header = widgets.HTML("<b style='font-size:11px'>Physical parameters & initial conditions</b>")
pendulum_box = widgets.VBox([
    params_header,
    m_p, l_p, g_p,
    theta0_p, omega0_p,
])
mass_spring_box = widgets.VBox([
    params_header,
    m_ms, k_ms,
    x0_ms, v0_ms,
])
double_pendulum_box = widgets.VBox([
    params_header,
    m1_dp, m2_dp, l1_dp, l2_dp, g_dp,
    theta1_0_dp, theta2_0_dp, omega1_0_dp, omega2_0_dp,
])

sim_header = widgets.HTML("<b style='font-size:11px'>Simulation settings</b>")
sim_box = widgets.VBox([sim_header, t_max, n_samples])

out = widgets.Output(layout=widgets.Layout(min_height="800px", overflow="auto"))

# Workaround for ipywidgets #3702: clear_output + display has odd/even bug;
# first display cycle fails. Pre-populate so first Run is the second cycle.
with out:
    display(HTML('<div style="padding:12px;color:#666;">Click <b>Run Simulation</b> to see results.</div>'))


def on_system_change(change):
    system = change["new"]
    if system == "pendulum":
        params_box.children = [pendulum_box]
    elif system == "mass_spring":
        params_box.children = [mass_spring_box]
    else:
        params_box.children = [double_pendulum_box]


system_dropdown.observe(on_system_change, names="value")
params_box = widgets.VBox([pendulum_box])
on_system_change({"new": system_dropdown.value})


def on_run(b):
    system = system_dropdown.value
    if system == "pendulum":
        params = {"m": m_p.value, "l": l_p.value, "g": g_p.value}
        ics = {"theta0": theta0_p.value, "omega0": omega0_p.value}
    elif system == "mass_spring":
        params = {"m": m_ms.value, "k": k_ms.value}
        ics = {"x0": x0_ms.value, "v0": v0_ms.value}
    else:
        params = {"m1": m1_dp.value, "m2": m2_dp.value, "l1": l1_dp.value, "l2": l2_dp.value, "g": g_dp.value}
        ics = {"theta1_0": theta1_0_dp.value, "theta2_0": theta2_0_dp.value, "omega1_0": omega1_0_dp.value, "omega2_0": omega2_0_dp.value}
    run_selected_system(system, params, ics, t_max.value, n_samples.value, out)


run_btn = widgets.Button(description="Run Simulation", button_style="success")
run_btn.on_click(on_run)

system_row = widgets.HBox([system_dropdown, run_btn], layout=widgets.Layout(margin="0 0 8px 0"))
controls_row = widgets.HBox([params_box, sim_box])
control_panel = widgets.VBox([system_row, controls_row], layout=widgets.Layout(padding="8px", border="1px solid #ddd", border_radius="4px"))

display(control_panel)
display(out)'''
    cells.append(make_cell("code", build_controls))

    nb = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.10.0"},
        },
        "cells": cells,
    }

    out_path = Path(__file__).parent / "lagrangian_lab.ipynb"
    with open(out_path, "w") as f:
        json.dump(nb, f, indent=1)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
