# Schrödinger's Cat Lab

An **interactive Jupyter notebook lab** that demonstrates quantum superposition and measurement using the Schrödinger's cat thought experiment.

## Overview

The lab combines:

- **Educational explanation** of quantum mechanics concepts
- **Interactive controls** for preparing states and measuring
- **Statistical experiments** with repeated trials
- **Artistic visualization** of the sealed box and superposition

The physics remains mathematically correct while the visuals stay intuitive and engaging.

## Setup

```bash
pip install -r requirements.txt
```

## Running

1. Start Jupyter:
   ```bash
   jupyter notebook
   ```

2. Open `notebooks/schrodinger_cat_lab.ipynb`

3. Run all cells. Use the widgets to:
   - Adjust the alive amplitude and phase
   - Prepare a quantum state
   - Measure (collapse) the state
   - Run repeated trials
   - Compare empirical frequencies with theoretical probabilities

## Structure

```
schrodinger-cat-lab/
├── notebooks/
│   └── schrodinger_cat_lab.ipynb    # Interactive lab
├── quantum_cat/
│   ├── __init__.py
│   ├── state.py       # State preparation, probabilities
│   ├── measurement.py # Born rule, collapse
│   ├── experiments.py # Repeated trials
│   └── visuals.py     # Cat box, bar charts
├── requirements.txt
└── README.md
```

## Dependencies

- numpy
- matplotlib
- ipywidgets
- IPython

## Quantum Model

We model a two-state system:

$$
|\psi\rangle = \alpha |alive\rangle + \beta |dead\rangle
$$

with probabilities given by the Born rule:

$$
P(alive) = |\alpha|^2, \quad P(dead) = |\beta|^2
$$

Measurement randomly selects an outcome and collapses the state to the corresponding basis vector.
