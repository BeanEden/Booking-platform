import pytest
from server import app
from tests.utilities.db_manage import get_club


club = "Simply Lift"
competition = "Spring Festival"


@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


def test_purchasePlace_booking_should_work(client):
    places_bought = 2
    club_base = get_club(club)
    rv = client.post('/purchasePlaces', data=dict(club=club, competition=competition, places=places_bought))
    data = rv.data.decode()
    points = club_base['points']
    message = 'Points available: ' + str(points-places_bought)
    assert rv.status_code == 200
    assert data.find('<li>Great-booking complete!</li>') != -1
    assert data.find(message) != -1
