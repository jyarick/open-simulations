import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


def rhs(t, y, k):
    x = y[0]
    dxdt = -k * x
    return [dxdt]


def true_coefficients_polynomial(k, degree=2):
    """
    True SINDy coefficients for exponential decay in polynomial library order.

    dx/dt = -k*x. Library for 1 state: [1, x0, x0^2, ...] -> coefficients [0, -k, 0, ...].
    """
    # 1 state: n_features = 1 + degree (constant + x, x^2, ..., x^degree)
    n = 1 + degree
    coefs = [0.0, -k] + [0.0] * (n - 2)
    return np.array(coefs[:n], dtype=float).reshape(-1, 1)


def simulate_exponential_decay(k=0.5, x0=1.0, t_span=(0, 10), num_points=1000):
    t_eval = np.linspace(t_span[0], t_span[1], num_points)

    sol = solve_ivp(
        fun=lambda t, y: rhs(t, y, k),
        t_span=t_span,
        y0=[x0],
        t_eval=t_eval,
        method="RK45",
    )

    if not sol.success:
        raise RuntimeError(sol.message)

    t = sol.t
    y = sol.y.T  # shape: (n_samples, 1)
    return t, y


def plot_results(t, y):
    plt.figure(figsize=(8, 4))
    plt.plot(t, y[:, 0], label="x(t)")
    plt.xlabel("t")
    plt.ylabel("x")
    plt.title("Exponential Decay")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    t, y = simulate_exponential_decay(k=0.5, x0=1.0)
    plot_results(t, y)