from flask import Blueprint, request, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import openai
from dotenv import load_dotenv
import os

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
    user_message = request.json.get('message')
    data = request.json.get('data')
    df = pd.DataFrame(data)
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Vous êtes un expert en analyse de données ( data analyst expert ) formé pour ne donner que des reponses extremement professionelles et detaillées."},
            {"role": "user", "content": f"Voici les données: {df.head().to_json()}. {user_message}"}
        ]
    )
    
    gpt_response = response.choices[0].message.content.strip()
    
    # Example of handling a specific command for generating a correlation heatmap
    if "correlation heatmap" in user_message.lower():
        plt.figure(figsize=(10, 8))
        sns.heatmap(df.corr(), annot=True, cmap='coolwarm')
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        return jsonify({'response': gpt_response, 'plot_url': plot_url})
    
    return jsonify({'response': gpt_response})
