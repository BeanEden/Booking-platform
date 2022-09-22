import os
import json


path = os.getcwd()
path = path.replace("utilities", "")


club = "Simply Lift"


def loadClubs():
    with open(path+'/database/clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


clubs = loadClubs()


def get_club(club):
    club = [c for c in clubs if c['name'] == club][0]
    return club
