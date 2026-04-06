import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add parent directory to path so imports work from tests directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
from main import app
from database import Base
from dependencies import get_db

# Setup test database (in-memory SQLite for isolation)
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Create tables before tests
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)

# Test /register endpoint
def test_register_user_success():
    response = client.post("/register", json={
        "username": "testuser",
        "password": "testpass",
        "name": "Test User",
        "flat_number": "101",
        "contact_id": "123456",
        "role": "member"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["role"] == "member"

def test_register_user_duplicate_username():
    # First, register a user
    client.post("/register", json={
        "username": "testuser2",
        "password": "testpass",
        "name": "Test User 2",
        "flat_number": "102",
        "contact_id": "123457",
        "role": "member"
    })
    # Try to register again with same username
    response = client.post("/register", json={
        "username": "testuser2",
        "password": "testpass",
        "name": "Test User 2",
        "flat_number": "102",
        "contact_id": "123457",
        "role": "member"
    })
    assert response.status_code == 400
    assert "Username already taken" in response.json()["detail"]

# Test /login endpoint
def test_login_success():
    # Register first
    client.post("/register", json={
        "username": "loginuser",
        "password": "loginpass",
        "name": "Login User",
        "flat_number": "103",
        "contact_id": "123458",
        "role": "member"
    })
    response = client.post("/login", json={
        "username": "loginuser",
        "password": "loginpass"
    })
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]
    assert "session" in response.cookies

def test_login_invalid_credentials():
    response = client.post("/login", json={
        "username": "invalid",
        "password": "invalid"
    })
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]

# Test /me endpoint
def test_get_me_authenticated():
    # Register and login
    client.post("/register", json={
        "username": "meuser",
        "password": "mepass",
        "name": "Me User",
        "flat_number": "104",
        "contact_id": "123459",
        "role": "member"
    })
    login_response = client.post("/login", json={
        "username": "meuser",
        "password": "mepass"
    })
    session_cookie = login_response.cookies.get("session")
    
    response = client.get("/me", cookies={"session": session_cookie})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Me User"
    assert data["role"] == "member"

def test_get_me_unauthenticated():
    response = client.get("/me")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

# Test /users endpoint
def test_get_users():
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Assuming at least one user from previous tests
    assert len(data) > 0
    assert "id" in data[0]
    assert "flat_number" in data[0]

# Test /expenses endpoints
def test_create_expense_success():
    # Register and login as secretary or treasurer
    client.post("/register", json={
        "username": "expenseuser",
        "password": "expensepass",
        "name": "Expense User",
        "flat_number": "105",
        "contact_id": "123460",
        "role": "secretary"
    })
    login_response = client.post("/login", json={
        "username": "expenseuser",
        "password": "expensepass"
    })
    session_cookie = login_response.cookies.get("session")
    
    response = client.post("/expenses?username=expenseuser", json={
        "date": "2025-01-01",
        "month": "January",
        "year": 2025,
        "expense_name": "Electricity",
        "description": "Monthly bill",
        "amount": 500.0,
        "paid_by": 105,
        "created_by": "expenseuser"
    }, cookies={"session": session_cookie})
    assert response.status_code == 200
    data = response.json()
    assert data["expense_name"] == "Electricity"

def test_create_expense_member_allowed():
    # Register as member and verify they can create expenses
    client.post("/register", json={
        "username": "memberuser2",
        "password": "memberpass",
        "name": "Member User",
        "flat_number": "106",
        "contact_id": "123461",
        "role": "member"
    })
    login_response = client.post("/login", json={
        "username": "memberuser2",
        "password": "memberpass"
    })
    session_cookie = login_response.cookies.get("session")

    response = client.post("/expenses?username=memberuser2", json={
        "date": "2025-01-01",
        "month": "January",
        "year": 2025,
        "expense_name": "Test",
        "description": "Test",
        "amount": 100.0,
        "paid_by": 106,
        "created_by": "memberuser2"
    }, cookies={"session": session_cookie})
    assert response.status_code == 200
    data = response.json()
    assert data["expense_name"] == "Test"

def test_get_expenses():
    response = client.get("/expenses?username=testuser")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

# Test /income endpoints
def test_create_maintenance_success():
    # Register and login
    client.post("/register", json={
        "username": "incomeuser",
        "password": "incomepass",
        "name": "Income User",
        "flat_number": "107",
        "contact_id": "123462",
        "role": "member"
    })
    login_response = client.post("/login", json={
        "username": "incomeuser",
        "password": "incomepass"
    })
    session_cookie = login_response.cookies.get("session")
    
    response = client.post("/income?username=incomeuser", json={
        "owner_name": "Owner",
        "date": "2025-01-01",
        "month": "January",
        "year": 2025,
        "amount": 1000.0,
        "paid_by": 107
    }, cookies={"session": session_cookie})
    assert response.status_code == 200
    data = response.json()
    assert data["owner_name"] == "Owner"

def test_get_maintenance():
    response = client.get("/income?username=incomeuser")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_download_receipt():
    # Assuming a maintenance record exists from previous test
    response = client.get("/income/1/receipt?username=incomeuser")
    assert response.status_code == 200
    # Check if it's a PDF
    assert response.headers["content-type"] == "application/pdf"

# Test /logout endpoint
def test_logout():
    # Login first
    client.post("/register", json={
        "username": "logoutuser",
        "password": "logoutpass",
        "name": "Logout User",
        "flat_number": "108",
        "contact_id": "123463",
        "role": "member"
    })
    login_response = client.post("/login", json={
        "username": "logoutuser",
        "password": "logoutpass"
    })
    session_cookie = login_response.cookies.get("session")
    
    response = client.post("/logout", cookies={"session": session_cookie})
    assert response.status_code == 200
    assert "Logged out successfully" in response.json()["message"]
