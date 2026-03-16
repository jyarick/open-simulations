# Gravity Assist Lab

A real-time **2D gravitational slingshot simulation** built with Python and Pygame. Watch a spacecraft gain or lose heliocentric energy by passing near moving planets—the classic *gravity assist* maneuver used by NASA and ESA for interplanetary missions.

## What is Gravity Assist?

A **gravity assist** (or *gravitational slingshot*) is a maneuver where a spacecraft passes close to a moving planet. The planet's gravity bends the spacecraft's trajectory, and because the planet is moving, the spacecraft can **gain or lose speed** relative to the star—without firing its engines. The energy comes from the planet's orbital motion.

**Key ideas this simulation makes intuitive:**
- Gravity assist changes heliocentric energy because the planet is moving
- Not every flyby produces escape—geometry matters
- Passing *behind* a planet (trailing side) can increase energy; passing *in front* can decrease it
- Multiple assists can build toward escape

## How to Run

```bash
cd gravity-assist-lab
pip install -r requirements.txt
python main.py
```

## Dependencies

- **Python** 3.9+
- **pygame** – graphics and real-time rendering
- **numpy** – vector math and numerical integration

## Controls

### Interactive Panel (right side)

Adjust parameters **mid-simulation** with sliders and buttons:

| Control | Effect |
|---------|--------|
| **Time scale** | Speed up or slow down the simulation (0.1x–4x) |
| **Zoom** | Zoom in/out on the view (1x–6x) |
| **Trail length** | Number of trail points (100–2000) |
| **Launch speed** | Initial speed for next spacecraft (0.3–1.2) |
| **Launch angle** | Entry angle in degrees (−45° to 45°) |
| **Trails / Arrows / Rings / HUD** | Toggle visual elements |
| **Reset** | Restore preset initial conditions |
| **New spacecraft** | Launch with current slider values |
| **◀ Preset / Preset ▶** | Switch scenario preset |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **Space** | Pause / Resume |
| **R** | Reset simulation |
| **N** | Launch new spacecraft (uses slider values) |
| **P** | Pause planet motion (for testing) |
| **[ / ]** | Previous / Next scenario preset |
| **Up / Down** | Increase / Decrease time scale |
| **T** | Toggle trails |
| **V** | Toggle velocity vectors |
| **G** | Toggle gravity rings |
| **H** | Toggle HUD overlay |
| **ESC** | Quit |

## Scenario Presets

Switch presets with **[** and **]** to explore different flyby outcomes:

| Preset | Description |
|--------|-------------|
| **Weak assist** | Small boost from inner planet, stays bound |
| **Strong assist** | Larger boost from inner planet, still bound |
| **Braking assist** | Pass in front of planet: lose heliocentric energy |
| **Near escape** | Jupiter assist brings ε close to zero |
| **Full escape** | Pass behind Jupiter: prograde assist produces solar escape |
| **Two-planet assist** | Inner then outer planet: multiple assists build toward escape |

## Heliocentric Energy (ε)

The HUD displays **heliocentric specific orbital energy**:

\[
\varepsilon = \frac{v^2}{2} - \frac{\mu}{r}
\]

- **ε < 0** → **Bound to star** (elliptical orbit)
- **ε = 0** → Parabolic (escape threshold)
- **ε > 0** → **Escape trajectory** (hyperbolic, leaving the system)

This is the key diagnostic: whether the slingshot actually produced solar escape, not just a visual bend.

## Project Structure

```
gravity-assist-lab/
├── main.py          # Pygame loop, event handling, UI wiring
├── config.py        # Constants, presets, planet definitions
├── physics.py       # Gravity, integration, heliocentric energy
├── entities.py      # Star, Planet, Spacecraft classes
├── simulation.py    # Simulation state, update loop, presets
├── renderer.py      # Drawing: bodies, trails, HUD
├── ui.py            # Interactive controls: sliders, buttons, checkboxes
├── utils.py         # Coordinate conversion, trail manager
├── README.md
├── requirements.txt
└── assets/          # (optional, for future use)
```

## Tunable Parameters

Edit `config.py` to adjust:

- Screen size, colors
- Star mass and position
- **Planet definitions** (inner, Jupiter-like outer): mass, orbit radius, phase
- **Scenario presets**: spacecraft initial position, speed, entry angle
- Simulation timestep, trail length
- View scale, vector arrow scale

## Educational Purpose

This project is designed for learning and visualization. It demonstrates:

1. **Newtonian gravity** – \( \vec{a} = G M \frac{\vec{r}}{|\vec{r}|^3} \)
2. **Orbital mechanics** – circular orbits, flyby trajectories
3. **Heliocentric energy** – ε determines bound vs escape
4. **Energy transfer** – how a moving planet can boost or brake a spacecraft

The simulation uses RK4 integration for accurate trajectories and a speed-colored trail to make the slingshot effect intuitive.

## License

Part of the Open Physics Simulations project.
