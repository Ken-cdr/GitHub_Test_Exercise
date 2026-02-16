import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_success():
    response = client.post("/activities/Chess%20Club/signup?email=tester@mergington.edu")
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    # Clean up: remove the test participant
    data = client.get("/activities").json()
    if "tester@mergington.edu" in data["Chess Club"]["participants"]:
        data["Chess Club"]["participants"].remove("tester@mergington.edu")

def test_signup_duplicate():
    # Add participant first
    client.post("/activities/Chess%20Club/signup?email=dupe@mergington.edu")
    # Try to add again
    response = client.post("/activities/Chess%20Club/signup?email=dupe@mergington.edu")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]
    # Clean up
    data = client.get("/activities").json()
    if "dupe@mergington.edu" in data["Chess Club"]["participants"]:
        data["Chess Club"]["participants"].remove("dupe@mergington.edu")

def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent/signup?email=ghost@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_signup_activity_full():
    # Fill up the activity
    data = client.get("/activities").json()
    activity = data["Tennis Club"]
    max_participants = activity["max_participants"]
    # Add fake participants to fill
    for i in range(len(activity["participants"]), max_participants):
        client.post(f"/activities/Tennis%20Club/signup?email=fake{i}@mergington.edu")
    # Now try to add one more
    response = client.post("/activities/Tennis%20Club/signup?email=overflow@mergington.edu")
    assert response.status_code == 400
    assert "Activity is full" in response.json()["detail"]
    # Clean up: remove fake participants
    data = client.get("/activities").json()
    activity = data["Tennis Club"]
    activity["participants"] = [p for p in activity["participants"] if not p.startswith("fake") and p != "overflow@mergington.edu"]
