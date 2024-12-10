from flask import jsonify, request
import json
import os
import openai


# Récupérer toutes les FAQs ou interroger GPT si nécessaire
def faq():
    try:
        file_path = os.path.join('data', 'faq.json')
        data = request.json if request.method == 'POST' else None
        question = data.get("question", "").strip() if data else None

        if request.method == 'GET':
            # Charger toutes les FAQs
            with open(file_path, 'r') as file:
                faq_data = json.load(file)
            return jsonify(faq_data)

        if request.method == 'POST':
            if not question:
                return jsonify({"error": "Une question est requise."}), 400

            # Charger les FAQs
            with open(file_path, 'r') as file:
                faq_data = json.load(file)

            # Rechercher une réponse existante dans les FAQs
            for item in faq_data["questions"]:
                if question.lower() == item["question"].lower():
                    # Utiliser GPT pour enrichir la réponse existante
                    openai.api_key = os.getenv("OPENAI_API_KEY")
                    response = openai.chat_completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "Vous êtes un assistant spécialisé dans les conférences technologiques."},
                            {"role": "user", "content": f"Enrichissez la réponse suivante : {item['answer']}"}
                        ],
                        max_tokens=150
                    )
                    enriched_answer = response.choices[0].message.content.strip()
                    return jsonify({
                        "question": question,
                        "answer": item["answer"],
                        "enriched_answer": enriched_answer
                    })

            # Si la question n'existe pas, interroger GPT
            response = openai.chat_completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Vous êtes un assistant spécialisé dans les conférences technologiques."},
                    {"role": "user", "content": question}
                ],
                max_tokens=150
            )
            answer = response.choices[0].message.content.strip()
            return jsonify({"question": question, "answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Ajouter une FAQ
def add_faq():
    try:
        data = request.json
        question = data.get("question", "").strip()
        answer = data.get("answer", "").strip()

        if not question or not answer:
            return jsonify({"error": "La question et la réponse sont obligatoires."}), 400

        # Charger le fichier JSON
        file_path = os.path.join('data', 'faq.json')
        with open(file_path, 'r') as file:
            faq_data = json.load(file)

        # Ajouter la nouvelle FAQ
        faq_data["questions"].append({"question": question, "answer": answer})

        # Sauvegarder les modifications
        with open(file_path, 'w') as file:
            json.dump(faq_data, file, indent=4)

        return jsonify({"message": "FAQ ajoutée avec succès.", "question": question, "answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Supprimer une FAQ
def delete_faq():
    try:
        data = request.json
        question = data.get("question", "").strip()

        if not question:
            return jsonify({"error": "La question à supprimer est obligatoire."}), 400

        # Charger le fichier JSON
        file_path = os.path.join('data', 'faq.json')
        with open(file_path, 'r') as file:
            faq_data = json.load(file)

        # Filtrer les FAQs pour supprimer celle qui correspond
        original_count = len(faq_data["questions"])
        faq_data["questions"] = [item for item in faq_data["questions"] if item["question"].lower() != question.lower()]

        if len(faq_data["questions"]) == original_count:
            return jsonify({"error": "La question spécifiée n'a pas été trouvée."}), 404

        # Sauvegarder les modifications
        with open(file_path, 'w') as file:
            json.dump(faq_data, file, indent=4)

        return jsonify({"message": "FAQ supprimée avec succès.", "question": question})
    except Exception as e:
        return jsonify({"error": str(e)}), 500