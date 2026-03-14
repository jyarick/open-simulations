import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


def rhs(t, y, g_over_L):
    """Nonlinear pendulum: theta'' + (g/L)*sin(theta) = 0. State: [theta, theta']."""
    theta, theta_dot = y[0], y[1]
    d_theta = theta_dot
    d_theta_dot = -(g_over_L) * np.sin(theta)
    return [d_theta, d_theta_dot]


def true_coefficients_polynomial(g_over_L, degree=3):
    """
    True SINDy coefficients for nonlinear pendulum under polynomial approximation.

    Exact: d(theta)/dt = theta',  d(theta')/dt = -(g/L)*sin(theta).
    With sin(theta) ≈ theta - theta^3/6 (small-angle + first nonlinear term),
    d(theta')/dt ≈ -(g/L)*theta + (g/L)/6 * theta^3.
    Library for 2 states degree 3: [1, x0, x1, ..., x0^3, ...].
    So eq0: coef x1=1.  eq1: coef x0=-g/L, x0^3=(g/L)/6.
    """
    n_feat_deg3 = 10
    Xi = np.array([
        [0, 0],
        [0, -g_over_L],
        [1, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, g_over_L / 6],
        [0, 0],
        [0, 0],
        [0, 0],
    ], dtype=float)
    if degree > 3:
        n_total = (degree + 1) * (degree + 2) // 2
        Xi_full = np.zeros((n_total, 2))
        Xi_full[:n_feat_deg3] = Xi
        return Xi_full
    if degree < 3:
        Xi = Xi[: (degree + 1) * (degree + 2) // 2]
    return Xi


def simulate_nonlinear_pendulum(
    g_over_L=9.81,
    theta0=0.2,
    theta_dot0=0.0,
    t_span=(0, 10),
    num_points=1000,
):
    t_eval = np.linspace(t_span[0], t_span[1], num_points)
    sol = solve_ivp(
        fun=lambda t, y: rhs(t, y, g_over_L),
        t_span=t_span,
        y0=[theta0, theta_dot0],
        t_eval=t_eval,
        method="RK45",
    )
    if not sol.success:
        raise RuntimeError(sol.message)
    return sol.t, sol.y.T


def plot_results(t, y):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
    ax1.plot(t, y[:, 0], label=r"$\theta$")
    ax1.plot(t, y[:, 1], label=r"$\dot{\theta}$")
    ax1.set_xlabel("t")
    ax1.set_ylabel("state")
    ax1.set_title("Nonlinear Pendulum")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax2.plot(y[:, 0], y[:, 1])
    ax2.set_xlabel(r"$\theta$")
    ax2.set_ylabel(r"$\dot{\theta}$")
    ax2.set_title("Phase plane")
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    t, y = simulate_nonlinear_pendulum(g_over_L=9.81, theta0=0.2, theta_dot0=0.0)
    plot_results(t, y)
