#code for the individual manager class for our fantasy league

from typing import List, Tuple
from Player import Player

class Team:
    MAX_PLAYERS = 6  #Maximum number of players allowed on a team

    def __init__(self, manager_name: str, team_name: str):
        self.manager_name = manager_name
        self.team_name = team_name


        self.players: List[Player] = [] #Initial empty roster of 6 players
        self.playersleft = Team.MAX_PLAYERS  #Tracks how many player slots are left

        self.salary_cap = 20000 #Total salary cap for the team
        self.balance = self.salary_cap #updates based on teams.csv 

        self.total_score = 0  #Total score of all players on the team

        self.discord_id = "None"  #Placeholder for Discord user ID

        self.autonomy = False #Placeholder for whether the user is able to use bot commmand independetly from admins
        print(f"team {self.team_name} created!")
    
    def rename_team(self, new_name) -> Tuple[bool, str]:
        if len(new_name) > 0:
            self.team_name = new_name
            return True, "Team renamed successfully."
        elif len(new_name) > 30:
            return False, "Team name too long. Maximum 30 characters."
        else:
            return False, "Invalid team name."

    def add_player(self, player: Player) -> Tuple[bool, str]:

        if len(self.players) >= self.MAX_PLAYERS:  #Too many players
            return False, "Roster is full."

        if player.salary > self.balance: #Not enough salary cap
            return False, "Insufficient salary cap."

        else: #Successfully add player
            self.players.append(player)  
            self.balance -= player.salary
            player.change_team(self.team_name)

        return True, f"{player.get_name()} added to {self.team_name}."
    
    def waivesign(self, waive: Player, sign: Player) :

        self.players.remove(waive)
        self.balance += waive.salary
        waive.change_team()  #Set player team to NO
        waive.update()
        waive.updateSalary()

        self.players.append(sign)
        self.balance -= sign.salary
        sign.change_team(self.team_name)
        sign.update()
        sign.updateSalary()

    def add_score(self, points: float):
        self.total_score += points
        self.total_score = round(self.total_score, 2)  # Round to 2 decimal places

    def reset_score(self):
        self.total_score = 0
    # ------------------------
    # Trade Validation
    # ------------------------

    def can_trade(
        self,
        other: "Team",
        export_player: Player,
        import_player: Player,
        cash: int = 0
    ) -> Tuple[bool, str]:

        if export_player not in self.players:
            return False, "Export player not on your roster."

        if import_player not in other.players:
            return False, "Import player not on opposing roster."

        if import_player.salary - export_player.salary + cash > self.balance:
            return False, "You cannot afford this trade."

        if export_player.salary - import_player.salary + cash > other.balance:
            return False, "Other team cannot afford this trade."

        return True, "Trade is valid."
    
    def can_waive(
        self,
        export_player: Player,
        import_player: Player,
    ) -> Tuple[bool, str]:

        if import_player.salary - export_player.salary > self.balance:
            return False, "You cannot afford to sign this player."

        return True, "Signing is valid."

    def get_total_score(self):
        return round(self.total_score,2)

    # ------------------------
    # Trade Execution
    # ------------------------
    def preview_trade(
        self,
        other: "Team",
        export_player: Player,
        import_player: Player,
        cash: int = 0
    ) -> Tuple[bool, str]:

        valid, message = self.can_trade(other, export_player, import_player, cash)
        if not valid:
            return False, message

        return True, (
            f"Trade Preview:\n"
            f"You give: {export_player.get_name()} + ${cash}\n"
            f"You receive: {import_player.get_name()}\n"
            f"New Salary after trade: ${self.balance - import_player.salary + export_player.salary - cash}"
        )

    def execute_trade(
        self,
        other: "Team",
        export_player: Player,
        import_player: Player,
        cash: int = 0
    ) -> Tuple[bool, str]:

        valid, message = self.can_trade(other, export_player, import_player, cash)
        if not valid:
            return False, message

        # Swap players
        self.players.remove(export_player)
        other.players.remove(import_player)

        self.players.append(import_player)
        other.players.append(export_player)

        # Adjust salaries
        self.balance += export_player.salary - import_player.salary - cash
        other.balance += import_player.salary - export_player.salary + cash

        # Update player teams
        export_player.change_team(other.team_name)
        import_player.change_team(self.team_name)

        if cash <= 0:
            message = f"Trade completed: {export_player.name} ↔ {import_player.name}"
        else:
            message = f"Trade completed: {export_player.name} ↔ {import_player.name}\n Cash: {cash}"
            
        return True, message
    

    
    def overview(self):
        return f"{self.team_name} managed by {self.manager_name}\nSalary:{self.balance}\nPoints:{self.total_score}"
    
    def __lt__(self,other) -> bool:
        return self.total_score < other.total_score 
    
    def __str__(self)-> str:
        return f"{self.manager_name}'s {self.team_name}"
    


def main():
    team1 = Team("KolakDSexy","Bolabinga Tennis Club")
    team2 = Team("Julian", "Habibi Tennis")
    print(team1)

    team1.rename_team("Celtics")
    print(team1)

    print(team1.overview())


if __name__ == "__main__":
    main()
