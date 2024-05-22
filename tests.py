from openai_api import get_response
from app import create_message
import streamlit as st

car_model = "BMW 218i Cabrio"
car_year = "2021"
car_specials = "Keine"
API_KEY = st.secrets['openai']['key']
AI_MODEL =  "gpt-3.5-turbo" # "mistral-large-latest"


car_descr = get_response(create_message(car_model, car_year, car_specials), False, API_KEY, AI_MODEL)

# save to txt
with open(f"test.txt", "w") as f:
    f.write(car_descr)