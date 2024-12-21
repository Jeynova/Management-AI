from flask import jsonify, request
import openai
import os
from dotenv import load_dotenv

load_dotenv()

def generate():
    try:
        data = request.json
        prompt = data.get("prompt", "Dites-moi quelque chose d'intéressant !")
        
        # Appel à l'API OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Vous êtes un assistant utile pour organiser une conférence."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        
        # Récupérer la réponse générée
        generated_text = response.choices[0].message.content
        return jsonify({"response": generated_text.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
