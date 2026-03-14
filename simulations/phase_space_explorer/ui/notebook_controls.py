"""
Notebook UI: build parameter and initial-condition sliders from system metadata.
Reusable from Jupyter; no UI logic inside system definitions.
"""

from ipywidgets import FloatSlider, Dropdown


def _slider_from_info(name, info):
    return FloatSlider(
        value=info["default"],
        min=info["min"],
        max=info["max"],
        step=info.get("step", (info["max"] - info["min"]) / 100),
        description=name,
        continuous_update=True,
    )


def sliders_for_system(system):
    """
    Return (param_sliders_dict, ic_sliders_dict) of ipywidgets FloatSliders
    built from system.parameter_info and system.initial_condition_info.
    """
    param_sliders = {
        name: _slider_from_info(name, info)
        for name, info in system.parameter_info.items()
    }
    ic_sliders = {
        name: _slider_from_info(name, info)
        for name, info in system.initial_condition_info.items()
    }
    return param_sliders, ic_sliders


def params_from_sliders(param_sliders):
    """Read current parameter dict from slider values."""
    return {name: s.value for name, s in param_sliders.items()}


def y0_from_sliders(ic_sliders, system):
    """Build initial state vector in system order from ic_sliders."""
    keys = list(system.initial_condition_info.keys())
    return [ic_sliders[k].value for k in keys]
