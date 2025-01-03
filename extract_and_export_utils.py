import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import csv


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


base_url = "https://books.toscrape.com/catalogue/"


# Fonction pour récupérer les liens des produits d'un catalogue
def get_catalogue_links(url_catalogue):
    links = []

    while True:
        # Effectuer la requête HTTP pour chaque page
        response = requests.get(url_catalogue)
        soup = BeautifulSoup(response.text, "html.parser")

        # Récupérer tous les articles de la page actuelle
        articles = soup.find_all('article')
        catalogue_name = soup.find(class_="page-header action").get_text(strip=True)

        for article in articles:
            link = article.find('a').attrs['href']
            # Construire l'URL absolue
            url_product = urljoin(base_url, link.replace('../../../', ''))
            links.append(url_product)

        # Vérifier s'il y a une page suivante
        is_next = soup.find(class_="next")

        if is_next:
            next_page = is_next.find('a')['href']
            url_catalogue = urljoin(url_catalogue, next_page)
        else:
            break

    return links, catalogue_name

# 5. Exporter un seul produit par son URL
def export_product_info(url):
    product_info = extract_product_info(url)
    write_to_csv(product_info)
    print(f"Produit exporté : {product_info['Product Title']}")


def export_product_infos_catalogue(url_catalogue):
    # Récupérer les liens des produits et le nom du catalogue
    product_links, catalogue_name = get_catalogue_links(url_catalogue)

    # Extraire les infos de chaque produit et les stocker dans une liste
    all_products = []

    for link in product_links:
        product_info = extract_product_info(link)  # Extraire les infos du produit
        all_products.append(product_info)  # Ajouter à la liste

    # Créer le fichier CSV global
    write_to_csv(all_products, catalogue_name)