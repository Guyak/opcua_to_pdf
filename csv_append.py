from pathlib import Path
import pandas as pd
import time

def append_dict_to_csv(csv_path, values, sep=";", encoding="utf-8"):
    csv_file = Path(csv_path)
    date_str = time.strftime("%Y-%m-%d")
    time_str = time.strftime("%H-%M-%S")

    # Colonnes fixes en tête
    fixed_cols = ["Date", "Heure"]

    # Lecture du CSV s'il existe, sinon DataFrame vide
    if csv_file.exists():
        df = pd.read_csv(csv_file, sep=sep, encoding=encoding)
    else:
        df = pd.DataFrame(columns=fixed_cols)

    # Tri des colonnes existantes et des clés du dictionnaire par ordre alphabétique -> pour tri en cas d'ajout de nouvel item dans le dictionnaire
    existing_dynamic = [c for c in df.columns if c not in fixed_cols]
    new_dynamic = sorted(set(existing_dynamic).union(values.keys()), key=str.lower)
    # Ordre final des colonnes
    final_cols = fixed_cols + new_dynamic
    # Reindexage du DF pour garantir la présence des nouvelles colonnes (remplies avec NaN)
    df = df.reindex(columns=final_cols)

    # Nouvelle ligne
    new_row = {col: "" for col in final_cols}  # valeurs vides par défaut
    new_row["date"] = date_str
    new_row["heure"] = time_str

    # Remplissage avec les valeurs du dictionnaire (uniquement pour les colonnes connues)
    for k, v in values.items():
        if k in new_row:
            new_row[k] = v

    # Ajout de la ligne
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Écriture du CSV
    df.to_csv(csv_file, index=False, sep=sep, encoding=encoding)

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
    append_dict_to_csv("datas.csv", d)
    
    # Plus tard, le dict gagne une nouvelle clé et en supprime d'autres:
    d2 = {"Recette.GEN_r": 21, "test": 17, "verif": "ok", "ajout": 45}
    append_dict_to_csv("datas.csv", d2)
'''