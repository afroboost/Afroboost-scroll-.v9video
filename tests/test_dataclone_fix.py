"""
Test suite for DataCloneError fix verification
Tests the fixes for PostHog DataCloneError that was blocking EmailJS and WhatsApp sending

Features tested:
1. PostHog configuration has capture_performance: false
2. Event handlers have e.preventDefault() and e.stopPropagation()
3. EmailJS service uses flat JSON payload
4. WhatsApp config API works correctly
5. Campaigns API works correctly
"""

import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestBackendAPIs:
    """Test backend APIs for campaigns and WhatsApp config"""
    
    def test_health_check(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Health check passed")
    
    def test_whatsapp_config_get(self):
        """Test WhatsApp config GET endpoint"""
        response = requests.get(f"{BASE_URL}/api/whatsapp-config")
        assert response.status_code == 200
        data = response.json()
        assert "accountSid" in data
        assert "authToken" in data
        assert "fromNumber" in data
        assert "apiMode" in data
        print(f"✅ WhatsApp config GET works - apiMode: {data.get('apiMode')}")
    
    def test_whatsapp_config_put(self):
        """Test WhatsApp config PUT endpoint"""
        # Get current config
        get_response = requests.get(f"{BASE_URL}/api/whatsapp-config")
        current_config = get_response.json()
        
        # Update with same values (to not break anything)
        response = requests.put(
            f"{BASE_URL}/api/whatsapp-config",
            json=current_config,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        print("✅ WhatsApp config PUT works")
    
    def test_campaigns_get(self):
        """Test campaigns GET endpoint"""
        response = requests.get(f"{BASE_URL}/api/campaigns")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Campaigns GET works - {len(data)} campaigns found")
    
    def test_campaigns_structure(self):
        """Test campaign data structure"""
        response = requests.get(f"{BASE_URL}/api/campaigns")
        assert response.status_code == 200
        data = response.json()
        
        if len(data) > 0:
            campaign = data[0]
            required_fields = ["id", "name", "message", "channels", "status"]
            for field in required_fields:
                assert field in campaign, f"Missing field: {field}"
            print(f"✅ Campaign structure valid - first campaign: {campaign.get('name')}")
        else:
            print("⚠️ No campaigns to test structure")


class TestCodeImplementation:
    """Test code implementation by reading source files"""
    
    def test_posthog_capture_performance_disabled(self):
        """Verify PostHog has capture_performance: false"""
        with open("/app/frontend/public/index.html", "r") as f:
            content = f.read()
        
        assert "capture_performance: false" in content, "PostHog capture_performance should be false"
        assert "disable_session_recording: true" in content, "PostHog session recording should be disabled"
        assert "autocapture: false" in content, "PostHog autocapture should be disabled"
        print("✅ PostHog configuration has DataCloneError fixes")
    
    def test_emailjs_handler_has_prevent_default(self):
        """Verify handleTestEmailJS has e.preventDefault()"""
        with open("/app/frontend/src/components/CoachDashboard.js", "r") as f:
            content = f.read()
        
        # Find handleTestEmailJS function
        pattern = r"const handleTestEmailJS = async \(e\) => \{[^}]*e\.preventDefault\(\)[^}]*e\.stopPropagation\(\)"
        match = re.search(pattern, content, re.DOTALL)
        assert match is not None, "handleTestEmailJS should have e.preventDefault() and e.stopPropagation()"
        print("✅ handleTestEmailJS has e.preventDefault() and e.stopPropagation()")
    
    def test_whatsapp_handler_has_prevent_default(self):
        """Verify handleTestWhatsApp has e.preventDefault()"""
        with open("/app/frontend/src/components/CoachDashboard.js", "r") as f:
            content = f.read()
        
        # Find handleTestWhatsApp function
        pattern = r"const handleTestWhatsApp = async \(e\) => \{[^}]*e\.preventDefault\(\)[^}]*e\.stopPropagation\(\)"
        match = re.search(pattern, content, re.DOTALL)
        assert match is not None, "handleTestWhatsApp should have e.preventDefault() and e.stopPropagation()"
        print("✅ handleTestWhatsApp has e.preventDefault() and e.stopPropagation()")
    
    def test_emailjs_service_flat_payload(self):
        """Verify EmailJS service uses flat JSON payload"""
        with open("/app/frontend/src/services/emailService.js", "r") as f:
            content = f.read()
        
        # Check for flat payload structure
        assert "String(params.to_email" in content or "to_email: String(" in content, \
            "EmailJS should use String() for flat payload"
        assert "templateParams = {" in content, "EmailJS should create templateParams object"
        print("✅ EmailJS service uses flat JSON payload")
    
    def test_emailjs_default_config(self):
        """Verify EmailJS has correct default IDs"""
        with open("/app/frontend/src/services/emailService.js", "r") as f:
            content = f.read()
        
        assert "service_8mrmxim" in content, "EmailJS should have correct service ID"
        assert "template_3n1u86p" in content, "EmailJS should have correct template ID"
        assert "5LfgQSIEQoqq_XSqt" in content, "EmailJS should have correct public key"
        print("✅ EmailJS has correct default configuration IDs")
    
    def test_whatsapp_save_is_async(self):
        """Verify handleSaveWhatsAppConfig is async"""
        with open("/app/frontend/src/components/CoachDashboard.js", "r") as f:
            content = f.read()
        
        # Check that handleSaveWhatsAppConfig is async
        assert "const handleSaveWhatsAppConfig = async" in content, \
            "handleSaveWhatsAppConfig should be async"
        print("✅ handleSaveWhatsAppConfig is async")
    
    def test_campaigns_tab_exists(self):
        """Verify Campaigns tab exists in CoachDashboard"""
        with open("/app/frontend/src/components/CoachDashboard.js", "r") as f:
            content = f.read()
        
        assert '"campaigns"' in content, "Campaigns tab ID should exist"
        assert "📢 Campagnes" in content, "Campaigns tab label should exist"
        print("✅ Campaigns tab exists in CoachDashboard")
    
    def test_test_buttons_have_type_button(self):
        """Verify test buttons have type='button' to prevent form submission"""
        with open("/app/frontend/src/components/CoachDashboard.js", "r") as f:
            content = f.read()
        
        # Check for type="button" on test buttons
        assert 'type="button"' in content, "Test buttons should have type='button'"
        print("✅ Test buttons have type='button'")
    
    def test_data_testids_exist(self):
        """Verify data-testid attributes exist for test buttons"""
        with open("/app/frontend/src/components/CoachDashboard.js", "r") as f:
            content = f.read()
        
        assert 'data-testid="test-email-btn"' in content, "EmailJS test button should have data-testid"
        assert 'data-testid="test-whatsapp-btn"' in content, "WhatsApp test button should have data-testid"
        assert 'data-testid="test-email-input"' in content, "Email test input should have data-testid"
        print("✅ data-testid attributes exist for test elements")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
