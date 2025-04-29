from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import pandas as pd
import joblib
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Automatisation de la création de la table
with app.app_context():
    Base.metadata.create_all(engine)

# Initialisation de Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(minutes=15)

# Identifiants utilisateur (simple authentification)
USER_CREDENTIALS = {"churn": "2025"}

# Chargement du modèle et scaler
model = joblib.load("knn_best_f1_model.joblib")
scaler = joblib.load("scaler.joblib")
threshold = joblib.load("knn_best_f1_threshold.joblib")

# Mapping des régions
region_mapping = {
    'DAKAR': 0, 'THIES': 1, 'SAINT-LOUIS': 2, 'LOUGA': 3, 'KAOLACK': 4,
    'DIOURBEL': 5, 'TAMBACOUNDA': 6, 'KOLDA': 7, 'KAFFRINE': 8, 'FATICK': 9,
    'MATAM': 10, 'ZIGUINCHOR': 11, 'SEDHIOU': 12, 'KEDOUGOU': 13
}

# Ordre des colonnes attendues par le modèle
ordered_columns = [
    'REGION', 'MONTANT', 'REVENUE', 'FREQUENCE',
    'DATA_VOLUME', 'ON_NET', 'ORANGE', 'REGULARITY',
    'TOP_PACK', 'FREQ_TOP_PACK'
]

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///local.db")
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Modèle de prédiction pour la base
class Prediction(Base):
    __tablename__ = 'predictions'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    region = Column(Integer)
    montant = Column(Float)
    revenue = Column(Float)
    frequence = Column(Float)
    data_volume = Column(Float)
    on_net = Column(Float)
    orange = Column(Float)
    regularity = Column(Float)
    top_pack = Column(Float)
    freq_top_pack = Column(Float)
    prediction_label = Column(Boolean)
    prediction_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

# Création de la table si elle n'existe pas
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db_session = Session()

# Politique cache pour forcer le rechargement
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Page principale de prédiction
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    prediction = None
    probability = None
    form_data = {}

    if request.method == 'POST':
        try:
            form_data = {col: float(request.form[col]) for col in ordered_columns}
            form_data["REGION"] = int(request.form["REGION"])

            input_df = pd.DataFrame([[form_data[col] for col in ordered_columns]], columns=ordered_columns)
            input_scaled = scaler.transform(input_df)
            proba = model.predict_proba(input_scaled)[:, 1][0]
            prediction = int(proba >= threshold)
            probability = round(proba, 4)

            # Vérification de l'existence d'une prédiction similaire
            existing_pred = db_session.query(Prediction).filter_by(
                username=session['user'],
                region=form_data['REGION'],
                montant=form_data['MONTANT'],
                revenue=form_data['REVENUE'],
                frequence=form_data['FREQUENCE'],
                data_volume=form_data['DATA_VOLUME'],
                on_net=form_data['ON_NET'],
                orange=form_data['ORANGE'],
                regularity=form_data['REGULARITY'],
                top_pack=form_data['TOP_PACK'],
                freq_top_pack=form_data['FREQ_TOP_PACK'],
                prediction_label=prediction,
                prediction_score=probability
            ).first()

            if not existing_pred:
                new_pred = Prediction(
                    username=session['user'],
                    region=form_data['REGION'],
                    montant=form_data['MONTANT'],
                    revenue=form_data['REVENUE'],
                    frequence=form_data['FREQUENCE'],
                    data_volume=form_data['DATA_VOLUME'],
                    on_net=form_data['ON_NET'],
                    orange=form_data['ORANGE'],
                    regularity=form_data['REGULARITY'],
                    top_pack=form_data['TOP_PACK'],
                    freq_top_pack=form_data['FREQ_TOP_PACK'],
                    prediction_label=prediction,
                    prediction_score=probability
                )
                db_session.add(new_pred)
                db_session.commit()
            else:
                print("⚠️ Prédiction déjà existante, pas enregistrée.")

        except Exception as e:
            print("Erreur de traitement :", e)

    return render_template("index.html", prediction=prediction, probability=probability,
                           regions=region_mapping, form_data=form_data)

# Page de l'historique des prédictions
@app.route('/historique')
def historique():
    if 'user' not in session:
        return redirect(url_for('login'))
    preds = db_session.query(Prediction).filter_by(username=session['user']).order_by(Prediction.created_at.desc()).all()
    return render_template('historique.html', preds=preds, regions=region_mapping)

# Page de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    session.pop('user', None)
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            session.permanent = True
            session['user'] = username
            return redirect(url_for('index'))
        else:
            error = "Identifiants invalides"
    return render_template('login.html', error=error)

# Déconnexion
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# API pour prédiction
@app.route('/api/predict', methods=['POST'])
def api_predict():
    if 'user' not in session:
        return jsonify({"error": "Non autorisé"}), 403
    try:
        input_json = request.get_json()
        if not all(col in input_json for col in ordered_columns):
            return jsonify({"error": "Certaines colonnes sont manquantes"}), 400

        input_df = pd.DataFrame([[input_json[col] for col in ordered_columns]], columns=ordered_columns)
        input_scaled = scaler.transform(input_df)
        proba = model.predict_proba(input_scaled)[:, 1][0]
        prediction = int(proba >= threshold)

        return jsonify({
            "prediction": prediction,
            "probability": round(proba, 4)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Lancement de l'application
if __name__ == '__main__':
    app.run()
