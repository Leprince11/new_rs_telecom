from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

# Liste des user agents
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
]

def create_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'user-agent={random.choice(user_agents)}')
    return webdriver.Chrome(options=options)

def get_recruteur(joblink):
    success = False
    while not success:
        driver = create_driver()
        try:
            driver.get(joblink)
            wait = WebDriverWait(driver, 10)
            recruiter_div = wait.until(EC.presence_of_element_located((By.XPATH, '//a[contains(@class, "app-aware-link") and contains(@aria-label, "Voir le profil de")]')))

            if recruiter_div:
                recruiter_name = recruiter_div.find_element(By.XPATH, './/span[@class="t-black jobs-poster__name"]').text.strip()
                recruiter_profile_link = recruiter_div.get_attribute('href')
                success = True
            else:
                recruiter_name = 'non mentionné'
                recruiter_profile_link = 'non mentionné'
        except Exception as e:
            print(f"Erreur lors de l'extraction du recruteur : {e}")
            recruiter_name = 'non mentionné'
            recruiter_profile_link = 'non mentionné'
        finally:
            driver.quit()

    return recruiter_name, recruiter_profile_link

# Exemple d'utilisation
joblink = "https://www.linkedin.com/jobs/view/ing%C3%A9nieur-linux-embarqu%C3%A9-h-f-at-seyos-3916832197/?trackingId=RU7D90Y02dDODz57mCAxNA%3D%3D&refId=cOTEAm8PJLcZmJ3zlswqhQ%3D%3D&pageNum=0&position=3&trk=public_&originalSubdomain=fr"
recruiter_name, recruiter_profile_link = get_recruteur(joblink)
print(f"Recruteur: {recruiter_name}, Profil LinkedIn: {recruiter_profile_link}")
