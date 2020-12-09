import streamlit as st

import requests

api_url = 'https://projectspotify-76glfmoaxq-ew.a.run.app'

st.markdown('#Please input the song uri')

uri = st.text_input('Spotify URI', 'URI here please')
response = requests.get(f'{api_url}/predict_genre/{uri}')
prediction = response.json()
pred = prediction['prediction']

st.markdown(f'''###The genre is:
#{pred}''')