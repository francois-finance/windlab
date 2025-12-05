import numpy as np
from physics.wake_bastankhah import bastankhah

def mc_from_signals(P1, P2, N=1000):
    """
    Monte-Carlo basé sur les signaux mesurés :
    - P1 = série temporelle éolienne 1
    - P2 = série temporelle éolienne 2
    """
    U1_mean = np.mean(P1)
    U2_mean = np.mean(P2)
    var = np.var(P2 - P1)

    results = []
    for _ in range(N):
        U1 = np.random.normal(U1_mean, np.sqrt(var))
        U2 = np.random.normal(U2_mean, np.sqrt(var))

        Ptot = U1**3 + U2**3
        results.append(Ptot)

    return np.array(results)