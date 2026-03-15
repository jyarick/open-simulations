# Deep Time Earth

A Python Turtle visualization of Earth evolving through 4.5 billion years of geologic time — from the Hadean to the present day.

## Run

```bash
python main.py
```

Requires Python 3 with the standard library (turtle, random). No extra dependencies.

## Controls

| Key | Action |
|-----|--------|
| Space | Pause / Resume |
| r | Restart simulation |
| s | Cycle speed |
| + / − | Speed up / down |
| d | Toggle debug overlay |
| h | Toggle help |

## What It Shows

- **Timeline** — Geologic eras (Hadean → Archean → Proterozoic → Phanerozoic → Cenozoic)
- **Life meter** — Biosphere complexity over time
- **Captions** — Current epoch or major event (Snowball Earth, Great Oxidation, Cambrian Explosion, Permian Extinction, K-Pg Impact)
- **Continental drift** — Point-cloud continents moving across the globe
- **Day/night** — Rotating terminator
- **Event overlays** — Visual effects during major events

## Project Structure

| File | Purpose |
|------|---------|
| `main.py` | Entry point, frame loop, key bindings |
| `config.py` | All tunables |
| `simulation.py` | State, update logic, intro/loop/pause |
| `render.py` | Projection, globe, overlays |
| `data.py` | Epochs, events, continent/cloud generation |
| `ui.py` | Life meter, timeline, captions, help, debug |

## Configuration

Edit `config.py` to tune speed, intro timing, colors, and UI layout. Set `PRESENTATION_MODE = False` for debug mode (overlay on, slower default speed).

## License

Part of the open-physics-simulations project.
