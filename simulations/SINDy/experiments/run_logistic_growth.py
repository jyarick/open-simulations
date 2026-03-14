"""
Run SINDy on logistic growth: dx/dt = r x - (r/K) x^2.
"""
import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
RESULTS_FIGURES = os.path.join(PROJECT_ROOT, "results", "figures")
os.makedirs(RESULTS_FIGURES, exist_ok=True)

import numpy as np
import matplotlib.pyplot as plt

from simulations.logistic_growth import simulate_logistic_growth, true_coefficients_polynomial
from sindy.differentiate import estimate_derivative
from sindy.library import polynomial_library
from sindy.sparse_regression import sparse_regression
from sindy.sindy_model import print_equations, print_coefficient_comparison
from sindy.metrics import coefficient_error, trajectory_reconstruction_error

# Derivative method: "finite_difference" or "savgol"
DERIVATIVE_METHOD = "savgol"

r, K = 2.0, 5.0
t, y = simulate_logistic_growth(r=r, K=K, x0=0.5)

# pipeline: derivative -> library -> regression
dydt = estimate_derivative(t, y, method=DERIVATIVE_METHOD, window_length=11, polyorder=3)
Theta, names = polynomial_library(y, degree=3)
Xi = sparse_regression(Theta, dydt, threshold=0.05)

# --- Outputs ---
print("Recovered equations:")
print_equations(Xi, names, state_names=["x"])

print("\nActive coefficients:")
for name, coef in zip(names, Xi[:, 0]):
    if abs(coef) > 1e-6:
        print(f"  {name}: {coef:.6f}")

Xi_true = true_coefficients_polynomial(r, K, degree=3)
coef_err = print_coefficient_comparison(Xi, Xi_true, names, state_names=["x"])
recon_err = trajectory_reconstruction_error(Theta, Xi, dydt)
print(f"\nRelative coefficient error: {coef_err:.6e}")
print(f"Trajectory reconstruction error: {recon_err:.6e}")

# --- Trajectory plot ---
fig, ax = plt.subplots(figsize=(6, 3))
ax.plot(t, y[:, 0], "b-", label="x(t)")
ax.set_xlabel("t")
ax.set_ylabel("x")
ax.set_title("Logistic growth: trajectory")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_FIGURES, "logistic_trajectory.png"), dpi=150)
plt.close()

# --- Bar plot: true vs recovered coefficients ---
fig, ax = plt.subplots(figsize=(6, 3))
x_pos = np.arange(len(names))
width = 0.35
ax.bar(x_pos - width / 2, Xi_true[:, 0], width, label="True", color="C0")
ax.bar(x_pos + width / 2, Xi[:, 0], width, label="Recovered", color="C1")
ax.set_xticks(x_pos)
ax.set_xticklabels(names)
ax.set_ylabel("Coefficient")
ax.set_title("Logistic growth: true vs recovered coefficients")
ax.legend()
ax.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_FIGURES, "logistic_coefficients.png"), dpi=150)
plt.close()
