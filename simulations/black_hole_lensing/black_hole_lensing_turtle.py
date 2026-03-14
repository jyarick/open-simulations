import math
import turtle
from dataclasses import dataclass


# ============================================================
# CONFIG
# ============================================================

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
BACKGROUND_COLOR = "#2b2f36"   # dark charcoal gray

# Black hole / geometry
BH_X = 0.0
BH_Y = 0.0
SCHWARZSCHILD_RADIUS = 70.0
PHOTON_SPHERE_RADIUS = 1.5 * SCHWARZSCHILD_RADIUS

# Beam launch
NUM_BEAMS = 61
LAUNCH_X = -SCREEN_WIDTH * 0.46
IMPACT_SPREAD = SCREEN_HEIGHT * 0.38

# Motion / curvature
BEAM_SPEED = 3.0
CURVATURE_STRENGTH = 5000.0
CURVATURE_POWER = 2.0
PHOTON_SPHERE_BOOST = 3.2
PHOTON_BAND_WIDTH = 30.0
EPS = 1e-9

# Drawing
ACTIVE_COLOR = "#f8f1a1"
ESCAPED_COLOR = "#7fe7ff"
CAPTURED_COLOR = "#ff7b7b"
HORIZON_OUTLINE = "#5f5f5f"
PHOTON_RING_COLOR = "#a98cff"

TRAILS_ON_DEFAULT = True
PEN_SIZE = 2

# Bounds
ESCAPE_MARGIN = 40

# Timing
FRAME_DELAY_MS = 16  # ~60 fps

# Warped grid (visual aid only)
SHOW_GRID = True
GRID_COLOR = "#3c424d"      # faint slate gray
GRID_SPACING = 50
GRID_HALF_WIDTH = SCREEN_WIDTH // 2
GRID_HALF_HEIGHT = SCREEN_HEIGHT // 2
GRID_STEPS = 140            # more steps = smoother curves
GRID_WARP_STRENGTH = 9000.0
GRID_WARP_POWER = 1.55
GRID_EXCLUSION_RADIUS = SCHWARZSCHILD_RADIUS + 8

# ============================================================
# GLOBAL STATE
# ============================================================

paused = False
trails_on = TRAILS_ON_DEFAULT
curvature_strength = CURVATURE_STRENGTH
beams = []


# ============================================================
# DATA MODEL
# ============================================================

@dataclass
class Beam:
    x: float
    y: float
    vx: float
    vy: float
    pen: turtle.Turtle
    state: str = "active"   # active, captured, escaped


# ============================================================
# VECTOR HELPERS
# ============================================================

def norm(x, y):
    return math.sqrt(x * x + y * y)


def normalize(x, y):
    n = norm(x, y)
    if n < EPS:
        return 0.0, 0.0
    return x / n, y / n


def dot(ax, ay, bx, by):
    return ax * bx + ay * by


def cross_z(ax, ay, bx, by):
    return ax * by - ay * bx


def rotate_vector(vx, vy, angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return c * vx - s * vy, s * vx + c * vy


# ============================================================
# TURTLE SETUP
# ============================================================

screen = turtle.Screen()
screen.setup(SCREEN_WIDTH, SCREEN_HEIGHT)
screen.bgcolor(BACKGROUND_COLOR)
screen.title("Black Hole Light Bending — Effective Schwarzschild-Inspired Demo")
screen.tracer(0, 0)

static_pen = turtle.Turtle(visible=False)
static_pen.speed(0)
static_pen.penup()

ui_pen = turtle.Turtle(visible=False)
ui_pen.speed(0)
ui_pen.penup()
ui_pen.color("white")


# ============================================================
# DRAWING HELPERS
# ============================================================

def draw_circle_outline(pen, x, y, r, color, pensize=2):
    pen.penup()
    pen.goto(x, y - r)
    pen.setheading(0)
    pen.pencolor(color)
    pen.pensize(pensize)
    pen.pendown()
    pen.circle(r)
    pen.penup()


def draw_filled_circle(pen, x, y, r, fillcolor, outlinecolor=None, pensize=2):
    pen.penup()
    pen.goto(x, y - r)
    pen.setheading(0)
    pen.pensize(pensize)
    pen.pencolor(outlinecolor if outlinecolor else fillcolor)
    pen.fillcolor(fillcolor)
    pen.begin_fill()
    pen.pendown()
    pen.circle(r)
    pen.end_fill()
    pen.penup()


def draw_static_scene():
    static_pen.clear()

    # Background warped grid first
    draw_warped_grid()

    # Photon sphere ring
    draw_circle_outline(
        static_pen,
        BH_X,
        BH_Y,
        PHOTON_SPHERE_RADIUS,
        color=PHOTON_RING_COLOR,
        pensize=2
    )

    # Event horizon
    draw_filled_circle(
        static_pen,
        BH_X,
        BH_Y,
        SCHWARZSCHILD_RADIUS,
        fillcolor="black",
        outlinecolor=HORIZON_OUTLINE,
        pensize=2
    )


def draw_ui():
    ui_pen.clear()
    ui_pen.goto(-SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT // 2 - 35)
    ui_pen.write(
        f"r: reset   p: pause   t: trails   [ ]: bend strength\n"
        f"curvature_strength = {curvature_strength:.1f}    "
        f"Rs = {SCHWARZSCHILD_RADIUS:.1f}    "
        f"photon sphere = {PHOTON_SPHERE_RADIUS:.1f}",
        font=("Arial", 12, "normal")
    )

def warp_point(x, y):
    """
    Purely visual radial warp used for background grid lines.
    This is not a physical embedding diagram or exact GR transform.
    """
    dx = x - BH_X
    dy = y - BH_Y
    r = norm(dx, dy)

    if r < GRID_EXCLUSION_RADIUS:
        # Avoid ugly numerical blow-up near the hole
        return x, y

    # Radial inward visual warp
    ux, uy = dx / (r + EPS), dy / (r + EPS)
    warp = GRID_WARP_STRENGTH / ((r ** GRID_WARP_POWER) + EPS)

    # Clamp so the grid stays subtle and doesn't fold too hard
    warp = min(warp, 18.0)

    return x - ux * warp, y - uy * warp


def draw_warped_polyline(points, color, pensize=1):
    if not points:
        return

    static_pen.pencolor(color)
    static_pen.pensize(pensize)
    static_pen.penup()

    x0, y0 = points[0]
    static_pen.goto(x0, y0)
    static_pen.pendown()

    for x, y in points[1:]:
        static_pen.goto(x, y)

    static_pen.penup()


def draw_warped_grid():
    if not SHOW_GRID:
        return

    # Vertical lines
    x_values = range(-GRID_HALF_WIDTH, GRID_HALF_WIDTH + 1, GRID_SPACING)
    for x in x_values:
        pts = []
        for i in range(GRID_STEPS + 1):
            y = -GRID_HALF_HEIGHT + i * (2 * GRID_HALF_HEIGHT / GRID_STEPS)
            wx, wy = warp_point(x, y)
            pts.append((wx, wy))
        draw_warped_polyline(pts, GRID_COLOR, pensize=1)

    # Horizontal lines
    y_values = range(-GRID_HALF_HEIGHT, GRID_HALF_HEIGHT + 1, GRID_SPACING)
    for y in y_values:
        pts = []
        for i in range(GRID_STEPS + 1):
            x = -GRID_HALF_WIDTH + i * (2 * GRID_HALF_WIDTH / GRID_STEPS)
            wx, wy = warp_point(x, y)
            pts.append((wx, wy))
        draw_warped_polyline(pts, GRID_COLOR, pensize=1)


# ============================================================
# BEAM CREATION
# ============================================================

def make_beam_pen():
    pen = turtle.Turtle(visible=False)
    pen.speed(0)
    pen.penup()
    pen.pencolor(ACTIVE_COLOR)
    pen.pensize(PEN_SIZE)
    return pen


def create_beams():
    global beams
    beams = []

    if NUM_BEAMS == 1:
        ys = [0.0]
    else:
        ys = [
            -IMPACT_SPREAD + i * (2 * IMPACT_SPREAD / (NUM_BEAMS - 1))
            for i in range(NUM_BEAMS)
        ]

    for y0 in ys:
        pen = make_beam_pen()

        # IMPORTANT: move first while pen is up, so no center-drawn triangle
        pen.goto(LAUNCH_X, y0)

        if trails_on:
            pen.pendown()

        beams.append(
            Beam(
                x=LAUNCH_X,
                y=y0,
                vx=1.0,
                vy=0.0,
                pen=pen,
                state="active"
            )
        )


def clear_beam_pens():
    for beam in beams:
        try:
            beam.pen.clear()
            beam.pen.hideturtle()
        except turtle.TurtleGraphicsError:
            pass


def reset_sim():
    clear_beam_pens()
    create_beams()
    draw_static_scene()
    draw_ui()
    screen.update()


# ============================================================
# EFFECTIVE CURVATURE MODEL
# ============================================================

def photon_sphere_enhancement(r):
    dr = r - PHOTON_SPHERE_RADIUS
    return 1.0 + PHOTON_SPHERE_BOOST * math.exp(-(dr * dr) / (2 * PHOTON_BAND_WIDTH ** 2))


def update_beam(beam):
    if beam.state != "active":
        return

    # Relative vector from beam to black hole
    rx = BH_X - beam.x
    ry = BH_Y - beam.y
    r = norm(rx, ry)

    # Capture condition
    if r <= SCHWARZSCHILD_RADIUS:
        beam.state = "captured"
        beam.pen.pencolor(CAPTURED_COLOR)
        return

    # Normalize velocity
    vx, vy = normalize(beam.vx, beam.vy)

    # Unit vector toward BH center
    tx, ty = normalize(rx, ry)

    # Decide which direction to rotate velocity
    z = cross_z(vx, vy, tx, ty)
    sign = 0.0
    if z > 0:
        sign = 1.0
    elif z < 0:
        sign = -1.0

    alignment = dot(vx, vy, tx, ty)

    # Effective curvature law
    bend_base = curvature_strength / ((r ** CURVATURE_POWER) + EPS)
    bend = bend_base * photon_sphere_enhancement(r)

    dtheta = sign * bend * 0.01

    # Prevent tiny jitter when already nearly radial
    if abs(z) < 1e-4 and alignment > 0.999:
        dtheta = 0.0

    # Rotate heading; keep speed constant
    vx, vy = rotate_vector(vx, vy, dtheta)
    vx, vy = normalize(vx, vy)

    beam.vx, beam.vy = vx, vy
    beam.x += vx * BEAM_SPEED
    beam.y += vy * BEAM_SPEED

    # Escape condition
    half_w = SCREEN_WIDTH / 2 + ESCAPE_MARGIN
    half_h = SCREEN_HEIGHT / 2 + ESCAPE_MARGIN
    if abs(beam.x) > half_w or abs(beam.y) > half_h:
        beam.state = "escaped"
        beam.pen.pencolor(ESCAPED_COLOR)

    beam.pen.goto(beam.x, beam.y)


# ============================================================
# CONTROLS
# ============================================================

def toggle_pause():
    global paused
    paused = not paused


def toggle_trails():
    global trails_on
    trails_on = not trails_on

    for beam in beams:
        if beam.state == "active":
            if trails_on:
                beam.pen.pendown()
            else:
                beam.pen.penup()

    draw_ui()
    screen.update()


def increase_curvature():
    global curvature_strength
    curvature_strength *= 1.15
    draw_ui()
    screen.update()


def decrease_curvature():
    global curvature_strength
    curvature_strength /= 1.15
    draw_ui()
    screen.update()


screen.listen()
screen.onkey(reset_sim, "r")
screen.onkey(toggle_pause, "p")
screen.onkey(toggle_trails, "t")
screen.onkey(decrease_curvature, "[")
screen.onkey(increase_curvature, "]")


# ============================================================
# MAIN LOOP
# ============================================================

def animate():
    if not paused:
        active_count = 0
        for beam in beams:
            if beam.state == "active":
                active_count += 1
                update_beam(beam)

        screen.update()

        if active_count == 0:
            draw_ui()
            screen.update()

    screen.ontimer(animate, FRAME_DELAY_MS)


# ============================================================
# RUN
# ============================================================

draw_static_scene()
create_beams()
draw_ui()
screen.update()
animate()
screen.mainloop()