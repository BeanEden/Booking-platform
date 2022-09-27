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


def test_login_book_then_refund(client):
    """l'utilisateur se connecte, essaie de trop réserver (plus que ses points)
    verification du passage par chaque page via html"""
    reset = resetDatabase(club, competition)
    club_base = getClub(club)
    points = club_base['points']
    rv = client.post('/showSummary', data={'email': [valid_email]})
    data = rv.data.decode()
    expected_booking_url = "/book/Spring%20Festival/Simply%20Lift"
    assert data.find(
        '<a href="' + expected_booking_url + '">Book Places</a>') != -1
    rv = client.get(expected_booking_url)
    data_booking = rv.data.decode()
    assert data_booking.find(
        '<input type="hidden" name="club" value="' + club + '">') != -1
    assert data_booking.find(
        '<input type="hidden" name="competition" value="' + competition + '">') != -1
    rv = client.post('/purchasePlaces',
                     data=dict(club=club,
                               competition=competition,
                               places=places_bought))
    data_purchased = rv.data.decode()
    # message = 'Points available: 27'
    assert data_purchased.find('<li>Great-booking complete!</li>') != -1
    # assert data_purchased.find(message) != -1

    rv = client.get(expected_booking_url)
    data_booking = rv.data.decode()
    assert data_booking.find(
        '<input type="hidden" name="club" value="' + club + '">') != -1

    rv = client.post('/purchasePlaces',
                     data=dict(club=club,
                               competition=competition,
                               places=-places_bought))
    data_purchased = rv.data.decode()
    # message = 'Points available: 33'
    assert data_purchased.find('<li>Great-booking complete!</li>') != -1
    # assert data_purchased.find(message) != -1
    rv = client.get('/logout')
    data_logout = rv.data.decode()
    rv = client.get('/')
    data_index = rv.data.decode()
    assert rv.status_code == 200
    assert data_logout.find('<h1>Redirecting...</h1>') != -1
    assert data_index.find(
        '<h1>Welcome to the GUDLFT Registration Portal!</h1>') != -1

