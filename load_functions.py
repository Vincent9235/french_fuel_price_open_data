# Import librairies
import requests
import pandas as pd
import json
import xml.etree.ElementTree as ET

# Function to load XML file
def load_xml(url_file) : 
    # Load XML file
    tree = ET.parse(url_file)
    root = tree.getroot()

    # Extract data
    data = []
    for element in root:
        item = {}
        for child in element:
            item[child.tag] = child.text
        data.append(item)

    # DataFrame conversion
    df = pd.DataFrame(data)
    # Return the DataFrame
    return df

# Function to load JSON file
def load_json(url_file) : 
    # Load JSON file
    with open(url_file) as json_file:
        data = json.load(json_file)
    # DataFrame conversion
    df = pd.DataFrame(data)
    # Return the DataFrame
    return df

# Function to call API
def call_api(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verify if the request is successful
        data = response.json()  # Convert to JSON format
        return data
    except requests.exceptions.RequestException as e:
        print("Une erreur s'est produite lors de l'appel à l'API :", e)
        return None