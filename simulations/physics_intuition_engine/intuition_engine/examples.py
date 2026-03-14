EXAMPLES = {
    "Undamped oscillator": "m*diff(x(t), t, 2) + k*x(t) = 0",
    "Damped oscillator": "m*diff(x(t), t, 2) + b*diff(x(t), t) + k*x(t) = 0",
    "Driven damped oscillator": "m*diff(x(t), t, 2) + b*diff(x(t), t) + k*x(t) = F0*cos(omega*t)",
    "Constant forcing": "m*diff(x(t), t, 2) + b*diff(x(t), t) + k*x(t) = F0",
    "Critical damping example": "diff(x(t), t, 2) + 4*diff(x(t), t) + 4*x(t) = 0",
}

SYSTEM_EXAMPLES = {
    "Linear 2D (stable node)": "diff(x(t), t) = -x + y; diff(y(t), t) = x - 2*y",
    "Simple harmonic (center)": "diff(x(t), t) = y; diff(y(t), t) = -x",
    "Saddle": "diff(x(t), t) = x + y; diff(y(t), t) = x - y",
}