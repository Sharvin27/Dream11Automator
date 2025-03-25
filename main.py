import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = FastAPI()

class MatchRequest(BaseModel):
    team1: str
    team2: str

def get_playing_11_and_subs(team1, team2):
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir=C:\\Users\\sharv\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 5")
    options.add_argument("--headless")  
    prefs = {"safebrowsing.enabled": True}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 10)

    try:
        driver.get("https://www.cricbuzz.com/")
        time.sleep(1)

        match_title_1 = f"{team1} v {team2}"
        match_title_2 = f"{team2} v {team1}"

        # Try finding either of the match titles
        match_div = wait.until(EC.element_to_be_clickable((
            By.XPATH, f"//a[contains(@title, '{match_title_1}') or contains(@title, '{match_title_2}')]"
        )))
        match_div.click()
        time.sleep(1)

        squads_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@title, 'Squads')]")))
        squads_tab.click()
        time.sleep(1)

        # Extract Team 1 Players (Left Side)
        team1_players = driver.find_elements(By.CSS_SELECTOR, ".cb-col.cb-col-100 a.cb-player-card-left")
        team1_squad = []
        for player in team1_players:
            full_text = player.find_element(By.CSS_SELECTOR, ".cb-player-name-left div").text.strip()
            lines = full_text.split("\n")
            name = lines[0]
            role = lines[1] if len(lines) > 1 else "Unknown"
            team1_squad.append({"name": name, "role": role})

        team1_top_11 = team1_squad[:11]   
        team1_next_5 = team1_squad[11:16]  

        # Extract Team 2 Players (Right Side)
        team2_players = driver.find_elements(By.CSS_SELECTOR, ".cb-col.cb-col-100 a.cb-player-card-right")
        team2_squad = []
        for player in team2_players:
            full_text = player.find_element(By.CSS_SELECTOR, ".cb-player-name-right div").text.strip()
            lines = full_text.split("\n")
            name = lines[0]
            role = lines[1] if len(lines) > 1 else "Unknown"
            team2_squad.append({"name": name, "role": role})

        team2_top_11 = team2_squad[:11]   
        team2_next_5 = team2_squad[11:16]  

        return {
            "team1": {"top_11": team1_top_11, "next_5": team1_next_5},
            "team2": {"top_11": team2_top_11, "next_5": team2_next_5}
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        driver.quit()

@app.post("/get_squads/")
def get_squads(request: MatchRequest):
    return get_playing_11_and_subs(request.team1, request.team2)

import uvicorn

if __name__ == "__main__":
    uvicorn.run("script_name:app", host="127.0.0.1", port=8000, reload=True, reload_exclude="env")
