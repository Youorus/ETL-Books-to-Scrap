from datetime import datetime
import requests
from bs4 import BeautifulSoup
import csv
import re

url = "/--ENTRER L'URL DU PRODUIT ICI--/"

def getProductsInfos(url):
    # Récupérer la page
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Extraire les données du produit
    table = soup.find('table', class_='table table-striped')
    product_title = soup.find('h1').get_text()

    # Ajouter la date
    create_at = datetime.now().strftime("%Y-%m-%d")

    # Initialisation des en-têtes et des valeurs
    headers = ['Product Title']
    product_infos = [product_title]

    # Nom du fichier CSV
    csv_file = f"{product_title}_infos_{create_at}.csv"

    # Parcourir la table pour ajouter les en-têtes et valeurs
    for tr in table.find_all('tr'):
        th = tr.find('th').get_text()
        td = tr.find('td').get_text()

        headers.append(th)
        product_infos.append(td)

    # Écriture des données dans un fichier CSV
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(headers)
        writer.writerow(product_infos)

    print(f"Le fichier {csv_file} a été créé avec succès.")


# Appel de la fonction
getProductsInfos(url)
