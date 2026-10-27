import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from connexion import se_connecter, get_driver, connexion, auth, naviguer


def ensure_connected(d=None):
  """Vérifie si le driver est connecté, sinon lance la connexion complète."""
  d = d or get_driver()
  if "connect.garmin.com" not in d.current_url or "sso.garmin.com" in d.current_url:
    d = se_connecter(d)
  return d


def get_who_data(d=None):
  """Accède au profil utilisateur et récupère dynamiquement les statistiques et la forme."""
  d = ensure_connected(d)

  # Dictionnaires pour stocker les données
  pas = {}
  cap = {}
  cyclisme = {}
  forme = {}

  try:
    if "profile" not in d.current_url:
      try:
        gotoprofile = WebDriverWait(d, 10).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "[class*='UserProfileMenu_avatar'], [class*='avatar'], button[aria-label*='profil' i]",
                )
            )
        )
        d.execute_script("arguments[0].click();", gotoprofile)
        time.sleep(1)

        displayprofile = WebDriverWait(d, 5).until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Afficher mon profil"))
        )
        d.execute_script("arguments[0].click();", displayprofile)
        print("Page de profil affichée via le menu !")
      except Exception:
        print("Accès direct à la page de profil...")
        d.get("https://connect.garmin.com/modern/profile")

    # Attente que les composants de statistiques et profil soient chargés dans le DOM
    WebDriverWait(d, 10).until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "[class*='statsList'], [class*='UserStats_statsGroup']",
            )
        )
    )
    time.sleep(1)

    # Extraction dynamique via JavaScript (gère Records personnels et Composants de Profil comme Forme)
    js_extract = """
        var result = { pas: {}, cap: {}, cyclisme: {}, forme: {} };
        // Sélectionne tous les titres de sections (Records personnels et Profil/Forme)
        var headings = document.querySelectorAll("h6[class*='statsHeading']");

        headings.forEach(function(h) {
            var cat = (h.innerText || h.textContent || "").trim().toLowerCase();
            
            // Ignorer la natation
            if (cat.includes("natation") || cat.includes("swimming")) {
                return;
            }
            
            var targetKey = null;
            if (cat.includes("pas") || cat.includes("step")) {
                targetKey = "pas";
            } else if (cat.includes("course") || cat.includes("running") || cat.includes("cap")) {
                targetKey = "cap";
            } else if (cat.includes("cyclisme") || cat.includes("cycling") || cat.includes("vélo") || cat.includes("velo")) {
                targetKey = "cyclisme";
            } else if (cat.includes("forme") || cat.includes("fitness")) {
                targetKey = "forme";
            }
            
            // Trouver la liste ul suivante
            var nextEl = h.nextElementSibling;
            while (nextEl && nextEl.tagName.toLowerCase() !== "ul") {
                nextEl = nextEl.nextElementSibling;
            }
            
            if (nextEl && nextEl.tagName.toLowerCase() === "ul" && targetKey) {
                var lis = nextEl.querySelectorAll("li");
                lis.forEach(function(li) {
                    var labelEl = li.querySelector("span[class*='statLabel']");
                    var dataEl = li.querySelector("span[class*='statData']");
                    if (labelEl && dataEl) {
                        var label = (labelEl.innerText || labelEl.textContent || "").trim().replace(/\\u00a0/g, ' ');
                        var val = (dataEl.innerText || dataEl.textContent || "").trim().replace(/\\u00a0/g, ' ');
                        if (label) {
                            result[targetKey][label] = val;
                        }
                    }
                });
            }
        });

        return result;
        """

    data_extracted = d.execute_script(js_extract)
    if data_extracted:
      pas.update(data_extracted.get("pas", {}))
      cap.update(data_extracted.get("cap", {}))
      cyclisme.update(data_extracted.get("cyclisme", {}))
      forme.update(data_extracted.get("forme", {}))

    # Fallback Selenium si JS n'a rien retourné
    if not (pas or cap or cyclisme or forme):
      headings = d.find_elements(
          By.CSS_SELECTOR, "h6[class*='statsHeading']"
      )
      for h in headings:
        cat = h.text.strip().lower()
        if "natation" in cat or "swimming" in cat:
          continue

        target = None
        if "pas" in cat or "step" in cat:
          target = pas
        elif "course" in cat or "running" in cat:
          target = cap
        elif "cyclisme" in cat or "cycling" in cat or "vélo" in cat:
          target = cyclisme
        elif "forme" in cat or "fitness" in cat:
          target = forme

        if target is not None:
          try:
            ul = h.find_element(
                By.XPATH,
                "following-sibling::ul[contains(@class, 'statsList')][1]",
            )
            lis = ul.find_elements(By.TAG_NAME, "li")
            for li in lis:
              label = (
                  li.find_element(
                      By.CSS_SELECTOR,
                      "span[class*='statLabel']",
                  )
                  .text.strip()
                  .replace("\xa0", " ")
              )
              val = (
                  li.find_element(
                      By.CSS_SELECTOR,
                      "span[class*='statData']",
                  )
                  .text.strip()
                  .replace("\xa0", " ")
              )
              if label:
                target[label] = val
          except Exception:
            pass

    print("Extraction des données de profil et de forme terminée avec succès !")

  except Exception as e:
    print(f"Erreur lors de l'extraction des données de profil : {e}")

  return {
      "pas": pas,
      "cap": cap,
      "cyclisme": cyclisme,
      "forme": forme,
  }



if __name__ == "__main__":
  # Permet d'exécuter directement fetchdata.py pour tester la connexion et le fetch
  print("Lancement direct de fetchdata...")
  driver = se_connecter()

  donnees_profil = get_who_data(driver)
  print("\n--- Données profil obtenues ---")
  print("Pas :", donnees_profil["pas"])
  print("Course à pied :", donnees_profil["cap"])
  print("Cyclisme :", donnees_profil["cyclisme"])
  print("Forme :", donnees_profil["forme"])

  input("\nAppuyez sur Entrée pour quitter...")
