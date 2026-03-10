import pandas as pd

df = pd.read_excel("conduites-sucidaires-indicateurs-du-barometre-2024.xlsx")
print("SitFin:", list(df["Situation financière perçue"].unique()))
print()
print("Sexe:", list(df["Sexe"].unique()))
print()
print("Age:", list(df["Classe d'âge"].unique()))
print()
print("Diplome:", list(df["Diplôme"].unique()))
print()

# Financial situation rows
mask = (
    df["Indicateur"].str.contains("Pensées suicidaires", case=False, na=False)
    & (df["Situation financière perçue"] != "Tous")
    & df["Situation financière perçue"].notna()
    & (df["Sexe"] == "Tous")
)
print("Financial rows (Sexe=Tous):", mask.sum())
print(df[mask][["Situation financière perçue", "Estimation"]].to_string())
print()

# Age group rows for pensées suicidaires
mask2 = (
    df["Indicateur"].str.contains("Pensées suicidaires", case=False, na=False)
    & (df["Classe d'âge"] != "Tous")
    & df["Classe d'âge"].notna()
    & (df["Sexe"] == "Tous")
    & (df["Situation financière perçue"] == "Tous")
    & (df["Diplôme"] == "Tous")
)
print("Age pensées suicidaires (Sexe=Tous):", mask2.sum())
print(df[mask2][["Classe d'âge", "Estimation"]].to_string())
print()

# Tentatives by age + sex
mask3 = (
    df["Indicateur"].str.contains("Tentative de suicide au cours de la vie", case=False, na=False)
    & (df["Classe d'âge"] != "Tous")
    & df["Classe d'âge"].notna()
    & (df["Sexe"] != "Tous")
    & (df["Diplôme"] == "Tous")
    & (df["Situation financière perçue"] == "Tous")
)
print("Tentatives vie by age+sex:", mask3.sum())
print(df[mask3][["Classe d'âge", "Sexe", "Estimation", "Effectif Brut"]].to_string())
