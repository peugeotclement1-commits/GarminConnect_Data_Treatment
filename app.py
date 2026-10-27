"""Interface terminal des statistiques Garmin avec Rich."""

import re

import pandas as pd
from rich import box
from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table

from treatdata import obtenir_donnees_traitees


def _libelle_affiche(indicateur, categorie):
  """Raccourcit les libellés pour qu'ils tiennent dans les colonnes."""
  libelle = str(indicateur).strip()

  if categorie == "pas":
    libelle = re.sub(r"\bde\s+pas\b", "", libelle, flags=re.IGNORECASE)
    libelle = re.sub(r"\bpas\b", "", libelle, flags=re.IGNORECASE)
    libelle = re.sub(r"\s+", " ", libelle).strip(" :–-")
    libelle = re.sub(r"\b(en\s+)?(un|une)\s+jour(née)?\b", "en un jour", libelle, flags=re.IGNORECASE)
    libelle = re.sub(r"\b(en\s+)?(une?)\s+semaine\b", "en une semaine", libelle, flags=re.IGNORECASE)
    if "record" in libelle.lower() and not libelle.lower().startswith("record"):
      libelle = "Record " + libelle
    return libelle[:1].upper() + libelle[1:] if libelle else str(indicateur)

  if categorie == "cyclisme" and any(
      mot in libelle.lower() for mot in ("longue", "longest", "distance maximale", "plus grande distance")
  ):
    return "Plus longue sortie"

  return libelle


def _tableau_stats(dataframe, categorie):
  """Construit un tableau sans colonne de catégorie ni index de lignes."""
  tableau = Table(box=box.SIMPLE, expand=True, show_header=False, padding=(0, 1))
  tableau.add_column("Indicateur", style="cyan", ratio=3, overflow="fold")
  tableau.add_column("Valeur", style="bold white", justify="right", ratio=2, overflow="fold")

  if dataframe is None or dataframe.empty:
    tableau.add_row("Aucune donnée disponible", "")
    return tableau

  # Les dataframes transmis contiennent les colonnes Indicateur et Valeur.
  # L'index pandas n'est jamais rendu dans le tableau Rich.
  colonnes = {str(col).lower(): col for col in dataframe.columns}
  col_indicateur = colonnes.get("indicateur")
  col_valeur = colonnes.get("valeur")
  if col_indicateur is None or col_valeur is None:
    tableau.add_row("Format de données non reconnu", "")
    return tableau

  for _, ligne in dataframe.iterrows():
    tableau.add_row(
        _libelle_affiche(ligne[col_indicateur], categorie),
        str(ligne[col_valeur]),
    )
  return tableau


def afficher_profil(resultats, console=None):
  """Affiche les trois activités principales en colonnes."""
  console = console or Console()
  dataframes = resultats.get("dataframes", {})
  categories = (("pas", "PAS"), ("cap", "CAP"), ("cyclisme", "CYCLISME"))
  panneaux = [
      Panel(
          _tableau_stats(dataframes.get(cle, pd.DataFrame()), cle),
          title=f"[bold]{titre}[/bold]",
          border_style="bright_blue",
          box=box.SQUARE,
          padding=(1, 1),
          expand=True,
      )
      for cle, titre in categories
  ]
  console.print(Panel("[bold white]WHO[/bold white]", box=box.SQUARE, style="white", padding=(0, 1)))
  console.print(Columns(panneaux, equal=True, expand=True, padding=(0, 0)))


def main():
  console = Console()
  try:
    resultats = obtenir_donnees_traitees()
    afficher_profil(resultats, console)
  except Exception as erreur:
    console.print(Panel(f"Impossible de récupérer les données Garmin : {erreur}", title="Erreur", border_style="red"))


if __name__ == "__main__":
  main()
