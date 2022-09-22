import pytest
from server import app, loadPlacesAlreadyBooked, updatePlacesBookedOrCreate
from tests.utilities.db_manage import reset_database

club = "Simply Lift"
competition = "Spring Festival"
places_bought = 2

reset_database(club, competition)


@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def club_one():
    club = {"name": "Simply Lift", "points": "13"}
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


def test_purchasePlace_booking_should_work(client):
    rv = client.post('/purchasePlaces', data=dict(club=club, competition=competition, places=places_bought))
    data = rv.data.decode()
    assert rv.status_code == 200
    assert data.find('<li>Great-booking complete!</li>') != -1


def test_purchasePlace_booking_impossible(client):
    places_bought = 50
    rv = client.post('/purchasePlaces', data=dict(club=club, competition=competition, places=places_bought))
    data = rv.data.decode()
    assert rv.status_code == 200
    assert data.find('<p>You can&#39;t book more than 12 places for an event</p>') != -1
