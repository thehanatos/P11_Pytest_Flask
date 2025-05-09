import pytest
from server import app
from datetime import datetime, timedelta
import html


@pytest.fixture
def client(monkeypatch):
    test_clubs = [{
        'name': 'Test Club',
        'email': 'test@email.com',
        'points': '20'
    }]

    future_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
    test_competitions = [{
        'name': 'Test Competition',
        'date': future_date,
        'numberOfPlaces': '10'
    }]

    monkeypatch.setattr('server.clubs', test_clubs)
    monkeypatch.setattr('server.competitions', test_competitions)

    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_login_success(client):
    response = client.post('/showSummary', data={'email': 'test@email.com'})
    assert response.status_code == 200
    assert b'Welcome' in response.data
    assert b'Test Competition' in response.data


def test_login_failure(client):
    response = client.post('/showSummary', data={'email': 'wrong@example.com'})
    assert response.status_code == 200
    text = html.unescape(response.data.decode())
    assert "Sorry, that email wasn't found." in text


def test_book_page_access(client):
    client.post('/showSummary', data={'email': 'test@email.com'})

    response = client.get('/book/Test Competition/Test Club')
    assert response.status_code == 200
    assert b'How many places?' in response.data or b'booking' in response.data.lower()


def test_successful_booking(client):
    # Connection
    client.post('/showSummary', data={'email': 'test@email.com'})

    # Booking
    response = client.post('/purchasePlaces', data={
        'competition': 'Test Competition',
        'club': 'Test Club',
        'places': '2'
    })
    assert response.status_code == 200
    assert b'Great - booking complete!' in response.data


def test_booking_more_than_allowed_limit(client):
    client.post('/showSummary', data={'email': 'test@example.com'})

    response = client.post('/purchasePlaces', data={
        'competition': 'Test Competition',
        'club': 'Test Club',
        'places': '13'
    })
    assert response.status_code == 200
    assert b'You cannot purchase more than 12 places' in response.data


def test_booking_past_competition(client, monkeypatch):
    # Change date into past
    past_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")
    past_competitions = [{
        'name': 'Old Comp',
        'date': past_date,
        'numberOfPlaces': '5'
    }]
    monkeypatch.setattr('server.competitions', past_competitions)

    response = client.get('/book/Old Comp/Test Club')
    assert b'You cannot book past competitions' in response.data


def test_logout_redirect(client):
    response = client.get('/logout')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')
