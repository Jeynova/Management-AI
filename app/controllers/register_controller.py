from flask import jsonify, request
import json
import os

def register():
    try:
        data = request.json
        participant = {
            "name": data.get("name"),
            "email": data.get("email"),
            "type": data.get("type", "general")
        }

        # Charger le fichier JSON
        file_path = os.path.join('data', 'participants.json')
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                json.dump({"participants": []}, file)

        with open(file_path, 'r') as file:
            participants_data = json.load(file)

        # Ajouter le participant
        participants_data["participants"].append(participant)

        # Sauvegarder les données
        with open(file_path, 'w') as file:
            json.dump(participants_data, file, indent=4)

        return jsonify({"message": "Participant enregistré avec succès.", "participant": participant})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
