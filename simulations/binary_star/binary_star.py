"""
Binary Star Gravitational Simulation — Pygame
Drag the sliders to change each star's mass and watch the orbits update in real time.

Controls:
  - Star 1 mass slider (coral)
  - Star 2 mass slider (blue)
  - Speed slider
  - Reset button
  - Esc to quit

Requirements: pip install pygame
"""

import pygame
import math
import random
import sys

# ─── Constants ────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1000, 640
SIM_W = 700
PANEL_X = SIM_W
PANEL_W = WIDTH - SIM_W
G = 800
TRAIL_LEN = 300
FPS = 60

# ─── Colors ───────────────────────────────────────────────────────────────────
BG = (10, 14, 26)
PANEL_BG = (18, 22, 34)
STAR1_COL = (240, 153, 123)
STAR2_COL = (133, 183, 235)
WHITE = (255, 255, 255)
GRAY = (140, 140, 155)
DARK_GRAY = (50, 54, 66)
ACCENT = (80, 85, 100)
BTN_BG = (35, 40, 55)
BTN_HOVER = (55, 62, 82)
SLIDER_TRACK = (40, 44, 58)
SLIDER_FILL_SPD = (130, 130, 150)


def make_bg_stars(n=200):
    return [
        (random.randint(0, SIM_W), random.randint(0, HEIGHT),
         random.uniform(0.4, 1.4), random.randint(120, 220))
        for _ in range(n)
    ]


def star_radius(m):
    return 4 + m ** 0.4 * 0.8


def init_bodies(m1, m2):
    cx, cy = SIM_W / 2, HEIGHT / 2
    total = m1 + m2
    sep = 160
    r1 = sep * m2 / total
    r2 = sep * m1 / total
    orb_v = math.sqrt(G * total / sep)
    v1 = orb_v * m2 / total
    v2 = orb_v * m1 / total
    s1 = {"x": cx + r1, "y": cy, "vx": 0.0, "vy": -v1, "m": float(m1)}
    s2 = {"x": cx - r2, "y": cy, "vx": 0.0, "vy": v2, "m": float(m2)}
    return s1, s2


def physics_step(s1, s2, dt):
    dx = s2["x"] - s1["x"]
    dy = s2["y"] - s1["y"]
    dist = max(math.hypot(dx, dy), 2.0)
    F = G * s1["m"] * s2["m"] / (dist * dist)
    fx, fy = F * dx / dist, F * dy / dist
    s1["vx"] += fx / s1["m"] * dt
    s1["vy"] += fy / s1["m"] * dt
    s2["vx"] -= fx / s2["m"] * dt
    s2["vy"] -= fy / s2["m"] * dt
    s1["x"] += s1["vx"] * dt
    s1["y"] += s1["vy"] * dt
    s2["x"] += s2["vx"] * dt
    s2["y"] += s2["vy"] * dt


def draw_trail(surf, trail, color):
    n = len(trail)
    if n < 2:
        return
    for i in range(1, n):
        a = i / n
        c = (int(color[0] * a), int(color[1] * a), int(color[2] * a))
        w = max(1, int(a * 2.5))
        pygame.draw.line(surf, c,
                         (int(trail[i - 1][0]), int(trail[i - 1][1])),
                         (int(trail[i][0]), int(trail[i][1])), w)


def draw_glow(surf, x, y, r, color):
    size = max(4, int(r * 8))
    glow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    center = size // 2
    for i in range(center, 0, -1):
        alpha = int(60 * (1 - i / center))
        pygame.draw.circle(glow_surf, (*color, alpha), (center, center), i)
    surf.blit(glow_surf, (int(x - center), int(y - center)))


def draw_com(surf, s1, s2):
    total = s1["m"] + s2["m"]
    cx = (s1["x"] * s1["m"] + s2["x"] * s2["m"]) / total
    cy = (s1["y"] * s1["m"] + s2["y"] * s2["m"]) / total
    cs = pygame.Surface((20, 20), pygame.SRCALPHA)
    c = (255, 255, 255, 60)
    pygame.draw.line(cs, c, (0, 10), (20, 10), 1)
    pygame.draw.line(cs, c, (10, 0), (10, 20), 1)
    pygame.draw.circle(cs, c, (10, 10), 4, 1)
    surf.blit(cs, (int(cx - 10), int(cy - 10)))


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Binary Star Simulation")
    clock = pygame.time.Clock()

    font_sm = pygame.font.SysFont(None, 20)
    font_md = pygame.font.SysFont(None, 24)
    font_lg = pygame.font.SysFont(None, 32)
    font_title = pygame.font.SysFont(None, 26)

    # ─── UI layout ────────────────────────────────────────────────────────────
    left = PANEL_X + 20
    sw = PANEL_W - 40  # slider width

    # Each slider: (x, track_y, width, min, max, value, label, color, unit)
    # track_y is the vertical center of the track line
    slider_m1 = {"x": left, "track_y": 100, "w": sw, "min": 1, "max": 200,
                 "val": 100, "label": "Star 1 mass", "color": STAR1_COL,
                 "unit": "M\u2609", "dragging": False}
    slider_m2 = {"x": left, "track_y": 190, "w": sw, "min": 1, "max": 200,
                 "val": 100, "label": "Star 2 mass", "color": STAR2_COL,
                 "unit": "M\u2609", "dragging": False}
    slider_spd = {"x": left, "track_y": 280, "w": sw, "min": 1, "max": 10,
                  "val": 3, "label": "Speed", "color": SLIDER_FILL_SPD,
                  "unit": "x", "dragging": False}

    all_sliders = [slider_m1, slider_m2, slider_spd]

    btn_rect = pygame.Rect(left, 320, sw, 42)

    # ─── Sim state ────────────────────────────────────────────────────────────
    bg_stars = make_bg_stars()
    s1, s2 = init_bodies(100, 100)
    trail1, trail2 = [], []
    prev_m1, prev_m2 = 100, 100

    # ─── Helpers ──────────────────────────────────────────────────────────────
    def thumb_x(s):
        frac = (s["val"] - s["min"]) / (s["max"] - s["min"])
        return s["x"] + frac * s["w"]

    def set_val_from_mouse(s, mx):
        frac = (mx - s["x"]) / s["w"]
        frac = max(0.0, min(1.0, frac))
        s["val"] = round(s["min"] + frac * (s["max"] - s["min"]))

    def hit_test(s, pos):
        # 50px tall hit zone centered on the track — very generous
        r = pygame.Rect(s["x"] - 10, s["track_y"] - 25, s["w"] + 20, 50)
        return r.collidepoint(pos)

    def draw_one_slider(s):
        ty = s["track_y"]
        label_y = ty - 35

        # Label (top-left)
        lbl_surf = font_sm.render(s["label"], True, GRAY)
        screen.blit(lbl_surf, (s["x"], label_y))

        # Value (top-right)
        val_surf = font_lg.render(str(s["val"]), True, s["color"])
        unit_surf = font_sm.render(" " + s["unit"], True, DARK_GRAY)
        vx = s["x"] + s["w"] - val_surf.get_width() - unit_surf.get_width()
        screen.blit(val_surf, (vx, label_y - 8))
        screen.blit(unit_surf, (vx + val_surf.get_width(), label_y + 2))

        # Track bg
        pygame.draw.rect(screen, SLIDER_TRACK,
                         (s["x"], ty - 3, s["w"], 6), border_radius=3)
        # Track fill
        tx = thumb_x(s)
        fw = int(tx - s["x"])
        if fw > 1:
            pygame.draw.rect(screen, s["color"],
                             (s["x"], ty - 3, fw, 6), border_radius=3)
        # Thumb
        pygame.draw.circle(screen, WHITE, (int(tx), ty), 10)
        pygame.draw.circle(screen, s["color"], (int(tx), ty), 7)

    # ─── Game loop ────────────────────────────────────────────────────────────
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break

            # ── Mouse down: start drag or press button ────────────────────
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for s in all_sliders:
                    if hit_test(s, event.pos):
                        s["dragging"] = True
                        set_val_from_mouse(s, event.pos[0])

                if btn_rect.collidepoint(event.pos):
                    s1, s2 = init_bodies(slider_m1["val"], slider_m2["val"])
                    trail1, trail2 = [], []
                    prev_m1 = slider_m1["val"]
                    prev_m2 = slider_m2["val"]

            # ── Mouse up: stop all drags ──────────────────────────────────
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                for s in all_sliders:
                    s["dragging"] = False

            # ── Mouse move: update dragged sliders ────────────────────────
            if event.type == pygame.MOUSEMOTION:
                for s in all_sliders:
                    if s["dragging"]:
                        set_val_from_mouse(s, event.pos[0])

        if not running:
            break

        # ── Read current slider values ────────────────────────────────────
        m1_val = slider_m1["val"]
        m2_val = slider_m2["val"]
        speed = slider_spd["val"]

        # ── Live mass update (keep positions, recompute velocities) ───────
        if m1_val != prev_m1 or m2_val != prev_m2:
            new_total = float(m1_val + m2_val)
            old_total = s1["m"] + s2["m"]
            com_vx = (s1["vx"] * s1["m"] + s2["vx"] * s2["m"]) / old_total
            com_vy = (s1["vy"] * s1["m"] + s2["vy"] * s2["m"]) / old_total

            s1["m"] = float(m1_val)
            s2["m"] = float(m2_val)

            dx = s2["x"] - s1["x"]
            dy = s2["y"] - s1["y"]
            dist = max(math.hypot(dx, dy), 2.0)
            orb_v = math.sqrt(G * new_total / dist)
            nx, ny = -dy / dist, dx / dist  # perpendicular to separation

            s1["vx"] = com_vx - nx * orb_v * s2["m"] / new_total
            s1["vy"] = com_vy - ny * orb_v * s2["m"] / new_total
            s2["vx"] = com_vx + nx * orb_v * s1["m"] / new_total
            s2["vy"] = com_vy + ny * orb_v * s1["m"] / new_total

            trail1.clear()
            trail2.clear()
            prev_m1, prev_m2 = m1_val, m2_val

        # ── Physics steps ─────────────────────────────────────────────────
        for _ in range(speed):
            physics_step(s1, s2, dt)
            trail1.append((s1["x"], s1["y"]))
            trail2.append((s2["x"], s2["y"]))
            if len(trail1) > TRAIL_LEN:
                trail1.pop(0)
            if len(trail2) > TRAIL_LEN:
                trail2.pop(0)

        # ── Draw: simulation area ─────────────────────────────────────────
        screen.fill(BG)
        for bx, by, br, ba in bg_stars:
            pygame.draw.circle(screen, (ba, ba, min(255, ba + 30)),
                               (bx, by), max(1, int(br)))

        draw_trail(screen, trail1, STAR1_COL)
        draw_trail(screen, trail2, STAR2_COL)
        draw_com(screen, s1, s2)

        r1 = star_radius(s1["m"])
        r2 = star_radius(s2["m"])
        draw_glow(screen, s1["x"], s1["y"], r1, STAR1_COL)
        draw_glow(screen, s2["x"], s2["y"], r2, STAR2_COL)
        pygame.draw.circle(screen, WHITE,
                           (int(s1["x"]), int(s1["y"])), max(2, int(r1)))
        pygame.draw.circle(screen, WHITE,
                           (int(s2["x"]), int(s2["y"])), max(2, int(r2)))

        # ── Draw: panel ───────────────────────────────────────────────────
        pygame.draw.rect(screen, PANEL_BG, (PANEL_X, 0, PANEL_W, HEIGHT))
        pygame.draw.line(screen, ACCENT, (PANEL_X, 0), (PANEL_X, HEIGHT), 1)

        title_surf = font_title.render("Binary star controls", True, WHITE)
        screen.blit(title_surf, (left, 24))

        for s in all_sliders:
            draw_one_slider(s)

        # Reset button
        mouse_pos = pygame.mouse.get_pos()
        btn_col = BTN_HOVER if btn_rect.collidepoint(mouse_pos) else BTN_BG
        pygame.draw.rect(screen, btn_col, btn_rect, border_radius=8)
        pygame.draw.rect(screen, ACCENT, btn_rect, 1, border_radius=8)
        btn_txt = font_md.render("Reset simulation", True, WHITE)
        screen.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width() // 2,
                              btn_rect.centery - btn_txt.get_height() // 2))

        # Mass ratio display
        mx = max(m1_val, m2_val, 1)
        ratio_str = f"{m1_val / mx:.1f} : {m2_val / mx:.1f}"
        screen.blit(font_sm.render("Mass ratio", True, GRAY), (left, 385))
        screen.blit(font_md.render(ratio_str, True, WHITE), (left, 405))

        screen.blit(font_sm.render("Esc to quit", True, DARK_GRAY),
                    (left, HEIGHT - 30))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()