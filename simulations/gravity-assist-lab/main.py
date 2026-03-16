"""
Gravity Assist Lab - Main entry point.
Real-time 2D gravitational slingshot simulation with interactive controls.
"""

import pygame
import sys

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    PANEL_WIDTH,
    TIME_SCALE_MIN,
    TIME_SCALE_MAX,
    VIEW_SCALE_MIN,
    VIEW_SCALE_MAX,
    TRAIL_LENGTH,
    TRAIL_LENGTH_MIN,
    TRAIL_LENGTH_MAX,
)
from simulation import Simulation
from renderer import Renderer
from ui import Slider, Button, Checkbox, ControlPanel, COLOR_PANEL_BG


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Gravity Assist Lab")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    viewport_w = SCREEN_WIDTH - PANEL_WIDTH
    viewport_h = SCREEN_HEIGHT
    viewport = (0, 0, viewport_w, viewport_h)

    sim = Simulation()
    renderer = Renderer(
        screen,
        show_trails=True,
        show_velocity_arrows=True,
        show_gravity_rings=True,
        show_hud=True,
    )

    # Control panel
    panel_x = viewport_w
    panel = ControlPanel(panel_x, 0, PANEL_WIDTH, SCREEN_HEIGHT)
    panel.rect = pygame.Rect(panel_x, 0, PANEL_WIDTH, SCREEN_HEIGHT)

    y = 45
    row_h = 50

    # Time scale slider
    time_slider = Slider(panel_x + 15, y, PANEL_WIDTH - 30, sim.time_scale, TIME_SCALE_MIN, TIME_SCALE_MAX, "Time scale", 1)
    panel.add_slider(time_slider)
    y += row_h

    # View scale (zoom) slider
    zoom_slider = Slider(panel_x + 15, y, PANEL_WIDTH - 30, sim.view_scale, VIEW_SCALE_MIN, VIEW_SCALE_MAX, "Zoom", 1)
    panel.add_slider(zoom_slider)
    y += row_h

    # Trail length slider
    trail_slider = Slider(panel_x + 15, y, PANEL_WIDTH - 30, TRAIL_LENGTH, TRAIL_LENGTH_MIN, TRAIL_LENGTH_MAX, "Trail length", 0)
    panel.add_slider(trail_slider)
    y += row_h

    # Initial speed slider (for next launch)
    sc = sim.preset["spacecraft"]
    speed_slider = Slider(panel_x + 15, y, PANEL_WIDTH - 30, sc["speed"], 0.3, 1.2, "Launch speed", 2)
    panel.add_slider(speed_slider)
    y += row_h

    # Initial angle slider
    angle_slider = Slider(panel_x + 15, y, PANEL_WIDTH - 30, sc["angle_deg"], -45, 45, "Launch angle (°)", 1)
    panel.add_slider(angle_slider)
    y += row_h + 10

    # Checkboxes
    trails_cb = Checkbox(panel_x + 15, y, "Trails", renderer.show_trails, lambda v: setattr(renderer, "show_trails", v))
    panel.add_checkbox(trails_cb)
    y += 28
    arrows_cb = Checkbox(panel_x + 15, y, "Velocity arrows", renderer.show_velocity_arrows, lambda v: setattr(renderer, "show_velocity_arrows", v))
    panel.add_checkbox(arrows_cb)
    y += 28
    rings_cb = Checkbox(panel_x + 15, y, "Gravity rings", renderer.show_gravity_rings, lambda v: setattr(renderer, "show_gravity_rings", v))
    panel.add_checkbox(rings_cb)
    y += 28
    hud_cb = Checkbox(panel_x + 15, y, "HUD", renderer.show_hud, lambda v: setattr(renderer, "show_hud", v))
    panel.add_checkbox(hud_cb)
    y += 40

    # Buttons
    btn_w = PANEL_WIDTH - 30
    btn_h = 32

    def _on_reset() -> None:
        sim._override_speed = None
        sim._override_angle = None
        sim.reset()
        sync_sliders_from_preset()

    reset_btn = Button(panel_x + 15, y, btn_w, btn_h, "Reset (R)", _on_reset)
    panel.add_button(reset_btn)
    y += btn_h + 8

    new_btn = Button(panel_x + 15, y, btn_w, btn_h, "New spacecraft (N)", lambda: _on_new_spacecraft())
    panel.add_button(new_btn)
    y += btn_h + 8

    def _prev_preset() -> None:
        sim.prev_preset()
        sync_sliders_from_preset()

    def _next_preset() -> None:
        sim.next_preset()
        sync_sliders_from_preset()

    prev_btn = Button(panel_x + 15, y, btn_w // 2 - 4, btn_h, "◀ Preset", _prev_preset)
    panel.add_button(prev_btn)
    next_btn = Button(panel_x + 15 + btn_w // 2 + 4, y, btn_w // 2 - 4, btn_h, "Preset ▶", _next_preset)
    panel.add_button(next_btn)

    def _on_new_spacecraft() -> None:
        sim.set_initial_override(speed_slider.value, angle_slider.value)
        sim.new_spacecraft()

    def sync_sliders_from_preset() -> None:
        sc = sim.preset["spacecraft"]
        speed_slider.value = sc["speed"]
        angle_slider.value = sc["angle_deg"]

    # Run multiple physics steps per frame for smooth motion
    steps_per_frame = max(1, int(1.0 / (FPS * sim.dt)))
    steps_per_frame = min(steps_per_frame, 15)

    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif panel.handle_event(event):
                pass  # UI handled it
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    sim.paused = not sim.paused
                elif event.key == pygame.K_r:
                    sim._override_speed = None
                    sim._override_angle = None
                    sim.reset()
                    sync_sliders_from_preset()
                elif event.key == pygame.K_n:
                    sim.set_initial_override(speed_slider.value, angle_slider.value)
                    sim.new_spacecraft()
                elif event.key == pygame.K_p:
                    sim.toggle_planet_pause()
                elif event.key == pygame.K_t:
                    renderer.show_trails = not renderer.show_trails
                    trails_cb.checked = renderer.show_trails
                elif event.key == pygame.K_v:
                    renderer.show_velocity_arrows = not renderer.show_velocity_arrows
                    arrows_cb.checked = renderer.show_velocity_arrows
                elif event.key == pygame.K_g:
                    renderer.show_gravity_rings = not renderer.show_gravity_rings
                    rings_cb.checked = renderer.show_gravity_rings
                elif event.key == pygame.K_h:
                    renderer.show_hud = not renderer.show_hud
                    hud_cb.checked = renderer.show_hud
                elif event.key == pygame.K_LEFTBRACKET:
                    sim.prev_preset()
                    sync_sliders_from_preset()
                elif event.key == pygame.K_RIGHTBRACKET:
                    sim.next_preset()
                    sync_sliders_from_preset()

        # Apply slider values (live updates)
        sim.time_scale = time_slider.value
        sim.view_scale = zoom_slider.value
        sim.set_trail_length(int(trail_slider.value))

        # Physics steps
        for _ in range(steps_per_frame):
            sim.step()

        # Render
        viewport = (0, 0, viewport_w, viewport_h)
        renderer.render_frame(sim, viewport, sim.view_scale)

        # Draw control panel
        pygame.draw.rect(screen, COLOR_PANEL_BG, panel.rect)
        pygame.draw.rect(screen, (50, 50, 70), panel.rect, 1)
        for slider in panel.sliders:
            slider.draw(screen)
        for checkbox in panel.checkboxes:
            checkbox.draw(screen)
        for button in panel.buttons:
            button.draw(screen)
        # Panel title and preset name
        font = pygame.font.Font(None, 24)
        title = font.render("Controls", True, (180, 190, 210))
        screen.blit(title, (panel_x + 12, 12))
        preset_label = font.render(sim.preset["name"], True, (140, 160, 200))
        screen.blit(preset_label, (panel_x + 12, SCREEN_HEIGHT - 25))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
