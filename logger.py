from time import time
import sqlite3
from datetime import datetime
from unicodedata import name

from discord import team 

#new improved logger that sends data ontop of the database

#parameters: manager_id, player_name, transaction(trade draft etc), time
def Entry(manager_id, player_name, transaction, timestamp=None):

    if timestamp is None:
         timestamp =  int(time() * 1000)

    if manager_id == "NO":
            manager_id = 0
    else: manager_id = int(manager_id)
    
    teams = {
    343916381584097282:"Bolabinga Tennis Club",
    394914770278416385:"Lanzhou Hand Pulled Noodles",
    673373625780404238:"Rileys Rascals",
    687838113896464448:"Ori Woohoo",
    1449543749385457798:"Bagel Brothers",
    "NO":"NO",
    0:"NO"
    }
    
    #connects to the database file
    #if the file doesn't exists, it is created
    con = sqlite3.connect('log.db')

    #the cursor is the program/user interacts with the database
    cur = con.cursor()

    # LOG TABLE SCHEMA 
    # eventNumber INTEGER PRIMARY KEY AUTOINCREMENT, INPUT NOT NEEDED!!!!!!!!
    # playerName TEXT 
    # timestamp DATETIME 
    # managerID INTEGER
    # teamName TEXT
    # eventType TEXT
    
    if manager_id == "NO":
        manager_id = 0

    row = (timestamp, manager_id, teams[manager_id], player_name, transaction)

    cur.execute("INSERT INTO log (timestamp, managerID, teamName, playerName, eventType) VALUES (?, ?, ?, ?, ?)",row)

    #save changes
    con.commit()

    #close the connection
    con.close()

    print("Log entry created.")
    return
