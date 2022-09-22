import json
from flask import Flask,render_template,request,redirect,flash,url_for
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


def loadPlacesAlreadyBooked(competition, club):
    try :
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
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def showSummary():
    club = [club for club in clubs if club['email'] == request.form['email']][0]
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


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesAlreadyBooked = loadPlacesAlreadyBooked(competition, club)
    placesRequired = int(request.form['places'])
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    totalPlacesBooked = placesAlreadyBooked + placesRequired
    if totalPlacesBooked > 12:
        error_message = "You can't book more than 12 places for an event"
        return render_template('booking.html', club=club, competition=competition, placesAlreadyBooked=placesAlreadyBooked,
                               error_message=error_message)
    else:
        competition['numberOfPlaces'] = int(
            competition['numberOfPlaces']) - placesRequired
        competition = updatePlacesBookedOrCreate(competition, club,
                                                 totalPlacesBooked)
        with open('database/competitions.json', "w") as cr:
            data = {'competitions': competitions}
            json.dump(data, cr)
        flash('Great-booking complete!')
        return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=False)