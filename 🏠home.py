# Import librairies
import requests
import zipfile
import pandas as pd
import io 
import json
import xml.etree.ElementTree as ET
import datetime
import streamlit as st
import plotly.express as px

# Import own functions
from load_functions import load_xml, load_json, call_api

# Page config
st.set_page_config(
    page_title='French fuel prices',
    page_icon='⛽',
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

# URL to load data
historique_2023_url = "https://donnees.roulez-eco.fr/opendata/annee"
# Local file if url is not available
historique_2023_filename = "data/PrixCarburants_annuel_2023.xml"
# I dont use url here because the original file is false
sign_file = 'data/stations.json'

# Load data from Open Data API	
api_url = "https://data.economie.gouv.fr/api/records/1.0/search/?dataset=prix-des-carburants-en-france-flux-instantane-v2&q=&rows=10000&facet=carburants_disponibles&facet=carburants_indisponibles&facet=horaires_automate_24_24&facet=services_service&facet=departement&facet=region&facet=id&facet=Adresse"
response_data = call_api(api_url)

st.title('Fuel prices in France💰')

# Display data in many columns
if response_data is not None:
    # Compute many statistics on the data
    # Compter le nombre de stations services
    nb_stations = len(response_data['records'])
    st.write('Number of fuel stations in France in the dataset: ', nb_stations, '⛽')

    # Count city number
    villes = []
    for record in response_data['records']:
        if 'fields' in record and 'ville' in record['fields']:
            villes.append(record['fields']['ville'])
    nb_villes = len(set(villes))
    st.write('Number of cities in the dataset : ', nb_villes, '🏙️')

    # Create a dictionary to store prices for each type of fuel
    prix_par_carburant = {}

    # Browse all records and extract prices by fuel type
    for record in response_data['records']:
        if 'fields' in record and 'prix' in record['fields']:
            prix_json = record['fields']['prix']
            prix_data = json.loads(prix_json)

            # Browse the prices of each type of fuel and add them to the dictionary
            for prix in prix_data:
                if '@nom' in prix and '@valeur' in prix:
                    nom_carburant = prix['@nom']
                    valeur_prix = float(prix['@valeur'])

                if nom_carburant not in prix_par_carburant:
                    prix_par_carburant[nom_carburant] = []
                prix_par_carburant[nom_carburant].append(valeur_prix)

# Calculate the average price of each type of fuel
prix_moyen_par_carburant = {}
for nom_carburant, prix_liste in prix_par_carburant.items():
    prix_moyen = sum(prix_liste) / len(prix_liste)
    prix_moyen_par_carburant[nom_carburant] = prix_moyen

# Show the average price of each type of fuel
st.subheader('National Fuel prices in France :')
# Calculate the number of columns needed
nb_colonnes = len(prix_moyen_par_carburant)
# Show the average price of each type of fuel
colonnes = st.columns(nb_colonnes)
for i, (nom_carburant, prix_moyen) in enumerate(prix_moyen_par_carburant.items()):
    colonne = colonnes[i]
    prix_arrondi = round(prix_moyen, 2)
    colonne.metric(label=nom_carburant, value=str(prix_arrondi) + '€') 

# Display a graph showing 30-day price trends for each type of fuel 
st.subheader('Price trends for each type of fuel over last 30 days :')

# Retrieve the ZIP file from the URL
response = requests.get(historique_2023_url)
zip_content = io.BytesIO(response.content)

# Extract XML from ZIP file 
with zipfile.ZipFile(zip_content, "r") as zip_ref:
    with zip_ref.open("PrixCarburants_annuel_2023.xml") as xml_file:
        tree = ET.parse(xml_file)
        root = tree.getroot()

# Dictionaries for storing price data by fuel
prix_par_carburant = {}
prix_par_carburant_6_mois = {}

# Get date of the day
date_jour = datetime.datetime.now().date()

# Get date of 30 days ago
date_30_jours = date_jour - datetime.timedelta(days=30)

# Get date of 6 months ago
date_6_mois = date_jour - datetime.timedelta(days=6 * 30)

# Browse <price> elements over the last 30 days in XML data
for prix_element in root.iter('prix'):
    # Get price, date and value
    nom_carburant = prix_element.get('nom')
    date_maj = prix_element.get('maj')
    valeur_prix = prix_element.get('valeur')

    # Check if the price value exists
    if valeur_prix is not None:
        valeur_prix = float(valeur_prix)

        # Check if the date is in the range of the last 30 days
        if date_maj >= str(date_30_jours):
            # Add the price to the dictionary corresponding to the fuel
            if nom_carburant in prix_par_carburant:
                prix_par_carburant[nom_carburant].append((date_maj, valeur_prix))
            else:
                prix_par_carburant[nom_carburant] = [(date_maj, valeur_prix)]

        # Check if the date is within the last 6 months range
        if date_maj >= str(date_6_mois):
            # Add the price to the dictionary corresponding to the fuel
            if nom_carburant in prix_par_carburant_6_mois:
                prix_par_carburant_6_mois[nom_carburant].append((date_maj, valeur_prix))
            else:
                prix_par_carburant_6_mois[nom_carburant] = [(date_maj, valeur_prix)]
                
# Average change in fuel prices over the past 30 days :

# Create a Pandas DataFrame from price data
df_prix = pd.DataFrame()
for carburant, prix in prix_par_carburant.items():
    df = pd.DataFrame(prix, columns=['date', 'prix'])
    df['carburant'] = carburant
    df_prix = pd.concat([df_prix, df], ignore_index=True)

# Convert 'date' column to datetime type
df_prix['date'] = pd.to_datetime(df_prix['date'])

# Group prices by date and fuel type
df_agrege = df_prix.groupby([df_prix['date'].dt.date, 'carburant']).mean().reset_index()

# Create a graph showing the average change in fuel prices over the last 30 days
fig = px.line(df_agrege, x='date', y='prix', color='carburant', title='Average change in fuel prices (last 30 days)')

# Display pot 
st.plotly_chart(fig)

# Display a graph showing 6 month price trends for each type of fuel 
st.subheader('Price trends for each type of fuel over last 6 months :')

df_prix_6_mois = pd.DataFrame()
for carburant, prix in prix_par_carburant_6_mois.items():
    df = pd.DataFrame(prix, columns=['date', 'prix'])
    df['carburant'] = carburant
    df_prix_6_mois = df_prix_6_mois.append(df)

# Convert 'date' column to datetime type
df_prix_6_mois['date'] = pd.to_datetime(df_prix_6_mois['date'])

# Group data by month and calculate average prices
df_agrege = df_prix_6_mois.groupby([pd.Grouper(key='date', freq='M'), 'carburant']).mean().reset_index()

# Create the graph with Plotly Express
fig = px.line(df_agrege, x='date', y='prix', color='carburant', title='Average change in fuel prices (last 6 months)')

# Display plot 
st.plotly_chart(fig)