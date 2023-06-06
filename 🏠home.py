# Lien pour trouver les marques des stations : https://raw.githubusercontent.com/openeventdatabase/datasources/master/fr.prix-carburants/stations.json
# Ex de réutilisation : https://explore.data.gouv.fr/prix-carburants

# TO DO:
# - Récupérer données via API ou via fichier zip/xml (historique de l'année)
# - Faire une page explication du projet et du traitement de la donnée
# - Analyser la qualité des données : doublons, valeurs manquantes, valeurs aberrantes

# Import librairies
import requests
import zipfile
import pandas as pd
import io 
import json
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
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
historique_2022_url = "https://donnees.roulez-eco.fr/opendata/annee/2022"

# Local file if url is not available
historique_2023_filename = "data/PrixCarburants_annuel_2023.xml"
historique_2022_filename = "data/PrixCarburants_annuel_2022.xml"
# I dont use url here because the original file is false
sign_file = 'data/stations.json'

## Load data 2022
#try:
#    # Verify if the URL is available
#    urllib.request.urlopen(historique_2022_url)
#    # if url is available, load XML file
#    response = requests.get(historique_2022_url)
#
#    zip_file = zipfile.ZipFile(BytesIO(response.content))
#    file_name = zip_file.namelist()[0]
#    data = zip_file.open(file_name)
#    price_2022 = load_xml(data)
#except:
#    # Else, load local file
#    price_2022 = load_xml(historique_2022_filename)

# Load data from Open Data API	
api_url = "https://data.economie.gouv.fr/api/records/1.0/search/?dataset=prix-des-carburants-en-france-flux-instantane-v2&q=&rows=10000&facet=carburants_disponibles&facet=carburants_indisponibles&facet=horaires_automate_24_24&facet=services_service&facet=departement&facet=region&facet=id&facet=Adresse"
response_data = call_api(api_url)

st.title('Fuel prices in France')
st.write('This application is a Streamlit dashboard that can be used to analyze fuel prices in France. The data is from the French government open data portal. The data is updated every 15 minutes.')
st.subheader('National Fuel prices in France :')

# Display data in many columns
if response_data is not None:
    # Compute many statistics on the data
    # Compter le nombre de stations services
    nb_stations = len(response_data['records'])
    st.write('Number of fuel stations in France in the dataset: ', nb_stations, '⛽')

    # Compter le nombre de villes
    villes = []
    for record in response_data['records']:
        if 'fields' in record and 'ville' in record['fields']:
            villes.append(record['fields']['ville'])
    nb_villes = len(set(villes))
    st.write('Number of cities in the dataset : ', nb_villes, '🏙️')

    # Créer un dictionnaire pour stocker les prix de chaque type de carburant
    prix_par_carburant = {}

    # Parcourir tous les enregistrements et extraire les prix par type de carburant
    for record in response_data['records']:
        if 'fields' in record and 'prix' in record['fields']:
            prix_json = record['fields']['prix']
            prix_data = json.loads(prix_json)

            # Parcourir les prix de chaque type de carburant et les ajouter au dictionnaire
            for prix in prix_data:
                if '@nom' in prix and '@valeur' in prix:
                    nom_carburant = prix['@nom']
                    valeur_prix = float(prix['@valeur'])

                if nom_carburant not in prix_par_carburant:
                    prix_par_carburant[nom_carburant] = []
                prix_par_carburant[nom_carburant].append(valeur_prix)

    # Calculer le prix moyen de chaque type de carburant
    prix_moyen_par_carburant = {}
    for nom_carburant, prix_liste in prix_par_carburant.items():
        prix_moyen = sum(prix_liste) / len(prix_liste)
        prix_moyen_par_carburant[nom_carburant] = prix_moyen

# Afficher le prix moyen de chaque type de carburant
# Calculer le nombre de colonnes nécessaires
    nb_colonnes = len(prix_moyen_par_carburant)
    # Afficher le prix moyen de chaque type de carburant dans Streamlit
    colonnes = st.columns(nb_colonnes)
    for i, (nom_carburant, prix_moyen) in enumerate(prix_moyen_par_carburant.items()):
        colonne = colonnes[i]
        prix_arrondi = round(prix_moyen, 2)  # Arrondir à deux chiffres après la virgule
        colonne.metric(label=nom_carburant, value=str(prix_arrondi) + '€') 

# Display a graph showing 30-day price trends for each type of fuel 
st.subheader('Price trends for each type of fuel over last 30 days :')

# Récupérer le fichier ZIP à partir de l'URL
response = requests.get(historique_2023_url)
zip_content = io.BytesIO(response.content)

# Extraire le fichier XML du fichier ZIP
with zipfile.ZipFile(zip_content, "r") as zip_ref:
    with zip_ref.open("PrixCarburants_annuel_2023.xml") as xml_file:
        tree = ET.parse(xml_file)
        root = tree.getroot()

# Average change in fuel prices over the past 30 days :

# Créer un dictionnaire pour stocker les données des prix par carburant
prix_par_carburant = {}
prix_par_carburant_6_mois = {}

# Récupérer la date du jour
date_jour = datetime.datetime.now().date()

# Récupérer la date d'il y a 30 jours
date_30_jours = date_jour - datetime.timedelta(days=30)

# Récupérer la date d'il y a 6 mois
date_6_mois = date_jour - datetime.timedelta(days=6 * 30)

# Parcourir les éléments <prix> sur les 30 derniers jours dans les données XML
for prix_element in root.iter('prix'):
    # Récupérer la date et la valeur du prix
    nom_carburant = prix_element.get('nom')
    date_maj = prix_element.get('maj')
    valeur_prix = prix_element.get('valeur')

    # Vérifier si la valeur du prix existe
    if valeur_prix is not None:
        valeur_prix = float(valeur_prix)

        # Vérifier si la date est dans la plage des 30 derniers jours
        if date_maj >= str(date_30_jours):
            # Ajouter le prix au dictionnaire correspondant au carburant
            if nom_carburant in prix_par_carburant:
                prix_par_carburant[nom_carburant].append((date_maj, valeur_prix))
            else:
                prix_par_carburant[nom_carburant] = [(date_maj, valeur_prix)]

        # Vérifier si la date est dans la plage des 6 derniers mois
        if date_maj >= str(date_6_mois):
            # Ajouter le prix au dictionnaire correspondant au carburant
            if nom_carburant in prix_par_carburant_6_mois:
                prix_par_carburant_6_mois[nom_carburant].append((date_maj, valeur_prix))
            else:
                prix_par_carburant_6_mois[nom_carburant] = [(date_maj, valeur_prix)]
                
# Evolution du prix des carburants au niveau national

# Créer un DataFrame Pandas à partir des données de prix
df_prix = pd.DataFrame()
for carburant, prix in prix_par_carburant.items():
    df = pd.DataFrame(prix, columns=['date', 'prix'])
    df['carburant'] = carburant
    df_prix = df_prix.append(df)

# Convertir la colonne 'date' en type datetime
df_prix['date'] = pd.to_datetime(df_prix['date'])

# Agréger les données par jour et calculer la moyenne des prix
df_agrege = df_prix.groupby([df_prix['date'].dt.date, 'carburant']).mean().reset_index()

# Créer le graphique avec Plotly Express
fig = px.line(df_agrege, x='date', y='prix', color='carburant', title='Average change in fuel prices (last 30 days)')

# Afficher le graphique dans Streamlit
st.plotly_chart(fig)

# Display a graph showing 6 month price trends for each type of fuel 
st.subheader('Price trends for each type of fuel over last 6 months :')

df_prix_6_mois = pd.DataFrame()
for carburant, prix in prix_par_carburant_6_mois.items():
    df = pd.DataFrame(prix, columns=['date', 'prix'])
    df['carburant'] = carburant
    df_prix_6_mois = df_prix_6_mois.append(df)

# Convertir la colonne 'date' en type datetime
df_prix_6_mois['date'] = pd.to_datetime(df_prix_6_mois['date'])

# Agréger les données par mois et calculer la moyenne des prix
df_agrege = df_prix_6_mois.groupby([pd.Grouper(key='date', freq='M'), 'carburant']).mean().reset_index()

# Créer le graphique avec Plotly Express
fig = px.line(df_agrege, x='date', y='prix', color='carburant', title='Average change in fuel prices (last 6 months)')

# Afficher le graphique dans Streamlit
st.plotly_chart(fig)