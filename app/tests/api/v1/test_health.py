from fastapi import status
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    API_URL = "/api/v1/health"

    response = client.get(API_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}
