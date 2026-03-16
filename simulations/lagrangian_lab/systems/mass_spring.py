"""
Mass-spring oscillator for Lagrangian Mechanics Lab.

Single mass attached to a spring moving in 1D.
Generalized coordinate: x(t). Wall at x=0, spring connects wall to mass.
"""

from sympy import symbols, lambdify, simplify
from lagrangian_lab.core.euler_lagrange import derive_euler_lagrange, solve_for_accelerations


# --- Symbolic definitions ---
t = symbols("t", real=True)
x = symbols("x", real=True)
x_dot = symbols("x_dot", real=True)
m, k = symbols("m k", real=True, positive=True)

# Position: mass at x (1D along x-axis). For visualization, (x, 0).
# Velocity: x_dot

# Kinetic energy: T = (1/2) m ẋ²
T = (1 / 2) * m * x_dot**2

# Potential energy: V = (1/2) k x² (spring potential, equilibrium at x=0)
V = (1 / 2) * k * x**2

# Lagrangian
L = T - V

# Euler–Lagrange
coords = [(x, x_dot)]
residuals = derive_euler_lagrange(L, coords, t)
x_ddot_solution = solve_for_accelerations(residuals, coords, t)

# Extract x_ddot expression
x_ddot_expr = list(x_ddot_solution.values())[0]
x_ddot_expr = simplify(x_ddot_expr)


def get_rhs_func():
    """Return a lambdified RHS for solve_ivp. State is [x, v]."""
    x_ddot_func = lambdify(
        [x, x_dot, m, k],
        x_ddot_expr,
        modules=["numpy"],
    )

    def rhs(t, state, m_val, k_val):
        x_val, v_val = state
        x_ddot_val = x_ddot_func(x_val, v_val, m_val, k_val)
        return [v_val, x_ddot_val]

    return rhs


def make_rhs(m_val, k_val):
    """
    Create the RHS function for solve_ivp with fixed parameters.

    Returns a function (t, state) -> dstate_dt where state = [x, v].
    """
    base_rhs = get_rhs_func()
    return lambda t, state: base_rhs(t, state, m_val, k_val)


def make_energy_funcs(m_val, k_val):
    """
    Return (T_func, V_func) for numerical energy evaluation.

    Each takes (x, v) and returns the energy.
    """
    T_func = lambdify([x, x_dot, m, k], T, modules=["numpy"])
    V_func = lambdify([x, x_dot, m, k], V, modules=["numpy"])

    def T_num(x_val, v_val):
        return T_func(x_val, v_val, m_val, k_val)

    def V_num(x_val, v_val):
        return V_func(x_val, v_val, m_val, k_val)

    return T_num, V_num


def get_position(x_vals):
    """
    Convert x to Cartesian position (x, y) for animation.

    Mass moves horizontally: returns (x, 0).

    Parameters
    ----------
    x_vals : array-like
        Position(s) of the mass.

    Returns
    -------
    x_pos, y_pos : arrays
        (x_vals, zeros) for horizontal motion.
    """
    import numpy as np
    x_vals = np.asarray(x_vals)
    return x_vals, np.zeros_like(x_vals)


# --- Public interface (matches pendulum) ---
# Use accel_expr as alias for generic notebook access
accel_expr = x_ddot_expr
n_dof = 1

__all__ = [
    "t",
    "x",
    "x_dot",
    "m", "k",
    "T", "V", "L",
    "residuals",
    "x_ddot_expr",
    "accel_expr",
    "get_rhs_func",
    "make_rhs",
    "make_energy_funcs",
    "get_position",
]
