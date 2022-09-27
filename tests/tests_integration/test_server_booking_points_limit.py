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


def test_login_book_points_fail_then_sucess_logout(client):
    reset = resetDatabase(club, competition)
    """l'utilisateur se connecte, essaie de trop réserver (plus que ses points)
    verification du passage par chaque page via html"""
    places_bought_fail = 100
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
    ### Booking request failing due to not enough points (still booking page)
    rv = client.post('/purchasePlaces',
                     data=dict(club=club,
                               competition=competition,
                               places=places_bought_fail))
    data_purchased_fail = rv.data.decode()
    # message_same_points = 'Points available : '+ str(
    #     points)
    # assert data_purchased_fail.find(message_same_points) != -1
    assert data_purchased_fail.find('<p>You don&#39;t have enough points '
                                    'to make this reservation</p>') != -1
    ### Booking successfull
    rv = client.post('/purchasePlaces',
                     data=dict(club=club,
                               competition=competition,
                               places=places_bought))
    data_purchased = rv.data.decode()
    # message = 'Points available: '+ str(
    #     points - (places_bought * POINTS_PER_PLACE))
    assert data_purchased.find('<li>Great-booking complete!</li>') != -1
    # assert data_purchased.find(message) != -1
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


