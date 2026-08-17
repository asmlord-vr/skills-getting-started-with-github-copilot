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
    # Arrange
    # No special setup needed for this read-only endpoint.

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"]
    assert payload["Chess Club"]["participants"]


def test_signup_for_activity_success(client):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_unknown_activity_returns_404(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post("/activities/Unknown%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_student_returns_400(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_student_success(client):
    # Arrange
    email = "student-to-remove@mergington.edu"
    activities["Chess Club"]["participants"].append(email)

    # Act
    response = client.delete("/activities/Chess%20Club/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_student_not_in_activity_returns_400(client):
    # Arrange
    email = "not-a-member@mergington.edu"

    # Act
    response = client.delete("/activities/Chess%20Club/unregister", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not signed up for this activity"
