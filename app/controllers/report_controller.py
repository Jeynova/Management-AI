from flask import jsonify
import json
import os
from dotenv import load_dotenv

load_dotenv()

def report():
    try:
        file_path = os.path.join('data', 'participants.json')
        if not os.path.exists(file_path):
            return jsonify({"message": "Aucun participant trouvé."})

        with open(file_path, 'r') as file:
            participants_data = json.load(file)

        total_participants = len(participants_data["participants"])
        return jsonify({"total_participants": total_participants, "details": participants_data["participants"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
