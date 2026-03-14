import turtle
import math

# -----------------------------
# Configuration
# -----------------------------

WIDTH = 1100
HEIGHT = 850

C = 7.0
DT = 0.16
MAX_STEPS = 5000

BH_MASS = 1500
HORIZON_RADIUS = 42
PHOTON_SPHERE_RADIUS = 1.5 * HORIZON_RADIUS

DISK_INNER_RADIUS = 72
DISK_OUTER_RADIUS = 130

BACKGROUND = "#1b1b1b"

START_X = -WIDTH / 2 + 80

# Impact parameter:
# try values like 20, 40, 55, 62, 68, 75, 90, 120
IMPACT_PARAMETER = 140

SHOW_TRAIL = True
SHOW_GUIDES = True
SHOW_ACCRETION_DISK = True
DRAW_MULTIPLE_TEST_RAYS = True

TEST_RAY_VALUES = [-140, -100, -75, -68, -62, -55, -40, 0, 40, 55, 62, 68, 75, 100, 140]

# -----------------------------
# Turtle screen setup
# -----------------------------

def create_screen():
    try:
        turtle.TurtleScreen._RUNNING = True
        turtle.Turtle._screen = None
    except Exception:
        pass

    screen = turtle.Screen()
    screen.setup(WIDTH, HEIGHT)
    screen.bgcolor(BACKGROUND)
    screen.title("Black Hole Light Bending — Impact Parameter Explorer")
    screen.tracer(0)
    return screen

# -----------------------------
# Utility
# -----------------------------

def hex_color(r, g, b):
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    return f"#{r:02x}{g:02x}{b:02x}"

def curvature_to_color(r):
    """
    Visual map:
    far away -> blue
    near photon sphere -> orange/red
    """
    strength = min(1.0, (2.4 * PHOTON_SPHERE_RADIUS) / max(r, 1))
    red = 70 + 185 * strength
    green = 210 - 180 * strength
    blue = 255 - 255 * strength
    return hex_color(red, green, blue)

# -----------------------------
# Scene drawing
# -----------------------------

def draw_ring(radius, color, width):
    pen = turtle.Turtle()
    pen.hideturtle()
    pen.speed(0)
    pen.penup()
    pen.goto(0, -radius)
    pen.pencolor(color)
    pen.width(width)
    pen.pendown()
    pen.circle(radius)
    pen.penup()

def draw_circle(radius, color, width=2, dashed=False):
    pen = turtle.Turtle()
    pen.hideturtle()
    pen.speed(0)
    pen.penup()
    pen.goto(0, -radius)
    pen.pencolor(color)
    pen.width(width)

    if not dashed:
        pen.pendown()
        pen.circle(radius)
        pen.penup()
        return

    # dashed approximation
    circumference = 2 * math.pi * radius
    dash_count = max(24, int(circumference / 12))
    arc = 360 / dash_count

    pen.setheading(0)
    for i in range(dash_count):
        if i % 2 == 0:
            pen.pendown()
        else:
            pen.penup()
        pen.circle(radius, arc)
    pen.penup()

def draw_black_hole_scene():
    if SHOW_ACCRETION_DISK:
        ring_specs = [
            (DISK_OUTER_RADIUS, "#331700", 18),
            (DISK_OUTER_RADIUS - 10, "#5c2400", 14),
            (DISK_OUTER_RADIUS - 20, "#8b3200", 11),
            (DISK_OUTER_RADIUS - 30, "#c94f00", 8),
            (DISK_INNER_RADIUS + 6, "#ffb347", 5),
        ]
        for radius, color, width in ring_specs:
            draw_ring(radius, color, width)

    if SHOW_GUIDES:
        draw_circle(PHOTON_SPHERE_RADIUS, "gray", width=2, dashed=True)
        draw_circle(HORIZON_RADIUS, "#000000", width=3, dashed=False)

    # Fill event horizon
    hole = turtle.Turtle()
    hole.hideturtle()
    hole.speed(0)
    hole.penup()
    hole.goto(0, -HORIZON_RADIUS)
    hole.color("black")
    hole.fillcolor("black")
    hole.begin_fill()
    hole.pendown()
    hole.circle(HORIZON_RADIUS)
    hole.end_fill()
    hole.penup()

def draw_axes():
    axis = turtle.Turtle()
    axis.hideturtle()
    axis.speed(0)
    axis.pencolor("#333333")
    axis.width(1)

    # x-axis
    axis.penup()
    axis.goto(-WIDTH // 2, 0)
    axis.pendown()
    axis.goto(WIDTH // 2, 0)

    # y-axis
    axis.penup()
    axis.goto(0, -HEIGHT // 2)
    axis.pendown()
    axis.goto(0, HEIGHT // 2)
    axis.penup()

def write_labels():
    writer = turtle.Turtle()
    writer.hideturtle()
    writer.penup()
    writer.color("white")

    writer.goto(-WIDTH // 2 + 20, HEIGHT // 2 - 35)
    writer.write(
        f"Impact parameter b = {IMPACT_PARAMETER}",
        font=("Arial", 14, "bold")
    )

    writer.goto(-WIDTH // 2 + 20, HEIGHT // 2 - 60)
    writer.write(
        "Blue = weak curvature, red/orange = strong curvature",
        font=("Arial", 11, "normal")
    )

    writer.goto(-WIDTH // 2 + 20, HEIGHT // 2 - 82)
    writer.write(
        "Dashed ring = photon sphere   |   Black disk = event horizon",
        font=("Arial", 11, "normal")
    )

# -----------------------------
# Photon class
# -----------------------------

class Photon:
    def __init__(self, y0, primary=False):
        self.x = START_X
        self.y = y0

        self.vx = C
        self.vy = 0.0

        self.alive = True
        self.escaped = False
        self.captured = False

        self.min_r = float("inf")
        self.total_deflection_estimate = 0.0

        self.pen = turtle.Turtle()
        self.pen.hideturtle()
        self.pen.shape("circle")
        self.pen.shapesize(0.22 if primary else 0.14)

        if primary:
            self.pen.showturtle()
            self.pen.pensize(3)
            self.pen.pencolor("white")
            self.pen.fillcolor("white")
        else:
            self.pen.showturtle()
            self.pen.pensize(2)

        self.pen.penup()
        self.pen.goto(self.x, self.y)

        if SHOW_TRAIL:
            self.pen.pendown()

        self.primary = primary

    def step(self):
        if not self.alive:
            return

        r = math.sqrt(self.x**2 + self.y**2)
        self.min_r = min(self.min_r, r)

        # Capture
        if r <= HORIZON_RADIUS:
            self.alive = False
            self.captured = True
            self.pen.hideturtle()
            return

        # Effective bending acceleration ~ 1/r^3
        accel = BH_MASS / (r**3)
        ax = -accel * self.x
        ay = -accel * self.y

        # Update velocity
        self.vx += ax * DT
        self.vy += ay * DT

        # Renormalize to constant speed
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed == 0:
            self.alive = False
            return

        self.vx = C * self.vx / speed
        self.vy = C * self.vy / speed

        # Track rough turning angle from direction
        angle = math.atan2(self.vy, self.vx)
        self.total_deflection_estimate = math.degrees(angle)

        # Update position
        self.x += self.vx * DT
        self.y += self.vy * DT

        # Color by curvature unless it is the primary highlighted photon
        if not self.primary:
            color = curvature_to_color(r)
            self.pen.pencolor(color)
            self.pen.fillcolor(color)
        else:
            # primary photon gets slight color shift but stays brighter
            color = curvature_to_color(r)
            self.pen.pencolor(color)
            self.pen.fillcolor(color)

        self.pen.goto(self.x, self.y)

        # Escape condition
        if self.x > WIDTH / 2 + 40 or abs(self.y) > HEIGHT / 2 + 40:
            self.alive = False
            self.escaped = True
            self.pen.hideturtle()

# -----------------------------
# Outcome display
# -----------------------------

def classify_outcome(photon):
    if photon.captured:
        return "captured by event horizon"

    if photon.min_r < PHOTON_SPHERE_RADIUS * 1.05:
        return "near-critical pass / photon-sphere grazing"

    if abs(photon.total_deflection_estimate) > 90:
        return "strong deflection"

    if abs(photon.total_deflection_estimate) > 20:
        return "moderate deflection"

    return "weak deflection"

def write_result(photon):
    writer = turtle.Turtle()
    writer.hideturtle()
    writer.penup()
    writer.color("white")

    result = classify_outcome(photon)

    writer.goto(-WIDTH // 2 + 20, HEIGHT // 2 - 120)
    writer.write(
        f"Primary ray outcome: {result}",
        font=("Arial", 13, "bold")
    )

    writer.goto(-WIDTH // 2 + 20, HEIGHT // 2 - 145)
    writer.write(
        f"Closest approach: r_min = {photon.min_r:.2f}",
        font=("Arial", 11, "normal")
    )

    writer.goto(-WIDTH // 2 + 20, HEIGHT // 2 - 168)
    writer.write(
        f"Final direction angle ≈ {photon.total_deflection_estimate:.1f}°",
        font=("Arial", 11, "normal")
    )

# -----------------------------
# Main
# -----------------------------

def run():
    screen = create_screen()
    draw_axes()
    draw_black_hole_scene()
    write_labels()

    photons = []

    if DRAW_MULTIPLE_TEST_RAYS:
        for b in TEST_RAY_VALUES:
            primary = (b == IMPACT_PARAMETER)
            photons.append(Photon(y0=b, primary=primary))
    else:
        photons.append(Photon(y0=IMPACT_PARAMETER, primary=True))

    primary_photon = None
    for p in photons:
        if p.primary:
            primary_photon = p
            break

    if primary_photon is None:
        primary_photon = photons[0]
        primary_photon.primary = True

    for _ in range(MAX_STEPS):
        alive_count = 0
        for photon in photons:
            if photon.alive:
                photon.step()
                alive_count += 1
        screen.update()

        if alive_count == 0:
            break

    write_result(primary_photon)
    screen.update()
    turtle.done()

run()