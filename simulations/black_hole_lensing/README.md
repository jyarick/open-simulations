# Black Hole Light Bending

## Overview

A visualization of gravitational lensing near a **Schwarzschild black hole** using Python's `turtle` graphics.

The simulation launches light rays past a black hole and demonstrates how curved spacetime alters their paths. Some rays escape, while others are captured by the event horizon.

The goal is to provide an **intuitive visual understanding of gravitational lensing and strong gravity**.

---

## Physics Concepts

This project illustrates several key ideas from **general relativity**.

### Event Horizon

The Schwarzschild radius

r_s = 2GM / c^2

defines the boundary where nothing, not even light, can escape.

### Photon Sphere

Light can orbit a black hole at

r_ph = 3GM / c^2

This orbit is **unstable**, meaning small perturbations cause photons to either escape or fall inward.

### Gravitational Lensing

Light passing near massive objects follows curved paths (null geodesics), producing bending similar to what this simulation visualizes.

---

## Simulation Features

- Schwarzschild-inspired black hole geometry
- Photon sphere visualization
- Light ray deflection
- Capture vs escape trajectories
- Adjustable curvature strength
- Real-time controls

---

## Controls

Key | Action
--- | ---
r | Reset simulation
p | Pause / unpause
t | Toggle trails
[ | Decrease curvature
] | Increase curvature

---

## How It Works

Each light ray moves at constant speed while its **direction rotates slightly toward the black hole**, representing spacetime curvature.

This is an **effective geometric model** rather than a full numerical solution of the Schwarzschild null geodesic equations, but it reproduces the qualitative behavior of:

- strong bending near the black hole
- photon sphere trajectories
- capture vs escape paths

---

## How to Run

Clone the repository

git clone https://github.com/jyarick/black-hole-lensing.git

Navigate into the directory

cd black-hole-lensing

Run the simulation

python3 blackhole_lensing_turtle.py

---

## Educational Purpose

This simulation helps illustrate:

- gravitational lensing
- strong gravity near black holes
- photon spheres
- event horizons
- qualitative behavior of null geodesics

The model is intentionally simplified and designed for **visual intuition rather than full relativistic accuracy**.

---

## Future Improvements

Potential directions for future versions include:

- numerical integration of full **Schwarzschild null geodesics**
- visualization of **accretion disks**
- rendering of **Einstein rings**
- multiple black hole lensing scenarios
- improved rendering performance

---

## License

Creative Commons **CC BY-NC-SA 4.0**

Attribution — NonCommercial — ShareAlike
