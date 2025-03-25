import requests
import re
from google.generativeai import GenerativeModel, configure

# Configure Gemini API
configure(api_key="AIzaSyCeIzo3yb2MYwp536XX_BODXUZBwjkP14Y")  # Replace with your actual API key
def get_ipl_teams(team1_code, team2_code):
    teams = {
        "DC": "Delhi Capitals",
        "LSG": "Lucknow Super Giants",
        "MI": "Mumbai Indians",
        "CSK": "Chennai Super Kings",
        "RCB": "Royal Challengers Bangalore",
        "KKR": "Kolkata Knight Riders",
        "SRH": "Sunrisers Hyderabad",
        "PBKS": "Punjab Kings",
        "GT": "Gujarat Titans",
        "RR": "Rajasthan Royals"
    }

    team1 = teams.get(team1_code, "Unknown Team")
    team2 = teams.get(team2_code, "Unknown Team")

    return team1, team2

def fetch_squads(t1,t2):
    team1, team2 = get_ipl_teams(t1, t2)
    api_url = "http://127.0.0.1:8000/get_squads/"
    request_body = {
        "team1": team1,
        "team2": team2
    }

    try:
        response = requests.post(api_url, json=request_body)
        response.raise_for_status()  # Raise an error for bad status codes
        squad_data = response.json()

        wk_players, bat_players, ar_players, bowl_players = send_to_gemini(squad_data)

        print("Wicketkeepers:", wk_players)
        print("Batsmen:", bat_players)
        print("All-rounders:", ar_players)
        print("Bowlers:", bowl_players)

        return wk_players, bat_players, ar_players, bowl_players  # Return the variables
    except requests.RequestException as error:
        print("Error fetching squads:", error)
        return [], [], [], []  # Return empty lists on failure

def send_to_gemini(squad_data):
    model = GenerativeModel("gemini-2.0-flash")

    prompt = f"""Please help me create an optimal Dream11 fantasy cricket team from the following player squads:

                {squad_data}

                Requirements:
                1. Select exactly 11 players total
                2. Maximum 6 players from any single team
                3. Must include players for these roles:
                - Wicketkeepers (WK)
                - Batsmen (BAT)
                - All-rounders (AR)
                - Bowlers (BOWL)

                Please provide your selection in this specific format:
                wk_players = [...]
                bat_players = [...]
                ar_players = [...]
                bowl_players = [...]

                Note: Dont mention brackets like (C) and (WK)

                Consider the following when making selections:
                - Recent form and performance
                - Player strengths against the opposition
                - Pitch conditions and match venue
                - Players likely to contribute maximum fantasy points
                - Balance between consistent performers and high-potential players"""

    try:
        result = model.generate_content(prompt)
        response_text = result.text
        return extract_players(response_text)
    except Exception as error:
        print("Error sending data to Gemini API:", error)
        return [], [], [], []

def extract_players(response_text):
    try:
        wk_players = re.search(r"wk_players\s*=\s*\[([^\]]+)\]", response_text).group(1).split(",")
        bat_players = re.search(r"bat_players\s*=\s*\[([^\]]+)\]", response_text).group(1).split(",")
        ar_players = re.search(r"ar_players\s*=\s*\[([^\]]+)\]", response_text).group(1).split(",")
        bowl_players = re.search(r"bowl_players\s*=\s*\[([^\]]+)\]", response_text).group(1).split(",")

        # Clean and strip quotes
        wk_players = [p.strip().strip("'\"") for p in wk_players]
        bat_players = [p.strip().strip("'\"") for p in bat_players]
        ar_players = [p.strip().strip("'\"") for p in ar_players]
        bowl_players = [p.strip().strip("'\"") for p in bowl_players]

        return wk_players, bat_players, ar_players, bowl_players
    except Exception as error:
        print("Error extracting players:", error)
        return [], [], [], []

# if __name__ == "__main__":
#     fetch_squads()
