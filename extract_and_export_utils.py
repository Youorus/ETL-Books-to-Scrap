import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import csv
import re



def extract_product_details(url):
    """
    Extrait les détails d'un produit à partir de l'URL de la page produit.
    Retourne les informations du produit et l'URL de l'image.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extraire le titre du produit
    product_title = soup.find('h1').get_text().strip()

    # Extraire l'URL de l'image du produit
    img_tag = soup.find('div', class_='item active').find('img')
    img_src = img_tag['src']
    img_url = urljoin(url, img_src)

    # Nettoyer le titre pour en faire un nom de fichier sûr
    safe_title = re.sub(r'[^A-Za-z0-9]+', '-', product_title).lower()[:30]

    # Initialisation des champs par défaut
    product_info = {
        'product_page_url': url,
        'universal_product_code (upc)': 'N/A',
        'title': product_title,
        'price_including_tax': 'N/A',
        'price_excluding_tax': 'N/A',
        'number_available': 'N/A',
        'product_description': 'N/A',
        'category': 'N/A',
        'review_rating': 'N/A',
        'image_url': img_url
    }

    # Extraire les détails du produit (table)
    product_details_table = soup.find('table', class_='table table-striped')
    for row in product_details_table.find_all('tr'):
        header = row.find('th').get_text(strip=True)
        value = row.find('td').get_text(strip=True)

        if header == "UPC":
            product_info['universal_product_code (upc)'] = value
        elif header == "Price (incl. tax)":
            product_info['price_including_tax'] = clean_price(value)
        elif header == "Price (excl. tax)":
            product_info['price_excluding_tax'] = clean_price(value)
        elif header == "Availability":
            product_info['number_available'] = re.search(r'\d+', value).group(0) if re.search(r'\d+', value) else '0'
        elif header == "Number of reviews":
            product_info['review_rating'] = value

    # Extraire la description du produit
    description_tag = soup.select_one('#product_description ~ p')
    if description_tag:
        product_info['product_description'] = description_tag.text.strip()

    # Extraire la catégorie
    category = soup.select_one('.breadcrumb li:nth-child(3) a')
    product_info['category'] = category.text.strip() if category else 'N/A'

    return product_info, safe_title, img_url


def save_to_csv(product_data, name, export_folder, is_single=False):
    """
    Enregistre les informations dans un fichier CSV et gère la structure des dossiers
    pour un produit unique, un catalogue complet ou toutes les catégories.
    """
    # Créer le dossier principal pour l'export
    os.makedirs(export_folder, exist_ok=True)

    # Déterminer le nom du fichier CSV et de l'image
    date_str = datetime.now().strftime('%Y-%m-%d')
    csv_name = f"{name}_details_{date_str}.csv"
    csv_path = os.path.join(export_folder, csv_name)

    # Créer le dossier d'images
    image_folder = os.path.join(export_folder, 'images')
    os.makedirs(image_folder, exist_ok=True)

    # Gérer les cas d'un produit unique (pour export_single_product)
    if is_single and isinstance(product_data, dict):
        product_data = [product_data]

    # En-têtes du CSV
    headers = [
        'product_page_url', 'universal_product_code (upc)', 'title',
        'price_including_tax', 'price_excluding_tax', 'number_available',
        'product_description', 'category', 'review_rating', 'image_url'
    ]

    # Écriture dans le CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(product_data)

    print(f"CSV exporté : {csv_path}")


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
    product_info, safe_title, img_url = extract_product_details(url)
    date_str = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    folder_name = f"{safe_title}_details"

    # Créer le dossier principal du produit
    product_folder = os.path.join(folder_name)
    image_folder = os.path.join(product_folder, 'images')
    os.makedirs(image_folder, exist_ok=True)

    # Télécharger l'image
    download_image(img_url, os.path.join(image_folder, f"{safe_title}_{date_str}.jpg"))

    # Enregistrer les détails dans un CSV
    save_to_csv(product_info, safe_title, product_folder, is_single=True)


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
        product_info, safe_title, img_url = extract_product_details(link)
        all_products.append(product_info)

        # Télécharger l'image
        date_str = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        image_path = os.path.join(image_folder, f"{safe_title}_{date_str}.jpg")
        download_image(img_url, image_path)

    save_to_csv(all_products, catalogue_name, catalogue_folder)


def export_all_catalogue_product(url):
    """
    Exporte tous les produits de toutes les catégories disponibles.
    """
    category_links = fetch_category_links(url)
    for link in category_links[1:]:
        export_catalogue_products(link)

def clean_price(price_str):
    """
    Nettoie et formate correctement le prix.
    Ex : "£45.20" -> 45.20
    """
    clean_str = re.sub(r'[^\d.]', '', price_str)
    return float(clean_str) if clean_str else 'N/A'

def download_image(url, save_as):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_as, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
    else:
        print(f"Échec du téléchargement de l'image : {response.status_code}")


# Base URL de départ
base_url = "https://books.toscrape.com/catalogue/"
