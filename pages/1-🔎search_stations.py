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

# Load data
villes_url = "https://www.data.gouv.fr/fr/datasets/r/521fe6f9-0f7f-4684-bb3f-7d3d88c581bb"
villes_filename = "data/cities.csv"
# I dont use url here because the original file is false
sign_file = 'data/stations.json'

# Load data sign
# Ouvrir le fichier JSON
with open(sign_file, 'r') as file:
    data = file.read()
# Supprimer les espaces blancs supplémentaires
data = data.replace('\n', '')
# Ajouter des virgules entre les objets JSON
data = data.replace('}{', '},{')
# Envelopper les objets JSON dans une liste
data = f"[{data}]"
# Charger les données JSON dans un dataframe
data_sign = pd.read_json(data)

# Load data from Open Data API	
api_url = "https://data.economie.gouv.fr/api/records/1.0/search/?dataset=prix-des-carburants-en-france-flux-instantane-v2&q=&rows=10000&facet=carburants_disponibles&facet=carburants_indisponibles&facet=horaires_automate_24_24&facet=services_service&facet=departement&facet=region&facet=id&facet=Adresse"
response_data = call_api(api_url)

# Créer un dataframe à partir des données de response_data
df_response = pd.DataFrame(response_data['records'])
df_id = df_response['fields'].apply(lambda x: x['id'])
df_id.rename('id', inplace=True)

# Effectuer la jointure en utilisant l'ID comme clé de jointure
df_merged = pd.merge(data_sign, df_id, left_on='id', right_on='id', how='inner')

# Page beginning 
st.title('Find the nearest fuel stations from your home')
st.subheader('Search your favorite fuel station')
st.info('If you didnt find your city in the selectbox, this means that there is no station in your town. I will update this after.')

# Liste des stations de la ville recherchée
stations_ville_recherchee = []
# Liste des villes de l'API
villes = []

for enregistrement in response_data['records']:
    fields = enregistrement.get("fields")
    ville = fields.get("ville")

    if ville and ville not in villes:
        villes.append(ville)

villes = sorted([ville for ville in villes if ville is not None])
city = st.selectbox('Select your city', villes)

# Parcourir les enregistrements
for enregistrement in response_data['records']:
    fields = enregistrement.get("fields")
    if fields and fields.get("ville") == city:
        # Ajouter la station à la liste
        stations_ville_recherchee.append(enregistrement)

# Vérifier si des stations ont été trouvées dans la ville recherchée
if len(stations_ville_recherchee) > 0:
    # Display all data in a map from the selected city
    st.subheader('Map of all fuel stations in your city')
    # Récupérer les coordonnées de la première station
    first_station = stations_ville_recherchee[0]
    latitude = first_station['geometry']['coordinates'][1]
    longitude = first_station['geometry']['coordinates'][0]
    # Créer la carte centrée sur la ville recherchée
    m = folium.Map(location=[latitude, longitude], zoom_start=13)

    # Afficher les informations des stations trouvées dans une carte Folium
    for station in stations_ville_recherchee:
        # Créer le contenu HTML du popup
        popup_content = f"<h4>{station['fields']['adresse'] + ' ' + station['fields']['cp'] + ' ' + station['fields']['ville']}</h4>"
        
        # Si la station a le champ carburant_indisponible
        if 'carburants_indisponibles' in station['fields']:
            popup_content += f"<p><strong>Carburants indisponibles :</strong> {station['fields']['carburants_indisponibles']}</p>"
        # Récupérer les prix des carburants
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
                # Si la valeur est une liste, cela signifie qu'il y a plusieurs carburants
                for carburant in prix_carburants:
                    nom_carburant = carburant.get('@nom')
                    valeur_carburant = carburant.get('@valeur')
                    if nom_carburant and valeur_carburant:
                        popup_content += f"<p><strong>Prix {nom_carburant}:</strong> {valeur_carburant}</p>"
                    else:
                        popup_content += f"<p><strong>Prix {nom_carburant}:</strong> None</p>"
        else:
            popup_content += "<p><strong>Prix:</strong> None</p>"

        # Ajouter le marqueur avec le popup à la carte
        folium.Marker(
            location=[station['geometry']['coordinates'][1], station['geometry']['coordinates'][0]],
            popup=folium.Popup(popup_content, max_width=250),
            icon=folium.Icon(color='green', icon='tint', prefix='fa')
        ).add_to(m)
        
    # Afficher la carte dans Streamlit
    st_folium(m, width=1250)
else : 
    st.error("No fuel station found in your city")