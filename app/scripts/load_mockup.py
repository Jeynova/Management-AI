import json
import openai
import os
from dotenv import load_dotenv

# Ajouter le chemin racine du projet
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app, db
from app.models import Feedback

# Charger les variables d'environnement
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def load_mockup_data():
    """Charge les données fictives dans la base de données."""
    # Charger les données du fichier JSON
    data_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/mockup.json'))
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            mock_feedbacks = json.load(f)
    except FileNotFoundError:
        print(f"Erreur : Le fichier mockup.json est introuvable dans {data_file}.")
        return

    app = create_app()
    with app.app_context():
        for feedback in mock_feedbacks:
            try:
                # Analyse du sentiment via GPT
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Vous êtes un assistant expert en analyse de sentiment."},
                        {"role": "user", "content": f"Déterminez le sentiment de ce retour : {feedback['feedback']}"}
                    ],
                    max_tokens=50
                )
                sentiment = response.choices[0].message.content.strip()

                # Ajouter le feedback à la base de données
                feedback_entry = Feedback(
                    participant_name=feedback['name'],
                    participant_email=feedback['email'],
                    feedback_text=feedback['feedback'],
                    sentiment=sentiment
                )
                db.session.add(feedback_entry)
            except Exception as e:
                print(f"Erreur lors du traitement de {feedback['name']}: {e}")

        # Valider les ajouts
        db.session.commit()
        print("Les données fictives ont été ajoutées avec succès !")


if __name__ == "__main__":
    load_mockup_data()