# Utilise l'image officielle Python
FROM python:3.11

# Définit le répertoire de travail
WORKDIR /app

# Copie les fichiers nécessaires
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie le dossier de l'application
COPY ./app ./app

# Copie le fichier .env pour que python-dotenv puisse le charger
COPY .env .env

# Commande pour lancer l'application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
