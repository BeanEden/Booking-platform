import pytest
from server import app
from tests.utilities.db_manage import resetDatabase

valid_email = "john@simplylift.co"
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
