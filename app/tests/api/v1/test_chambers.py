import pytest
from fastapi import status
from fastapi.testclient import TestClient
from models.chamber import Chamber
from sqlalchemy.orm import Session


@pytest.fixture(scope="function")
def test_chamber(db_session: Session):
    """
    Fixture to create a sample chamber in the database for testing.
    This chamber is cleaned up after the test.
    """
    chamber = Chamber(chamber_name="Test Chamber", address="123 Test St, Test City")

    db_session.add(chamber)
    db_session.commit()
    db_session.refresh(chamber)

    yield chamber

    db_session.delete(chamber)
    db_session.commit()


def test_get_chamber_success(client: TestClient, authenticated_user, test_chamber):
    CHAMBER_API_URL = "/api/v1/chambers/"

    response = client.get(CHAMBER_API_URL)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["chamber_name"] == "Test Chamber"


def test_get_chambers_unauthenticated(client: TestClient):
    CHAMBER_API_URL = "/api/v1/chambers/"

    response = client.get(CHAMBER_API_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_search_chambers_success(
    client: TestClient, authenticated_user, test_chamber: Chamber
):
    CHAMBER_API_QUERY_URL = "/api/v1/chambers/search?params=Test%20Chamber"

    response = client.get(CHAMBER_API_QUERY_URL)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["id"] == test_chamber.id
    assert data[0]["chamber_name"] == "Test Chamber"


def test_search_chambers_unauthenticated(client: TestClient, test_chamber: Chamber):
    CHAMBER_API_QUERY_URL = "/api/v1/chambers/search?params=Test%20Chamber"

    response = client.get(CHAMBER_API_QUERY_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_chamber_details_success(
    client: TestClient, authenticated_user, test_chamber: Chamber
):
    response = client.get(f"/api/v1/chambers/{test_chamber.id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_chamber.id
    assert data["chamber_name"] == test_chamber.chamber_name


def test_get_chamber_details_not_found(
    client: TestClient, authenticated_user, test_chamber: Chamber
):
    response = client.get("/api/v1/chambers/999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
