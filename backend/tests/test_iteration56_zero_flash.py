"""
Test Iteration 56 - Zero-Flash & Synchronisation Horaire
=========================================================
Tests for:
1. Zero-Flash: Profile + ?group=ID → chat opens automatically (no form flash)
2. BookingPanel: French date formatting with Intl.DateTimeFormat (Europe/Paris)
3. BookingPanel: Fallback location ('Lieu à confirmer' if empty)
4. Chat container: overflow-anchor: none applied
5. CampaignManager: Close button (✕) with min 44px for mobile
6. CampaignManager: Modal max-height 80vh
7. Chat input: safe-area-inset-bottom and z-index 100
"""

import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestBackendAPIs:
    """Backend API tests for iteration 56"""
    
    def test_api_root_health(self):
        """Test API root endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        print("✅ TEST 1 - API root endpoint accessible")
    
    def test_courses_endpoint(self):
        """Test courses endpoint returns data"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ TEST 2 - Courses endpoint returns {len(data)} courses")
    
    def test_courses_have_location_field(self):
        """Test courses have location field for BookingPanel"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        courses = response.json()
        if len(courses) > 0:
            course = courses[0]
            # Should have location or locationName
            has_location = 'location' in course or 'locationName' in course
            assert has_location, "Course should have location or locationName field"
            print(f"✅ TEST 3 - Course has location field: {course.get('location') or course.get('locationName')}")
        else:
            print("⚠️ TEST 3 - No courses to test location field")
    
    def test_groups_join_endpoint_exists(self):
        """Test /api/groups/join endpoint exists for Zero-Flash"""
        response = requests.post(f"{BASE_URL}/api/groups/join", json={
            "group_id": "community",
            "email": "test@example.com",
            "name": "Test User"
        })
        # Should return 200 or 400 (validation error), not 404
        assert response.status_code != 404, "Groups join endpoint should exist"
        print(f"✅ TEST 4 - Groups join endpoint exists (status: {response.status_code})")
    
    def test_smart_entry_endpoint(self):
        """Test smart-entry endpoint for chat initialization"""
        response = requests.post(f"{BASE_URL}/api/chat/smart-entry", json={
            "name": "TestUser",
            "email": "test@example.com",
            "whatsapp": "+41791234567"
        })
        assert response.status_code in [200, 201]
        data = response.json()
        # API returns participant object with id
        assert 'participant' in data or 'session_id' in data or 'id' in data
        if 'participant' in data:
            assert 'id' in data['participant'], "Participant should have id"
        print("✅ TEST 5 - Smart-entry endpoint works")
    
    def test_promo_code_validation(self):
        """Test promo code validation for subscriber profile"""
        response = requests.post(f"{BASE_URL}/api/discount-codes/validate", json={
            "code": "basxx",
            "email": "bassicustomshoes@gmail.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get('valid') == True
        print("✅ TEST 6 - Promo code 'basxx' validates correctly")
    
    def test_active_conversations_endpoint(self):
        """Test active conversations endpoint for CampaignManager"""
        response = requests.get(f"{BASE_URL}/api/conversations/active")
        assert response.status_code == 200
        data = response.json()
        assert 'success' in data or 'conversations' in data or isinstance(data, list)
        print("✅ TEST 7 - Active conversations endpoint works")


class TestFrontendCodeReview:
    """Code review tests for frontend implementation"""
    
    def test_chatwidget_zero_flash_implementation(self):
        """Verify Zero-Flash implementation in ChatWidget.js"""
        with open('/app/frontend/src/components/ChatWidget.js', 'r') as f:
            content = f.read()
        
        # Check pendingGroupJoin useState with URL detection BEFORE first render
        assert 'pendingGroupJoin' in content, "Should have pendingGroupJoin state"
        assert "urlParams.get('group')" in content, "Should detect ?group=ID parameter"
        assert 'getInitialStep' in content, "Should have getInitialStep function"
        assert 'getInitialOpen' in content, "Should have getInitialOpen function"
        
        # Verify Zero-Flash logic: profile + groupId → direct chat
        assert 'profile && groupId' in content, "Should check profile AND groupId for Zero-Flash"
        print("✅ TEST 8 - ChatWidget Zero-Flash implementation verified")
    
    def test_chatwidget_overflow_anchor(self):
        """Verify overflow-anchor: none in ChatWidget.js"""
        with open('/app/frontend/src/components/ChatWidget.js', 'r') as f:
            content = f.read()
        
        assert "overflowAnchor: 'none'" in content, "Should have overflow-anchor: none"
        print("✅ TEST 9 - ChatWidget overflow-anchor: none verified")
    
    def test_chatwidget_safe_area_inset(self):
        """Verify safe-area-inset-bottom in ChatWidget.js"""
        with open('/app/frontend/src/components/ChatWidget.js', 'r') as f:
            content = f.read()
        
        assert 'safe-area-inset-bottom' in content, "Should have safe-area-inset-bottom"
        assert 'zIndex: 100' in content, "Should have z-index 100 for input"
        print("✅ TEST 10 - ChatWidget safe-area-inset-bottom and z-index 100 verified")
    
    def test_bookingpanel_french_date_formatting(self):
        """Verify French date formatting in BookingPanel.js"""
        with open('/app/frontend/src/components/chat/BookingPanel.js', 'r') as f:
            content = f.read()
        
        # Check Intl.DateTimeFormat with fr-FR locale
        assert "Intl.DateTimeFormat('fr-FR'" in content, "Should use Intl.DateTimeFormat with fr-FR"
        assert "timeZone: 'Europe/Paris'" in content, "Should use Europe/Paris timezone"
        assert "weekday: 'long'" in content, "Should format weekday in long format"
        print("✅ TEST 11 - BookingPanel French date formatting verified")
    
    def test_bookingpanel_location_fallback(self):
        """Verify location fallback in BookingPanel.js"""
        with open('/app/frontend/src/components/chat/BookingPanel.js', 'r') as f:
            content = f.read()
        
        assert 'getLocationDisplay' in content, "Should have getLocationDisplay function"
        assert "Lieu à confirmer" in content, "Should have fallback 'Lieu à confirmer'"
        print("✅ TEST 12 - BookingPanel location fallback verified")
    
    def test_campaignmanager_close_button_44px(self):
        """Verify close button min 44px in CampaignManager.js"""
        with open('/app/frontend/src/components/coach/CampaignManager.js', 'r') as f:
            content = f.read()
        
        assert "minWidth: '44px'" in content, "Should have minWidth 44px"
        assert "minHeight: '44px'" in content, "Should have minHeight 44px"
        assert 'close-recipient-dropdown' in content, "Should have close button data-testid"
        print("✅ TEST 13 - CampaignManager close button 44px verified")
    
    def test_campaignmanager_modal_max_height(self):
        """Verify modal max-height 80vh in CampaignManager.js"""
        with open('/app/frontend/src/components/coach/CampaignManager.js', 'r') as f:
            content = f.read()
        
        assert "maxHeight: '80vh'" in content, "Should have maxHeight 80vh"
        print("✅ TEST 14 - CampaignManager modal max-height 80vh verified")


class TestZeroFlashLogic:
    """Detailed tests for Zero-Flash logic"""
    
    def test_zero_flash_detection_before_render(self):
        """Verify ?group=ID is detected BEFORE first render"""
        with open('/app/frontend/src/components/ChatWidget.js', 'r') as f:
            content = f.read()
        
        # The useState initializer should detect group parameter
        # Look for useState(() => { ... urlParams.get('group') ... })
        pattern = r"useState\(\(\)\s*=>\s*\{[^}]*urlParams\.get\('group'\)"
        match = re.search(pattern, content, re.DOTALL)
        assert match, "Should detect ?group=ID in useState initializer (before first render)"
        print("✅ TEST 15 - Zero-Flash detection before first render verified")
    
    def test_zero_flash_direct_chat_step(self):
        """Verify profile + groupId → step='chat' (no form)"""
        with open('/app/frontend/src/components/ChatWidget.js', 'r') as f:
            content = f.read()
        
        # Check getInitialStep returns 'chat' when profile && groupId
        assert "if (profile && groupId)" in content, "Should check profile && groupId"
        assert "return 'chat'" in content, "Should return 'chat' for Zero-Flash"
        print("✅ TEST 16 - Zero-Flash direct chat step verified")
    
    def test_zero_flash_auto_open(self):
        """Verify chat opens automatically with profile + groupId"""
        with open('/app/frontend/src/components/ChatWidget.js', 'r') as f:
            content = f.read()
        
        # Check getInitialOpen returns true when groupId && profile
        assert "getInitialOpen" in content, "Should have getInitialOpen function"
        assert "groupId && profile" in content, "Should check groupId && profile"
        print("✅ TEST 17 - Zero-Flash auto-open verified")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
