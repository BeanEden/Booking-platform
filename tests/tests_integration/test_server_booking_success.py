import pytest
from server import app, dateStringSplit, dateTimeCheck, \
    loadPlacesAlreadyBooked, updatePlacesBookedOrCreate, POINTS_PER_PLACE
from tests.utilities.db_manage import getClub, resetDatabase, resetSpecificElement

valid_email = "john@simplylift.co"
unvalid_email = "unvalidmail"
unregistered_mail = "unregistered_mail@irontemple.com"
club = "Simply Lift"
competition = "Spring Festival"
places_bought = 2
resetDatabase(club, competition)

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


def test_login_book_logout_route(client):
    reset = resetDatabase(club, competition)
    """l'utilisateur se connecte, fait une réservation et se déconnecte
    verification du passage par chaque page via html"""
    club_base = getClub(club)
    points = club_base['points']
### Index
    rv = client.get('/')
    data = rv.data.decode()
    assert rv.status_code == 200
    assert data.find(
        '<h1>Welcome to the GUDLFT Registration Portal!</h1>') != -1
### Properly Logged In
    rv = client.post('/showSummary', data={'email': [valid_email]})
    data = rv.data.decode()
    expected_booking_url = "/book/Spring%20Festival/Simply%20Lift"
    assert data.find(
        '<a href="' + expected_booking_url + '">Book Places</a>') != -1
### Booking page
    rv = client.get(expected_booking_url)
    data_booking = rv.data.decode()
    assert data_booking.find(
        '<input type="hidden" name="club" value="' + club + '">') != -1
    assert data_booking.find(
        '<input type="hidden" name="competition" value="' + competition + '">') != -1
    assert data_booking.find(
        '<input type="hidden" name="club" value="' + club + '">') != -1
### Booking successful, back to index
    rv = client.post('/purchasePlaces',
                     data=dict(club=club,
                               competition=competition,
                               places=places_bought))
    data_purchased = rv.data.decode()
    message = 'Points available: ' + str(
        points - (places_bought * POINTS_PER_PLACE))
    assert data_purchased.find('<li>Great-booking complete!</li>') != -1
    assert data_purchased.find(message) != -1
### Log out
    rv = client.get('/logout')
    data_logout = rv.data.decode()
    assert data_logout.find('<h1>Redirecting...</h1>') != -1
### Back to index
    rv = client.get('/')
    data_index = rv.data.decode()
    assert rv.status_code == 200
    assert data_index.find(
        '<h1>Welcome to the GUDLFT Registration Portal!</h1>') != -1
    resetSpecificElement(client, club, competition, places_bought)
