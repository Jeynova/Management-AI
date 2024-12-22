import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms import OpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.schema import SystemMessage, HumanMessage
from dotenv import load_dotenv, find_dotenv

# Clé OpenAI
load_dotenv(find_dotenv())
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# Titre
st.title('Assistant IA pour l\'analyse de données 🤖')

# Message de bienvenue
st.write("Bonjour, 👋 Je suis votre assistant IA")

# Explication dans la barre latérale
with st.sidebar:
    st.write('*Assistant d\'analyse de fichier.*')
    st.caption('''**Bienvenue dans votre assistant. Il a été conçu afin de vous aider à analyser des fichiers de données et de récupérer les informations pertinentes afin de les sauvegarder pour une utilisation ultérieure.**
    ''')

    st.divider()

    st.caption("<p style ='text-align:center'>'''**Powered by GPT-4**'''</p>", unsafe_allow_html=True)

# Initialiser la clé dans l'état de session
if 'clicked' not in st.session_state:
    st.session_state.clicked = {1: False}

# Fonction pour mettre à jour la valeur dans l'état de session
def clicked(button):
    st.session_state.clicked[button] = True
st.button("Commençons", on_click=clicked, args=[1])
if st.session_state.clicked[1]:
    user_csv = st.file_uploader("Téléchargez votre fichier ici", type="csv")
    if user_csv is not None:
        user_csv.seek(0)
        df = pd.read_csv(user_csv, low_memory=False)

        # Modèle llm
        llm = OpenAI(temperature=0, max_tokens=250)

        # Fonction dans la barre latérale
        @st.cache_data
        def steps_eda():
            steps_eda = llm.invoke('Quelles sont les étapes de l\'AED ( Analyse Exploratoire des Données )? Repondez de maniere clair et rapide')
            return steps_eda

        # Agent Pandas
        pandas_agent = create_pandas_dataframe_agent(llm, df, verbose=True, allow_dangerous_code=True)

        @st.cache_data
        def function_agent():
            st.write("**Aperçu des données**")
            st.write("Les premières lignes de votre jeu de données ressemblent à ceci :")
            st.write(df.head(5))  # Affichez seulement les 5 premières lignes

            st.write("**Nettoyage des données**")
            columns_df = pandas_agent.invoke("Quelle est la signification des colonnes ? Répondez en Français.")
            st.write(columns_df['output'])

            missing_values = pandas_agent.invoke("Combien de valeurs manquantes y a-t-il dans ce dataframe ? Commencez la réponse par 'Il y a'. Répondez en Français.")
            st.write(missing_values['output'])

            duplicates = pandas_agent.invoke("Y a-t-il des valeurs dupliquées et si oui, où ? Répondez en Français.")
            st.write(duplicates['output'])

            st.write("**Résumé des données**")
            st.write(df.describe())

            # Calculer les corrélations en dehors de l'agent
            correlation_matrix = df.corr(numeric_only=True)
            st.write("**Analyse des corrélations**")
            st.write(correlation_matrix)

            # Identifier les valeurs aberrantes en dehors de l'agent
            outliers = identify_outliers(df)  # Implémentez cette fonction selon vos besoins
            st.write("**Valeurs aberrantes**")
            st.write(outliers)

            new_features = pandas_agent.invoke("Quelles nouvelles fonctionnalités seraient intéressantes à créer ? Répondez en Français.")
            st.write(new_features['output'])

            return

        # Exemple de fonction pour identifier les valeurs aberrantes
        def identify_outliers(dataframe):
            # Implémentez votre logique pour identifier les valeurs aberrantes
            return "Fonction d'identification des valeurs aberrantes à implémenter"

        @st.cache_data
        def function_question_variable():
            st.line_chart(df, y=[user_question_variable])
            summary_statistics = pandas_agent.invoke(f"Donnez-moi un résumé des statistiques de {user_question_variable} Repondez en Français")
            st.write(summary_statistics['output'])
            normality = pandas_agent.invoke(f"Vérifiez la normalité ou les formes de distribution spécifiques de {user_question_variable} Repondez en Français")
            st.write(normality['output'])
            outliers = pandas_agent.invoke(f"Évaluez la présence de valeurs aberrantes de {user_question_variable} Repondez en Français")
            st.write(outliers['output'])
            trends = pandas_agent.invoke(f"Analysez les tendances, la saisonnalité et les motifs cycliques de {user_question_variable} Repondez en Français")
            st.write(trends['output'])
            missing_values = pandas_agent.invoke(f"Déterminez l'étendue des valeurs manquantes de {user_question_variable} Repondez en Français")
            st.write(missing_values['output'])
            return
        
        @st.cache_data
        def function_question_dataframe():
            dataframe_info = pandas_agent.invoke(user_question_dataframe)
            st.write(dataframe_info['output'])
            return

        # Principal

        st.header('Analyse exploratoire des données')
        st.subheader('Informations générales sur le jeu de données')

        with st.sidebar:
            with st.expander('Quelles sont les étapes de l\'AED ( Analyse Exploratoire des Données )'):
                st.write(steps_eda())

        function_agent()

        st.subheader('Variable d\'étude')
        user_question_variable = st.text_input('Quelle variable vous intéresse ?')
        if user_question_variable is not None and user_question_variable != "":
            function_question_variable()

            st.subheader('Étude complémentaire')

        if user_question_variable:
            user_question_dataframe = st.text_input("Y a-t-il autre chose que vous aimeriez savoir sur votre dataframe ? Repondez en Français, de manière claire et détaillée. En prenant le role d'un expert en analyse de données. vous donnerez des réponses professionnelles et détaillées, ainsi que des projections sur les analyses futures.")
            if user_question_dataframe is not None and user_question_dataframe not in ("", "non", "Non"):
                function_question_dataframe()
            if user_question_dataframe in ("non", "Non"):
                st.write("")
