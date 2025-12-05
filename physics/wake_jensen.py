import numpy as np

def jensen(U0, Ct, x, D, k=0.05):
    if x <= 0:
        return U0

    eps = (1 + k * x / D)**2
    deficit = (1 - np.sqrt(1 - Ct)) / eps
    return U0 * (1 - deficit)