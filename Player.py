import csv
from unidecode import unidecode

class Player: #Player attributes from corresponding csv file fields
    def __init__(self, first_name: str, last_name: str, nation: str, points: int, team: str = "NO", score: int = 0, rank: int = 0):
        self.first_name = first_name
        self.last_name = last_name
        self.nation = nation
        self.salary = int(points)  #Salary = Points but freezes value when on a team
        self.points = int(points) #Current Points
        self.team = team #Initial team set to NO
        self.score = int(score)  #Used for scoring in matches
        self.rank = int(rank) 

    @staticmethod
    # Fetches player from csv file based on first and last name
    def grab_player(first_name, last_name):
        with open("players.csv", newline='') as csvfile:

            print(f"Searching for player: {first_name} {last_name}")

            reader = csv.DictReader(csvfile)
            for row in reader:
                if clean_name(row['FirstName']) == clean_name(first_name) and clean_name(row['LastName']) == clean_name(last_name):
                    return Player(
                        first_name=row['FirstName'],
                        last_name=row['LastName'],
                        nation=row['Nation'],
                        points=row['Points'],
                        team=row['Team'],
                        rank=row['Rank']
                    )
            print("Player Not Found\n")
            
            raise ValueError(f"Player {first_name} {last_name} not found in CSV.")
            
    
    #Changes Player's Team attribute. Used when drafting, dropping or trading.
    #Leave blank to set to NO team(WAIVING)

    def change_team(self, newTeam="NO"):

        print(f"Changing team for {self.get_name()} from {self.team} to {newTeam}\n")

        self.salary = self.points  #Freeze salary to current points when changing teams
        self.team = newTeam
    

    #Update salary to current points
    def updateSalary(self):
        print(f"Updating salary for {self.get_name()} from {self.salary} to {self.points}\n")
        self.salary = self.points

    def add_score(self, points: float):
        self.score += points
        self.score = round(self.score, 2)  # Round to 2 decimal places

    def reset_score(self):
        self.score = 0
    
    # Updates Player's points and nation from the csv file DOES NOT CHANGE SALARY
    def update(self):
        with open("players.csv", newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['FirstName'] == self.first_name and row['LastName'] == self.last_name:
                    self.nation = str(row['Nation'])
                    self.points = int(row['Points'])
                    break
    
    def get_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"
    
    # String representation of the Player
    def __str__(self):
        return f"{self.first_name} {self.last_name}, Nation: {self.nation}, Salary: {self.salary}, Points: {self.points}, Team: {self.team}"
    
    # Less than comparison based on points for sorting
    def __lt__ (self, other):
        return self.points < other.points
    
    #
    
    # Equality check based on first and last name
    def __eq__(self, other):
        return self.first_name == other.first_name and self.last_name == other.last_name

# Helper function to clean names for comparison
def clean_name(name: str) -> str:
    return unidecode(name).strip().lower() 


def main():
    player1 = Player.grab_player("Ben", "Shelton")
    player2 = Player.grab_player("Felix", "Auger-Aliassime")
    player3 = Player.grab_player("Novak", "Djokovic")
    player4 = Player.grab_player("Carlos", "Alcaraz")
    
    print(player1)
    print(player2)
    print(player3)
    
    print(f"Is {player1.get_name()} worth less points than {player2.get_name()}? {'Yes' if player1 < player2 else 'No'}")
    print(f"Is {player2.get_name()} equal to {player3.get_name()}? {'Yes' if player2 == player3 else 'No'}")

    player1.change_team("TeamA")
    print(f"{player1.get_name()} is now on team: {player1.team} with a frozen salary of: {player1.salary}")

    print(f"{player4.get_name()} is ranked world {player4.rank}")

if __name__ == "__main__":
    main()
