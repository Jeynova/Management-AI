from flask import jsonify, request, render_template
import openai
import os

def render_feedback_form():
    return render_template('feedback_form.html')

def submit_feedback():
    from app import mysql
    try:
        data = request.json
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        feedback_text = data.get("feedback", "").strip()

        if not name or not feedback_text:
            return jsonify({"error": "Le nom et le retour sont obligatoires."}), 400

        # Analyse du sentiment avec GPT
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Vous êtes un assistant expert en analyse de sentiment."},
                {"role": "user", "content": f"Déterminez le sentiment de ce retour : {feedback_text}"}
            ],
            max_tokens=50
        )
        sentiment = response.choices[0].message.content.strip()

        # Enregistrer dans MySQL
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO feedbacks (participant_name, participant_email, feedback_text, sentiment) "
            "VALUES (%s, %s, %s, %s)",
            (name, email, feedback_text, sentiment)
        )
        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Feedback enregistré avec succès.", "sentiment": sentiment})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def analyze_feedbacks():
    from app import mysql
    try:
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM feedbacks ORDER BY created_at DESC")
        feedbacks = cursor.fetchall()
        cursor.close()

        # Récupérer les textes pour analyse
        feedback_texts = " ".join([fb['feedback_text'] for fb in feedbacks])

        # Générer un résumé avec GPT
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Vous êtes un assistant spécialisé en analyse de feedback."},
                {"role": "user", "content": f"Générez un résumé des points clés des retours suivants : {feedback_texts}"}
            ],
            max_tokens=300
        )
        summary = response.choices[0].message.content.strip()

        return jsonify({"feedbacks": feedbacks, "summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500