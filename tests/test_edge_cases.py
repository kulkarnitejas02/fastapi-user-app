import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models
from main import app
from database import Base
from dependencies import get_db

# Setup test database
TEST_DATABASE_URL = "sqlite:///./test_edge_cases.db"
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
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# ============ BOUNDARY & EDGE CASES ============

def test_register_very_long_username():
    """Test registration with extremely long username"""
    response = client.post("/register", json={
        "username": "a" * 1000,  # Very long username
        "password": "pass",
        "name": "Test",
        "flat_number": 101,
        "contact_id": "123",
        "role": "member"
    })
    # Should either accept or reject gracefully
    assert response.status_code in [200, 422, 400]

def test_register_very_long_password():
    """Test registration with extremely long password"""
    response = client.post("/register", json={
        "username": "longpassuser",
        "password": "a" * 10000,  # Very long password
        "name": "Test",
        "flat_number": 101,
        "contact_id": "123",
        "role": "member"
    })
    assert response.status_code in [200, 422, 400]

def test_register_with_null_values():
    """Test registration with null values"""
    response = client.post("/register", json={
        "username": None,
        "password": None,
        "name": None,
        "flat_number": None,
        "contact_id": None,
        "role": None
    })
    assert response.status_code == 422

def test_register_with_empty_strings():
    """Test registration with all empty strings"""
    response = client.post("/register", json={
        "username": "",
        "password": "",
        "name": "",
        "flat_number": "",
        "contact_id": "",
        "role": ""
    })
    assert response.status_code == 422

def test_expense_future_date():
    """Test expense with far future date"""
    client.post("/register", json={
        "username": "futureuser",
        "password": "pass",
        "name": "Test",
        "flat_number": 101,
        "contact_id": "123",
        "role": "secretary"
    })
    login = client.post("/login", json={"username": "futureuser", "password": "pass"})
    session = login.cookies.get("session")

    response = client.post("/expenses?username=futureuser", json={
        "date": "2100-12-31",  # Far future
        "month": "December",
        "year": 2100,
        "expense_name": "Future",
        "description": "Test",
        "amount": 100.0,
        "paid_by": 1,
        "created_by": "futureuser"
    }, cookies={"session": session})
    assert response.status_code == 200

def test_expense_very_old_date():
    """Test expense with very old date"""
    client.post("/register", json={
        "username": "olduser",
        "password": "pass",
        "name": "Test",
        "flat_number": 101,
        "contact_id": "123",
        "role": "secretary"
    })
    login = client.post("/login", json={"username": "olduser", "password": "pass"})
    session = login.cookies.get("session")

    response = client.post("/expenses?username=olduser", json={
        "date": "1900-01-01",  # Very old
        "month": "January",
        "year": 1900,
        "expense_name": "Old",
        "description": "Test",
        "amount": 100.0,
        "paid_by": 1,
        "created_by": "olduser"
    }, cookies={"session": session})
    assert response.status_code == 200

def test_flat_number_zero():
    """Test registration with flat number as zero"""
    response = client.post("/register", json={
        "username": "zeroflat",
        "password": "pass",
        "name": "Test",
        "flat_number": 0,
        "contact_id": "123",
        "role": "member"
    })
    # Should probably be rejected but schema doesn't validate
    assert response.status_code in [200, 422]

def test_flat_number_max_int():
    """Test registration with maximum integer flat number"""
    response = client.post("/register", json={
        "username": "maxflat",
        "password": "pass",
        "name": "Test",
        "flat_number": 2147483647,  # Max 32-bit int
        "contact_id": "123",
        "role": "member"
    })
    assert response.status_code in [200, 422]

def test_expense_very_small_amount():
    """Test expense with very small decimal amount"""
    client.post("/register", json={
        "username": "smalluser",
        "password": "pass",
        "name": "Test",
        "flat_number": 101,
        "contact_id": "123",
        "role": "secretary"
    })
    login = client.post("/login", json={"username": "smalluser", "password": "pass"})
    session = login.cookies.get("session")

    response = client.post("/expenses?username=smalluser", json={
        "date": "2025-01-01",
        "month": "January",
        "year": 2025,
        "expense_name": "Small",
        "description": "Test",
        "amount": 0.01,  # Smallest typical amount
        "paid_by": 1,
        "created_by": "smalluser"
    }, cookies={"session": session})
    assert response.status_code == 200

def test_expense_many_decimals():
    """Test expense with many decimal places"""
    client.post("/register", json={
        "username": "decimaluser",
        "password": "pass",
        "name": "Test",
        "flat_number": 101,
        "contact_id": "123",
        "role": "secretary"
    })
    login = client.post("/login", json={"username": "decimaluser", "password": "pass"})
    session = login.cookies.get("session")

    response = client.post("/expenses?username=decimaluser", json={
        "date": "2025-01-01",
        "month": "January",
        "year": 2025,
        "expense_name": "Decimal",
        "description": "Test",
        "amount": 100.123456789,  # Many decimals
        "paid_by": 1,
        "created_by": "decimaluser"
    }, cookies={"session": session})
    assert response.status_code == 200

# ============ CONCURRENT ACCESS ============

def test_same_user_multiple_sessions():
    """Test same user logging in from multiple sessions"""
    client.post("/register", json={
        "username": "concurrentuser",
        "password": "pass",
        "name": "Test",
        "flat_number": 101,
        "contact_id": "123",
        "role": "member"
    })

    # Login twice
    login1 = client.post("/login", json={"username": "concurrentuser", "password": "pass"})
    login2 = client.post("/login", json={"username": "concurrentuser", "password": "pass"})

    session1 = login1.cookies.get("session")
    session2 = login2.cookies.get("session")

    # Both sessions should be valid
    response1 = client.get("/me", cookies={"session": session1})
    response2 = client.get("/me", cookies={"session": session2})

    assert response1.status_code == 200
    assert response2.status_code == 200

# ============ MISSING/EXTRA PARAMETERS ============

def test_expense_extra_unknown_fields():
    """Test expense creation with extra unknown fields"""
    client.post("/register", json={
        "username": "extrauser",
        "password": "pass",
        "name": "Test",
        "flat_number": 101,
        "contact_id": "123",
        "role": "secretary"
    })
    login = client.post("/login", json={"username": "extrauser", "password": "pass"})
    session = login.cookies.get("session")

    response = client.post("/expenses?username=extrauser", json={
        "date": "2025-01-01",
        "month": "January",
        "year": 2025,
        "expense_name": "Test",
        "description": "Test",
        "amount": 100.0,
        "paid_by": 1,
        "created_by": "extrauser",
        "unknown_field": "should_be_ignored",
        "another_field": 123
    }, cookies={"session": session})
    # Pydantic should ignore extra fields
    assert response.status_code == 200

def test_login_with_extra_fields():
    """Test login with extra fields"""
    client.post("/register", json={
        "username": "extrauser2",
        "password": "pass",
        "name": "Test",
        "flat_number": 101,
        "contact_id": "123",
        "role": "member"
    })

    response = client.post("/login", json={
        "username": "extrauser2",
        "password": "pass",
        "extra_field": "should_be_ignored"
    })
    assert response.status_code == 200

# ============ TYPE COERCION VULNERABILITIES ============

def test_flat_number_string_numeric():
    """Test if flat_number accepts numeric string"""
    response = client.post("/register", json={
        "username": "stringnum",
        "password": "pass",
        "name": "Test",
        "flat_number": "101",  # String that looks like number
        "contact_id": "123",
        "role": "member"
    })
    # Pydantic should convert if possible
    assert response.status_code == 200

def test_year_string_numeric():
    """Test if year accepts numeric string"""
    client.post("/register", json={
        "username": "yearuser",
        "password": "pass",
        "name": "Test",
        "flat_number": 101,
        "contact_id": "123",
        "role": "member"
    })
    login = client.post("/login", json={"username": "yearuser", "password": "pass"})
    session = login.cookies.get("session")

    response = client.post("/income?username=yearuser", json={
        "owner_name": "Owner",
        "date": "2025-01-01",
        "month": "January",
        "year": "2025",  # String
        "amount": 100.0,
        "paid_by": 1
    }, cookies={"session": session})
    # Backend may return 400 for invalid year type
    assert response.status_code in [200, 400, 422]

# ============ WHITESPACE & ENCODING ============

def test_username_with_spaces():
    """Test username containing spaces"""
    response = client.post("/register", json={
        "username": "user name with spaces",
        "password": "pass",
        "name": "Test",
        "flat_number": 101,
        "contact_id": "123",
        "role": "member"
    })
    assert response.status_code in [200, 422]

def test_username_with_leading_trailing_spaces():
    """Test username with leading/trailing spaces"""
    response = client.post("/register", json={
        "username": "  username  ",
        "password": "pass",
        "name": "Test",
        "flat_number": 101,
        "contact_id": "123",
        "role": "member"
    })
    assert response.status_code == 200

def test_expense_name_only_whitespace():
    """Test expense_name with only whitespace"""
    client.post("/register", json={
        "username": "whitespaceuser",
        "password": "pass",
        "name": "Test",
        "flat_number": 101,
        "contact_id": "123",
        "role": "secretary"
    })
    login = client.post("/login", json={"username": "whitespaceuser", "password": "pass"})
    session = login.cookies.get("session")

    response = client.post("/expenses?username=whitespaceuser", json={
        "date": "2025-01-01",
        "month": "January",
        "year": 2025,
        "expense_name": "   ",  # Only spaces
        "description": "Test",
        "amount": 100.0,
        "paid_by": 1,
        "created_by": "whitespaceuser"
    }, cookies={"session": session})
    # Should allow (schema doesn't validate)
    assert response.status_code in [200, 422]

def test_month_case_sensitivity():
    """Test month field with different cases"""
    client.post("/register", json={
        "username": "monthuser",
        "password": "pass",
        "name": "Test",
        "flat_number": 101,
        "contact_id": "123",
        "role": "secretary"
    })
    login = client.post("/login", json={"username": "monthuser", "password": "pass"})
    session = login.cookies.get("session")

    response = client.post("/expenses?username=monthuser", json={
        "date": "2025-01-01",
        "month": "january",  # Lowercase
        "year": 2025,
        "expense_name": "Test",
        "description": "Test",
        "amount": 100.0,
        "paid_by": 1,
        "created_by": "monthuser"
    }, cookies={"session": session})
    assert response.status_code == 200
