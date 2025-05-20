# from openai_api import get_response
# from mistral_api import get_response
from deepseek_api import get_response
from app import create_message
import streamlit as st

API_KEY = st.secrets['deepseek']['key'] # st.secrets['deepseek']['key']
AI_MODEL =  "deepseek-chat" # "gpt-3.5-turbo", "mistral-large-latest", "deepseek-chat"

car_model = "BMW 218i Cabrio"
car_year = "2021"
car_specials = "Keine"

car_descr = get_response(create_message(car_model, car_year, car_specials), False, API_KEY, AI_MODEL)

# save to txt
with open(f"test.txt", "w") as f:
    f.write(car_descr)