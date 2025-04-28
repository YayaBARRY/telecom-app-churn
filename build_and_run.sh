#!/bin/

# Active l'environnement virtuel
venv\Scripts\activate

# Construction de l'image Docker
docker build -t telecom-churn-app .

# Suppression du conteneur précédent s'il existe
docker rm -f telecom-churn-app-container || true

# Lancement du conteneur en mode interactif
docker run -d -p 5000:5000 --name telecom-churn-app-container telecom-churn-app

echo "✅ Application démarrée : http://localhost:5000"