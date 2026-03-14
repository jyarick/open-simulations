import numpy as np


def add_noise(y, noise_std=0.01, random_seed=None):
    """
    Add Gaussian noise to data.

    Parameters
    ----------
    y : ndarray
        State data.
    noise_std : float
        Standard deviation of noise.
    random_seed : int or None
        For reproducibility.
    """

    rng = np.random.default_rng(random_seed)

    noise = rng.normal(0, noise_std, size=y.shape)

    return y + noise