# Étape 1 : utiliser une image officielle légère de Python
FROM python:3.13-slim

# Étape 2 : définir le répertoire de travail
WORKDIR /app

# Étape 3 : copier le fichier requirements.txt
COPY requirements.txt .

# Étape 4 : installer toutes les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Étape 5 : copier tout le code dans le conteneur
COPY . .

# Étape 6 : définir la variable d'environnement pour Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Étape 7 : exposer le port 5000 pour Render
EXPOSE 5000

# Étape 8 : commande pour lancer Flask avec Gunicorn (meilleure production)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]