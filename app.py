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


# Start a session
session = requests.Session()

# Initialisation automatique du driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

driver.get("https://www.google.com")

first_url_route ="https://connect.garmin.com/fr/"

driver.get(first_url_route)


def connexion(url):

  try:
    cookie_button = driver.find_element(
        By.CSS_SELECTOR, "a[data-button-key='accept_all']"
    )
    driver.execute_script("arguments[0].click();", cookie_button)

  except:
    pass  

  button = WebDriverWait(driver, 10).until(
      EC.presence_of_element_located(
          (By.CSS_SELECTOR, "._1omhclk7._1omhclk1._1omhclk0")
      )
  )

  driver.execute_script("arguments[0].click();", button)

  print("Clic réussi sur le bouton de connexion !")
  input(" waiting ")







def main():

    try:
        connexion(first_url_route)
        global url
        url = driver.current_url
    except RuntimeError:
        print("404")
    
    
if __name__ == "__main__":
    main()
