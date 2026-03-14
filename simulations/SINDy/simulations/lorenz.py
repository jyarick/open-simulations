import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from mpl_toolkits.mplot3d import Axes3D


def rhs(t, y, sigma, rho, beta):
    """Lorenz system: dx/dt = sigma(y-x), dy/dt = x(rho-z)-y, dz/dt = xy - beta*z."""
    x, y, z = y[0], y[1], y[2]
    dxdt = sigma * (y - x)
    dydt = x * (rho - z) - y
    dzdt = x * y - beta * z
    return [dxdt, dydt, dzdt]


def true_coefficients_polynomial(sigma, rho, beta, degree=2):
    """
    True SINDy coefficients for Lorenz in polynomial library order.

    dx/dt = sigma*(x1-x0),  dy/dt = rho*x0 - x1 - x0*x2,  dz/dt = x0*x1 - beta*x2.
    Library for 3 states degree 2: [1, x0, x1, x2, x0^2, x0*x1, x0*x2, x1^2, x1*x2, x2^2].
    """
    n_feat_deg2 = 10
    Xi = np.array([
        [0, 0, 0],
        [-sigma, rho, 0],
        [sigma, -1, 0],
        [0, 0, -beta],
        [0, 0, 0],
        [0, 0, 1],
        [0, -1, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ], dtype=float)
    if degree > 2:
        n_total = (degree + 1) * (degree + 2) * (degree + 3) // 6
        Xi_full = np.zeros((n_total, 3))
        Xi_full[:n_feat_deg2] = Xi
        return Xi_full
    if degree < 2:
        n_total = (degree + 1) * (degree + 2) * (degree + 3) // 6
        Xi = Xi[:n_total]
    return Xi


def simulate_lorenz(
    sigma=10.0,
    rho=28.0,
    beta=8.0 / 3.0,
    x0=1.0,
    y0=1.0,
    z0=1.0,
    t_span=(0, 25),
    num_points=2500,
):
    t_eval = np.linspace(t_span[0], t_span[1], num_points)
    sol = solve_ivp(
        fun=lambda t, y: rhs(t, y, sigma, rho, beta),
        t_span=t_span,
        y0=[x0, y0, z0],
        t_eval=t_eval,
        method="RK45",
    )
    if not sol.success:
        raise RuntimeError(sol.message)
    return sol.t, sol.y.T


def plot_results(t, y):
    x, y_, z = y[:, 0], y[:, 1], y[:, 2]
    fig = plt.figure(figsize=(10, 4))
    ax1 = fig.add_subplot(131)
    ax1.plot(t, x, label="x")
    ax1.plot(t, y_, label="y")
    ax1.plot(t, z, label="z")
    ax1.set_xlabel("t")
    ax1.set_title("Lorenz: time series")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax2 = fig.add_subplot(132, projection="3d")
    ax2.plot(x, y_, z, lw=0.5)
    ax2.set_xlabel("x")
    ax2.set_ylabel("y")
    ax2.set_zlabel("z")
    ax2.set_title("Attractor")
    ax3 = fig.add_subplot(133)
    ax3.plot(x, z)
    ax3.set_xlabel("x")
    ax3.set_ylabel("z")
    ax3.set_title("x-z projection")
    ax3.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    t, y = simulate_lorenz(sigma=10, rho=28, beta=8/3, x0=1, y0=1, z0=1)
    plot_results(t, y)
