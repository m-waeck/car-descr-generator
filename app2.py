# app2.py
import streamlit as st
from datetime import datetime
from mistral_api import get_response
from pymongo import MongoClient

DB = "autohalle"
COLL = "cars"

# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["mongodb"]["mongoURI"])

client = init_connection()

# Pull data from the collection.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=300)
def get_data():
    db = client[DB]
    coll = db[COLL]
    items = list(coll.find())  # make hashable for st.cache_data
    return items

def display_data(items):
    for car in items:
        print(type(car['year']))
        sh = f"{car['model']}, Baujahr: {car['year']}"
        st.subheader(sh)
        st.write(f"{car['date']} | {car['time']} Uhr")
        st.write(car["descr"])

def insert_data(data):
    db = client[DB]
    coll = db[COLL]
    result = coll.insert_one(data)
    return result

# Function to fetch and display data from MongoDB
def tests():
    # Replace <connection_string> with your actual connection string
    connection_string = st.secrets['mongodb']['mongoURI']
    try:
        client = MongoClient(connection_string)
        st.success("Connected to MongoDB Atlas successfully.")
    except Exception as e:
        st.error(f"Error connecting to MongoDB Atlas: {e}")

    if client:
        # Replace <dbname> and <collection_name> with your actual database and collection names
        db = client[DB]
        collection = db[COLL]

        # Fetch data from MongoDB
        data = list(collection.find())# {"_id" : "65b6f879ebfeecf83ac10d0a"})) 

        # List all databases
        database_names = client.list_database_names()

        if database_names:
            # Display the list of databases
            st.write("List of databases:")
            for db_name in database_names:
                st.write(db_name)

        # Display data in Streamlit
        if data:
            st.write("### MongoDB Data")
            st.write(data)
        else:
            st.warning("No data found in the MongoDB collection.")


def main():
    st.title("MongoDB Atlas and Streamlit Example")
    # tests()

    # get data from MongoDB
    items = get_data()
    if 'items' not in st.session_state:
        st.session_state.items = items

    # Text input for user to enter text
    st.header("Beschreibungstext generieren")
    car_model = st.text_input("Modelbezeichnung:", "Fiat Multipla")
    car_year = st.text_input("Baujahr:", "2001")

    # Display a button
    button_generate = st.button("Generieren")
    if button_generate:

        car_date = datetime.now().strftime('%d-%m-%Y')
        car_time = datetime.now().strftime('%H:%M:%S')
        car_descr = "Lorem Ipsum"
        # st.subheader(car_model)
        # st.write(car_year)
        # st.write(car_date)
        # st.write(car_time)
        # st.write(car_descr)
        # Document to be added to the collection
        new_document = {"date":car_date,
                        "time":car_time,
                        "model":car_model,
                        "year":int(car_year),
                        "specials":"None",
                        "descr":car_descr}

        # Add the document to the collection
        result = insert_data(new_document)
        # update items
        st.session_state.items = get_data()




    # items = get_data()
    display_data(st.session_state.items)


        


if __name__ == "__main__":
    main()