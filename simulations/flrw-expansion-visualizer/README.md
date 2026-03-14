# FLRW Expansion Visualizer (Toy Model)

A simple Python/Matplotlib visualization of cosmological expansion in an FLRW universe.

**What it shows**
- Comoving test particles (“galaxies”) mapped to physical coordinates via  
  **r(t) = a(t) x**
- A comoving grid that stretches in the **physical view**
- A photon **Gaussian wave packet** whose wavelength stretches with expansion:  
  **λ_phys(t) = a(t) λ₀**

**Model**
- Flat universe enforced: ΩΛ = 1 − Ωm
- Matter + Λ only (no radiation)
- No local gravity / structure formation
- No peculiar velocities (pure Hubble flow)

## Run

python3 FLRW.py

Optional:
python3 FLRW.py --omega_m 0.3 --n_gal 800 --lambda0 0.25

## Controls

- space pause/play
- r reset
- c toggle physical ↔ comoving view
- h toggle Hubble radius circle
- p flip photon packet direction
- q / esc quit

## Notes / Disclaimer

This is a toy model meant for intuition. It does not simulate structure formation, bound systems, or full relativistic light propagation.