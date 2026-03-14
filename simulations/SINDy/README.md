# Sparse Discovery of Dynamical Systems (SINDy)

Recover governing differential equations directly from time-series data using sparse regression.

---

## Overview

This project implements a modular pipeline for discovering differential equations from simulated data using the SINDy method (Brunton et al., 2016). The system simulates dynamical systems, optionally adds noise, constructs a polynomial feature library from the state data, and uses sparse regression (Sequential Thresholded Least Squares) to recover the underlying governing equations.

---

## Key Features

- Modular SINDy pipeline implementation
- Simulation of classical dynamical systems (exponential decay, logistic growth, damped oscillator, Lotka–Volterra, nonlinear pendulum, Lorenz)
- Sparse regression using Sequential Thresholded Least Squares (STLSQ)
- Polynomial feature libraries with cross terms
- Derivative estimation: finite differences or Savitzky–Golay (noise-robust)
- Noise robustness experiments comparing derivative methods
- Recovery of nonlinear systems including the Lorenz attractor
- Diagnostics: coefficient error, trajectory reconstruction error, true vs recovered comparison

---

## Project Structure

```
simulations/   Physics systems used to generate training data (exponential decay,
               logistic growth, damped oscillator, Lorenz, Lotka–Volterra, etc.)

sindy/         Core equation-discovery pipeline: derivative estimation, feature
               library construction, sparse regression, equation printing, metrics

experiments/   Runnable experiment scripts that connect simulations with the
               SINDy pipeline

results/       Saved figures and experiment outputs (e.g. results/figures/)
```

---

## Pipeline

```
Simulate system  →  (optional) add noise  →  estimate derivatives
       →  build feature library  →  sparse regression (STLSQ)
       →  print recovered equations  →  (optional) diagnostics
```

1. **Simulate** — ODE solver produces time-series data.
2. **Optional noise** — Gaussian noise can be added to test robustness.
3. **Derivative estimation** — Finite difference or Savitzky–Golay.
4. **Feature library** — Polynomial terms (constant, linear, cross terms) in library order.
5. **Sparse regression** — STLSQ fits coefficients and thresholds small terms iteratively.
6. **Output** — Recovered equations and, when available, coefficient error vs true system.

---

## Example Result

### Logistic growth

**True equation**

```
dx/dt = 2x − 0.4x²
```

**Recovered equation**

```
dx/dt ≈ 2.001x − 0.400x²
```

### Lorenz system

**Recovered form (σ=10, ρ=28, β=8/3)**

```
dx/dt ≈ 10(y − x)
dy/dt ≈ 28x − y − xz
dz/dt ≈ xy − 2.67z
```

Small coefficient drift can occur due to derivative estimation and numerical error; for chaotic systems like Lorenz, a higher sparsity threshold is used to reduce spurious terms.

---

## Installation

```bash
pip install -r requirements.txt
```

Dependencies: **numpy**, **scipy**, **matplotlib**.

---

## Running Experiments

From the **project root**:

```bash
python3 experiments/run_exponential_decay.py
python3 experiments/run_logistic_growth.py
python3 experiments/run_lorenz.py
python3 experiments/run_noise_experiment.py
```

Each script simulates the system, runs the SINDy pipeline, and prints the recovered equations (and diagnostics where true coefficients are known). Plots are saved under `results/figures/`.

---

## Limitations

- **Derivative estimation** — SINDy is sensitive to how dx/dt is estimated; noise amplifies with finite differences. Savitzky–Golay assumes uniformly spaced time.
- **Noise** — High noise can introduce spurious terms or bias coefficients; threshold and smoothing help but do not remove the need for reasonable data quality.
- **Library choice** — The polynomial library constrains which equations can be discovered; non-polynomial dynamics (e.g. trigonometric) require different or extended libraries.
- **Threshold tuning** — The STLSQ sparsity threshold may need to be adjusted per system (e.g. higher for Lorenz to suppress spurious terms).

---

## Reference

Brunton, S. L., Proctor, J. L., & Kutz, J. N. (2016). Discovering governing equations from data by sparse identification of nonlinear dynamical systems. *Proceedings of the National Academy of Sciences*, 113(15), 3932–3937.

---

## License

MIT License
