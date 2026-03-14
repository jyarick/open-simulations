import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


def rhs(t, y, r, K):
    x = y[0]
    dxdt = r * x * (1 - x / K)
    return [dxdt]


def true_coefficients_polynomial(r, K, degree=3):
    """
    True SINDy coefficients for logistic growth in polynomial library order.

    dx/dt = r*x*(1 - x/K) = r*x - (r/K)*x^2.
    Library for 1 state: [1, x, x^2, x^3] → coefficients [0, r, -r/K, 0].

    Parameters
    ----------
    r, K : float
        Logistic growth parameters.
    degree : int
        Library degree (must match polynomial_library; default 3).

    Returns
    -------
    Xi_true : ndarray (n_features, 1)
        Coefficient matrix in library order.
    """
    # 1, x, x^2, x^3 for single state
    coefs = [0.0, r, -r / K, 0.0]
    if degree < 3:
        coefs = coefs[: degree + 1]
    return np.array(coefs, dtype=float).reshape(-1, 1)


def simulate_logistic_growth(r=2.0, K=5.0, x0=0.5, t_span=(0, 10), num_points=1000):
    t_eval = np.linspace(t_span[0], t_span[1], num_points)

    sol = solve_ivp(
        fun=lambda t, y: rhs(t, y, r, K),
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
    plt.title("Logistic Growth")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    t, y = simulate_logistic_growth(r=2.0, K=5.0, x0=0.5)
    plot_results(t, y)