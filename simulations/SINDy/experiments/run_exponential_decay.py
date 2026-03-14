"""
Run SINDy on exponential decay: dx/dt = -k x.
"""
import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
RESULTS_FIGURES = os.path.join(PROJECT_ROOT, "results", "figures")
os.makedirs(RESULTS_FIGURES, exist_ok=True)

import numpy as np
import matplotlib.pyplot as plt

from simulations.exponential_decay import simulate_exponential_decay, true_coefficients_polynomial
from sindy.differentiate import estimate_derivative
from sindy.library import polynomial_library
from sindy.sparse_regression import sparse_regression
from sindy.sindy_model import print_equations, print_coefficient_comparison
from sindy.metrics import coefficient_error

# Derivative method: "finite_difference" or "savgol"
DERIVATIVE_METHOD = "savgol"

k = 0.5
t, y = simulate_exponential_decay(k=k, x0=1.0)

# pipeline: derivative -> library -> regression
dydt = estimate_derivative(t, y, method=DERIVATIVE_METHOD, window_length=11, polyorder=3)
Theta, names = polynomial_library(y, degree=2)
Xi = sparse_regression(Theta, dydt, threshold=0.05)

# --- Outputs ---
print("Recovered equation:")
print_equations(Xi, names, state_names=["x"])

print("\nActive coefficients:")
for name, coef in zip(names, Xi[:, 0]):
    if abs(coef) > 1e-6:
        print(f"  {name}: {coef:.6f}")

Xi_true = true_coefficients_polynomial(k, degree=2)
coef_err = print_coefficient_comparison(Xi, Xi_true, names, state_names=["x"])
print(f"\nRelative coefficient error: {coef_err:.6e}")

# --- Trajectory plot ---
fig, ax = plt.subplots(figsize=(6, 3))
ax.plot(t, y[:, 0], "b-", label="x(t)")
ax.set_xlabel("t")
ax.set_ylabel("x")
ax.set_title("Exponential decay: trajectory")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_FIGURES, "exponential_decay_trajectory.png"), dpi=150)
plt.close()
