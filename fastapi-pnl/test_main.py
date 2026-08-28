import os
from dotenv import load_dotenv
import pytest
from fastapi.testclient import TestClient
from main import app, get_db
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from models import Transaction

load_dotenv()
dataTestURL = os.getenv("TEST_DATABASE_URL")
API_KEY = os.getenv("APP_API_KEY")

engine = create_engine(dataTestURL)
SessionTestLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_test_db():
    with SessionTestLocal() as session:
        yield session

app.dependency_overrides[get_db] = get_test_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_client():
    return TestClient(app, headers={"x-api-key": API_KEY})

@pytest.fixture
def false_client():
    return TestClient(app, headers={"x-api-key": "invalid key"})

@pytest.fixture(autouse=True)
def clean_db():
    with SessionTestLocal() as session:
        stmt = delete(Transaction)
        session.execute(stmt)
        session.commit()
    yield

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, this is my Crypto P&L API"}

def test_about(client):
    response = client.get("/about")
    assert response.status_code == 200
    assert response.json() == {"name":"Crypto P&L Tracker", "version":"v1.0", "feature":"Tracking crypto position & Calculating ROI", "author":"Aeron"}

def test_get_price_success(client):
    response = client.get("/price/bitcoin")
    assert response.status_code == 200
    assert type(response.json()["coin"]) == str
    assert type(response.json()["price"]) in (int, float)

def test_get_price_fail(client):
    response = client.get("/price/notacoin")
    assert response.status_code == 404
    assert response.json() == {"detail": "This coin doesn't exist. Try another one."}

def test_post_transaction_invalid_amount(auth_client):
    response = auth_client.post("/transaction", json={"coin": "bitcoin", "action": "buy", "amount": -5, "price": 64000})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid amount value"}

def test_post_transaction_invalid_price(auth_client):
    response = auth_client.post("/transaction", json={"coin": "bitcoin", "action": "buy", "amount": 0.5, "price": -64000})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid price"}

def test_post_transaction(auth_client):
    response = auth_client.post("/transaction", json={"coin": "bitcoin", "action": "buy", "amount": 0.5, "price": 64000})
    assert response.status_code == 200
    assert response.json()["data"]["total"] == 32000

def test_get_transactions(auth_client):
    auth_client.post("/transaction", json={"coin": "bitcoin", "action": "buy", "amount": 0.5, "price": 64000})
    response = auth_client.get("/transactions")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["coin"] == "bitcoin"

def test_get_tx_by_id(auth_client):
    auth_client.post("/transaction", json={"coin": "bitcoin", "action": "buy", "amount": 0.5, "price": 64000})
    rows = auth_client.get("/transactions")
    id = rows.json()[0]["id"]
    response = auth_client.get(f"/transactions/{id}")
    assert response.status_code == 200
    assert response.json()["id"] == id
    assert response.json()["coin"] == "bitcoin"
    assert response.json()["action"] == "buy"
    assert response.json()["amount"] == 0.5
    assert response.json()["price"] == 64000
    assert response.json()["total"] == 32000
    assert response.json()["created_at"] is not None

def test_delete_tx_by_id(auth_client):
    auth_client.post("/transaction", json={"coin": "bitcoin", "action": "buy", "amount": 0.5, "price": 64000})
    rows_before = auth_client.get("/transactions")
    id = rows_before.json()[0]["id"]
    response = auth_client.delete(f"/transactions/{id}")
    assert response.status_code == 200
    rows_after = auth_client.get("/transactions")
    assert len(rows_after.json()) == 0

def test_no_key(client):
    response = client.post("/transaction", json={"coin": "bitcoin", "action": "buy", "amount": 0.5, "price": 64000})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid API key!"}

def test_invalid_key(false_client):
    response = false_client.post("/transaction", json={"coin": "bitcoin", "action": "buy", "amount": 0.5, "price": 64000})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid API key!"}

def test_valid_key(auth_client):
    auth_client.post("/transaction", json={"coin": "bitcoin", "action": "buy", "amount": 0.5, "price": 64000})
    response = auth_client.get("/transactions")
    assert response.status_code != 401

def test_put_invalid_id(auth_client):
    response = auth_client.put(f"/transactions/999999999", json={"coin": "bitcoin", "action": "buy", "amount": 0.5, "price": 64000})
    assert response.status_code == 404
    assert response.json() == {"detail": "Invalid id number"}