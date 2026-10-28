// Sélection de la base de données
const database = db.getSiblingDB("healthcare");

// Récupération des mots de passe
const analystPassword = process.env.MONGO_ANALYST_PASSWORD;
const engineerPassword = process.env.MONGO_MIGRATION_PASSWORD;

// Vérification des mots de passe
if (!analystPassword || !engineerPassword) {
    throw new Error("Mots de passe MongoDB manquants");
}

// Création de l'utilisateur analyste
database.createUser({
    user: "analyste",
    pwd: analystPassword,
    roles: [
        { role: "read", db: "healthcare" }
    ]
});

// Création de l'utilisateur Data Engineer
database.createUser({
    user: "data_engineer",
    pwd: engineerPassword,
    roles: [
        { role: "readWrite", db: "healthcare" }
    ]
});

print("Utilisateurs MongoDB créés avec succès");