# Master TNAH - Atelier "Python pour les données de la recherche en histoire" - Reconnaissance et liage d'entités nommées

Bienvenue sur le dépôt du matériel, code et instructions, pour  réaliser la seconde séquence de l'atelier "Python pour les données de la recherche en histoire" du master Technologies numériques appliquées à l'histoire à l'École Nationale des Chartes.

Cette troisième séquence est dédiée à l'expérimentation de deux tâches classiques du traitement automatique du langage naturel en SHS :

1. la reconnaissance d'entités nommées
2.le liage d'entités nommées  

Elle est composée de deux parties :

1. Une expérimentation de la reconnaissance d'entités nommées et l'entraînement d'un modèle spécialisé pour la presse ancienne, avec SpaCy
2. La mise en place d'une chaîne de traitement de liage avec DBPedia

Les deux séances s'appuient sur des données historiques réelles : les textes annotés de **la presse française aux XIX-XXe siècles**, [produites par la BnF](https://api.bnf.fr/fr/texte-de-presse-annote-en-entites-nommees) dans le projet de recherche [Europeana Newspaper](http://www.europeana-newspapers.eu/) et diffusées sous license ouverte sur le portail de données de la BnF : [https://api.bnf.fr/fr/texte-de-presse-annote-en-entites-nommees](https://api.bnf.fr/fr/texte-de-presse-annote-en-entites-nommees)

Dernière mise à jour : **Mars 2025**.

## Mise en place 🏗️

1. Télécharger le dépôt avec Git

```bash
git clone git@github.com:HueyNemud/enc-tnah-atelierspython-nlp.git
```

2. Vérifier que Python 3.10 ou supérieur est utilisé

```bash
python --version
```

3. Au besoin, créez un nouvel environnement virtuel Python

```bash
python -m venv ~/python_atelierstnah
source ~/python_atelierstnah/bin/activate
```
