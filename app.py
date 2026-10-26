from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchFrameException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
import time


# Initialisation automatique avec undetected-chromedriver
driver = uc.Chrome(version_main=155)

# Vos identifiants
my_email = "clempgt13@gmail.com"
my_pswrd = "Clemlebgdu27"
# Optionnel : passer par Google ou aller directement sur Garmin
driver.get("https://www.google.com")

first_url_route = "https://connect.garmin.com/fr/"
driver.get(first_url_route)



def handle_trustarc_banner():
  try:
    print("Recherche et nettoyage forcé du bandeau TrustArc...")
    time.sleep(3)  # On laisse le temps à la page de stabiliser son DOM

    # Script JS global amélioré qui cherche et supprime le bandeau partout (même dans les iframes si accessible, ou sur la page principale)
    script_suppression = """
        // 1. Suppression sur la page principale
        var banners = document.querySelectorAll('div.mainContent, div.gdpr, div[aria-labelledby="cookieMainHeader"], div[id*="truste"]');
        var removedCount = 0;
        banners.forEach(function(el) {
            el.remove();
            removedCount++;
        });

        // 2. Suppression dans les iframes de la page principale
        var iframes = document.querySelectorAll('iframe');
        iframes.forEach(function(iframe) {
            try {
                var innerDoc = iframe.contentDocument || iframe.contentWindow.document;
                var innerBanners = innerDoc.querySelectorAll('div.mainContent, div.gdpr, div[aria-labelledby="cookieMainHeader"], div[id*="truste"]');
                innerBanners.forEach(function(el) {
                    el.remove();
                    removedCount++;
                });
            } catch(e) {
                // Erreur de cross-origin potentielle, ignorée silencieusement
            }
        });

        return removedCount;
        """

    resultat = driver.execute_script(script_suppression)
    if resultat and resultat > 0:
      print(f"Bandeau(x) de cookies supprimé(s) avec succès ! ({resultat})")
    else:
      print("Aucun bandeau trouvé à ce moment précis.")

  except Exception as e:
    print(f"Erreur lors du nettoyage global : {e}")
    print(f"Erreur lors du nettoyage global : {e}")

def connexion(url):
  driver.get(url)
  time.sleep(2)  # Petite pause pour laisser la page charger

  # Gestion des cookies
  try:
      handle_trustarc_banner()
  except:
      print("404")

  # Clic sur le bouton de connexion initial sur la page d'accueil
  try:
    button = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "._1omhclk7._1omhclk1._1omhclk0")
        )
    )
    driver.execute_script("arguments[0].click();", button)
    print("Clic réussi sur le bouton de connexion initial !")
  except:
    print("Bouton de connexion initial non trouvé ou déjà sur la page.")


def auth(url):
  try:
    # Petite pause pour s'assurer que le formulaire de login est affiché
    time.sleep(2)

    email = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "email"))
    )
    email.clear()
    email.send_keys(my_email)

    pswrd = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    pswrd.clear()
    pswrd.send_keys(my_pswrd)

    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[data-testid='g__button']")
        )
    )

    driver.execute_script("arguments[0].click();", submit_button)
    print("Formulaire soumis avec succès !")

  except Exception as e:
    print(f"Erreur dans auth() : {e}")



def main():
  try:
    connexion(first_url_route)
    new_url = driver.current_url
    auth(new_url)
    new_url = driver.current_url
    time.sleep(8)
    handle_trustarc_banner()
    input("input : ")
  except Exception as e:
    print(f"Erreur globale : {e}")
  finally:
    driver.quit()


if __name__ == "__main__":
  main()