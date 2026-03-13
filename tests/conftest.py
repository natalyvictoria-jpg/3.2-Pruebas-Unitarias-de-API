# tests/conftest.py
import pytest
from app import create_app, db as _db
from app.config import TestingConfig

@pytest.fixture(scope="session")
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture(scope="function")
def client(app):
    with app.app_context():
        yield app.test_client()

@pytest.fixture(scope="session")
def db(app):
    with app.app_context():
        yield _db

@pytest.fixture
def estudiante_data():
    return {
        "matricula": "TEST001",
        "nombre": "Carlos",
        "apellido": "Ramirez",
        "email": "carlos@test.edu.mx",
        "carrera": "ITIC",
        "semestre": 5
    }

@pytest.fixture
def auth_headers(client):
    client.post("/api/auth/registro", json={
        "username": "docente_test",
        "email": "doc@test.mx",
        "password": "Password123!",
        "rol": "docente"
    })
    resp = client.post("/api/auth/login", json={
        "username": "docente_test",
        "password": "Password123!"
    })
    token = resp.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}