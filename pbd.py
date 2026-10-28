import sys
import os
import json

import csv 

def point_breakdown(name):
    name
    total_points = 0
    teams = {
        "Bolabinga Tennis Club": 0,
        "Lanzhou Hand Pulled Noodles": 0,
        "Rileys Rascals": 0,
        "Ori Woohoo": 0,
        "Bagel Brothers": 0,
        "NO": 0
    }
    for file in os.listdir("matches"):
        if os.path.join("matches", file).endswith(".json"):
            with open(os.path.join("matches", file), "r") as f:
                data = json.load(f)
                if data["player1"].lower() == name.lower():
                    print(f"Processing file: {file}")  # Debugging line to check which files are being processed 
                    team = data["player1_team"]
                    teams[team] += round(data["player1_stats"]["points"],2)
                    total_points += round(data["player1_stats"]["points"],2)
                elif data["player2"].lower() == name.lower():
                    print(f"Processing file: {file}")  # Debugging line to check which files are being processed
                    team = data["player2_team"]
                    teams[team] += round(data["player2_stats"]["points"],2)
                    total_points += round(data["player2_stats"]["points"],2)
                else:
                    continue

    print(f"Point breakdown for {name}:")
    print(f"{name} scored {total_points} points in total")
    print(f"{name} scored {teams['NO']} points as a free agent")
    print(f"{name} scored {teams['Bolabinga Tennis Club']} points for Bolabinga Tennis Club")
    print(f"{name} scored {teams['Lanzhou Hand Pulled Noodles']} points for Lanzhou Hand Pulled Noodles")
    print(f"{name} scored {teams['Rileys Rascals']} points for Rileys Rascals")
    print(f"{name} scored {teams['Ori Woohoo']} points for Ori Woohoo")
    print(f"{name} scored {teams['Bagel Brothers']} points for Bagel Brothers")

def team_breakdown(team_name):
    team_name = team_name.lower()
    total_points = 0
    players = {}
    for file in os.listdir("matches"):
        if os.path.join("matches", file).endswith(".json"):
            with open(os.path.join("matches", file), "r") as f:
                data = json.load(f)
                if data["player1_team"].lower() == team_name:
                    print(f"Processing file: {file}")  # Debugging line to check which files are being processed
                    player = data["player1"]
                    if player not in players:
                        players[player] = 0
                    players[player] += round(data["player1_stats"]["points"],2)
                    total_points += round(data["player1_stats"]["points"],2)
                if data["player2_team"].lower() == team_name:
                    print(f"Processing file: {file}")  # Debugging line to check which files are being processed
                    player = data["player2"]
                    if player not in players:
                        players[player] = 0
                    players[player] += round(data["player2_stats"]["points"],2)
                    total_points += round(data["player2_stats"]["points"],2)
                else:
                    continue

    print(f"Point breakdown for {team_name}:")
    print(f"{team_name} scored {total_points} points in total")
    for player, points in players.items():
        print(f"{player} scored {points} points for {team_name}")

def event_breakdown(tournament):
    teams = {
            "Bolabinga Tennis Club": 0,
            "Lanzhou Hand Pulled Noodles": 0,
            "Rileys Rascals": 0,
            "Ori Woohoo": 0,
            "Bagel Brothers": 0,
            "NO": 0
        }

    alternative_names = {
        "ao": "australian open",
        "fo": "french open",
        "us": "us open",
        "wim": "wimbledon",
        "wimby": "wimbledon",
        "iw": "indian wells",
    }

    for file in os.listdir("matches"):
            if os.path.join("matches", file).endswith(f"{tournament}.json"):
                ...

    
    


def main():
    options = {
        "1": point_breakdown,
        "2": team_breakdown,
        "3": event_breakdown
    }
    print("1 for point breakdown by player and 2 for point breakdown by team and 3 for event breakdown")
    choice = input("Enter your choice: ")  

    if choice in options:
            name = input("Enter the name of the player or team: ")
            options[choice](name)

if __name__ == "__main__":
    main()
    
    