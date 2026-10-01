import pandas as pd
import json

# ════════════════════════════════════════
# CHARGEMENT DES DONNÉES BRUTES
# ════════════════════════════════════════

# on recharge le fichier de ventes nettoyé
ventes = pd.read_csv("ventes_unifie.csv", low_memory=False)

# on force les colonnes numériques
ventes["montant"] = pd.to_numeric(ventes["montant"], errors="coerce")
ventes["quantite"] = pd.to_numeric(ventes["quantite"], errors="coerce")
ventes["prix_unitaire"] = pd.to_numeric(ventes["prix_unitaire"], errors="coerce")
ventes["remise"] = pd.to_numeric(ventes["remise"], errors="coerce")
ventes["date"] = pd.to_datetime(ventes["date"])

# on charge le catalogue produits
with open("produits.json", encoding="utf-8") as f:
    data = json.load(f)
produits_raw = pd.DataFrame(data["catalogue"]["produits"])
produits_raw["categorie"] = produits_raw["categorie"].apply(lambda x: x["nom"])
produits_raw["prix_achat"] = produits_raw["prix"].apply(lambda x: x["achat"])
produits_raw["prix_vente"] = produits_raw["prix"].apply(lambda x: x["vente"])
produits_raw["fournisseur"] = produits_raw["fournisseur"].apply(lambda x: x["nom"] if x else "Inconnu")
produits_raw = produits_raw.drop(columns=["prix"])

# on charge les clients des deux feuilles Excel
clients_2023 = pd.read_excel("clients.xlsx", sheet_name="Clients_2023")
clients_2024 = pd.read_excel("clients.xlsx", sheet_name="Clients_2024_2025")

# on charge les vendeurs
vendeurs_raw = pd.read_excel("employes_objectifs.xlsx", sheet_name="Vendeurs", skiprows=2)

# ════════════════════════════════════════
# TABLE 1 — dim_temps
# ════════════════════════════════════════

dates_uniques = ventes["date"].dropna().unique()
dim_temps = pd.DataFrame({"date": dates_uniques})
dim_temps["date"] = pd.to_datetime(dim_temps["date"])
dim_temps["annee"] = dim_temps["date"].dt.year
dim_temps["trimestre"] = dim_temps["date"].dt.quarter
dim_temps["mois_num"] = dim_temps["date"].dt.month
dim_temps["mois_nom"] = dim_temps["date"].dt.strftime("%B")
dim_temps["semaine"] = dim_temps["date"].dt.isocalendar().week.astype(int)
dim_temps["jour_num"] = dim_temps["date"].dt.day
dim_temps["jour_nom"] = dim_temps["date"].dt.strftime("%A")
dim_temps["est_weekend"] = dim_temps["date"].dt.dayofweek.isin([5, 6]).astype(int)
dim_temps = dim_temps.sort_values("date").reset_index(drop=True)

dim_temps.to_csv("dim_temps.csv", index=False)
print(f"✓ dim_temps : {dim_temps.shape}")

# ════════════════════════════════════════
# TABLE 2 — dim_produits
# ════════════════════════════════════════

dim_produits = produits_raw[["id", "libelle", "categorie", "prix_achat", "prix_vente", "fournisseur", "actif"]].copy()
dim_produits["categorie"] = dim_produits["categorie"].str.strip().str.title()
dim_produits["categorie"] = dim_produits["categorie"].replace({
    "Vetements":    "Vêtements",
    "Vetement":     "Vêtements",
    "Alimentaire":  "Alimentation",
    "Electronique": "Électronique",
})
dim_produits = dim_produits.rename(columns={"id": "id_produit"})
dim_produits["id_produit"] = (dim_produits["id_produit"]
    .astype(str).str.upper().str.strip()
    .str.replace(r'^P-0*', 'P0', regex=True)
    .str.replace(r'^P-', 'P', regex=True))
dim_produits = dim_produits.drop_duplicates(subset=["id_produit"], keep="first")
dim_produits["prix_achat"] = pd.to_numeric(dim_produits["prix_achat"], errors="coerce")
dim_produits["prix_vente"] = pd.to_numeric(dim_produits["prix_vente"], errors="coerce")

dim_produits.to_csv("dim_produits.csv", index=False)
print(f"✓ dim_produits : {dim_produits.shape}")

# ════════════════════════════════════════
# TABLE 3 — dim_clients
# ════════════════════════════════════════

clients_2023.columns = clients_2023.columns.str.strip()
clients_2024.columns = clients_2024.columns.str.strip()
dim_clients = pd.concat([clients_2023, clients_2024], ignore_index=True)
dim_clients = dim_clients.drop_duplicates(subset=["ID"], keep="last")
dim_clients = dim_clients.rename(columns={"ID": "id_client"})
dim_clients["Ville"] = dim_clients["Ville"].str.strip().str.title()
dim_clients["Sexe"] = dim_clients["Sexe"].str.strip().str.title()
dim_clients["Sexe"] = dim_clients["Sexe"].replace({
    "Masculin": "M", "Homme": "M", "H": "M",
    "Feminin": "F", "Femme": "F",
})

dim_clients.to_csv("dim_clients.csv", index=False)
print(f"✓ dim_clients : {dim_clients.shape}")

# ════════════════════════════════════════
# TABLE 4 — dim_boutiques
# ════════════════════════════════════════

boutiques = sorted(ventes["boutique"].unique())
dim_boutiques = pd.DataFrame({
    "id_boutique": range(1, len(boutiques) + 1),
    "boutique":    boutiques,
    "region": ["Atlantique", "Atacora", "Littoral", "Borgou", "Zou", "Ouémé"]
})

dim_boutiques.to_csv("dim_boutiques.csv", index=False)
print(f"✓ dim_boutiques : {dim_boutiques.shape}")

# ════════════════════════════════════════
# TABLE 5 — dim_vendeurs
# ════════════════════════════════════════

dim_vendeurs = vendeurs_raw[["id_vendeur", "nom_complet", "boutique", "date_embauche", "statut"]].copy()
dim_vendeurs = dim_vendeurs.dropna(subset=["id_vendeur"])

dim_vendeurs.to_csv("dim_vendeurs.csv", index=False)
print(f"✓ dim_vendeurs : {dim_vendeurs.shape}")

# ════════════════════════════════════════
# TABLE 6 — fait_ventes (table centrale)
# ════════════════════════════════════════

fait_ventes = ventes[[
    "id_transaction", "date", "id_client", "id_produit",
    "boutique", "vendeur", "quantite", "prix_unitaire", "remise", "montant",
]].copy()

# normalisation id_produit
fait_ventes["id_produit"] = (fait_ventes["id_produit"]
    .astype(str).str.upper().str.strip()
    .str.replace(r'^P-0*', 'P0', regex=True)
    .str.replace(r'^P-', 'P', regex=True))

# fusion avec prix_achat pour calculer la marge
fait_ventes = fait_ventes.merge(
    dim_produits[["id_produit", "prix_achat"]], on="id_produit", how="left")

# calcul cout et marge
fait_ventes["cout"] = fait_ventes["prix_achat"] * fait_ventes["quantite"]
fait_ventes["marge_brute"] = fait_ventes["montant"] - fait_ventes["cout"]
fait_ventes = fait_ventes.drop(columns=["prix_achat"])

# forcer toutes les colonnes numériques
fait_ventes["montant"] = pd.to_numeric(fait_ventes["montant"], errors="coerce")
fait_ventes["quantite"] = pd.to_numeric(fait_ventes["quantite"], errors="coerce")
fait_ventes["prix_unitaire"] = pd.to_numeric(fait_ventes["prix_unitaire"], errors="coerce")
fait_ventes["remise"] = pd.to_numeric(fait_ventes["remise"], errors="coerce")
fait_ventes["cout"] = pd.to_numeric(fait_ventes["cout"], errors="coerce")
fait_ventes["marge_brute"] = pd.to_numeric(fait_ventes["marge_brute"], errors="coerce")

fait_ventes.to_csv("fait_ventes.csv", index=False)
print(f"✓ fait_ventes : {fait_ventes.shape}")

# ════════════════════════════════════════
# TABLE 7 — paiements_propre
# ════════════════════════════════════════
# on nettoie les modes de paiement et les statuts
# pour éviter les doublons dans Tableau

paiements = pd.read_csv("paiements.csv", encoding="utf-8", low_memory=False)

# normalisation mode de paiement
paiements["mode_paiement"] = paiements["mode_paiement"].str.lower().str.strip()
paiements["mode_paiement"] = paiements["mode_paiement"].replace({
    "mtn mobile money": "MTN MoMo",
    "momo mtn":         "MTN MoMo",
    "mtn momo":         "MTN MoMo",
    "espèces":          "Espèces",
    "especes":          "Espèces",
    "cash":             "Espèces",
    "moov":             "Moov Money",
    "moov money":       "Moov Money",
    "carte bancaire":   "Carte Bancaire",
    "carte":            "Carte Bancaire",
    "cb":               "Carte Bancaire",
})

# normalisation statut
paiements["statut"] = paiements["statut"].str.lower().str.strip()
paiements["statut"] = paiements["statut"].replace({
    "ok":     "Réussi",
    "reussi": "Réussi",
    "réussi": "Réussi",
    "echec":  "Échoué",
    "échoué": "Échoué",
})

paiements.to_csv("paiements_propre.csv", index=False)
print(f"✓ paiements_propre : {paiements.shape}")

# ════════════════════════════════════════
# RÉSUMÉ FINAL
# ════════════════════════════════════════
print("\n╔══════════════════════════════════════════╗")
print("║   SCHÉMA EN ÉTOILE — TABLES EXPORTÉES   ║")
print("╚══════════════════════════════════════════╝")
print("  fait_ventes.csv       → table centrale")
print("  dim_temps.csv         → dimension temps")
print("  dim_produits.csv      → dimension produits")
print("  dim_clients.csv       → dimension clients")
print("  dim_boutiques.csv     → dimension boutiques")
print("  dim_vendeurs.csv      → dimension vendeurs")
print("  paiements_propre.csv  → paiements nettoyés")
print("\n✅ Prêt pour Tableau")