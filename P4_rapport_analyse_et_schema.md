# Projet 4 — Analyse préalable à la migration MongoDB

**Source :** `healthcare_dataset.csv` (SHA-256 : `d8c23c7dddaf0e1f5daf26182eb908c219d28a63bb574377c3ba6cb09be8a342`)  
**Méthode :** profilage pandas et contrôles non destructifs, 23 octobre 2026.

## Synthèse de la qualité

| Indicateur | Valeur |
|---|---:|
| Lignes | 55 500 |
| Colonnes | 15 |
| Taille | 8 399 221 octets |
| Valeurs nulles | 0 |
| Chaînes vides | 0 |
| Doublons exacts (15 champs) | 534 (0,96 %) |
| Enregistrements distincts (15 champs) | 54 966 |
| Dates invalides | 0 |
| Dates de sortie antérieures à l'admission | 0 |
| Durée d'hospitalisation min / max | 1 / 30 jours |
| Âges min / max | 13 / 89 ans |
| Montants négatifs | 108 (0,19 %) |
| Montant min / max (unités du fichier) | -2008,4921 / 52764,2767 |
| Identifiant patient explicite | Aucun |

**Interprétation.** Les 534 doublons ont une égalité exacte sur toutes les colonnes. Le dataset ne contient pas de clé d'événement stable permettant de prouver que deux lignes identiques sont deux hospitalisations distinctes ou une duplication accidentelle. Il convient donc de **ne pas les supprimer automatiquement**. Les 108 facturations négatives nécessitent une validation métier ; elles peuvent être des corrections ou des anomalies.

## Dictionnaire de données et types MongoDB proposés

| Champ CSV | Chemin MongoDB | Type BSON | Rôle / vigilance |
|---|---|---|---|
| `Name` | `patient.nom` | `String` | Identité déclarée ; non unique |
| `Age` | `patient.age` | `Int32` | Âge en années (13–89 observés) |
| `Gender` | `patient.genre` | `String` | Catégorie déclarée |
| `Blood Type` | `patient.groupe_sanguin` | `String` | Groupe sanguin |
| `Medical Condition` | `medical.pathologie` | `String` | Pathologie déclarée |
| `Date of Admission` | `hospitalisation.date_admission` | `Date` | Date ISO YYYY-MM-DD |
| `Doctor` | `hospitalisation.medecin` | `String` | Nom du médecin |
| `Hospital` | `hospitalisation.hopital` | `String` | Établissement |
| `Insurance Provider` | `facturation.assureur` | `String` | Organisme assureur |
| `Billing Amount` | `facturation.montant` | `Decimal128` | Montant monétaire ; 108 valeurs négatives |
| `Room Number` | `hospitalisation.numero_chambre` | `Int32` | Numéro de chambre |
| `Admission Type` | `hospitalisation.type_admission` | `String` | Elective, Urgent, Emergency |
| `Discharge Date` | `hospitalisation.date_sortie` | `Date` | Date de sortie ISO YYYY-MM-DD |
| `Medication` | `medical.medicament` | `String` | Médicament mentionné |
| `Test Results` | `medical.resultat_test` | `String` | Normal, Abnormal, Inconclusive |


### Modèle documentaire recommandé

**Une collection `hospitalisations`**, avec un document par ligne source et des sous-documents :

```javascript
{
  _id: "healthcare_dataset.csv:000001", // identifiant d'ingestion stable
  patient: {
    nom: "Patient fictif",
    age: 42,
    genre: "Female",
    groupe_sanguin: "O+"
  },
  hospitalisation: {
    date_admission: ISODate("2024-01-31T00:00:00Z"),
    date_sortie: ISODate("2024-02-02T00:00:00Z"),
    medecin: "Médecin fictif",
    hopital: "Hôpital fictif",
    numero_chambre: 328,
    type_admission: "Urgent"
  },
  medical: {
    pathologie: "Asthma",
    medicament: "Paracetamol",
    resultat_test: "Normal"
  },
  facturation: {
    assureur: "Aetna",
    montant: NumberDecimal("18856.281305978155")
  },
  provenance: {
    fichier: "healthcare_dataset.csv",
    numero_ligne: 2
  }
}
```

Les valeurs du document d'exemple sont **fictives** ; elles ne proviennent pas d'une personne du fichier. Le numéro de ligne dans l'identifiant technique permet un import reproductible et idempotent du **même fichier non modifié** (avec `upsert`) et n'identifie pas un patient de manière pérenne. Pour distinguer deux versions différentes du CSV, incorporer également une version ou l'empreinte du fichier dans la provenance et la stratégie d'identifiant.

### Index à envisager

```javascript
db.hospitalisations.createIndex({"hospitalisation.date_admission": 1});
db.hospitalisations.createIndex({"hospitalisation.hopital": 1, "hospitalisation.date_admission": -1});
db.hospitalisations.createIndex({"medical.pathologie": 1, "hospitalisation.date_admission": -1});
```

Ce sont des **candidats** : confirmer leur pertinence selon les requêtes réelles et `explain()`. Ne pas créer un index unique sur `patient.nom`.

### Plan de validation après migration

1. **Conservation :** si aucune transformation métier n'est appliquée, `countDocuments({}) == 55500` ; les doublons exacts doivent rester présents.
2. **Structure :** vérifier la présence et le type des champs imbriqués. Deux dates BSON, deux entiers et un montant `Decimal128` par document.
3. **Qualité :** recalculer valeurs manquantes, dates incohérentes, facturations négatives et doublons pour comparer à ce rapport.
4. **Reprise :** rejouer la migration du même fichier et confirmer que le décompte reste stable.
5. **CRUD :** effectuer create, read, update, delete dans une collection dédiée `tests_crud` puis nettoyer.
6. **Sécurité :** se connecter avec différents rôles utilisateurs et valider que les opérations non autorisées sont refusées.

### Sécurité et partage

Un dataset mêlant noms et informations médicales doit être manipulé comme **potentiellement sensible**. Vérifier la nature réelle ou synthétique du jeu de données et les obligations applicables, notamment RGPD en cas de données personnelles réelles. Ne publier sur GitHub **ni les lignes sources, ni les secrets d'authentification, ni des journaux nominatifs**. Utiliser `.gitignore`, `.env.example`, un compte applicatif à permissions minimales et restreindre l'accès réseau au serveur MongoDB.

### Points à arbitrer avant le script de migration

- Supprimer les 534 doublons ou les préserver ? **Par défaut, préserver.**
- Un montant négatif représente-t-il un avoir ou une erreur ? **Ne pas corriger sans consigne métier.**
- Arrondir les montants à deux décimales ? **Non sans consigne ; stocker la valeur d'origine avec `Decimal128`.**
- Créer une collection `patients` distincte ? **Pas encore : il manque un identifiant patient fiable.**
