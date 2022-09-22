import pytest
from server import app


club = "Iron Temple"
competition = "Spring Festival"


@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


def test_purchasePlace_booking_should_work(client):
    places_bought = 1
    rv = client.post('/purchasePlaces', data=dict(club=club, competition=competition, places=places_bought))
    data = rv.data.decode()
    assert rv.status_code == 200
    assert data.find('<li>Great-booking complete!</li>') != -1


def test_purchasePlace_booking_impossible(client):
    places_bought = 50
    rv = client.post('/purchasePlaces', data=dict(club=club, competition=competition, places=places_bought))
    data = rv.data.decode()
    assert rv.status_code == 200
    assert data.find('<p>You don&#39;t have enough points to make this reservation</p>') != -1
