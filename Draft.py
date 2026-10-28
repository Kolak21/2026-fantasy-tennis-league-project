import random
from typing import List, Optional
from Team import Team
from Player import Player
import logger
import csv
''' Hoo boy this is a big one. This class manages a snake draft system for a fantasy league.
    This is making me lose my mind lol. I thought this would be sunshine and rainbows.'''

class SnakeDraft:
    def __init__(  #parameters 
        self,
        teams: List[Team],
        available_players: List[Player],
        rounds: int = 6,
        draft_order: Optional[List[Team]] = None,
        shuffle: bool = False
    ):
        # Load available players from CSV if not provided
        with open('players.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Team'] == "NO" and len(available_players) == 0:
                    print("available players empty, loading from CSV")
                    player = Player.grab_player(row['FirstName'], row['LastName'])
                    available_players.append(player)

        if draft_order and shuffle: 
            raise ValueError("Provide draft_order OR shuffle, not both.")

        if draft_order:
            self.teams = draft_order[:]
        else:
            self.teams = teams[:]
            if shuffle:
                random.shuffle(self.teams)

        self.available_players = available_players[:]
        self.rounds = rounds

        self.current_round = 1
        self.current_pick_index = 0
        self.forward = True  # direction flag
        self.is_complete = False

    # ------------------------
    # Draft State
    # ------------------------

    def current_team(self) -> Team:
        return self.teams[self.current_pick_index]

    def is_snake_round(self) -> bool:
        return not self.forward

    # ------------------------
    # Pick Logic
    # ------------------------

    def pick_player(self, team: Team, player: Player):
        if self.is_complete:
            return False, "Draft is complete."

        if team != self.current_team():
            return False, "It is not your turn."

        if player not in self.available_players:
            return False, "Player already drafted."

        success, message = team.add_player(player)
        if not success:
            return False, message

        self.available_players.remove(player)
        
        #add to log
        logger.Entry(team.discord_id,player.name,"draft")

        for p in self.available_players: #Debug: print remaining players
            print(f"Remaining Player: {p.get_name()}")

        self._advance_pick()

        return True, f"{team.team_name} selected {player.get_name()}."

    # ------------------------
    # Internal Mechanics
    # ------------------------

    # Advance to the next pick in the draft order
    def _advance_pick(self):
        if self.forward:
            self.current_pick_index += 1
            if self.current_pick_index >= len(self.teams):
                self.current_round += 1
                if self.current_round > self.rounds:
                    self.is_complete = True
                    return
                self.forward = False
                self.current_pick_index = len(self.teams) - 1
        else:
            self.current_pick_index -= 1
            if self.current_pick_index < 0:
                self.current_round += 1
                if self.current_round > self.rounds:
                    self.is_complete = True
                    return
                self.forward = True
                self.current_pick_index = 0
    
    def reset_draft(self):
        self.current_round = 1
        self.current_pick_index = 0
        self.forward = True
        self.is_complete = False

# Using the main function to test the SnakeDraft class
def main():
    print("=== SnakeDraft Test ===")

    teams = ["Team A", "Team B", "Team C"]

    p1= Player.grab_player("Carlos", "Alcaraz")
    p2 = Player.grab_player("Jannik", "Sinner")
    p3 = Player.grab_player("Alexander", "Zverev")
    p4 = Player.grab_player("Novak", "Djokovic")
    p5 = Player.grab_player("Stefanos", "Tsitsipas")
    p6 = Player.grab_player("gael", "monfils")
    p7 = Player.grab_player("Taylor", "Fritz")
    p8 = Player.grab_player("Cameron", "Norrie")
    p9 = Player.grab_player("Andrey", "Rublev")
    p10 = Player.grab_player("Felix", "Auger-Aliassime")
    p11 = Player.grab_player("Daniil", "Medvedev")
    p12 = Player.grab_player("Rafael", "Nadal")
    p13 = Player.grab_player("Hubert", "Hurkacz")
    p14 = Player.grab_player("Diego", "Schwartzman")
    p15 = Player.grab_player("Matteo", "Berrettini")
    p16 = Player.grab_player("Jenson", "Brooksby")
    p17 = Player.grab_player("Frances", "Tiafoe")
    p18 = Player.grab_player("Grigor", "Dimitrov")


    players = [p1, p2, p3, p4, p5, p6, p7, p8, p16, p9, p10, p11, p12, p13, p14, p15, p17, p18]
    draft = SnakeDraft(teams, players)

    picks = draft.run_draft()

    for pick in picks:
        print(f"Round {pick[0]}: {pick[1]} picks {pick[2]}")

    assert len(picks) == 18
    print("SnakeDraft test PASSED")


if __name__ == "__main__":
    main()
