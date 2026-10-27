import numpy as np
import pandas as pd
from fetchdata import get_who_data, get_who_datas


def dictionnaire_vers_matrice(data_dict):
  """Transforme un dictionnaire {indicateur: valeur} en matrice 2D NumPy (N lignes, 2 colonnes)."""
  if not data_dict:
    return np.empty((0, 2), dtype=object)

  paires = [[cle, str(valeur)] for cle, valeur in data_dict.items()]
  matrice = np.array(paires, dtype=object)
  return matrice


def matrice_vers_dataframe(matrice, categorie=None):
  """Transforme une matrice NumPy 2D en DataFrame pandas."""
  if matrice.size == 0:
    df = pd.DataFrame(columns=["Indicateur", "Valeur"])
  else:
    df = pd.DataFrame(matrice, columns=["Indicateur", "Valeur"])

  if categorie:
    df.insert(0, "Catégorie", categorie)

  return df


def traiter_donnees_profil(donnees):
  """Prend en entrée les résultats de get_who_data:

  {"pas": {...}, "cap": {...}, "cyclisme": {...}, "forme": {...}}

  1. Crée des matrices NumPy pour chaque catégorie.
  2. Transforme ces matrices en DataFrames pandas.
  3. Construit également une matrice et un DataFrame consolidés pour tout le profil.
  """
  categories = ["pas", "cap", "cyclisme", "forme"]
  matrices = {}
  dataframes = {}

  lignes_globales = []

  for cat in categories:
    cat_dict = donnees.get(cat, {})

    # 1. Création de la matrice NumPy (N x 2)
    matrice = dictionnaire_vers_matrice(cat_dict)
    matrices[cat] = matrice

    # 2. Transformation de la matrice en DataFrame pandas
    df = matrice_vers_dataframe(matrice, categorie=cat)
    dataframes[cat] = df

    # Accumulation pour la matrice globale
    for k, v in cat_dict.items():
      lignes_globales.append([cat, k, str(v)])

  # 3. Matrice globale consolidée et DataFrame global
  if lignes_globales:
    matrice_globale = np.array(lignes_globales, dtype=object)
    df_global = pd.DataFrame(
        matrice_globale, columns=["Catégorie", "Indicateur", "Valeur"]
    )
  else:
    matrice_globale = np.empty((0, 3), dtype=object)
    df_global = pd.DataFrame(columns=["Catégorie", "Indicateur", "Valeur"])

  matrices["global"] = matrice_globale
  dataframes["global"] = df_global

  return {
      "matrices": matrices,
      "dataframes": dataframes,
      "df_global": df_global,
      "df_pas": dataframes["pas"],
      "df_cap": dataframes["cap"],
      "df_cyclisme": dataframes["cyclisme"],
      "df_forme": dataframes["forme"],
  }


def obtenir_donnees_traitees(driver=None):
  """Récupère les données avec get_who_data() puis les traite en matrices NumPy / DataFrames pandas."""
  donnees = get_who_data(driver)
  return traiter_donnees_profil(donnees)


if __name__ == "__main__":
  print("--- Traitement des données Garmin (NumPy & Pandas) ---")
  try:
    print("Récupération des données en direct via get_who_data()...")
    donnees_brutes = get_who_data()
    resultats = traiter_donnees_profil(donnees_brutes)

    print("\n=== MATRICES NUMPY ===")
    for nom, mat in resultats["matrices"].items():
      print(f"\nMatrice '{nom}' (shape={mat.shape}):")
      print(mat)

    print("\n=== DATAFRAMES PANDAS ===")
    for nom, df in resultats["dataframes"].items():
      print(f"\nDataFrame '{nom}':")
      print(df)
  except Exception as e:
    print(f"Erreur : {e}")
