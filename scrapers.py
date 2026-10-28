from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import pandas as pd
import requests
import json
import os
from unidecode import unidecode

# global selenium firefox options

def create_driver():
    options=Options()
    options.set_preference("permissions.default.image", 2)                          # dont load images
    options.set_preference("dom.disable_beforeunload", True)                        # dont load popups
    options.set_preference("permissions.default.stylesheet", 2)                     # dont load css
    options.set_preference("javascript.enabled", False)                             # disable javascript
    options.set_preference("dom.ipc.plugins.enabled.libflashplayer.so","false")     # dont use flash (is that even a thing anymore?)
    options.add_argument("--headless")                                              # open browser in background (headless)
    driver = webdriver.Firefox(options=options)
    return driver, options 

def scrape_rankings():
    driver, options = create_driver()

    driver.get("https://live-tennis.eu/en/atp-live-ranking")
    # xpath tells selenium what html elements to look for
    rows = driver.find_element(By.ID,"plyrRankings").find_elements(By.XPATH,".//tbody/tr[position()<=506 and (contains(@class, 'of1') or contains(@class, 'of2') or contains(@class, 'on1') or contains(@class, 'on2'))]")

    dataset = []
    for row in rows:
        data = {}
        cells = row.find_elements(By.TAG_NAME,"td")
        data['Rank'] = cells[0].text
        data['FirstName'] = unidecode(cells[3].text.split(" ")[0])
        data['LastName'] = unidecode(" ".join(cells[3].text.split(" ")[1:]))
        data['Age'] = cells[4].text
        data['Nation'] = cells[5].text
        data['Points'] = cells[6].text
        if len(cells) >= 10:
            data['Current'] = cells[9].text.split("\n")[0]
        else:
            data['Current'] = ""
        if len(cells) >= 11:
            data['Previous'] = cells[10].text.split("\n")[0]
        else:
            data['Previous'] = ""
        data['Team'] = "NO"
        dataset.append(data)
    
    df = pd.DataFrame(dataset)
    df.to_csv("players.csv", index=False)
    
    driver.quit()
    print("Rankings have been updated.")

if __name__ == "__main__":
   scrape_rankings()
