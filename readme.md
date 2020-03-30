# Covid

Ce repo permet de générer des statistiques instantanées sur des fiches `.xlsx`.

# Utilisation

Télécharger le contenu de ce repo en [cliquant ici](https://github.com/yopox/covid/archive/master.zip), puis extraire le dossier `covid`.

## macOS

### Installation

Ouvrir le fichier `install.command`. Cette opération peut prendre quelques minutes.

### Utilisation

Ouvrir le fichier `stats.command`.

Le script python génère des stats sur tous les fichiers `.xlsx` placés dans le même dossier que lui ou dans des sous dossiers.

### Mise à jour

Ouvrir le fichier `update.command`.

## Linux

### Installation

Installez `python3` et les dépendances :

```
sudo apt install python3
pip3 install openpyxl
pip3 install numpy
pip3 install matplotlib
```

### Utilisation

```
python3 stats.py
```