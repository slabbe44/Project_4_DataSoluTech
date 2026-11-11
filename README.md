# Projet 4 — DataSoluTech

## Présentation du projet

Ce projet est réalisé dans le cadre de ma formation Data Engineer.

L'objectif est de développer une solution permettant de migrer un dataset médical au format CSV vers une base de données NoSQL MongoDB.

La solution devra être automatisée, conteneurisée avec Docker et accompagnée d'une étude des possibilités de déploiement sur AWS.

## Technologies utilisées

- **Python / Pandas** : analyse, nettoyage et transformation des données.
- **MongoDB** : stockage des données au format documentaire.
- **PyMongo** : communication entre Python et MongoDB.
- **Docker / Docker Compose** : conteneurisation et orchestration de MongoDB et du script Python de migration.
- **Git / GitHub** : versionnement et documentation.

## Organisation du projet

Les fichiers sont répartis par fonction afin de distinguer l'analyse, la migration, la configuration Docker et la documentation :

```text
Project_4/
├── P4_analyse_dataset_medical.ipynb      # Analyse et contrôles initiaux
├── P4_conteneurisation_docker.ipynb      # Déploiement Docker et sécurité
├── P4_rapport_analyse_et_schema.md       # Rapport et modèle documentaire
├── P4_etude_deploiement_AWS.ipynb        # Rapport et modèle documentaire
├── migration.py                          # Migration et contrôles automatiques
├── requirements.txt                      # Dépendances Python et versions
├── Dockerfile                            # Image du script Python
├── docker-compose.yml                    # Services MongoDB et migration
├── docker-compose.test.yml               # Environnement de test indépendant
├── docker/
│   └── init_users.js                     # Initialisation des utilisateurs
├── reports/
│   └── qualite_avant_migration.json      # Bilan qualité du CSV d'origine
├── .env.example                          # Modèle des paramètres (sans secrets)
├── .gitignore                            # Exclusions Git
├── .dockerignore                         # Exclusions de l'image Docker
├── README.md                             # Documentation du projet
└── data/
    └── healthcare_dataset.csv            # Données locales, non publiées
```

Le dossier `data/` et le fichier `.env` sont exclus de Git. Les données d'entrée et les mots de passe doivent être fournis localement.

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
- [x] Définition et test des index MongoDB
- [x] Automatisation de la création des index dans `migration.py`
- [x] Tests CRUD
- [x] Automatisation du script de migration
- [x] Conteneurisation avec Docker
- [x] Authentification et gestion des utilisateurs MongoDB
- [x] Étude des solutions AWS (./P4_etude_deploiement_AWS.ipynb)


## Schéma de la base MongoDB

### Organisation des données

Notre base de données `healthcare` contient une collection principale nommée `hospitalisations`.

Chaque document représente une hospitalisation et regroupe les informations dans quatre sous-documents :

- `patient` : informations personnelles du patient.
- `medical` : pathologie, traitement et résultats des examens.
- `hospitalisation` : informations relatives au séjour hospitalier.
- `facturation` : assurance et montant facturé.

Cette organisation permet de regrouper les informations associées à une hospitalisation dans un même document.

### Dictionnaire des champs MongoDB

| Sous-document | Champ | Type BSON |
|---|---|---|
| patient | nom | String |
| patient | age | Int32 |
| patient | genre | String |
| patient | groupe_sanguin | String |
| medical | pathologie | String |
| medical | medicament | String |
| medical | resultat_test | String |
| hospitalisation | date_admission | Date |
| hospitalisation | date_sortie | Date |
| hospitalisation | medecin | String |
| hospitalisation | hopital | String |
| hospitalisation | numero_chambre | Int32 |
| hospitalisation | type_admission | String |
| facturation | assureur | String |
| facturation | montant | Double |

Les types BSON correspondent aux conversions effectuées dans notre script Python `migration.py`.

MongoDB génère également automatiquement un identifiant unique `_id` pour chaque document.

### Index MongoDB

Trois index ont été définis pour optimiser les recherches :

| Champ indexé | Objectif |
|---|---|
| `medical.pathologie` | Rechercher les hospitalisations par pathologie |
| `hospitalisation.date_admission` | Rechercher les admissions par date |
| `hospitalisation.hopital` | Rechercher les hospitalisations par établissement |

Ces index peuvent améliorer les performances des requêtes utilisant ces champs. Ils ne sont pas uniques, car plusieurs hospitalisations peuvent partager une même pathologie, une même date ou un même hôpital.
**Le script `migration.py` crée automatiquement les trois index. »**

Pour vérifier leur présence :

```javascript
db.hospitalisations.getIndexes()
```

### Justification du modèle

Nous avons choisi une structure avec sous-documents plutôt qu'une structure plate, afin d'exploiter les possibilités d'imbrication offertes par MongoDB.

Cette organisation facilite la lecture, le regroupement logique des informations et l'évolution future du modèle.

Chaque document correspond à une hospitalisation et non à un patient unique, car le dataset source ne possède pas d'identifiant unique de patient.

Après nettoyage et migration, la collection contient **54 966 documents**.

## Fonctionnement du script `migration.py`

Le script réalise la migration depuis le fichier CSV jusqu'à la collection MongoDB `healthcare.hospitalisations` :

1. **Chargement :** `pandas.read_csv()` lit `data/healthcare_dataset.csv`.
2. **Nettoyage :** `drop_duplicates()` retire les 534 doublons exacts ; `to_datetime()` convertit les dates d'admission et de sortie.
3. **Transformation :** la fonction `create_doc()` transforme chaque ligne en document Python contenant les quatre sous-documents `patient`, `medical`, `hospitalisation` et `facturation`.
4. **Connexion :** PyMongo utilise les variables d'environnement pour joindre MongoDB. Depuis Docker, le nom d'hôte est `mongodb` et le port interne est `27017` ; depuis Windows, le port publié est `27018`.
5. **Importation :** si la collection est vide, `insert_many()` insère les documents. Si elle contient déjà 54 966 documents, le script ne les réinsère pas. Si le nombre est différent, il annule l'importation.
6. **Contrôles :** après l'opération, le script compare le nombre de documents attendus et vérifie la structure des quatre sous-documents et leurs 15 champs.
7. **Fermeture :** la connexion MongoDB est fermée après les vérifications.

Cette protection empêche les réinsertions simples, **mais elle ne constitue pas une synchronisation complète** : deux collections de même taille peuvent contenir des valeurs différentes. Les tests plus détaillés et les contrôles d'intégrité initiaux sont documentés dans les notebooks et dans `reports/`.

Le script utilise le compte `data_engineer` avec le rôle `readWrite`, et non le compte administrateur.

## Confidentialité

Le fichier CSV contenant les données médicales est exclu du dépôt GitHub grâce au fichier `.gitignore`.

Les données individuelles ne doivent pas être publiées. Les notebooks et rapports versionnés doivent être vérifiés avant chaque commit, notamment leurs sorties enregistrées, pour éviter de diffuser des informations personnelles.

## Installation et déploiement avec Docker

### Prérequis

Pour exécuter le projet, les outils suivants sont nécessaires :

- Git
- Docker Desktop avec Docker Compose

Python et MongoDB n'ont pas besoin d'être installés localement, car ils sont exécutés dans des conteneurs Docker.

### 1. Récupérer le projet

Cloner le dépôt GitHub :

```powershell
git clone https://github.com/slabbe44/Project_4_DataSoluTech.git
cd Project_4_DataSoluTech
```

### 2. Préparer les données

Créer un dossier `data` à la racine du projet et y placer le fichier `healthcare_dataset.csv`.

Ce fichier n'est pas présent sur GitHub afin de préserver la confidentialité des données médicales.

### 3. Configurer les variables d'environnement

Créer le fichier `.env` à partir du modèle :

```powershell
Copy-Item .env.example .env
```

Renseigner les mots de passe MongoDB dans ce fichier, avec un mot de passe différent par compte. Le modèle doit contenir les variables suivantes :

```dotenv
MONGO_ROOT_USER=admin
MONGO_ROOT_PASSWORD=CHANGE_ME
MONGO_MIGRATION_USER=data_engineer
MONGO_MIGRATION_PASSWORD=CHANGE_ME
MONGO_ANALYST_PASSWORD=CHANGE_ME
```

Remplacer chaque `CHANGE_ME` par un mot de passe personnel, sans utiliser ces valeurs d'exemple pour un vrai déploiement. Le fichier `.env` est exclu du dépôt GitHub, contrairement à `.env.example` qui ne contient aucun secret.

### 4. Démarrer MongoDB

Exécuter :

```powershell
docker compose up -d mongodb
```

Vérifier que le conteneur est opérationnel :

```powershell
docker compose ps
```

Le conteneur `datasolutech_mongodb` doit afficher le statut `healthy`.

### 5. Exécuter la migration

Lancer le script Python dans son conteneur Docker :

```powershell
docker compose run --rm --build migration
```

Cette commande permet de :

- Construire l'image Python à partir du Dockerfile.
- Installer les dépendances définies dans `requirements.txt`.
- Charger et nettoyer les données du CSV.
- Transformer les enregistrements en documents MongoDB.
- Importer les documents si la collection est vide.
- Vérifier le nombre et la structure des documents.

### 6. Vérifier les index

Après une première migration sur un volume MongoDB neuf, ouvrir le shell avec le compte administrateur :

```powershell
docker compose exec mongodb mongosh -u admin -p --authenticationDatabase admin
```

Saisir le mot de passe administrateur lorsqu'il est demandé, puis exécuter dans `mongosh` :

```javascript
use healthcare
db.hospitalisations.getIndexes()
exit
```

L'index `_id_` est créé automatiquement par MongoDB. Les trois autres index doivent figurer dans la liste.

### 7. Vérifier la migration

Le dataset initial contient 55 500 enregistrements.

Après suppression des 534 doublons exacts, **54 966 documents** doivent être présents dans la collection `hospitalisations`.

Le script vérifie automatiquement le nombre de documents et leur structure.

Si la collection contient déjà 54 966 documents, le script évite de les réimporter. Cette vérification du nombre ne garantit toutefois pas à elle seule que le contenu est identique.

### 8. Arrêter les conteneurs

Pour arrêter l'environnement :

```powershell
docker compose down
```

Les données MongoDB sont conservées dans le volume Docker `mongo_data`.

**Attention :** ne pas utiliser l'option `-v` si l'on souhaite conserver les données du volume.


## Authentification et gestion des utilisateurs

L'accès à MongoDB est sécurisé par un système d'authentification utilisant des comptes distincts selon les responsabilités des utilisateurs.

Nous avons mis en place trois profils :

| Utilisateur | Rôle MongoDB | Permissions |
|---|---|---|
| `admin` | `root` | Administration complète du serveur |
| `analyste` | `read` | Consultation des données |
| `data_engineer` | `readWrite` | Lecture, insertion, modification et suppression des documents |

### Principe du moindre privilège

Chaque utilisateur dispose uniquement des permissions nécessaires à sa fonction.

Le script `migration.py` utilise le compte `data_engineer` plutôt que le compte administrateur.

Les droits des comptes `analyste` et `data_engineer` sont limités à la base `healthcare`.

### Création automatique des utilisateurs

Les utilisateurs sont créés automatiquement lors de la première initialisation de MongoDB :

- Le compte administrateur est créé par les variables d'environnement de Docker Compose.
- Les comptes `analyste` et `data_engineer` sont créés par le script `docker/init_users.js`.

Les mots de passe sont définis dans le fichier `.env`, exclu de GitHub. Le script `init_users.js` n'est exécuté automatiquement que lors de la **première initialisation d'un volume MongoDB vide** : il ne modifie pas les comptes d'une base déjà initialisée.

### Validation des permissions

Nous avons testé les permissions des utilisateurs avec les opérations CRUD.

Nous avons également validé leur création automatique sur une nouvelle instance MongoDB indépendante de notre environnement principal.

Ces tests confirment que les comptes disposent des rôles attendus.