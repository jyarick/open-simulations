# Gravity Assist Lab

A Python visualization that demonstrates **gravitational slingshot** (gravity assist) mechanics—the technique used by Voyager and other spacecraft to gain speed by flying past planets.

## Features

- **Physics-based simulation** using Newtonian gravity
- **RK4 integrator** for accurate orbital mechanics
- **Dark space aesthetic** with star, planet, spacecraft, and trajectory trails
- **Velocity vector arrows** and optional gravity field rings
- **Incoming/outgoing speed** and energy change printed after the run

## Quick Start

```bash
cd gravity-assist-lab
pip install -r requirements.txt
python main.py
```

## Tunable Parameters

Edit the top of `main.py` to explore different scenarios:

| Parameter | Description |
|-----------|-------------|
| `planet_mass` | Planet mass (affects gravity strength) |
| `planet_orbit_radius` | Distance from star |
| `planet_orbit_speed` | Orbital angular velocity |
| `spacecraft_initial_speed` | Approach speed |
| `spacecraft_entry_angle` | Approach angle (degrees from +x) |
| `spacecraft_start_x`, `spacecraft_start_y` | Starting position |
| `simulation_dt` | Time step (smaller = more accurate) |

## Project Structure

```
gravity-assist-lab/
├── main.py              # Entry point, parameters, animation loop
├── config/
│   └── constants.py     # Physical constants, defaults
├── physics/
│   ├── bodies.py        # Star, planet, spacecraft
│   ├── gravity.py       # Newtonian gravity
│   └── integrator.py    # RK4, semi-implicit Euler
├── simulation/
│   ├── universe.py      # Manages all bodies
│   └── spacecraft.py   # Spacecraft dynamics
└── visuals/
    ├── renderer.py      # Matplotlib rendering
    └── trails.py        # Trajectory trail
```

## How It Works

1. **Star** is fixed at the center.
2. **Planet** orbits the star in a circular path.
3. **Spacecraft** experiences gravity from both star and planet.
4. When the spacecraft passes *behind* the moving planet, it gains speed (gravity assist).

The velocity change occurs because the spacecraft exchanges momentum with the planet—the planet slows down slightly while the spacecraft speeds up.

## Future Extensions

- Multiple planets
- Interactive sliders
- Pygame for smoother animation
- Mission planning tools
