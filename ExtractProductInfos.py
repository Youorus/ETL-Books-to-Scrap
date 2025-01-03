from datetime import datetime
import requests
from bs4 import BeautifulSoup
import csv
import re

# 1. Fonction pour extraire les informations d'un produit
def extract_product_info(url):
    # Récupérer la page
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extraire le titre du produit
    product_title = soup.find('h1').get_text()

    # Extraire la table des détails du produit
    table = soup.find('table', class_='table table-striped')

    # Initialisation des en-têtes et des valeurs
    product_info = {'Product Title': product_title}

    # Parcourir les lignes de la table
    for tr in table.find_all('tr'):
        th = tr.find('th').get_text()
        td = tr.find('td').get_text()
        product_info[th] = td

    return product_info


import csv
import re
from datetime import datetime


def write_to_csv(product_data, catalogue_name=None):
    # Si aucune donnée, arrêter
    if not product_data:
        print("Aucune donnée à écrire.")
        return

    # Cas d'un seul produit (dictionnaire)
    if isinstance(product_data, dict):
        product_data = [product_data]  # Convertir en liste pour uniformiser

    # Si catalogue_name est fourni, créer un fichier global pour le catalogue
    if catalogue_name:
        file_name = f"{catalogue_name}_catalogue_infos_{datetime.now().strftime('%Y-%m-%d')}.csv"

        # Écriture dans le fichier global
        with open(file_name, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=product_data[0].keys())
            writer.writeheader()
            writer.writerows(product_data)
        print(f"Catalogue complet exporté : {file_name}")

    # Si aucun catalogue_name, créer un fichier CSV par produit
    else:
        for product in product_data:
            product_title =  product['Product Title']
            file_name = f"{product_title}_infos_{datetime.now().strftime('%Y-%m-%d')}.csv"

            # Écriture pour chaque produit individuellement
            with open(file_name, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=product.keys())
                writer.writeheader()
                writer.writerow(product)
            print(f"Produit exporté individuellement : {file_name}")
