import json
import openai
import sys
import os
from dotenv import load_dotenv
load_dotenv()

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Now imports will work
from app import mysql, create_app

# Configuration de l'API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def load_mockup_data():
    app = create_app()

    # Charger les données du fichier JSON
    data_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/mockup.json'))
    with open(data_file, 'r', encoding='utf-8') as f:
        mock_feedbacks = json.load(f)

    with app.app_context():
        cursor = mysql.connection.cursor()
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

                # Insérer dans la base de données
                cursor.execute(
                    "INSERT INTO feedbacks (participant_name, participant_email, feedback_text, sentiment) "
                    "VALUES (%s, %s, %s, %s)",
                    (feedback['name'], feedback['email'], feedback['feedback'], sentiment)
                )
            except Exception as e:
                print(f"Erreur lors du traitement de {feedback['name']}: {e}")

        mysql.connection.commit()
        cursor.close()

if __name__ == "__main__":
    load_mockup_data()
