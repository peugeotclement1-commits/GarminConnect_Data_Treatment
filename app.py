from selenium import webdriver
from selenium.webdriver.common.by import By
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


def cookies(url):

     link=WebDriverWait(driver, 10).until(
          EC.element_to_be_clickable(By.PARTIAL_LINK_TEXT, "Tout accepter")
     )

     link.click()


def connexion(url):

    cookies(url)
    button = WebDriverWait(driver, 10)

    button=driver.find_element_by_css_selector("_1omhclk7 _1omhclk1 _1omhclk0")

    button.click()







def main():

    try:
        connexion(first_url_route)
        global url
        url = driver.current_url
    except RuntimeError:
        print("404")
    
    
    if __name__ == "__main__":
	    main()
