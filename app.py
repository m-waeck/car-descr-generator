# app.py
import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Import our new modules
from feature_extraction import extract_features, verify_features
from db_operations import fetch_items, add_new_document
from openai_api import get_json_response


DB = "autohalle"
COLL_TEXT = "cars"
COLL_FEAT = "features"
FEATURES_COLL = "features"
CONN_STR = st.secrets["mongodb"]["mongoURI"]
DEFAULT_AI_MODEL = 0 # 0 = ChatGPT, 1 = Mistral, 2 = DeepSeek
OPENAI_MODEL_EXTRACTION = "gpt-4o"  # Model for feature extraction

# Function to create message for AI
def create_message(car_model, car_year, car_specials):
    message = (f"Beschreibe das Auto {car_model} aus dem Jahr {car_year} in einem kurzen Fließtext auf Deutsch."
               f"Der Text soll maximal 8 Sätze enthalten."
               f"Der Text soll positiv klingen und die Vorteile des Autos hervorheben."
               f"Erwähne nicht das Baujahr."
               f"Verwende nicht immer die gleichen Formulierungen, aber achte auch darauf, dass der Text verständlich bleibt.")
    if car_specials:
        message += f"Beachte folgende Besonderheiten und gehe darauf ein: {car_specials}"
    return message

def main():
    # Sidebar
    sidebar = st.sidebar
    sidebar.header("Projekt von Marvin Wäcker")
    st.sidebar.markdown("[GitHub](https://github.com/m-waeck)")
    st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/marvin-waecker/)")

    selected_button = st.sidebar.radio("Sprachmodell auswählen", 
                                       ("ChatGPT", "Mistral", "DeepSeek"), 
                                       index=DEFAULT_AI_MODEL)

    # Display content based on selected button
    if selected_button == "ChatGPT":
        from openai_api import get_response
        API_KEY = st.secrets['openai']['key']
        AI_MODEL = "gpt-3.5-turbo"
        print("ChatGPT selected.")
    elif selected_button == "Mistral":
        from mistral_api import get_response
        API_KEY = st.secrets['mistral']['key']
        AI_MODEL = "mistral-large-latest"
        print("Mistral selected.")
    elif selected_button == "DeepSeek":
        from deepseek_api import get_response
        API_KEY = st.secrets['deepseek']['key']
        AI_MODEL = "deepseek-chat"
        print("DeepSeek selected.")
    else:
        st.error("Model nicht verfügbar. Bitte wähle ein anderes Model.")
        return

    # Header image
    st.image("autohalle-titelbild.png")

    # Add tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["Textgenerator", "Merkmalsextraktor", "Analyse"])
    
    ###############################################################################################
    # Text generation tab

    with tab1:
        st.title("Text-Generierung mittels KI")
        st.write((f"Mit diesem Tool lassen sich Texte generieren, die von einer KI geschrieben wurden "
                f"und in wenigen Sätzen ein bestimmtes Auto beschreiben."))
        # st.markdown("<br>", unsafe_allow_html=True)

        # Text input for user to enter text
        st.header("Beschreibungstext generieren")
        #TODO: Add Button to delete current text and start over
        car_model_textgen = st.text_input("Modelbezeichnung:", placeholder="z.B. Fiat Multipla", key="car_model_textgen")
        car_year_textgen = st.text_input("Baujahr:", placeholder="z.B. 2001", key="car_year_textgen")
        car_specials_textgen = st.text_input("Besonderheiten:", placeholder="Keine", key="car_specials_textgen")

        # Display button to add a new document
        gen_button = st.button("Generieren")

        # Add a new document when the button is pressed
        if gen_button:
            car_date = datetime.now().strftime('%d-%m-%Y')
            car_time = datetime.now().strftime('%H:%M:%S')
            WORD_COUNT = 12345
            print(f"Generating description using model {AI_MODEL} for {car_model_textgen} ({car_year_textgen})...")
            with st.spinner("Generiere Text..."):
                while WORD_COUNT > 160:
                    car_descr = get_response(create_message(car_model_textgen, 
                                                            car_year_textgen, 
                                                            car_specials_textgen), 
                                                False, API_KEY, AI_MODEL)
                    WORD_COUNT = len(car_descr.split())
            print(f"Text generated with {WORD_COUNT} words.")

            # Document to be added to the collection
            if car_specials_textgen == "Keine" or car_specials_textgen == "": 
                car_specials_textgen = None
            new_document = {"date":car_date,
                            "time":car_time,
                            "model":car_model_textgen,
                            "year":int(car_year_textgen),
                            "specials":car_specials_textgen,
                            "descr":car_descr,
                            "ai_model":AI_MODEL}
            add_new_document(CONN_STR, DB, COLL_TEXT, new_document)

        # Fetch and display items
        items_cars = fetch_items(CONN_STR, DB, COLL_TEXT)
        if items_cars:
            st.header("Generierte Beschreibungen")
            for i, car in enumerate(reversed(items_cars)):
                if i > 9: break
                ad_title = f"{car['model']}, Baujahr: {car['year']}"
                st.subheader(ad_title)
                st.write(f"{car['date']} | {car['time']} Uhr")
                st.write(car["descr"])
                if car["specials"]:
                    st.write(f"Besonderheiten: {car['specials']}")

        else:
            st.warning("No items found in the MongoDB collection.")
            print("No items found in the MongoDB collection.")
    


    ###############################################################################################
    # Feature extraction tab

    with tab2:
        st.title("Merkmal-Extraktion mittels KI")
        st.write(f"Mit diesem Tool lassen sich Fahrzeugmerkmale mithilfe von KI aus einem unformatierten Text extrahieren "
                 f"und alphabetisch kategorisieren.")
        # st.markdown("<br>", unsafe_allow_html=True)
        
        st.header("Fahrzeugmerkmale extrahieren")
        # Text input for car model
        car_model_featext = st.text_input("Modelbezeichnung:", placeholder="z.B.Fiat Multipla", key="car_model_featext")
        # Text area for pasting car specifications
        feature_text = st.text_area("Unformatierten Text mit Fahrzeugspezifikationen hier einfügen:",
                                    placeholder="z.B. Klimaautomatik, Panoramadach, Sportpaket, Airbag, 1,5l TDI ...",
                                    height=100)
        
        # Extract button
        extract_button = st.button("Extrahieren")
        
        if extract_button and feature_text:
            feat_date = datetime.now().strftime('%d-%m-%Y')
            feat_time = datetime.now().strftime('%H:%M:%S')
            # Extract features
            with st.spinner("Extrahiere Fahrzeugmerkmale..."):
                features = extract_features(feature_text, get_json_response, st.secrets['openai']['key'], OPENAI_MODEL_EXTRACTION)
            
            # Verify extraction
            is_complete, missing_features = verify_features(feature_text, features["all_features"])
            
            if not is_complete:
                st.warning(f"Einige Merkmale wurden möglicherweise nicht erkannt: {', '.join(missing_features)}")
            
            # Document to be added to the collection
            if features:
                new_document = {"date":feat_date,
                                "time":feat_time,
                                "model":car_model_featext,
                                "features":features["categorized_features"],
                                "all_features":features["all_features"],
                                "raw_text":feature_text,
                                "ai_model":AI_MODEL}
                add_new_document(CONN_STR, DB, COLL_FEAT, new_document)

        # Fetch and display items
        items_feats = fetch_items(CONN_STR, DB, COLL_FEAT)
        if items_feats:
            st.header("Extrahierte Fahrzeugmerkmale")
            for i, feats in enumerate(reversed(items_feats)):
                if i > 9: break
                st.subheader(f"{feats['model']}")
                st.write(f"{feats['date']} | {feats['time']} Uhr")
                #TODO: Add Copy Button
                # Display features in categories
                for category, features_list in feats['features'].items():
                    if features_list:
                        category_name = {
                            "motor_getriebe_fahrwerk_lenkung": "Motor & Getriebe & Fahrwerk & Lenkung",
                            "pakete": "Pakete",
                            "sicherheit": "Sicherheit",
                            "audio_kommunikation": "Audio & Kommunikation",
                            "komfort": "Komfort",
                            "interieur": "Interieur",
                            "exterieur": "Exterieur",
                            "weiteres": "Weiteres"
                        }.get(category, category)
                        
                        st.write(f"**{category_name}**")
                        for feature in sorted(features_list):
                            st.write(f"- {feature}")
                        st.write("")
        else:
            st.warning("No items found in the MongoDB collection.")
            print("No items found in the MongoDB collection.")



    ###############################################################################################
    # Analysis tab

    with tab3:
        st.title("Analyse der generierten Daten")
        st.write("Hier werden die bisher generierten Fahrzeugdaten aus der Datenbank analysiert und visualisiert.")

        # Fetch items from MongoDB
        items_cars = fetch_items(CONN_STR, DB, COLL_TEXT)
        
        if items_cars:
            df_cars = pd.DataFrame(items_cars)
            df_cars['date'] = pd.to_datetime(df_cars['date'], format='%d-%m-%Y')
            df_cars['time'] = pd.to_datetime(df_cars['time'], format='%H:%M:%S').dt.time
            
            # Display DataFrame
            st.subheader("Verteilung Baujahr")

            # Plot distribution of year
            plt.figure(figsize=(12, 6))
            # bars should have this color: #d52c24
            sns.countplot(data=df_cars, x='year', color='#d52c24')
            plt.xlabel('Baujahr', fontsize=14)
            plt.ylabel('Anzahl Fahrzeuge', fontsize=14)
            plt.xticks(fontsize=11)
            plt.yticks(fontsize=11)
            st.pyplot(plt)

            # Fahrzeuganzahl nach Monaten
            st.subheader("Fahrzeuganzahl nach Monaten")

            # Plot histogram of date binned by month (col: 'date' - datetime)
            # Group by month
            df_monthly = df_cars.groupby(df_cars['date'].dt.to_period('M')).size()

            # Convert PeriodIndex to datetime for plotting
            df_monthly.index = df_monthly.index.to_timestamp()

            # Plot
            plt.figure(figsize=(12,6))
            sns.lineplot(x=df_monthly.index, y=df_monthly.values, marker='o', color='#d52c24')
            plt.xlabel("Monat", fontsize=14)
            plt.ylabel("Anzahl Fahrzeuge", fontsize=14)
            plt.xticks(fontsize=11)
            plt.yticks(fontsize=11)
            plt.grid(True)
            st.pyplot(plt)

            # Fahrzeuganzahl nach Stunden
            st.subheader("Fahrzeuganzahl nach Stunden")

            # Extract hour
            df_cars['hour'] = pd.to_datetime(df_cars['time'], format='%H:%M:%S').dt.hour

            # Count samples per hour
            df_hourly = df_cars.groupby('hour').size()

            # Plot as bar chart
            plt.figure(figsize=(12,6))
            sns.barplot(x=df_hourly.index, y=df_hourly.values, color='#d52c24')
            plt.xlabel("Stunde des Tages", fontsize=14)
            plt.ylabel("Anzahl Fahrzeuge", fontsize=14)
            plt.xticks(fontsize=11)
            plt.yticks(fontsize=11)
            st.pyplot(plt)

        else:
            st.warning("No items found in the MongoDB collection.")
            print("No items found in the MongoDB collection.")



if __name__ == "__main__":
    main()
