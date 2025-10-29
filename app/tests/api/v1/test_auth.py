from fastapi import status
from fastapi.testclient import TestClient
from models.user import User, UserRole
from services.auth_service import get_password_hash
from sqlalchemy.orm import Session


def test_register_user_successfully(client: TestClient, db_session: Session):
    REGISTER_API_URL = "/api/v1/auth/register"

    registration_data = {
        "email": "testuser@example.com",
        "password": "strongpassword123",
        "full_name": "Test User",
    }

    response = client.post(REGISTER_API_URL, json=registration_data)

    assert response.status_code == status.HTTP_201_CREATED

    # Check in response
    data = response.json()
    assert data["full_name"] == "Test User"
    assert data["role"] == "USER"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data

    # Check in db
    user_in_db = (
        db_session.query(User).filter(User.email == "testuser@example.com").first()
    )
    assert user_in_db is not None
    assert user_in_db.full_name == "Test User"
    assert user_in_db.role == UserRole.USER


def test_register_existing_user_fails(client: TestClient, db_session: Session):
    REGISTER_API_URL = "/api/v1/auth/register"

    existing_user = User(
        email="existing@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Existing User",
    )

    db_session.add(existing_user)
    db_session.commit()

    register_user = {
        "email": "existing@example.com",
        "password": "password123",
        "full_name": "Existing User",
    }

    response = client.post(REGISTER_API_URL, json=register_user)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert not data["success"]
    assert "error" in data
    assert data["error"] == "Email already registered"


def test_login_successfully(client: TestClient, test_user: User):
    LOGIN_API_URL = "/api/v1/auth/login"

    login_data = {"email": "test_user@example.com", "password": "password123"}

    response = client.post(LOGIN_API_URL, json=login_data)

    assert response.status_code == status.HTTP_200_OK

    # Check response
    data = response.json()
    assert data["full_name"] == "Test User"
    assert data["role"] == "USER"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data

    # Check cookies
    cookies = response.cookies
    assert "access_token" in cookies
    assert "refresh_token" in cookies


def test_login_wrong_password_fails(client: TestClient, test_user: User):
    LOGIN_API_URL = "/api/v1/auth/login"

    login_data = {"email": "test_user@example.com", "password": "wrongpassword"}

    response = client.post(LOGIN_API_URL, json=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert not data["success"]
    assert "error" in data
    assert data["error"] == "Invalid credentials"


def test_non_existent_user_login_fails(client: TestClient, test_user: User):
    LOGIN_API_URL = "/api/v1/auth/login"

    login_data = {"email": "non_existent_user@example.com", "password": "wrongpassword"}

    response = client.post(LOGIN_API_URL, json=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert not data["success"]
    assert "error" in data
    assert data["error"] == "Invalid credentials"


def test_logout_successfully(client: TestClient, test_user: User):
    LOGIN_API_URL = "/api/v1/auth/login"
    LOGOUT_API_URL = "/api/v1/auth/logout"

    login_data = {"email": "test_user@example.com", "password": "password123"}

    login_response = client.post(LOGIN_API_URL, json=login_data)

    assert login_response.status_code == status.HTTP_200_OK
    cookies = login_response.cookies
    assert "access_token" in cookies
    assert "refresh_token" in cookies

    access_token = cookies.get("access_token")
    refresh_token = cookies.get("refresh_token")

    client.cookies["access_token"] = access_token
    client.cookies["refresh_token"] = refresh_token

    logout_response = client.post(LOGOUT_API_URL)

    assert logout_response.status_code == status.HTTP_200_OK
    assert "detail" in logout_response.json()
    assert logout_response.json()["detail"] == "Logged out successfully"
