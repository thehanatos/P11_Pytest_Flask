import pytest
from server import app, clubs, competitions
import html


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to the GUDLFT Registration Portal!' in response.data


def setup_module(module):
    clubs.clear()
    clubs.extend([
        {'name': 'Test Club', 'email': 'test@club.com', 'points': '20'},
        {'name': 'Club Few Points', 'email': 'few@club.com', 'points': '5'}
    ])
    competitions.clear()
    competitions.extend([
        {'name': 'Spring Festival', 'date': '2099-06-21 10:00:00', 'numberOfPlaces': '25'},
        {'name': 'Past Competition', 'date': '2000-01-01 10:00:00', 'numberOfPlaces': '5'}
    ])


def test_show_summary_invalid_email(client):
    response = client.post('/showSummary', data={'email': 'invalid@email.com'})
    assert response.status_code == 200
    text = html.unescape(response.data.decode())
    assert "Sorry, that email wasn't found." in text


def test_book_past_competition(client):
    response = client.get('/book/Past Competition/Test Club')
    assert b'You cannot book past competitions' in response.data


def test_purchase_places_success(client):
    data = {
        'competition': 'Spring Festival',
        'club': 'Test Club',
        'places': '2'
    }
    response = client.post('/purchasePlaces', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Great - booking complete!' in response.data


def test_purchase_more_than_12_places(client):
    data = {
        'competition': 'Spring Festival',
        'club': 'Test Club',
        'places': '13'
    }
    response = client.post('/purchasePlaces', data=data, follow_redirects=True)
    assert b'You cannot purchase more than 12 places at once.' in response.data


def test_purchase_for_past_competition(client):
    data = {
        'competition': 'Past Competition',
        'club': 'Test Club',
        'places': '1'
    }
    response = client.post('/purchasePlaces', data=data, follow_redirects=True)
    assert b'You cannot purchase places for past competitions.' in response.data


def test_purchase_insufficient_points(client):
    data = {
        'competition': 'Spring Festival',
        'club': 'Club Few Points',
        'places': '10'
    }
    response = client.post('/purchasePlaces', data=data, follow_redirects=True)
    assert b'You do not have enough points to book these places.' in response.data


def test_book_valid(client):
    response = client.get('/book/Spring Festival/Test Club')
    assert response.status_code == 200
    assert b'How many places?' in response.data
