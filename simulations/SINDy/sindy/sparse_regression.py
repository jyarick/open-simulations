import numpy as np


def sparse_regression(Theta, dXdt, threshold=0.1, max_iter=10):
    """
    Sequential thresholded least squares for sparse regression.

    Parameters
    ----------
    Theta : ndarray (n_samples, n_features)
        Feature library matrix.
    dXdt : ndarray (n_samples, n_states)
        Time derivatives.
    threshold : float
        Coefficient threshold for sparsity.
    max_iter : int
        Number of thresholding iterations.

    Returns
    -------
    Xi : ndarray (n_features, n_states)
        Sparse coefficient matrix.
    """

    # initial least-squares fit
    Xi, *_ = np.linalg.lstsq(Theta, dXdt, rcond=None)

    for _ in range(max_iter):

        small = np.abs(Xi) < threshold
        Xi[small] = 0

        for i in range(dXdt.shape[1]):
            big = Xi[:, i] != 0
            if np.sum(big) == 0:
                continue

            Xi[big, i], *_ = np.linalg.lstsq(
                Theta[:, big],
                dXdt[:, i],
                rcond=None
            )

    return Xi