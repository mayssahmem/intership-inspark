import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import pandas as pd

# Définir les URLs des sites web à scraper
urls = [
    "https://www.who.int",
    "https://www.undp.org",
    "https://www.worldbank.org",
    "http://www.ins.tn",
    "https://ftdes.net",
    "http://www.onm.nat.tn",
    "http://www.courdescomptes.nat.tn",
    "https://fr.slideshare.net",
    "https://inkyfada.com",
    "http://www.santetunisie.rns.tn",
    "https://www.tunisiaodd.tn",
    "http://www.comiteethique.rns.tn",
    "https://tunisia.unfpa.org",
    "https://frenchhealthcare-association.fr",
    "https://www.memoireonline.com",
    "https://www.april-international.com",
    "https://www.challenges.tn",
    "https://ftdes.net",
    "https://jamaity.org",
    "https://tunisia.iom.int",
    "https://www.persee.fr"
]

# Fonction pour récupérer le contenu HTML d'une URL avec des en-têtes
def fetch_web_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Assure que la demande s'est bien terminée
    return response

# Fonction pour extraire un titre général et significatif
def generate_general_title(soup):
    # Essayer d'utiliser le titre de la page
    title_tag = soup.find('title')
    if title_tag and title_tag.get_text(strip=True):
        return title_tag.get_text(strip=True)

    # Essayer d'utiliser une balise <h1> s'il n'y a pas de <title>
    h1_tag = soup.find('h1')
    if (h1_tag and h1_tag.get_text(strip=True)):
        return h1_tag.get_text(strip=True)

    # Essayer d'utiliser une balise <meta name="description">
    meta_description = soup.find('meta', attrs={'name': 'description'})
    if meta_description and meta_description.get('content'):
        return meta_description.get('content')[:50]  # Limiter à 50 caractères

    # En dernier recours, retourne un titre par défaut
    return "Titre non trouvé"

# Liste des mots-clés à rechercher
keywords = [
    "One Health",
    "Antibioresistance",
    "Maladies sexuelles et reproductives",
    "Mental health",
    "Maladies infectieuses",
    "Tunisia",
    "Tunisie"
]

# Fonction pour vérifier si le titre contient un des mots-clés
def contains_keywords(title):
    return any(keyword.lower() in title.lower() for keyword in keywords)

# Fonction pour extraire les informations sur les articles (titre, date, URL)
def extract_article_info(soup, base_url):
    articles = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        title = link.get_text(strip=True)
        date = extract_article_date(soup)
        if contains_keywords(title):
            articles.append({
                "url": full_url,
                "title": title,
                "date": date,
                "site": base_url
            })
    return articles

# Fonction pour extraire la date de publication d'un article (à personnaliser selon les sites)
def extract_article_date(soup):
    # Cherche une balise <time> pour extraire la date
    date_tag = soup.find('time')
    if date_tag and date_tag.get('datetime'):
        return date_tag.get('datetime')
    # Exemples d'autres méthodes pour extraire la date
    date_tag = soup.find('meta', {'property': 'article:published_time'})
    if date_tag and date_tag.get('content'):
        return date_tag.get('content')
    date_tag = soup.find('meta', {'name': 'date'})
    if date_tag and date_tag.get('content'):
        return date_tag.get('content')
    return "Date non trouvée"

# Fonction pour scraper les sites web et extraire les articles
def scrape_urls(urls):
    results = []
    for url in urls:
        try:
            response = fetch_web_page(url)
            content_type = response.headers.get('Content-Type', '').lower()

            if 'html' in content_type:
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = extract_article_info(soup, url)
                results.extend(articles)
            elif 'text' in content_type:
                text = response.text
                general_title = text[:50]  # Limiter à 50 caractères pour l'exemple
                results.append({
                    "url": url,
                    "title": general_title,
                    "date": "Date non disponible",
                    "site": url
                })
            else:
                print(f"Skipping URL {url} with content type {content_type}")

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as e:
            print(f"Failed to fetch or process {url}: {e}")
        finally:
            time.sleep(1)  # Délai pour éviter de surcharger le serveur

    return results

# Scraper les sites web
articles = scrape_urls(urls)

# Sauvegarder les résultats dans un fichier CSV
df = pd.DataFrame(articles)
df.to_csv("extracted_articles.csv", index=False)

print("Les articles avec leurs titres, dates et noms de sites ont été sauvegardés dans 'extracted_articles.csv'.")

# Affichage des articles extraits pour vérification
for article in articles:
    print(f"Site: {article['site']}")
    print(f"Titre: {article['title']}")
    print(f"URL: {article['url']}")
    print(f"Date: {article['date']}")
    print("\n")

