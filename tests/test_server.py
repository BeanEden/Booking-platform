import pytest
from server import app, date_str_split, datetime_check, loadPlacesAlreadyBooked, updatePlacesBookedOrCreate
from tests.utilities.db_manage import get_club, reset_database

valid_email = "admin@irontemple.com"
unvalid_email = "unvalidmail"
unregistered_mail = "unregistered_mail@irontemple.com"
club = "Simply Lift"
competition = "Spring Festival"
places_bought = 2



@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


def test_get_index_page(client):
    rv = client.get('/')
    assert rv.status_code == 200


def test_showSummary_valid_mail(client):
    rv = client.post('/showSummary', data={'email': [valid_email]})
    data = rv.data.decode()
    assert rv.status_code == 200
    assert data.find('<p>Sorry, that email wasn&#39;t found.</p>') == -1


def test_showSummary_unvalid_email(client):
    rv = client.post('/showSummary', data={'email': [unvalid_email]})
    data = rv.data.decode()
    assert rv.status_code == 200
    assert data.find('<p>Sorry, that email wasn&#39;t found.</p>') != -1


def test_showSummary_unregistered_mail(client):
    rv = client.post('/showSummary', data={'email': [unregistered_mail]})
    data = rv.data.decode()
    assert rv.status_code == 200
    assert data.find('<p>Sorry, that email wasn&#39;t found.</p>') != -1


def test_date_str_split():
    date_clean = "2020-03-27 10:00:00"
    date_datetime_str = "2020-03-27 10:00:00.134247"
    expected_value = "202003271000"

    assert date_str_split(date_clean) == expected_value
    assert date_str_split(date_datetime_str) == expected_value


def test_datetime_check():
    competition_open = {'date': "2024-03-27 10:00:00"}
    competition_closed_year = {'date': "2020-03-27 10:00:00"}
    competition_closed_month = {'date': "2022-03-27 10:00:00"}

    assert datetime_check(competition_open)['status'] == 'open'
    assert datetime_check(competition_closed_year)['status'] == 'closed'
    assert datetime_check(competition_closed_month)['status'] == 'closed'


def test_showSummary(client):
    rv = client.post('/showSummary', data={'email': [valid_email]})
    data = rv.data.decode()
    assert rv.status_code == 200
    assert data.find('<a href="/book/Spring%20Festival/Iron%20Temple">Book Places</a>') != -1


# def test_purchasePlace_booking_should_work(client):
#     reset = reset_database(club, competition)
#     club_base = get_club(club)
#     rv = client.post('/purchasePlaces', data=dict(club=club, competition=competition, places=places_bought))
#     data = rv.data.decode()
#     points = club_base['points']
#     print("points", points)
#     message = 'Points available: ' + str(points-places_bought)
#     assert rv.status_code == 200
#     assert data.find('<li>Great-booking complete!</li>') != -1
#     assert data.find(message) != -1

def test_purchasePlace_booking_should_work(client, club_one, competition_with_club_one):
    reset = reset_database(club, competition)
    club_base = get_club(club)
    compet_loaded = competition_with_club_one
    rv = client.post('/purchasePlaces', data=dict(club=club_one["name"], competition=compet_loaded["name"], places=places_bought))
    data = rv.data.decode()
    points = club_base['points']
    message = 'Points available: ' + str(points-places_bought)
    assert rv.status_code == 200
    assert data.find('<li>Great-booking complete!</li>') != -1
    assert data.find(message) != -1


@pytest.fixture
def club_one():
    club = {"name": "Simply Lift", "points": "20"}
    return club


@pytest.fixture
def competition_without_club_list():
    competition = {"name": "Spring Festival", "numberOfPlaces": 3}
    return competition


@pytest.fixture
def competition_with_empty_club_list():
    competition = {"name": "Spring Festival", "numberOfPlaces": 3,
                   "clubsParticipating": []}
    return competition


@pytest.fixture
def competition_with_other_club():
    competition = {"name": "Spring Festival",
                   "numberOfPlaces": 3,
                   "clubsParticipating": [
                       {"club": "Iron Temple", "placesBooked": 4}
                   ]}
    return competition


@pytest.fixture
def competition_with_club_one():
    competition = {"name": "Spring Festival",
                   "numberOfPlaces": 3,
                   "clubsParticipating": [
                       {"club": "Simply Lift", "placesBooked": 4}
                   ]}
    return competition


def test_loadPlacesAlreadyBooked_no_club_should_return_zero(competition_without_club_list, club_one):
    competition = competition_without_club_list
    club = club_one
    assert loadPlacesAlreadyBooked(competition, club) == 0


def test_loadPlacesAlreadyBooked_empty_list_should_return_zero(competition_with_empty_club_list, club_one):
    competition = competition_with_empty_club_list
    club = club_one
    assert loadPlacesAlreadyBooked(competition, club) == 0


def test_loadPlacesAlreadyBooked_other_clubs_participating_should_return_zero(competition_with_other_club, club_one):
    competition = competition_with_other_club
    club = club_one
    assert loadPlacesAlreadyBooked(competition, club) == 0


def test_loadPlacesAlreadyBooked_clubs_participating_should_return_four(competition_with_club_one, club_one):
    competition = competition_with_club_one
    club = club_one
    assert loadPlacesAlreadyBooked(competition, club) == 4


def test_updatePlaceBookedOrCreate_without_club_list(competition_without_club_list, club_one):
    competition = competition_without_club_list
    club = club_one
    test = updatePlacesBookedOrCreate(competition, club, places_bought)
    expected_value = {"name": "Spring Festival",
                      "numberOfPlaces": 3,
                      "clubsParticipating": [
                          {"club": "Simply Lift", "placesBooked": 2}
                      ]}
    assert test == expected_value


def test_updatePlaceBookedOrCreate_empty_club_list(competition_with_empty_club_list, club_one):
    competition = competition_with_empty_club_list
    club = club_one
    test = updatePlacesBookedOrCreate(competition, club, places_bought)
    expected_value = {"name": "Spring Festival",
                   "numberOfPlaces": 3,
                   "clubsParticipating": [
                       {"club": "Simply Lift", "placesBooked": 2}
                   ]}
    assert test == expected_value


def test_updatePlaceBookedOrCreate_other_club(competition_with_other_club, club_one):
    competition = competition_with_other_club
    club = club_one
    test = updatePlacesBookedOrCreate(competition, club, places_bought)
    expected_value = {"name": "Spring Festival",
                      "numberOfPlaces": 3,
                      "clubsParticipating": [
                          {"club": "Iron Temple", "placesBooked": 4},
                          {"club": "Simply Lift", "placesBooked": 2}
                      ]}
    assert test == expected_value


def test_updatePlaceBookedOrCreate_with_club_one(competition_with_club_one, club_one):
    competition = competition_with_club_one
    club = club_one
    test = updatePlacesBookedOrCreate(competition, club, places_bought)
    expected_value = {"name": "Spring Festival",
                      "numberOfPlaces": 3,
                      "clubsParticipating": [
                          {"club": "Simply Lift", "placesBooked": 2}
                      ]}
    assert test == expected_value



def test_purchasePlace_booking_impossible(client):
    places_bought = 50
    rv = client.post('/purchasePlaces', data=dict(club=club, competition=competition, places=places_bought))
    reset_database(club, competition)
    data = rv.data.decode()
    assert rv.status_code == 200
    assert data.find('<p>You don&#39;t have enough points to make this reservation</p>') != -1


def test_purchasePlace_book_more_than_12_in_2_booking(client):
    reset_database(club, competition)
    places_bought = 7
    club_two = get_club(club)
    rv1 = client.post('/purchasePlaces', data=dict(club=club, competition=competition, places=places_bought))
    rv = client.post('/purchasePlaces', data=dict(club=club, competition=competition, places=places_bought))
    club_two = get_club(club)
    data = rv.data.decode()
    reset_database(club, competition)
    assert rv.status_code == 200
    assert data.find('<p>You can&#39;t book more than 12 places for an event</p>') != -1


def test_clubsTable(client):
    expected_club_one = 'Iron Temple - 4 points'
    expected_club_two = 'She Lifts - 12 points'
    expected_club_three = 'Simply Lift - 21 points'
    rv = client.get('/clubs')
    data = rv.data.decode()
    assert rv.status_code == 200
    assert data.find(expected_club_one) != -1
    assert data.find(expected_club_two) != -1
    assert data.find(expected_club_three) != -1