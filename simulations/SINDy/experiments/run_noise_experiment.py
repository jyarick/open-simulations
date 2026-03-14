"""
Noise robustness: sweep noise levels, run SINDy, plot noise vs coefficient error.
Compares derivative methods: Savitzky-Golay vs finite difference.
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
from sindy.add_noise import add_noise
from sindy.differentiate import estimate_derivative
from sindy.library import polynomial_library
from sindy.sparse_regression import sparse_regression
from sindy.metrics import coefficient_error

# Fixed dynamics and data
r, K = 2.0, 5.0
t, y_clean = simulate_logistic_growth(r=r, K=K, x0=0.5)
Xi_true = true_coefficients_polynomial(r, K, degree=3)

noise_levels = [0, 0.01, 0.05, 0.1]
random_seed = 42

def run_sindy_at_noise(noise_std, method):
    y = add_noise(y_clean, noise_std=noise_std, random_seed=random_seed)
    dydt = estimate_derivative(t, y, method=method, window_length=11, polyorder=3)
    Theta, names = polynomial_library(y, degree=3)
    Xi = sparse_regression(Theta, dydt, threshold=0.05)
    return coefficient_error(Xi, Xi_true)

# Sweep noise for both derivative methods
errors_savgol = []
errors_fd = []
for noise_level in noise_levels:
    err_sg = run_sindy_at_noise(noise_level, "savgol")
    err_fd = run_sindy_at_noise(noise_level, "finite_difference")
    errors_savgol.append(err_sg)
    errors_fd.append(err_fd)
    print(f"noise_std = {noise_level:.2f}  savgol err = {err_sg:.6e}  finite_diff err = {err_fd:.6e}")

errors_savgol = np.array(errors_savgol)
errors_fd = np.array(errors_fd)

# Plot: noise level vs coefficient error (both methods)
fig, ax = plt.subplots(figsize=(6, 4))
ax.semilogy(noise_levels, errors_savgol, "o-", color="C0", linewidth=2, markersize=8, label="Savitzky-Golay")
ax.semilogy(noise_levels, errors_fd, "s-", color="C1", linewidth=2, markersize=8, label="Finite difference")
ax.set_xlabel("Noise level (std)")
ax.set_ylabel("Coefficient error (relative)")
ax.set_title("SINDy: noise vs coefficient error by derivative method")
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xticks(noise_levels)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_FIGURES, "noise_vs_error.pdf"))
plt.savefig(os.path.join(RESULTS_FIGURES, "noise_vs_error.png"), dpi=150)
plt.close()
print(f"\nPlots saved to {RESULTS_FIGURES}/")
