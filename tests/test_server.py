import pytest
from server import app


@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


def test_clubsTable(client):
    expected_club_one = 'Iron Temple - 4 points'
    expected_club_two = 'She Lifts - 12 points'
    expected_club_three = 'Simply Lift - 13 points'
    rv = client.get('/clubs')
    data = rv.data.decode()
    assert rv.status_code == 200
    assert data.find(expected_club_one) != -1
    assert data.find(expected_club_two) != -1
    assert data.find(expected_club_three) != -1
