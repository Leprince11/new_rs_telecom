import random
import re
import time
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.db.models import Q
import requests
from chromedriver_py import binary_path # Cette ligne importe le chemin du binaire
import urllib.parse
from ..models import Leads
# from tests.models import Leads

# Liste de différents User-Agents
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
]

# Fonction pour obtenir le HTML avec un User-Agent aléatoire
def get_html_special(url):
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            print(f'Failed to retrieve {url}. Status code: {response.status_code}')
            return None
    except Exception as e:
        print(f"An error occurred while fetching {url}: {e}")
        return None
    finally:
        time.sleep(random.uniform(1, 3))

# Fonction pour extraire le nom de l'entreprise depuis l'URL
def extract_company_name_from_url(url):
    match = re.search(r'at-([^-]+)-(\d+)', url)
    if match:
        company_name = match.group(1).replace('-', ' ')
        return company_name
    return None

# Fonction pour extraire la description du poste depuis le contenu HTML
def extract_job_description(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        job_description_section = soup.find('section', class_='show-more-less-html')
        if job_description_section:
            job_description = job_description_section.get_text(separator="\n", strip=True)
            return job_description
        else:
            return "No job description found."
    except Exception as e:
        print(f"An error occurred while parsing job description: {e}")
        return "Error extracting job description."

# Fonction pour créer un driver Selenium avec des options aléatoires
def create_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'user-agent={random.choice(user_agents)}')
    service = Service(executable_path=binary_path)
    return webdriver.Chrome(service=service, options=options)

# Fonction pour rechercher des offres d'emploi sur LinkedIn
def fetch_job_listings_selenium(keywords, location, time_frame, max_jobs=10):
    print('dans fetch avant driver')
    try :
        base_url = "https://www.linkedin.com/jobs/search/"
        time_options = {
            'mois dernier': 'r2592000',
            'semaine dernière': 'r604800',
            'dernières 24h': 'r86400'
        }
        params = {
            "keywords": keywords,
            "location": location,
            "f_TPR": time_options[time_frame],
            "distance": '25'
        }
        search_url = f"{base_url}?keywords={params['keywords']}&location={params['location']}&f_TPR={params['f_TPR']}&distance={params['distance']}"
        driver = create_driver()
        print('dans fetch apres driver')
        driver.get(search_url)
        
        print('dans fetch apres driver 1')
        time.sleep(random.uniform(3, 5))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        job_cards = soup.find_all("div", class_="base-search-card")
        
        print('dans fetch apres driver 2')

        company_job_pairs = []

        for job_card in job_cards[:max_jobs]:  # Limite le nombre de jobs scrappés
            job_id = job_card.get("data-entity-urn")
            job_title_tag = job_card.find("h3", class_="base-search-card__title")
            company_tag = job_card.find("h4", class_="base-search-card__subtitle")
            datetime_tag = job_card.find("time", class_="job-search-card__listdate--new")
            job_link_tag = job_card.find("a", class_="base-card__full-link")
            
            if job_id and job_title_tag and company_tag and datetime_tag and job_link_tag:
                job_title = job_title_tag.text.strip()
                company_name = company_tag.text.strip()
                datetime_value = datetime_tag.get('datetime')
                job_link = job_link_tag['href']
                company_job_pairs.append((company_name, job_title, job_id, datetime_value, job_link))
                
        company_counts = {}
        for name, _, _, _, _ in company_job_pairs:
            if name in company_counts:
                company_counts[name] += 1
            else:
                company_counts[name] = 1
        
        driver.quit()
        return company_job_pairs, company_counts, search_url
    except Exception as e:
        print(e)

# Fonction pour afficher les détails des offres d'emploi depuis l'URL de recherche
def fetch_and_display_job_details_from_search_url(search_url, max_jobs=10):
    try:
        starttime = time.time()
        driver = create_driver()
        print("driver creee")
        driver.get(search_url)
        print("driver creee et passee")
        time.sleep(random.uniform(5, 7))  # Augmentation du temps d'attente initial
        print("pb timeout")

        job_elements = driver.find_elements(By.CSS_SELECTOR, "ul.jobs-search__results-list li")
        job_details = []

        for index in range(min(len(job_elements), max_jobs)):
            success = False
            error_counter = 0

            while not success and error_counter < 3:
                try:
                    job_elements = driver.find_elements(By.CSS_SELECTOR, "ul.jobs-search__results-list li")
                    if index >= len(job_elements):
                        print(f"Index {index} out of range after re-fetching job elements.")
                        break

                    job_link = job_elements[index].find_element(By.CSS_SELECTOR, "a.base-card__full-link")
                    driver.execute_script("arguments[0].click();", job_link)
                    time.sleep(random.uniform(5, 7))  # Augmentation du temps d'attente après le clic

                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    recruiter_div = soup.find('div', class_='message-the-recruiter')
                    recruiter_name_tag = recruiter_div.find('span', class_='sr-only') if recruiter_div else None
                    recruiter_name = recruiter_name_tag.text.strip() if recruiter_name_tag else None
                    recruiter_profile_link_tag = recruiter_div.find('a', class_='message-the-recruiter__cta') if recruiter_div else None
                    recruiter_profile_link = recruiter_profile_link_tag['href'] if recruiter_profile_link_tag and "https://" in recruiter_profile_link_tag['href'] and "linkedin" in recruiter_profile_link_tag['href'] else None

                    job_description_div = soup.find('div', class_='show-more-less-html__markup')
                    job_description = job_description_div.text.strip() if job_description_div else None

                    job_details.append((recruiter_name, job_description, recruiter_profile_link))
                    success = True
                    driver.back()
                    time.sleep(random.uniform(7, 10))  # Augmentation du temps d'attente avant de retourner à la page précédente

                except Exception as e:
                    print(f"Error processing job {index + 1}: {e}")  # index list out of range car les jobs n'ont pas pu être récupérés
                    error_counter += 1
                    time.sleep(random.uniform(5, 7))  # Augmentation du temps d'attente en cas d'erreur
    except Exception as x :
        print(x)
    finally:
        driver.quit()      
    endtime = time.time()
    print(f"Temps total d'exécution : {endtime - starttime} secondes")
    return job_details

# Fonction pour rechercher une entreprise dans la base de données
def search_in_database(company_name):
    try:
        companies = Leads.objects.filter(Q(nom__icontains=company_name)).exclude(
            secteur_activite__in=['non mentionné', 'null'],
            taille_entreprise__in=['non mentionné', 'null']
        )
        for company_info in companies:
            return {
                'site_web': 'non mentionné',
                'secteur': company_info.secteur_activite,
                'taille': company_info.taille_entreprise,
                'siege_social': 'non mentionné',
                'type': 'non mentionné',
                'fondee_en': 'non mentionné',
                'specialisations': 'non mentionné'
            }
    except Exception as e:
        print(f"Database search failed: {e}")
    return None

# Fonction pour obtenir les informations de l'entreprise sur LinkedIn
def get_linkedin_company_info(company_name, max_attempts=3):
    company_info = search_in_database(company_name)
    if company_info:
        return company_info
    
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        try:
            driver = create_driver()
            search_url = f"https://www.google.com/search?q={company_name}+site:linkedin.com/company"
            driver.get(search_url)
            time.sleep(random.uniform(3, 5))

            search_results = driver.find_elements(By.CSS_SELECTOR, 'div.yuRUbf a')
            if search_results:
                company_url = search_results[0].get_attribute('href')
                driver.get(company_url)
                time.sleep(random.uniform(3, 5))

                try:
                    about_tab = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[@data-control-name='page_member_main_nav_about_tab']"))
                    )
                    driver.execute_script("arguments[0].click();", about_tab)
                    time.sleep(random.uniform(3, 5))
                except Exception as e:
                    print("About tab not found or not clickable:", e)

                soup = BeautifulSoup(driver.page_source, 'html.parser')

                try:
                    about_section = driver.find_element(By.XPATH, "//h2[contains(text(),'À propos')]")
                    driver.execute_script("arguments[0].scrollIntoView(true);", about_section)
                except Exception as e:
                    print("About section not found. Exiting.")
                    driver.quit()
                    continue

                content_container = soup.find('div', class_='core-section-container__content break-words')
                if not content_container:
                    print("Content container not found. Exiting.")
                    driver.quit()
                    continue

                def extract_info(label, data_test_id):
                    dt_element = content_container.find('div', {'data-test-id': data_test_id})
                    if dt_element:
                        dd_element = dt_element.find('dd')
                        if dd_element:
                            info = dd_element.get_text(strip=True)
                            return info
                    return None

                company_info = {
                    'site_web': extract_info('Site web', 'about-us__website'),
                    'secteur': extract_info('Secteur', 'about-us__industry'),
                    'taille': extract_info('Taille de l’entreprise', 'about-us__size'),
                    'siege_social': extract_info('Siège social', 'about-us__headquarters'),
                    'type': extract_info('Type', 'about-us__organizationType'),
                    'fondee_en': extract_info('Fondée en', 'about-us__foundedOn'),
                    'specialisations': extract_info('Domaines', 'about-us__specialties')
                }

                if company_info.get('secteur') and company_info.get('secteur') not in ('non mentionné', 'null', None) and \
                   company_info.get('taille') and company_info.get('taille') not in ('non mentionné', 'null', None):
                    driver.quit()
                    return company_info
            else:
                print("Company URL not found.")

            driver.quit()
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            time.sleep(random.uniform(3, 5))

    return {
        'site_web': 'non mentionné',
        'secteur': 'non mentionné',
        'taille': 'non mentionné',
        'siege_social': 'non mentionné',
        'type': 'non mentionné',
        'fondee_en': 'non mentionné',
        'specialisations': 'non mentionné'
    }


def convert_date(date_str):
    try:
        # Nettoyer la chaîne de caractères pour éliminer les espaces insécables
        clean_date_str = date_str.replace('\xa0', '').strip()
        return datetime.strptime(clean_date_str, '%d/%m/%Y').date()
    except ValueError as e:
        print(f"Erreur lors de la conversion de la date: {e}")
        return None

def build_url(base_url, location, keywords, salary_min, salary_max):
    params = {
        'lieux': location,
        'motsCles': keywords,
        'salaireMinimum': salary_min,
        'salaireMaximum': salary_max
    }
    query_string = urllib.parse.urlencode(params)
    return f"{base_url}?{query_string}"

def scraping_apec(base_url, location, keywords, salary_min, salary_max):
    url = build_url(base_url, location, keywords, salary_min, salary_max)
    driver = create_driver()
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    offers = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'card-offer')))

    data = []
    for offer in offers:
        try:
            parent_a = offer.find_element(By.XPATH, 'ancestor::a')
            detail_url = parent_a.get_attribute('href')

            company_name = offer.find_element(By.CLASS_NAME, 'card-offer__company').text
            job_title = offer.find_element(By.CLASS_NAME, 'card-title').text
            job_description = offer.find_element(By.CLASS_NAME, 'card-offer__description').text
            salary = offer.find_element(By.XPATH, './/ul[@class="details-offer"]/li[1]').text if offer.find_elements(By.XPATH, './/ul[@class="details-offer"]/li[1]') else 'Non spécifié'
            contract_type = offer.find_element(By.XPATH, './/ul[@class="details-offer important-list"]/li[1]').text
            location = offer.find_element(By.XPATH, './/ul[@class="details-offer important-list"]/li[2]').text
            publication_date_str = offer.find_element(By.XPATH, './/ul[@class="details-offer important-list"]/li[3]').text

            publication_date = convert_date(publication_date_str)

            if not publication_date:
                continue

            # Scrape job details page
            job_details = scrape_apec_job_details(detail_url)
            full_description = f"{job_description}\n\nProfil recherché:\n{job_details['profil_recherche']}"

            # Check if the lead already exists
            lead, created = Leads.objects.update_or_create(
                nom=company_name,
                nom_offre=job_title,
                defaults={
                    'nombre_offres': 1,
                    'localisation_du_lead': location,
                    'description_job': full_description,
                    'source_lead': 'apec',
                    'date_publication_offre': publication_date,
                    'type_contrat': contract_type,
                    'lien_vers_lead': detail_url,
                    'porteur_lead': job_details['charge_recrutement']
                }
            )

            if created:
                print(f"New lead created: {company_name} - {job_title}")
            else:
                print(f"Existing lead updated: {company_name} - {job_title}")

            offer_data = {
                'company_name': company_name,
                'job_title': job_title,
                'job_description': full_description,
                'salary': salary,
                'contract_type': contract_type,
                'location': location,
                'publication_date': publication_date_str,
                'detail_url': detail_url,
                'porteur_lead': job_details['charge_recrutement'],
                'profil_recherche': job_details['profil_recherche']
            }
            data.append(offer_data)
        except Exception as e:
            print(f"Erreur lors du scraping de l'offre: {e}")
    
    print(data)
    driver.quit()
    return data

def scrape_apec_job_details(url):
    driver = create_driver()
    driver.get(url)
    
    # Attendre que la page soit complètement chargée
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'details-post')))
    
    # Imprimer le code source de la page pour le débogage
    print(driver.page_source)
    
    # Extraire le contenu de la page
    job_details = {}
    
    # Descriptif du poste
    try:
        job_details['descriptif_de_mission'] = driver.find_element(By.XPATH, '//div[@class="details-post"]/h4[text()="Descriptif du poste"]/following-sibling::p').text.strip()
    except Exception as e:
        job_details['descriptif_de_mission'] = 'Non spécifié'
        print(f"Erreur lors de l'extraction du descriptif de mission: {e}")

    # Profil recherché
    try:
        job_details['profil_recherche'] = driver.find_element(By.XPATH, '//h4[text()="Profil recherché"]/following-sibling::p').text.strip()
    except Exception as e:
        job_details['profil_recherche'] = 'Non spécifié'
        print(f"Erreur lors de l'extraction du profil recherché: {e}")

    # Entreprise
    try:
        job_details['entreprise'] = driver.find_element(By.XPATH, '//h4[text()="Entreprise"]/following-sibling::p').text.strip()
    except Exception as e:
        job_details['entreprise'] = 'Non spécifié'
        print(f"Erreur lors de l'extraction de l'entreprise: {e}")

    # Chargé de recrutement
    try:
        charge_recrutement_element = driver.find_element(By.XPATH, '//p[strong[text()="Personne en charge du recrutement"]]')
        job_details['charge_recrutement'] = charge_recrutement_element.text.replace('Personne en charge du recrutement\n', '').strip()
    except Exception as e:
        job_details['charge_recrutement'] = 'Non spécifié'
        print(f"Erreur lors de l'extraction du chargé de recrutement: {e}")

    driver.quit()
    
    return job_details

# # URL de l'offre d'emploi
# url = 'https://www.apec.fr/candidat/recherche-emploi.html/emploi/detail-offre/174165620W?lieux=75&motsCles=d%C3%A9veloppeur&salaireMinimum=20&salaireMaximum=200&typesConvention=143684&typesConvention=143685&typesConvention=143686&typesConvention=143687&typesConvention=143706&selectedIndex=0&page=0'

# # Appel de la fonction
# job_details = scrape_apec_job_details(url)

# # Affichage des résultats
# for key, value in job_details.items():
#     print(f"{key}: {value}")