import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import numpy as np

from data.loader import load_labview_txt
from data.preprocess import fft_filter, running_mean, smooth_savgol, compute_spectrogram
from simulation.montecarlo import mc_from_signals
from simulation.optimize import optimize_two_turbines
from utils.plotting import (
    plot_signal, plot_fft, plot_spectrogram, plot_montecarlo_results, plot_park_positions
)
from reporting.pdf_generator import generate_pdf

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class WindLabGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("WindLab – Analyse de Sillage & Optimisation")
        self.geometry("1300x750")
        self.figures = []       # Figures pour PDF
        self.runs = {}          # Dictionnaire {run_number: {"P1": df, "P2": df}}
        self.current_P1 = None
        self.current_P2 = None

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.tabs = {}
        self.create_tabs()

    # -----------------------------------------------------------------------
    #   TABS CREATION
    # -----------------------------------------------------------------------
    def create_tabs(self):
        tab_names = [
            "DATA",
            "FFT & Filtrage",
            "Spectrogramme",
            "Monte-Carlo",
            "Optimisation",
            "Export PDF"
        ]

        for name in tab_names:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=name)
            self.tabs[name] = frame

        self.build_tab_data()
        self.build_tab_fft()
        self.build_tab_spectrogram()
        self.build_tab_mc()
        self.build_tab_opt()
        self.build_tab_pdf()

    # -----------------------------------------------------------------------
    #   TAB 1 — DATA
    # -----------------------------------------------------------------------
    def build_tab_data(self):
        frame = self.tabs["DATA"]

        ttk.Button(frame, text="Charger dossier TXT", command=self.load_directory).pack(pady=10)

        self.run_listbox = tk.Listbox(frame, width=40, height=15)
        self.run_listbox.pack(pady=10)
        self.run_listbox.bind("<<ListboxSelect>>", self.on_run_select)

        self.data_stats_label = ttk.Label(frame, text="Aucune donnée chargée.")
        self.data_stats_label.pack()

        self.data_plot_container = ttk.Frame(frame)
        self.data_plot_container.pack(fill="both", expand=True)

    def load_directory(self):
        directory = filedialog.askdirectory(title="Choisir dossier contenant fichiers TXT")
        if not directory:
            return

        self.runs = {}
        self.run_listbox.delete(0, tk.END)

        files = sorted(f for f in os.listdir(directory) if f.endswith(".txt"))

        for f in files:
            # Format : Run_34 1 P1.txt
            name = f.replace(".txt", "")
            parts = name.split()

            if len(parts) < 3:
                continue

            run_id = parts[1]
            turbine = parts[2]  # "P1" / "P2"

            if run_id not in self.runs:
                self.runs[run_id] = {}

            full_path = os.path.join(directory, f)
            self.runs[run_id][turbine] = load_labview_txt(full_path)

        for run in self.runs.keys():
            if "P1" in self.runs[run] and "P2" in self.runs[run]:
                self.run_listbox.insert(tk.END, f"Run {run}")

        messagebox.showinfo("OK", "Données chargées avec succès !")

    def on_run_select(self, event):
        selection = self.run_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        label = self.run_listbox.get(index)
        run_id = label.split()[1]

        self.current_P1 = self.runs[run_id]["P1"]
        self.current_P2 = self.runs[run_id]["P2"]

        sig1 = self.current_P1["lum"].astype(float).values
        sig2 = self.current_P2["lum"].astype(float).values

        fig = plot_signal(sig1, sig2, title=f"Run {run_id} — Lumière P1 (bleu) vs P2 (orange)")
        self.display_plot(self.data_plot_container, fig)
        self.figures.append(fig)

        mean1 = np.mean(sig1)
        mean2 = np.mean(sig2)
        TI = np.std(sig1 - sig2) / mean1

        self.data_stats_label.config(
            text=f"P1 mean={mean1:.3f} | P2 mean={mean2:.3f} | TI={TI:.3f}"
        )

    # -----------------------------------------------------------------------
    #   TAB 2 — FFT & Filtrage
    # -----------------------------------------------------------------------
    def build_tab_fft(self):
        frame = self.tabs["FFT & Filtrage"]

        params = ttk.Frame(frame)
        params.pack(pady=10)

        ttk.Label(params, text="fmin:").grid(row=0, column=0)
        ttk.Label(params, text="fmax:").grid(row=1, column=0)

        self.fmin_entry = ttk.Entry(params)
        self.fmax_entry = ttk.Entry(params)

        self.fmin_entry.insert(0, "0.2")
        self.fmax_entry.insert(0, "3")

        self.fmin_entry.grid(row=0, column=1)
        self.fmax_entry.grid(row=1, column=1)

        ttk.Button(frame, text="Appliquer FFT + Filtrage", command=self.apply_fft).pack(pady=10)

        self.fft_plot_container = ttk.Frame(frame)
        self.fft_plot_container.pack(fill="both", expand=True)

    def apply_fft(self):
        if self.current_P1 is None:
            return messagebox.showerror("Erreur", "Aucun run sélectionné.")

        try:
            fmin = float(self.fmin_entry.get())
            fmax = float(self.fmax_entry.get())
        except:
            return messagebox.showerror("Erreur", "Paramètres FFT invalides.")

        sig = self.current_P2["lum"].astype(float).values
        filtered, freqs, spectrum = fft_filter(sig, sampling_rate=1000, fmin=fmin, fmax=fmax)

        fig_sig = plot_signal(sig, filtered, title="Signal filtré FFT")
        fig_fft = plot_fft(freqs, spectrum)

        self.display_plot(self.fft_plot_container, fig_sig)
        self.display_plot(self.fft_plot_container, fig_fft)

        self.figures.extend([fig_sig, fig_fft])
        self.filtered_signal = filtered

    # -----------------------------------------------------------------------
    #   TAB 3 — SPECTROGRAMME
    # -----------------------------------------------------------------------
    def build_tab_spectrogram(self):
        frame = self.tabs["Spectrogramme"]

        ttk.Button(frame, text="Afficher spectrogramme P2", command=self.show_spectrogram).pack(pady=10)

        self.spectro_plot_container = ttk.Frame(frame)
        self.spectro_plot_container.pack(fill="both", expand=True)

    def show_spectrogram(self):
        if self.current_P2 is None:
            return messagebox.showerror("Erreur", "Sélectionne un run.")

        sig = self.current_P2["lum"].astype(float).values
        f, t, Sxx = compute_spectrogram(sig, sampling_rate=1000)

        fig = plot_spectrogram(f, t, Sxx, title="Spectrogramme — Lumière P2")
        self.display_plot(self.spectro_plot_container, fig)
        self.figures.append(fig)

    # -----------------------------------------------------------------------
    #   TAB 4 — MONTE CARLO
    # -----------------------------------------------------------------------
    def build_tab_mc(self):
        frame = self.tabs["Monte-Carlo"]

        ttk.Button(frame, text="Lancer Monte-Carlo", command=self.run_mc).pack(pady=10)
        self.mc_plot_container = ttk.Frame(frame)
        self.mc_plot_container.pack(fill="both", expand=True)

    def run_mc(self):
        if (self.current_P1 is None) or (self.current_P2 is None):
            return messagebox.showerror("Erreur", "Sélectionne un run.")

        P1 = self.current_P1["lum"].astype(float).values
        P2 = self.current_P2["lum"].astype(float).values

        results = mc_from_signals(P1, P2, N=2000)

        fig = plot_signal(results, title="Distribution Monte-Carlo (puissance simulée)")
        self.display_plot(self.mc_plot_container, fig)
        self.figures.append(fig)

    # -----------------------------------------------------------------------
    #   TAB 5 — OPTIMISATION PARC
    # -----------------------------------------------------------------------
    def build_tab_opt(self):
        frame = self.tabs["Optimisation"]

        ttk.Button(frame, text="Optimiser positions", command=self.run_opt).pack(pady=10)
        self.opt_plot_container = ttk.Frame(frame)
        self.opt_plot_container.pack(fill="both", expand=True)

    def run_opt(self):
        if self.current_P1 is None:
            return messagebox.showerror("Erreur", "Sélectionne un run.")

        U0 = np.mean(self.current_P1["lum"].astype(float).values)
        var = np.var(self.current_P1["lum"].astype(float).values)

        score, pos = optimize_two_turbines(U0, var, iterations=1500)

        fig = plot_park_positions(pos)
        self.display_plot(self.opt_plot_container, fig)
        self.figures.append(fig)

    # -----------------------------------------------------------------------
    #   TAB 6 — EXPORT PDF
    # -----------------------------------------------------------------------
    def build_tab_pdf(self):
        frame = self.tabs["Export PDF"]

        ttk.Button(frame, text="Générer PDF", command=self.export_pdf).pack(pady=20)

    def export_pdf(self):
        if len(self.figures) == 0:
            return messagebox.showerror("Erreur", "Aucune figure à exporter.")

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf", title="Enregistrer PDF"
        )
        if not path:
            return

       # On limite le nombre de figures pour correspondre à la signature de generate_pdf
        figs_for_pdf = self.figures[:4]   # <= maximum 4 images

        stats = {
            "mean": 0,
            "variance": 0,
            "TI": 0
        }

        generate_pdf(path, stats, *figs_for_pdf)
        messagebox.showinfo("OK", "PDF généré.")

    # -----------------------------------------------------------------------
    # DISPLAY UTILITY
    # -----------------------------------------------------------------------
    def display_plot(self, parent, fig):
        canvas = FigureCanvasTkAgg(fig, master=parent)
        widget = canvas.get_tk_widget()
        widget.pack(fill="both", expand=True)
        canvas.draw()


if __name__ == "__main__":
    app = WindLabGUI()
    app.mainloop()