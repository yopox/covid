from openpyxl import load_workbook
from datetime import date
import glob
import re
import unidecode
import json

print("Analyse des fichiers…")


# Liste des fichiers .xlsx
fichiers = [x for x in glob.glob("**/*.xlsm", recursive=False) if "~" not in x]
jours = []

if len(fichiers) > 1:
    print(f"{len(fichiers)} fiches trouvées.")
else:
    print(f"{len(fichiers)} fiche trouvée.")

for nomFichier in fichiers:

    entrees = {}
    try:
        # Chargement du .xlsm
        classeur = load_workbook(filename = nomFichier)
        fa = classeur['Fiche Administrative']
        fm = classeur['Fiche Médicale']

        # Date de la consultation
        if fa['C3'].value is not None:
            entrees["date-consultation"] = fa['C3'].value.strftime("%d/%m/%y")

        # Nom
        if fa['C5'].value is not None and fa['C6'].value is not None:
            entrees["nom"] = fa['C6'].value + " " + fa['C5'].value
        
        # Heure de la consultation
        if fa['C4'].value is not None:
            if type(fa['C4'].value) is date:
                entrees["heure-consultation"] = fa['C4'].value.strftime("%H:%M")
            elif type(fa['C4'].value) is str:
                entrees["heure-consultation"] = fa['C4'].value

        # Calcul de l'âge
        naissance = fa['C7'].value
        if naissance is not None:
            auj = date.today() 
            entrees["age"] = auj.year - naissance.year - ((auj.month, auj.day) < (naissance.month, naissance.day))

        # Genre
        genre = fm['I4'].value
        if genre is not None:
            entrees["femme"] = 'f' in genre or 'F' in genre

        # Code Postal
        if fa['C10'].value is not None:
            code = re.search(r"([0-9]{5})", fa['C10'].value)
            if code is not None:
                entrees["code-postal"] = re.search(r"([0-9]{5})", fa['C10'].value).group(1)

        # Médecin traitant
        if fa['C15'].value is not None:
            entrees["medecin-traitant"] = unidecode.unidecode(fa['C15'].value)

        # Adressé par
        if fa['C16'].value is not None:
            entrees["adresse-par"] = unidecode.unidecode(fa['C16'].value).capitalize()

        # J1
        if fm['E7'].value is not None:
            entrees["j1"] = fm['E7'].value.strftime("%d/%m/%y")

        # Première consultation
        if fm['E7'].value is not None and fa['C3'].value is not None:
            delai = fa['C3'].value.toordinal() - fm['E7'].value.toordinal() + 1
            if delai < 10:
                entrees["j-consultation"] = f"J0{delai}"
            else:
                entrees["j-consultation"] = f"J{delai}"

        # Nom infirmier
        if fm['H2'].value is not None:
            entrees["nom-infirmier"] = unidecode.unidecode(fm['H2'].value)

        # Nom medecin
        if fm['K2'].value is not None:
            entrees["nom-medecin"] = unidecode.unidecode(fm['K2'].value)

        # Suivi
        entrees["suivi"] = {
            "autosurveillance": fm["C52"].value,
            "test-covid": fm["F52"].value,
            "test-recu" : fm["F48"].value,
            "test-positif" : fm["F50"].value,
            "hospitalisation" : fm["I52"].value
        }

        # Autres
        entrees["proche-fragile"] = fm['O39'].value
        entrees["piece-confinement"] = fm['O40'].value

        # Diagnostic
        if fm["O30"]:
            entrees["diagnostic"] = "Peu Probable"
        elif fm["O31"]:
            entrees["diagnostic"] = "Suspect"
        elif fm["R30"]:
            entrees["diagnostic"] = "Très Probable"
        elif fm["R31"]:
            entrees["diagnostic"] = "COVID confirmé par test"
        else:
            entrees["diagnostic"] = "Manquant"

        # Critères de gravité
        entrees["criteres-de-gravite"] = {
            "polypnee": fm['O3'].value,
            "sat": fm['O4'].value,
            "pas": fm['O5'].value,
            "deshydration": fm['O6'].value,
            "signes-neurologiques": fm['O7'].value,
            "aeg-brutale": fm['O8'].value
        }

        # Paramètres vitaux
        entrees["parametres-vitaux"] = {
            "sat": fm['G12'].value,
            "frequence-respiratoire": fm['G13'].value,
            "temperature": fm['G14'].value,
            "pas": fm['G15'].value,
            "frequence-cardiaque": fm['G16'].value
        }

        # Paramètres cliniques
        entrees["parametres-cliniques"] = {
            "sensation": fm['G20'].value,
            "frissons": str(fm['G21'].value).count("+"),
            "toux": str(fm['G22'].value).capitalize(),
            "expectorations": str(fm['G23'].value).count("+"),
            "gene-respiratoire": str(fm['G24'].value).count("+"),
            "dyspnee-de-repos": str(fm['G25'].value).count("+"),
            "agueusie": str(fm['G26'].value).count("+"),
            "dysgueusie": str(fm['G27'].value).count("+")
        }

        # Facteurs de risque
        entrees["facteurs-de-risque"] = {
            "age": entrees["age"] >= 70,
            "patho-respiratoire": fm['S4'].value,
            "insiffisance-cardiaque": fm['S5'].value,
            "atcd-cv": fm['S6'].value,
            "diabete": fm['S7'].value,
            "immunodepressionn": fm['S8'].value,
            "imc": fm['S9'].value,
            "insuffisance-renale": fm['S10'].value,
            "grossesse": fm['S11'].value,
            "cirrhose": fm['S12'].value,
            "isolement": fm['X3'].value,
            "precarite": fm['X4'].value,
            "difficulte-linguistique": fm['X5'].value,
            "trouble-neuro": fm['X6'].value,
            "pas-moyen-communication": fm['X7'].value,
            "contact-covid": fm['O38'].value
        }

        jours.append(entrees)

    except:
        print(f"/!\ Erreur lors de la lecture de {nomFichier}. A été lu : {entrees}")

with open("stats.js", "w") as output:
    output.write("var data = ")
    json.dump(jours, output, indent=2, skipkeys=True)
    print(f"Écriture de stats.js réussie ({len(jours)} / {len(fichiers)} fiches traitées).")