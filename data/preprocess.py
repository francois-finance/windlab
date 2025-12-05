import numpy as np
import scipy.signal as sg
from numpy.fft import fft, fftfreq, ifft

# ---------- FFT 1D ----------
def fft_filter(signal, sampling_rate, fmin=None, fmax=None):
    N = len(signal)
    spectrum = fft(signal)
    freqs = fftfreq(N, d=1/sampling_rate)

    mask = np.ones_like(freqs, dtype=bool)
    if fmin is not None:
        mask &= np.abs(freqs) >= fmin
    if fmax is not None:
        mask &= np.abs(freqs) <= fmax

    filtered_spectrum = spectrum * mask
    filtered_signal = np.real(ifft(filtered_spectrum))

    return filtered_signal, freqs, spectrum

# ---------- SAVGOL ----------
def smooth_savgol(signal, window=101, poly=3):
    return sg.savgol_filter(signal, window_length=window, polyorder=poly)

# ---------- Moyenne glissante ----------
def running_mean(signal, window=50):
    kernel = np.ones(window) / window
    return np.convolve(signal, kernel, mode='same')

# ---------- Spectrogramme ----------
def compute_spectrogram(signal, sampling_rate, nperseg=256, noverlap=128):
    f, t, Sxx = sg.spectrogram(
        signal,
        fs=sampling_rate,
        nperseg=nperseg,
        noverlap=noverlap,
        scaling='density',
        mode='magnitude'
    )
    return f, t, Sxx