from fastapi.testclient import TestClient
import copy
import pytest

from src.app import app, activities


@pytest.fixture
def client():
    # Snapshot activities and restore after each test to avoid cross-test pollution
    original = copy.deepcopy(activities)
    client = TestClient(app)
    yield client
    activities.clear()
    activities.update(original)


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Basketball" in data


def test_signup_and_duplicate(client):
    email = "testuser@example.com"
    # Signup
    resp = client.post(f"/activities/Basketball/signup?email={email}")
    assert resp.status_code == 200
    assert email in activities["Basketball"]["participants"]

    # Duplicate signup should return 400
    resp2 = client.post(f"/activities/Basketball/signup?email={email}")
    assert resp2.status_code == 400


def test_unregister(client):
    email = "removeme@example.com"
    # Register then unregister
    resp = client.post(f"/activities/Tennis%20Club/signup?email={email}")
    assert resp.status_code == 200
    assert email in activities["Tennis Club"]["participants"]

    # Now unregister
    resp2 = client.delete(f"/activities/Tennis%20Club/unregister?email={email}")
    assert resp2.status_code == 200
    assert email not in activities["Tennis Club"]["participants"]
