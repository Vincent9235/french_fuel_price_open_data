# - Regarder les enseignes les plus chères par département
# - Regarder les enseignes les moins chères par département
# - Regarder les enseignes les plus présentes par département
# - Regarder les enseignes les moins présentes par département
# - Regarder les enseignes les plus chères par ville
# - Regarder les enseignes les moins chères par ville
# - Regarder les enseignes les plus présentes par ville
# - Regarder les enseignes les moins présentes par ville

# Imports
import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import requests
import io
import zipfile
import datetime

# Import own functions
from load_functions import load_xml, load_json, call_api

# Page config
st.set_page_config(
    page_title='Statistics on french fuel stations',
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


# URL to load data
historique_2023_url = "https://donnees.roulez-eco.fr/opendata/annee"
# Local file if url is not available
historique_2023_filename = "../data/PrixCarburants_annuel_2023.xml"

# Load data 2023
# Récupérer le fichier ZIP à partir de l'URL
response = requests.get(historique_2023_url)
zip_content = io.BytesIO(response.content)

# Extraire le fichier XML du fichier ZIP
with zipfile.ZipFile(zip_content, "r") as zip_ref:
    with zip_ref.open("PrixCarburants_annuel_2023.xml") as xml_file:
        tree = ET.parse(xml_file)
        root = tree.getroot()

# Load data sign
# I dont use url here because the original file is false
sign_file = 'data/stations.json'
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

# Calculer le nombre de stations par enseigne
number_values_by_enseigne = df_merged['marque'].value_counts()
number_values_by_enseigne.rename('number_stations', inplace=True)

# Voir le top 3 des enseignes les plus chers au niveau national avec le prix moyen sur les 30 derniers jours
# Créer un dictionnaire pour stocker les données des prix par carburant
prix_par_carburant = {}

# Récupérer la date du jour
date_jour = datetime.datetime.now().date()

# Récupérer le fichier ZIP à partir de l'URL
response = requests.get(historique_2023_url)
zip_content = io.BytesIO(response.content)

# Extraire le fichier XML du fichier ZIP
with zipfile.ZipFile(zip_content, "r") as zip_ref:
    with zip_ref.open("PrixCarburants_annuel_2023.xml") as xml_file:
        tree = ET.parse(xml_file)
        root = tree.getroot()

# Extract data from pdv elements
data = []
for pdv_element in root.iter('pdv'):
    pdv_id = pdv_element.get('id')
    
    # Extract prix elements
    prix_elements = pdv_element.findall('prix')
    for prix_element in prix_elements:
        item = {}
        item['pdv_id'] = pdv_id
        item['nom'] = prix_element.get('nom')
        item['maj'] = prix_element.get('maj')
        item['valeur'] = prix_element.get('valeur')
        data.append(item)

# Create DataFrame
df = pd.DataFrame(data)

# Convert 'valeur' column to numeric
df['valeur'] = pd.to_numeric(df['valeur'], errors='coerce')

# Convert 'maj' column to datetime type
df['maj'] = pd.to_datetime(df['maj'])

# Convert 'id' to int64 type
df['pdv_id'] = df['pdv_id'].astype('int64')

# Group by 'pdv_id', 'nom', and date (day) of 'maj', and aggregate 'valeur' with mean
df['maj_day'] = df['maj'].dt.date
df_aggregated = df.groupby(['pdv_id', 'nom', 'maj_day'])['valeur'].mean().reset_index()

# Effectuer la jointure en utilisant l'ID comme clé de jointure
df_merged_2 = pd.merge(data_sign, df_aggregated, left_on='id', right_on='pdv_id', how='inner')

# Voir le top 3 des enseignes les plus chers au niveau national avec le prix moyen sur les 30 derniers jours

# Convert 'maj_day' column to datetime type
df_merged_2['maj_day'] = pd.to_datetime(df_merged_2['maj_day'])

# Filter data for the last 30 days
last_30_days = df_merged_2['maj_day'] >= df_merged_2['maj_day'].max() - pd.DateOffset(days=30)
df_merged_2['within_last_30_days'] = last_30_days

# Calculate the average price per brand and fuel type
average_price_per_brand_fuel = df_merged_2[last_30_days].groupby(['marque', 'nom_y'])['valeur'].mean()

# Find the top 3 most expensive brands per fuel type
top_3_expensive_brands_fuel = average_price_per_brand_fuel.groupby('nom_y').nlargest(3) 

# Find the top 3 cheapest brands per fuel type
top_3_cheapest_brands_fuel = average_price_per_brand_fuel.groupby('nom_y').nsmallest(3) 


# Page beginning 
st.title('Stats on different fuel signs in France')
st.subheader('Number of stations by sign')

# Display the number of stations by sign
st.dataframe(number_values_by_enseigne)

# Get unique fuel types
fuel_types = df_merged_2['nom_y'].unique().tolist()
# Create tabs for each fuel type
tabs = st.tabs(fuel_types)

# Display top 3 most expensive brands per fuel type
st.subheader('Top 3 most expensive brands per fuel type')
st.dataframe(top_3_expensive_brands_fuel)

# Display top 3 cheapest brands per fuel type
st.subheader('Top 3 cheapest brands per fuel type')
st.dataframe(top_3_cheapest_brands_fuel)