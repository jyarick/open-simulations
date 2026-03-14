# Phase Space Explorer

A modular **dynamical systems** teaching tool in Python: define systems, simulate with SciPy, analyze equilibria and stability, and plot dimension-aware phase portraits.

## Features

- **Reusable engine**: simulation, stability, and plotting are separate from any UI.
- **Four built-in systems**:
  1. **Logistic growth** (1D) — \( \frac{dx}{dt} = r x (1 - x/K) \)
  2. **Lotka–Volterra** (2D) — predator–prey
  3. **Damped harmonic oscillator** (2D) — \( \ddot{x} + \gamma\dot{x} + \omega^2 x = 0 \)
  4. **Lorenz** (3D) — chaotic attractor
- **Simulation**: `solve_ivp`-based `simulate(system, y0, params, t_span, t_eval)`.
- **Stability**: equilibria from `system.equilibria(params)`, classification via Jacobian eigenvalues (1D: derivative test; 2D/3D: eigenvalue sign).
- **Plotting**: 1D (trajectory, vector field, phase line); 2D (phase plane, vector field, time series); 3D (trajectory, time series, projections).

## Install

```bash
cd phase_space_explorer
pip install -r requirements.txt
pip install -e .
```

Or from project root:

```bash
pip install -e .
```

## Usage

**From a notebook** (e.g. `notebooks/phase_space_explorer_demo.ipynb`):

```python
from phase_space_explorer import ALL_SYSTEMS, simulate, plot_system, get_equilibria_with_stability

system = ALL_SYSTEMS[0]  # Logistic
params = {k: info["default"] for k, info in system.parameter_info.items()}
y0 = [info["default"] for info in system.initial_condition_info.values()]
t, y = simulate(system, y0, params, (0, 20), t_eval=np.linspace(0, 20, 500))
equilibria = get_equilibria_with_stability(system, params)
plot_system(system, params, t, y, equilibria=equilibria)
```

**Adding a new system**: implement a `DynamicalSystem` (see `systems/base.py`) with `name`, `dimension`, `rhs`, `equilibria`, `jacobian`, `parameter_info`, `initial_condition_info`, `description`, `interpretation`, and register it in `systems/__init__.py`. No UI logic in the system definition.

## Project layout

```
phase_space_explorer/
├── notebooks/
│   └── phase_space_explorer_demo.ipynb
├── phase_space_explorer/
│   ├── __init__.py
│   ├── systems/          # base + logistic, predator_prey, oscillator, lorenz
│   ├── core/              # simulate, stability, jacobian, analysis
│   ├── plotting/         # plot_1d, plot_2d, plot_3d, plot_system
│   └── ui/                # notebook_controls (sliders from metadata)
├── requirements.txt
└── README.md
```

## License

Use as you like; no warranty.
