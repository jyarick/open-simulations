#importing packages
import random
import math
import turtle
import tkinter

STEPS_PER_SOLAR_RADIUS = 200
SCALE = 420
SIGMA_SB = 5.670374419e-8   # W m^-2 K^-4
L_SUN = 3.828e26            # W

PALETTE = [
    # cool reds
    "indianred",
    "lightcoral",
    "rosybrown",
    "mistyrose",

    # cool oranges
    "lightsalmon",
    "peachpuff",
    "bisque",

    # cool yellows
    "lightgoldenrodyellow",
    "palegoldenrod",
    "khaki",
    "lemonchiffon",

    # cool greens
    "darkseagreen",
    "mediumseagreen",
    "seagreen",
    "palegreen",
    "aquamarine",
    "mediumaquamarine",

    # cool cyans
    "paleturquoise",
    "lightseagreen",
    "cadetblue",
    "powderblue",

    # cool blues
    "lightskyblue",
    "skyblue",
    "cornflowerblue",
    "steelblue",
    "royalblue",

    # cool purples
    "mediumpurple",
    "mediumorchid",
    "plum",
    "thistle",
    "lavender"
]

def createScreen():
    screen = turtle.Screen()
    screen.setup(width=1.0, height=1.0)
    screen.title("The Random Walk")
    screen.bgcolor("black")
    screen.tracer(0, 0)
    return screen

def blendColor(c1, c2, t):
    """
    Interpolate between two RGB colors.
    c1, c2 are (r, g, b) tuples with values 0–255.
    """
    r = int(c1[0] + (c2[0] - c1[0]) * t)
    g = int(c1[1] + (c2[1] - c1[1]) * t)
    b = int(c1[2] + (c2[2] - c1[2]) * t)
    return (r, g, b)


def getRGB(colorname):
    """
    Convert a turtle/Tk color name to an (r, g, b) tuple in 0–255.
    """
    canvas = turtle.getcanvas()
    r, g, b = canvas.winfo_rgb(colorname)
    return (r // 256, g // 256, b // 256)

def colorDistance(c1, c2):
    return math.sqrt(
        (c1[0] - c2[0])**2 +
        (c1[1] - c2[1])**2 +
        (c1[2] - c2[2])**2
    )


def getVisiblePalette(star_color, palette, min_distance=120):
    star_rgb = getRGB(star_color)
    visible = []

    for color in palette:
        try:
            rgb = getRGB(color)
            if colorDistance(star_rgb, rgb) >= min_distance:
                visible.append(color)
        except Exception:
            pass

    # fallback so we never return empty
    if not visible:
        visible = palette[:]

    return visible

# create the star's turtle
def createStar(R_sol, star_color):
    steps_size = STEPS_PER_SOLAR_RADIUS * R_sol
    layers = 80

    turtle.colormode(255)

    star_rgb = getRGB(star_color)
    white = (255, 255, 255)

    star = turtle.Turtle()
    star.speed(0)
    star.hideturtle()
    star.penup()

    for i in range(layers, 0, -1):
        r = steps_size * i / layers
        t = (i / layers) ** 1.3
        color = blendColor(white, star_rgb, t)

        star.goto(0, -r)
        star.color(color)
        star.begin_fill()
        star.circle(r)
        star.end_fill()


# create the background stars turtle
def createBackgroundStars(screen, n_stars, R_sol):

    stars = []
    star_radius_steps = STEPS_PER_SOLAR_RADIUS * R_sol

    for _ in range(n_stars):
        x = random.uniform(-720, 720)
        y = random.uniform(-404, 404)

        # do not draw stars behind the star
        if math.sqrt(x * x + y * y) < star_radius_steps:
            continue

        t = turtle.Turtle(visible=False)
        t.speed(0)
        t.penup()
        t.goto(x, y)

        size = random.randint(1, 4)
        t.dot(size, "white")

        stars.append(t)

    screen.update()
    return stars


# creates a turtle for each photon
def createPhotons(screen, n_photons, star_color):
    photons = []
    visible_palette = getVisiblePalette(star_color, PALETTE)

    for _ in range(n_photons):
        t = turtle.Turtle(visible=False)
        t.color(random.choice(visible_palette))
        t.speed(0)
        t.penup()
        t.goto(0, 0)
        t.pendown()
        photons.append(t)

    screen.update()
    return photons


def estimateMainSequenceRadius(M_sol):
    # approximate main-sequence mass-radius relation in solar units
    if M_sol < 1.0:
        return M_sol**0.8
    else:
        return M_sol**0.57


def estimateMainSequenceLuminosity(M_sol):
    # approximate main-sequence mass-luminosity relation in solar units
    return L_SUN * (M_sol ** 3.5)


def estimateTemperature(L_SI, R_SI):
    # effective temperature from Stefan-Boltzmann law
    return (L_SI / (4 * math.pi * R_SI**2 * SIGMA_SB))**0.25

def getStarColorFromTemperature(T):
    if T < 3500:
        return "red"
    elif T < 5000:
        return "orange"
    elif T < 6000:
        return "yellow"
    elif T < 7500:
        return "white"
    elif T < 10000:
        return "lightblue"
    else:
        return "deepskyblue"

def estimateInitialOpacity(rho, T):
    """
    Toy opacity model:
    kappa_total = electron scattering + Kramers-like term
    """
    kappa_es = 0.034   # m^2/kg
    #k0 = 4e25          # toy coefficient
    #reduction = 1e-15
    #kappa_kramers = reduction * k0 * rho * (T ** -3.5)

    return kappa_es #kappa_es + kappa_kramers


# converts solar mass units into kilograms (SI units)
def getMass(M_sol):
    return 1.989e30 * M_sol


# converts solar radius units into meters (SI units)
def getRadius(R_sol):
    return 6.95e8 * R_sol


# calculates the density normalization at the center of the star (SI units)
def getInitialDensity(M_SI, R_SI):
    # for rho(r) = rho_i * (1 - r/R), this gives total mass M
    return (3 * M_SI) / (math.pi * (R_SI**3))


# calculates the current density of star based on the photons current position (SI units)
def getCurrentDensity(rho_i, r, R):
    return max(rho_i * (1 - (r / R)), 1e-12)


def getCurrentOpacity(k0, r, R, a=1):
    return max(k0 * (1 - r / R)**a, 1e-12)


def getCurrentMeanPathLength(k, rho):
    return 1 / (k * rho)


def sampleStepLength(mean_free_path):
    u = random.random()
    return -mean_free_path * math.log(u)


def sample3DStep(step):
    # isotropic direction in 3D:
    # phi   = azimuthal angle in [0, 2pi)
    # mu    = cos(theta_polar) uniform in [-1, 1]
    phi = 2 * math.pi * random.random()
    mu = 2 * random.random() - 1.0
    sin_theta = math.sqrt(1 - mu * mu)

    dx = step * sin_theta * math.cos(phi)
    dy = step * sin_theta * math.sin(phi)
    dz = step * mu

    return dx, dy, dz


def clamp(val, lo, hi):
    return max(lo, min(val, hi))


def clamp_with_msg(val, lo, hi, name):
    original = val
    val = clamp(val, lo, hi)
    if val != original:
        print(f"{name} adjusted to {val} (allowed range {lo}–{hi})")
    return val


def get_user_inputs():
    n_photons = clamp_with_msg(int(input("Photons: ")), 1, 50, "Photons")
    n_stars   = clamp_with_msg(int(input("Background stars: ")), 0, 300, "Background Stars")
    mass      = clamp_with_msg(float(input("Mass (M☉): ")), 0.1, 10.0, "Mass")

    radius = estimateMainSequenceRadius(mass)
    print(f"Estimated main-sequence radius: {radius:.3f} R☉")

    return n_photons, n_stars, mass, radius


def moveOnePhoton(photon, X, Y, r_steps, R_SI, kappa_i, rho_i, steps_to_SI):
    r_SI = r_steps * steps_to_SI

    rho = getCurrentDensity(rho_i, r_SI, R_SI)
    kappa = getCurrentOpacity(kappa_i, r_SI, R_SI)
    mfp = getCurrentMeanPathLength(kappa, rho)
    step_SI = sampleStepLength(mfp)
    step = step_SI * SCALE

    dx, dy, dz = sample3DStep(step)
    X += dx
    Y += dy

    r_steps = math.sqrt(X * X + Y * Y)

    photon.goto(X, Y)
    return X, Y, r_steps


def movePhotons(screen, M_sol, R_sol, photons):
    M_SI = getMass(M_sol)
    R_SI = getRadius(R_sol)
    rho_i = getInitialDensity(M_SI, R_SI)

    L_SI = estimateMainSequenceLuminosity(M_sol)
    T_i = estimateTemperature(L_SI, R_SI)
    kappa_i = estimateInitialOpacity(rho_i, T_i)

    print(f"Estimated luminosity: {L_SI:.3e} W")
    print(f"Estimated effective temperature: {T_i:.1f} K")
    print(f"Estimated initial opacity: {kappa_i:.3e} m^2/kg")

    steps_to_SI = R_SI / (R_sol * STEPS_PER_SOLAR_RADIUS)
    R_steps = STEPS_PER_SOLAR_RADIUS * R_sol

    X = [0.0] * len(photons)
    Y = [0.0] * len(photons)
    R = [0.0] * len(photons)

    furthest = 0.0
    while furthest <= R_steps:
        try:
            for i, p in enumerate(photons):
                X[i], Y[i], R[i] = moveOnePhoton(
                    p, X[i], Y[i], R[i], R_SI, kappa_i, rho_i, steps_to_SI
                )
            screen.update()
            furthest = max(R)

        except (turtle.Terminator, tkinter.TclError):
            break

def closeSimulation(screen):
    screen.exitonclick()


# function that takes in all user defined inputs, and simulates the photons' random walk
def simulateRandomWalk(n_photons, n_stars, M_sol, R_sol):
    M_SI = getMass(M_sol)
    R_SI = getRadius(R_sol)
    L_SI = estimateMainSequenceLuminosity(M_sol)
    T_i = estimateTemperature(L_SI, R_SI)
    star_color = getStarColorFromTemperature(T_i)

    screen = createScreen()

    createStar(R_sol, star_color)
    createBackgroundStars(screen, n_stars, R_sol)
    photons = createPhotons(screen, n_photons, star_color)

    movePhotons(screen, M_sol, R_sol, photons)
    closeSimulation(screen)


def main():
    args = get_user_inputs()
    simulateRandomWalk(*args)


if __name__ == "__main__":
    main()