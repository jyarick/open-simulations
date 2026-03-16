"""
Double pendulum system for Lagrangian Mechanics Lab.

Two generalized coordinates: θ₁(t), θ₂(t).
Pivot at origin; rod 1 to mass 1; rod 2 from mass 1 to mass 2.
"""

from sympy import symbols, sin, cos, diff, lambdify, simplify
from lagrangian_lab.core.euler_lagrange import derive_euler_lagrange, solve_for_accelerations


# --- Symbolic definitions ---
t = symbols("t", real=True)
theta_1 = symbols("theta_1", real=True)
theta_2 = symbols("theta_2", real=True)
theta_1_dot = symbols("theta_1_dot", real=True)
theta_2_dot = symbols("theta_2_dot", real=True)
m1, m2, l1, l2, g = symbols("m1 m2 l1 l2 g", real=True, positive=True)

# Positions (pivot at origin, y positive down)
# Mass 1
x1 = l1 * sin(theta_1)
y1 = -l1 * cos(theta_1)

# Mass 2 (relative to mass 1)
x2 = x1 + l2 * sin(theta_2)
y2 = y1 - l2 * cos(theta_2)

# Velocities (chain rule)
vx1 = diff(x1, theta_1) * theta_1_dot
vy1 = diff(y1, theta_1) * theta_1_dot

vx2 = diff(x2, theta_1) * theta_1_dot + diff(x2, theta_2) * theta_2_dot
vy2 = diff(y2, theta_1) * theta_1_dot + diff(y2, theta_2) * theta_2_dot

# Kinetic energy
T = (1 / 2) * m1 * (vx1**2 + vy1**2) + (1 / 2) * m2 * (vx2**2 + vy2**2)

# Potential energy
V = m1 * g * y1 + m2 * g * y2

# Lagrangian
L = T - V

# Euler–Lagrange
coords = [(theta_1, theta_1_dot), (theta_2, theta_2_dot)]
residuals = derive_euler_lagrange(L, coords, t)
accel_solution = solve_for_accelerations(residuals, coords, t)

# Extract θ̈₁ and θ̈₂ (solution dict keys are the q_ddot symbols from solve_for_accelerations)
theta_1_ddot_expr, theta_2_ddot_expr = list(accel_solution.values())
theta_1_ddot_expr = simplify(theta_1_ddot_expr)
theta_2_ddot_expr = simplify(theta_2_ddot_expr)

# accel_expr for generic notebook: tuple of (θ̈₁, θ̈₂)
accel_expr = (theta_1_ddot_expr, theta_2_ddot_expr)
n_dof = 2


def get_rhs_func():
    """Return a lambdified RHS for solve_ivp. State is [θ₁, θ₂, ω₁, ω₂]."""
    theta_1_ddot_func = lambdify(
        [theta_1, theta_2, theta_1_dot, theta_2_dot, m1, m2, l1, l2, g],
        theta_1_ddot_expr,
        modules=["numpy"],
    )
    theta_2_ddot_func = lambdify(
        [theta_1, theta_2, theta_1_dot, theta_2_dot, m1, m2, l1, l2, g],
        theta_2_ddot_expr,
        modules=["numpy"],
    )

    def rhs(t, state, m1_val, m2_val, l1_val, l2_val, g_val):
        th1, th2, om1, om2 = state
        th1_ddot = theta_1_ddot_func(th1, th2, om1, om2, m1_val, m2_val, l1_val, l2_val, g_val)
        th2_ddot = theta_2_ddot_func(th1, th2, om1, om2, m1_val, m2_val, l1_val, l2_val, g_val)
        return [om1, om2, th1_ddot, th2_ddot]

    return rhs


def make_rhs(m1_val, m2_val, l1_val, l2_val, g_val):
    """
    Create the RHS function for solve_ivp with fixed parameters.

    Returns a function (t, state) -> dstate_dt where state = [θ₁, θ₂, ω₁, ω₂].
    """
    base_rhs = get_rhs_func()
    return lambda t, state: base_rhs(t, state, m1_val, m2_val, l1_val, l2_val, g_val)


def make_energy_funcs(m1_val, m2_val, l1_val, l2_val, g_val):
    """
    Return (T_func, V_func) for numerical energy evaluation.

    Each takes (θ₁, θ₂, ω₁, ω₂) and returns the energy.
    """
    T_func = lambdify(
        [theta_1, theta_2, theta_1_dot, theta_2_dot, m1, m2, l1, l2, g],
        T,
        modules=["numpy"],
    )
    V_func = lambdify(
        [theta_1, theta_2, theta_1_dot, theta_2_dot, m1, m2, l1, l2, g],
        V,
        modules=["numpy"],
    )

    def T_num(th1, th2, om1, om2):
        return T_func(th1, th2, om1, om2, m1_val, m2_val, l1_val, l2_val, g_val)

    def V_num(th1, th2, om1, om2):
        return V_func(th1, th2, om1, om2, m1_val, m2_val, l1_val, l2_val, g_val)

    return T_num, V_num


def angles_to_positions(theta_1_vals, theta_2_vals, l1_val, l2_val):
    """
    Convert angles to Cartesian positions for animation.

    Parameters
    ----------
    theta_1_vals, theta_2_vals : array-like
        Angular displacements (rad).
    l1_val, l2_val : float
        Rod lengths.

    Returns
    -------
    x1, y1, x2, y2 : arrays
        Positions of mass 1 and mass 2.
    """
    import numpy as np
    th1 = np.asarray(theta_1_vals)
    th2 = np.asarray(theta_2_vals)
    x1_pos = l1_val * np.sin(th1)
    y1_pos = -l1_val * np.cos(th1)
    x2_pos = x1_pos + l2_val * np.sin(th2)
    y2_pos = y1_pos - l2_val * np.cos(th2)
    return x1_pos, y1_pos, x2_pos, y2_pos


# --- Public interface (matches other systems) ---
__all__ = [
    "t",
    "theta_1", "theta_2",
    "theta_1_dot", "theta_2_dot",
    "m1", "m2", "l1", "l2", "g",
    "x1", "y1", "x2", "y2",
    "T", "V", "L",
    "residuals",
    "theta_1_ddot_expr", "theta_2_ddot_expr",
    "accel_expr",
    "get_rhs_func",
    "make_rhs",
    "make_energy_funcs",
    "angles_to_positions",
]
