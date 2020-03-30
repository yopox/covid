from openpyxl import load_workbook
from datetime import date
import glob

# Liste des fichiers .xlsx
fichiers = [x for x in glob.glob("*.xlsx") if "~" not in x]
jours = {}

for nomFichier in fichiers:

    # Chargement du .xlsx
    classeur = load_workbook(filename = nomFichier)
    administrative = classeur['Fiche Administrative']
    medicale = classeur['Fiche Médicale']

    # Date de la consultation
    dateConsultation = administrative['C3'].value

    # Calcul de l'âge
    naissance = administrative['C7'].value
    auj = date.today() 
    age = auj.year - naissance.year - ((auj.month, auj.day) < (naissance.month, naissance.day))

    # Genre
    genre = medicale['G4'].value
    femme = 'f' in genre or 'F' in genre

    # Ajout des données 
    if not dateConsultation in jours:
        jours[dateConsultation] = []

    jours[dateConsultation].append({"age" : age, "femme" : femme})

for jour in jours:
    # Affichage du jour
    print(f"Statistiques du {jour.strftime('%d/%m/%Y')} :")

    patients = jours[jour]
    
    print(f"  • Nombre de personnes vues : {len(patients)}")

    # Age moyen
    ages = [x["age"] for x in patients]
    print("  • Âge moyen : {:.1f} ans".format(sum(ages) / len(ages)))

    # Genre
    genres = [x["femme"] for x in patients]
    f = sum(genres)
    m = len(genres) - f
    print(f"  • Genres : F ({f}, {round(f/len(genres)*100)}%) ; M ({m}, {round(m/len(genres)*100)}%)")
    print()