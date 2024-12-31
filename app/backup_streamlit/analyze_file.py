import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms import OpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.schema import SystemMessage, HumanMessage
from dotenv import load_dotenv, find_dotenv

# Cl√© OpenAI
load_dotenv(find_dotenv())
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# Titre
st.title('Assistant IA pour l\'analyse de donn√©es ü§ñ')

# Message de bienvenue
st.write("Bonjour, üëã Je suis votre assistant IA")

# Explication dans la barre lat√©rale
with st.sidebar:
    st.write('*Assistant d\'analyse de fichier.*')
    st.caption('''**Bienvenue dans votre assistant. Il a √©t√© con√ßu afin de vous aider √† analyser des fichiers de donn√©es et de r√©cup√©rer les informations pertinentes afin de les sauvegarder pour une utilisation ult√©rieure.**
    ''')

    st.divider()

    st.caption("<p style ='text-align:center'>'''**Powered by GPT-4**'''</p>", unsafe_allow_html=True)

# Initialiser la cl√© dans l'√©tat de session
if 'clicked' not in st.session_state:
    st.session_state.clicked = {1: False}

# Fonction pour mettre √† jour la valeur dans l'√©tat de session
def clicked(button):
    st.session_state.clicked[button] = True
st.button("Commen√ßons", on_click=clicked, args=[1])
if st.session_state.clicked[1]:
    user_csv = st.file_uploader("T√©l√©chargez votre fichier ici", type="csv")
    if user_csv is not None:
        user_csv.seek(0)
        df = pd.read_csv(user_csv, low_memory=False)

        # Mod√®le llm
        llm = OpenAI(temperature=0, max_tokens=250)

        # Fonction dans la barre lat√©rale
        @st.cache_data
        def steps_eda():
            steps_eda = llm.invoke('Quelles sont les √©tapes de l\'AED ( Analyse Exploratoire des Donn√©es )? Repondez de maniere clair et rapide')
            return steps_eda

        # Agent Pandas
        pandas_agent = create_pandas_dataframe_agent(llm, df, verbose=True, allow_dangerous_code=True)

        @st.cache_data
        def function_agent():
            st.write("**Aper√ßu des donn√©es**")
            st.write("Les premi√®res lignes de votre jeu de donn√©es ressemblent √† ceci :")
            st.write(df.head(5))  # Affichez seulement les 5 premi√®res lignes

            st.write("**Nettoyage des donn√©es**")
            columns_df = pandas_agent.invoke("Quelle est la signification des colonnes ? R√©pondez en Fran√ßais.")
            st.write(columns_df['output'])

            missing_values = pandas_agent.invoke("Combien de valeurs manquantes y a-t-il dans ce dataframe ? Commencez la r√©ponse par 'Il y a'. R√©pondez en Fran√ßais.")
            st.write(missing_values['output'])

            duplicates = pandas_agent.invoke("Y a-t-il des valeurs dupliqu√©es et si oui, o√π ? R√©pondez en Fran√ßais.")
            st.write(duplicates['output'])

            st.write("**R√©sum√© des donn√©es**")
            st.write(df.describe())

            # Calculer les corr√©lations en dehors de l'agent
            correlation_matrix = df.corr(numeric_only=True)
            st.write("**Analyse des corr√©lations**")
            st.write(correlation_matrix)

            # Identifier les valeurs aberrantes en dehors de l'agent
            outliers = identify_outliers(df)  # Impl√©mentez cette fonction selon vos besoins
            st.write("**Valeurs aberrantes**")
            st.write(outliers)

            new_features = pandas_agent.invoke("Quelles nouvelles fonctionnalit√©s seraient int√©ressantes √† cr√©er ? R√©pondez en Fran√ßais.")
            st.write(new_features['output'])

            return

        # Exemple de fonction pour identifier les valeurs aberrantes
        def identify_outliers(dataframe):
            # Impl√©mentez votre logique pour identifier les valeurs aberrantes
            return "Fonction d'identification des valeurs aberrantes √† impl√©menter"

        @st.cache_data
        def function_question_variable():
            st.line_chart(df, y=[user_question_variable])
            summary_statistics = pandas_agent.invoke(f"Donnez-moi un r√©sum√© des statistiques de {user_question_variable} Repondez en Fran√ßais")
            st.write(summary_statistics['output'])
            normality = pandas_agent.invoke(f"V√©rifiez la normalit√© ou les formes de distribution sp√©cifiques de {user_question_variable} Repondez en Fran√ßais")
            st.write(normality['output'])
            outliers = pandas_agent.invoke(f"√âvaluez la pr√©sence de valeurs aberrantes de {user_question_variable} Repondez en Fran√ßais")
            st.write(outliers['output'])
            trends = pandas_agent.invoke(f"Analysez les tendances, la saisonnalit√© et les motifs cycliques de {user_question_variable} Repondez en Fran√ßais")
            st.write(trends['output'])
            missing_values = pandas_agent.invoke(f"D√©terminez l'√©tendue des valeurs manquantes de {user_question_variable} Repondez en Fran√ßais")
            st.write(missing_values['output'])
            return
        
        @st.cache_data
        def function_question_dataframe():
            dataframe_info = pandas_agent.invoke(user_question_dataframe)
            st.write(dataframe_info['output'])
            return

        # Principal

        st.header('Analyse exploratoire des donn√©es')
        st.subheader('Informations g√©n√©rales sur le jeu de donn√©es')

        with st.sidebar:
            with st.expander('Quelles sont les √©tapes de l\'AED ( Analyse Exploratoire des Donn√©es )'):
                st.write(steps_eda())

        function_agent()

        st.subheader('Variable d\'√©tude')
        user_question_variable = st.text_input('Quelle variable vous int√©resse ?')
        if user_question_variable is not None and user_question_variable != "":
            function_question_variable()

            st.subheader('√âtude compl√©mentaire')

        if user_question_variable:
            user_question_dataframe = st.text_input("Y a-t-il autre chose que vous aimeriez savoir sur votre dataframe ? Repondez en Fran√ßais, de mani√®re claire et d√©taill√©e. En prenant le role d'un expert en analyse de donn√©es. vous donnerez des r√©ponses professionnelles et d√©taill√©es, ainsi que des projections sur les analyses futures.")
            if user_question_dataframe is not None and user_question_dataframe not in ("", "non", "Non"):
                function_question_dataframe()
            if user_question_dataframe in ("non", "Non"):
                st.write("")
