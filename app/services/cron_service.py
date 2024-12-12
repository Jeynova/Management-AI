import sys
import os

# Ajouter le répertoire racine au chemin Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import logging
from datetime import datetime, timedelta
from app import create_app
from app.controllers.feedback_controller import analyze_feedbacks
from apscheduler.schedulers.blocking import BlockingScheduler
import requests
# Initialiser l'application Flask
app = create_app()

# Configurer le logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# URL de Pipedream
PIPEDREAM_URL = os.getenv("PIPEDREAM_URL")

def analyze_feedback_with_mail():
    with app.app_context():
        try:
            # Définir la plage de dates
            now = datetime.utcnow()
            start_time = now - timedelta(days=1)
            start_time = start_time.replace(hour=21, minute=0, second=0, microsecond=0)
            end_time = now.replace(hour=21, minute=0, second=0, microsecond=0)

            # Appeler la fonction d'analyse
            result = analyze_feedbacks(start_time, end_time)

            if "error" in result:
                raise Exception(result["error"])

            # Log des résultats
            logger.info(f"Résumé des feedbacks généré : {result['summary']}")
            logger.info(f"Total feedbacks : {result['total_feedbacks']}")
            logger.info(f"Ratio positif/négatif : {result['ratio']}")

            # Envoi de l'email via Pipedream
            if PIPEDREAM_URL:
                response = requests.post(PIPEDREAM_URL, json=result)
                if response.status_code == 200:
                    logger.info("Email envoyé avec succès via Pipedream.")
                else:
                    logger.error(f"Erreur lors de l'envoi de l'email via Pipedream : {response.text}")
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des feedbacks : {str(e)}")

# Configurer le cron
scheduler = BlockingScheduler()
scheduler.add_job(analyze_feedback_with_mail, "cron", hour=16, minute=26)

if __name__ == "__main__":
    try:
        logger.info("Service de cron démarré.")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Service de cron arrêté.")