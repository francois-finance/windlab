import numpy as np
from physics.wake_bastankhah import bastankhah

def score_two_turbines(x1, y1, x2, y2, U0, variance, D=100, Ct=0.7, k=0.05):
    """
    Score = production moyenne des deux turbines.
    Hypothèse : alignement simplifié → le vent vient de la gauche vers la droite.
    """
    dist = x2 - x1  # si vent = axe x
    if dist <= 0:
        return -1  # turbine aval doit être à droite

    U1 = np.random.normal(U0, np.sqrt(variance))
    U2 = bastankhah(U1, Ct, dist, r=0, D=D, k=k)

    return (U1**3) + (U2**3)


def optimize_two_turbines(U0, variance, iterations=5000, terrain_size=2000, D=100):
    best_score = -np.inf
    best_positions = None

    for _ in range(iterations):
        x1, y1 = np.random.uniform(0, terrain_size, 2)
        x2, y2 = np.random.uniform(0, terrain_size, 2)

        # contrainte : espacement > 2D
        if np.sqrt((x2-x1)**2 + (y2-y1)**2) < 2*D:
            continue

        score = score_two_turbines(x1, y1, x2, y2, U0, variance, D=D)
        if score > best_score:
            best_score = score
            best_positions = ((x1, y1), (x2, y2))

    return best_score, best_positions