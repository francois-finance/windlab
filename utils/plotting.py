import matplotlib.pyplot as plt
import numpy as np

def plot_signal(original, filtered=None, title="Signal"):
    """
    Trace un signal brut et, optionnellement, sa version filtrée.
    original : array-like
    filtered : array-like ou None
    """
    plt.figure(figsize=(8, 4))
    plt.plot(original, label="Original", alpha=0.6)
    if filtered is not None:
        plt.plot(filtered, label="Filtré", linewidth=2)
    plt.legend()
    plt.title(title)
    plt.xlabel("Indice")
    plt.ylabel("Amplitude")
    plt.tight_layout()
    return plt.gcf()


def plot_fft(freqs, spectrum):
    """
    Trace le module du spectre de Fourier.
    freqs : fréquences (Hz)
    spectrum : valeurs complexes de la FFT
    """
    plt.figure(figsize=(8, 4))
    plt.plot(freqs, np.abs(spectrum))
    plt.title("Spectre FFT")
    plt.xlabel("Fréquence (Hz)")
    plt.ylabel("|FFT|")
    plt.tight_layout()
    return plt.gcf()


def plot_montecarlo_results(results):
    """
    results : dict {distance: puissance_moyenne}
    """
    L = np.array(list(results.keys()))
    P = np.array(list(results.values()))

    plt.figure(figsize=(6, 4))
    plt.plot(L, P, marker="o")
    plt.xlabel("Distance (D)")
    plt.ylabel("Puissance moyenne")
    plt.title("Monte-Carlo – Influence de la distance")
    plt.grid()
    plt.tight_layout()
    return plt.gcf()


def plot_park_positions(pos):
    """
    pos : ((x1, y1), (x2, y2))
    """
    (x1, y1), (x2, y2) = pos

    plt.figure(figsize=(6, 6))
    plt.scatter([x1, x2], [y1, y2], s=150)
    plt.xlim(0, 2000)
    plt.ylim(0, 2000)
    plt.title("Optimisation parc (2 éoliennes)")
    plt.xlabel("x (m)")
    plt.ylabel("y (m)")
    plt.grid()
    plt.tight_layout()
    return plt.gcf()


def plot_spectrogram(f, t, Sxx, title="Spectrogramme"):
    """
    Trace un spectrogramme (issu de scipy.signal.spectrogram).

    f : fréquences (Hz)
    t : temps (s)
    Sxx : matrice (len(f) x len(t)) des amplitudes ou puissances
    """
    plt.figure(figsize=(7, 5))
    # Sxx est supposé déjà positif (mode='magnitude' ou 'psd')
    plt.pcolormesh(t, f, Sxx, shading="gouraud")
    plt.ylabel("Fréquence (Hz)")
    plt.xlabel("Temps (s)")
    plt.title(title)
    cbar = plt.colorbar()
    cbar.set_label("Amplitude")
    plt.tight_layout()
    return plt.gcf()