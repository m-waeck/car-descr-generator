# app.py
import streamlit as st
from pymongo import MongoClient
from datetime import datetime


DB = "autohalle"
COLL = "cars"
CONN_STR = st.secrets["mongodb"]["mongoURI"]
DEFAULT_AI_MODEL = 0 # 0 = GPT, 1 = Mistral


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
    selected_button = st.sidebar.radio("Select Model", ("GPT", "Mistral"), index=DEFAULT_AI_MODEL)

    # Display content based on selected button
    if selected_button == "GPT":
        # st.sidebar.write("GPT is activated")
        from openai_api import get_response
        API_KEY = st.secrets['openai']['key']
        AI_MODEL = "gpt-3.5-turbo"
    else:
        # st.sidebar.write("Mistral is activated")
        from mistral_api import get_response
        API_KEY = st.secrets['mistral']['key']
        AI_MODEL = "mistral-large-latest" # "mistral-small"


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
        # print(API_KEY, AI_MODEL)
        WORD_COUNT = 12345
        while WORD_COUNT > 160:
            car_descr = get_response(create_message(car_model, car_year, car_specials), False, API_KEY, AI_MODEL)
            WORD_COUNT = len(car_descr.split())
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

    # Fetch and display items
    items = fetch_items()
    if items:
        st.header("Generierte Beschreibungen")
        for i, car in enumerate(reversed(items)):
            if i > 9: break
            sh = f"{car['model']}, Baujahr: {car['year']}"
            st.subheader(sh)
            st.write(f"{car['date']} | {car['time']} Uhr")
            st.write(car["descr"])
            if car["specials"]:
                st.write(f"Besonderheiten: {car['specials']}")
    else:
        st.warning("No items found in the MongoDB collection.")

if __name__ == "__main__":
    main()
