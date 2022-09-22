import pytest
from server import app
from server import date_str_split, datetime_check


valid_email = "admin@irontemple.com"


@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


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
