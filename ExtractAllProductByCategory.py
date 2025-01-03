import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from ExtractProductInfos import extract_product_info, write_to_csv

# Préfixe de l'URL de base
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

# Exemple d'utilisation dans ton code existant
url_catalogue = "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html"

# Récupérer les liens des produits et le nom du catalogue
product_links, catalogue_name = get_catalogue_links(url_catalogue)

# Extraire les infos de chaque produit et les stocker dans une liste
all_products = []

for link in product_links:
    product_info = extract_product_info(link)  # Extraire les infos du produit
    all_products.append(product_info)          # Ajouter à la liste


write_to_csv(all_products, catalogue_name)  # Créer le fichier CSV global






