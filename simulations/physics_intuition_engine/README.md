# Physics Intuition Engine

A symbolic equation-reading tool for ODEs and linear systems: it parses equations, extracts structure (coefficients, eigenvalues, eigenvectors), computes characteristic scales and regime conditions, and shows general solutions and physics-oriented summaries.

## What it does

**Single ODEs** — Given an equation such as

$$
m\ddot{x} + b\dot{x} + kx = F_0 \cos(\omega t),
$$

the engine:

- Parses the equation into canonical form
- Classifies order, linearity, constant vs time-varying coefficients, forcing
- Extracts coefficients and derived quantities (discriminant, natural frequency, damping ratio, timescales)
- Identifies regime conditions (overdamped, critical, underdamped, resonance, etc.)
- Computes a **general solution** (symbolic, no initial conditions)
- Suggests **physical systems** the equation might represent
- Produces mathematical and physics/intuition summaries

**Systems of ODEs** — For a system in normal form (e.g. \(\dot{x} = -x + y\), \(\dot{y} = x - 2y\)), the engine:

- Parses the system and builds the coefficient matrix \(A\) and vector \(\mathbf{b}\)
- Computes **eigenvalues**, **eigenvectors**, **trace**, and **determinant**
- Summarizes **stability** (stable node, spiral, saddle, etc.) and regime insights
- Computes a **general solution** for the system
- Suggests physical systems (coupled oscillators, predator–prey, etc.)

## Scope

- **Strongest support:** second-order linear constant-coefficient ODEs; linear first-order systems in normal form.
- **Recognized with partial interpretation:** first-order linear (constant or time-varying), second-order time-varying, nonlinear.
- **Input:** one equation, or multiple equations separated by `;` or newline for systems.

## Project structure

```text
physics_intuition_engine/
├── intuition_engine/
│   ├── __init__.py
│   ├── examples.py
│   ├── pipeline.py
│   ├── ode/                    # Single ODEs
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   ├── parser.py
│   │   ├── classifier.py
│   │   ├── extractors.py
│   │   ├── regimes.py
│   │   ├── scaling.py
│   │   ├── validation.py
│   │   ├── explain.py
│   │   └── solution.py
│   └── systems/                # Systems of ODEs (matrix, eigenvalues, eigenvectors)
│       ├── __init__.py
│       ├── schemas.py
│       ├── parser.py
│       └── extract.py
├── notebooks/
│   └── engine_playground.ipynb
├── tests/
│   └── test_cases.py
├── requirements.txt
└── README.md
```

## Installation

Create and use a virtual environment (recommended), then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run the notebook from the project root (so imports resolve):

```bash
jupyter notebook notebooks/engine_playground.ipynb
```

## Usage

From Python:

```python
from intuition_engine.pipeline import analyze_equation

# Single ODE
report = analyze_equation("m*diff(x(t), t, 2) + b*diff(x(t), t) + k*x(t) = F0*cos(omega*t)")
# report.parsed, report.classification, report.features, report.regimes, report.solution, report.physical_systems

# System
report = analyze_equation("diff(x(t), t) = -x + y; diff(y(t), t) = x - 2*y")
# report.system_info.matrix_A, .eigenvalues, .eigenvectors, .trace, .determinant, .stability_summary
# report.solution  # general solution
```

Or use the notebook UI: paste an equation (or system, separated by `;`), then click **Analyze Equation**.

## Why this project exists

Many students learn to manipulate equations without learning to read them physically. This project turns equations into structured intuition: scales, regimes, stability, and what the equation might represent in the real world.
