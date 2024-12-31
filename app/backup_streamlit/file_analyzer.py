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
    st.set_page_config(page_title="ChatGPT Data Assistant", page_icon="üìä", layout="centered")
    hide_menu_style = "<style> footer {visibility: hidden;} </style>"
    st.markdown(hide_menu_style, unsafe_allow_html=True)

def sidebar():
    st.sidebar.title('√Ä propos')
    st.sidebar.info('''
        Cette application utilise l'[API OpenAI](https://platform.openai.com/docs/overview) pour g√©n√©rer des r√©ponses aux questions sur les fichiers de donn√©es.
        ''')
    st.sidebar.title('Guide')
    st.sidebar.info('''
        1. T√©l√©chargez un fichier de donn√©es au format CSV.
        2. S√©lectionnez une invite dans le menu d√©roulant.
        3. Cliquez sur le bouton "G√©n√©rer une r√©ponse".
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
                "Vous √™tes un assistant expert en analyse de donn√©es. Posez les questions n√©cessaires pour d√©finir "
                "l'objectif et le type d'analyse (Descriptive, Diagnostique, Pr√©dictive, Prescriptive, ou autre). "
                "Adaptez votre analyse aux points cl√©s sp√©cifi√©s par l'utilisateur, en proc√©dant √©tape par √©tape selon "
                "ses retours. Utilisez des m√©thodes statistiques appropri√©es, nettoyez les donn√©es, et fournissez des "
                "recommandations exploitables. Documentez chaque √©tape pour assurer transparence et clart√©."
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
    st.title("Assistant d'analyse de donn√©es")
    upload_file = st.file_uploader("T√©l√©chargez votre fichier de donn√©es", type=["csv", "xlsx", "xls"])
    example_data = st.checkbox("Utiliser des donn√©es d'exemple")

    prompt_selected = st.selectbox("S√©lectionnez une question", list(question_bank.keys()))

    if st.button("G√©n√©rer une r√©ponse"):
        with st.spinner('G√©n√©ration de la r√©ponse...'):
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
                st.markdown('### R√©sultat :')
                st.write(answer)
                print(answer)
                
                # Calculer le r√©sum√© statistique pour chaque colonne num√©rique
                """ numeric_cols = df.select_dtypes(include=[np.number])
                summary = numeric_cols.describe().transpose()
                medians = pd.Series(numeric_cols.median(), name='median')
                summary = summary.join(medians)
                
                st.markdown('### R√©sum√© Statistique :')
                st.write(summary) """
            else:
                st.error('Veuillez t√©l√©charger un fichier de donn√©es')
                st.stop()
            return df

if __name__ == '__main__':
    page_config()
    run_app()
    sidebar()