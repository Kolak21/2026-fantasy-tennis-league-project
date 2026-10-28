import discord
from discord.ext import commands
import logging
import random

from League import League
from Player import Player
from Draft import SnakeDraft
from TradeRequest import TradeRequest, TradeStatus
from unidecode import unidecode
import paginator
import logger
import csv 
import scrapers #commented out so debugging could be faster lol


#Startup tasks

logging.basicConfig(level=logging.INFO)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
owners = [343916381584097282, 1449543749385457798]
bot = commands.Bot(command_prefix='!', intents=intents, owner_ids = set(owners), help_command=None)

#Opening the league
league = League("Double Fault Fantasy Tennis League")
league.load_players_from_csv() # via players.csv, salaries in memory equal current pts from csv
league.load_teams_from_csv() # via teams.csv, players get put in teams in memory, salaries in memory get changed to csv value
league.get_active_players() # teams in memory are now correct, so make list of players on teams
league.matches = league.read_all_matches() #Load match data from matches folde
league.rebuild_scores() #rebuilds all match scores from json files and updates player scores in memory and updates teams.csv with new scores and total points for each team. This is the most important function to run at startup to ensure that all scores are correct and up to date.


available_players: list[Player] = league.available_players  # Load from CSV


# Helper functions
def get_team_by_mention(user_id: int):
    for team in league.teams:
        print(f"USING get_team_by_mention Comparing {user_id} with {team.discord_id}")
        if team.discord_id == user_id or str(team.discord_id) == str(user_id):
            return team
    return None

def find_player_by_name(name: str):
    for player in (league.available_players + league.active_players):
        if player.get_name().lower() == name.lower():
            return player
        elif player.last_name.lower() == name.lower(): 
            return player
    return None

def get_trade_by_id(trade_id: int):
    for trade in league.trade_requests:
        if trade.id == trade_id:
            return trade
    return None

def refresh_files(league: League):
    league.write_players_to_csv()
    league.write_teams_to_csv()
    league.load_players_from_csv()
    league.get_active_players()
    league.load_teams_from_csv()
# -------------------------
# Bot Events & Commands
# -------------------------

@bot.event
async def on_ready():
    print("Starting bot")
    print(f"{bot.user} is now running!")

@bot.command()
@commands.is_owner()
async def update_rankings(ctx):
    #overwrites all player data in players.csv to update to current atp rankings 
    #An important side effect is that it will say that none of the players are on the teams 
    scrapers.scrape_rankings() 
    refresh_files(league) #input player data to keep teams consistent
    await ctx.send("Rankings have been updated!")
    
@bot.command()
async def help(ctx):
    help_text = """
    **Fantasy Tennis Bot Commands:**
    `!add_team <team_name>` - Create a new team.
    `!start_draft [rounds] [shuffle]` - Start a snake draft.
    `!pick <player_name>` - Pick a player during your turn.
    `!propose_trade <offer_player> <request_player> [cash]` - Propose a trade.
    `!accept_trade <trade_id>` - Accept a trade proposal.
    `!reject_trade <trade_id>` - Reject a trade proposal.
    `!standings` - Show current league standings.
    `!myteam` - Show your team's roster and points.
    `!available` - List all available players. Also !free or !fa.
    `!waive <player_name> <free_agent_name>` - Waive a player from your team.
    `!sign_free_agent <player_name>` - Sign a free agent to your team.
    `!hello` - Greet the bot.
    `!refresh` - Manually updates the csv files to account for player activity (Usually **shouldn't** need to be used)
    `!teams` - Shows all team rosters.
    `!update_rankings` - Updates the ATP rankings used to most recent
    `!help` - Show this help message.
    """
    await ctx.send(help_text)

@bot.command()
async def add_team(ctx, team_name: str="Someone definitely did not add a team name", member: discord.Member = None):
    if team_name == "Someone definitely did not add a team name":
        await ctx.send("Please provide a team name. Usage: !add_team <team_name>")
        return
    
    #The default is to add the author of the command message as the team manager
    if member == None:
     discord_id = ctx.author.id
     success, msg = league.add_team(ctx.author.name, team_name)
     print(f"Team created!\nTeam: {team_name}\nManager Name: {ctx.author.name}\nDiscord ID: {ctx.author.id}")
     if success:
        team = league.teams[-1]
        team.discord_id = discord_id
        await ctx.send(msg)

    #If a member is provided, add the team to that member instead
    elif member != None:
     discord_id = member.id
     success, msg = league.add_team(member.name, team_name)
     print(f"Team created!\nTeam: {team_name}\nManager Name: {member.name}\nDiscord ID: {discord_id}")
     if success:
        team = league.teams[-1]
        team.discord_id = discord_id
        await ctx.send(msg)


@bot.command()
@commands.is_owner()
async def refresh(ctx):
    refresh_files(league)
    await ctx.send("All files are refreshed")
    return

@bot.command()
@commands.is_owner()
async def start_draft(ctx, rounds: int = 6, shuffle: bool = True):
    if not league.teams or not available_players:
        await ctx.send("League must have teams and available players to start a draft.")
        return
    league.active_draft = SnakeDraft(
        teams=league.teams,
        available_players=league.available_players,
        rounds=rounds,
        shuffle=shuffle
    )
    order = ", ".join(team.team_name for team in league.active_draft.teams)
    await ctx.send(f"Draft started! Order of picks:\n{order}")

@bot.command()
async def pick(ctx, player_name: str):
    if not league.active_draft:
        await ctx.send("No active draft.")
        return
    team = get_team_by_mention(ctx.author.id)
    if not team:
        await ctx.send("You do not have a team.")
        return
    player = find_player_by_name(player_name)
    if not player:
        await ctx.send("Player not found.")
        return
    if player not in league.active_draft.available_players:
        await ctx.send(f"{player.name} has already been drafted.")
        return
    success, msg = league.active_draft.pick_player(team, player)
    await ctx.send(msg)
    if league.active_draft.is_complete:
        refresh_files(league)
        await ctx.send("Draft is complete!")

@bot.command(aliases=["propose"])
async def propose_trade(ctx, offer_player_name: str, request_player_name: str, cash: int = 0):

    team = get_team_by_mention(ctx.author.id)
    offer_player = find_player_by_name(offer_player_name)
    request_player = find_player_by_name(request_player_name)
    if not team:
        await ctx.send("You do not have a team.")
        return
    if not offer_player:
        await ctx.send(f"Player '{offer_player_name}' not found.")
        return
    if offer_player not in team.players:
        await ctx.send(f"You do not own {offer_player.name}.")
        return
    if not request_player:
        await ctx.send(f"Player '{request_player_name}' not found.")
        return
    if request_player.team == team.team_name:
        await ctx.send(f"{request_player.name} is already on your team.")
        return

    other_team = next((t for t in league.teams if request_player in t.players), None)
    if not other_team:
        await ctx.send(f"{request_player.name} is not on any team.")
        return

    success,msg = team.can_trade(other_team,offer_player,request_player,cash)
    if not success:
        await ctx.send(msg)
        return

    trade = TradeRequest(team, other_team, offer_player, request_player, cash)
    league.trade_requests.append(trade)
    await ctx.send(f"**Trade {trade.id} proposed!**\n{team.team_name} wants to trade {offer_player.get_name()} for {other_team}'s {request_player.get_name()}")

@bot.command(aliases=["accept"])
async def accept_trade(ctx, trade_id: int):
    team = get_team_by_mention(ctx.author.id)
    trade = get_trade_by_id(trade_id)
    if not trade:
        await ctx.send("Trade not found.")
        return
    if team != trade.to_team:
        await ctx.send("You are not authorized to accept this trade.")
        return
    success, msg = trade.accept()
    await ctx.send(msg)
    if success:
        trade.execute()
        refresh_files(league)
        logger.Entry(trade.from_team.discord_id,trade.request_player.name,"trade")
        logger.Entry(trade.to_team.discord_id,trade.offer_player.name,"trade")
        league.trade_requests.remove(trade)

@bot.command(aliases=["reject"])
async def reject_trade(ctx, trade_id: int):
    team = get_team_by_mention(ctx.author.id)
    trade = get_trade_by_id(trade_id)
    if not trade:
        await ctx.send("Trade not found.")
        return
    if team != trade.to_team:
        await ctx.send("You are not authorized to reject this trade.")
        return
    trade.decline()
    await ctx.send(f"Trade ID {trade.id} rejected by {team.team_name}")
    league.trade_requests.remove(trade)

@bot.command()
async def standings(ctx):
    standings = sorted(league.teams, key=lambda t: t.get_total_score(), reverse=True)
    msg = "Standings:\n" + "\n".join(f"{idx+1}. {t.manager_name}'s {t.team_name} - {t.get_total_score()} pts" for idx, t in enumerate(standings))
    await ctx.send(msg)

@bot.event #Shows a message when bot is running 
async def on_ready():
        print(f'{bot.user} is now running!')

@bot.command()
async def hello(ctx):
        greetings = [
            "Hi", "Bonjour", "Selamat Pagi", "Bwehh", "Yurrrr",
            "You've grown slim", "Good morrow", "សួស្តី", "مرحبًا", "Hallo"
        ]
        await ctx.send(f"{random.choice(greetings)} {ctx.author.mention}")

@bot.command()
async def myteam(ctx):
    team = get_team_by_mention(ctx.author.id)

    if not team:
        await ctx.send("You do not currently manage a team.")
        return

    if not team.players:
        await ctx.send(f"{team.team_name} has no players yet.")
        return

    total_score = team.get_total_score()
    p_name = ""
    p_salary = ""       #Why is points and score a string????
    p_score = ""        # JULIAN: it's to have the line breaks for the column rows to display properly
    net_value = 0
    total_salaries = 0
    for p in team.players:
        difference = ""
        if (p.points - p.salary) > 0:
            difference = f" `+{p.points-p.salary}`"
        elif (p.points - p.salary) < 0:
            difference = f" `{p.points-p.salary}`"
        elif (p.points - p.salary) == 0:
            difference = ""
        net_value += p.points
        total_salaries += p.salary
        p_name += f"{p.get_name()}\n"
        p_salary += f"{p.salary}{difference}\n"
        p_score += f"{p.score}\n"

    team_roi = net_value - total_salaries
    if team_roi <= 0:
        team_roi = f"{team_roi}"
    elif team_roi > 0:
        team_roi = f"+{team_roi}"

    embed = discord.Embed(title=f"{team.team_name}",color=discord.Color.random()).add_field(name="Player",value=p_name).add_field(name="Salary",value=p_salary).add_field(name="Score",value=p_score).add_field(name="Total Score",value=f"{total_score}").add_field(name="Balance",value=f"{team.balance}").add_field(name="ROI",value=team_roi)

    await ctx.send(embed=embed)

    
@bot.command(aliases=["free","fa"]) 
async def available(ctx):
    if len(league.available_players) == 0:
        await ctx.send("No available players. Someone fucked up.")
        return
    else:
        pages = []
        players = []
        for p in league.available_players:
            player = []
            player.append(f"{p.get_name()}")
            player.append(f"{p.points}")
            player.append(f"{p.rank}")
            players.append(player)
        p_lists = [list(players)[x:x+20] for x in range(0, len(list(players)), 20)]
        for l in p_lists:
            p_ranks = []
            p_names = []
            p_prices = []
            for t in l:
                p_names.append(t[0])
                p_prices.append(t[1])
                p_ranks.append(t[2])
            pnj = "\n".join(p_names)
            ppj = "\n".join(p_prices)
            ppp = "\n".join(p_ranks)
            pages.append(discord.Embed(title="Available Players",color=discord.Color.random()).add_field(name="\u200b",value=ppp).add_field(name="Player",value=pnj).add_field(name="Price",value=ppj))
        await paginator.Simple().start(ctx, pages=pages)

@bot.command()
async def teams(ctx):
    pages = []
    for team in league.teams:
        p_name = ""
        p_salary = ""
        p_score = ""
        net_value = 0
        total_salaries = 0
        total_score = team.get_total_score()
        for p in team.players:
            difference = ""
            if (p.points - p.salary) > 0:
                difference = f" `+{p.points-p.salary}`"
            elif (p.points - p.salary) < 0:
                difference = f" `{p.points-p.salary}`"
            elif (p.points - p.salary) == 0:
                difference = ""
            net_value += p.points
            total_salaries += p.salary
            p_name += f"{p.get_name()}\n"
            p_salary += f"{p.salary}{difference}\n"
            p_score += f"{p.score}\n"

        team_roi = net_value - total_salaries
        if team_roi <= 0:
            team_roi = f"{team_roi}"
        elif team_roi > 0:
            team_roi = f"+{team_roi}"

        pages.append(discord.Embed(title=f"{team.team_name}",description=f"-# {team.manager_name}",color=discord.Color.random()).add_field(name="Player",value=p_name).add_field(name="Salary",value=p_salary).add_field(name="Score",value=p_score).add_field(name="Total Score",value=f"{total_score}").add_field(name="Balance",value=f"{team.balance}").add_field(name="ROI",value=team_roi))
    await paginator.Simple().start(ctx, pages=pages)

@bot.command()
async def waive(ctx, waive_player_name: str, sign_player_name: str):

    team = get_team_by_mention(ctx.author.id)
    waive_player = find_player_by_name(waive_player_name)
    sign_player = find_player_by_name(sign_player_name)
    if not team:
        await ctx.send("You do not have a team.")
        return
    if not waive_player:
        await ctx.send(f"Player '{waive_player_name}' not found.")
        return
    if waive_player not in team.players:
        await ctx.send(f"You do not own {waive_player.name}.")
        return
    if not sign_player:
        await ctx.send(f"Player '{sign_player_name}' not found.")
        return
    if sign_player.team == team.team_name:
        await ctx.send(f"{sign_player.name} is already on your team.")
        return
    if sign_player.team != "NO":
        await ctx.send(f"{sign_player.name} is on a team.")
        return
    
    success,msg = team.can_waive(waive_player,sign_player)
    if not success:
        await ctx.send(msg)
        return

    team.waivesign(waive_player,sign_player)
    refresh_files(league)
    logger.Entry(team.discord_id,sign_player.name,"sign")
    logger.Entry("0",waive_player.name,"waive")

    await ctx.send(f"You have waived {waive_player.name} and signed {sign_player.name}.")


'''These commands are going to contain functions to end the bot and update player stats from the scraper.
    These will be restricted to the bot owner only.
    '''
@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    refresh_files(league)
    await ctx.send("Shutting down the bot...")
    await bot.close()
    

def start_bot(token: str):
    bot.run(token)
