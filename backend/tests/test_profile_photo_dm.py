"""
Test Profile Photo Upload and DM (Private Messaging) APIs
Tests for Coach Bassi App - Afroboost

Features tested:
1. Profile photo upload via /api/upload/profile-photo
2. Private conversations via /api/private/conversations
3. Private messages via /api/private/messages
4. Promo code validation for subscriber flow
"""

import pytest
import requests
import os
import uuid
import io
from PIL import Image

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthCheck:
    """Basic health check"""
    
    def test_api_health(self):
        """Test API is healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✅ API health check passed")


class TestPromoCodeValidation:
    """Test promo code validation for subscriber flow"""
    
    def test_validate_basxx_code_correct_email(self):
        """Test basxx code validates with correct email bassicustomshoes@gmail.com"""
        response = requests.post(f"{BASE_URL}/api/discount-codes/validate", json={
            "code": "basxx",
            "email": "bassicustomshoes@gmail.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("valid") == True, f"Expected valid=True, got: {data}"
        print(f"✅ basxx code validated for correct email: {data}")
    
    def test_validate_basxx_code_wrong_email(self):
        """Test basxx code rejected with wrong email"""
        response = requests.post(f"{BASE_URL}/api/discount-codes/validate", json={
            "code": "basxx",
            "email": "wrong@email.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("valid") == False, f"Expected valid=False, got: {data}"
        assert "réservé" in data.get("message", "").lower() or "autre compte" in data.get("message", "").lower()
        print(f"✅ basxx code correctly rejected for wrong email: {data.get('message')}")
    
    def test_validate_basxx_case_insensitive(self):
        """Test code validation is case-insensitive"""
        response = requests.post(f"{BASE_URL}/api/discount-codes/validate", json={
            "code": "BASXX",  # Uppercase
            "email": "bassicustomshoes@gmail.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("valid") == True, f"Expected valid=True for uppercase code, got: {data}"
        print("✅ Code validation is case-insensitive")


class TestProfilePhotoUpload:
    """Test profile photo upload API"""
    
    def test_upload_profile_photo_success(self):
        """Test successful profile photo upload"""
        # Create a test image in memory
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        participant_id = f"test_user_{uuid.uuid4().hex[:8]}"
        
        files = {'file': ('test_photo.jpg', img_bytes, 'image/jpeg')}
        data = {'participant_id': participant_id}
        
        response = requests.post(
            f"{BASE_URL}/api/upload/profile-photo",
            files=files,
            data=data
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        result = response.json()
        assert "url" in result, f"Expected 'url' in response, got: {result}"
        assert result["url"].startswith("/api/uploads/profiles/")
        print(f"✅ Profile photo uploaded successfully: {result['url']}")
        return result["url"]
    
    def test_upload_profile_photo_invalid_type(self):
        """Test upload rejects non-image files"""
        files = {'file': ('test.txt', b'not an image', 'text/plain')}
        data = {'participant_id': 'test_user'}
        
        response = requests.post(
            f"{BASE_URL}/api/upload/profile-photo",
            files=files,
            data=data
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid file type, got {response.status_code}"
        print("✅ Invalid file type correctly rejected")


class TestPrivateConversations:
    """Test private messaging (DM) API"""
    
    @pytest.fixture
    def test_participants(self):
        """Create test participant IDs"""
        return {
            "user1_id": f"test_user_1_{uuid.uuid4().hex[:8]}",
            "user1_name": "Test User 1",
            "user2_id": f"test_user_2_{uuid.uuid4().hex[:8]}",
            "user2_name": "Test User 2"
        }
    
    def test_create_private_conversation(self, test_participants):
        """Test creating a new private conversation"""
        response = requests.post(f"{BASE_URL}/api/private/conversations", json={
            "participant_1_id": test_participants["user1_id"],
            "participant_1_name": test_participants["user1_name"],
            "participant_2_id": test_participants["user2_id"],
            "participant_2_name": test_participants["user2_name"]
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data, f"Expected 'id' in response, got: {data}"
        assert data["participant_1_id"] == test_participants["user1_id"]
        assert data["participant_2_id"] == test_participants["user2_id"]
        print(f"✅ Private conversation created: {data['id']}")
        return data
    
    def test_get_existing_conversation(self, test_participants):
        """Test that requesting same conversation returns existing one"""
        # Create first conversation
        response1 = requests.post(f"{BASE_URL}/api/private/conversations", json={
            "participant_1_id": test_participants["user1_id"],
            "participant_1_name": test_participants["user1_name"],
            "participant_2_id": test_participants["user2_id"],
            "participant_2_name": test_participants["user2_name"]
        })
        conv1 = response1.json()
        
        # Request same conversation again
        response2 = requests.post(f"{BASE_URL}/api/private/conversations", json={
            "participant_1_id": test_participants["user1_id"],
            "participant_1_name": test_participants["user1_name"],
            "participant_2_id": test_participants["user2_id"],
            "participant_2_name": test_participants["user2_name"]
        })
        conv2 = response2.json()
        
        assert conv1["id"] == conv2["id"], "Should return same conversation ID"
        print("✅ Existing conversation correctly returned")
    
    def test_get_conversation_reverse_order(self, test_participants):
        """Test that conversation is found regardless of participant order"""
        # Create conversation with user1 as participant_1
        response1 = requests.post(f"{BASE_URL}/api/private/conversations", json={
            "participant_1_id": test_participants["user1_id"],
            "participant_1_name": test_participants["user1_name"],
            "participant_2_id": test_participants["user2_id"],
            "participant_2_name": test_participants["user2_name"]
        })
        conv1 = response1.json()
        
        # Request with reversed order (user2 as participant_1)
        response2 = requests.post(f"{BASE_URL}/api/private/conversations", json={
            "participant_1_id": test_participants["user2_id"],
            "participant_1_name": test_participants["user2_name"],
            "participant_2_id": test_participants["user1_id"],
            "participant_2_name": test_participants["user1_name"]
        })
        conv2 = response2.json()
        
        assert conv1["id"] == conv2["id"], "Should return same conversation regardless of order"
        print("✅ Conversation found with reversed participant order")


class TestPrivateMessages:
    """Test private message sending and retrieval"""
    
    @pytest.fixture
    def conversation(self):
        """Create a test conversation"""
        user1_id = f"msg_test_user_1_{uuid.uuid4().hex[:8]}"
        user2_id = f"msg_test_user_2_{uuid.uuid4().hex[:8]}"
        
        response = requests.post(f"{BASE_URL}/api/private/conversations", json={
            "participant_1_id": user1_id,
            "participant_1_name": "Message Test User 1",
            "participant_2_id": user2_id,
            "participant_2_name": "Message Test User 2"
        })
        conv = response.json()
        conv["user1_id"] = user1_id
        conv["user2_id"] = user2_id
        return conv
    
    def test_send_private_message(self, conversation):
        """Test sending a private message"""
        response = requests.post(f"{BASE_URL}/api/private/messages", json={
            "conversation_id": conversation["id"],
            "sender_id": conversation["user1_id"],
            "sender_name": "Message Test User 1",
            "recipient_id": conversation["user2_id"],
            "recipient_name": "Message Test User 2",
            "content": "Hello, this is a test message!"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["content"] == "Hello, this is a test message!"
        assert data["sender_id"] == conversation["user1_id"]
        print(f"✅ Private message sent: {data['id']}")
        return data
    
    def test_get_private_messages(self, conversation):
        """Test retrieving messages from a conversation"""
        # Send a message first
        requests.post(f"{BASE_URL}/api/private/messages", json={
            "conversation_id": conversation["id"],
            "sender_id": conversation["user1_id"],
            "sender_name": "Message Test User 1",
            "recipient_id": conversation["user2_id"],
            "recipient_name": "Message Test User 2",
            "content": "Test message for retrieval"
        })
        
        # Get messages
        response = requests.get(f"{BASE_URL}/api/private/messages/{conversation['id']}")
        
        assert response.status_code == 200
        messages = response.json()
        assert isinstance(messages, list)
        assert len(messages) >= 1
        assert any(m["content"] == "Test message for retrieval" for m in messages)
        print(f"✅ Retrieved {len(messages)} messages from conversation")
    
    def test_mark_messages_read(self, conversation):
        """Test marking messages as read"""
        # Send a message
        requests.post(f"{BASE_URL}/api/private/messages", json={
            "conversation_id": conversation["id"],
            "sender_id": conversation["user1_id"],
            "sender_name": "Message Test User 1",
            "recipient_id": conversation["user2_id"],
            "recipient_name": "Message Test User 2",
            "content": "Message to be marked as read"
        })
        
        # Mark as read by recipient
        response = requests.put(
            f"{BASE_URL}/api/private/messages/read/{conversation['id']}",
            params={"reader_id": conversation["user2_id"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✅ Messages marked as read: {data.get('marked_read', 0)} messages")
    
    def test_get_unread_count(self, conversation):
        """Test getting unread message count"""
        # Send a message
        requests.post(f"{BASE_URL}/api/private/messages", json={
            "conversation_id": conversation["id"],
            "sender_id": conversation["user1_id"],
            "sender_name": "Message Test User 1",
            "recipient_id": conversation["user2_id"],
            "recipient_name": "Message Test User 2",
            "content": "Unread message"
        })
        
        # Get unread count for recipient
        response = requests.get(f"{BASE_URL}/api/private/unread/{conversation['user2_id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert "unread_count" in data
        print(f"✅ Unread count retrieved: {data['unread_count']}")


class TestSmartEntry:
    """Test smart-entry API for subscriber identification"""
    
    def test_smart_entry_new_user(self):
        """Test smart-entry creates session for new user"""
        unique_name = f"TestUser_{uuid.uuid4().hex[:6]}"
        
        response = requests.post(f"{BASE_URL}/api/chat/smart-entry", json={
            "name": unique_name,  # API expects "name" not "firstName"
            "whatsapp": "+41791234567",
            "email": f"{unique_name.lower()}@test.com"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "session" in data or "sessionId" in data or "participant_id" in data
        print(f"✅ Smart-entry created session for new user: {unique_name}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
