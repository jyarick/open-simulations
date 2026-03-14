import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


def rhs(t, y, beta, omega):
    x, v = y
    dxdt = v
    dvdt = -2 * beta * v - (omega ** 2) * x
    return [dxdt, dvdt]


def true_coefficients_polynomial(beta, omega, degree=2):
    """
    True SINDy coefficients for damped oscillator in polynomial library order.

    dx0/dt = x1,  dx1/dt = -omega^2*x0 - 2*beta*x1.
    Library for 2 states degree 2: [1, x0, x1, x0^2, x0*x1, x1^2].
    """
    n_feat_deg2 = 6
    Xi = np.array([
        [0, 0],
        [0, -omega ** 2],
        [1, -2 * beta],
        [0, 0],
        [0, 0],
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


def simulate_damped_harmonic_oscillator(
    beta=0.2,
    omega=2.0,
    x0=1.0,
    v0=0.0,
    t_span=(0, 15),
    num_points=1000,
):
    t_eval = np.linspace(t_span[0], t_span[1], num_points)

    sol = solve_ivp(
        fun=lambda t, y: rhs(t, y, beta, omega),
        t_span=t_span,
        y0=[x0, v0],
        t_eval=t_eval,
        method="RK45",
    )

    if not sol.success:
        raise RuntimeError(sol.message)

    t = sol.t
    y = sol.y.T  # shape: (n_samples, 2)
    return t, y


def plot_results(t, y):
    x = y[:, 0]
    v = y[:, 1]

    plt.figure(figsize=(8, 4))
    plt.plot(t, x, label="x(t)")
    plt.plot(t, v, label="v(t)")
    plt.xlabel("t")
    plt.ylabel("state")
    plt.title("Damped Harmonic Oscillator")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(5, 5))
    plt.plot(x, v)
    plt.xlabel("x")
    plt.ylabel("v")
    plt.title("Phase Space")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    t, y = simulate_damped_harmonic_oscillator(beta=0.2, omega=2.0, x0=1.0, v0=0.0)
    plot_results(t, y)