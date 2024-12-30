from flask import request, jsonify
import pandas as pd
import openai
import numpy as np

def analyze_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Aucun fichier trouvé."}), 400

        file = request.files['file']
        if not file.filename.endswith('.csv'):
            return jsonify({"error": "Le fichier doit être au format CSV."}), 400

        # Charger le fichier CSV
        df = pd.read_csv(file)
                # Effectuer une analyse de base
        summary = df.describe(include='all').transpose()
        summary = summary.fillna("null")  # Remplacer NaN par "null"
        summary = summary.replace({np.inf: "null", -np.inf: "null"})  # Gérer les infinis

        # Effectuer une analyse de base
        analysis = {
            "total_rows": len(df),
            "columns": list(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "summary": summary.to_dict()  # Convertir en dictionnaire JSON-friendly
        }

        return jsonify({"analysis": analysis})
    except Exception as e:
        return jsonify({"error": f"Erreur lors de l'analyse : {str(e)}"}), 500
    
def analyze_file_with_gpt():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Aucun fichier trouvé."}), 400

        file = request.files['file']
        if not file.filename.endswith('.csv'):
            return jsonify({"error": "Le fichier doit être au format CSV."}), 400

        # Charger le fichier CSV
        df = pd.read_csv(file)
        context = df.head().to_dict()

        # Construire un prompt
        prompt = f"""
        Voici un échantillon des données : {context}.
        Analyse les tendances principales et génère des recommandations.
        """

        analysis = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un générateur de feedbacks professionnels pour des conférences."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )

        raw_response = analysis.choices[0].message.content.strip()
        return jsonify({"gpt_analysis": raw_response})
    except Exception as e:
        return jsonify({"error": f"Erreur lors de l'analyse avec GPT : {str(e)}"}), 500