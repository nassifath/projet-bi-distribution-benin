import pandas as pd
# pandas = bibliothèque principale pour manipuler des tableaux de données

def nettoyer(df, nom_boutique):
    # Cette fonction reçoit un DataFrame brut et le nom de la boutique
    # Elle corrige tous les problèmes de qualité des données
    # Elle retourne le DataFrame propre avec une colonne boutique ajoutée

    # Problème 1 : clients manquants → remplacer NaN par "ANONYME"
    df["id_client"] = df["id_client"].fillna("ANONYME")

    # Problème 2 : remise stockée comme texte avec virgule → convertir en nombre
    # astype(str) : convertit en texte d'abord
    # str.replace(",", ".") : remplace la virgule par un point
    # str.replace("%", "") : supprime le signe % si présent
    # astype(float) : convertit en nombre décimal
    df["remise"] = df["remise"].astype(str).str.replace(",", ".").str.replace("%", "").astype(float)

    # Problème 3 : date stockée comme texte → convertir en vraie date
    # dayfirst=True : le jour vient en premier dans nos dates (JJ/MM/AAAA)
    # errors="coerce" : si une date est illisible → NaT au lieu de planter
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

    # Problème 4 : quantite en float (4.0) → convertir en entier (4)
    # Int64 avec majuscule : accepte les valeurs nulles, contrairement à int64
    df["quantite"] = df["quantite"].astype("Int64")

    # Ajout d'une colonne pour identifier la boutique d'origine
    # utile quand on va fusionner tous les fichiers ensemble
    df["boutique"] = nom_boutique

    return df
    # return renvoie le DataFrame corrigé à celui qui a appelé la fonction

# ── UTILISATION ──
# On lit le fichier brut
df1= pd.read_csv("ventes_cotonou.csv", sep=";", encoding="latin1")

# On appelle la fonction pour nettoyer — elle reçoit df et retourne df corrigé
df1= nettoyer(df1, "Cotonou")

# Abomey-Calavi — colonnes avec noms différents, date avec heure(on uniformise les noms partout)
df2=pd.read_csv("ventes_abomey_calavi.csv", sep=";", encoding="latin1")

# rename() renomme les colonnes pour les harmoniser avec Cotonou
df2= df2.rename(columns=
                   {
                        "N_Transaction": "id_transaction",
                        "Date_Vente":    "date",
                        "Client":        "id_client",
                        "Ref_Produit":   "id_produit",
                        "Qte":           "quantite",
                        "PU":            "prix_unitaire",
                        "Remise_pct":    "remise",
                        "Total":         "montant",
                        "Employé":       "vendeur",
                    }   
                )
# la date contient l'heure "27/09/2025 19:49" → on garde juste la date
df2["date"] = df2["date"].str.split("").str[0]
df2 =nettoyer(df2, "Abomey-Calavi")

# Bohicon — colonnes en majuscule
df3 = pd.read_csv("ventes_bohicon.csv")
# on met toutes les colonnes en minuscule
df3.columns = df3.columns.str.lower()
df3 = df3.rename(columns={
    "prix_unit": "prix_unitaire",
    "qte":       "quantite",
    "client":    "id_client",
    "produit":   "id_produit"
})
df3 = nettoyer(df3, "Bohicon")

# Natitingou — séparateur point-virgule
df4 = pd.read_csv("ventes_natitingou.csv", sep=";", encoding="latin1")
df4 = nettoyer(df4, "Natitingou")

# Parakou — fichier .txt avec tabulation comme séparateur
df5 = pd.read_csv("ventes_parakou.txt", sep="\t", encoding="utf-8")
df5 = nettoyer(df5, "Parakou")

# Porto-Novo
df6 = pd.read_csv("ventes_porto_novo.csv", encoding="latin1")
df6 = nettoyer(df6, "Porto-Novo")

# ── FUSION ──
# concat assemble tous les DataFrames en un seul
# ignore_index=True : recrée les numéros de lignes de 0 à la fin
ventes = pd.concat([df1, df2, df3, df4, df5, df6], ignore_index=True)

# shape affiche les dimensions du tableau fusionné
# on attend (180540, 10) = toutes les lignes des 6 villes réunies
print(ventes.shape)


# value_counts() compte combien de lignes il y a par boutique
# ça nous permet de vérifier que toutes les villes sont bien présentes
# et que le nombre de lignes correspond à ce qu'on attendait
print(ventes["boutique"].value_counts())


# ── EXPORT ──
# to_csv() sauvegarde le DataFrame dans un fichier CSV
# index=False : on ne sauvegarde pas les numéros de lignes
ventes.to_csv("ventes_unifie.csv", index=False)

print("Fichier sauvegardé : ventes_unifie.csv")