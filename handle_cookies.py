import time
from selenium.webdriver.common.by import By


def handle_trustarc_banner(driver, timeout=15):
  """Recherche et clique automatiquement sur le bouton 'Tout accepter' des cookies.
  
  Gère le DOM principal, le Shadow DOM (TrustArc CCM Pro) et les iframes.
  """
  try:
    print(f"Recherche et clic automatique sur les cookies (timeout={timeout}s)... URL: {driver.current_url}")
    end_time = time.time() + timeout

    js_click_script = """
        function clickAcceptInRoot(root) {
            if (!root) return null;

            // 1. Sélecteurs précis (TrustArc, OneTrust, Garmin, etc.)
            var selectors = [
                "#truste-consent-button",
                ".trustarc-acceptall-btn",
                "a[data-button-key='accept_all']",
                "button[data-button-key='accept_all']",
                "[data-button-key='accept_all']",
                ".truste-button1",
                "button.call",
                "a.call",
                "button#onetrust-accept-btn-handler",
                "#truste-consent-buttons button",
                ".trustarc-banner-actions button",
                "button.truste-consent-button",
                "a.truste-consent-button",
                "div.mainContent a",
                "div.mainContent button",
                "div.gdpr a",
                "div.gdpr button",
                "div[id*='truste'] a",
                "div[id*='truste'] button",
                "div[id*='trustarc'] button",
                "div[id*='trustarc'] a",
                "div[class*='trustarc'] button",
                "div[class*='trustarc'] a",
                "div[aria-labelledby='cookieMainHeader'] a",
                "div[aria-labelledby='cookieMainHeader'] button",
                "[aria-label*='tout accepter' i]",
                "[aria-label*='accepter tout' i]",
                "[aria-label*='accept all' i]"
            ];

            for (var i = 0; i < selectors.length; i++) {
                try {
                    var el = root.querySelector(selectors[i]);
                    if (el) {
                        try {
                            el.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, view: window }));
                            el.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true, view: window }));
                            el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
                        } catch(e) {}
                        el.click();
                        return selectors[i];
                    }
                } catch(e) {}
            }

            // 2. Recherche textuelle parmi les boutons et liens dans ce root
            try {
                var candidates = root.querySelectorAll('button, a, div[role="button"], span[role="button"], input[type="button"]');
                for (var j = 0; j < candidates.length; j++) {
                    var txt = (candidates[j].innerText || candidates[j].textContent || "").trim().toLowerCase();
                    if (txt.includes("tout accepter") || txt.includes("accepter tout") || txt.includes("accept all") || txt === "accepter" || txt === "j'accepte" || txt === "accept") {
                        try {
                            candidates[j].dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, view: window }));
                            candidates[j].dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true, view: window }));
                            candidates[j].dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
                        } catch(e) {}
                        candidates[j].click();
                        return "texte: " + txt;
                    }
                }
            } catch(e) {}

            // 3. Exploration récursive de tous les Shadow Roots enfants
            try {
                var allElems = root.querySelectorAll('*');
                for (var k = 0; k < allElems.length; k++) {
                    if (allElems[k].shadowRoot) {
                        var foundInShadow = clickAcceptInRoot(allElems[k].shadowRoot);
                        if (foundInShadow) {
                            return "shadowRoot -> " + foundInShadow;
                        }
                    }
                }
            } catch(e) {}

            return null;
        }

        return clickAcceptInRoot(document);
        """

    while time.time() < end_time:
      # 1. Vérification dans la page principale (DOM et Shadow DOM)
      try:
        clicked = driver.execute_script(js_click_script)
        if clicked:
          print(f"Bouton de cookies cliqué avec succès dans la page : {clicked}")
          time.sleep(1)
          return True
      except Exception:
        pass

      # 2. Vérification dans les iframes (et leurs Shadow DOM)
      try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
          try:
            driver.switch_to.frame(iframe)
            clicked = driver.execute_script(js_click_script)
            if clicked:
              print(f"Bouton de cookies cliqué avec succès dans l'iframe : {clicked}")
              driver.switch_to.default_content()
              time.sleep(1)
              return True
          except Exception:
            pass
          finally:
            driver.switch_to.default_content()
      except Exception:
        driver.switch_to.default_content()

      time.sleep(1)

    print("Aucun bandeau de cookies trouvé à cliquer dans le délai imparti.")
    return False

  except Exception as e:
    driver.switch_to.default_content()
    print(f"Erreur lors de la gestion des cookies : {e}")
    return False

    return False