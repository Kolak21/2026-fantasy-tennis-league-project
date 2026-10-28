import time

from Team import Team
from Player import Player
from Match import Match
from typing import Dict, Any
import csv 
import sqlite3


def calculate_points(match: Match, options = "None"):
    #get the points for the match based on the league's point system
    multipliers = {
        "games_won": 2,
        "games_lost": -1.6,
        "sets_won": 5,
        "sets_lost": -2.5,
        "aces": 0.25,
        "double_faults": -1,
        "breaks": 0.5,
        "clean_set": 2.5
    }
    
    flat_points = {
        "match_won": 5,
        "match_played": 30,
        "walkover_win": 30,
        "straight_sets_win": 5,
        "no_double_faults": 5,
        "15+ aces": 2
    }
    #add any extra bonus points that you want lol
    bonus_points = {
        "vs_active_player" : 1.25, #multiplies the points by 1.25 if the player is playing against an active player
    }

    p1_score = 0
    p2_score = 0

    #walkover wins and match wins
    if match.data["game_status"] == "walkover":
        if match.data["player1"] == match.data["winner"]:
            p1_score += flat_points["walkover_win"]
        elif match.data["player2"] == match.data["winner"]:
            p2_score += flat_points["walkover_win"]

    #match wins
    if match.data["game_status"] == "complete":
        p1_score += flat_points["match_played"]
        p2_score += flat_points["match_played"]

        if match.data["winner"] == match.data["player1"]:
            p1_score += flat_points["match_won"]
            if match.data["sets_played"] == match.data["player1_stats"]["sets_won"] and match.data["player1_stats"]["sets_lost"] == 0:
                p1_score += flat_points["straight_sets_win"]

        elif match.data["winner"] == match.data["player2"]:
            p2_score += flat_points["match_won"]
            if match.data["sets_played"] == match.data["player2_stats"]["sets_won"] and match.data["player2_stats"]["sets_lost"] == 0:
                p2_score += flat_points["straight_sets_win"]

    #calculating player
    p1_score +=    match.data["player1_stats"]["games_won"] * multipliers["games_won"]
    p1_score +=    match.data["player1_stats"]["games_lost"] * multipliers["games_lost"]
    p1_score +=    match.data["player1_stats"]["aces"] * multipliers["aces"]
    p1_score +=    match.data["player1_stats"]["double_faults"] * multipliers["double_faults"]
    p1_score +=    match.data["player1_stats"]["breaks"] * multipliers["breaks"]
    p1_score +=    match.data["player1_stats"]["sets_won"] * multipliers["sets_won"]
    p1_score +=    match.data["player1_stats"]["sets_lost"] * multipliers["sets_lost"]

    #Calculating points from winning/losing sets

    #clean sets
    for n in range(1, match.data["sets_played"] + 1):
        if match.data["player1_stats"].get(f"set{n}_games_won") == 6 and match.data["player1_stats"].get(f"set{n}_games_lost") == 0:
            p1_score += multipliers["clean_set"]

    if match.data["player1_stats"]["aces"] >= 15:
        p1_score += flat_points["15+ aces"]

    if match.data["player1_stats"]["double_faults"] == 0:
        p1_score += flat_points["no_double_faults"]
    
    p1_score = round(p1_score, 2)
    print(f"{match.data['player1']}'s points for this match is {p1_score}!") # Fixed nested quotes syntax error

    #Calculating player 2 stats
    p2_score +=    match.data["player2_stats"]["games_won"] * multipliers["games_won"]
    p2_score +=    match.data["player2_stats"]["games_lost"] * multipliers["games_lost"]
    p2_score +=    match.data["player2_stats"]["aces"] * multipliers["aces"]
    p2_score +=    match.data["player2_stats"]["double_faults"] * multipliers["double_faults"]
    p2_score +=    match.data["player2_stats"]["breaks"] * multipliers["breaks"]
    p2_score +=    match.data["player2_stats"]["sets_won"] * multipliers["sets_won"]
    p2_score +=    match.data["player2_stats"]["sets_lost"] * multipliers["sets_lost"]

    #Calculating points from winning/losing sets

    #clean sets
    for n in range(1, match.data["sets_played"] + 1):
        if match.data["player2_stats"].get(f"set{n}_games_won") == 6 and match.data["player2_stats"].get(f"set{n}_games_lost") == 0:
            p2_score += multipliers["clean_set"]

    if match.data["player2_stats"]["aces"] >= 15:
            p2_score += flat_points["15+ aces"]
    
    if match.data["player2_stats"]["double_faults"] == 0:
            p2_score += flat_points["no_double_faults"]
    
    p2_score = round(p2_score, 2)
    print(f"{match.data['player2']}'s points for this match is {p2_score}!") # Fixed nested quotes syntax error

    #adding bonus points for playing against an active player
    if match.data["player1_team"] != "NO" and match.data["player2_team"] != "NO":
        p1_score *= bonus_points["vs_active_player"]
        p2_score *= bonus_points["vs_active_player"]

    return p1_score, p2_score

def update_points(match: Match, p1_points: int, p2_points: int):
    match.update_scores(p1_points, p2_points)
    return

def get_team_at_match_time(player_name: str, match_time: str):
    con = sqlite3.connect("log.db")
    cur = con.cursor()

    cur.execute("""
        SELECT teamName
        FROM log
        WHERE playerName = ?
        AND timestamp <= ?
        ORDER BY timestamp DESC
        LIMIT 1;
    """, (player_name, match_time))

    row = cur.fetchone()

    con.close()

    if row:
        return row[0]

    return "NO"

def revise_teams(match: Match):

    p1 = match.player1.name
    p2 = match.player2.name
    match_time = match.data["time"]

    p1_team = get_team_at_match_time(p1, match_time)
    p2_team = get_team_at_match_time(p2, match_time)

    if match.data["player1_team"] != p1_team:
        match.revise_metadata("player1_team", p1_team)

    if match.data["player2_team"] != p2_team:
        match.revise_metadata("player2_team", p2_team)

def pointhandler(match):
    p1_points, p2_points = calculate_points(match)
    update_points(match, p1_points, p2_points)
    revise_teams(match)
    return p1_points, p2_points
                
def main():
    p1_name = input("Enter player 1's name: ")
    p2_name = input("Enter player 2's name: ")
    tournament = input("Enter the tournament name or abbreviation: ")

    match = Match.Matchmaker(p1_name, p2_name, tournament)
    p1_points, p2_points = calculate_points(match)
    update_points(match, p1_points, p2_points)
    revise_teams(match)


if __name__ == "__main__":    
    main()