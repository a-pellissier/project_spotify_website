import streamlit as st

import requests

api_url = 'https://projectspotify-76glfmoaxq-ew.a.run.app'

st.markdown('''
    # Please input the song uri''')

uri = st.text_input('Spotify URI')

if st.button('Make the magic happen'):
    # print is visible in server output, not in the page
    st.write('Querying the amazing API!')
    response = requests.get(f'{api_url}/predict_genre/{uri}')
    if response.status_code == 200:
        prediction = response.json()
        pred = prediction['prediction']
        st.markdown(f'''
        ### The genre is:
        # {pred}''')
    else:
        st.markdown('''## Spotify caused an error 😞''')
else:
    st.write('')
