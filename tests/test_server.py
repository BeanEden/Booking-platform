import pytest
from server import app


valid_email = "admin@irontemple.com"
unvalid_email = "unvalidmail"
unregistered_mail = "unregistered_mail@irontemple.com"


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
