# Deep Time Earth

A stylized simulation showing how Earth transformed across 4.5 billion years — from a molten world to the modern biosphere.

## Run

```bash
cd deep-time-earth
python3 run.py
```

## Controls

| Key | Action |
|-----|--------|
| ↑ | Increase simulation speed |
| ↓ | Decrease simulation speed |
| Space | Pause / Resume |
| S | Toggle planet spin |
| R | Restart simulation |

## Procedural Continent Generator

Continents are generated procedurally with:

- **Spherical geometry**: `spherical_offset()` uses a tangent-plane approximation for proper lat/lon boundary points
- **Smooth coastlines**: Low-frequency sinusoids + `smooth_noise_profile()` — no jagged edges
- **Drift**: Each continent has `drift_lat`, `drift_lon`, `spin`; `rotation_phase` evolves over time
- **Subtle deformation**: `sim_time` adds a small "breathing" oscillation to coastlines

### Shape generation

For each boundary point at angle θ:

1. Base radius + mode coefficients: `base + m1*sin(θ) + m2*sin(2θ) + m3*cos(θ)`
2. Smooth noise: `smooth_noise_profile(seed, θ)` scaled by roughness
3. Time breathing: `0.02 * sin(sim_time * 0.001) * base_radius`
4. `spherical_offset(center_lat, center_lon, azimuth, r_total)` → (lat, lon)

### API

- `generate_initial_continents(seed, count)` — create continent set
- `generate_continent(name, center_lat, center_lon, seed)` — single continent
- `update_continent(continent, dt)` / `update_continents(continents, dt)`
- `get_continent_boundary_latlon(continent, num_points, sim_time)` — boundary points for rendering

Designed for future splitting/merging: continent objects are independent, count is configurable.
