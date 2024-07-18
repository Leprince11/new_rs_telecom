from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random

# Informations de connexion LinkedIn
LINKEDIN_USERNAME = "kaosskills56@gmail.com"
LINKEDIN_PASSWORD = "linkedin2024!!!"

# Liste des user agents
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
]

def create_driver():
    options = Options()
    options.add_argument('--headless')  # Exécute le navigateur en mode headless (sans interface graphique)
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument(f'user-agent={random.choice(user_agents)}')
    # Désactiver WebRTC
    options.add_argument('--disable-features=WebRtcHideLocalIpsWithMdns')
    options.add_argument('--disable-webrtc')
    
    driver = webdriver.Chrome(options=options)
    return driver

def login_to_linkedin(driver):
    print("Navigating to LinkedIn login page...")
    driver.get("https://www.linkedin.com/login")
    time.sleep(random.uniform(2, 5))
    
    print("Entering username and password...")
    username_input = driver.find_element(By.ID, "username")
    password_input = driver.find_element(By.ID, "password")
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")

    username_input.send_keys(LINKEDIN_USERNAME)
    password_input.send_keys(LINKEDIN_PASSWORD)
    login_button.click()
    time.sleep(random.uniform(5, 10))

def is_logged_in(driver):
    print("Checking if login was successful...")
    try:
        # Vérifiez la présence d'un élément unique disponible uniquement après connexion
        profile_icon = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img.global-nav__me-photo"))
        )
        print("Login successful!")
        return True
    except Exception as e:
        print(f"Error checking login status: {e}")
        return False

def send_message_to_recruiter(driver, recruiter_profile_link, message):
    print(f"Navigating to recruiter's profile: {recruiter_profile_link}...")
    driver.get(recruiter_profile_link)
    time.sleep(random.uniform(5, 10))

    try:
        print("Waiting for the profile action div...")
        action_div = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.entry-point.profile-action-compose-option"))
        )

        print("Profile action div found. Parsing the page with BeautifulSoup...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        message_button = soup.find('button', {'aria-label': lambda x: x and x.startswith('Envoyer un message à')})
        
        if message_button:
            print("Message button found. Clicking the button...")
            button_id = message_button['id']
            driver.execute_script(f"document.getElementById('{button_id}').click();")
            time.sleep(random.uniform(5, 10))
            
            print("Waiting for the message input to appear...")
            message_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.msg-form__contenteditable"))
            )
            
            print("Message input found. Entering the message...")
            message_input.send_keys(message)
            
            print("Waiting for the send button to be clickable...")
            send_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.msg-form__send-button"))
            )
            
            print("Send button found. Clicking the send button...")
            send_button.click()
            time.sleep(random.uniform(5, 10))
            print("Message sent successfully!")
            return True

        else:
            print("Message button not found.")
            return False

    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def main():
    recruiter_profile_link = "https://www.linkedin.com/in/ptrotin/"
    message = "Bonjour, je suis intéressé par vous , pour une offre d'alternance pourriez vous m'en dire plus sur vous pour un éventuel entretien , 5000 boules l'année?"

    driver = create_driver()
    login_to_linkedin(driver)
    
    if is_logged_in(driver):
        print("Connexion réussie")
        while not send_message_to_recruiter(driver, recruiter_profile_link, message):
            print("Échec de l'envoi du message, nouvelle tentative...")
            time.sleep(random.uniform(5, 10))
        print("Message envoyé avec succès")
    else:
        print("Échec de la connexion")

    driver.quit()

if __name__ == "__main__":
    main()
