import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import json
import re
import time
from datetime import datetime
from unidecode import unidecode
from Match import Match
import pointhandler
import os 

# global selenium firefox options
options=Options()
options.set_preference("permissions.default.image", 2)                          # dont load images
options.set_preference("dom.disable_beforeunload", True)                        # dont load popups
options.set_preference("permissions.default.stylesheet", 2)                     # dont load css
options.set_preference("dom.ipc.plugins.enabled.libflashplayer.so","false")     # dont use flash (is that even a thing anymore?)
options.add_argument("--headless")                                              # open browser in background (headless)
driver = webdriver.Firefox(options=options)

def match_scrape(url):
    # --- this block formats the URL to make sure the match stats tab is open
    if ("flashscoreusa" in url):
        url = url.replace("flashscoreusa.com/game/tennis","flashscore.in/match/tennis") #oh brother 
    if ("/summary/stats/overall" in url):
        driver.get(url)
    elif ("/?mid=" in url):
        staturl = url.replace("?","summary/stats/overall/?")
        driver.get(staturl)
    elif ("/match/tennis/" in url):
        staturl = url + "summary/stats/overall/"
        driver.get(staturl)
    else:
        print("Invalid URL. Make sure you are linking to a tennis match on Flashscore.")
        return
    # ---

    main = driver.find_element(By.CSS_SELECTOR,"#detail") # selects match stats panel as the base element to search in

    WebDriverWait(main, 20).until(EC.visibility_of_element_located((By.CLASS_NAME,"duelParticipant__startTime")))
    WebDriverWait(main, 20).until(EC.visibility_of_element_located((By.CLASS_NAME,"fixedHeaderDuel__detailStatus")))
    starttime = int(datetime.strptime(main.find_element(By.CLASS_NAME,"duelParticipant__startTime").text, "%d.%m.%Y %H:%M").timestamp() * 1000)
    if ("WALKOVER" in main.find_element(By.CLASS_NAME,"fixedHeaderDuel__detailStatus").text):
        game_status = "walkover"
    elif ("RETIRED" in main.find_element(By.CLASS_NAME,"fixedHeaderDuel__detailStatus").text):
        game_status = "retirement"
        WebDriverWait(main, 20).until(EC.visibility_of_element_located((By.CLASS_NAME,"wcl-tabsTertiary_wjP-c")))
    elif ("FINISHED" in main.find_element(By.CLASS_NAME,"fixedHeaderDuel__detailStatus").text):
        game_status = "complete"
        WebDriverWait(main, 20).until(EC.visibility_of_element_located((By.CLASS_NAME,"wcl-tabsTertiary_wjP-c")))

    sets_played = len(main.find_element(By.CLASS_NAME,"wcl-tabsTertiary_wjP-c").find_elements(By.TAG_NAME,"a"))-1
    
    if (main.find_element(By.XPATH,".//div[1]/nav/ol/li[3]/a/span").text.rsplit(",",1)[0].lower() == "french open"): # this site calls it "french open" so we need this line...
        tournament = "roland garros"
    elif (main.find_element(By.XPATH,".//div[1]/nav/ol/li[3]/a/span").text.rsplit(",",1)[0].lower() == "monte carlo"): # this site calls it "french open" so we need this line...
        tournament = "monte-carlo"
    else:
        tournament = main.find_element(By.XPATH,".//div[1]/nav/ol/li[3]/a/span").text.rsplit(",",1)[0].lower()
    if ("qualification" in tournament):
        return

    player1 = driver.find_element(By.CLASS_NAME,"seoTop__content").text.split(" v ")[0]
    player2 = re.split(r" .[0-9]",driver.find_element(By.CLASS_NAME,"seoTop__content").text.split(" v ")[1])[0]

    # --- NAME EXCEPTIONS
    player1 = "Daniel Merida" if player1 == "Daniel Merida Aguilar" else player1
    player2 = "Daniel Merida" if player2 == "Daniel Merida Aguilar" else player2
    player1 = "Jan Lennard Struff" if player1 == "Jan-Lennard Struff" else player1
    player2 = "Jan Lennard Struff" if player2 == "Jan-Lennard Struff" else player2
    player1 = "Pablo Carreno Busta" if player1 == "Pablo Carreno-Busta" else player1
    player2 = "Pablo Carreno Busta" if player2 == "Pablo Carreno-Busta" else player2
    player1 = "Pierre Hugues Herbert" if player1 == "Pierre-Hugues Herbert" else player1
    player2 = "Pierre Hugues Herbert" if player2 == "Pierre-Hugues Herbert" else player2
    player1 = "Coleman Wong" if player1 == "Chak Lam Coleman Wong" else player1
    player2 = "Coleman Wong" if player2 == "Chak Lam Coleman Wong" else player2
    player1 = "Aleksandr Shevchenko" if player1 == "Alexander Shevchenko" else player1
    player2 = "Aleksandr Shevchenko" if player2 == "Alexander Shevchenko" else player2
    player1 = "Roberto Bautista Agut" if player1 == "Roberto Bautista-Agut" else player1
    player2 = "Roberto Bautista Agut" if player2 == "Roberto Bautista-Agut" else player2
    # ---

    #creating filename and checking for duplicates 
    filename = "matches/" + " ".join(player1.split()[1:]).lower() + "_vs_" + " ".join(player2.split()[1:]).lower() + "_" + tournament + ".json"
    reverse_filename = "matches/" + " ".join(player2.split()[1:]).lower() + "_vs_" + " ".join(player1.split()[1:]).lower() + "_" + tournament + ".json"

    #checking for duplicates
    if os.path.exists(filename):
        print(f"match already exists please check {filename}")
        print("aborting...")
        return
    elif os.path.exists(reverse_filename):
        print(f"match already exist please check {reverse_filename}")
        print("aborting...")
        return 


    winnerurl = main.find_element(By.CLASS_NAME,"duelParticipant--winner").find_element(By.CLASS_NAME,"participant__participantLink").get_attribute("href")
    p1url = main.find_element(By.CLASS_NAME,"duelParticipant__home").find_element(By.TAG_NAME,"a").get_attribute("href")
    if (p1url == winnerurl):
        winner = player1
        loser = player2
    else:
        winner = player2
        loser = player1

    if (game_status == "walkover"):
        stats = {"time": starttime,
                 "game_status": game_status,
                 "sets_played": 0,
                 "player1": player1,
                 "player1_team": "NO",
                 "player2": player2,
                 "player2_team": "NO",
                 "tournament": tournament,
                 "winner": winner,
                 "loser": loser,
                 "player1_stats":{
                     "aces": 0,
                     "double_faults": 0,
                     "breaks": 0,
                     "set1_games_won": 0,
                     "set1_games_lost": 0,
                     "set2_games_won": 0,
                     "set2_games_lost": 0,
                     "set3_games_won": 0,
                     "set3_games_lost": 0,
                     "set4_games_won": 0,
                     "set4_games_lost": 0,
                     "set5_games_won": 0,
                     "set5_games_lost": 0,
                     "games_won": 0,
                     "games_lost": 0,
                     "sets_won": 0,
                     "sets_lost": 0,
                     "points": 0
                     },
                 "player2_stats":{
                     "aces": 0,
                     "double_faults": 0,
                     "breaks": 0,
                     "set1_games_won": 0,
                     "set1_games_lost": 0,
                     "set2_games_won": 0,
                     "set2_games_lost": 0,
                     "set3_games_won": 0,
                     "set3_games_lost": 0,
                     "set4_games_won": 0,
                     "set4_games_lost": 0,
                     "set5_games_won": 0,
                     "set5_games_lost": 0,
                     "games_won": 0,
                     "games_lost": 0,
                     "sets_won": 0,
                     "sets_lost": 0,
                     "points": 0
                     }
                 }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=4)

    else:
        servesection = main.find_elements(By.CLASS_NAME,"section")[0]
        returnsection = main.find_elements(By.CLASS_NAME,"section")[1]
        p1aces = int(servesection.find_elements(By.CLASS_NAME,"wcl-homeValue_3Q-7P")[0].text)
        p2aces = int(servesection.find_elements(By.CLASS_NAME,"wcl-awayValue_Y-QR1")[0].text)
        p1double_faults = int(servesection.find_elements(By.CLASS_NAME,"wcl-homeValue_3Q-7P")[1].text)
        p2double_faults = int(servesection.find_elements(By.CLASS_NAME,"wcl-awayValue_Y-QR1")[1].text)
        p1breaks = int(returnsection.find_elements(By.CLASS_NAME,"wcl-homeValue_3Q-7P")[2].text.split("/")[0])
        p2breaks = int(returnsection.find_elements(By.CLASS_NAME,"wcl-awayValue_Y-QR1")[2].text.split("/")[0])

        driver.get(url.replace("/summary/stats/overall",""))
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH,".//div[contains(@class, 'smh__home smh__part--1')]")))

        p1set1_games_won = int(driver.find_element(By.XPATH,".//div[contains(@class, 'smh__home smh__part--1')]").text.split("\n")[0])
        if (driver.find_element(By.XPATH,".//div[contains(@class, 'smh__home smh__part--2')]").text.split("\n")[0]):
            p1set2_games_won = int(driver.find_element(By.XPATH,".//div[contains(@class, 'smh__home smh__part--2')]").text.split("\n")[0])
        else:
            p1set2_games_won = None
        if (driver.find_element(By.XPATH,".//div[contains(@class, 'smh__home smh__part--3')]").text.split("\n")[0]):
            p1set3_games_won = int(driver.find_element(By.XPATH,".//div[contains(@class, 'smh__home smh__part--3')]").text.split("\n")[0])
        else:
            p1set3_games_won = None
        if (driver.find_element(By.XPATH,".//div[contains(@class, 'smh__home smh__part--4')]").text.split("\n")[0]):
            p1set4_games_won = int(driver.find_element(By.XPATH,".//div[contains(@class, 'smh__home smh__part--4')]").text.split("\n")[0])
        else:
            p1set4_games_won = None
        if (driver.find_element(By.XPATH,".//div[contains(@class, 'smh__home smh__part--5')]").text.split("\n")[0]):
            p1set5_games_won = int(driver.find_element(By.XPATH,".//div[contains(@class, 'smh__home smh__part--5')]").text.split("\n")[0])
        else:
            p1set5_games_won = None
        p2set1_games_won = int(driver.find_element(By.XPATH,".//div[contains(@class, 'smh__away smh__part--1')]").text.split("\n")[0])
        if (driver.find_element(By.XPATH,".//div[contains(@class, 'smh__away smh__part--2')]").text.split("\n")[0]):
            p2set2_games_won = int(driver.find_element(By.XPATH,".//div[contains(@class, 'smh__away smh__part--2')]").text.split("\n")[0])
        else:
            p2set2_games_won = None
        if (driver.find_element(By.XPATH,".//div[contains(@class, 'smh__away smh__part--3')]").text.split("\n")[0]):
            p2set3_games_won = int(driver.find_element(By.XPATH,".//div[contains(@class, 'smh__away smh__part--3')]").text.split("\n")[0])
        else:
            p2set3_games_won = None
        if (driver.find_element(By.XPATH,".//div[contains(@class, 'smh__away smh__part--4')]").text.split("\n")[0]):
            p2set4_games_won = int(driver.find_element(By.XPATH,".//div[contains(@class, 'smh__away smh__part--4')]").text.split("\n")[0])
        else:
            p2set4_games_won = None
        if (driver.find_element(By.XPATH,".//div[contains(@class, 'smh__away smh__part--5')]").text.split("\n")[0]):
            p2set5_games_won = int(driver.find_element(By.XPATH,".//div[contains(@class, 'smh__away smh__part--5')]").text.split("\n")[0])
        else:
            p2set5_games_won = None
        p1set1_games_lost = p2set1_games_won
        p1set2_games_lost = p2set2_games_won
        p1set3_games_lost = p2set3_games_won
        p1set4_games_lost = p2set4_games_won
        p1set5_games_lost = p2set5_games_won
        p2set1_games_lost = p1set1_games_won
        p2set2_games_lost = p1set2_games_won
        p2set3_games_lost = p1set3_games_won
        p2set4_games_lost = p1set4_games_won
        p2set5_games_lost = p1set5_games_won
        p1games_won = sum([p1set1_games_won,(p1set2_games_won or 0),(p1set3_games_won or 0),(p1set4_games_won or 0),(p1set5_games_won or 0)])
        p2games_won = sum([p2set1_games_won,(p2set2_games_won or 0),(p2set3_games_won or 0),(p2set4_games_won or 0),(p2set5_games_won or 0)])
        p1games_lost = sum([p2set1_games_won,(p2set2_games_won or 0),(p2set3_games_won or 0),(p2set4_games_won or 0),(p2set5_games_won or 0)])
        p2games_lost= sum([p1set1_games_won,(p1set2_games_won or 0),(p1set3_games_won or 0),(p1set4_games_won or 0),(p1set5_games_won or 0)])
        p1sets_won = int(driver.find_element(By.XPATH,".//div[contains(@class, 'smh__home smh__part--current')]").text)
        p2sets_won = int(driver.find_element(By.XPATH,".//div[contains(@class, 'smh__away smh__part--current')]").text)
        p1sets_lost= int(driver.find_element(By.XPATH,".//div[contains(@class, 'smh__away smh__part--current')]").text)
        p2sets_lost = int(driver.find_element(By.XPATH,".//div[contains(@class, 'smh__home smh__part--current')]").text)

        stats = {"time": starttime,
                 "game_status": game_status,
                 "sets_played": sets_played,
                 "player1": player1,
                 "player1_team": "NO",
                 "player2": player2,
                 "player2_team": "NO",
                 "tournament": tournament,
                 "winner": winner,
                 "loser": loser,
                 "player1_stats":{
                     "aces": p1aces,
                     "double_faults": p1double_faults,
                     "breaks": p1breaks,
                     "set1_games_won": p1set1_games_won,
                     "set1_games_lost": p1set1_games_lost,
                     "set2_games_won": p1set2_games_won,
                     "set2_games_lost": p1set2_games_lost,
                     "set3_games_won": p1set3_games_won,
                     "set3_games_lost": p1set3_games_lost,
                     "set4_games_won": p1set4_games_won,
                     "set4_games_lost": p1set4_games_lost,
                     "set5_games_won": p1set5_games_won,
                     "set5_games_lost": p1set5_games_lost,
                     "games_won": p1games_won,
                     "games_lost": p1games_lost,
                     "sets_won": p1sets_won,
                     "sets_lost": p1sets_lost,
                     "points": 0
                     },
                 "player2_stats":{
                     "aces": p2aces,
                     "double_faults": p2double_faults,
                     "breaks": p2breaks,
                     "set1_games_won": p2set1_games_won,
                     "set1_games_lost": p2set1_games_lost,
                     "set2_games_won": p2set2_games_won,
                     "set2_games_lost": p2set2_games_lost,
                     "set3_games_won": p2set3_games_won,
                     "set3_games_lost": p2set3_games_lost,
                     "set4_games_won": p2set4_games_won,
                     "set4_games_lost": p2set4_games_lost,
                     "set5_games_won": p2set5_games_won,
                     "set5_games_lost": p2set5_games_lost,
                     "games_won": p2games_won,
                     "games_lost": p2games_lost,
                     "sets_won": p2sets_won,
                     "sets_lost": p2sets_lost,
                     "points": 0
                     }
                 }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=4)
    print(filename + " was created.")

    match = Match.File2Match(filename)
    pointhandler.pointhandler(match)

def tournament_scrape(url):
    if ("flashscoreusa" in url):
        url = url.replace("flashscoreusa.com","flashscore.in")
    if ("results" not in url):
        url = url.rsplit("#",1)[0] + "results"
        driver.get(url)
    else:
        driver.get(url)

        
    with open("teams.csv", newline="") as file: #this is causing a logic error 
        teams = file.read()
    links = []
    driver.implicitly_wait(10)
    for match in driver.find_elements(By.CLASS_NAME,"event__match"):
        for player in match.find_elements(By.CLASS_NAME,"wcl-name_jjfMf"):
            if (player.text.split()[0] in teams):
                links.append(match.find_element(By.CLASS_NAME,"eventRowLink").get_attribute("href")) #logic error 
                break


    for link in links:
        match_scrape(link)
    print("Tournament fully scanned.")

def main():
    if sys.argv[1].endswith(".txt"):
            with open(sys.argv[1]) as f:
                for link in f:
                    match_scrape(link)
    elif ("atp-singles" in sys.argv[1]):
        tournament_scrape(sys.argv[1])
    else:
        for i in range(1,len(sys.argv)):
            match_scrape(sys.argv[i])
    
        driver.quit()
    return 

if __name__ == "__main__":
    if sys.argv[1].endswith(".txt"):
        with open(sys.argv[1]) as f:
            for link in f:
                if ("atp-singles" in link):
                    tournament_scrape(link)
                else:
                    match_scrape(link)
    elif ("atp-singles" in sys.argv[1]):
        tournament_scrape(sys.argv[1])
    else:
        for i in range(1,len(sys.argv)):
            match_scrape(sys.argv[i])

    driver.quit()
