from pathlib import Path
import pandas as pd
import time

def dict_to_csv(csv_chemin, dictionnaire, exclusions, sep=";", encoding="utf-8"):
    csv_fichier = Path(csv_chemin)
    date_str = time.strftime("%Y-%m-%d")
    heure_str = time.strftime("%H:%M:%S")

    ## Colonnes fixes en tête
    col_fixes = ["Date", "Heure"] + exclusions

    ## Lecture du CSV s'il existe, sinon DataFrame vide
    if csv_fichier.exists():
        df = pd.read_csv(csv_fichier, sep=sep, encoding=encoding, dtype={"Rapport.GEN_Symbole_Specimen":str})
    else:
        df = pd.DataFrame(columns=col_fixes)

    ## Tri des colonnes existantes et des clés du dictionnaire par ordre alphabétique
    # Récupération des clés existantes
    cles_actuelles = [c for c in df.columns if c not in col_fixes]
    # Tri des clés existantes avec les potentielles clés rajoutées par le dictionnaire
    # (on ignore les clés qui doivent rester au début du fichier)
    cles_nouvelles = sorted(set(cles_actuelles).union(k for k in dictionnaire.keys() if k not in exclusions), key=str.lower)
    # Ordre final des colonnes
    colonnes = col_fixes + cles_nouvelles
    # Reindexage du DF pour garantir la présence des nouvelles colonnes (remplies avec NaN)
    df = df.reindex(columns=colonnes)

    ## Nouvelle ligne
    # Remplissage des colonnes dont la valeur n'est pas présente dans le dictionaire
    nouvelle_ligne = {col: "" for col in colonnes}  # Valeurs vides par défaut
    nouvelle_ligne["Date"] = date_str
    nouvelle_ligne["Heure"] = heure_str
    # Remplissage avec les valeurs du dictionnaire
    for k, v in dictionnaire.items():
        if k in nouvelle_ligne:
            nouvelle_ligne[k] = v

    # Ajout de la ligne
    df = pd.concat([df, pd.DataFrame([nouvelle_ligne])], ignore_index=True)

    # Écriture du CSV
    df.to_csv(csv_fichier, index=False, sep=sep, encoding=encoding)

'''
# --- Exemple d'utilisation ---
if __name__ == "__main__":
    d_r = {"GEN_r": 15, "test_r": 18, "VIDE_r": "valeur", "Ajout_r":"789654"}
    d_s = {"GEN_s": 15, "test_s": 18, "VIDE_s": "valeur", "Ajout_s":"789654"}
    # Modif dictionnaire pour ajouter "Recette." ou "Rapport." devant les clés
    d_r_modifie = {f"Recette.{k}": v for k, v in d_r.items()}
    d_s_modifie = {f"Rapport.{k}": v for k, v in d_s.items()}
    # Union des deux dictionnaires
    d = d_r_modifie | d_s_modifie
    # Appel de fonction
    dict_to_csv("datas.csv", d)
    
    # Plus tard, le dict gagne une nouvelle clé et en supprime d'autres:
    d2 = {"Recette.GEN_r": 21, "test": 17, "verif": "ok", "ajout": 45}
    dict_to_csv("datas.csv", d2)
'''