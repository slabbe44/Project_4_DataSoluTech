# librairies
import os
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path
from pymongo import MongoClient

# fonctions
def create_doc(line):
    doc = {
        "patient": {
            "nom": line["Name"],
            "age": int(line["Age"]),
            "genre": line["Gender"],
            "groupe_sanguin": line["Blood Type"]
        },

        "medical": {
            "pathologie": line["Medical Condition"],
            "medicament": line["Medication"],
            "resultat_test": line["Test Results"]
        },

        "hospitalisation": {
            "date_admission": line["Date of Admission"].to_pydatetime(),
            "date_sortie": line["Discharge Date"].to_pydatetime(),
            "medecin": line["Doctor"],
            "hopital": line["Hospital"],
            "numero_chambre": int(line["Room Number"]),
            "type_admission": line["Admission Type"]
        },

        "facturation": {
            "assureur": line["Insurance Provider"],
            "montant": float(line["Billing Amount"])
        }
    }

    return doc

# ---------------

# Chargement du fichier CSV
csv_path = Path("data/healthcare_dataset.csv")
df = pd.read_csv(csv_path)

# Suppression des doublons
df_clean = df.drop_duplicates().copy()

# Conversion des dates
df_clean["Date of Admission"] = pd.to_datetime(df_clean["Date of Admission"])
df_clean["Discharge Date"] = pd.to_datetime(df_clean["Discharge Date"])

# Bilan du nettoyage
print("Lignes initiales :", len(df))
print("Doublons supprimés :", len(df) - len(df_clean))
print("Lignes à migrer :", len(df_clean))

# Transformation des lignes en documents MongoDB
docs = []

for index, ligne in df_clean.iterrows():
    docs.append(create_doc(ligne))

print("Documents créés :", len(docs))

# Connexion à MongoDB
# Chargement des identifiants
load_dotenv(".env")

# Connexion à MongoDB Docker
# Paramètres de connexion
load_dotenv(".env")

host = os.getenv("MONGO_HOST", "localhost")
port = int(os.getenv("MONGO_PORT", "27018"))

client = MongoClient(
    host=host,
    port=port,
    username=os.getenv("MONGO_ROOT_USER"),
    password=os.getenv("MONGO_ROOT_PASSWORD"),
    authSource="admin"
)

client.admin.command("ping")
print("Connexion MongoDB réussie !")

# Sélection de la base et de la collection
db = client["healthcare"]
collection = db["hospitalisations"]

# Vérification avant importation
nb_documents = collection.count_documents({})

if nb_documents == 0:
    collection.insert_many(docs)
    print("Importation terminée !")

elif nb_documents == len(docs):
    print("La collection contient déjà", nb_documents, "documents.")

else:
    print("Importation annulée : la collection contient déjà",
          nb_documents, "documents sur", len(docs), "attendus.")

# Vérification finale
print("Documents dans MongoDB :", collection.count_documents({}))

# Vérification de la migration
nb_ok = collection.count_documents({}) == len(df_clean)

structure_ok = all(
    set(doc.keys()) == {"patient", "medical", "hospitalisation", "facturation"}
    and len(doc["patient"]) == 4
    and len(doc["medical"]) == 3
    and len(doc["hospitalisation"]) == 6
    and len(doc["facturation"]) == 2
    for doc in collection.find({}, {"_id": 0})
)

print("\n=== Vérification de la migration ===")
print("Nombre de documents conforme :", nb_ok)
print("Structure des documents conforme :", structure_ok)

if nb_ok and structure_ok:
    print("Vérification réussie !")
else:
    raise ValueError("Échec de la vérification de la migration")

client.close()