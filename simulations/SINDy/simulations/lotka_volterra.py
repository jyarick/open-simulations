import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


def rhs(t, y, a, b, c, d):
    """Lotka-Volterra: prey x, predator y. dx/dt = a*x - b*x*y, dy/dt = -c*y + d*x*y."""
    x, y_val = y[0], y[1]
    dxdt = a * x - b * x * y_val
    dydt = -c * y_val + d * x * y_val
    return [dxdt, dydt]


def true_coefficients_polynomial(a, b, c, d, degree=2):
    """
    True SINDy coefficients for Lotka-Volterra in polynomial library order.

    dx0/dt = a*x0 - b*x0*x1,  dx1/dt = -c*x1 + d*x0*x1.
    Library for 2 states degree 2: [1, x0, x1, x0^2, x0*x1, x1^2].
    """
    n_feat_deg2 = 6
    Xi = np.array([
        [0, 0],
        [a, 0],
        [0, -c],
        [0, 0],
        [-b, d],
        [0, 0],
    ], dtype=float)
    if degree > 2:
        n_total = (degree + 1) * (degree + 2) // 2
        Xi_full = np.zeros((n_total, 2))
        Xi_full[:n_feat_deg2] = Xi
        return Xi_full
    if degree < 2:
        Xi = Xi[:3]
    return Xi


def simulate_lotka_volterra(
    a=1.0,
    b=0.5,
    c=1.0,
    d=0.5,
    x0=2.0,
    y0=1.0,
    t_span=(0, 20),
    num_points=1000,
):
    t_eval = np.linspace(t_span[0], t_span[1], num_points)
    sol = solve_ivp(
        fun=lambda t, y: rhs(t, y, a, b, c, d),
        t_span=t_span,
        y0=[x0, y0],
        t_eval=t_eval,
        method="RK45",
    )
    if not sol.success:
        raise RuntimeError(sol.message)
    return sol.t, sol.y.T


def plot_results(t, y):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
    ax1.plot(t, y[:, 0], label="prey x")
    ax1.plot(t, y[:, 1], label="predator y")
    ax1.set_xlabel("t")
    ax1.set_ylabel("population")
    ax1.set_title("Lotka-Volterra")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax2.plot(y[:, 0], y[:, 1])
    ax2.set_xlabel("prey x")
    ax2.set_ylabel("predator y")
    ax2.set_title("Phase plane")
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    t, y = simulate_lotka_volterra(a=1.0, b=0.5, c=1.0, d=0.5, x0=2.0, y0=1.0)
    plot_results(t, y)
