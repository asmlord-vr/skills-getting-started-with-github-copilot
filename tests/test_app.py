import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_state = copy.deepcopy(activities)
    with TestClient(app) as test_client:
        yield test_client
    activities.clear()
    activities.update(original_state)


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"]
    assert payload["Chess Club"]["participants"]


def test_signup_for_activity_success(client):
    email = "newstudent@mergington.edu"

    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_unknown_activity_returns_404(client):
    response = client.post("/activities/Unknown%20Club/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_student_returns_400(client):
    email = "michael@mergington.edu"

    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_student_success(client):
    email = "student-to-remove@mergington.edu"
    activities["Chess Club"]["participants"].append(email)

    response = client.delete("/activities/Chess%20Club/unregister", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_student_not_in_activity_returns_400(client):
    email = "not-a-member@mergington.edu"

    response = client.delete("/activities/Chess%20Club/unregister", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student not signed up for this activity"
