# Projet 4 — DataSoluTech

## Présentation du projet

Ce projet est réalisé dans le cadre de ma formation Data Engineer.

L'objectif est de développer une solution permettant de migrer un dataset médical au format CSV vers une base de données NoSQL MongoDB.

La solution devra être automatisée, conteneurisée avec Docker et accompagnée d'une étude des possibilités de déploiement sur AWS.

## Technologies utilisées

- **Python / Pandas** : analyse, nettoyage et transformation des données.
- **MongoDB** : stockage des données au format documentaire.
- **PyMongo** : communication entre Python et MongoDB.
- **Docker** : conteneurisation de la solution (à venir).
- **Git / GitHub** : versionnement et documentation.

## Dataset

Le dataset initial contient 55 500 enregistrements et 15 colonnes.

Les principales opérations de préparation sont :

- Vérification des valeurs manquantes.
- Identification et suppression de 534 doublons exacts.
- Vérification et conversion des dates.
- Contrôle de cohérence des données numériques et catégorielles.

Après nettoyage, le dataset contient **54 966 enregistrements**.

## Modélisation MongoDB

Chaque document représente une hospitalisation et contient quatre sous-documents :

- `patient` : informations concernant le patient.
- `medical` : informations médicales.
- `hospitalisation` : informations administratives et dates.
- `facturation` : assurance et montant facturé.

Cette structure permet de regrouper logiquement les informations liées à une hospitalisation.

## Avancement du projet

- [x] Analyse et nettoyage du dataset
- [x] Définition du modèle documentaire
- [x] Migration initiale vers MongoDB
- [x] Contrôles d'intégrité
- [x] Création d'index
- [x] Tests CRUD
- [ ] Automatisation du script de migration
- [ ] Conteneurisation avec Docker
- [ ] Authentification et gestion des utilisateurs
- [ ] Étude des solutions AWS

## Confidentialité

Le fichier CSV contenant les données médicales est exclu du dépôt GitHub grâce au fichier `.gitignore`.

Les données individuelles ne sont pas publiées. Seuls les scripts, notebooks et rapports de contrôle anonymes sont versionnés.