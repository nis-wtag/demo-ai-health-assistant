from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from core.exceptions import (
    EmailAlreadyRegisteredException,
    InvalidCredentialsException,
)
from models.session import Session
from models.user import User
from services import auth_service
from services.auth_service import (
    authenticate_user,
    get_password_hash,
    login,
    logout,
    refresh,
    register_user,
    verify_password,
)


@pytest.fixture
def mock_db():
    """Provides a MagicMock for the DbSession."""
    return MagicMock(spec=Session)


@pytest.fixture
def mock_user():
    """Provides a reusable mock User object."""
    user = MagicMock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    user.hashed_password = "$argon2id$v=19$m=65536,t=3,p=4$C8s2k/k...$H+...w"
    user.full_name = "Test User"
    return user


@pytest.fixture
def mock_session_obj():
    """Provides a reusable mock Session object."""
    session = MagicMock(spec=Session)
    session.id = 100
    session.user_id = 1
    session.access_token = "old_access_token"
    session.refresh_token = "old_refresh_token"
    session.access_expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    session.refresh_expires_at = datetime.now(timezone.utc) + timedelta(days=6)
    return session


def test_password_utils():
    """
    Tests that get_password_hash and verify_password work together.
    This is a concrete test, not a mock, as they are pure functions.
    """
    password = "password123"
    hashed_password = get_password_hash(password)

    assert password != hashed_password
    assert verify_password(password, hashed_password) is True


def test_register_user_success(mocker, mock_db):
    """
    Tests successful user registration.
    """
    # 1. Arrange (Mock dependencies)
    mocker.patch(
        "services.auth_service.user_repository.get_by_email", return_value=None
    )
    mocker.patch(
        "services.auth_service.get_password_hash",
        return_value="new_hashed_password",
    )
    mock_create = mocker.patch(
        "services.auth_service.user_repository.create",
        return_value=MagicMock(spec=User),
    )

    # 2. Act (Call the function)
    new_user = register_user(
        mock_db, email="new@example.com", password="password123", full_name="New User"
    )

    # 3. Assert (Check results and mock calls)
    auth_service.user_repository.get_by_email.assert_called_once_with(
        mock_db, email="new@example.com"
    )

    mock_create.assert_called_once_with(
        mock_db,
        email="new@example.com",
        hashed_password="new_hashed_password",
        full_name="New User",
    )
    assert new_user is not None


def test_register_user_already_exists(mocker, mock_db, mock_user):
    """
    Tests that registration fails if the email is already taken.
    """
    # 1. Arrange
    # Mock user_repository to return an existing user
    mocker.patch(
        "services.auth_service.user_repository.get_by_email", return_value=mock_user
    )

    # 2. Act & Assert
    # Check that the specific exception is raised
    with pytest.raises(EmailAlreadyRegisteredException):
        register_user(
            mock_db,
            email="test@example.com",
            password="password123",
            full_name="Test User",
        )


# --- Tests for authenticate_user ---


def test_authenticate_user_success(mocker, mock_db, mock_user):
    """
    Tests successful authentication with correct email and password.
    """
    # 1. Arrange
    mocker.patch(
        "services.auth_service.user_repository.get_by_email", return_value=mock_user
    )
    mocker.patch("services.auth_service.verify_password", return_value=True)

    # 2. Act
    authenticated_user = authenticate_user(
        mock_db, email="test@example.com", password="correct_password"
    )

    # 3. Assert
    auth_service.user_repository.get_by_email.assert_called_once_with(
        mock_db, email="test@example.com"
    )
    auth_service.verify_password.assert_called_once_with(
        "correct_password", mock_user.hashed_password
    )
    assert authenticated_user == mock_user


def test_authenticate_user_not_found(mocker, mock_db):
    """
    Tests authentication failure when the user does not exist.
    """
    # 1. Arrange
    mocker.patch(
        "services.auth_service.user_repository.get_by_email", return_value=None
    )

    # 2. Act & Assert
    with pytest.raises(InvalidCredentialsException):
        authenticate_user(
            mock_db, email="not_found@example.com", password="password123"
        )


def test_authenticate_user_wrong_password(mocker, mock_db, mock_user):
    """
    Tests authentication failure with the correct email but wrong password.
    """
    # 1. Arrange
    mocker.patch(
        "services.auth_service.user_repository.get_by_email", return_value=mock_user
    )
    mocker.patch(
        "services.auth_service.verify_password",
        return_value=False,  # Mock password verification to fail
    )

    # 2. Act & Assert
    with pytest.raises(InvalidCredentialsException):
        authenticate_user(mock_db, email="test@example.com", password="wrong_password")


# --- Tests for login ---


def test_login_success(mocker, mock_db, mock_user):
    """
    Tests the complete login flow, mocking dependencies.
    """
    # 1. Arrange
    # Mock the functions *called by* login
    mocker.patch("services.auth_service.authenticate_user", return_value=mock_user)
    mocker.patch(
        "services.auth_service.generate_token",
        side_effect=["mock_access_token", "mock_refresh_token"],
    )
    mocker.patch("services.auth_service.session_service.create_session")

    # 2. Act
    user, access_token, refresh_token = login(
        mock_db, email="test@example.com", password="correct_password"
    )

    # 3. Assert
    assert user == mock_user
    assert access_token == "mock_access_token"
    assert refresh_token == "mock_refresh_token"


# --- Tests for logout ---


def test_logout_success(mocker, mock_db, mock_session_obj):
    """
    Tests successful logout by invalidating the session.
    """
    # 1. Arrange
    mocker.patch(
        "services.auth_service.session_service.get_by_access_token",
        return_value=mock_session_obj,
    )
    mock_invalidate = mocker.patch(
        "services.auth_service.session_service.invalidate_session"
    )

    # 2. Act
    logout(mock_db, access_token="old_access_token")

    # 3. Assert
    auth_service.session_service.get_by_access_token.assert_called_once_with(
        mock_db, "old_access_token"
    )
    mock_invalidate.assert_called_once_with(mock_db, mock_session_obj)


def test_logout_invalid_token(mocker, mock_db):
    """
    Tests that logout fails if the access token is invalid.
    """
    # 1. Arrange
    mocker.patch(
        "services.auth_service.session_service.get_by_access_token",
        return_value=None,  # Mock session not found
    )

    # 2. Act & Assert
    with pytest.raises(InvalidCredentialsException, match="Invalid access token"):
        logout(mock_db, access_token="invalid_token")


# --- Tests for refresh ---


def test_refresh_success(mocker, mock_db, mock_user, mock_session_obj):
    """
    Tests successful token refresh.
    """
    # 1. Arrange
    mocker.patch(
        "services.auth_service.session_service.get_by_refresh_token",
        return_value=mock_session_obj,
    )
    mock_invalidate = mocker.patch(
        "services.auth_service.session_service.invalidate_session"
    )
    mocker.patch(
        "services.auth_service.user_repository.get_by_id", return_value=mock_user
    )
    mocker.patch(
        "services.auth_service.generate_token",
        side_effect=["new_access_token", "new_refresh_token"],
    )
    mock_create_session = mocker.patch(
        "services.auth_service.session_service.create_session"
    )

    # 2. Act
    tokens = refresh(mock_db, refresh_token="old_refresh_token")

    # 3. Assert
    assert tokens == {
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token",
    }
    # Check that old session was invalidated
    mock_invalidate.assert_called_once_with(mock_db, mock_session_obj)
    # Check that new session was created
    mock_create_session.assert_called_once()


def test_refresh_invalid_token(mocker, mock_db):
    """
    Tests refresh failure if token is not found.
    """
    # 1. Arrange
    mocker.patch(
        "services.auth_service.session_service.get_by_refresh_token",
        return_value=None,
    )

    # 2. Act & Assert
    with pytest.raises(
        InvalidCredentialsException, match="Invalid or expired refresh token"
    ):
        refresh(mock_db, refresh_token="invalid_token")


def test_refresh_expired_token(mocker, mock_db, mock_session_obj):
    """
    Tests refresh failure if token is expired.
    """
    # 1. Arrange
    # Mock datetime.now() to be *after* the token's expiry
    mock_now = datetime.now(timezone.utc) + timedelta(days=10)
    mocker.patch("services.auth_service.datetime")
    auth_service.datetime.now.return_value = mock_now

    # Set the mock session's expiry to be in the past
    mock_session_obj.refresh_expires_at = datetime.now(timezone.utc) - timedelta(days=1)

    mocker.patch(
        "services.auth_service.session_service.get_by_refresh_token",
        return_value=mock_session_obj,
    )

    # 2. Act & Assert
    with pytest.raises(
        InvalidCredentialsException, match="Invalid or expired refresh token"
    ):
        refresh(mock_db, refresh_token="expired_token")
