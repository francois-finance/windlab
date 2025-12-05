# WindLab – Analyse de sillage d'éoliennes en soufflerie

Projet développé dans le cadre d'une expérience en soufflerie (13/11/2025) visant à étudier
le sillage généré par une éolienne amont et son impact sur une éolienne aval.

L'application permet :
- de charger des fichiers de mesure LabVIEW (.lvm / .txt),
- d'afficher et comparer les signaux P1 (éolienne amont) et P2 (éolienne aval),
- d'appliquer une analyse fréquentielle (FFT) et du filtrage,
- de calculer et visualiser des spectrogrammes (STFT),
- de lancer des simulations Monte-Carlo à partir des signaux mesurés,
- d'optimiser la position relative de deux éoliennes sur un parc 2 km × 2 km,
- de générer un rapport PDF incluant les figures principales.

---

## Architecture du projet

```text
windlab/
├── main.py                # Point d'entrée – lance la GUI
├── gui.py                 # Interface graphique (Tkinter + matplotlib)
├── data/
│   ├── loader.py          # Lecture fichiers LabVIEW (.txt/.lvm) et nettoyage
│   ├── preprocess.py      # FFT, filtrage, spectrogrammes
├── physics/
│   ├── wake_bastankhah.py # Modèle de sillage gaussien (Bastankhah 2014)
│   ├── wake_jensen.py     # Modèle de sillage de Jensen
├── simulation/
│   ├── montecarlo.py      # Simulations Monte-Carlo basées sur les signaux mesurés
│   ├── optimize.py        # Optimisation de positions dans un parc éolien
├── utils/
│   ├── plotting.py        # Fonctions de tracé (signaux, FFT, spectrogrammes, parc)
├── reporting/
│   ├── pdf_generator.py   # Génération de rapport PDF (ReportLab)
├── requirements.txt
├── .gitignore
└── README.md