import requests
from bs4 import BeautifulSoup


def get_category_links(url):
    # Envoyer une requête GET à l'URL
    page = requests.get(url)

    # Vérifier si la requête a réussi
    if page.status_code != 200:
        print(f"Erreur de connexion : {page.status_code}")
        return []

    # Parser le contenu de la page
    soup = BeautifulSoup(page.content, 'html.parser')

    # Récupérer la section des catégories
    links_section = soup.find(class_="side_categories")

    # Vérifier si la section est trouvée
    if links_section:
        # Trouver tous les liens dans cette section
        all_links = [link['href'] for link in links_section.find_all('a', href=True)]
        return all_links
    else:
        print("Aucune catégorie trouvée.")
        return []


# Tester la méthode
url = "https://books.toscrape.com/"
category_links = get_category_links(url)

# Afficher les liens récupérés
if category_links:
    print("Liens des catégories :")
    for link in category_links:
        print(link)
else:
    print("Aucun lien récupéré.")