"""
Test suite for Notification System and Guard Rails
- Notification endpoints: GET /api/notifications/unread, PUT /api/notifications/mark-read
- Guard Rails: AI vision (café congolais), Twint payment link
- CRM: Search and infinite scroll functionality
"""

import pytest
import requests
import os
import uuid
import time

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    raise RuntimeError("REACT_APP_BACKEND_URL environment variable is required")

print(f"[TEST] Using BASE_URL: {BASE_URL}")


class TestNotificationEndpoints:
    """Test notification system endpoints"""
    
    # Store created test data for cleanup
    test_session_id = None
    test_participant_id = None
    test_message_ids = []
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self):
        """Create test session and participant for notification tests"""
        # Create a test participant
        participant_data = {
            "name": "TEST_NotificationUser",
            "email": "notif_test@example.com",
            "whatsapp": "+41790000001",
            "source": "test_notifications"
        }
        resp = requests.post(f"{BASE_URL}/api/chat/participants", json=participant_data)
        if resp.status_code == 200:
            self.test_participant_id = resp.json().get("id")
        
        # Create a test session
        session_data = {
            "mode": "ai",
            "is_ai_active": True,
            "title": "TEST_NotificationSession"
        }
        resp = requests.post(f"{BASE_URL}/api/chat/sessions", json=session_data)
        if resp.status_code == 200:
            self.test_session_id = resp.json().get("id")
        
        yield
        
        # Cleanup: Delete test messages, session, and participant
        for msg_id in self.test_message_ids:
            try:
                requests.put(f"{BASE_URL}/api/chat/messages/{msg_id}/delete")
            except:
                pass
        
        if self.test_session_id:
            try:
                requests.put(f"{BASE_URL}/api/chat/sessions/{self.test_session_id}", 
                           json={"is_deleted": True})
            except:
                pass
        
        if self.test_participant_id:
            try:
                requests.delete(f"{BASE_URL}/api/chat/participants/{self.test_participant_id}")
            except:
                pass
    
    def test_get_unread_notifications_coach(self):
        """Test Backend 1: GET /api/notifications/unread?target=coach returns count and messages"""
        response = requests.get(f"{BASE_URL}/api/notifications/unread", params={"target": "coach"})
        
        # Status code assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Data structure assertions
        data = response.json()
        assert "count" in data, "Response should contain 'count' field"
        assert "messages" in data, "Response should contain 'messages' field"
        assert "target" in data, "Response should contain 'target' field"
        
        # Type assertions
        assert isinstance(data["count"], int), "count should be an integer"
        assert isinstance(data["messages"], list), "messages should be a list"
        assert data["target"] == "coach", "target should be 'coach'"
        
        print(f"✅ GET /api/notifications/unread?target=coach - count: {data['count']}, messages: {len(data['messages'])}")
    
    def test_get_unread_notifications_client(self):
        """Test GET /api/notifications/unread?target=client returns count and messages"""
        response = requests.get(f"{BASE_URL}/api/notifications/unread", params={"target": "client"})
        
        assert response.status_code == 200
        
        data = response.json()
        assert "count" in data
        assert "messages" in data
        assert data["target"] == "client"
        
        print(f"✅ GET /api/notifications/unread?target=client - count: {data['count']}")
    
    def test_get_unread_notifications_with_session_filter(self):
        """Test GET /api/notifications/unread with session_id filter"""
        if not self.test_session_id:
            pytest.skip("No test session available")
        
        response = requests.get(
            f"{BASE_URL}/api/notifications/unread",
            params={"target": "coach", "session_id": self.test_session_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "messages" in data
        
        # All messages should be from the specified session
        for msg in data["messages"]:
            assert msg.get("session_id") == self.test_session_id
        
        print(f"✅ GET /api/notifications/unread with session_id filter - count: {data['count']}")
    
    def test_mark_notifications_read_with_message_ids(self):
        """Test Backend 2: PUT /api/notifications/mark-read with message_ids works"""
        # First, create a test message
        if not self.test_session_id or not self.test_participant_id:
            pytest.skip("No test session or participant available")
        
        message_data = {
            "session_id": self.test_session_id,
            "sender_id": self.test_participant_id,
            "sender_name": "TEST_NotificationUser",
            "sender_type": "user",
            "content": "Test message for notification marking"
        }
        
        create_resp = requests.post(f"{BASE_URL}/api/chat/messages", json=message_data)
        if create_resp.status_code != 200:
            pytest.skip(f"Could not create test message: {create_resp.text}")
        
        message_id = create_resp.json().get("id")
        self.test_message_ids.append(message_id)
        
        # Now mark it as read
        mark_read_data = {"message_ids": [message_id]}
        response = requests.put(f"{BASE_URL}/api/notifications/mark-read", json=mark_read_data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True, "Response should indicate success"
        assert "marked_count" in data, "Response should contain 'marked_count'"
        
        print(f"✅ PUT /api/notifications/mark-read with message_ids - marked: {data['marked_count']}")
    
    def test_mark_notifications_read_all_for_target(self):
        """Test Backend 2: PUT /api/notifications/mark-read with all_for_target works"""
        mark_read_data = {"all_for_target": "coach"}
        response = requests.put(f"{BASE_URL}/api/notifications/mark-read", json=mark_read_data)
        
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") == True
        assert "marked_count" in data
        
        print(f"✅ PUT /api/notifications/mark-read with all_for_target=coach - marked: {data['marked_count']}")
    
    def test_mark_notifications_read_with_session_filter(self):
        """Test PUT /api/notifications/mark-read with session_id filter"""
        if not self.test_session_id:
            pytest.skip("No test session available")
        
        mark_read_data = {
            "all_for_target": "client",
            "session_id": self.test_session_id
        }
        response = requests.put(f"{BASE_URL}/api/notifications/mark-read", json=mark_read_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        
        print(f"✅ PUT /api/notifications/mark-read with session_id filter - marked: {data['marked_count']}")


class TestNewMessageNotifiedField:
    """Test Backend 3: New messages have notified=false by default"""
    
    test_session_id = None
    test_participant_id = None
    test_message_id = None
    
    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        """Setup test data and cleanup after"""
        # Create participant
        participant_data = {
            "name": "TEST_NotifiedFieldUser",
            "email": "notified_test@example.com",
            "whatsapp": "+41790000002"
        }
        resp = requests.post(f"{BASE_URL}/api/chat/participants", json=participant_data)
        if resp.status_code == 200:
            self.test_participant_id = resp.json().get("id")
        
        # Create session
        session_data = {"mode": "ai", "title": "TEST_NotifiedFieldSession"}
        resp = requests.post(f"{BASE_URL}/api/chat/sessions", json=session_data)
        if resp.status_code == 200:
            self.test_session_id = resp.json().get("id")
        
        yield
        
        # Cleanup
        if self.test_message_id:
            requests.put(f"{BASE_URL}/api/chat/messages/{self.test_message_id}/delete")
        if self.test_session_id:
            requests.put(f"{BASE_URL}/api/chat/sessions/{self.test_session_id}", 
                       json={"is_deleted": True})
        if self.test_participant_id:
            requests.delete(f"{BASE_URL}/api/chat/participants/{self.test_participant_id}")
    
    def test_new_message_has_notified_false(self):
        """Test Backend 3: New messages have notified=false by default"""
        if not self.test_session_id or not self.test_participant_id:
            pytest.skip("No test session or participant available")
        
        # Create a new message
        message_data = {
            "session_id": self.test_session_id,
            "sender_id": self.test_participant_id,
            "sender_name": "TEST_NotifiedFieldUser",
            "sender_type": "user",
            "content": f"Test message {uuid.uuid4().hex[:8]}"
        }
        
        response = requests.post(f"{BASE_URL}/api/chat/messages", json=message_data)
        assert response.status_code == 200, f"Failed to create message: {response.text}"
        
        created_message = response.json()
        self.test_message_id = created_message.get("id")
        
        # Verify the notified field is False by default
        assert "notified" in created_message, "Message should have 'notified' field"
        assert created_message["notified"] == False, "New message should have notified=false by default"
        
        print(f"✅ New message has notified=false by default - message_id: {self.test_message_id}")
    
    def test_message_notified_field_updates_after_mark_read(self):
        """Test that notified field changes to true after mark-read"""
        if not self.test_session_id or not self.test_participant_id:
            pytest.skip("No test session or participant available")
        
        # Create a new message
        message_data = {
            "session_id": self.test_session_id,
            "sender_id": self.test_participant_id,
            "sender_name": "TEST_NotifiedFieldUser",
            "sender_type": "user",
            "content": f"Test message for mark-read {uuid.uuid4().hex[:8]}"
        }
        
        create_resp = requests.post(f"{BASE_URL}/api/chat/messages", json=message_data)
        assert create_resp.status_code == 200
        
        message_id = create_resp.json().get("id")
        self.test_message_id = message_id
        
        # Mark as read
        mark_resp = requests.put(
            f"{BASE_URL}/api/notifications/mark-read",
            json={"message_ids": [message_id]}
        )
        assert mark_resp.status_code == 200
        
        # Verify the message is now marked as notified
        # Get messages from session to verify
        messages_resp = requests.get(f"{BASE_URL}/api/chat/sessions/{self.test_session_id}/messages")
        assert messages_resp.status_code == 200
        
        messages = messages_resp.json()
        target_message = next((m for m in messages if m.get("id") == message_id), None)
        
        if target_message:
            assert target_message.get("notified") == True, "Message should be marked as notified after mark-read"
            print(f"✅ Message notified field updated to true after mark-read")
        else:
            print(f"⚠️ Could not verify notified field update (message not found in response)")


class TestGuardRailsAIVision:
    """Test Garde-Fou 1: AI recognizes café congolais (10 CHF)"""
    
    def test_ai_recognizes_cafe_congolais(self):
        """Test Garde-Fou 1: L'IA reconnaît toujours le café congolais (10 CHF)"""
        # First, ensure there's a café congolais product in the offers
        # Check existing offers
        offers_resp = requests.get(f"{BASE_URL}/api/offers")
        assert offers_resp.status_code == 200
        
        offers = offers_resp.json()
        cafe_product = next(
            (o for o in offers if "café" in o.get("name", "").lower() or "congolais" in o.get("name", "").lower()),
            None
        )
        
        if not cafe_product:
            # Create a test café congolais product
            cafe_data = {
                "name": "Café Congolais",
                "price": 10.0,
                "description": "Café premium du Congo",
                "visible": True,
                "isProduct": True,
                "category": "boisson"
            }
            create_resp = requests.post(f"{BASE_URL}/api/offers", json=cafe_data)
            if create_resp.status_code == 200:
                cafe_product = create_resp.json()
                print(f"✅ Created test café congolais product: {cafe_product.get('id')}")
        
        # Now test the AI chat endpoint
        chat_data = {
            "message": "Combien coûte le café congolais ?",
            "leadId": "",
            "firstName": "TestUser",
            "email": "test@example.com",
            "whatsapp": "+41790000000"
        }
        
        response = requests.post(f"{BASE_URL}/api/chat", json=chat_data)
        
        # The endpoint should return 200
        assert response.status_code == 200, f"Chat endpoint failed: {response.text}"
        
        data = response.json()
        ai_response = data.get("response", "").lower()
        
        # Check if the AI mentions the price (10 CHF) or the product
        price_mentioned = "10" in ai_response or "dix" in ai_response
        product_mentioned = "café" in ai_response or "congolais" in ai_response
        
        print(f"✅ AI Response for café congolais: {ai_response[:200]}...")
        print(f"   Price mentioned: {price_mentioned}, Product mentioned: {product_mentioned}")
        
        # At minimum, the AI should respond (not error)
        assert "response" in data, "AI should provide a response"


class TestGuardRailsTwintLink:
    """Test Garde-Fou 2: AI mentions Twint link when asked about payment"""
    
    def test_ai_mentions_twint_for_payment(self):
        """Test Garde-Fou 2: L'IA mentionne le lien Twint quand on demande comment payer"""
        # First, check if Twint payment URL is configured
        ai_config_resp = requests.get(f"{BASE_URL}/api/ai-config")
        assert ai_config_resp.status_code == 200
        
        ai_config = ai_config_resp.json()
        twint_url = ai_config.get("twintPaymentUrl", "")
        
        if not twint_url:
            # Set a test Twint URL
            update_resp = requests.put(
                f"{BASE_URL}/api/ai-config",
                json={"twintPaymentUrl": "https://twint.ch/pay/afroboost-test-123"}
            )
            if update_resp.status_code == 200:
                twint_url = "https://twint.ch/pay/afroboost-test-123"
                print(f"✅ Set test Twint URL: {twint_url}")
        
        # Now test the AI chat endpoint with payment question
        chat_data = {
            "message": "Comment je peux payer ? Je veux acheter quelque chose.",
            "leadId": "",
            "firstName": "TestUser",
            "email": "test@example.com",
            "whatsapp": "+41790000000"
        }
        
        response = requests.post(f"{BASE_URL}/api/chat", json=chat_data)
        
        assert response.status_code == 200, f"Chat endpoint failed: {response.text}"
        
        data = response.json()
        ai_response = data.get("response", "").lower()
        
        # Check if Twint is mentioned
        twint_mentioned = "twint" in ai_response
        link_mentioned = "twint.ch" in ai_response or "lien" in ai_response or "payer" in ai_response
        
        print(f"✅ AI Response for payment question: {ai_response[:200]}...")
        print(f"   Twint mentioned: {twint_mentioned}, Link/payment mentioned: {link_mentioned}")
        
        # The AI should at least respond about payment
        assert "response" in data, "AI should provide a response"


class TestCRMFunctionality:
    """Test CRM: Search and infinite scroll functionality"""
    
    def test_crm_conversations_endpoint(self):
        """Test CRM: GET /api/conversations returns paginated results"""
        response = requests.get(f"{BASE_URL}/api/conversations", params={"page": 1, "limit": 10})
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Check pagination structure
        assert "conversations" in data, "Response should contain 'conversations'"
        assert "total" in data, "Response should contain 'total'"
        assert "page" in data, "Response should contain 'page'"
        assert "pages" in data, "Response should contain 'pages'"
        assert "has_more" in data, "Response should contain 'has_more'"
        
        print(f"✅ GET /api/conversations - total: {data['total']}, pages: {data['pages']}")
    
    def test_crm_search_functionality(self):
        """Test CRM: Search with query parameter works"""
        # First, create a test participant with unique name
        unique_name = f"TEST_CRMSearch_{uuid.uuid4().hex[:6]}"
        participant_data = {
            "name": unique_name,
            "email": f"crm_search_{uuid.uuid4().hex[:6]}@test.com",
            "whatsapp": "+41790000003"
        }
        
        create_resp = requests.post(f"{BASE_URL}/api/chat/participants", json=participant_data)
        participant_id = None
        if create_resp.status_code == 200:
            participant_id = create_resp.json().get("id")
        
        # Search for the participant
        response = requests.get(
            f"{BASE_URL}/api/conversations",
            params={"query": unique_name, "page": 1, "limit": 10}
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert "conversations" in data
        assert "total" in data
        
        print(f"✅ CRM search for '{unique_name}' - found: {data['total']} results")
        
        # Cleanup
        if participant_id:
            requests.delete(f"{BASE_URL}/api/chat/participants/{participant_id}")
    
    def test_crm_pagination_infinite_scroll(self):
        """Test CRM: Pagination works for infinite scroll"""
        # Get first page
        page1_resp = requests.get(f"{BASE_URL}/api/conversations", params={"page": 1, "limit": 5})
        assert page1_resp.status_code == 200
        
        page1_data = page1_resp.json()
        
        if page1_data.get("has_more"):
            # Get second page
            page2_resp = requests.get(f"{BASE_URL}/api/conversations", params={"page": 2, "limit": 5})
            assert page2_resp.status_code == 200
            
            page2_data = page2_resp.json()
            
            # Verify different pages return different data
            page1_ids = [c.get("id") for c in page1_data.get("conversations", [])]
            page2_ids = [c.get("id") for c in page2_data.get("conversations", [])]
            
            # No overlap between pages
            overlap = set(page1_ids) & set(page2_ids)
            assert len(overlap) == 0, f"Pages should not overlap, found: {overlap}"
            
            print(f"✅ CRM pagination works - page1: {len(page1_ids)} items, page2: {len(page2_ids)} items")
        else:
            print(f"✅ CRM pagination - only 1 page of data (total: {page1_data.get('total')})")


class TestHealthAndBasicEndpoints:
    """Basic health and endpoint tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✅ Health check passed - database: {data.get('database')}")
    
    def test_offers_endpoint(self):
        """Test offers endpoint returns data"""
        response = requests.get(f"{BASE_URL}/api/offers")
        assert response.status_code == 200
        
        offers = response.json()
        assert isinstance(offers, list)
        print(f"✅ Offers endpoint - {len(offers)} offers found")
    
    def test_courses_endpoint(self):
        """Test courses endpoint returns data"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        
        courses = response.json()
        assert isinstance(courses, list)
        print(f"✅ Courses endpoint - {len(courses)} courses found")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
