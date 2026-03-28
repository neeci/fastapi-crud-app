import pytest
from fastapi.testclient import TestClient
from app.main import app, UserORM
from app.models import UserORM

@pytest.fixture
def client():
    return TestClient(app)

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to My First Back-end"}

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {"status" : "ok", "message" : "The service is running"}

def test_greet(client):
    response = client.get('/greet/John'
    )
    assert response.status_code == 200
    assert response.json() == {"message": f"Hello John, Welcome to the api"}  

def test_create(client):

    user = {
        "name" : "nissi",
        "email" : "nissi@gmail.com",
        "age" : 12
    }

    response = client.post('/user', json = user)
    assert response.status_code == 201
    assert response.json() == user
