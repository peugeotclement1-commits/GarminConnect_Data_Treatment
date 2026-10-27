import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from handle_cookies import handle_trustarc_banner

# Vos identifiants et routes par défaut
MY_EMAIL = ""
MY_PSWRD = ""
FIRST_URL_ROUTE = "https://connect.garmin.com/fr/"

# Instance globale de driver partagée
driver = None


def get_driver(version_main=155):
  """Retourne l'instance active du driver, ou en crée une nouvelle."""
  global driver
  if driver is None:
    driver = uc.Chrome(version_main=version_main)
  return driver


def connexion(d=None, url=FIRST_URL_ROUTE):
  """Accède à la page d'accueil Garmin et clique sur le bouton de connexion."""
  d = d or get_driver()

  try:
    d.get("https://www.google.com")
  except Exception:
    pass

  d.get(url)
  time.sleep(2)  # Pause pour laisser la page charger

  # Gestion des cookies initiaux
  try:
    handle_trustarc_banner(d)
  except Exception as e:
    print(f"Info cookies connexion initiale : {e}")

  # Clic sur le bouton de connexion initial sur la page d'accueil
  try:
    button = WebDriverWait(d, 5).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "._1omhclk7._1omhclk1._1omhclk0")
        )
    )
    d.execute_script("arguments[0].click();", button)
    print("Clic réussi sur le bouton de connexion initial !")
  except Exception:
    print("Bouton de connexion initial non trouvé ou déjà sur la page.")

  return d


def auth(d=None, email=MY_EMAIL, password=MY_PSWRD):
  """Remplit le formulaire d'authentification Garmin SSO et valide."""
  d = d or get_driver()

  try:
    time.sleep(2)  # Pause pour s'assurer que le formulaire de login est affiché

    email_field = WebDriverWait(d, 10).until(
        EC.presence_of_element_located((By.ID, "email"))
    )
    email_field.clear()
    email_field.send_keys(email)

    pswrd_field = WebDriverWait(d, 10).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    pswrd_field.clear()
    pswrd_field.send_keys(password)

    submit_button = WebDriverWait(d, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[data-testid='g__button']")
        )
    )

    d.execute_script("arguments[0].click();", submit_button)
    print("Formulaire soumis avec succès !")

    # Attendre la redirection post-connexion (sortie du SSO Garmin)
    print("Attente de la redirection vers l'application Garmin...")
    try:
      WebDriverWait(d, 15).until(
          lambda drv: "sso.garmin.com" not in drv.current_url
      )
      print(f"Redirection réussie vers : {d.current_url}")
    except TimeoutException:
      print("Délai de redirection dépassé, poursuite...")

  except Exception as e:
    print(f"Erreur dans auth() : {e}")

  return d


def naviguer(d=None, timeout=15):
  """Gère la page après connexion et accepte les cookies sur l'application."""
  d = d or get_driver()
  print("Début de naviguer()...")
  time.sleep(2)  # Pause pour laisser le SPA de Garmin Connect charger ses composants

  # Clic automatique sur les cookies s'ils apparaissent (DOM, Shadow DOM, iframes)
  handle_trustarc_banner(d, timeout=timeout)
  return d


def se_connecter(d=None, email=MY_EMAIL, password=MY_PSWRD, url=FIRST_URL_ROUTE):
  """Fonction tout-en-un pour effectuer la connexion complète à Garmin Connect."""
  d = d or get_driver()
  connexion(d, url)
  auth(d, email, password)
  naviguer(d)
  return d
