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
from tests.models import Leads
import requests
from chromedriver_py import binary_path # Cette ligne importe le chemin du binaire

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