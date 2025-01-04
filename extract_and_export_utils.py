import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import csv
import re


def extract_product_details(url, image_folder):
    """
    Extrait les détails d'un produit à partir de l'URL de la page produit.
    Télécharge également l'image associée au produit.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extraire le titre du produit
    product_title = soup.find('h1').get_text().strip()

    # Extraire l'URL de l'image du produit
    img_tag = soup.find('div', class_='item active').find('img')
    img_src = img_tag['src']
    img_url = urljoin(url, img_src)

    # Nettoyer et limiter la longueur du nom
    safe_title = re.sub(r'[^A-Za-z0-9 ]+', '', product_title)[:100]
    if not safe_title:
        safe_title = "Unknown_Product"

    # Utiliser la date et l'heure pour éviter les doublons
    date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    image_name = f"{safe_title}_{date_str}_image.jpg"

    # Construire le chemin de l'image
    image_path = os.path.join(image_folder, image_name)

    # Télécharger l'image
    download_image(img_url, image_path)

    # Extraire les détails du produit
    product_info = {'Product Title': product_title}
    product_details_table = soup.find('table', class_='table table-striped')

    for row in product_details_table.find_all('tr'):
        header = row.find('th').get_text(strip=True)
        value = row.find('td').get_text(strip=True)
        product_info[header] = value

    return product_info


def save_to_csv(product_data, catalogue_name, folder):
    """
    Enregistre les informations des produits dans un fichier CSV.
    """
    if not product_data:
        print("Aucune donnée à enregistrer.")
        return

    # Créer le dossier s'il n'existe pas
    os.makedirs(folder, exist_ok=True)

    # Créer le nom du fichier CSV
    file_name = f"{catalogue_name}_infos_{datetime.now().strftime('%Y-%m-%d')}.csv"
    save_path = os.path.join(folder, file_name)

    # Gérer les cas d'un produit unique
    if isinstance(product_data, dict):
        product_data = [product_data]

    # Enregistrer dans un fichier CSV
    with open(save_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=product_data[0].keys())
        writer.writeheader()
        writer.writerows(product_data)

    print(f"Catalogue exporté : {save_path}")


def fetch_catalogue_product_links(url_catalogue):
    """
    Récupère les liens de tous les produits d'un catalogue.
    """
    links = []
    catalogue_name = None

    while True:
        response = requests.get(url_catalogue)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extraire le nom du catalogue
        catalogue_name = soup.find(class_="page-header action").get_text(strip=True)

        # Récupérer les liens vers les produits
        articles = soup.find_all('article')
        for article in articles:
            product_link = article.find('a')['href']
            absolute_link = urljoin(base_url, product_link.replace('../../../', ''))
            links.append(absolute_link)

        # Passer à la page suivante s'il y en a une
        next_page = soup.find(class_="next")
        if next_page:
            next_page_link = next_page.find('a')['href']
            url_catalogue = urljoin(url_catalogue, next_page_link)
        else:
            break

    return links, catalogue_name


def export_single_product(url):
    """
    Exporte les informations d'un seul produit dans un dossier spécifique.
    """
    product_folder = os.path.join("Product_Info")
    os.makedirs(product_folder, exist_ok=True)

    # Dossier pour les images
    image_folder = os.path.join(product_folder, 'images')
    os.makedirs(image_folder, exist_ok=True)

    # Extraire les détails du produit
    product_info = extract_product_details(url, image_folder)

    # Enregistrer les détails dans un CSV
    save_to_csv(product_info, "single_product", product_folder)

    print(f"Produit exporté : {product_info['Product Title']}")


def fetch_category_links(url):
    """
    Récupère les liens de toutes les catégories disponibles sur la page principale.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    links_section = soup.find(class_="side_categories")

    if links_section:
        category_links = [urljoin(url, link['href']) for link in links_section.find_all('a', href=True)]
        return category_links
    else:
        print("Aucune catégorie trouvée.")
        return []


def export_catalogue_products(url_catalogue):
    """
    Exporte les produits d'un catalogue entier.
    """
    product_links, catalogue_name = fetch_catalogue_product_links(url_catalogue)
    catalogue_folder = os.path.join(catalogue_name.replace(' ', '_'))
    image_folder = os.path.join(catalogue_folder, 'images')

    os.makedirs(image_folder, exist_ok=True)

    all_products = []
    for link in product_links:
        product_info = extract_product_details(link, image_folder)
        all_products.append(product_info)

    save_to_csv(all_products, catalogue_name, catalogue_folder)


def export_all_catalogue_product(url):
    """
    Exporte tous les produits de toutes les catégories disponibles.
    """
    category_links = fetch_category_links(url)
    for link in category_links[1:]:
        export_catalogue_products(link)


def download_image(url, save_as):
    """
    Télécharge une image à partir de l'URL et l'enregistre localement.
    """
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_as, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
    else:
        print(f"Échec du téléchargement de l'image : {response.status_code}")


# Base URL de départ
base_url = "https://books.toscrape.com/catalogue/"
