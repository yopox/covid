from openpyxl import load_workbook
from datetime import date
import glob
import re
import unidecode
import json
global rapport

# Liste des fichiers .xlsx
fichiers = [x for x in glob.glob("**/*.xlsm", recursive=False) if "~" not in x]
sortie = []
rapport = ""

def log(texte):
    global rapport
    rapport += texte
    print(texte)

if len(fichiers) > 1:
    log(f"• {len(fichiers)} fiches trouvées.\n")
else:
    log(f"• {len(fichiers)} fiche trouvée.\n")

log("• Erreurs d'analyse :\n")

for nomFichier in fichiers:

    pb = "Chargement du fichier"
    entrees = {}
    try:
        entrees["nom-fichier"] = nomFichier

        # Chargement du .xlsm
        classeur = load_workbook(filename = nomFichier)
        fa = classeur['Fiche Administrative']
        fm = classeur['Fiche Médicale']

        pb = "Date de la consultation"
        if fa['C3'].value is not None:
            entrees["date-consultation"] = fa['C3'].value.strftime("%d/%m/%y")

        pb = "Nom"
        if fa['C5'].value is not None and fa['C6'].value is not None:
            entrees["nom"] = fa['C6'].value + " " + fa['C5'].value
        
        pb = "Heure de la consultation"
        if fa['C4'].value is not None:
            if type(fa['C4'].value) is date:
                entrees["heure-consultation"] = fa['C4'].value.strftime("%H:%M")
            elif type(fa['C4'].value) is str:
                entrees["heure-consultation"] = fa['C4'].value

        pb = "Calcul de l'âge"
        naissance = fa['C7'].value
        if naissance is not None:
            auj = date.today() 
            entrees["age"] = auj.year - naissance.year - ((auj.month, auj.day) < (naissance.month, naissance.day))

        pb = "Genre"
        genre = fm['I4'].value
        if genre is not None:
            entrees["femme"] = 'f' in genre or 'F' in genre

        pb = "Code Postal"
        if fa['C10'].value is not None:
            code = re.search(r"([0-9]{5})", fa['C10'].value)
            if code is not None:
                entrees["code-postal"] = re.search(r"([0-9]{5})", fa['C10'].value).group(1)

        pb = "Médecin traitant"
        if fa['C15'].value is not None:
            entrees["medecin-traitant"] = unidecode.unidecode(str(fa['C15'].value))

        pb = "Adressé par"
        if fa['C16'].value is not None:
            entrees["adresse-par"] = unidecode.unidecode(str(fa['C16'].value)).capitalize()

        pb = "J1"
        if fm['E7'].value is not None:
            entrees["j1"] = fm['E7'].value.strftime("%d/%m/%y")

        pb = "Première consultation"
        if fm['E7'].value is not None and fa['C3'].value is not None:
            delai = fa['C3'].value.toordinal() - fm['E7'].value.toordinal() + 1
            if delai < 10:
                entrees["j-consultation"] = f"J0{delai}"
            else:
                entrees["j-consultation"] = f"J{delai}"

        pb = "Nom infirmier"
        if fm['H2'].value is not None:
            entrees["nom-infirmier"] = unidecode.unidecode(str(fm['H2'].value))

        pb = "Nom medecin"
        if fm['K2'].value is not None:
            entrees["nom-medecin"] = unidecode.unidecode(str(fm['K2'].value))

        pb = "Suivi"
        entrees["suivi"] = {
            "autosurveillance": fm["C52"].value,
            "test-covid": fm["F52"].value,
            "test-negatif" : fm["F49"].value,
            "test-positif" : fm["F50"].value,
            "hospitalisation" : fm["I52"].value
        }

        pb = "Autres"
        entrees["proche-fragile"] = fm['O39'].value
        entrees["piece-confinement"] = fm['O40'].value

        pb = "Diagnostic"
        if fm["O30"].value:
            entrees["diagnostic"] = "Peu Probable"
        elif fm["O31"].value:
            entrees["diagnostic"] = "Suspect"
        elif fm["R30"].value:
            entrees["diagnostic"] = "Tres Probable"
        elif fm["R31"].value:
            entrees["diagnostic"] = "COVID confirme par test"
        else:
            entrees["diagnostic"] = "Manquant"

        pb = "Critères de gravité"
        entrees["criteres-de-gravite"] = {
            "polypnee": fm['O3'].value,
            "sat": fm['O4'].value,
            "pas": fm['O5'].value,
            "deshydration": fm['O6'].value,
            "signes-neurologiques": fm['O7'].value,
            "aeg-brutale": fm['O8'].value
        }

        pb = "Paramètres vitaux"
        entrees["parametres-vitaux"] = {
            "sat": fm['G12'].value,
            "frequence-respiratoire": fm['G13'].value,
            "temperature": fm['G14'].value,
            "pas": fm['G15'].value,
            "frequence-cardiaque": fm['G16'].value
        }

        pb = "Paramètres cliniques"
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
        entrees["examen-clinique"] = fm['C29'].value

        pb = "Facteurs de risque"
        entrees["facteurs-de-risque"] = {
            "age": entrees["age"] >= 70,
            "patho-respiratoire": fm['S4'].value,
            "insiffisance-cardiaque": fm['S5'].value,
            "atcd-cv": fm['S6'].value,
            "diabete": fm['S7'].value,
            "immunodepression": fm['S8'].value,
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

        sortie.append(entrees)

    except:
        log(f"\tFichier : {nomFichier}\n\tErreur : {pb}\n")


log("• Erreurs de format de case (il ne faut pas que le format soit une date) :\n")

interdit = "<class 'datetime.datetime'>"
aSuppr = []
i = -1
for entrees in sortie:
    i += 1
    for cle in entrees:
        if str(type(entrees[cle])) == interdit:
            log(f"\tFichier : {entrees['nom-fichier']}\n\tErreur : {cle}\n")
    
            if i not in aSuppr:
                aSuppr.append(i)
        if type(entrees[cle]) is dict:
            for sousCle in entrees[cle]:
                if str(type(entrees[cle][sousCle])) == interdit:
                    log(f"\tFichier : {entrees['nom-fichier']}\n\tErreur : {cle}\n")
            
                    if i not in aSuppr:
                        aSuppr.append(i)

while len(aSuppr) > 0:
    del sortie[aSuppr[-1]]
    del aSuppr[-1]

with open("log.txt", "w") as logFile:
    logFile.write(rapport)

with open("stats.js", "w") as output:
    output.write("var data = ")
    json.dump(sortie, output, indent=2, skipkeys=True)
    log(f"• Écriture de stats.js réussie ({len(sortie)} / {len(fichiers)} fiches traitées).")