import os
import json

path = os.getcwd()
path = path.replace("utilities", "")
print(path)

club = "Simply Lift"
competition = "Spring Festival"
places_bought = 2


def loadClubs():
    """load all clubs of the db, return a list of dict"""
    with open(path+'/database/clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def getClub(club):
    """get a specific club from the db"""
    clubs = loadClubs()
    club = [c for c in clubs if c['name'] == club][0]
    return club


def loadCompetitions():
    """load all competitions of the db, return a list of dict"""
    with open(path+'/database/competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


clubs = loadClubs()
competitions = loadCompetitions()


def resetDatabase(club, competition):
    """reset the db in order for the tests to be truthful everytime"""
    club = [c for c in clubs if c['name'] == club][0]
    competition = [c for c in competitions if c['name'] == competition][0]

    try:
        for i in competition['clubsParticipating']:
            if club['name'] == i['club']:
                i['placesBooked'] = 1
    except KeyError:
        competition['clubsParticipating'] = [
            {'club': club['name'], 'placesBooked': 1}]

    club['points'] = 30
    competition['numberOfPlaces'] = 50

    with open(path + '/database/competitions.json', "w") as cr:
        data = {'competitions': competitions}
        json.dump(data, cr)

    with open(path + '/database/clubs.json', "w") as cr:
        data = {'clubs': clubs}
        json.dump(data, cr)
