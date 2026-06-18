"""
Tests for Mergington High School API using AAA (Arrange-Act-Assert) pattern
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def reset_activities():
    """Reset global activities data before each test"""
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Join the school soccer team for drills and competitive matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["nina@mergington.edu", "alex@mergington.edu"]
        },
        "Swimming Squad": {
            "description": "Train in swimming techniques and prepare for swim meets",
            "schedule": "Mondays, Wednesdays, 5:00 PM - 6:30 PM",
            "max_participants": 16,
            "participants": ["mia@mergington.edu", "tyler@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and mixed media art projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["sarah@mergington.edu", "lucas@mergington.edu"]
        },
        "Drama Society": {
            "description": "Rehearse scenes, perform plays, and build stagecraft skills",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Practice problem solving and compete in math contests",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 12,
            "participants": ["rachel@mergington.edu", "noah@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["zara@mergington.edu", "liam@mergington.edu"]
        }
    }

    activities.clear()
    activities.update(original_activities)

    yield

    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_returns_all_activities(self, client, reset_activities):
        # Arrange
        expected_activity_count = 9

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert len(response.json()) == expected_activity_count
        assert "Chess Club" in response.json()
        assert "Programming Class" in response.json()

    def test_get_activities_returns_correct_structure(self, client, reset_activities):
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        activities_data = response.json()

        # Assert
        assert response.status_code == 200
        for activity in activities_data.values():
            for field in required_fields:
                assert field in activity


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_success(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_for_nonexistent_activity_returns_404(self, client, reset_activities):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_student_returns_400(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already enrolled

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""

    def test_remove_participant_success(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_remove_from_nonexistent_activity_returns_404(self, client, reset_activities):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_remove_nonexistent_participant_returns_404(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    def test_state_isolation_between_tests(self, client, reset_activities):
        # Arrange - verify reset happens between tests
        activity_name = "Programming Class"

        # Act
        response = client.get("/activities")

        # Assert - verify state is clean (original participants)
        assert response.status_code == 200
        assert activities[activity_name]["participants"] == ["emma@mergington.edu", "sophia@mergington.edu"]
