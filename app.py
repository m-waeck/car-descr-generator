# app.py
import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import textwrap as tw
import json
from bson.objectid import ObjectId

# Import our new modules
from feature_extraction import extract_features, verify_features
from db_operations import connect_to_mongodb, save_features, get_features_by_car_id


DB = "autohalle"
COLL = "cars"
FEATURES_COLL = "features"
CONN_STR = st.secrets["mongodb"]["mongoURI"]
DEFAULT_AI_MODEL = 0 # 0 = ChatGPT, 1 = Mistral, 2 = DeepSeek


# Function to connect to MongoDB Atlas
def connect_to_mongodb():
    # Replace <connection_string> with your actual connection string
    try:
        client = MongoClient(CONN_STR)
        # st.success("Connected to MongoDB Atlas successfully.")
        return client
    except Exception as e:
        st.error(f"Error connecting to MongoDB Atlas: {e}")
        return None

# Function to fetch items from MongoDB
def fetch_items():
    client = connect_to_mongodb()

    if client:
        # Replace <dbname> and <collection_name> with your actual database and collection names
        db = client[DB]
        collection = db[COLL]

        # Fetch items from MongoDB
        items = list(collection.find())

        return items

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

# Function to add a new document to MongoDB
def add_new_document(doc):
    client = connect_to_mongodb()

    if client:
        # Replace <dbname> and <collection_name> with your actual database and collection names
        db = client[DB]
        collection = db[COLL]

        # Add a new document
        collection.insert_one(doc)

def main():
    # Sidebar
    sidebar = st.sidebar
    sidebar.header("Projekt von Marvin Wäcker")
    st.sidebar.markdown("[GitHub](https://github.com/m-waeck)")
    st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/marvin-waecker/)")
    
    # Add tabs for different functionalities
    tab1, tab2 = st.tabs(["Text Generation", "Feature Extraction"])
    
    with tab1:
        # Text generation tab
        selected_button = st.radio("Sprachmodell auswählen",
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


        # Header
        st.image("autohalle-titelbild.png")
        st.title("Text-Generierung mittels KI")
        st.write((f"Mit diesem Tool lassen sich Texte generieren, die von einer KI geschrieben wurden "
                f"und in wenigen Sätzen ein bestimmtes Auto beschreiben."))
        st.markdown("<br>", unsafe_allow_html=True)

        # Text input for user to enter text
        st.header("Beschreibungstext generieren")
        car_model = st.text_input("Modelbezeichnung:", "Fiat Multipla")
        car_year = st.text_input("Baujahr:", "2001")
        car_specials = st.text_input("Besonderheiten:", "Keine")

        # Display button to add a new document
        gen_button = st.button("Generieren")

        # Add a new document when the button is pressed
        if gen_button:
            car_date = datetime.now().strftime('%d-%m-%Y')
            car_time = datetime.now().strftime('%H:%M:%S')
            WORD_COUNT = 12345
            print(f"Generating description using model {AI_MODEL} for {car_model} ({car_year})...")
            while WORD_COUNT > 160:
                car_descr = get_response(create_message(car_model, car_year, car_specials), False, API_KEY, AI_MODEL)
                WORD_COUNT = len(car_descr.split())
            print(f"Text generated with {WORD_COUNT} words.")

            # Document to be added to the collection
            if car_specials == "Keine": car_specials = None
            new_document = {"date":car_date,
                            "time":car_time,
                            "model":car_model,
                            "year":int(car_year),
                            "specials":car_specials,
                            "descr":car_descr,
                            "ai_model":AI_MODEL}
            add_new_document(new_document)
    
    with tab2:
        # Feature extraction tab
        st.image("autohalle-titelbild.png")
        st.title("Feature-Extraktion mittels KI")
        st.write("Mit diesem Tool lassen sich Fahrzeugmerkmale aus einem Text extrahieren und kategorisieren.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # LLM selection for feature extraction
        feature_extraction_model = st.radio("Sprachmodell für Feature-Extraktion auswählen:",
                                          ("ChatGPT", "Mistral", "DeepSeek"),
                                          index=DEFAULT_AI_MODEL)
        
        # Get API key and model based on selection
        if feature_extraction_model == "ChatGPT":
            from openai_api import get_response as extract_response
            EXTRACT_API_KEY = st.secrets['openai']['key']
            EXTRACT_AI_MODEL = "gpt-3.5-turbo"
        elif feature_extraction_model == "Mistral":
            from mistral_api import get_response as extract_response
            EXTRACT_API_KEY = st.secrets['mistral']['key']
            EXTRACT_AI_MODEL = "mistral-large-latest"
        elif feature_extraction_model == "DeepSeek":
            from deepseek_api import get_response as extract_response
            EXTRACT_API_KEY = st.secrets['deepseek']['key']
            EXTRACT_AI_MODEL = "deepseek-chat"
        else:
            st.error("Model nicht verfügbar. Bitte wähle ein anderes Model.")
            return
        
        # Text area for pasting car specifications
        st.header("Fahrzeugmerkmale extrahieren")
        feature_text = st.text_area("Fahrzeugspezifikationen hier einfügen:", height=200)
        
        # Extract button
        extract_button = st.button("Merkmale extrahieren")
        
        if extract_button and feature_text:
            # Extract features
            with st.spinner("Extrahiere Fahrzeugmerkmale..."):
                features = extract_features(feature_text, extract_response, EXTRACT_API_KEY, EXTRACT_AI_MODEL)
            
            # Verify extraction
            is_complete, missing_features = verify_features(feature_text, features["all_features"])
            
            if not is_complete:
                st.warning(f"Einige Merkmale wurden möglicherweise nicht erkannt: {', '.join(missing_features)}")
            
            # Display categorized features
            st.subheader("Extrahierte Fahrzeugmerkmale")
            
            # Store features in session state for later use
            st.session_state.extracted_features = features
            st.session_state.raw_text = feature_text
            
            # Display features in categories
            for category, features_list in features["categorized_features"].items():
                if features_list:
                    category_name = {
                        "technical_specs": "Technische Spezifikationen",
                        "performance": "Leistung",
                        "comfort": "Komfort",
                        "safety": "Sicherheit"
                    }.get(category, category)
                    
                    st.write(f"**{category_name}**")
                    for feature in sorted(features_list):
                        st.write(f"- {feature}")
                    st.write("")
            
            # Car model and year inputs for saving
            st.subheader("Speichern")
            car_model_extract = st.text_input("Modelbezeichnung:", "")
            car_year_extract = st.text_input("Baujahr:", "")
            
            # Save button
            save_button = st.button("Extrahierte Merkmale speichern")
            
            if save_button:
                if not car_model_extract or not car_year_extract:
                    st.error("Bitte geben Sie Modelbezeichnung und Baujahr ein, um die Merkmale zu speichern.")
                else:
                    # Create a car document
                    car_doc = {
                        "date": datetime.now().strftime('%d-%m-%Y'),
                        "time": datetime.now().strftime('%H:%M:%S'),
                        "model": car_model_extract,
                        "year": car_year_extract,
                        "specials": None,
                        "descr": "",
                        "ai_model": "None"
                    }
                    
                    # Add car to database
                    client = connect_to_mongodb(CONN_STR)
                    if client:
                        db = client[DB]
                        collection = db[COLL]
                        car_result = collection.insert_one(car_doc)
                        car_id = car_result.inserted_id
                        
                        # Save features
                        features_id = save_features(
                            CONN_STR,
                            car_id,
                            feature_text,
                            features["categorized_features"],
                            features["all_features"],
                            EXTRACT_AI_MODEL
                        )
                        
                        st.success("Fahrzeugmerkmale erfolgreich gespeichert!")


    # Fetch and display items (outside of tabs)
    items = fetch_items()
    if items:
        st.header("Generierte Beschreibungen")
        for i, car in enumerate(reversed(items)):
            if i > 9: break
            ad_title = f"{car['model']}, Baujahr: {car['year']}"
            st.subheader(ad_title)
            st.write(f"{car['date']} | {car['time']} Uhr")
            
            # Display description if it exists
            if "descr" in car and car["descr"]:
                st.write(car["descr"])
            
            if car.get("specials"):
                st.write(f"Besonderheiten: {car['specials']}")
            
            # Check if this car has extracted features
            if "features_id" in car:
                features = get_features_by_car_id(CONN_STR, car["_id"])
                if features:
                    with st.expander("Extrahierte Fahrzeugmerkmale anzeigen"):
                        for category, features_list in features["categorized_features"].items():
                            if features_list:
                                category_name = {
                                    "technical_specs": "Technische Spezifikationen",
                                    "performance": "Leistung",
                                    "comfort": "Komfort",
                                    "safety": "Sicherheit"
                                }.get(category, category)
                                
                                st.write(f"**{category_name}**")
                                for feature in sorted(features_list):
                                    st.write(f"- {feature}")
                                st.write("")
    else:
        st.warning("No items found in the MongoDB collection.")
        print("No items found in the MongoDB collection.")

if __name__ == "__main__":
    main()
