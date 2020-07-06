import os
import pytest
from main import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    client = app.test_client()
    cleanup()

    db.create_all()

    yield client


def cleanup():
    db.drop_all()

def login(client):
    client.post('/login', data={"user-name": "Test user", "user-email": "test@example.com",
                                "user-password": "password"}, follow_redirects=True)


def test_index_not_logged_in(client):
    response = client.get('/')
    assert b'Enter your name' in response.data


def test_index_logged_in(client):
    login(client)

    response = client.get('/')
    assert b'Enter your guess' in response.data


