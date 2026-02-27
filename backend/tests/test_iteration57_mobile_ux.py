"""
Test Iteration 57 - Mobile UX & Skeleton Loading Features
Tests for:
1. Input chat: font-size 16px pour éviter zoom Safari iOS
2. Bouton Envoyer: min 44px pour accessibilité mobile
3. MessageSkeleton: Composant avec animation pulse créé
4. Cache Hybride: sessionStorage avec clé 'afroboost_last_msgs'
5. Skeleton affiché pendant isLoadingHistory
6. Fallback 'Lieu à confirmer': style gris (#999) et italique
7. Messages initialisés depuis le cache (getCachedMessages)
8. Messages sauvegardés dans le cache après chaque changement
"""

import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestIteration57BackendAPIs:
    """Backend API tests for Iteration 57"""
    
    def test_api_root_accessible(self):
        """TEST 1: API root endpoint accessible"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        print("✅ TEST 1 PASSED: API root endpoint accessible")
    
    def test_courses_endpoint(self):
        """TEST 2: Courses endpoint returns data"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ TEST 2 PASSED: Courses endpoint returns {len(data)} courses")
    
    def test_promo_code_basxx_validates(self):
        """TEST 3: Promo code 'basxx' validates correctly (requires specific email)"""
        # basxx is reserved for bassicustomshoes@gmail.com
        response = requests.post(f"{BASE_URL}/api/discount-codes/validate", json={
            "code": "basxx",
            "email": "bassicustomshoes@gmail.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("valid") == True
        print("✅ TEST 3 PASSED: Promo code 'basxx' validates correctly")
    
    def test_smart_entry_endpoint(self):
        """TEST 4: Smart-entry endpoint works"""
        response = requests.post(f"{BASE_URL}/api/chat/smart-entry", json={
            "name": "TestUser57",
            "email": "test57@example.com",
            "whatsapp": "+41791234567"
        })
        assert response.status_code == 200
        data = response.json()
        assert "participant" in data
        assert "session" in data
        print("✅ TEST 4 PASSED: Smart-entry endpoint works")


class TestIteration57FrontendCode:
    """Frontend code verification tests for Iteration 57"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Load frontend files for testing"""
        self.chatwidget_path = "/app/frontend/src/components/ChatWidget.js"
        self.skeleton_path = "/app/frontend/src/components/chat/MessageSkeleton.js"
        self.booking_path = "/app/frontend/src/components/chat/BookingPanel.js"
        
        with open(self.chatwidget_path, 'r') as f:
            self.chatwidget_content = f.read()
        with open(self.skeleton_path, 'r') as f:
            self.skeleton_content = f.read()
        with open(self.booking_path, 'r') as f:
            self.booking_content = f.read()
    
    def test_chat_input_font_size_16px(self):
        """TEST 5: Chat input has font-size 16px for Safari iOS zoom fix"""
        # Check for fontSize: '16px' in the input style
        assert "fontSize: '16px'" in self.chatwidget_content or 'fontSize: "16px"' in self.chatwidget_content
        # Verify it's in the chat input context
        assert "FIX ZOOM SAFARI iOS" in self.chatwidget_content
        print("✅ TEST 5 PASSED: Chat input has font-size 16px (Safari iOS zoom fix)")
    
    def test_send_button_44px(self):
        """TEST 6: Send button has min 44px for mobile accessibility"""
        # Check for width: '44px' and height: '44px'
        assert "width: '44px'" in self.chatwidget_content or 'width: "44px"' in self.chatwidget_content
        assert "height: '44px'" in self.chatwidget_content or 'height: "44px"' in self.chatwidget_content
        # Verify it's in the send button context
        assert "Min 44px pour accessibilité mobile" in self.chatwidget_content
        print("✅ TEST 6 PASSED: Send button has 44px for mobile accessibility")
    
    def test_message_skeleton_component_exists(self):
        """TEST 7: MessageSkeleton component exists with pulse animation"""
        # Check component import
        assert "import MessageSkeleton from './chat/MessageSkeleton'" in self.chatwidget_content
        # Check pulse animation in skeleton
        assert "skeletonPulse" in self.skeleton_content
        assert "@keyframes skeletonPulse" in self.skeleton_content
        print("✅ TEST 7 PASSED: MessageSkeleton component exists with pulse animation")
    
    def test_cache_hybrid_implementation(self):
        """TEST 8: Cache hybride with sessionStorage key 'afroboost_last_msgs'"""
        # Check cache key constant
        assert "MESSAGE_CACHE_KEY = 'afroboost_last_msgs'" in self.chatwidget_content
        # Check getCachedMessages function
        assert "getCachedMessages" in self.chatwidget_content
        # Check saveCachedMessages function
        assert "saveCachedMessages" in self.chatwidget_content
        # Check sessionStorage usage
        assert "sessionStorage.getItem(MESSAGE_CACHE_KEY)" in self.chatwidget_content
        assert "sessionStorage.setItem(MESSAGE_CACHE_KEY" in self.chatwidget_content
        print("✅ TEST 8 PASSED: Cache hybride with sessionStorage implemented")
    
    def test_skeleton_displayed_during_loading(self):
        """TEST 9: Skeleton displayed during isLoadingHistory"""
        # Check isLoadingHistory state
        assert "isLoadingHistory" in self.chatwidget_content
        # Check conditional rendering
        assert "isLoadingHistory && messages.length === 0" in self.chatwidget_content
        assert "<MessageSkeleton" in self.chatwidget_content
        print("✅ TEST 9 PASSED: Skeleton displayed during isLoadingHistory")
    
    def test_location_fallback_styling(self):
        """TEST 10: Fallback 'Lieu à confirmer' with gray (#999) and italic style"""
        # Check fallback text
        assert "Lieu à confirmer" in self.booking_content
        # Check gray color #999
        assert "#999" in self.booking_content
        # Check italic style
        assert "fontStyle:" in self.booking_content and "italic" in self.booking_content
        print("✅ TEST 10 PASSED: Fallback 'Lieu à confirmer' with gray/italic style")
    
    def test_messages_initialized_from_cache(self):
        """TEST 11: Messages initialized from cache (getCachedMessages)"""
        # Check useState initialization with getCachedMessages
        assert "useState(() => getCachedMessages())" in self.chatwidget_content
        print("✅ TEST 11 PASSED: Messages initialized from cache")
    
    def test_messages_saved_to_cache(self):
        """TEST 12: Messages saved to cache after each change"""
        # Check useEffect for saving messages
        assert "saveCachedMessages(messages)" in self.chatwidget_content
        print("✅ TEST 12 PASSED: Messages saved to cache after changes")
    
    def test_skeleton_data_testid(self):
        """TEST 13: MessageSkeleton has data-testid attribute"""
        assert 'data-testid="message-skeleton"' in self.skeleton_content
        print("✅ TEST 13 PASSED: MessageSkeleton has data-testid attribute")
    
    def test_booking_panel_location_display(self):
        """TEST 14: BookingPanel getLocationDisplay function"""
        # Check getLocationDisplay function
        assert "getLocationDisplay" in self.booking_content
        assert "course?.location || course?.locationName || 'Lieu à confirmer'" in self.booking_content
        print("✅ TEST 14 PASSED: BookingPanel getLocationDisplay function implemented")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
