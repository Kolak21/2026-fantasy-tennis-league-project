import json
from Player import Player
from typing import List, Tuple
import os

# Match class meant to work with manually inputted matches (must be changed to a new version for scraping)
class Match:
    def __init__(self, player1: Player, player2: Player, tournament: str):
        print(f"Initializing match between {player1.get_name()} and {player2.get_name()} at {tournament}\n")

        self.player1 = player1
        self.player2 = player2
        self.data = {}
        self.reversed_order = False

        # all grand slams and masters tournaments
        tournaments = [
            "australian open", "roland garros", "wimbledon", "us open",  # grand slams
            "indian wells", "miami", "monte-carlo", "madrid", "rome",
            "montreal", "cincinnati", "shanghai", "paris"  # the masters
        ]

        # common abbreviations for grand slams
        abbreviations = {
            "ao": "australian open",
            "rg": "roland garros",
            "uso": "us open",
            "iw": "indian wells",
            "bnp": "indian wells"
        }

        tournament = tournament.lower()

        if tournament in abbreviations:
            self.tournament = abbreviations[tournament]

        elif tournament in tournaments:
            self.tournament = tournament

        else:
            self.tournament = tournament
        

        # searching for the json file for the match
        self.filename = (
            f"matches/{self.player1.last_name.lower()}_vs_"
            f"{self.player2.last_name.lower()}_{self.tournament}.json"
        )

        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                self.data = json.load(f)

                # process the data to update player stats and points
                # update player points based on match result
                # update player stats based on match result

                print(
                    f"Match data for {self.player1.get_name()} vs "
                    f"{self.player2.get_name()} at {self.tournament} loaded successfully.\n"
                )

        # checking to see if it was saved with the players in the opposite order
        else:
            reverse_filename = (
                f"matches/{self.player2.last_name.lower()}_vs_"
                f"{self.player1.last_name.lower()}_{self.tournament}.json"
            )

            if os.path.exists(reverse_filename):
                self.filename = reverse_filename
                self.reversed_order = True

                with open(self.filename, "r") as f:
                    self.data = json.load(f)

                    # process the data to update player stats and points
                    # update player points based on match result
                    # update player stats based on match result

                    print(
                        f"Match data for {self.player2.get_name()} vs "
                        f"{self.player1.get_name()} at {self.tournament} loaded successfully.\n"
                    )

            else:
                raise FileNotFoundError(
                    f"Match data not found for "
                    f"{self.player1.get_name()} vs {self.player2.get_name()} "
                    f"at {self.tournament}"
                )

    def revise_stats(self, player: Player, stat: str, value: int):
        if player == self.player1:
            key = "player1_stats" if not self.reversed_order else "player2_stats"
        elif player == self.player2:
            key = "player2_stats" if not self.reversed_order else "player1_stats"
        else:
            raise ValueError("Player is not part of this match.")

        self.data[key][stat] = value

        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)

    def update_scores(self, p1_score: int, p2_score: int):
        if not self.reversed_order:
            self.data["player1_stats"]["points"] = p1_score
            self.data["player2_stats"]["points"] = p2_score
        else:
            self.data["player1_stats"]["points"] = p2_score
            self.data["player2_stats"]["points"] = p1_score

        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)

    def revise_metadata(self, key, value):
        self.data[key] = value

        print(f"Revised {key} to {value} for match between {self.player1.get_name()} and {self.player2.get_name()} at {self.tournament}.")
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)

    @staticmethod
    def Matchmaker(player1_name, player2_name, tournament):
        p1_parts = player1_name.split()
        p2_parts = player2_name.split()

        player1 = Player.grab_player(
            p1_parts[0],
            " ".join(p1_parts[1:])
        )

        player2 = Player.grab_player(
            p2_parts[0],
            " ".join(p2_parts[1:])
        )

        match = Match(player1, player2, tournament)
        return match

    @staticmethod
    def File2Match(filename):
        with open(filename, "r") as f:
            data = json.load(f)
    
        p1_parts = data["player1"].split()
        p2_parts = data["player2"].split()

        try:
            player1 = Player.grab_player(
                p1_parts[0],
                " ".join(p1_parts[1:])
            )
        except ValueError:
            player1 = Player(p1_parts[0], " ".join(p1_parts[1:]), "Unknown", 0, "NO", 0) 

        try:
            player2 = Player.grab_player(
                p2_parts[0],
                " ".join(p2_parts[1:])
            )
        except ValueError:
            player2 = Player(p2_parts[0], " ".join(p2_parts[1:]), "Unknown", 0, "NO", 0)

        match = Match(player1, player2, data["tournament"])
        return match
        
        


def main():
    p1_name = input("Enter player 1's full name: ")
    p2_name = input("Enter player 2's full name: ")
    tournament = input("Enter the tournament name or abbreviation: ")

    try:
        match = Match.Matchmaker(p1_name, p2_name, tournament)
        print(match.data)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
