# Image Python
FROM python:3.12-slim

# Dossier de travail dans le conteneur
WORKDIR /app

# Installation des bibliothèques
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du script de migration
COPY migration.py .

# Commande exécutée au démarrage
CMD ["python", "migration.py"]