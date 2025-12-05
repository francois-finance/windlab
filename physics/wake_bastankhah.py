import numpy as np

def sigma(x, D, k=0.05):
    return k*x + D/np.sqrt(8)

def bastankhah(U0, Ct, x, r, D, k=0.05):
    if x <= 0:
        return U0

    eps = (D / (D + 2*k*x))**2
    sig = sigma(x, D, k)
    gauss = np.exp(-(r**2) / (2*sig**2))
    deficit = (1 - np.sqrt(1 - Ct)) * eps * gauss

    return U0 * (1 - deficit)