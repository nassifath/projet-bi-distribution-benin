import pandas as pd
import json

# ── ÉTAPE 1 : CHARGEMENT ──

# On charge le fichier de ventes nettoyé
# low_memory=False : évite un avertissement sur les types mixtes
ventes = pd.read_csv("ventes_unifie.csv", low_memory=False)

# On ouvre le fichier JSON des produits
with open("produits.json", encoding="utf-8") as f:
    data = json.load(f)

# On transforme la liste des produits en tableau pandas
produits = pd.DataFrame(data["catalogue"]["produits"])

# ── ÉTAPE 2 : EXTRACTION DES COLONNES IMBRIQUÉES ──

# categorie est un dictionnaire — on extrait juste le nom
produits["categorie"] = produits["categorie"].apply(lambda x: x["nom"])

# prix est un dictionnaire — on extrait achat et vente séparément
produits["prix_achat"] = produits["prix"].apply(lambda x: x["achat"])
produits["prix_vente"] = produits["prix"].apply(lambda x: x["vente"])

# on supprime les colonnes qui ne servent plus
produits = produits.drop(columns=["prix", "fournisseur"])

# ── ÉTAPE 3 : JOINTURE VENTES + PRODUITS ──

# merge() fusionne deux tableaux sur une colonne commune
# how="left" : on garde toutes les lignes de ventes
ventes = ventes.merge(produits, left_on="id_produit", right_on="id", how="left")

# ── ÉTAPE 4 : CALCUL DE LA MARGE ──

# forcer les colonnes en nombres avant de calculer
ventes["montant"] = pd.to_numeric(ventes["montant"], errors="coerce")
ventes["quantite"] = pd.to_numeric(ventes["quantite"], errors="coerce")
ventes["prix_achat"] = pd.to_numeric(ventes["prix_achat"], errors="coerce")

# calcul de la marge
ventes["cout"] = ventes["prix_achat"] * ventes["quantite"]
ventes["marge_brute"] = ventes["montant"] - ventes["cout"]
ventes["marge_pct"] = (ventes["marge_brute"] / ventes["montant"] * 100).round(2)

# ── QUESTION 1 : MARGE PAR BOUTIQUE ET CATÉGORIE ──
print("=" * 60)
print("QUESTION 1 — MARGE PAR BOUTIQUE")
print("=" * 60)
marge_boutique = ventes.groupby("boutique").agg(
    ca_total        = ("montant", "sum"),
    cout_total      = ("cout", "sum"),
    marge_totale    = ("marge_brute", "sum"),
    nb_transactions = ("id_transaction", "count")
).reset_index()
marge_boutique["taux_marge"] = (marge_boutique["marge_totale"] / marge_boutique["ca_total"] * 100).round(2)
marge_boutique = marge_boutique.sort_values("marge_totale", ascending=False)
print(marge_boutique.to_string())

print("\n")
print("=" * 60)
print("QUESTION 1 — MARGE PAR CATÉGORIE")
print("=" * 60)
marge_categorie = ventes.groupby("categorie").agg(
    ca_total     = ("montant", "sum"),
    cout_total   = ("cout", "sum"),
    marge_totale = ("marge_brute", "sum")
).reset_index()
marge_categorie["taux_marge"] = (marge_categorie["marge_totale"] / marge_categorie["ca_total"] * 100).round(2)
marge_categorie = marge_categorie.sort_values("marge_totale", ascending=False)
print(marge_categorie.to_string())

# ── QUESTION 2 : VENTES À PERTE ──
print("\n")
print("=" * 60)
print("QUESTION 2 — VENTES À PERTE")
print("=" * 60)
ventes_perte = ventes[ventes["marge_brute"] < 0]
print("Nombre de ventes à perte :", len(ventes_perte))
print("\nPar boutique :")
print(ventes_perte.groupby("boutique")["marge_brute"].sum().sort_values())
print("\nPar catégorie :")
print(ventes_perte.groupby("categorie")["marge_brute"].sum().sort_values())
print("\nTop 10 produits vendus à perte :")
print(ventes_perte.groupby("libelle")["marge_brute"].sum().sort_values().head(10).to_string())

# ── QUESTION 3 : ÉVOLUTION DANS LE TEMPS ──
print("\n")
print("=" * 60)
print("QUESTION 3 — ÉVOLUTION DES VENTES")
print("=" * 60)

# on convertit la date en datetime au cas où
ventes["date"] = pd.to_datetime(ventes["date"])

# on extrait l'année et le mois
# dt.to_period("M") convertit une date en période mensuelle ex: 2023-01
ventes["mois"] = ventes["date"].dt.to_period("M")
ventes["annee"] = ventes["date"].dt.year

# CA mensuel
ca_mensuel = ventes.groupby("mois")["montant"].sum().reset_index()
ca_mensuel.columns = ["mois", "ca"]
print("CA mensuel (12 derniers mois) :")
print(ca_mensuel.tail(12).to_string())

# CA annuel
ca_annuel = ventes.groupby("annee")["montant"].sum().reset_index()
ca_annuel.columns = ["annee", "ca"]
print("\nCA annuel :")
print(ca_annuel.to_string())

# ── QUESTION 4 : MEILLEURS CLIENTS ──
print("\n")
print("=" * 60)
print("QUESTION 4 — MEILLEURS CLIENTS")
print("=" * 60)

# on exclut les anonymes pour cette analyse
clients_identifies = ventes[ventes["id_client"] != "ANONYME"]

# top 10 clients par CA
top_clients = clients_identifies.groupby("id_client").agg(
    ca_total        = ("montant", "sum"),
    nb_achats       = ("id_transaction", "count"),
    marge_generee   = ("marge_brute", "sum")
).reset_index()
top_clients = top_clients.sort_values("ca_total", ascending=False)
print("Top 10 clients par CA :")
print(top_clients.head(10).to_string())

# panier moyen par client
panier_moyen = clients_identifies.groupby("id_client")["montant"].mean().mean()
print(f"\nPanier moyen global : {panier_moyen:,.0f} FCFA")

# ── QUESTION 5 : MODES DE PAIEMENT ──
print("\n")
print("=" * 60)
print("QUESTION 5 — MODES DE PAIEMENT")
print("=" * 60)

# on charge le fichier paiements
paiements = pd.read_csv("paiements.csv", encoding="utf-8", low_memory=False)

# normalisation du mode de paiement — tout en minuscule sans espaces
# pour regrouper "MTN MoMo" et "mtn momo" ensemble
paiements["mode_paiement"] = paiements["mode_paiement"].str.lower().str.strip()

print("Répartition par mode de paiement :")
print(paiements["mode_paiement"].value_counts())

print("\nMontant total par mode :")
repartition = paiements.groupby("mode_paiement").agg(
    nb_transactions = ("id_transaction", "count"),
    montant_total   = ("montant_paye", "sum")
).reset_index()
repartition = repartition.sort_values("montant_total", ascending=False)
print(repartition.to_string())

print("\nStatut des paiements :")
print(paiements["statut"].value_counts())

# ── QUESTION 6 : RETOURS ET RUPTURES ──
print("\n")
print("=" * 60)
print("QUESTION 6 — RETOURS ET RUPTURES DE STOCK")
print("=" * 60)

# on charge le fichier retours
retours = pd.read_excel("retours_stocks.xlsx", sheet_name="Retours")
ruptures = pd.read_excel("retours_stocks.xlsx", sheet_name="Ruptures")

print("Retours — shape :", retours.shape)
print("\nCoût total des retours :")
print(f"{retours['montant_rembourse'].sum():,.0f} FCFA")

print("\nRetours par boutique :")
print(retours.groupby("boutique")["montant_rembourse"].sum().sort_values(ascending=False))

print("\nRetours par motif :")
print(retours["motif"].value_counts())

print("\nRuptures de stock :")
print(ruptures.shape)
print(ruptures.groupby("boutique").size().sort_values(ascending=False))

# ── QUESTION 7 : OBJECTIFS 2025 ──
print("\n")
print("=" * 60)
print("QUESTION 7 — OBJECTIFS 2025 ATTEINTS ?")
print("=" * 60)

# on charge les objectifs
objectifs = pd.read_excel("employes_objectifs.xlsx", sheet_name="Objectifs_2025", skiprows=4)
# skiprows=4 : on saute les 4 premières lignes qui sont des titres

print("Objectifs chargés :")
print(objectifs.head())

# CA réel 2025 par boutique par mois
ventes_2025 = ventes[ventes["annee"] == 2025].copy()
ventes_2025["mois_num"] = ventes_2025["date"].dt.month

ca_2025 = ventes_2025.groupby(["boutique", "mois_num"])["montant"].sum().reset_index()
ca_2025.columns = ["boutique", "mois", "ca_reel"]

print("\nCA réel 2025 par boutique :")
print(ventes_2025.groupby("boutique")["montant"].sum().sort_values(ascending=False))