import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import csv


# 1. Fonction pour extraire les informations d'un produit
def extract_product_details(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    product_title = soup.find('h1').get_text()
    product_details_table = soup.find('table', class_='table table-striped')

    product_info = {'Product Title': product_title}

    for row in product_details_table.find_all('tr'):
        header = row.find('th').get_text()
        value = row.find('td').get_text()
        product_info[header] = value

    return product_info


# 2. Fonction pour écrire des données dans un fichier CSV
def save_to_csv(product_data, catalogue_name=None):
    if not product_data:
        print("Aucune donnée à écrire.")
        return

    # Gérer le cas d'un produit unique
    if isinstance(product_data, dict):
        product_data = [product_data]

    # Si un catalogue est spécifié
    if catalogue_name:
        file_name = f"{catalogue_name}_catalogue_infos_product{datetime.now().strftime('%Y-%m-%d')}.csv"
        with open(file_name, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=product_data[0].keys())
            writer.writeheader()
            writer.writerows(product_data)
        print(f"Catalogue complet exporté : {file_name}")
    else:
        # Exporter chaque produit individuellement
        for product in product_data:
            product_title = product['Product Title']
            file_name = f"{product_title}_infos_{datetime.now().strftime('%Y-%m-%d')}.csv"
            with open(file_name, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=product.keys())
                writer.writeheader()
                writer.writerow(product)
            print(f"Produit exporté individuellement : {file_name}")


# 3. Fonction pour récupérer les liens de tous les produits dans un catalogue
def fetch_catalogue_product_links(url_catalogue):
    links = []
    catalogue_name = None

    while True:
        response = requests.get(url_catalogue)
        soup = BeautifulSoup(response.text, "html.parser")

        articles = soup.find_all('article')
        catalogue_name = soup.find(class_="page-header action").get_text(strip=True)

        for article in articles:
            product_link = article.find('a').attrs['href']
            absolute_link = urljoin(base_url, product_link.replace('../../../', ''))
            links.append(absolute_link)

        # Vérifier la pagination
        next_page = soup.find(class_="next")
        if next_page:
            next_page_link = next_page.find('a')['href']
            url_catalogue = urljoin(url_catalogue, next_page_link)
        else:
            break

    return links, catalogue_name


# 4. Fonction pour exporter un seul produit
def export_single_product(url):
    product_info = extract_product_details(url)
    save_to_csv(product_info)
    print(f"Produit exporté : {product_info['Product Title']}")


# 5. Fonction pour récupérer les liens des catégories
def fetch_category_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    links_section = soup.find(class_="side_categories")

    if links_section:
        category_links = [urljoin(url, link['href']) for link in links_section.find_all('a', href=True)]
        return category_links
    else:
        print("Aucune catégorie trouvée.")
        return []


# 6. Fonction pour exporter les produits d'un catalogue entier
def export_catalogue_products(url_catalogue):
    product_links, catalogue_name = fetch_catalogue_product_links(url_catalogue)
    all_products = []

    for link in product_links:
        product_info = extract_product_details(link)
        all_products.append(product_info)

    save_to_csv(all_products, catalogue_name)


# 7. Fonction pour exporter tous les produits de toutes les catégories
def export_all_catalogue_product(url):
    category_links = fetch_category_links(url)
    for link in category_links[1:]:
        export_catalogue_products(link)



# Base URL de départ
base_url = "https://books.toscrape.com/catalogue/"
