import os
import json
# from tests.test_server import club, competition, places_bought

path = os.getcwd()
path = path.replace("utilities", "")


club = "Simply Lift"
competition = "Spring Festival"
places_bought = 2


def loadClubs():
    with open(path+'/database/clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open(path+'/database/competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


clubs = loadClubs()
competitions = loadCompetitions()


def reset_database(club, competition):
    club = [c for c in clubs if c['name'] == club][0]
    competition = [c for c in competitions if c['name'] == competition][0]

    try:
        for i in competition['clubsParticipating']:
            if club['name'] == i['club']:
                i['placesBooked'] = 1
                print("placesbooked reset")
    except KeyError:
        print("keyerror")
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