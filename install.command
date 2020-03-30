# Présentation
echo "Bienvenue dans le script d'installation de covid-stats.\nCe script installera Homebrew et Python3 (cela peut prendre un peu de temps).\n\nSi votre mot de passe sera demandé, il n'y aura pas de retour visuel mais le clavier sera bien fonctionnel !\n\nAppuyez sur entrée pour continuer ou fermez la fenêtre pour annuler."

read continueScript
clear

# Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

# Python
brew install python@3.8

# Dependances
pip3 install openpyxl
pip3 install numpy
pip3 install matplotlib