import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def api(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Learn and play chess",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": ["existing@mergington.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)
    return TestClient(app_module.app), test_activities


def test_get_activities_returns_activity_data(api):
    client, test_activities = api

    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == test_activities


def test_signup_adds_participant(api):
    client, test_activities = api
    email = "new@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in test_activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(api):
    client, test_activities = api
    email = test_activities["Chess Club"]["participants"][0]

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert test_activities["Chess Club"]["participants"].count(email) == 1


def test_signup_rejects_unknown_activity(api):
    client, _ = api

    response = client.post("/activities/Unknown/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(api):
    client, test_activities = api
    email = test_activities["Chess Club"]["participants"][0]

    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert email not in test_activities["Chess Club"]["participants"]


def test_unregister_rejects_unregistered_participant(api):
    client, _ = api

    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "absent@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_rejects_unknown_activity(api):
    client, _ = api

    response = client.delete("/activities/Unknown/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"