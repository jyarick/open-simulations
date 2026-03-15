"""
Deep Time Earth — Simulation state and update logic.

State flow: intro (phase 0,1) → run → loop_hold → reset (sim_t=0, continents reset)
update_visual_state: derives epoch, event, captions, colors from sim_t
update_smoothed_state: dampens life and overlay for smooth transitions
"""

import config
from data import (
    EPOCHS,
    EVENTS,
    get_epoch_at,
    get_active_event,
    event_strength,
    wrap_lon,
    reset_continents,
)


# =============================================================================
# STATE
# =============================================================================
class SimulationState:
    def __init__(self):
        self.sim_t = 0.0
        self.rotation_angle = 0.0
        self.moon_angle = 0.0
        self.cloud_angle = 0.0
        self.light_angle = 0.0

        self.epoch = EPOCHS[0]
        self.active_event = None
        self.event_strength = 0.0

        self.target_life = 0.0
        self.smoothed_life = 0.0

        self.earth_color = "darkblue"
        self.atmosphere_color = "lightcyan"
        self.continent_color = "gray"
        self.surface_tint = None
        self.atmosphere_tint = None
        self.continent_contrast = None

        self.overlay_intensity = 0.0
        self.smoothed_overlay_intensity = 0.0

        self.caption_primary = ""
        self.caption_secondary = ""
        self.caption_tertiary = ""

        self.speed_multiplier = 1
        self.cloud_density = 0.5

        # Runtime: intro, loop hold, pause
        self.intro_phase = 0          # 0=title, 1=subtitle, 2=running
        self.intro_timer = 0.0
        self.loop_holding = False
        self.loop_hold_timer = 0.0
        self.paused = False


# =============================================================================
# EASING
# =============================================================================
def damp(current, target, alpha):
    return current + alpha * (target - current)


# =============================================================================
# UPDATE — Flow: intro → run → loop hold → reset
# =============================================================================
def update_simulation(state, continents):
    mult = state.speed_multiplier
    dt = config.FRAME_DELAY_MS / 1000.0

    # Intro phase: staged title/subtitle, then transition to run
    if state.intro_phase < 2:
        state.intro_timer += dt
        if state.intro_phase == 0:
            if state.intro_timer >= config.INTRO_TITLE_DURATION:
                state.intro_phase = 1
                state.intro_timer = 0
        elif state.intro_phase == 1:
            if state.intro_timer >= config.INTRO_SUBTITLE_DURATION:
                state.intro_phase = 2
        # During intro, advance angles slightly for visual interest
        state.rotation_angle += config.ROTATION_SPEED * mult * 0.3
        state.moon_angle += config.MOON_ORBIT_SPEED * mult * 0.3
        state.cloud_angle += config.CLOUD_DRIFT_SPEED * mult * 0.3
        state.light_angle += config.LIGHT_ROTATION_SPEED * mult * 0.3
        return

    if state.paused:
        return

    # Loop hold: at end of timeline, hold briefly then reset
    if state.loop_holding:
        state.loop_hold_timer -= dt
        if state.loop_hold_timer <= 0:
            state.loop_holding = False
            state.sim_t = 0.0
            reset_continents(continents)
        else:
            state.rotation_angle += config.ROTATION_SPEED * mult
            state.moon_angle += config.MOON_ORBIT_SPEED * mult
            state.cloud_angle += config.CLOUD_DRIFT_SPEED * mult
            state.light_angle += config.LIGHT_ROTATION_SPEED * mult
        return

    state.sim_t += config.SIM_SPEED * mult

    if state.sim_t >= config.LOOP_HOLD_SIM_T:
        state.sim_t = config.LOOP_HOLD_SIM_T
        state.loop_holding = True
        state.loop_hold_timer = config.LOOP_HOLD_AT_END_SEC

    state.rotation_angle += config.ROTATION_SPEED * mult
    state.moon_angle += config.MOON_ORBIT_SPEED * mult
    state.cloud_angle += config.CLOUD_DRIFT_SPEED * mult
    state.light_angle += config.LIGHT_ROTATION_SPEED * mult

    for c in continents:
        c["center_lon"] += c["drift_lon"] * mult
        c["center_lat"] += c["drift_lat"] * mult
        c["center_lat"] = max(-89, min(89, c["center_lat"]))
        c["center_lon"] = wrap_lon(c["center_lon"])


def update_visual_state(state):
    # Loop hold: show "Present Day" caption and final-epoch visuals
    if state.loop_holding:
        epoch = get_epoch_at(1.0)
        state.caption_primary = "Present Day"
        state.caption_secondary = "Earth today — ready to cycle"
        state.caption_tertiary = "Press R to restart anytime"
        state.epoch = epoch
        state.active_event = None
        state.event_strength = 0.0
        state.target_life = 0.95
        state.overlay_intensity = 0.0
        state.earth_color = epoch["earth_color"]
        state.atmosphere_color = epoch["atmosphere_color"]
        state.continent_color = epoch["continent_color"]
        state.cloud_density = epoch["cloud_density"]
        return

    t = state.sim_t % 1.0
    epoch = get_epoch_at(t)
    ev = get_active_event(t)

    state.epoch = epoch
    state.active_event = ev

    base_life = epoch["base_life"]
    life_mult = 1.0
    state.surface_tint = None
    state.atmosphere_tint = None
    state.continent_contrast = None

    if ev:
        strength = event_strength(t, ev)
        state.event_strength = strength
        state.overlay_intensity = strength * ev["intensity"]

        life_mult = 1.0 - ev["life_impact"] * strength
        state.surface_tint = ev["surface_tint"]
        state.atmosphere_tint = ev["atmosphere_tint"]
        state.continent_contrast = ev.get("continent_contrast")
        state.caption_primary = ev["caption_title"]
        state.caption_secondary = ev["caption_subtitle"]
        state.caption_tertiary = ev["caption_tertiary"]
    else:
        state.event_strength = 0.0
        state.overlay_intensity = 0.0
        state.caption_primary = epoch["name"]
        state.caption_secondary = epoch["caption_theme"]
        state.caption_tertiary = f"Life: {int(base_life * 100)}%"

    state.target_life = max(0, min(1, base_life * life_mult))
    state.earth_color = epoch["earth_color"]
    state.atmosphere_color = epoch["atmosphere_color"]
    state.continent_color = epoch["continent_color"]
    state.cloud_density = epoch["cloud_density"]


def update_smoothed_state(state):
    state.smoothed_life = damp(
        state.smoothed_life, state.target_life, config.LIFE_SMOOTH_ALPHA
    )
    state.smoothed_overlay_intensity = damp(
        state.smoothed_overlay_intensity,
        state.overlay_intensity,
        config.OVERLAY_SMOOTH_ALPHA,
    )
