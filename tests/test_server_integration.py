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


def test_login_logout_route(client):
    """l'utilisateur se connecte et se deconnecte
    verification du passage par chaque page via html
    4 pages : index > login > logout > index"""
### Index
    rv = client.get('/')
    data = rv.data.decode()
    assert rv.status_code == 200
    assert data.find(
        '<h1>Welcome to the GUDLFT Registration Portal!</h1>') != -1
### Properly Logged In
    rv = client.post('/showSummary', data={'email': [valid_email]})
    data_login = rv.data.decode()
    assert data_login.find('<h2>Welcome, ' + valid_email + ' </h2>') != -1
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
    message_same_points = 'Points available: '+ str(
        points)
    assert data_purchased_fail.find(message_same_points) != -1
    assert data_purchased_fail.find('<p>You don&#39;t have enough points '
                                    'to make this reservation</p>') != -1
    ### Booking successfull
    rv = client.post('/purchasePlaces',
                     data=dict(club=club,
                               competition=competition,
                               places=places_bought))
    data_purchased = rv.data.decode()
    message = 'Points available: '+ str(
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


def test_login_book_limit_fail_then_sucess_logout(client):
    reset = resetDatabase(club, competition)
    """l'utilisateur se connecte, essaie de trop réserver (plus que ses points)
    verification du passage par chaque page via html"""
    places_over_limit = 13
    places_over_limit_in_two = 7
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
    ### Booking request failing due over 12 places (still booking page)
    rv = client.post('/purchasePlaces',
                     data=dict(club=club,
                               competition=competition,
                               places=places_over_limit))
    data_purchased_fail = rv.data.decode()
    message_same_points = 'Points available: ' + str(points)
    assert data_purchased_fail.find(message_same_points) != -1
    assert data_purchased_fail.find('<p>You can&#39;t book more than '
                                    '12 places for an event</p>') != -1
    ### Booking successfull
    rv = client.post('/purchasePlaces',
                     data=dict(club=club,
                               competition=competition,
                               places=places_over_limit_in_two))
    data_purchased = rv.data.decode()
    message = 'Points available: ' + str(
        points - (places_over_limit_in_two * POINTS_PER_PLACE))
    assert data_purchased.find('<li>Great-booking complete!</li>') != -1
    assert data_purchased.find(message) != -1

    ### Back to booking page try to book over 12
    rv = client.get(expected_booking_url)
    data_booking = rv.data.decode()
    assert data_booking.find(
        '<input type="hidden" name="club" value="' + club + '">') != -1
    assert data_booking.find(
        '<input type="hidden" name="competition" value="' + competition + '">') != -1
    assert data_booking.find(
        '<input type="hidden" name="club" value="' + club + '">') != -1

    ### Booking request failing due over 12 places (still booking page)
    rv = client.post('/purchasePlaces',
                     data=dict(club=club,
                               competition=competition,
                               places=places_over_limit_in_two))
    data_purchased_fail = rv.data.decode()
    print(data_purchased_fail)
    print(message)
    message_same_points = message
    assert data_purchased_fail.find(message_same_points) != -1
    assert data_purchased_fail.find('<p>You can&#39;t book more than '
                                    '12 places for an event</p>') != -1

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
    resetSpecificElement(client, club, competition, places_over_limit_in_two)

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


def test_login_clubsTable_logout_route(client):
    """l'utilisateur se connecte et se deconnecte
    verification du passage par chaque page via html
    4 pages : index > login > logout > index"""
### Index
    rv = client.get('/')
    data = rv.data.decode()
    assert rv.status_code == 200
    assert data.find(
        '<h1>Welcome to the GUDLFT Registration Portal!</h1>') != -1
### Properly Logged In
    rv = client.post('/showSummary', data={'email': [valid_email]})
    data_login = rv.data.decode()
    assert data_login.find('<h2>Welcome, ' + valid_email + ' </h2>') != -1
### Connect to clubsTable
    rv = client.get('/clubs')
    data = rv.data.decode()
    print(data)
    assert rv.status_code == 200
    assert data.find('<h2>Clubs_list</h2>') != -1

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