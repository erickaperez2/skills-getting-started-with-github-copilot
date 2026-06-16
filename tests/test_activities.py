import pytest


class TestGetActivities:
    def test_get_activities_success(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10
        assert "Chess Club" in data
        assert data["Chess Club"]["max_participants"] == 12

    def test_activities_have_participants(self, client):
        """Test that activities include participant lists"""
        response = client.get("/activities")
        data = response.json()
        for activity_name, activity in data.items():
            assert "participants" in activity
            assert isinstance(activity["participants"], list)


class TestSignup:
    def test_signup_success(self, client):
        """Test successful student signup"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up newstudent@mergington.edu for Chess Club" in response.json()["message"]

    def test_signup_adds_participant(self, client):
        """Test that signup actually adds participant to list"""
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]

    def test_signup_duplicate_email(self, client):
        """Test that duplicate signup is rejected"""
        # Try to signup with existing participant
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity(self, client):
        """Test signup for activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestUnregister:
    def test_unregister_success(self, client):
        """Test successful student unregistration"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        assert "Unregistered michael@mergington.edu" in response.json()["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes participant"""
        client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_registered(self, client):
        """Test unregistering a student who isn't signed up"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
