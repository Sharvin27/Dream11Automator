import uiautomator2 as u2
import time
import random
from test3 import fetch_squads

selected_count = 0

# Connect to device
def connect_to_device():
    try:
        # Initialize connection to the device
        d = u2.connect()  # Will connect to the first available device
        print(f"Connected to device: {d.info['productName']}")
        return d
    except Exception as e:
        print(f"Failed to connect to device: {e}")
        exit(1)

# Launch Dream11 app
def launch_dream11(d):
    print("Launching Dream11...")
    d.app_start("com.dream11.fantasy.cricket.football.kabaddi")
    # Wait for app to load completely
    time.sleep(1)
    # Check if app is running
    if d.app_current()['package'] != "com.dream11.fantasy.cricket.football.kabaddi":
        print("Failed to launch Dream11. Please check if the app is installed.")
        exit(1)
    print("Dream11 launched successfully.")

# Navigate to matches tab and select an upcoming match
def navigate_to_upcoming_match(d):
    if d(text="CREATE TEAM").exists():
        d(text="CREATE TEAM").click()

    else:
        d.click(540,1598)  # Click in the upper middle of the screen
        time.sleep(2)
        print(7)
        
        # Now try to find "CREATE TEAM" button on the match details screen
        if d(text="CREATE TEAM").exists():
            d(text="CREATE TEAM").click()
        else:
            return False
    
    time.sleep(3)
    return True

# Join a contest or go directly to team creation
def create_new_team(d):
    print("Creating a new team...")
    
    # Check if we're on the team selection screen or contest selection screen
    if d(text="SELECT TYPE").exists() or d(text="WK").exists():
        print("Already on team creation screen.")
        print("A")

    else:
        # Look for a contest to join
        print("c")
        if d(text="JOIN").exists():
            d(text="JOIN").click()
            time.sleep(3)
            if d(text="CREATE TEAM").exists():
                d(text="CREATE TEAM").click()
        else:
            # Try scrolling down to find more contests
            d.swipe(0.5, 0.8, 0.5, 0.2)  # Swipe up
            time.sleep(2)
            if d(text="JOIN").exists():
                d(text="JOIN").click()
                time.sleep(3)
                if d(text="CREATE TEAM").exists():
                    d(text="CREATE TEAM").click()
            else:
                return False
    
    time.sleep(3)
    return True

# Select players for the team
def select_players(d,t1,t2):
    print("Selecting players...")
    
    # Check if we're on the player selection screen
    if not (d(text="WK").exists() or d(text="BAT").exists() or d(text="AR").exists() or d(text="BOWL").exists()):
        return False
    
    wk_players, bat_players, ar_players, bowl_players = fetch_squads(t1,t2)
    
    # Select 1 player from WK
    wk_selected = select_players_by_name(d, "WK", wk_players, len(wk_players))
    if wk_selected == 0:
        print("Failed to select any WK player")
        return False
    
    # Select 3 players from BAT
    bat_selected = select_players_by_name(d, "BAT", bat_players, len(bat_players))
    if bat_selected < 3:
        print(f"Warning: Only selected {bat_selected}/3 BAT players")
    
    # Select 3 players from AR
    ar_selected = select_players_by_name(d, "AR", ar_players, len(ar_players))
    if ar_selected < 3:
        print(f"Warning: Only selected {ar_selected}/3 AR players")
    
    # Select 4 players from BOWL
    bowl_selected = select_players_by_name(d, "BOWL", bowl_players, len(bowl_players))
    if bowl_selected < 4:
        print(f"Warning: Only selected {bowl_selected}/4 BOWL players")
    
    # Proceed to next screen
    if d(text="NEXT").exists():
        d(text="NEXT").click()
        time.sleep(3)
        return True
    elif d(text="CONTINUE").exists():
        d(text="CONTINUE").click()
        time.sleep(3)
        return True
    else:
        width, height = d.window_size()
        d.click(width * 0.75, height * 0.95)  # Try clicking where the NEXT button might be
        time.sleep(3)
        
        # Check if we've moved to the next screen
        if d(text="CAPTAIN").exists() or d(text="CHOOSE YOUR CAPTAIN").exists():
            return True
        else:
            return False
        
def playerfind(d,player_name):
    global selected_count
    found_player = False
    scroll_count = 0
    # Get screen dimensions
    width, height = d.window_size()
    
    # Try to find this player, scrolling if necessary
    while not found_player and scroll_count < 4:
        # Try multiple ways to find the player name
        
        # 1. Exact text match
        if d(text=player_name).exists():
            found_player = True
            player_element = d(text=player_name)
            print(f"Found player with exact match: {player_name}")
        
        # 2. Contains text match
        elif d(textContains=player_name).exists():
            found_player = True
            player_element = d(textContains=player_name)
            print(f"Found player with partial match: {player_name}")
        
        # 3. Try searching for first name and last name separately
        elif " " in player_name:
            first_name, last_name = player_name.rsplit(" ", 1)
            if d(textContains=last_name).exists():
                found_player = True
                player_element = d(textContains=last_name)
                print(f"Found player with last name match: {last_name}")
        
        
        if found_player:
            try:
                # Get the bounds of the player element
                element_bounds = player_element[0].info['bounds']
                player_center_y = (element_bounds['top'] + element_bounds['bottom']) / 2
                
                # Click the "+" button (on the right side of the screen)
                d.click(width * 0.9, player_center_y)
                print(f"Clicked on '+' button for player: {player_name}")
                
                selected_count += 1
                time.sleep(1.5)  # Wait for selection to register
                print(1)
                return True  # Move to next player
            except Exception as e:
                print(f"Error selecting player {player_name}: {e}")
                found_player = False  # Reset so we can try scrolling
        
        # If player not found, scroll and try again
        if not found_player:
            print(f"Player {player_name} not found on current screen, scrolling...")

            if scroll_count % 2 == 0:
                # Scroll Down
                d.swipe(width * 0.5, height * 0.8, width * 0.5, height * 0.2)
                print("Scrolling Down")
            else:
                # Scroll Up
                d.swipe(width * 0.5, height * 0.4, width * 0.5, height * 0.9)
                print("Scrolling Up")

            time.sleep(2)
            scroll_count += 1
            print(scroll_count)
    
    # If we couldn't find this player after all scrolls
    if not found_player:
        print(f"Could not find player {player_name} after {scroll_count} scrolls")
        return False

def select_players_by_name(d, category, player_list, required_count):
    print(f"Selecting {required_count} players from {category} category")
    
    # Switch to the category tab
    category_initial = d(textContains=category)

    if category_initial.exists():
        category_initial.click()
        time.sleep(2)
    
    if d(text=category).exists():
        d(text=category).click()
        time.sleep(2)
    else:
        print(f"Could not find {category} tab.")
        return 0
        
    # Track how many players we've selected
    
    global selected_count
    selected_count = 0
    max_scroll_attempts = 4
    scroll_attempts = 0
    
    # Get screen dimensions
    width, height = d.window_size()
    
    # Try each player name from our list
    for player_name in player_list:
        # Skip if we've already selected enough players
        if selected_count >= required_count:
            break
            
        print(f"Looking for player: {player_name}")
        found = playerfind(d,player_name)

        if not found:
            category_elements = d(textContains="BAT")

            if category_elements.exists():
                category_elements.click()
                time.sleep(2)
            found = playerfind(d, player_name)

            if found and player_name != player_list[-1]:
                cat = d(textContains=category)
                if cat.exists():
                    cat.click()
                    time.sleep(2)
                
            if not found:
                print(f"Still could not find {player_name} in BAT category, skipping.")

        if not found:
            category_elements = d(textContains="AR")
            if category_elements.exists():
                category_elements.click()
                time.sleep(2)
            found = playerfind(d, player_name)

            if found and player_name != player_list[-1]:
                cat = d(textContains=category)
                if cat.exists():
                    cat.click()
                    time.sleep(2)
                
            if not found:
                print(f"Still could not find {player_name} in AR category, skipping.")
    

        
    
    # If we couldn't select enough players by name, fall back to selecting by position
    if selected_count < required_count:
        print(f"Could only select {selected_count}/{required_count} {category} players by name")
        print(f"Falling back to selecting by position to get remaining {required_count - selected_count} players")
        
        # Try to select remaining players by position
        fallback_attempts = 0
        max_fallback_attempts = 5
        
        # Look at players from the top of the screen
        row_height = height * 0.15  # Each row is roughly 15% of screen height
        start_y = height * 0.25     # First player starts around 25% from top
        
        while selected_count < required_count and fallback_attempts < max_fallback_attempts:
            for i in range(5):  # Try up to 5 positions
                if selected_count >= required_count:
                    break
                    
                # Try clicking the "+" button at calculated positions
                y_pos = start_y + (i * row_height)
                d.click(width * 0.9, y_pos)
                print(f"Attempting fallback selection at position {i+1}")
                selected_count += 1
                time.sleep(1.5)
            
            # If we still need more players, scroll and try again
            if selected_count < required_count:
                d.swipe(width * 0.5, height * 0.8, width * 0.5, height * 0.2)  # Swipe up
                time.sleep(2)
                fallback_attempts += 1
    
    print(f"Selected {selected_count}/{required_count} players from {category} category")
    return selected_count

# Select captain and vice-captain
def select_captain_and_vc(d):
    print("Selecting captain and vice-captain...")
    
    # Check if we're on the captain selection screen
    if not d(text="CHOOSE YOUR CAPTAIN AND VICE CAPTAIN").exists():
        if not (d(text="C").exists() or d(text="VC").exists()):
            return False
    
    time.sleep(2)
    
    # Select a random player as captain
    width, height = d.window_size()
    c_buttons = []
    
    # Try to find all C buttons
    if d(text="C").exists():
        c_buttons = d(text="C")
        # Randomly select a captain
        if len(c_buttons) > 0:
            random_index = random.randint(0, len(c_buttons) - 1)
            c_buttons[random_index].click()
    else:
        # Fallback: click where the first C button might be
        d.click(width * 0.25, height * 0.3)
    
    time.sleep(2)
    
    # Select a different random player as vice-captain
    vc_buttons = []
    if d(text="VC").exists():
        vc_buttons = d(text="VC")
        # Randomly select a vice-captain
        if len(vc_buttons) > 0:
            random_index = random.randint(0, len(vc_buttons) - 1)
            vc_buttons[random_index].click()
    else:
        # Fallback: click where the second VC button might be
        d.click(width * 0.75, height * 0.4)
    
    time.sleep(2)
    
    # Save the team
    if d(text="SAVE TEAM").exists():
        d(text="SAVE TEAM").click()
    elif d(text="SAVE").exists():
        d(text="SAVE").click()
    else:
        # Fallback: click where the save button might be
        d.click(width * 0.5, height * 0.9)
    
    time.sleep(5)
    return True

# Save the team and handle team name dialog
def save_team(d):
    print("Saving team...")
    
    # Check if there's a team name dialog
    if d(text="TEAM NAME").exists() or d(text="Enter Team Name").exists():
        # Clear any existing text
        if d(className="android.widget.EditText").exists():
            d(className="android.widget.EditText").clear_text()
            # Enter a team name
            team_name = f"AutoTeam{random.randint(1, 999)}"
            d(className="android.widget.EditText").set_text(team_name)
            time.sleep(1)
            
            # Click save or create
            if d(text="CREATE").exists():
                d(text="CREATE").click()
            elif d(text="SAVE").exists():
                d(text="SAVE").click()
            else:
                # Fallback: try clicking where the save button might be
                width, height = d.window_size()
                d.click(width * 0.5, height * 0.8)
    
    time.sleep(5)
    return True

def select_contest(d):
    for price in ["₹49", "₹39"]:
        category_elements = d(textContains=price)
        
        if category_elements.exists():
            category_elements.click()
            time.sleep(2)
            
            if d(text="JOIN CONTEST").exists():
                d(text="JOIN CONTEST").click()
                print(f"Joined contest with entry fee {price}")
                return True  
    
    print("No eligible contest found.")
    return False  
    

# Main execution function
def create_dream11_team():
    try:
        # Connect to device
        d = connect_to_device()

        team1_code, team2_code = input("Enter two team codes separated by space: ").split()
        
        # Launch Dream11
        launch_dream11(d)
        
        # Navigate to an upcoming match
        if not navigate_to_upcoming_match(d):
            print("Failed to navigate to an upcoming match.")
            return
        
        # Create a new team
        if not create_new_team(d):
            print("Failed to create a new team.")
            return
        
        # Select players
        if not select_players(d,team1_code,team2_code):
            print("Failed to select players.")
            return
        
        # Select captain and vice-captain
        if not select_captain_and_vc(d):
            print("Failed to select captain and vice-captain.")
            return
        
        # Save the team
        if not save_team(d):
            print("Failed to save the team.")
            return
        
        # Save the team
        if not select_contest(d):
            print("Failed to select a contest.")
            return
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_dream11_team()