"""
Tests for the High School Management System API endpoints
"""

import pytest
from fastapi import status


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root path redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client, reset_activities):
        """Test that getting activities returns 200 OK"""
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_activities_returns_dict(self, client, reset_activities):
        """Test that getting activities returns a dictionary"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_activities_contains_expected_activities(self, client, reset_activities):
        """Test that the response contains expected activities"""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Soccer Team",
            "Basketball Club",
            "Art Workshop",
            "Drama Club",
            "Math Olympiad",
            "Science Club"
        ]
        
        for activity in expected_activities:
            assert activity in data
    
    def test_activity_has_required_fields(self, client, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data, f"{activity_name} missing {field}"
    
    def test_participants_is_list(self, client, reset_activities):
        """Test that participants field is a list"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_existing_activity_success(self, client, reset_activities):
        """Test successful signup for an existing activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant to the activity"""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signing up for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_duplicate_signup_fails(self, client, reset_activities):
        """Test that signing up twice for same activity fails"""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_multiple_students(self, client, reset_activities):
        """Test signing up multiple students to the same activity"""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(f"/activities/Chess%20Club/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK
        
        # Verify all students were added
        response = client.get("/activities")
        data = response.json()
        
        for email in emails:
            assert email in data["Chess Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant_success(self, client, reset_activities):
        """Test successful unregistration of an existing participant"""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant from the activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        # Unregister the participant
        client.delete(f"/activities/Chess%20Club/unregister?email={email}")
        
        # Verify participant was removed
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]
    
    def test_unregister_from_nonexistent_activity_fails(self, client, reset_activities):
        """Test that unregistering from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent%20Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """Test that unregistering a non-participant returns 404"""
        email = "notregistered@mergington.edu"
        
        response = client.delete(f"/activities/Chess%20Club/unregister?email={email}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"].lower()
    
    def test_signup_and_unregister_workflow(self, client, reset_activities):
        """Test complete workflow of signing up and then unregistering"""
        email = "workflow@mergington.edu"
        activity = "Chess Club"
        
        # Sign up
        signup_response = client.post(f"/activities/{activity.replace(' ', '%20')}/signup?email={email}")
        assert signup_response.status_code == status.HTTP_200_OK
        
        # Verify signup
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}")
        assert unregister_response.status_code == status.HTTP_200_OK
        
        # Verify unregistration
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]


class TestActivityManagement:
    """Integration tests for activity management"""
    
    def test_multiple_activities_independent(self, client, reset_activities):
        """Test that operations on different activities are independent"""
        email = "multitask@mergington.edu"
        
        # Sign up for multiple activities
        activities_to_join = ["Chess Club", "Programming Class", "Gym Class"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity.replace(' ', '%20')}/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK
        
        # Verify all signups
        response = client.get("/activities")
        data = response.json()
        
        for activity in activities_to_join:
            assert email in data[activity]["participants"]
        
        # Unregister from one
        client.delete(f"/activities/Chess%20Club/unregister?email={email}")
        
        # Verify only one was affected
        response = client.get("/activities")
        data = response.json()
        
        assert email not in data["Chess Club"]["participants"]
        assert email in data["Programming Class"]["participants"]
        assert email in data["Gym Class"]["participants"]
    
    def test_participant_count_accuracy(self, client, reset_activities):
        """Test that participant counts are accurate"""
        response = client.get("/activities")
        initial_data = response.json()
        
        initial_count = len(initial_data["Chess Club"]["participants"])
        
        # Add a participant
        client.post("/activities/Chess%20Club/signup?email=counter@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        assert len(data["Chess Club"]["participants"]) == initial_count + 1
        
        # Remove a participant
        client.delete("/activities/Chess%20Club/unregister?email=counter@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        assert len(data["Chess Club"]["participants"]) == initial_count
