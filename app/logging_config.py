import logging

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/app.log"),  # Log dans un fichier
            logging.StreamHandler()  # Log dans la console
        ]
    )