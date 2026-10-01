import pandas as pd
import json
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
# matplotlib.pyplot : la bibliothèque qui crée les graphiques
# matplotlib.ticker : pour formater les nombres sur les axes (ex: 1,000,000 au lieu de 1000000)

# ════════════════════════════════════════
# CHARGEMENT ET PRÉPARATION DES DONNÉES
# ════════════════════════════════════════

# on recharge le fichier de ventes nettoyé
ventes = pd.read_csv("ventes_unifie.csv", low_memory=False)

# on recharge le catalogue produits
with open("produits.json", encoding="utf-8") as f:
    data = json.load(f)

# on transforme la liste des produits en tableau
produits = pd.DataFrame(data["catalogue"]["produits"])

# on extrait les colonnes imbriquées
produits["categorie"] = produits["categorie"].apply(lambda x: x["nom"])
produits["prix_achat"] = produits["prix"].apply(lambda x: x["achat"])
produits["prix_vente"] = produits["prix"].apply(lambda x: x["vente"])
produits = produits.drop(columns=["prix", "fournisseur"])

# on fusionne ventes et produits pour avoir le prix d'achat sur chaque vente
ventes = ventes.merge(produits, left_on="id_produit", right_on="id", how="left")

# on force les colonnes numériques en nombres
# errors="coerce" : si une valeur est illisible → NaN au lieu de planter
ventes["montant"] = pd.to_numeric(ventes["montant"], errors="coerce")
ventes["quantite"] = pd.to_numeric(ventes["quantite"], errors="coerce")
ventes["prix_achat"] = pd.to_numeric(ventes["prix_achat"], errors="coerce")

# on calcule le coût et la marge sur chaque vente
ventes["cout"] = ventes["prix_achat"] * ventes["quantite"]
ventes["marge_brute"] = ventes["montant"] - ventes["cout"]

# on convertit la date en vrai type date
ventes["date"] = pd.to_datetime(ventes["date"])

# on extrait le mois et l'année pour les analyses temporelles
ventes["mois"] = ventes["date"].dt.to_period("M")
ventes["annee"] = ventes["date"].dt.year

# on normalise les catégories
# str.strip() : enlève les espaces avant et après
# str.title() : met la première lettre en majuscule
ventes["categorie"] = ventes["categorie"].str.strip().str.title()

# on regroupe les variantes sous un seul nom
# même logique que pour les modes de paiement
ventes["categorie"] = ventes["categorie"].replace({
    "Vetements":   "Vêtements",
    "Vetement":    "Vêtements",
    "Vêtement":    "Vêtements",
    "Alimentaire": "Alimentation",
    "Electronique": "Électronique",
})

# ════════════════════════════════════════
# NETTOYAGE DES PAIEMENTS
# ════════════════════════════════════════

paiements = pd.read_csv("paiements.csv", encoding="utf-8", low_memory=False)

# on normalise le mode de paiement
# str.lower() : tout en minuscule → "MTN MoMo" devient "mtn momo"
# str.strip() : enlève les espaces
paiements["mode_paiement"] = paiements["mode_paiement"].str.lower().str.strip()

# on regroupe les variantes du même mode sous un seul nom
paiements["mode_paiement"] = paiements["mode_paiement"].replace({
    "mtn mobile money": "mtn momo",
    "momo mtn":         "mtn momo",
    "espèces":          "especes",
    "cash":             "especes",
    "moov":             "moov money",
    "carte bancaire":   "carte",
    "cb":               "carte"
})

# on normalise le statut des paiements
paiements["statut"] = paiements["statut"].str.lower().str.strip()
paiements["statut"] = paiements["statut"].replace({
    "ok":     "réussi",
    "reussi": "réussi",
    "echec":  "échoué"
})

# ════════════════════════════════════════
# NETTOYAGE DES RETOURS
# ════════════════════════════════════════

# sheet_name="Retours" : on lit l'onglet "Retours" du fichier Excel
retours = pd.read_excel("retours_stocks.xlsx", sheet_name="Retours")

# on normalise les noms de boutiques
# str.strip() : enlève les espaces
# str.title() : "cotonou" → "Cotonou", "COTONOU" → "Cotonou"
retours["boutique"] = retours["boutique"].str.strip().str.title()

# on regroupe les variantes sous un seul nom
retours["boutique"] = retours["boutique"].replace({
    "Abomey Calavi":  "Abomey-Calavi",
    "Porto Novo":     "Porto-Novo",
})

# ════════════════════════════════════════
# GRAPHIQUE 1 — CA ET MARGE PAR BOUTIQUE
# ════════════════════════════════════════
# répond à la question 1 du brief : quelles boutiques rapportent de l'argent ?

# on groupe par boutique et on calcule le CA total et la marge totale
marge_boutique = ventes.groupby("boutique").agg(
    ca_total     = ("montant", "sum"),
    marge_totale = ("marge_brute", "sum")
).reset_index()

# on trie par CA décroissant
marge_boutique = marge_boutique.sort_values("ca_total", ascending=False)

# figsize=(10, 6) : taille du graphique en pouces (largeur, hauteur)
fig, ax = plt.subplots(figsize=(10, 6))

# x = position de chaque boutique sur l'axe horizontal
x = range(len(marge_boutique))

# barres bleues pour le CA
ax.bar(x, marge_boutique["ca_total"],
       label="CA total", color="#2196F3", width=0.4, align="center")

# barres vertes pour la marge, décalées de 0.4 pour ne pas se superposer
ax.bar([i + 0.4 for i in x], marge_boutique["marge_totale"],
       label="Marge brute", color="#4CAF50", width=0.4, align="center")

# on place les étiquettes des boutiques au centre des deux barres
ax.set_xticks([i + 0.2 for i in x])
ax.set_xticklabels(marge_boutique["boutique"], rotation=15)

# titre et labels des axes
ax.set_title("CA et Marge brute par boutique")
ax.set_ylabel("FCFA")

# format des nombres sur l'axe Y : 1000000 → 1,000,000
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

# légende pour savoir quelle couleur correspond à quoi
ax.legend()

# tight_layout() ajuste automatiquement les marges pour que rien ne soit coupé
plt.tight_layout()

# savefig() sauvegarde le graphique en image PNG dans le dossier
plt.savefig("graphique_1_boutiques.png")
print("✓ Graphique 1 sauvegardé")

# ════════════════════════════════════════
# GRAPHIQUE 2 — ÉVOLUTION MENSUELLE DU CA
# ════════════════════════════════════════
# répond à la question 3 du brief : comment évoluent les ventes dans le temps ?

# on groupe par mois et on somme le CA
ca_mensuel = ventes.groupby("mois")["montant"].sum().reset_index()

# on convertit la période en texte pour l'affichage sur l'axe X
ca_mensuel["mois_str"] = ca_mensuel["mois"].astype(str)

fig, ax = plt.subplots(figsize=(14, 5))

# graphique en ligne avec des points à chaque mois
# marker="o" : affiche un cercle à chaque point
# markersize=4 : taille des cercles
ax.plot(ca_mensuel["mois_str"], ca_mensuel["montant"],
        color="#2196F3", linewidth=2, marker="o", markersize=4)

ax.set_title("Évolution mensuelle du CA — 2023 à 2025")
ax.set_ylabel("FCFA")
ax.set_xlabel("Mois")

# on affiche 1 label sur 3 pour éviter de surcharger l'axe X
ticks = list(range(0, len(ca_mensuel), 3))
ax.set_xticks(ticks)
ax.set_xticklabels([ca_mensuel["mois_str"].iloc[i] for i in ticks], rotation=45)

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
plt.tight_layout()
plt.savefig("graphique_2_evolution.png")
print("✓ Graphique 2 sauvegardé")

# ════════════════════════════════════════
# GRAPHIQUE 3 — TAUX DE MARGE PAR CATÉGORIE
# ════════════════════════════════════════
# répond à la question 1 du brief : quelles catégories rapportent vraiment ?

marge_cat = ventes.groupby("categorie").agg(
    ca_total     = ("montant", "sum"),
    marge_totale = ("marge_brute", "sum")
).reset_index()

# on calcule le taux de marge en pourcentage
marge_cat["taux_marge"] = (marge_cat["marge_totale"] / marge_cat["ca_total"] * 100).round(1)

# on trie du plus faible au plus élevé
marge_cat = marge_cat.sort_values("taux_marge", ascending=True)

fig, ax = plt.subplots(figsize=(8, 5))

# couleur rouge si taux < 10%, vert sinon
couleurs = ["#F44336" if v < 10 else "#4CAF50" for v in marge_cat["taux_marge"]]

# barh() crée des barres horizontales
ax.barh(marge_cat["categorie"], marge_cat["taux_marge"], color=couleurs)

ax.set_title("Taux de marge par catégorie (%)")
ax.set_xlabel("Taux de marge (%)")

# ligne verticale à 0 pour visualiser ce qui est négatif
ax.axvline(x=0, color="black", linewidth=0.8)

plt.tight_layout()
plt.savefig("graphique_3_categories.png")
print("✓ Graphique 3 sauvegardé")

# ════════════════════════════════════════
# GRAPHIQUE 4 — MODES DE PAIEMENT
# ════════════════════════════════════════
# répond à la question 5 du brief : quel est le poids de chaque mode de paiement ?

# on groupe par mode et on somme les montants payés
repartition = paiements.groupby("mode_paiement")["montant_paye"].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(repartition.index, repartition.values, color="#9C27B0")
ax.set_title("Montant total par mode de paiement")
ax.set_ylabel("FCFA")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
plt.tight_layout()
plt.savefig("graphique_4_paiements.png")
print("✓ Graphique 4 sauvegardé")

# ════════════════════════════════════════
# GRAPHIQUE 5 — RETOURS PAR BOUTIQUE
# ════════════════════════════════════════
# répond à la question 6 du brief : les retours coûtent-ils cher ?

# on groupe par boutique et on somme les montants remboursés
retours_boutique = retours.groupby("boutique")["montant_rembourse"].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(retours_boutique.index, retours_boutique.values, color="#FF5722")
ax.set_title("Coût des retours par boutique (FCFA)")
ax.set_ylabel("FCFA")
ax.set_xlabel("Boutique")
plt.xticks(rotation=15)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
plt.tight_layout()
plt.savefig("graphique_5_retours.png")
print("✓ Graphique 5 sauvegardé")
print("\n✅ Tous les graphiques sont sauvegardés dans ton dossier.")