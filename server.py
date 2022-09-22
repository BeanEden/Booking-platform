import json
import datetime
from flask import Flask, render_template, request, redirect, flash, url_for
import os


def loadClubs():
    with open(os.getcwd()+'/database/clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open(os.getcwd()+'/database/competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'


competitions = loadCompetitions()
clubs = loadClubs()


def bookingLimit(competition, club, already_booked):
    listed = []
    listed.append(int(competition['numberOfPlaces']))
    listed.append(int(club['points']))
    listed.append(12-int(already_booked))
    return min(listed)


def datetime_check(competition):
    today = date_str_split(str(datetime.datetime.now()))
    competition_date = date_str_split(competition['date'])

    if int(today) < int(competition_date):
        competition['status'] = 'open'
    else:
        competition['status'] = 'closed'
    return competition


def date_str_split(date):
    days = date[:10].replace("-", "")
    hours = date[11:16].replace(":", "")
    date = days+hours
    return str(date)



def loadPlacesAlreadyBooked(competition, club):
    try:
        if len(competition['clubsParticipating']) > 0:
            count = 0
            for i in competition['clubsParticipating']:
                if club['name'] == i['club']:
                    count += 1
                    return int(i['placesBooked'])
            if count == 0:
                return 0
        else:
            return 0
    except KeyError:
        competition['clubsParticipating'] = [
            {'club': club['name'], 'placesBooked':0}]
        return 0


def updatePlacesBookedOrCreate(competition, club, places):
    try:
        if len(competition['clubsParticipating']) > 0:
            count = 0
            for i in competition['clubsParticipating']:
                if club['name'] == i['club']:
                    i['placesBooked'] = places
                    count += 1
            if count == 0:
                competition["clubsParticipating"].append(
                    {'club': club['name'], 'placesBooked': places})
            return competition
        else:
            competition["clubsParticipating"].append({'club': club['name'], 'placesBooked': places})
            return competition
    except KeyError:
        competition['clubsParticipating'] = [
            {'club': club['name'], 'placesBooked':places}]
        return competition


@app.route('/')
def index(error_message="False"):
    return render_template('index.html', error_message=error_message)




@app.route('/showSummary', methods=['POST'])
def showSummary():
    try:
        club = [club for club in clubs if club['email'] == request.form['email']][0]
    except IndexError:
        return index(error_message="Sorry, that email wasn't found.")
    for i in competitions:
        i = datetime_check(i)
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        placesAlreadyBooked = loadPlacesAlreadyBooked(foundCompetition,
                                                      foundClub)
        bookingMax = bookingLimit(foundCompetition, foundClub,
                                  placesAlreadyBooked)
        return render_template('booking.html', club=foundClub,
                               competition=foundCompetition,
                               placesAlreadyBooked=placesAlreadyBooked,
                               booking_max=bookingMax)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesAlreadyBooked = loadPlacesAlreadyBooked(competition, club)
    placesRequired = int(request.form['places'])
    if placesRequired > int(club['points']):
        error_message = "You don't have enough points to make this reservation"
        return render_template('booking.html', club=club, competition=competition, error_message=error_message)

    totalPlacesBooked = placesAlreadyBooked + placesRequired
    if totalPlacesBooked > 12:
        error_message = "You can't book more than 12 places for an event"
        return render_template('booking.html', club=club, competition=competition, placesAlreadyBooked=placesAlreadyBooked,
                               error_message=error_message)
    else:
        competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
        club['points'] = int(club['points'])-placesRequired
        competition = updatePlacesBookedOrCreate(competition, club,
                                                 totalPlacesBooked)
        with open(os.getcwd() + '/database/clubs.json', "w") as c:
            data = {'clubs': clubs}
            json.dump(data, c)
        with open(os.getcwd() +'/database/competitions.json', "w") as cr:
            data = {'competitions': competitions}
            json.dump(data, cr)
        flash('Great-booking complete!')
        return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display
@app.route('/clubs')
def clubsTable():
    sorted_list = sorted(clubs, key=lambda item: item['name'])
    return render_template('clubs.html', clubs=sorted_list)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=False)
