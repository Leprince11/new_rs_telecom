import requests
from bs4 import BeautifulSoup
import re
import csv
from .linkedIn import *
import os
import pandas as pd 

import requests
import random
import time
from fake_useragent import UserAgent
from requests.exceptions import RequestException
from datetime import datetime
import asyncio

def get_html(url):
    try:
        # Générer un user-agent aléatoire
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random,
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.google.com'
        }
        
        # Délais aléatoires pour simuler le comportement humain
        time.sleep(random.uniform(1, 3))
        
        response = requests.get(url, headers=headers)
        
        print(f'Status Code: {response.status_code}')
        if response.status_code == 200:
            return response.text
        else:
            return None
    except RequestException as e:
        print(f"Error accessing URL: {e}")
        return None

# Exemple d'utilisation


    
def parse_html(html):
    results = {
        'taille': None,
        'secteur': None,
        'chiffre_d_affaires': None,
        'lien_site': None,
    }
    try:
        soup = BeautifulSoup(html, 'html.parser')

        # Récupération de la taille de l'entreprise
        size_div = soup.find('div', class_='css-18pwhsj e1wnkr790', text="Taille de l'entreprise")
        if size_div:
            next_size_div = size_div.find_next_sibling('div')
            if next_size_div:
                size_content = next_size_div.get_text(strip=True)
                results['taille'] = size_content
            else:
                print("Aucun div trouvé après le div 'Taille de l'entreprise'.")

        # Récupération du secteur
        sector_div = soup.find('div', class_='css-18pwhsj e1wnkr790', text='Secteur')
        if sector_div and sector_div.find_next_sibling('div'):
            results['secteur'] = sector_div.find_next_sibling('div').get_text(strip=True)

        # Récupération du chiffre d'affaires
        revenue_div = soup.find('div', class_='css-18pwhsj e1wnkr790', text="Chiffre d'affaires")
        if revenue_div and revenue_div.find_next_sibling('div'):
            results['chiffre_d_affaires'] = revenue_div.find_next_sibling('div').get_text(strip=True)

        # Récupération du lien du site
        link_div = soup.find('div', class_='css-18pwhsj e1wnkr790', text='Site Web')
        if link_div:
            next_link_div = link_div.find_next_sibling('div')
            if next_link_div:
                link_tag = next_link_div.find('a')
                if link_tag:
                    results['lien_site'] = link_tag['href']
                else:
                    print("Aucun lien trouvé après le div 'Site Web'.")
            else:
                print("Aucun div trouvé après le div 'Site Web'.")


    except Exception as e:
        print(f"Erreur lors du parsing HTML: {e}")
    
    return results

def extract_p_elements(html):
    results = {'nombre_employes': None}
    try:
        soup = BeautifulSoup(html, 'html.parser')
        target_div = soup.find('div', class_="css-brv7kd eu4oa1w0")
        if target_div:
            p_elements = target_div.find_all('p')
            if len(p_elements) >= 2:
                numbers_only = re.findall(r'\d+', p_elements[1].get_text(strip=True))
                results['nombre_employes'] = ''.join(numbers_only) + ' employés'
    except Exception as e:
        pass
    return results

def create_company_url(company_name):
    base_url = "https://fr.indeed.com/cmp/"
    return base_url + company_name.replace(" ", "-")



###################################################################

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import random

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.41',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
    ]
    return random.choice(user_agents)

def extract_all_links(linkedin_url, wait_time=10):
    user_agent = get_random_user_agent()

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={user_agent}")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(linkedin_url)

    job_links = []
    try:
        WebDriverWait(driver, wait_time).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.base-card')))
        job_cards = driver.find_elements(By.CSS_SELECTOR, 'div.base-csard')

        for job_card in job_cards:
            try:
                link_tag = job_card.find_element(By.CSS_SELECTOR, 'a.base-card__full-link')
                company_tag = job_card.find_element(By.CSS_SELECTOR, 'h4.base-search-card__subtitle')

                link = link_tag.get_attribute('href')
                company_name = company_tag.text.strip()

                job_links.append((link, company_name))
                print(f"Lien trouvé : {link}, Nom de l'entreprise : {company_name}")
            except NoSuchElementException as e:
                print(f"An element was not found in job card: {e}")
            except Exception as e:
                print(f"An error occurred while processing a job card: {e}")

    except TimeoutException:
        print("Timeout occurred while waiting for job cards.")
    except Exception as e:
        print(f"An error occurred while waiting for job cards: {e}")

    driver.quit()
    return job_links

def read_csv_data(filename):
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file,delimiter=';')
            return list(reader)
    except FileNotFoundError:
        return []





def write_to_csv(data, filename='donnees_leads.csv', delimiter=';'):
    fieldnames = ['nom', 'nombre_offres', 'nom_offre', 'localisation', 'taille', 'secteur', 'chiffre_d_affaires', 'job_description', 'porteur_lead', 'joblien']
    file_exists = os.path.exists(filename) and os.path.getsize(filename) > 0
    
    with open(filename, mode='a' if file_exists else 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter=delimiter)
        
        if not file_exists:
            dict_writer.writeheader()
        
        # Ensure 'index' column is removed before writing to CSV
        data_to_write = [{key: row[key] for key in fieldnames} for row in data]
        dict_writer.writerows(data_to_write)

##############################################################################################""
import pandas as pd

def load_and_filter_communes(file_path):
    """
    Charge un fichier Excel et filtre les colonnes 'Nom (minuscules)', 'Région', et 'code postal'.
    Enregistre ensuite les données filtrées dans un fichier CSV.

    Args:
        file_path (str): Chemin vers le fichier Excel.

    Returns:
        str: Chemin vers le fichier CSV généré.
    """
    # Lire le fichier Excel
    df = pd.read_excel(file_path)

    # Sélectionner les colonnes spécifiques
    filtered_df = df[['Nom (minuscules)', 'Région']]

    # Chemin vers le fichier CSV de sortie
    output_csv_path = 'nom_communes.csv'

    # Enregistrer les données filtrées dans un fichier CSV avec utf-8-sig pour conserver les caractères spéciaux
    filtered_df.to_csv(output_csv_path, sep=';', index=False, encoding='utf-8-sig')
    

    return output_csv_path

def construct_job_url(job_id, job_name, company):
    base_url = "https://www.linkedin.com/jobs/view/"
    job_name_formatted = job_name.lower().replace(' ', '-')
    company_formatted = company.lower().replace(' ', '-')
    return f"{base_url}{job_name_formatted}-at-{company_formatted}-{job_id}?trk=public_jobs_topcard-title"

def update_or_replace_entries(existing_data, new_data):
    # Convertir les données existantes en un DataFrame pandas
    df_existing = pd.DataFrame(existing_data)
    
    # Convertir les nouvelles données en DataFrame pandas
    df_new = pd.DataFrame(new_data)
    
    # Supprimer les lignes existantes qui ont le même 'nom' et 'nom_offre' que les nouvelles données
    if not df_existing.empty:
        df_existing.set_index(['nom', 'nom_offre'], inplace=True)
        df_new.set_index(['nom', 'nom_offre'], inplace=True)
        
        df_existing.drop(df_new.index, errors='ignore', inplace=True)
        
        # Combiner les anciennes et les nouvelles données
        df_updated = pd.concat([df_existing, df_new]).reset_index()
    else:
        df_updated = df_new.reset_index()

    return df_updated.to_dict('records')


from ..models import Leads
from django.utils import timezone
from django.db import IntegrityError

def insert_lead_to_db(data):
    try:
        lead, created = Leads.objects.update_or_create(
            nom=data['nom'],
            nom_offre=data['nom_offre'],
            defaults={
                'nombre_offres': data['nombre_offres'],
                'localisation_du_lead': data['localisation'],
                'porteur_lead': data.get('porteur_lead', 'non mentionné'),
                'url_profil_porteur_lead': data.get('lien_profil_linkedin', 'non mentionné'),
                'adresse_mail_de_contact': data.get('adresse_mail_de_contact', 'non@rstelecom.com'),
                'telephone': data.get('telephone', 'non mentionné'),
                'secteur_activite': data.get('secteur', 'non mentionné'),
                'taille_entreprise': data.get('taille', 'non mentionné'),
                'chiffre_d_affaires': data.get('chiffre_d_affaires', 'non mentionné'),
                'source_lead': data.get('source_lead', 'linkedIn'),
                'statut_du_lead': data.get('statut_du_lead', 'Nouveau'),
                'date_publication_offre': data.get('date_publication_offre', 'non mentionné'),
                'date_maj_lead': timezone.now(),
                'remarques': data.get('remarques', 'non mentionné'),
                'priorite': data.get('priorite', 'Moyen'),
                'description_job': data.get('job_description', 'non mentionné'),
                'lien_vers_lead': data.get('joblien', 'non mentionné'),
            }
        )
        if created:
            print(f"Lead {lead.nom} - {lead.nom_offre} created.")
        else:
            print(f"Lead {lead.nom} - {lead.nom_offre} updated.")
    except IntegrityError as e:
        print(f"Error creating or updating lead: {e}")
        
def write_to_db(data):
    for row in data:
        insert_lead_to_db(row)


# Fonction principale d'extraction
def main_extraction(keywords, location, time_frame):
    max_jobs = 10  # Limite à 10 jobs
    max_attempts = 3  # Nombre maximum de tentatives
    pause_duration = 5  # Durée de la pause en secondes
    attempts = 0
    new_data = []
    search_url = None  # Initialiser search_url

    while attempts < max_attempts and (new_data is None or not new_data):
        print('je suis à l\'intérieur de la fonction, tentative:', attempts + 1)
        
        try:
            company_job_pairs, company_counts, search_url = fetch_job_listings_selenium(keywords, location, time_frame, max_jobs)
            job_details = fetch_and_display_job_details_from_search_url(search_url, max_jobs)
            print(job_details)

            for (company, job_name, job_id, datetime_value, job_link), (recruiter_name, job_description, recruiter_profile_link) in zip(company_job_pairs, job_details):
                linkedin_info = get_linkedin_company_info(company)  # Appel de la nouvelle fonction pour obtenir les informations LinkedIn

                # Conversion de la chaîne datetime en objet date
                try:
                    date_publication = datetime.strptime(datetime_value, '%Y-%m-%d').date()
                except ValueError:
                    date_publication = None
                except Exception as m:
                    print(m)

                row_data = {
                    'nom': company,
                    'nombre_offres': company_counts.get(company, 1),
                    'nom_offre': job_name,
                    'localisation': location,
                    'taille': linkedin_info.get('taille', 'non mentionné'),
                    'secteur': linkedin_info.get('secteur', 'non mentionné'),
                    'chiffre_d_affaires': linkedin_info.get('fondee_en', 'non mentionné'),  # Placeholder pour chiffre d'affaires
                    'job_description': job_description,
                    'porteur_lead': recruiter_name if recruiter_name is not None else 'non mentionné',
                    'joblien': job_link,
                    'lien_profil_linkedin': recruiter_profile_link,
                    'date_publication_offre': date_publication
                }
                insert_lead_to_db(row_data)
                new_data.append(row_data)
            print(new_data)

            if new_data:
                return search_url, new_data
            else:
                attempts += 1
                print(f"new_data est vide. Tentative {attempts}. Attente de {pause_duration} secondes avant la nouvelle tentative.")
                time.sleep(pause_duration)

        except Exception as e:
            print(f"Le crash est causé par {e}")
            attempts += 1
            time.sleep(pause_duration)  # Attendre avant la prochaine tentative

    return search_url, new_data