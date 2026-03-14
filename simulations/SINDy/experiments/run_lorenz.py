"""
Run SINDy on Lorenz: dx/dt = 10(y-x), dy/dt = 28x - xz - y, dz/dt = xy - 2.67z.
"""
import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
RESULTS_FIGURES = os.path.join(PROJECT_ROOT, "results", "figures")
os.makedirs(RESULTS_FIGURES, exist_ok=True)

import numpy as np
import matplotlib.pyplot as plt

from simulations.lorenz import simulate_lorenz, true_coefficients_polynomial
from sindy.differentiate import estimate_derivative
from sindy.library import polynomial_library
from sindy.sparse_regression import sparse_regression
from sindy.sindy_model import print_equations, print_coefficient_comparison
from sindy.metrics import coefficient_error, trajectory_reconstruction_error

# Derivative method: "finite_difference" or "savgol"
DERIVATIVE_METHOD = "savgol"

sigma, rho, beta = 10.0, 28.0, 8.0 / 3.0
t, y = simulate_lorenz(sigma=sigma, rho=rho, beta=beta, x0=1, y0=1, z0=1, t_span=(0, 25), num_points=2500)

# pipeline: derivative -> library -> regression (higher threshold for Lorenz)
dydt = estimate_derivative(t, y, method=DERIVATIVE_METHOD, window_length=21, polyorder=3)
Theta, names = polynomial_library(y, degree=2)
Xi = sparse_regression(Theta, dydt, threshold=0.15)

# --- Outputs ---
print("Recovered equations:")
print_equations(Xi, names, state_names=["x", "y", "z"])

print("\nActive coefficients (nonzero only):")
for i, state in enumerate(["x", "y", "z"]):
    for j, name in enumerate(names):
        if abs(Xi[j, i]) > 1e-6:
            print(f"  d{state}/dt <- {name}: {Xi[j, i]:.6f}")

Xi_true = true_coefficients_polynomial(sigma, rho, beta, degree=2)
coef_err = print_coefficient_comparison(Xi, Xi_true, names, state_names=["x", "y", "z"])
recon_err = trajectory_reconstruction_error(Theta, Xi, dydt)
print(f"\nRelative coefficient error: {coef_err:.6e}")
print(f"Trajectory reconstruction error: {recon_err:.6e}")

# --- Trajectory plot (time series) ---
fig, ax = plt.subplots(figsize=(8, 3))
ax.plot(t, y[:, 0], label="x", alpha=0.8)
ax.plot(t, y[:, 1], label="y", alpha=0.8)
ax.plot(t, y[:, 2], label="z", alpha=0.8)
ax.set_xlabel("t")
ax.set_ylabel("state")
ax.set_title("Lorenz: time series")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_FIGURES, "lorenz_trajectory.png"), dpi=150)
plt.close()
