import pandas as pd
import numpy as np
import io

def load_labview_txt(filepath):
    """
    Charge un fichier LabVIEW Measurement (.lvm / .txt) au format :

    LabVIEW Measurement
    ...
    ***End_of_Header***
    ...
    ***End_of_Header***
    X_Value  Generateur  Lumiere  Comment
    0,000000 0,680847 1,983643 ...
    ...

    On :
      - saute tous les headers
      - lit la table après le dernier ***End_of_Header***
      - gère les virgules comme séparateur décimal
      - renomme les colonnes en t, gen, lum, comment
    """

    # 1) Lire tout le fichier en mémoire
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    # 2) Trouver l'indice de la DERNIÈRE ligne contenant ***End_of_Header***
    start_idx = 0
    for i, line in enumerate(lines):
        if "***End_of_Header***" in line:
            start_idx = i + 1  # les données commencent après

    # 3) Construire une chaîne avec uniquement les lignes de données
    data_str = "".join(lines[start_idx:])

    # 4) Parser avec pandas : séparateur = tab, décimale = virgule
    df = pd.read_csv(
        io.StringIO(data_str),
        sep="\t",
        decimal=",",
        engine="python"
    )

    # 5) Normaliser les noms de colonnes
    # Par ex. "X_Value" -> "t", "Generateur" -> "gen", "Lumiere" -> "lum"
    cols_lower = {c.lower(): c for c in df.columns}

    if "x_value" in cols_lower:
        df = df.rename(columns={cols_lower["x_value"]: "t"})
    else:
        raise ValueError(f"Colonne X_Value introuvable dans {filepath}")

    if "generateur" in cols_lower:
        df = df.rename(columns={cols_lower["generateur"]: "gen"})
    if "lumiere" in cols_lower:
        df = df.rename(columns={cols_lower["lumiere"]: "lum"})
    if "comment" in cols_lower:
        df = df.rename(columns={cols_lower["comment"]: "comment"})

    # Conversion en float
    for col in ["t", "gen", "lum"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def remove_outliers(df, column="lum", zmax=3.5):
    """
    Filtrage simple des valeurs aberrantes sur une colonne (par défaut 'lum').

    On enlève les points dont le z-score est > zmax.
    """
    if column not in df.columns:
        return df

    data = df[column].astype(float)
    z = (data - data.mean()) / data.std(ddof=0)
    mask = np.abs(z) < zmax
    df_clean = df[mask].reset_index(drop=True)
    return df_clean