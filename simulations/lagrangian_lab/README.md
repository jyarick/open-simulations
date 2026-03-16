# Lagrangian Mechanics Lab

A Jupyter-based interactive lab for learning classical mechanics through symbolic derivation and numerical simulation.

---

## What It Is

Lagrangian Mechanics Lab is an educational tool that walks you through the full pipeline from physical system definition to equations of motion, numerical solution, and visualization. You choose a system, set parameters and initial conditions, and see how the Lagrangian formalism produces the dynamics.

## Core Idea

The lab demonstrates how a mechanical system moves by following this sequence:

1. **System definition** — Choose generalized coordinates and express positions in terms of them  
2. **Energies** — Compute kinetic energy $T$ and potential energy $V$  
3. **Lagrangian** — Form $L = T - V$  
4. **Euler–Lagrange equations** — Derive the equations of motion  
5. **Numerical solution** — Integrate with `scipy.integrate.solve_ivp`  
6. **Visualization** — Plots (time series, energy, phase space) and animation  

## Current Systems

- **Simple pendulum** — One degree of freedom, angle $\theta$
- **Mass-spring oscillator** — One degree of freedom, position $x$
- **Double pendulum** — Two degrees of freedom, angles $\theta_1$, $\theta_2$

## Features

- **Symbolic mechanics** with SymPy — coordinates, $T$, $V$, $L$, and Euler–Lagrange residuals
- **Numerical integration** with `solve_ivp`
- **Diagnostics** — energy conservation, phase space
- **Animation** — in-notebook visualization of the motion
- **Interactive controls** with ipywidgets — system selection, parameters, initial conditions, simulation settings

## Educational Purpose

This lab helps students connect abstract Lagrangian mechanics to concrete motion. By seeing the symbolic derivation and numerical results side by side, learners can:

- Understand what generalized coordinates are and why they matter
- See how $L = T - V$ encodes the dynamics
- Follow the Euler–Lagrange procedure from Lagrangian to equations of motion
- Verify energy conservation and interpret phase space

## Installation

```bash
cd simulations/lagrangian_lab
pip install -r requirements.txt
```

**Requirements:** Python 3.8+, Jupyter, SymPy, NumPy, SciPy, Matplotlib, ipywidgets

For JupyterLab, you may need the ipywidgets extension:

```bash
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

## Usage

```bash
jupyter lab notebook/lagrangian_lab.ipynb
```

Or with classic Jupyter Notebook:

```bash
jupyter notebook notebook/lagrangian_lab.ipynb
```

1. Run the **Setup** cell to load the lab  
2. Use the **Control Panel** to select a system and set parameters  
3. Click **Run Simulation** — symbolic derivation, plots, and animation appear below  

## Project Structure

```
lagrangian_lab/
├── notebook/
│   ├── lagrangian_lab.ipynb      # Main interactive notebook
│   └── build_interactive_notebook.py   # Regenerates the notebook
├── core/
│   ├── euler_lagrange.py         # Symbolic E–L derivation
│   ├── solver.py                 # solve_ivp wrapper
│   └── display.py                # Animation helpers
├── systems/
│   ├── pendulum.py               # Simple pendulum
│   ├── mass_spring.py            # Mass-spring oscillator
│   └── double_pendulum.py        # Double pendulum
├── requirements.txt
└── README.md
```

## Suggested Screenshots

For presentations or documentation, these settings produce clear, readable visuals:

| System           | Suggested settings                          | Why                                      |
|------------------|---------------------------------------------|------------------------------------------|
| Simple pendulum  | $\theta_0 = 0.7$ rad (~40°), $\omega_0 = 0$ | Visible oscillation, clean phase curve   |
| Mass-spring      | $x_0 = 0.5$ m, $v_0 = 0$                    | Simple harmonic motion, clear energy swap |
| Double pendulum  | $\theta_1 = \theta_2 = 0.6$ rad, both $\omega = 0$ | Interesting coupling, not immediately chaotic |

Use **Run Simulation** with these defaults, then capture the output (symbolic equations, plots, animation).

## Future Directions

Possible extensions (not yet implemented):

- Additional systems (coupled oscillators, bead on wire, etc.)
- Noether's theorem and conserved quantities
- Comparison of different coordinate choices
- Export to video or GIF
- Improved interactivity (e.g., live parameter updates)

## License

Part of the Open Physics Simulations project.
