# Photon Random Walk

A visualization of photon diffusion inside a star using a stochastic random-walk model.

This project simulates photons scattering through stellar material and gradually escaping the surface. The model illustrates how microscopic interactions between photons and matter lead to macroscopic energy transport in stars.

The simulation uses Python's `turtle` graphics to display photon trajectories and visualize the stochastic diffusion process.

---

## Overview

Inside stars, photons produced by nuclear fusion do not travel directly to the surface. Instead, they undergo a large number of scattering events with charged particles in the stellar plasma.

Each scattering event changes the photon’s direction, causing the photon to execute a **random walk** through the star.

The average distance between scattering events is called the **mean free path**

\[
\lambda = \frac{1}{\kappa \rho}
\]

where

- \( \kappa \) = opacity of the stellar material  
- \( \rho \) = local density  

Because the stellar interior is dense, photons typically take **many millions to billions of steps** before escaping.

This simulation visualizes that process in an educational and interactive way.

---

## Features

### Stellar properties derived from mass

The simulation assumes a **main sequence star** and derives several stellar properties from the user-provided mass:

- Mass–radius relation  
- Mass–luminosity relation  
- Effective temperature from the Stefan–Boltzmann law  

These quantities determine the visual appearance of the star and the transport properties of photons.

---

### Radial density profile

The stellar density is modeled with a simple radial profile

\[
\rho(r) = \rho_0 \left(1 - \frac{r}{R}\right)
\]

which decreases toward the surface.

---

### Opacity model

The initial opacity is estimated using a simplified combination of:

- electron scattering opacity
- a Kramers-like opacity term

This provides a reasonable educational approximation for photon transport.

---

### Photon transport

Photon motion is modeled using:

- exponential sampling of free path lengths
- isotropic scattering directions in **3D**
- projection of motion onto a **2D visualization plane**

The step length is sampled from

\[
P(\ell) = \frac{1}{\lambda} e^{-\ell/\lambda}
\]

where \( \lambda \) is the local mean free path.

---

### Visual features

- Stellar color determined by effective temperature
- Radial color gradient representing a hotter interior
- Background stars rendered behind the stellar disk
- Photon colors chosen to remain visible against the stellar color
- Smooth animation using `turtle` graphics

---

## Example

Typical simulation workflow:
Photons: 20
Background stars: 50
Mass (M☉): 2

The program then estimates

- stellar radius
- luminosity
- effective temperature
- opacity

before beginning the photon random walk simulation.

---

## Installation

Clone the repository

git clone https://github.com/jyarick/photon-random-walk.git

Navigate to the directory

cd photon-random-walk

Run the simulation

python_random_walk.py

Requirements

- Python 3
- standard library modules (`math`, `random`, `turtle`, `tkinter`)

---

## Educational Purpose

This project is designed as a **visual and conceptual tool** to help illustrate:

- stochastic processes
- radiative energy transport
- photon diffusion
- mean free path and opacity
- stellar structure concepts

The physics model is intentionally simplified and intended primarily for intuition and visualization.

---

## Acknowledgements

This work was developed by the **EQuIPD Grant at the University of Florida** in the department of **Materials Science and Engineering** at the **Herbert Wertheim College of Engineering**. All work CC4.0 share alike non-commercial.

Early versions of this code were developed during that work, and I would like to acknowledge the contributions of colleagues who helped review and improve the original implementation.

Special thanks to:

- **Hajymyrat Geldimuradov** for feedback and error edits to earlier versions of the simulation.
- The **EQuIPD Grant team** for supporting the development of educational computational tools.

Any remaining errors or simplifications are my own.

---

## Future Improvements

Potential directions for future versions include:

- fully tracking photon motion in **3D**
- computing photon **escape time distributions**
- implementing more realistic **stellar structure profiles**
- adding **opacity tables** instead of analytic approximations
- improving rendering performance for large photon counts

---

## License

This project includes work developed through the EQuIPD Grant at the University of Florida.

Educational materials and related content are shared under a
CC BY-NC-SA 4.0 license unless otherwise specified.