import math
import random
import turtle

# =========================================================
# SETTINGS
# =========================================================

WIDTH, HEIGHT = 1000, 800
BG_COLOR = "black"

G = 1200.0
STAR_MASS = 5000.0
STAR_RADIUS = 10

N_PARTICLES = 150
R_INNER = 80
R_OUTER = 280

DT = 0.03
GAS_DRAG = 0.003
SUB_KEPLERIAN = 0.985

BOUNCE_FACTOR = 0.85
MERGE_SPEED_FACTOR = 1.0
FRAGMENT_SPEED_FACTOR = 2.8   # if v_rel > this * v_escape => fragment

DENSITY = 0.08
WALL_MARGIN = 1000
SHOW_ORBITS = False

# --- New features ---
BIG_BODY_GRAVITY_MASS = 8.0      # only bodies above this exert particle-particle gravity
BIG_BODY_TRAIL_MASS = 100.0       # only large bodies leave trails
MAX_DUST = 120                   # cap dust particles
DUST_LIFETIME = 120              # steps
DUST_SPEED = 1.8                 # fragment dust kick speed
LOG_INTERVAL = 20                # steps between mass log samples

# =========================================================
# SCREEN SETUP
# =========================================================

screen = turtle.Screen()
screen.setup(WIDTH, HEIGHT)
screen.bgcolor(BG_COLOR)
screen.title("Planet Formation Simulator - Turtle Prototype")
screen.tracer(0, 0)

# =========================================================
# DRAWERS
# =========================================================

star_drawer = turtle.Turtle(visible=False)
star_drawer.penup()
star_drawer.color("yellow")

particle_drawer = turtle.Turtle(visible=False)
particle_drawer.penup()
particle_drawer.speed(0)

trail_drawer = turtle.Turtle(visible=False)
trail_drawer.penup()
trail_drawer.speed(0)

dust_drawer = turtle.Turtle(visible=False)
dust_drawer.penup()
dust_drawer.speed(0)

text_drawer = turtle.Turtle(visible=False)
text_drawer.penup()
text_drawer.color("white")

plot_drawer = turtle.Turtle(visible=False)
plot_drawer.penup()
plot_drawer.speed(0)
plot_drawer.color("lime")

screen.colormode(255)

# =========================================================
# HELPERS
# =========================================================

def mass_to_radius(m):
    return max(2, (m / DENSITY) ** (1/3))

def distance(ax, ay, bx, by):
    dx = bx - ax
    dy = by - ay
    return math.hypot(dx, dy), dx, dy

def kepler_speed(r):
    return math.sqrt(G * STAR_MASS / max(r, 1e-6))

def clamp_color(value, lo=0, hi=255):
    return max(lo, min(hi, int(value)))

def mass_to_color(m):
    x = min(1.0, m / 30.0)
    r = clamp_color(50 + 205 * x)
    g = clamp_color(220 - 140 * x)
    b = clamp_color(255 - 255 * x)
    return (r, g, b)

def trail_color(m):
    x = min(1.0, m / 40.0)
    return (
        clamp_color(120 + 120 * x),
        clamp_color(120 + 60 * x),
        clamp_color(255 - 200 * x)
    )

# =========================================================
# PARTICLES
# =========================================================

class Particle:
    def __init__(self, x, y, vx, vy, mass):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.alive = True
        self.prev_x = x
        self.prev_y = y

    @property
    def radius(self):
        return mass_to_radius(self.mass)

class Dust:
    def __init__(self, x, y, vx, vy, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.alive = True

# =========================================================
# INITIALIZATION
# =========================================================

particles = []
dust_particles = []

for _ in range(N_PARTICLES):
    r = random.uniform(R_INNER, R_OUTER)
    theta = random.uniform(0, 2 * math.pi)

    x = r * math.cos(theta)
    y = r * math.sin(theta)

    v = kepler_speed(r)
    v *= random.uniform(0.96, 1.04)

    vx = -v * math.sin(theta)
    vy =  v * math.cos(theta)

    vx += random.uniform(-0.4, 0.4)
    vy += random.uniform(-0.4, 0.4)

    mass = random.uniform(0.8, 2.0)
    particles.append(Particle(x, y, vx, vy, mass))

# one seed protoplanet
particles.append(Particle(170, 0, 0, kepler_speed(170) * 0.98, 8.0))

# logging
step_count = 0
largest_mass_history = []

# =========================================================
# PHYSICS
# =========================================================

def apply_star_gravity_and_drag(p):
    r = math.hypot(p.x, p.y)
    if r < 1e-6:
        return

    a = G * STAR_MASS / (r * r)
    ax = -a * p.x / r
    ay = -a * p.y / r

    p.vx += ax * DT
    p.vy += ay * DT

    v_gas = SUB_KEPLERIAN * kepler_speed(r)
    tx = -p.y / r
    ty =  p.x / r

    vx_gas = v_gas * tx
    vy_gas = v_gas * ty

    p.vx += -GAS_DRAG * (p.vx - vx_gas)
    p.vy += -GAS_DRAG * (p.vy - vy_gas)

def apply_big_body_gravity():
    alive = [p for p in particles if p.alive]
    big_bodies = [p for p in alive if p.mass >= BIG_BODY_GRAVITY_MASS]

    for p in alive:
        for b in big_bodies:
            if p is b:
                continue
            d, dx, dy = distance(p.x, p.y, b.x, b.y)
            soften = b.radius + 8.0
            dist2 = d * d + soften * soften
            dist = math.sqrt(dist2)
            if dist < 1e-6:
                continue

            a = G * b.mass / dist2
            p.vx += a * (dx / dist) * DT
            p.vy += a * (dy / dist) * DT

def update_positions():
    for p in particles:
        if not p.alive:
            continue
        p.prev_x = p.x
        p.prev_y = p.y
        p.x += p.vx * DT
        p.y += p.vy * DT

        if abs(p.x) > WALL_MARGIN or abs(p.y) > WALL_MARGIN:
            p.alive = False

def update_dust():
    for d in dust_particles:
        if not d.alive:
            continue
        d.x += d.vx * DT
        d.y += d.vy * DT
        d.vx *= 0.995
        d.vy *= 0.995
        d.lifetime -= 1
        if d.lifetime <= 0:
            d.alive = False

def spawn_fragment_dust(x, y, base_vx, base_vy, count=8):
    alive_dust = sum(1 for d in dust_particles if d.alive)
    room = max(0, MAX_DUST - alive_dust)
    count = min(count, room)

    for _ in range(count):
        theta = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.3, DUST_SPEED)
        vx = base_vx + speed * math.cos(theta)
        vy = base_vy + speed * math.sin(theta)
        dust_particles.append(Dust(x, y, vx, vy, DUST_LIFETIME))

def resolve_collisions():
    alive_particles = [p for p in particles if p.alive]

    for i in range(len(alive_particles)):
        p1 = alive_particles[i]
        if not p1.alive:
            continue

        for j in range(i + 1, len(alive_particles)):
            p2 = alive_particles[j]
            if not p2.alive:
                continue

            d, dx, dy = distance(p1.x, p1.y, p2.x, p2.y)
            min_dist = p1.radius + p2.radius

            if d >= min_dist or d == 0:
                continue

            nx = dx / d
            ny = dy / d

            rvx = p2.vx - p1.vx
            rvy = p2.vy - p1.vy
            v_rel = math.hypot(rvx, rvy)

            v_esc = math.sqrt(
                2 * G * (p1.mass + p2.mass) / max(min_dist, 1e-6)
            )

            if v_rel < MERGE_SPEED_FACTOR * v_esc:
                merge_particles(p1, p2)

            elif v_rel > FRAGMENT_SPEED_FACTOR * v_esc:
                fragment_particles(p1, p2, nx, ny)

            else:
                bounce_particles(p1, p2, nx, ny)

def merge_particles(p1, p2):
    total_mass = p1.mass + p2.mass

    new_x = (p1.mass * p1.x + p2.mass * p2.x) / total_mass
    new_y = (p1.mass * p1.y + p2.mass * p2.y) / total_mass

    new_vx = (p1.mass * p1.vx + p2.mass * p2.vx) / total_mass
    new_vy = (p1.mass * p1.vy + p2.mass * p2.vy) / total_mass

    p1.x = new_x
    p1.y = new_y
    p1.vx = new_vx
    p1.vy = new_vy
    p1.mass = total_mass

    p2.alive = False

def bounce_particles(p1, p2, nx, ny):
    m1, m2 = p1.mass, p2.mass

    rel_vx = p2.vx - p1.vx
    rel_vy = p2.vy - p1.vy
    vn = rel_vx * nx + rel_vy * ny

    if vn > 0:
        return

    e = BOUNCE_FACTOR
    impulse = -(1 + e) * vn / (1/m1 + 1/m2)

    ix = impulse * nx
    iy = impulse * ny

    p1.vx -= ix / m1
    p1.vy -= iy / m1
    p2.vx += ix / m2
    p2.vy += iy / m2

    overlap = (p1.radius + p2.radius) - math.hypot(p2.x - p1.x, p2.y - p1.y)
    if overlap > 0:
        shift = 0.55 * overlap
        p1.x -= shift * nx
        p1.y -= shift * ny
        p2.x += shift * nx
        p2.y += shift * ny

def fragment_particles(p1, p2, nx, ny):
    total_mass = p1.mass + p2.mass

    # keep two surviving fragments, lose a little mass to dust
    dust_mass_loss = 0.15 * total_mass
    remain_mass = total_mass - dust_mass_loss

    m1_new = 0.55 * remain_mass
    m2_new = 0.45 * remain_mass

    com_x = (p1.mass * p1.x + p2.mass * p2.x) / total_mass
    com_y = (p1.mass * p1.y + p2.mass * p2.y) / total_mass
    com_vx = (p1.mass * p1.vx + p2.mass * p2.vx) / total_mass
    com_vy = (p1.mass * p1.vy + p2.mass * p2.vy) / total_mass

    kick = 1.0
    tx, ty = -ny, nx

    p1.x = com_x + 0.5 * p1.radius * nx
    p1.y = com_y + 0.5 * p1.radius * ny
    p2.x = com_x - 0.5 * p2.radius * nx
    p2.y = com_y - 0.5 * p2.radius * ny

    p1.vx = com_vx + kick * tx
    p1.vy = com_vy + kick * ty
    p2.vx = com_vx - kick * tx
    p2.vy = com_vy - kick * ty

    p1.mass = max(0.3, m1_new)
    p2.mass = max(0.3, m2_new)

    spawn_fragment_dust(com_x, com_y, com_vx, com_vy, count=10)

# =========================================================
# DRAWING
# =========================================================

def draw_star():
    star_drawer.clear()
    star_drawer.goto(0, -STAR_RADIUS)
    star_drawer.begin_fill()
    star_drawer.circle(STAR_RADIUS)
    star_drawer.end_fill()

def draw_trails():
    for p in particles:
        if not p.alive or p.mass < BIG_BODY_TRAIL_MASS:
            continue
        trail_drawer.pencolor(trail_color(p.mass))
        trail_drawer.penup()
        trail_drawer.goto(p.prev_x, p.prev_y)
        trail_drawer.pendown()
        trail_drawer.goto(p.x, p.y)
        trail_drawer.penup()

def draw_particles():
    particle_drawer.clear()

    if SHOW_ORBITS:
        particle_drawer.pencolor((50, 50, 50))
        for r in (R_INNER, (R_INNER + R_OUTER)/2, R_OUTER):
            particle_drawer.penup()
            particle_drawer.goto(0, -r)
            particle_drawer.pendown()
            particle_drawer.circle(r)
            particle_drawer.penup()

    alive_sorted = sorted(
        [p for p in particles if p.alive],
        key=lambda p: p.mass
    )

    for p in alive_sorted:
        particle_drawer.goto(p.x, p.y)
        particle_drawer.dot(int(2 * p.radius), mass_to_color(p.mass))

def draw_dust():
    dust_drawer.clear()
    for d in dust_particles:
        if not d.alive:
            continue
        brightness = max(40, min(200, int(255 * d.lifetime / DUST_LIFETIME)))
        dust_drawer.goto(d.x, d.y)
        dust_drawer.dot(3, (brightness, brightness, brightness))

def draw_stats():
    text_drawer.clear()
    alive = [p for p in particles if p.alive]
    total_mass = sum(p.mass for p in alive)
    largest = max((p.mass for p in alive), default=0)
    big_count = sum(1 for p in alive if p.mass >= BIG_BODY_GRAVITY_MASS)

    text_drawer.goto(-WIDTH//2 + 20, HEIGHT//2 - 40)
    text_drawer.write(
        f"Alive: {len(alive)}   Largest: {largest:.2f}   Total: {total_mass:.2f}   Big Bodies: {big_count}",
        font=("Arial", 14, "normal")
    )

def log_largest_mass():
    alive = [p for p in particles if p.alive]
    largest = max((p.mass for p in alive), default=0)
    largest_mass_history.append(largest)

def draw_mass_plot():
    plot_drawer.clear()

    if len(largest_mass_history) < 2:
        return

    plot_x0 = WIDTH//2 - 260
    plot_y0 = HEIGHT//2 - 170
    plot_w = 220
    plot_h = 120

    # axes
    plot_drawer.color("gray")
    plot_drawer.penup()
    plot_drawer.goto(plot_x0, plot_y0)
    plot_drawer.pendown()
    plot_drawer.goto(plot_x0 + plot_w, plot_y0)
    plot_drawer.penup()
    plot_drawer.goto(plot_x0, plot_y0)
    plot_drawer.pendown()
    plot_drawer.goto(plot_x0, plot_y0 + plot_h)
    plot_drawer.penup()

    max_mass = max(largest_mass_history)
    if max_mass <= 0:
        return

    plot_drawer.color("lime")
    for i, m in enumerate(largest_mass_history):
        x = plot_x0 + plot_w * i / max(1, len(largest_mass_history) - 1)
        y = plot_y0 + plot_h * (m / max_mass)
        if i == 0:
            plot_drawer.penup()
            plot_drawer.goto(x, y)
            plot_drawer.pendown()
        else:
            plot_drawer.goto(x, y)
    plot_drawer.penup()

# =========================================================
# MAIN LOOP
# =========================================================

def step():
    global step_count

    alive = [p for p in particles if p.alive]

    for p in alive:
        apply_star_gravity_and_drag(p)

    apply_big_body_gravity()
    update_positions()
    update_dust()
    resolve_collisions()

    if step_count % LOG_INTERVAL == 0:
        log_largest_mass()

    draw_star()
    draw_trails()
    draw_particles()
    draw_dust()
    draw_stats()
    draw_mass_plot()

    screen.update()

    step_count += 1
    screen.ontimer(step, 16)

draw_star()
step()
screen.mainloop()