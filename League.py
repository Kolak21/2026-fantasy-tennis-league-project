from typing import List, Tuple
from discord import player
from Team import Team
from TradeRequest import TradeRequest
from Player import Player
from Draft import SnakeDraft
import csv
import pointhandler
from Match import Match
import os
import json


class League:
    def __init__(self, league_name: str):
        self.league_name = league_name
        self.teams: List[Team] = []
        self.trade_requests: List[TradeRequest] = []
        self.active_draft: SnakeDraft = None
        self.available_players: List[Player] = []
        self.active_players: List[Player] = []
        self.csv_filepath = "players.csv"
        self.csv_write_path = "players.csv"
        self.teams_csv_path = "teams.csv"
        self.matches: List[Match] = []
        
        print("League Initialized")
        msg = "All teams in the league!: \n"
        for team in self.teams:
            msg += f"Team Name: {team.team_name}\n"

    # ------------------------
    # Team Management
    # ------------------------

    def add_team(self, manager_name: str, team_name: str) -> Tuple[bool, str]:
        if any(t.manager_name == manager_name for t in self.teams):
            return False, "Manager already exists."

        self.teams.append(Team(manager_name, team_name))
        return True, "Team added successfully."

    def remove_team(self, team: Team) -> Tuple[bool, str]:
        if team not in self.teams:
            return False, "Team not found."

        self.teams.remove(team)
        return True, "Team removed successfully."

    def add_team_score(self, team_name: str, score: float) -> bool:
        for team in self.teams:
            if team.team_name == team_name:
                team.total_score += score
                return True
        return False

    # ------------------------
    # League Controls
    # ------------------------

    def freeze_all(self) -> None:
        for team in self.teams:
            team.autonomy = False

    def unfreeze_all(self) -> None:
        for team in self.teams:
            team.autonomy = True

    # ------------------------
    # Trades
    # ------------------------

    def propose_trade(
        self,
        from_team: Team,
        to_team: Team,
        offer_player,
        request_player,
        cash: int = 0
    ) -> Tuple[bool, str]:

        valid, message = from_team.can_trade(
            other=to_team,
            export_player=offer_player,
            import_player=request_player,
            cash=cash
        )

        if not valid:
            return False, message

        trade = TradeRequest(
            from_team=from_team,
            to_team=to_team,
            offer_player=offer_player,
            request_player=request_player,
            cash=cash
        )

        self.trade_requests.append(trade)
        return True, "Trade request created."

    def get_pending_trades(self) -> List[TradeRequest]:
        return [
            t for t in self.trade_requests
            if t.status.name == "PENDING"
        ]

    def remove_trade(self, trade: TradeRequest) -> None:
        if trade in self.trade_requests:
            self.trade_requests.remove(trade)

    # ------------------------
    # Standings
    # ------------------------

    def load_players_from_csv(self):
        self.available_players.clear()

        with open(self.csv_filepath, newline="") as csvfile:
            self.available_players.clear()
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["Team"] == "NO":
                    self.available_players.append(
                        Player(
                            first_name=row["FirstName"],
                            last_name=row["LastName"],
                            nation=row["Nation"],
                            points=int(row["Points"]),
                            team=row["Team"],
                            rank=row["Rank"]
                        )
                    )

    #Returns a list of all active players    
    def get_active_players(self):
        self.active_players.clear()

        with open(self.csv_filepath, newline="") as csvfile:
            self.active_players.clear()
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["Team"] != "NO":
                    self.active_players.append(
                        Player(
                            first_name=row["FirstName"],
                            last_name=row["LastName"],
                            nation=row["Nation"],
                            points=int(row["Points"]),
                            team=row["Team"],
                            rank=row["Rank"]
                        )
                    )
        return self.active_players

    def get_player(self, player_name: str) -> Player:
    # Find a player currently assigned to a team.
        for team in self.teams:
            for player in team.players:
                if player.get_name() == player_name:
                    return player

        return None

    def write_players_to_csv(self):
        with open(self.csv_filepath, newline="") as csvfile:
            rows = list(csv.DictReader(csvfile))
            fieldnames = rows[0].keys()

        for row in rows:
            for player in self.available_players:
                row["Team"] = "NO"

        for row in rows:
            for team in self.teams:
                for player in team.players:
                    if (
                        row["FirstName"] == player.first_name
                        and row["LastName"] == player.last_name
                    ):
                        row["Team"] = team.team_name

        with open(self.csv_write_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def standings(self) -> List[Team]:
        return sorted(self.teams, reverse=True)
    
    def start_draft(
        self,
        available_players: List[Player],
        rounds: int = 6,
        draft_order: List[Team] = None,
        shuffle: bool = False
    ) -> SnakeDraft:
        self.active_draft = SnakeDraft(
            teams=self.teams,
            available_players=available_players,
            rounds=rounds,
            draft_order=draft_order,
            shuffle=shuffle
        )
        return self.active_draft
    
    def _load_existing_team_ids(self) -> dict:
        ids = {}

        try:
         with open(self.teams_csv_path, newline="") as csvfile:
               reader = csv.DictReader(csvfile)
               for row in reader:
                    ids[row["TeamName"]] = row.get("id")
        except FileNotFoundError:
            pass

        return ids

    
    # This function takes teams from memory and writes them to teams.csv to preserve team rosters after draft
    # If there is not teams in memeory, it creates an empty teams.csv with headers only 
    # Please call this function after draft completion
    def write_teams_to_csv(self):
        saved_ids = self._load_existing_team_ids()

        with open(self.teams_csv_path, "w", newline="") as csvfile:
            fieldnames = [
                "id",
                "ManagerName", "TeamName", "Balance", 
                "P1", "P1Score", "P1Salary", 
                "P2", "P2Score", "P2Salary", 
                "P3", "P3Score","P3Salary", 
                "P4", "P4Score","P4Salary", 
                "P5", "P5Score","P5Salary", 
                "P6", "P6Score","P6Salary", 
                "TOTAL"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for team in self.teams:
                row = {
                    "id": team.discord_id,
                    "ManagerName": team.manager_name,
                    "TeamName": team.team_name,
                    "Balance": team.balance,
                    "TOTAL": round(team.total_score,2)
                }
                # Fill in player data  for each player slot
                for i, player in enumerate(team.players, start=1):
                    row[f"P{i}"] = player.get_name()
                    row[f"P{i}Score"] = round(player.score,2)
                    row[f"P{i}Salary"] = round(player.salary,2)
                writer.writerow(row)


    #loads teams from teams.csv import after draft to keep players assigned to teams
    # ------------------------
    # Team Loading
    # ------------------------              
    def load_teams_from_csv(self):
        with open(self.teams_csv_path, newline="") as csvfile:
            self.teams.clear()
            reader = csv.DictReader(csvfile)
            for row in reader:
                team = Team(row["ManagerName"], row["TeamName"])
                team.discord_id = row["id"]
                team.balance = int(row["Balance"])
                team.total_score = float(row["TOTAL"])
                for i in range(1, 7):  # Assuming max 6 players
                    player_name = row.get(f"P{i}")
                    if player_name:
                        first_name, last_name = player_name.split(" ", 1)
                        player = Player.grab_player(first_name, last_name)
                        if player:
                            team.players.append(player)
                            player.change_team(row["TeamName"])
                            player.salary = int(row.get(f"P{i}Salary"))
                            player.score = float(row.get(f"P{i}Score"))
                            player.update()
                self.teams.append(team)

    def get_team_dict(self):
        with open(self.teams_csv_path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            team_dict = {}

            for row in reader:
                team_name = row["TeamName"]
                manager_name = row["ManagerName"]

                team_dict[team_name] = Team(manager_name, team_name)
                team_dict[team_name].discord_id = row["id"]

            return team_dict
    
    #loads teams from players csv import after draft to keep players assigned to teams at startup 
    def load_teams_from_playerscsv(self):
        team_dict = self.get_team_dict()

        with open(self.csv_filepath, newline="") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                team_name = row["Team"]

                if team_name != "NO" and team_name in team_dict:
                    player = Player.grab_player(
                        row["FirstName"],
                        row["LastName"]
                    )

                    if player:
                        team_dict[team_name].players.append(player)

        self.teams = list(team_dict.values())
    
    #adding match support to league, this will be used for point distribution and updating player stats after matches
    def read_all_matches(self):
        self.matches = []
        for filename in os.listdir("matches"):
            if filename.endswith(".json"):
                full_path = os.path.join("matches", filename)
                match = Match.File2Match(full_path)
                self.matches.append(match)
        return self.matches
    
    def recalc_all_match_scores(self):
        for m in self.matches:
            pointhandler.pointhandler(m)
        return

    def rebuild_scores(self):
        """
        Completely rebuild all fantasy scores from historical matches.

        Existing player scores are discarded.
        Every match is recalculated using the current scoring rubric.
        The resulting player scores and team totals are written to teams.csv.
        """

        print("Rebuilding all scores from historical matches...")

        #1. Resetting all player scores to 0

        for team in self.teams:
            team.reset_score()
            for player in team.players:
                player.reset_score()

        print("All player scores reset to 0.")

        # =====================================================
        # 2. Create a historical player-score dictionary
        # =====================================================

        player_scores = {}

        # We use names as keys because Match data stores
        # player names rather than Player objects.
        
        # Example:
        #
        # player_scores["Valentin Vacherot"] = 123.45

       # =====================================================
       # 3. Load all historical matches
       # =====================================================


        print(f"Loaded {len(self.matches)} matches.")

        # =====================================================
        # 4. Recalculate every historical match
        # =====================================================

        for match in self.matches:

            # Recalculate this match using the current scoring
            # system.
            p1_score, p2_score = pointhandler.pointhandler(match)

            p1_name = match.player1.get_name()
            p2_name = match.player2.get_name()

            # -------------------------------------------------
            # Add points to PLAYER historical totals
            # -------------------------------------------------

            player_scores[p1_name] = (
                player_scores.get(p1_name, 0) + p1_score
            )

            player_scores[p2_name] = (
                player_scores.get(p2_name, 0) + p2_score
            )

            # -------------------------------------------------
            # Add points to TEAM historical totals
            # -------------------------------------------------

            p1_team = match.data.get("player1_team")
            p2_team = match.data.get("player2_team")

            if p1_team and p1_team != "NO":
                self.add_team_score(p1_team, p1_score)

            if p2_team and p2_team != "NO":
                self.add_team_score(p2_team, p2_score)

        
        #-------------------------------------------------
        # Adding bonus points for winning tournaments to the winning player INCOMPLETE, needs to be finished
        #-------------------------------------------------
        bonus_points = {
            "slams": 100,
            "masters": 50,
            "atp500": 25,
            "atp250": 12.5,
            }

        with open("2026_titles.json", "r") as f:
            titles_data = json.load(f)

            #slams 
            for slam in titles_data.get("slams", []):
                

                winner_name = titles_data["slams"][slam]["winner"]
                winner_team = pointhandler.get_team_at_match_time(winner_name, titles_data["slams"][slam]["time"])

                print(f" \nProcessing Slam bonus: {slam} with winner {winner_name} at {titles_data['slams'][slam]['time']} for team {winner_team}")

                if winner_name in player_scores:
                    player_scores[winner_name]= (bonus_points["slams"] + player_scores[winner_name])
                else:
                    player_scores[winner_name] = bonus_points["slams"]

                if winner_team != "NO":
                    self.add_team_score(winner_team, bonus_points["slams"])

            #masters
            for master in titles_data.get("masters", []):
                winner_name = titles_data["masters"][master]["winner"]
                winner_team = pointhandler.get_team_at_match_time(winner_name, titles_data["masters"][master]["time"])

                print(f" \nProcessing Masters bonus: {master} with winner {winner_name} at {titles_data['masters'][master]['time']} for team {winner_team}")

                if winner_name in player_scores:
                    player_scores[winner_name]= (bonus_points["masters"] + player_scores[winner_name])
                else:
                    player_scores[winner_name] = bonus_points["masters"]

                if winner_team != "NO":
                    self.add_team_score(winner_team, bonus_points["masters"])

            #500s
            for fivehundred in titles_data.get("500s", []):
                winner_name = titles_data["500s"][fivehundred]["winner"]
                winner_team = pointhandler.get_team_at_match_time(winner_name, titles_data["500s"][fivehundred]["time"])

                print(f" \nProcessing 500 bonus: {fivehundred} with winner {winner_name} at {titles_data['500s'][fivehundred]['time']} for team {winner_team}")

                if winner_name in player_scores:
                    player_scores[winner_name]= (bonus_points["atp500"] + player_scores[winner_name])
                else:
                    player_scores[winner_name] = bonus_points["atp500"]

                if winner_team != "NO":
                    self.add_team_score(winner_team, bonus_points["atp500"])

            #250s
            for twofifty in titles_data.get("250s", []):
                winner_name = titles_data["250s"][twofifty]["winner"]
                winner_team = pointhandler.get_team_at_match_time(winner_name, titles_data["250s"][twofifty]["time"])

                print(f" \nProcessing 250 bonus: {twofifty} with winner {winner_name} at {titles_data['250s'][twofifty]['time']} for team {winner_team}")

                if winner_name in player_scores:
                    player_scores[winner_name]= (bonus_points["atp250"] + player_scores[winner_name])
                else:
                    player_scores[winner_name] = bonus_points["atp250"]

                if winner_team != "NO":
                    self.add_team_score(winner_team, bonus_points["atp250"])
                



        # =====================================================
        # 5. Apply historical player totals to current
        #    Player objects
        # =====================================================

        for team in self.teams:
            for player in team.players:

                score = player_scores.get(
                    player.get_name(),
                    0
                )

                player.reset_score()
                player.add_score(score)

        # =====================================================
        # 6. Write everything to teams.csv
        # =====================================================

        self.write_teams_to_csv()

        print("All scores rebuilt and written to teams.csv.")

        # Optional debugging information
        print("\nFinal team scores:")

        for team in self.teams:
            player_sum = round(
            sum(player.score for player in team.players),
            2
        )
        return

    def add_player_score(self, player_name: str, points: float) -> bool:
    #"""Add match points to a rostered player."""

        player = self.get_rostered_player(player_name)

        if player is None:
            return False

        player.add_score(points)
        return True

    def get_rostered_player(self, player_name: str):
        for team in self.teams:
            for player in team.players:
                if player.get_name().lower() == player_name.lower():
                    return player
        return None
    
    
def get_available_players(filepath: str) -> List[Player]:
    players: List[Player] = []

    with open(filepath, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["Team"] == "NO":
                players.append(
                    Player(
                        first_name=row["FirstName"],
                        last_name=row["LastName"],
                        nation=row["Nation"],
                        points=int(row["Points"]),
                        team=row["Team"],
                        rank=row["Rank"]
                    )
                )
    return players

def main():
    league = League("Testing League!")

    league.add_team("A", "Team A")
    league.add_team("B", "Team B")

    team_a = league.teams[0]
    team_b = league.teams[1]

    p1 = Player.grab_player("Alexander","Zverev")
    p2 = Player.grab_player("Ben", "Shelton")

    print(p1.salary)
    print(team_a.balance)
    team_a.add_player(p1)
    team_b.add_player(p2)

    print(p1.get_name())
    print(p1.team)

    trade = TradeRequest(team_a, team_b, p1, p2, cash=10)

    assert trade.status.name == "PENDING"
    success, msg = trade.accept()

    print(success)

    if success == True:
        trade.execute()
    

    print("TradeRequest test PASSED")

    print(p1.get_name())
    print(p1.team)


    

if __name__ == "__main__":
    main()
