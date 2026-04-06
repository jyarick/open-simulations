# Binary star simulation

A small interactive **binary star** demo in [Pygame](https://www.pygame.org/). Two point masses orbit under mutual Newtonian gravity; you can change each star’s mass with sliders, speed up the integrator, and reset the system. The crosshair marks the **center of mass**.

This is a toy model (scaled constants for a pleasant display), not a literal solar-system integrator.

## Requirements

- Python 3.9+ recommended
- See `requirements.txt` (only `pygame`)

## Setup

```bash
cd simulations/binary_star
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python binary_star.py
```

## Controls

| Control | Action |
|--------|--------|
| **Star 1 / Star 2 mass** sliders | Mass of each body (in arbitrary display units, labeled M☉ for flavor) |
| **Speed** slider | Substeps per frame (higher = faster wall-clock evolution) |
| **Reset simulation** | Re-initialize positions and velocities for the current masses |
| **Esc** | Quit |

## Model (brief)

- Inverse-square force between the two bodies, equal and opposite.
- Semi-implicit (Euler-like) stepping with a softening on distance to avoid blow-ups at very close passes.
- When you change a mass, the code tries to keep the center-of-mass velocity and re-scale orbital motion about the new masses (trails clear on mass change).

## License

Same as the parent [open-simulations](https://github.com/jyarick/open-simulations) repository unless noted otherwise.
