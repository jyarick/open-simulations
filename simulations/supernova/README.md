# Supernova Turtle Visualization

A state-driven Python turtle simulation of a massive star undergoing core collapse and supernova, ending as a neutron star or black hole.

## Requirements

- Python 3.10+ (uses standard library only; no external packages)

## Run

```bash
cd supernova_sim
python3 main.py
```

## Phases

1. **Stable** — Glowing star with subtle pulsation  
2. **Collapse** — Star contracts (easing-based)  
3. **Bounce** — Brief flash, shockwave and particles spawn  
4. **Explosion** — Ejecta and shockwave expand  
5. **Remnant** — Neutron star (mass &lt; 20 M☉) or black hole (≥ 20 M☉)

## Tuning

Edit `config.py` for screen size, timings, particle count, colors, remnant mass threshold, and other parameters.

## Structure

- `main.py` — Entry point, screen setup, loop start  
- `config.py` — All tunable constants  
- `sim_state.py` — Phases and global state  
- `engine.py` — Simulation orchestration (update/draw, phase transitions)  
- `star.py`, `particles.py`, `shockwave.py`, `remnant.py` — Actors  
- `background.py`, `effects.py` — Environment and cinematic effects  
- `utils.py` — clamp, lerp, easing, polar/cartesian helpers  
