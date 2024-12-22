from flask import Blueprint, request, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import openai
from dotenv import load_dotenv
import os
import ast

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

data_bp = Blueprint('data_bp', __name__)

@data_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file and file.filename.endswith('.csv'):
        df = pd.read_csv(file)
        return jsonify({'message': 'File uploaded successfully', 'data': df.to_dict()})
    return jsonify({'error': 'Invalid file format'})

@data_bp.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")
    data = request.json.get("data")
    df = pd.DataFrame(data)

    # Appeler ChatGPT pour générer une réponse ou du code
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": (
                "Vous êtes un expert en analyse de données (data analyst expert) formé pour fournir des réponses professionnelles et détaillées. "
                "Si un graphique est nécessaire et / ou demandé, Tu simuleras la création d'un graphique et ne retournera comme réponse que le code python permettant de generer ce graphique.TU NE DOIS PAS ET JAMAIS FOURNIR AUTRE CHOSE QUE LE CODE. Nous n attendons pas de contexte pour le code dans ce cas. Uniquement du code.Tu ne mettras pas non plus les imports. Sans aucune phrase,titre,commentaire ou autre. Uniquement le code de façon à être immediatement traité via notre application. "
                "Sinon, fournissez une analyse textuelle Claire et detaillée, visant un haut professionallisme et un resultat digne d'un expert du domaine. Cette analyse doit être la plus précise possible donnat des details concrets et pertinents. Elle devra prendre en compte les données fournies et les informations contextuelles. Et être le plus detaillée possible."
            )},
            {"role": "user", "content": f"Voici les données: {df.head().to_json()}. {user_message}."}
        ]
    )

    # Récupérer la réponse de ChatGPT
    gpt_response = response.choices[0].message.content.strip()

    # Vérifier si la réponse est un code Python
    if gpt_response.startswith("plt.") or "sns." in gpt_response:
        try:
            # Exécuter le code Python fourni
            exec_env = {"df": df, "plt": plt, "sns": sns, "io": io}

            # Exécuter le code dans un environnement sécurisé
            exec(gpt_response, exec_env)

            # Sauvegarder le graphique généré
            img = io.BytesIO()
            exec_env["plt"].savefig(img, format="png")
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            exec_env["plt"].close()

            return jsonify({"response": "Graphique généré avec succès.", "plot_url": f"data:image/png;base64,{plot_url}"})

        except Exception as e:
            return jsonify({"response": f"Erreur lors de l'exécution du code Python : {str(e)}"})
    else:
        # Si la réponse n'est pas du code, retourner la réponse textuelle
        return jsonify({"response": gpt_response})
    
@data_bp.route('/execute_code', methods=['POST'])
def execute_code():
    code = request.json.get("code")

    # Valider le code Python
    valid, error_message = is_valid_python_code(code)
    if not valid:
        return jsonify({"error": f"Code Python invalide : {error_message}"})

    try:
        # Définir un environnement d'exécution isolé
        exec_env = {"plt": plt, "sns": sns, "pd": pd, "io": io}
        exec(code, exec_env)

        # Sauvegarder le graphique généré
        img = io.BytesIO()
        exec_env["plt"].savefig(img, format="png")
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        exec_env["plt"].close()

        return jsonify({"plot_url": f"data:image/png;base64,{plot_url}"})

    except Exception as e:
        return jsonify({"error": f"Erreur lors de l'exécution du code Python : {str(e)}"})

def is_valid_python_code(code):
    """
    Vérifie si le code est un script Python valide.
    """
    try:
        ast.parse(code)  # Tente d'analyser le code avec le module ast
        return True
    except SyntaxError:
        return False
        
    """ gpt_response = response.choices[0].message.content.strip()
    
    # Example of handling a specific command for generating a correlation heatmap
    if "correlation heatmap" in user_message.lower():
        plt.figure(figsize=(10, 8))
        sns.heatmap(df.corr(), annot=True, cmap='coolwarm')
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        return jsonify({'response': gpt_response, 'plot_url': plot_url})
    
    return jsonify({'response': gpt_response}) """
