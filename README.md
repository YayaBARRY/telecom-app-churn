
# Application de Prédiction du Churn – Expresso Sénégal
Cette application Flask prédit le risque de désabonnement des clients de l'opérateur Expresso Sénégal à partir de données client. Elle est déployée sur Render avec intégration d'une base PostgreSQL pour stocker les prédictions effectuées en empechant les doublons d'enregistrement.


## Fonctionnalités
- Formulaire utilisateur avec saisie des données client 
- Prédiction avec un modèle Machine Learning (`KNN`) 
- Affichage du résultat de la prédiction avec probabilité
- Stockage de chaque prédiction dans une base PostgreSQL 
- Historique des prédictions par utilisateur 
- Authentification simple par identifiants 


## Technologies utilisées
- Python / Flask
- Scikit-learn, Joblib, Pandas
- SQLAlchemy & PostgreSQL (Render)
- Bootstrap 5 (pour le front-end)
- Déploiement via GitHub + Docker + Render


## Installation locale

### 1. Cloner le dépôt
```bash
git clone https://github.com/ton-utilisateur/nom-du-repo.git
cd nom-du-repo
```

### 2. Créer un environnement virtuel et installer les dépendances
```bash
python -m venv venv
venv\Scripts\activate  # (Windows)
# ou
source venv/bin/activate  # (Linux/Mac)

pip install -r requirements.txt
```

### 3. Lancer l'application localement
```bash
python app.py
```

> En local, l'application utilisera SQLite (`local.db`) si `DATABASE_URL` n'est pas défini.


## Déploiement sur Render

### 1. Ajouter les variables d’environnement
Dans Render, dans l’onglet **Environment** :
```
DATABASE_URL = postgresql://postgres:motdepasse@host:5432/churn_db
```

### 2. Déclencher un déploiement automatique via GitHub
Chaque `git push` déclenchera un nouveau déploiement.


## Structure des pages
- `/login` – page de connexion
- `/` – formulaire principal + prédiction
- `/historique` – affichage de toutes les prédictions passées


## Développé par
**Mamadou Yaya BARRY – 2025**  
Étudiant en Master 2 MIAGE à l'UGB, passionné de Data & d'IA.
