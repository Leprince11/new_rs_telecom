from celery import shared_task
import requests
from django.middleware.csrf import get_token
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task
def run_start_scraping():
    try:
        logger.info("Starting the scraping task")
        print("Starting the scraping task")
        
        # Obtenir le jeton CSRF en envoyant une requête GET
        session = requests.Session()
        response = session.get(f'{settings.BASE_URL}/rstelecom/start-scraping/')
        csrf_token = response.cookies['csrftoken']
        
        # Envoyer la requête POST avec le jeton CSRF
        headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token,
        }
        data = {
            'nom': 'Paris',
            'region': 'Île-de-France',
            'keywords': ['keyword1', 'keyword2'],
            'time_frame': 'last_24_hours'
        }
        response = session.post(f'{settings.BASE_URL}/rstelecom/start-scraping/', json=data, headers=headers)
        
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response content: {response.content.decode('utf-8')}")

        if response.status_code != 200:
            logger.error(f"Failed with status code: {response.status_code}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")