"""
Test Suite for Scheduler and Conversations Features
Tests:
1. Scheduler sends messages to community group
2. Conversations API returns sessions with messages
3. Chat participants API returns 27 CRM contacts
4. Community session contains Coach Bassi messages
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSchedulerHealth:
    """Test scheduler is active and healthy"""
    
    def test_scheduler_health_endpoint(self):
        """Verify scheduler is running and active"""
        response = requests.get(f"{BASE_URL}/api/scheduler/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "active"
        assert "last_run" in data
        print(f"✅ Scheduler status: {data['status']}, last run: {data['last_run']}")


class TestCommunityMessages:
    """Test community session messages including Coach Bassi automated messages"""
    
    COMMUNITY_SESSION_ID = "5c8b0ed0-07fd-4b9b-b17a-bd569dc966f6"
    
    def test_community_session_exists(self):
        """Verify community session exists"""
        response = requests.get(f"{BASE_URL}/api/chat/sessions/{self.COMMUNITY_SESSION_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("id") == self.COMMUNITY_SESSION_ID
        assert data.get("mode") == "community"
        print(f"✅ Community session found: {data.get('title', 'No title')}")
    
    def test_community_session_has_messages(self):
        """Verify community session has messages"""
        response = requests.get(f"{BASE_URL}/api/chat/sessions/{self.COMMUNITY_SESSION_ID}/messages")
        assert response.status_code == 200
        messages = response.json()
        assert len(messages) > 0
        print(f"✅ Community session has {len(messages)} messages")
    
    def test_coach_bassi_messages_present(self):
        """Verify Coach Bassi automated messages are in the community session"""
        response = requests.get(f"{BASE_URL}/api/chat/sessions/{self.COMMUNITY_SESSION_ID}/messages")
        assert response.status_code == 200
        messages = response.json()
        
        # Filter Coach Bassi messages
        coach_bassi_messages = [m for m in messages if "Coach Bassi" in m.get("sender_name", "")]
        assert len(coach_bassi_messages) >= 3, f"Expected at least 3 Coach Bassi messages, found {len(coach_bassi_messages)}"
        
        # Verify the scheduled message (Test Automate 2min)
        scheduled_message = None
        for msg in coach_bassi_messages:
            if "Message automatique" in msg.get("content", "") or "scheduler" in msg.get("content", "").lower():
                scheduled_message = msg
                break
        
        assert scheduled_message is not None, "Scheduled message from scheduler not found"
        print(f"✅ Found {len(coach_bassi_messages)} Coach Bassi messages")
        print(f"✅ Scheduled message found: {scheduled_message['content'][:50]}...")
        
        # Print all Coach Bassi messages
        for msg in coach_bassi_messages:
            print(f"  - {msg['created_at'][:19]}: {msg['content'][:60]}...")


class TestCRMContacts:
    """Test CRM contacts/participants API"""
    
    def test_chat_participants_count(self):
        """Verify 27 CRM contacts are returned"""
        response = requests.get(f"{BASE_URL}/api/chat/participants")
        assert response.status_code == 200
        participants = response.json()
        assert len(participants) == 27, f"Expected 27 contacts, found {len(participants)}"
        print(f"✅ CRM contacts count: {len(participants)}")
    
    def test_chat_participants_structure(self):
        """Verify participant data structure"""
        response = requests.get(f"{BASE_URL}/api/chat/participants")
        assert response.status_code == 200
        participants = response.json()
        
        # Check first participant has required fields
        if participants:
            p = participants[0]
            assert "id" in p
            assert "name" in p
            assert "email" in p
            assert "source" in p
            assert "created_at" in p
            print(f"✅ Participant structure valid: {p['name']} ({p['email']})")


class TestConversationsAPI:
    """Test conversations/sessions API"""
    
    def test_chat_sessions_list(self):
        """Verify chat sessions API returns list"""
        response = requests.get(f"{BASE_URL}/api/chat/sessions")
        assert response.status_code == 200
        sessions = response.json()
        assert isinstance(sessions, list)
        print(f"✅ Chat sessions count: {len(sessions)}")
    
    def test_chat_sessions_structure(self):
        """Verify session data structure"""
        response = requests.get(f"{BASE_URL}/api/chat/sessions")
        assert response.status_code == 200
        sessions = response.json()
        
        if sessions:
            s = sessions[0]
            assert "id" in s
            assert "mode" in s
            assert "created_at" in s
            print(f"✅ Session structure valid: {s['id'][:8]}... mode={s['mode']}")


class TestReservationsExport:
    """Test reservations API for CSV export"""
    
    def test_reservations_all_data_endpoint(self):
        """Verify reservations API with all_data=true works"""
        response = requests.get(f"{BASE_URL}/api/reservations?all_data=true")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        print(f"✅ Reservations export endpoint works, count: {len(data['data'])}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
