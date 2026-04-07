"""
Binary Star Gravitational Simulation — Pygame
Drag the sliders to change each star's mass and watch the orbits respond naturally.
Mass changes preserve existing velocities, so orbits become elliptical or chaotic
just like real physics would predict.

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
TRAIL_LEN = 400
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


# ─── Camera that follows center of mass ──────────────────────────────────────
class Camera:
    def __init__(self):
        self.cx = SIM_W / 2
        self.cy = HEIGHT / 2
        self.smooth = 0.05  # lerp factor

    def update(self, s1, s2):
        total = s1["m"] + s2["m"]
        target_x = (s1["x"] * s1["m"] + s2["x"] * s2["m"]) / total
        target_y = (s1["y"] * s1["m"] + s2["y"] * s2["m"]) / total
        self.cx += (target_x - self.cx) * self.smooth
        self.cy += (target_y - self.cy) * self.smooth

    def offset(self):
        return SIM_W / 2 - self.cx, HEIGHT / 2 - self.cy


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
    sw = PANEL_W - 40

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
    camera = Camera()

    # ─── Helpers ──────────────────────────────────────────────────────────────
    def thumb_x(s):
        frac = (s["val"] - s["min"]) / (s["max"] - s["min"])
        return s["x"] + frac * s["w"]

    def set_val_from_mouse(s, mx):
        frac = (mx - s["x"]) / s["w"]
        frac = max(0.0, min(1.0, frac))
        s["val"] = round(s["min"] + frac * (s["max"] - s["min"]))

    def hit_test(s, pos):
        r = pygame.Rect(s["x"] - 10, s["track_y"] - 25, s["w"] + 20, 50)
        return r.collidepoint(pos)

    def draw_one_slider(s):
        ty = s["track_y"]
        label_y = ty - 35

        lbl_surf = font_sm.render(s["label"], True, GRAY)
        screen.blit(lbl_surf, (s["x"], label_y))

        val_surf = font_lg.render(str(s["val"]), True, s["color"])
        unit_surf = font_sm.render(" " + s["unit"], True, DARK_GRAY)
        vx = s["x"] + s["w"] - val_surf.get_width() - unit_surf.get_width()
        screen.blit(val_surf, (vx, label_y - 8))
        screen.blit(unit_surf, (vx + val_surf.get_width(), label_y + 2))

        pygame.draw.rect(screen, SLIDER_TRACK,
                         (s["x"], ty - 3, s["w"], 6), border_radius=3)
        tx = thumb_x(s)
        fw = int(tx - s["x"])
        if fw > 1:
            pygame.draw.rect(screen, s["color"],
                             (s["x"], ty - 3, fw, 6), border_radius=3)
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

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for s in all_sliders:
                    if hit_test(s, event.pos):
                        s["dragging"] = True
                        set_val_from_mouse(s, event.pos[0])

                if btn_rect.collidepoint(event.pos):
                    s1, s2 = init_bodies(slider_m1["val"], slider_m2["val"])
                    trail1, trail2 = [], []
                    camera = Camera()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                for s in all_sliders:
                    s["dragging"] = False

            if event.type == pygame.MOUSEMOTION:
                for s in all_sliders:
                    if s["dragging"]:
                        set_val_from_mouse(s, event.pos[0])

        if not running:
            break

        # ── Just update masses directly — let physics do its thing ────────
        s1["m"] = float(slider_m1["val"])
        s2["m"] = float(slider_m2["val"])
        speed = slider_spd["val"]

        # ── Physics steps ─────────────────────────────────────────────────
        for _ in range(speed):
            physics_step(s1, s2, dt)
            trail1.append((s1["x"], s1["y"]))
            trail2.append((s2["x"], s2["y"]))
            if len(trail1) > TRAIL_LEN:
                trail1.pop(0)
            if len(trail2) > TRAIL_LEN:
                trail2.pop(0)

        # ── Camera tracks center of mass ──────────────────────────────────
        camera.update(s1, s2)
        ox, oy = camera.offset()

        # ── Draw: simulation area ─────────────────────────────────────────
        screen.fill(BG)
        for bx, by, br, ba in bg_stars:
            pygame.draw.circle(screen, (ba, ba, min(255, ba + 30)),
                               (bx, by), max(1, int(br)))

        # Draw trails with camera offset
        def offset_trail(trail):
            return [(x + ox, y + oy) for x, y in trail]

        draw_trail(screen, offset_trail(trail1), STAR1_COL)
        draw_trail(screen, offset_trail(trail2), STAR2_COL)

        # COM marker
        total_m = s1["m"] + s2["m"]
        com_x = (s1["x"] * s1["m"] + s2["x"] * s2["m"]) / total_m + ox
        com_y = (s1["y"] * s1["m"] + s2["y"] * s2["m"]) / total_m + oy
        cs = pygame.Surface((20, 20), pygame.SRCALPHA)
        cc = (255, 255, 255, 60)
        pygame.draw.line(cs, cc, (0, 10), (20, 10), 1)
        pygame.draw.line(cs, cc, (10, 0), (10, 20), 1)
        pygame.draw.circle(cs, cc, (10, 10), 4, 1)
        screen.blit(cs, (int(com_x - 10), int(com_y - 10)))

        # Stars with camera offset
        s1_sx, s1_sy = s1["x"] + ox, s1["y"] + oy
        s2_sx, s2_sy = s2["x"] + ox, s2["y"] + oy
        r1 = star_radius(s1["m"])
        r2 = star_radius(s2["m"])
        draw_glow(screen, s1_sx, s1_sy, r1, STAR1_COL)
        draw_glow(screen, s2_sx, s2_sy, r2, STAR2_COL)
        pygame.draw.circle(screen, WHITE,
                           (int(s1_sx), int(s1_sy)), max(2, int(r1)))
        pygame.draw.circle(screen, WHITE,
                           (int(s2_sx), int(s2_sy)), max(2, int(r2)))

        # ── Clip the panel area so trails don't bleed over ────────────────
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

        # Mass ratio
        m1v = slider_m1["val"]
        m2v = slider_m2["val"]
        mx = max(m1v, m2v, 1)
        ratio_str = f"{m1v / mx:.1f} : {m2v / mx:.1f}"
        screen.blit(font_sm.render("Mass ratio", True, GRAY), (left, 385))
        screen.blit(font_md.render(ratio_str, True, WHITE), (left, 405))

        # Orbit type hint
        ratio = max(m1v, m2v) / max(min(m1v, m2v), 1)
        if ratio < 1.5:
            hint = "Binary system"
        elif ratio < 5:
            hint = "Unequal binary"
        elif ratio < 20:
            hint = "Star + companion"
        else:
            hint = "Star + satellite"
        screen.blit(font_sm.render("Regime", True, GRAY), (left, 440))
        screen.blit(font_md.render(hint, True, WHITE), (left, 460))

        screen.blit(font_sm.render("Esc to quit", True, DARK_GRAY),
                    (left, HEIGHT - 30))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()