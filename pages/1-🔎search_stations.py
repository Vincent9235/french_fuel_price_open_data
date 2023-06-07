# Imports
import json
import streamlit as st
import folium 
import pandas as pd
from streamlit_folium import st_folium

# Import own functions
from load_functions import load_xml, load_json, call_api

# Page config
st.set_page_config(
    page_title='Search french fuel stations',
    page_icon='🔎',
    layout='wide',
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    })

# Side bar
with st.sidebar:
    st.header('Informations on author')
    st.markdown('**Vincent Laurens💻**')
    st.write('📈Data Scientist at Bouygues Construction IT | Data Management student🏫') 
    st.write("""<div style="width:100%;text-align:center;"><a href="https://www.linkedin.com/in/vincentlaurenspro" style="float:center"><img src="https://img.shields.io/badge/Vincent%20Laurens-0077B5?style=for-the-badge&logo=linkedin&logoColor=white&link=https://www.linkedin.com/in/vincentlaurenspro/%22" width="100%" height="50%"></img></a></div>""", unsafe_allow_html=True)

# Load data
# I dont use url here because the original file is false
sign_file = 'data/stations.json'

# Load data sign
# I dont use url here because the original file is false
sign_file = 'data/stations.json'
# Ouvrir JSON file
with open(sign_file, 'r') as file:
    data = file.read()
# Remove extra white space
data = data.replace('\n', '')
# Add commas between JSON objects
data = data.replace('}{', '},{')
# Wrap JSON objects in a list
data = f"[{data}]"
# Load JSON data into a dataframe
data_sign = pd.read_json(data)

# Load data from Open Data API	
api_url = "https://data.economie.gouv.fr/api/records/1.0/search/?dataset=prix-des-carburants-en-france-flux-instantane-v2&q=&rows=10000&facet=carburants_disponibles&facet=carburants_indisponibles&facet=horaires_automate_24_24&facet=services_service&facet=departement&facet=region&facet=id&facet=Adresse"
response_data = call_api(api_url)

# Create a dataframe from response_data
df_response = pd.DataFrame(response_data['records'])
df_id = df_response['fields'].apply(lambda x: x['id'])
df_id.rename('id', inplace=True)

# Join on ID 
df_merged = pd.merge(data_sign, df_id, left_on='id', right_on='id', how='inner')

# Page beginning 
st.title('Find the nearest fuel stations from your home🔎')
st.subheader('Search your favorite fuel station⛽')
st.info('If you didnt find your city in the selectbox, this means that there is no station in your town. I will update this after.')

# List of stations in the searched city
stations_ville_recherchee = []
# API city list
villes = set()

# Browse records
for enregistrement in response_data['records']:
    fields = enregistrement.get("fields")
    ville = fields.get("ville")

    if ville:
        villes.add(ville)

# Convert set to sorted list
villes = sorted(list(villes))

city = st.selectbox('Select your city🏙️', villes)

# List of stations in the city you are looking for
stations_ville_recherchee = [enregistrement for enregistrement in response_data['records'] if enregistrement.get("fields") and enregistrement.get("fields").get("ville") == city]

# Check if any stations have been found in the searched city
if len(stations_ville_recherchee) > 0:
    # Display all data in a map from the selected city
    st.subheader('Map of all fuel stations in your city')
    # Retrieve the coordinates of the first station
    first_station = stations_ville_recherchee[0]
    latitude = first_station['geometry']['coordinates'][1]
    longitude = first_station['geometry']['coordinates'][0]
    # Create the map centered on the desired city
    m = folium.Map(location=[latitude, longitude], zoom_start=13)

    # Display information of stations found in a Folium map
    for station in stations_ville_recherchee:
        # Create the HTML content of the popup
        popup_content = f"<h4>{station['fields']['adresse'] + ' ' + station['fields']['cp'] + ' ' + station['fields']['ville']}</h4>"
        
        # If the station has the fuel_unavailable field
        if 'carburants_indisponibles' in station['fields']:
            popup_content += f"<p><strong>Carburants indisponibles :</strong> {station['fields']['carburants_indisponibles']}</p>"
        # Get fuel prices
        prix_carburants = station['fields'].get('prix')
        if prix_carburants:
            prix_carburants = json.loads(prix_carburants)
            if isinstance(prix_carburants, dict):
                # Si la valeur est un dictionnaire, cela signifie qu'il y a un seul carburant
                nom_carburant = prix_carburants.get('@nom')
                valeur_carburant = prix_carburants.get('@valeur')
                if nom_carburant and valeur_carburant:
                    popup_content += f"<p><strong>Prix {nom_carburant}:</strong> {valeur_carburant}</p>"
                else:
                    popup_content += f"<p><strong>Prix {nom_carburant}:</strong> None</p>"
            elif isinstance(prix_carburants, list):
                # If the value is a list, it means there are multiple fuels
                for carburant in prix_carburants:
                    nom_carburant = carburant.get('@nom')
                    valeur_carburant = carburant.get('@valeur')
                    if nom_carburant and valeur_carburant:
                        popup_content += f"<p><strong>Prix {nom_carburant}:</strong> {valeur_carburant}</p>"
                    else:
                        popup_content += f"<p><strong>Prix {nom_carburant}:</strong> None</p>"
        else:
            popup_content += "<p><strong>Prix:</strong> None</p>"

        # Add marker with popup to map
        folium.Marker(
            location=[station['geometry']['coordinates'][1], station['geometry']['coordinates'][0]],
            popup=folium.Popup(popup_content, max_width=250),
            icon=folium.Icon(color='green', icon='tint', prefix='fa')
        ).add_to(m)
        
    # Display the map in the Streamlit app
    st_folium(m, width=1250)
else : 
    st.error("No fuel station found in your city")