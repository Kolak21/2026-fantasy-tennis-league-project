#This is a library of helper functions for the Match object.
#This file will allow someone to write match data through standard input and it will write a json file
#This was separate from the Match.py file to make debugging easier
#Lowkey will be obselete once scraping works
'''lets go coco! wooooo! I am watching miami!!!!'''
import json
from tkinter.filedialog import test
from Player import Player
from typing import Dict, Any
from time import time
from datetime import datetime
import os
from Match import Match
import pointhandler

#Walkover (set to true if there is a walkover, false if there is a retirement)
def match_entry(p1: Player, p2: Player, walkover : bool, retire : bool, options: str = ""):
    p1_name = p1.get_name().lower()
    p2_name = p2.get_name().lower()

    #I do not wanna write AO times in manually so all of them will be about the same time
    options = options.lower()

    if options == "aopt":
        match_time = datetime(2026, 1, 22)
        time_ms = int(match_time.timestamp() * 1000)
        print("Using pre-trade AO date for match time.")
    elif options == "now":
        time_ms = int(time() * 1000)
        match_time = datetime.fromtimestamp(time_ms / 1000)
        print("Using current time for match time.")
    elif options == "nbo":
        match_time = datetime(2026, 8, 10)
        time_ms = int(match_time.timestamp() * 1000)
        print("Using pre-trade NBO date for match time.")

    # Input date with format and get unix timestamp in milliseconds
    else:
        time_input = input("Enter match time (YYYY-MM-DD): ")
        match_time = datetime.strptime(time_input, "%Y-%m-%d")
        time_ms = int(match_time.timestamp() * 1000)

    #all grand slams and masters tournaments
    slams = ["australian open","roland garros","wimbledon","us open"]
    masters = ["indian wells", "miami", "monte-carlo","madrid","rome","montreal","cincinnati","shanghai","paris"]
    
    #common abbreviations for grand slams
    abbreviations = {
        "ao": "australian open",
        "rg": "roland garros",
        "uso": "us open",
        "iw": "indian wells",
        "bnp":"indian wells"
    }


    
    #default stats to None since we don't have them yet, will be updated later when we get the match stats
    p1_stats = {
            "aces": None,
            "double_faults": None,
            "breaks": None,

            #Sets 
            "set1_games_won": None,
            "set1_games_lost": None,

            "set2_games_won": None,
            "set2_games_lost": None,

            "set3_games_won": None,
            "set3_games_lost": None,

            "set4_games_won": None,
            "set4_games_lost": None,

            "set5_games_won": None,
            "set5_games_lost": None,

            "games_won": None,
            "games_lost": None,

            "sets_won": None,
            "sets_lost": None,

            "points": 0
        }
    
    
    p2_stats = {
            "aces": None,
            "double_faults": None,
            "breaks": None,
            
            #Sets 
            "set1_games_won": None,
            "set1_games_lost": None,

            "set2_games_won": None,
            "set2_games_lost": None,

            "set3_games_won": None,
            "set3_games_lost": None,

            "set4_games_won": None,
            "set4_games_lost": None,

            "set5_games_won": None,
            "set5_games_lost": None,

            "games_won": None,
            "games_lost": None,

            "sets_won": None,
            "sets_lost": None,
            
            "points": 0
        }
    
    match_metadata = {}

    #Tournament input handling
    #note: Tournament type is assigned here slams are bo5 and masters are bo3

    tournament_type = None #Either slam or masters

    t_input = input("Enter tournament: ")

    if t_input in abbreviations:
        t_input = abbreviations[t_input]
    
    if t_input.lower() in slams:
        match_tournament = t_input.lower()
        tournament_type = "slam"

    elif t_input.lower() in masters:
        match_tournament = t_input.lower()
        tournament_type = "master"

        #No need for 4 or 5 sets 
        for x in range(4,6):
            p1_stats.pop(f"set{x}_games_won")
            p2_stats.pop(f"set{x}_games_won")

    elif t_input.lower() == "help":
        print("Valid tournament names: australian open, roland garros, wimbledon, us open, indian wells, miami, monte-carlo, madrid, rome, montreal, cincinnati, shanghai, paris")
        print("Abbreviations: ao (australian open), rg (roland garros), uso (us open), iw or bnp (indian wells)")
        return match_entry(p1,p2,walkover,retire,options)
    
    else:
        print("Invalid tournament name. Type 'help' for valid tournament names.")
        return match_entry(p1,p2,walkover,retire,options)
    
    #create filename for json file to be saved in matches folder, format is matches/player1_vs_player2_tournament.json
    filename = f"matches/{p1.last_name.lower()}_vs_{p2.last_name.lower()}_{match_tournament}.json"
    reverse_filename = f"matches/{p2.last_name.lower()}_vs_{p1.last_name.lower()}_{match_tournament}.json"

    #Check if file already exists to avoid duplicates, check both player1_vs_player2 and player2_vs_player1 since we don't know the order yet, if there is a duplicate we can just exit and let the user check the matches folder
    if os.path.exists(filename):

        raise FileExistsError((f"{filename} already exists. Please check the matches folder to avoid duplicates."))
    
    elif os.path.exists(reverse_filename):
        raise FileExistsError(f"{reverse_filename} already exists. Please check the matches folder to avoid duplicates.")
        
     
    #determine winner and loser
    winner_input = input(f"Who won the match? ({p1_name} or {p2_name}): ")
    if winner_input.lower() == p1_name or (winner_input.lower() in p1_name and not winner_input.lower() in p2_name):
        winner = p1_name
    elif winner_input.lower() == p2_name or (winner_input.lower() in p2_name and not winner_input.lower() in p1_name):
        winner = p2_name
    else:
        print("Invalid input. Please enter the name of the winner.")
        return match_entry(p1,p2,walkover,retire,options)
    
    loser = p2_name if winner == p1_name else p1_name
    

    
    if walkover:
        print(f"{winner} won by walkover.{loser} did not play.")

        #set all stats to 0 for the winner and None for the loser since they didn't play
        for stat in p1_stats:
            p1_stats[stat] = 0

        for stat in p2_stats:
            p2_stats[stat] = 0
        
        with open(filename, "w") as f:
            json.dump({
                "time": time_ms,
                "game_status": "walkover",
                "sets_played": 0,
                "player1": p1_name,
                "player1_team": p1.team,
                "player2": p2_name,
                "player2_team": p2.team,
                "tournament": match_tournament,
                "winner": winner,
                "loser": loser,
                "player1_stats": p1_stats,
                "player2_stats": p2_stats
            }, f, indent=4)
        return filename 
    
    print("Now we are doing match results. All match stats should be integers.")

    #This loops allow the stats to be re-entered instead of redoing the entire thing.
    is_stats_complete = False

    while not is_stats_complete:
        try:
            
            #determining how many sets were played based on the tournament type and the games won/lost for the winner
            p1_stats["sets_won"] = int(input(f"Enter {p1_name}'s total sets won: "))
            p1_stats["sets_lost"] = int(input(f"Enter {p1_name}'s total sets lost: "))

            sets_played = p1_stats["sets_won"] + p1_stats["sets_lost"]

            #adding the games won for each set 
            for x in range(1, sets_played + 1):
                p1_stats[f"set{x}_games_won"] = int(input(f"Enter {p1_name}'s games won in set {x}: "))
                p1_stats[f"set{x}_games_lost"] = int(input(f"Enter {p1_name}'s games lost in set {x}: "))
            
            #winner consistency checks
            if winner == p1_name and p1_stats["sets_won"] <= p1_stats["sets_lost"] and not retire:
                raise ValueError(f"Inconsistent input: {p1_name} is the winner but has less or equal sets won than lost.")
            
            if winner == p2_name and p1_stats["sets_won"] >= p1_stats["sets_lost"] and not retire:
                raise ValueError(f"Inconsistent input: {p2_name} is the winner but {p1_name} has more or equal sets won than lost.")
                
            #We can calculate the total games won and lost based on the games won and lost in each set
            p1_stats["games_won"] = 0
            p1_stats["games_lost"] = 0

            for x in range(1, sets_played + 1):
                    print(f"Adding set {x} games won and lost to total.")
                    p1_stats["games_won"] += p1_stats.get(f"set{x}_games_won", 0)
                    p1_stats["games_lost"] += p1_stats.get(f"set{x}_games_lost", 0)

            #adding the other stats that are not games or sets for player 1
            p1_stats["aces"] = int(input(f"Enter {p1_name}'s aces: "))
            p1_stats["double_faults"] = int(input(f"Enter {p1_name}'s double faults: "))
            p1_stats["breaks"] = int(input(f"Enter {p1_name}'s breaks: ")) 
            
            #For games and sets lost we can calculate them based on the games and sets won for the other player
            p2_stats["games_lost"] = p1_stats["games_won"]
            p2_stats["sets_lost"] = p1_stats["sets_won"]
            p2_stats["games_won"] = p1_stats["games_lost"]
            p2_stats["sets_won"] = p1_stats["sets_lost"]
            
            p2_stats["set1_games_lost"] = p1_stats["set1_games_won"]
            p2_stats["set1_games_won"] = p1_stats["set1_games_lost"]
            p2_stats["set2_games_lost"] = p1_stats["set2_games_won"]
            p2_stats["set2_games_won"] = p1_stats["set2_games_lost"]
            
            if sets_played >= 3:
                p2_stats["set3_games_lost"] = p1_stats["set3_games_won"]
                p2_stats["set3_games_won"] = p1_stats["set3_games_lost"]
                if sets_played >= 4:
                    p2_stats["set4_games_lost"] = p1_stats["set4_games_won"]
                    p2_stats["set4_games_won"] = p1_stats["set4_games_lost"]
                    if sets_played == 5:
                        p2_stats["set5_games_lost"] = p1_stats["set5_games_won"]
                        p2_stats["set5_games_won"] = p1_stats["set5_games_lost"]

            #adding the rest of the stats for player 2
            p2_stats["aces"] = int(input(f"Enter {p2_name}'s aces: "))
            p2_stats["double_faults"] = int(input(f"Enter {p2_name}'s double faults: "))
            p2_stats["breaks"] = int(input(f"Enter {p2_name}'s breaks: "))
        
        except ValueError as e:
            print(f"Error: {e}")
            print("Invalid input. Please enter integers for all stats.")
            continue 
        
        #Confirm the stats with the user before saving
        print("Summary of match results:")
        print(f"{winner} def {loser} at {match_tournament} on {match_time.strftime('%Y-%m-%d')}")
        
        print(f"{p1_name}'s stats:")
        print(p1_stats)

        print(f"{p2_name}'s stats:")
        print(p2_stats)

        confirm = input("Are these stats correct? (Y/n)? : ")
        if confirm.lower() == "y":
            with open(filename, "w") as f:
                json.dump({
                    "time": time_ms,
                    "game_status": "complete" if not retire else "retirement",
                    "sets_played": sets_played,
                    "player1": p1_name,
                    "player1_team": p1.team,
                    "player2": p2_name,
                    "player2_team": p2.team,
                    "tournament": match_tournament,
                    "winner": winner,
                    "loser": loser,
                    "player1_stats": p1_stats,
                    "player2_stats": p2_stats
                }, f, indent=4)
            print(f"Match data saved to {filename}")
            is_stats_complete = True
            return filename 
        else: 
            print("Let's try entering the stats again.")

            for stat in p1_stats:
                if stat not in ["sets_won", "sets_lost", "games_won", "games_lost", "points"]:
                    p1_stats[stat] = None
            for stat in p2_stats:
                if stat not in ["games_lost", "sets_lost", "games_won", "sets_won", "points", "set1_games_lost", "set1_games_won", "set2_games_lost", "set2_games_won", "set3_games_lost", "set3_games_won", "set4_games_lost", "set4_games_won", "set5_games_lost", "set5_games_won"]:
                    p2_stats[stat] = None
            continue

def main():
    p1_input = input("Enter player 1's name: ")
    p2_input = input("Enter player 2's name: ")
    walkover_input = input("Was there a walkover? (Y/n): ")
    options_input = (input("Enter the options (AO pretrade): ")).lower()

    p1 = Player.grab_player(p1_input.split()[0], p1_input.split()[1] + (" " + p1_input.split()[2] if len(p1_input.split()) > 2 else "") + (" " + p1_input.split()[3] if len(p1_input.split()) > 3 else ""))
    p2 = Player.grab_player(p2_input.split()[0], p2_input.split()[1] + (" " + p2_input.split()[2] if len(p2_input.split()) > 2 else "") + (" " + p2_input.split()[3] if len(p2_input.split()) > 3 else ""))

    #If there is a walkover we can skip retirement
    if walkover_input.lower() == "y":
        walkover = True
        filename = match_entry(p1, p2, walkover, False, options_input)
    
    else:
        retire_input = input("Was there a retirement? (Y/n): ")
        if retire_input.lower() == "y":
            retire = True
        else:
            retire = False
        filename = match_entry(p1, p2, False, retire, options_input)

    match = Match.File2Match(filename)
    pointhandler.pointhandler(match)



if __name__ == "__main__":
    main()