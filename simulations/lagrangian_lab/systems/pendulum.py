"""
Simple pendulum system for Lagrangian Mechanics Lab.

Generalized coordinate: θ(t). Position: x = l·sin(θ), y = -l·cos(θ).
"""

from sympy import symbols, sin, cos, diff, lambdify, simplify
from lagrangian_lab.core.euler_lagrange import derive_euler_lagrange, solve_for_accelerations


# --- Symbolic definitions ---
t = symbols("t", real=True)
theta = symbols("theta", real=True)
theta_dot = symbols("theta_dot", real=True)
m, l, g = symbols("m l g", real=True, positive=True)

# Cartesian position (pivot at origin, y positive downward convention: y = -l*cos(θ))
x = l * sin(theta)
y = -l * cos(theta)

# Velocities (chain rule: d/dt of x, y in terms of theta, theta_dot)
vx = diff(x, theta) * theta_dot
vy = diff(y, theta) * theta_dot

# Kinetic energy: T = (1/2) m (vx² + vy²)
T = (1 / 2) * m * (vx**2 + vy**2)

# Potential energy: V = m g y (y measured from pivot; bob below pivot has negative y, so V = -m g l cos(θ))
# Standard convention: V = 0 at bottom (θ=0). So V = m g l (1 - cos(θ)) or V = -m g l cos(θ).
# With y = -l cos(θ), V = m g y = -m g l cos(θ). At θ=0: V = -m g l (minimum).
# For "V = 0 at pivot" we'd use V = m g (y_pivot - y_bob) = m g l (1 - cos(θ)).
# User said "potential energy should be consistent and simple". Using V = -m g l cos(θ)
# gives V_min at θ=0 (bottom), which is standard.
V = m * g * y  # = -m g l cos(θ)

# Lagrangian
L = T - V

# Euler–Lagrange
coords = [(theta, theta_dot)]
residuals = derive_euler_lagrange(L, coords, t)
theta_ddot_solution = solve_for_accelerations(residuals, coords, t)

# Extract theta_ddot expression (key for solve_ivp)
theta_ddot_sym = symbols("theta_ddot", real=True)
theta_ddot_expr = theta_ddot_solution.get(theta_ddot_sym, residuals[0])
# Actually the solution dict keys are the symbols we created in solve_for_accelerations
# which have name "theta_ddot". So we need to get the right key.
# The keys in solution are the q_ddot symbols from solve_for_accelerations.
# Let me get the first (and only) value from the solution dict.
theta_ddot_expr = list(theta_ddot_solution.values())[0]
theta_ddot_expr = simplify(theta_ddot_expr)


def get_rhs_func():
    """
    Return a lambdified RHS for solve_ivp.

    State is [theta, omega]. Returns d(state)/dt = [omega, theta_ddot].

    The returned function has signature (t, state) -> dstate_dt.
    It is closed over parameters (m, l, g) - use make_rhs(m, l, g) for specific values.
    """
    # For a generic RHS we need to accept m, l, g as arguments.
    # So we lambdify (theta, theta_dot, m, l, g) -> theta_ddot
    theta_ddot_func = lambdify(
        [theta, theta_dot, m, l, g],
        theta_ddot_expr,
        modules=["numpy"],
    )

    def rhs(t, state, m_val, l_val, g_val):
        th, om = state
        th_ddot = theta_ddot_func(th, om, m_val, l_val, g_val)
        return [om, th_ddot]

    return rhs


def make_rhs(m_val, l_val, g_val):
    """
    Create the RHS function for solve_ivp with fixed parameters.

    Returns a function (t, state) -> dstate_dt where state = [theta, omega].
    """
    base_rhs = get_rhs_func()
    return lambda t, state: base_rhs(t, state, m_val, l_val, g_val)


def make_energy_funcs(m_val, l_val, g_val):
    """
    Return (T_func, V_func) for numerical energy evaluation.

    Each takes (theta, omega) and returns the energy.
    """
    T_func = lambdify([theta, theta_dot, m, l, g], T, modules=["numpy"])
    V_func = lambdify([theta, theta_dot, m, l, g], V, modules=["numpy"])

    def T_num(th, om):
        return T_func(th, om, m_val, l_val, g_val)

    def V_num(th, om):
        return V_func(th, om, m_val, l_val, g_val)

    return T_num, V_num


def theta_to_xy(theta_vals, l_val):
    """
    Convert theta (rad) to bob Cartesian position (x, y) for animation.

    Uses x = l*sin(θ), y = -l*cos(θ) with pivot at origin.

    Parameters
    ----------
    theta_vals : array-like
        Angular displacement(s) in radians.
    l_val : float
        Pendulum length.

    Returns
    -------
    x, y : arrays
        Bob position(s).
    """
    import numpy as np
    theta_vals = np.asarray(theta_vals)
    x_bob = l_val * np.sin(theta_vals)
    y_bob = -l_val * np.cos(theta_vals)
    return x_bob, y_bob


# --- Public interface (for notebook) ---
# accel_expr for generic notebook access (matches mass_spring)
accel_expr = theta_ddot_expr
n_dof = 1

__all__ = [
    "t",
    "theta",
    "theta_dot",
    "m", "l", "g",
    "x", "y",
    "T", "V", "L",
    "residuals",
    "theta_ddot_expr",
    "accel_expr",
    "get_rhs_func",
    "make_rhs",
    "make_energy_funcs",
    "theta_to_xy",
]
