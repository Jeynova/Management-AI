import pandas as pd
import openai
from dotenv import load_dotenv
import os
import json
import streamlit as st
import numpy as np

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# Charger le fichier JSON
with open('data/questions.json', 'r', encoding='utf-8') as file:
    question_bank = json.load(file)

def page_config():
    st.set_page_config(page_title="ChatGPT Data Assistant", page_icon="📊", layout="centered")
    hide_menu_style = "<style> footer {visibility: hidden;} </style>"
    st.markdown(hide_menu_style, unsafe_allow_html=True)

def sidebar():
    st.sidebar.title('À propos')
    st.sidebar.info('''
        Cette application utilise l'[API OpenAI](https://platform.openai.com/docs/overview) pour générer des réponses aux questions sur les fichiers de données.
        ''')
    st.sidebar.title('Guide')
    st.sidebar.info('''
        1. Téléchargez un fichier de données au format CSV.
        2. Sélectionnez une invite dans le menu déroulant.
        3. Cliquez sur le bouton "Générer une réponse".
        ''')
    st.text(" ")
    st.sidebar.markdown(
    """
    Powered by [OpenAI](https://platform.openai.com/docs/overview)
    """, unsafe_allow_html=True
    )

def open_ai_response(question: str, dataframe: pd.DataFrame) -> str:
    prompt = f'''{question}
    \n
    [dataframe]
    \n{dataframe}'''

    response = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "system",
            "content": (
                "Vous êtes un assistant expert en analyse de données. Posez les questions nécessaires pour définir "
                "l'objectif et le type d'analyse (Descriptive, Diagnostique, Prédictive, Prescriptive, ou autre). "
                "Adaptez votre analyse aux points clés spécifiés par l'utilisateur, en procédant étape par étape selon "
                "ses retours. Utilisez des méthodes statistiques appropriées, nettoyez les données, et fournissez des "
                "recommandations exploitables. Documentez chaque étape pour assurer transparence et clarté."
            )
        },
        {"role": "user", "content": prompt}
    ],
    max_tokens=1000
)

    answer = response.choices[0].message.content.strip()
    print(prompt)

    return answer

def run_app():
    st.title("Assistant d'analyse de données")
    upload_file = st.file_uploader("Téléchargez votre fichier de données", type=["csv", "xlsx", "xls"])
    example_data = st.checkbox("Utiliser des données d'exemple")

    prompt_selected = st.selectbox("Sélectionnez une question", list(question_bank.keys()))

    if st.button("Générer une réponse"):
        with st.spinner('Génération de la réponse...'):
            if upload_file is not None:
                if not example_data:
                    if upload_file.name.endswith('.csv'):
                        df = pd.read_csv(upload_file)
                    elif upload_file.name.endswith('.xlsx') or upload_file.name.endswith('.xls'):
                        df = pd.read_excel(upload_file)
                else:
                    df = pd.read_csv(upload_file)
                
                prompt = question_bank[prompt_selected]['question']
                answer = open_ai_response(prompt, df)
                st.markdown('### Résultat :')
                st.write(answer)
                print(answer)
                
                # Calculer le résumé statistique pour chaque colonne numérique
                """ numeric_cols = df.select_dtypes(include=[np.number])
                summary = numeric_cols.describe().transpose()
                medians = pd.Series(numeric_cols.median(), name='median')
                summary = summary.join(medians)
                
                st.markdown('### Résumé Statistique :')
                st.write(summary) """
            else:
                st.error('Veuillez télécharger un fichier de données')
                st.stop()
            return df

if __name__ == '__main__':
    page_config()
    run_app()
    sidebar()