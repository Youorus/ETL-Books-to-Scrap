# 📚 Book Scraper – Web Scraping pour Books to Scrape

## 📄 Description

Book Scraper est un projet de web scraping qui extrait les informations détaillées (titre, prix, disponibilité, etc.) des livres disponibles sur le site Books to Scrape.
Les informations extraites sont enregistrées dans des fichiers CSV, accompagnées des images des couvertures des livres.


## 📁 Structure du Projet

### Le projet est organisé autour de trois scripts principaux :

* **export_single_product.py** : Extrait les informations d'un seul produit spécifique à partir de son URL.
* **export_catalogue.py** : Extrait les détails de tous les produits d'un catalogue donné (une catégorie).
* **export_all_catalogues.py** : Extrait les produits de toutes les catégories du site, en créant des fichiers CSV et des dossiers distincts pour chaque catalogue.

## ⚙️ Fonctionnalités

* Extraction des détails du produit : Titre, prix, disponibilité et autres informations détaillées.
* Téléchargement des images des couvertures des livres dans des sous-dossiers dédiés.
* Organisation automatique des données extraites en fonction des catégories.
* Gestion des pages multiples d'un catalogue avec prise en charge de la pagination.

## 🛠️ Prérequis

* Python 3.8+
* Dépendances : pip install -r `requirements.txt`

## 📋 Comment Utiliser
1. Exporter un produit spécifique `export_single_product.py` : Ce script téléchargera les détails et l'image dans le dossier Product_Info/.
2. Exporter un catalogue complet `export_catalogue.py` : Les données seront stockées dans un dossier nommé d'après la catégorie choisie
3. Exporter tous les catalogues `export_all_catalogues.py` :  Chaque catalogue est exporté dans un dossier distinct avec ses propres fichiers CSV et images.

## 🛡️ Conformité et Bonnes Pratiques

* **Noms de fichiers sûrs** : Les noms de fichiers sont nettoyés pour éviter les caractères spéciaux.
* **Gestion des doublons** : Les images et CSV sont horodatés pour éviter les écrasements de fichiers.
* **Dossiers organisés** : Chaque produit ou catalogue dispose de son propre dossier pour une meilleure gestion des données.

## 📞 Contact

* Auteur : Marc
* Supervision : Openclassrooms
* Dépôt GitHub : https://github.com/Youorus/ETL-Books-to-Scrap