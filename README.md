# Double Fault Fantasy

Double Fault Fantasy is a Discord bot that manages a fantasy ATP tennis league. (although WTA would be more interesting)

The bot is written in Python using mainly `discord.py` and Selenium.

---

## Features

- 🎾 Fantasy ATP league management
- 📝 Snake draft system
- 🤝 Player trading
- 👥 Team management
- 📊 On-demand ATP data scraping
- 💾 Persistent league storage
- 💬 Discord command interface

---

## Libraries Used

The project uses the following external Python libraries:

- `discord.py`
- `pandas`
- `requests`
- `selenium`
- `Unidecode`

---

## To install external libraries 

Run in powershell for windows or terminal using mac/linux

`` pip install discord.py; pip install pandas; pip install requests;pip install selenium pip install Unidecode``

---


---
# Table of Contents

- [Project Structure](#project-structure)
- [Design Choices](#design-choices)
- [Core Programs](#core-programs)
- [Core Classes](#core-classes)
- [Player Acquisition](#player-acquisition)
- [Match Handling](#match-handling)
- [Persistent Data](#persistent-data)
- [Adding Match Entries](#manually-adding-match-entries)

---

# Project Structure

```
DoubleFaultFantasy/
│
├── bot.py
├── scrapers.py
│
├── League.py ── Team.py ── Player.py
├── Draft.py
├── TradeRequest.py
├── Match.py
│
├── matchentry.py
├── pointhandler.py
│
├── players.csv
├── Teams.csv
├── log.db
└── Match JSON files
```

---

# Core Programs

## `bot.py`

The main entry point for the application.

Responsibilities:


- Starts the Discord bot
- Loads league data into memory
- Registers Discord commands
- Handles user interaction
- Coordinates league operations (Draft, Trade, etc...)

### Bot initialization

```
league = League("Double Fault Fantasy Tennis League")
league.load_players_from_csv() # via players.csv, salaries in memory equal current pts from csv
league.load_teams_from_csv() # via teams.csv, players get put in teams in memory, salaries in memory get changed to csv value
league.get_active_players() # teams in memory are now correct, so make list of players on teams
league.write_teams_to_csv() # then, for some reason, write teams into teams.csv (idk why i put this here but im leaving it for now)
league.read_all_matches() # loads all json matches into memory
league.recalc_all_match_scores() #recalculates all fo the scores for every match 

```

All player, team, and match data are loaded into memory when the bot starts up. 



---

## `scrapers.py`

Responsible for collecting ATP data.

Scrapes live atp leaderboard from livetennis.eu

updates the players.csv

---

# Core Classes

## `League.py`

Represents the fantasy league itself.

Responsible for:

- League settings
- Registered teams
- Player ownership
- Transactions
- Overall league state

---

## `Player.py`

Represents an individual ATP player.

Contains information such as:

- Name
- Ranking
- Statistics
- Current fantasy owner

---

## `Team.py`

Represents a fantasy team.

Stores:

- Team name
- Owner
- Roster
- Team statistics

---

## `TradeRequest.py`

Represents a proposed trade between two teams.

Responsible for:

- Validating trades
- Accepting trades
- Rejecting trades
- Tracking pending requests

---

## `Draft.py`

Handles the fantasy draft.

Responsibilities include:

- Snake draft order
- Pick validation
- Available player pool
- Draft progression

---

## `Match.py`

Represents an ATP match used for fantasy scoring.

Contains:

- Players
- Match statistics
- Results
- Fantasy point calculations

---

# Player Acquisition

Players can be acquired through several systems.

## Draft

New leagues use the snake draft implemented in:

- `Draft.py`

## Trades

Managers can exchange players using:

- `TradeRequest.py`

## League Management

Ownership and roster validation are managed by:

- `League.py`

---

# Match Handling

Match processing is split across multiple modules.

## `matchentry.py`

Creates and stores match entries.

## `Match.py`

Represents the match object and its data.

## `pointhandler.py`

Calculates fantasy points based on completed matches.

---

# Persistent Data

The bot stores information across multiple files.

| File | Purpose |
|-------|----------|
| Match JSON files | Individual match information |
| `Teams.csv` | Fantasy team data |
| `players.csv` | Player information |
| `log.db` | Logging and historical data |

---

# Design Choices

## Why are there so many classes?

Each class is designed with a single responsibility. Separating functionality into smaller, focused objects makes the codebase easier to:

- Debug
- Maintain
- Extend
- Test

Most of these objects are loaded into memory when the bot starts. This minimizes disk access during runtime and allows Discord commands to respond quickly.

---

## Why do many functions return `(success, value)`?

Many functions return a tuple structured like this:

```python
(success, value)
```

or

```python
(success, error_message)
```

instead of raising exceptions for expected failures.

Example:

```python
success, team = league.get_team(team_name)

if success:
    print(team.owner)
else:
    print(team)
```

This approach makes it straightforward to provide meaningful feedback to Discord users while keeping error handling explicit and easy to follow.

---

## Coding Style

Please follow these conventions when contributing:

- Use **snake_case** for:
  - Variables
  - Functions
  - Methods

- Use descriptive variable names.

- Keep functions focused on a single responsibility.

- Document public methods when appropriate.

---

# Future Improvements

Checklist:

- Cleaning up titles json
- Automating match scraping and atp leaderboard scraping
- Adding point breakdown as a command
- Adding bonus points for winning titles

---
# Manually Adding Match Entries
---

## 1. Find a match that an active player played
- All active players are in teams.csv
- Links to tournament's draw are also above (Start by submitting the a player's Australian Open run and go down to Wimby)

## 2. Run matchentry.py 

Command Line/Terminal
   ```
    Python3 matchentry.py
   ```

Alternatively you can use VScode or any other IDE to start the program.

## 3. Enter player's name and indicate whether there was a walkover

Example:

``` 
    Enter player 1's name: Chris P. Bacon 

    Enter player 2's name: Diana Murder

    Was there a walkover? (Y/n): Y

    Enter the options (AO pretrade): (type "now" to set to current time otherwise press enter to leave blank)
```

## 4. Entering match time

If the player's name was entered correctly, you will be prompted to enter the date(if not set to another time already) and the tournament the match was played.
```
Enter match time (YYYY-MM-DD): (enter date of match or the day your are entering this)
```

## 5. Entering tournament
```
    #all grand slams and masters tournaments
    slams = ["australian open","roland garros","wimbledon","us open"]
    masters = ["indian wells", "miami", "monte-carlo","madrid","rome","montreal","cincinnati","shanghai","paris"]
```

For some tournaments they have common abbreviations and will help entering the tournament name easier

```
    #common abbreviations for grand slams
    abbreviations = {
        "ao": "australian open",
        "rg": "roland garros",
        "uso": "us open",
        "iw": "indian wells",
        "bnp":"indian wells"
    }
```

## 6. Checking for Duplicates
If the match entry was already submitted, then you will get the following message:

``` 
player1_vs_player2_tournament already exists please check the matches folder to avoid duplicates
```

In that case the json file already exists

## 7. For the rest, you can enter the match stats accordingly.

Enter the rest of the stats. When completed, the scores will automatically calculate.


---
