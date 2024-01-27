# app.py
import os
import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
from mistral_api import get_response
import pandas as pd

def main():

    # variables
    os.environ[st.secrets['mistral']['key']] = st.secrets['mistral']['key']
    api_key = os.environ[st.secrets['mistral']['key']]
    model = "mistral-tiny"

<<<<<<< HEAD
    # Load the Google Sheet into a dataframe.
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_cars = conn.read(worksheet="Sheet1", ttl="10m", usecols=[0,1,2,3,4])
    df_cars = df_cars.dropna(axis='index', how='all')
    if 'df_cars' not in st.session_state:
        st.session_state.df_cars = df_cars
    # print(st.session_state.df_cars.shape)

    # Print results.
    # for row in df.itertuples():
    #     # st.write(row)
    #     st.write(f"{row.datum} um {row.uhrzeit} Uhr:  {row.bezeichnung}, {row.baujahr}")
    #     st.write(row.beschreibung)
    

    # dict_to_save = dict(datum=["01-01-2024", "02-01-2024"], uhrzeit=["14:00:00", "15:00:00"], bezeichnung=["Audi TT", "VW Tuareg"], baujahr=["2001", "2002"], beschreibung=["Das Auto ist sehr gut.", "Das Auto ist sehr schlecht."])
    # df_to_save = pd.DataFrame(dict_to_save)
    # print(df_to_save)
    # combined_df = pd.concat([df, df_to_save])
    # conn.update(worksheet="Sheet1", data=combined_df)


=======
>>>>>>> 3d66216 (fixed secrets)
    # Header
    st.image("autohalle-titelbild.png")
    st.title("Text-Generierung mittels KI")
    st.write((f"Mit diesem Tool lassen sich Texte generieren, die von einer KI geschrieben wurden "
              f"und in wenigen Sätzen ein bestimmtes Auto beschreiben."))
    st.markdown("<br>", unsafe_allow_html=True)


    # Sidebar
    sidebar = st.sidebar
    sidebar.header("Projekt von Marvin Wäcker")
    # Adding GitHub link to the sidebar
    st.sidebar.markdown("[GitHub](https://github.com/m-waeck)")
    st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/marvin-waecker/)")
    

    # Text input for user to enter text
    st.header("Beschreibungstext generieren")
    car_name = st.text_input("Autobezeichnung:", "Fiat Multipla")
    car_year = st.text_input("Baujahr:", "2001")
<<<<<<< HEAD
    # # Initialize a list to store the text history
    # if 'car_history' not in st.session_state:
    #     st.session_state.car_history = []
=======
    # Initialize a list to store the text history
    if 'car_history' not in st.session_state:
        st.session_state.car_history = []
>>>>>>> d231608 (descr functionality)
    # Display a button
    if st.button("Generieren"):
        # Action to perform when the button is clicked
        message = (f"Beschreibe das Auto {car_name} aus dem Jahr {car_year} in einem kurzen Fließtext auf Deutsch."
                   f"Der Text sollte positiv klingen und die Vorteile des Autos hervorheben."
                   f"Erwähne nicht das Baujahr.")
<<<<<<< HEAD
<<<<<<< HEAD
        car_descr = get_response(message, False, api_key, model)
        # st.session_state.car_history.insert(0, [car_name, car_year, car_descr])
        # Create a Series representing a new row
        date = datetime.now().strftime('%d-%m-%Y')
        time = datetime.now().strftime('%H:%M:%S')
        new_car = pd.Series([date, time, car_name, car_year, car_descr], index=st.session_state.df_cars.columns)
        # Concatenate the DataFrame and the Series to add the new row
        st.session_state.df_cars = pd.concat([st.session_state.df_cars, new_car.to_frame().transpose()], ignore_index=True)
=======
        car_descr = get_response(message, True, api_key, model)
        st.session_state.car_history.insert(0, [car_name, car_year, car_descr])
>>>>>>> 3d66216 (fixed secrets)
=======
        car_descr = get_response(message, True)
        st.session_state.car_history.insert(0, [car_name, car_year, car_descr])

    # Display the text history
    if st.session_state.car_history:
        st.header("Generierte Beschreibungen")
        for car in st.session_state.car_history:
            st.subheader(car[0] + ", Baujahr: " + car[1])
            st.write(car[2])
>>>>>>> d231608 (descr functionality)

    
    # Display the text history
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("Generierte Beschreibungen")
    # df_cars_rev = st.session_state.df_cars.iloc[::-1]
    for _, car in (st.session_state.df_cars.iloc[::-1]).iloc[:5].iterrows():
        sh = f"{car['bezeichnung']}, Baujahr: {remove_decimal(car['baujahr'])}"
        st.subheader(sh)
        st.write(f"{car['datum']} | {car['uhrzeit']} Uhr")
        st.write(car["beschreibung"])
        if not st.session_state.df_cars.empty:
            conn.update(worksheet="Sheet1", data=st.session_state.df_cars)


def remove_decimal(value):
    # Convert to string
    str_value = str(value)

    # Remove decimal part
    if '.' in str_value:
        str_value = str_value.split('.')[0]

    # Convert back to the original type (either str or float)
    return str_value

if __name__ == "__main__":
    main()



