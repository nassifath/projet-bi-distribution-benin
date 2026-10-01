# 📊 Projet BI — Groupe Distribution Bénin

Analyse complète des données de ventes d'un réseau de 6 boutiques au Bénin sur la période 2023–2025.

## 🎯 Objectif

Répondre aux 7 questions stratégiques de la direction à partir de données brutes hétérogènes :

1. Quelles boutiques et catégories rapportent réellement de l'argent ?
2. Y a-t-il des produits ou périodes où l'on vend à perte ?
3. Comment évoluent les ventes dans le temps ?
4. Qui sont les meilleurs clients ?
5. Quel est le poids de chaque mode de paiement ?
6. Les retours et ruptures de stock coûtent-ils cher ?
7. Les objectifs 2025 sont-ils atteints ?

---

## 📁 Structure du projet

```
projet-bi-distribution-benin/
│
├── nettoyage.py        # Nettoyage et fusion des 12 fichiers sources
├── analyse.py          # Exploration et réponses aux 7 questions
├── modelisation.py     # Schéma en étoile — export des tables pour Tableau
├── visualisation.py    # Graphiques Python (matplotlib)
│
└── README.md
```

---

## 🗂️ Sources de données

| Fichier | Contenu | Volume |
|---|---|---|
| `ventes_*.csv / .txt` | Transactions par boutique | 180 540 lignes |
| `produits.json` | Catalogue produits | 244 références |
| `clients.xlsx` | Base clients | 8 002 clients |
| `paiements.csv` | Transactions financières | 178 158 lignes |
| `retours_stocks.xlsx` | Retours et ruptures | 5 100 lignes |
| `employes_objectifs.xlsx` | Vendeurs et objectifs 2025 | 24 vendeurs |

---

## 🔧 Outils utilisés

- **Python 3** — pandas, matplotlib, json, openpyxl
- **Tableau Public** — Dashboard interactif
- **VS Code** — Environnement de développement

---

## 🧹 Problèmes de qualité traités

- 4 formats de dates différents entre fichiers
- Noms de colonnes hétérogènes
- Remises stockées comme texte (`0,15` au lieu de `0.15`)
- IDs produits inconsistants (`P0168` / `p-0168` / `PROD-0168`)
- Modes de paiement dupliqués (`mtn momo`, `MTN MoMo`, `mtn mobile money`)
- 39% de clients anonymes — traités comme réalité métier

---

## ⭐ Modélisation — Schéma en étoile

```
              [dim_temps]
                   |
[dim_produits]─[fait_ventes]─[dim_clients]
                   |
            [dim_boutiques]
                   |
            [dim_vendeurs]
```

---

## 📈 Insights clés

- **Bohicon** : taux de marge de **34%** — meilleure boutique malgré un CA modeste
- **Électronique** : **9,5% des ventes réalisées à perte** (17 203 transactions)
- **Croissance** : +9% en 2024, +14% en 2025
- **Mobile money** : **55% des paiements** (MTN MoMo + Moov Money)
- **Clients anonymes** : **39%** des ventes sans identification

---

## 🚀 Comment exécuter

```bash
# 1. Installer les dépendances
pip install pandas matplotlib openpyxl

# 2. Nettoyage et fusion
python nettoyage.py

# 3. Analyse
python analyse.py

# 4. Modélisation
python modelisation.py

# 5. Visualisation
python visualisation.py
```

---

## 👤 Auteur

**Sobour SANNI** — Data Analyst  
*Projet réalisé dans le cadre d'un apprentissage pratique de l'analyse de données*
