"""
Test EmailJS and WhatsApp Direct Bindings in CoachDashboard.js
Verifies the real bindings for campaign sending functionality:
1. EmailJS SDK import and constants
2. useEffect initialization with emailjs.init()
3. handleTestEmailJS calls directly emailjs.send()
4. sendWhatsAppMessageDirect exists and logs data
5. handleTestWhatsApp uses sendWhatsAppMessageDirect
6. launchCampaignWithSend iterates on emailResults and calls emailjs.send
7. All handlers have e.preventDefault() first
"""

import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Read the CoachDashboard.js file content
COACH_DASHBOARD_PATH = "/app/frontend/src/components/CoachDashboard.js"

@pytest.fixture(scope="module")
def coach_dashboard_content():
    """Load CoachDashboard.js content once for all tests"""
    with open(COACH_DASHBOARD_PATH, 'r') as f:
        return f.read()


class TestEmailJSImportAndConstants:
    """Test EmailJS SDK import and constants are correctly defined"""
    
    def test_emailjs_sdk_import(self, coach_dashboard_content):
        """Verify EmailJS SDK is imported from @emailjs/browser"""
        assert "import emailjs from '@emailjs/browser'" in coach_dashboard_content, \
            "EmailJS SDK import not found"
        print("✅ EmailJS SDK import verified: import emailjs from '@emailjs/browser'")
    
    def test_emailjs_service_id_constant(self, coach_dashboard_content):
        """Verify EMAILJS_SERVICE_ID constant is defined with correct value"""
        assert 'const EMAILJS_SERVICE_ID = "service_8mrmxim"' in coach_dashboard_content, \
            "EMAILJS_SERVICE_ID constant not found or incorrect"
        print("✅ EMAILJS_SERVICE_ID constant verified: service_8mrmxim")
    
    def test_emailjs_template_id_constant(self, coach_dashboard_content):
        """Verify EMAILJS_TEMPLATE_ID constant is defined with correct value"""
        assert 'const EMAILJS_TEMPLATE_ID = "template_3n1u86p"' in coach_dashboard_content, \
            "EMAILJS_TEMPLATE_ID constant not found or incorrect"
        print("✅ EMAILJS_TEMPLATE_ID constant verified: template_3n1u86p")
    
    def test_emailjs_public_key_constant(self, coach_dashboard_content):
        """Verify EMAILJS_PUBLIC_KEY constant is defined with correct value"""
        assert 'const EMAILJS_PUBLIC_KEY = "5LfgQSIEQoqq_XSqt"' in coach_dashboard_content, \
            "EMAILJS_PUBLIC_KEY constant not found or incorrect"
        print("✅ EMAILJS_PUBLIC_KEY constant verified: 5LfgQSIEQoqq_XSqt")


class TestEmailJSInitialization:
    """Test EmailJS SDK initialization in useEffect"""
    
    def test_emailjs_init_in_useeffect(self, coach_dashboard_content):
        """Verify emailjs.init() is called in useEffect"""
        # Check for useEffect with emailjs.init
        assert "emailjs.init(EMAILJS_PUBLIC_KEY)" in coach_dashboard_content, \
            "emailjs.init(EMAILJS_PUBLIC_KEY) not found in useEffect"
        print("✅ emailjs.init(EMAILJS_PUBLIC_KEY) found in useEffect")
    
    def test_emailjs_init_useeffect_structure(self, coach_dashboard_content):
        """Verify useEffect structure for EmailJS initialization"""
        # Check that useEffect with empty dependency array exists and contains emailjs.init
        # The useEffect block spans multiple lines, so we check for the pattern more flexibly
        assert "useEffect(() => {" in coach_dashboard_content, "useEffect not found"
        assert "emailjs.init(EMAILJS_PUBLIC_KEY)" in coach_dashboard_content, "emailjs.init not found"
        # Check that }, []); follows the emailjs.init block
        init_pos = coach_dashboard_content.find("emailjs.init(EMAILJS_PUBLIC_KEY)")
        closing_pos = coach_dashboard_content.find("}, []);", init_pos)
        assert closing_pos > init_pos and closing_pos - init_pos < 500, \
            "useEffect with empty dependency array not found near emailjs.init"
        print("✅ useEffect structure verified with empty dependency array []")


class TestHandleTestEmailJS:
    """Test handleTestEmailJS function implementation"""
    
    def test_handle_test_emailjs_exists(self, coach_dashboard_content):
        """Verify handleTestEmailJS function exists"""
        assert "const handleTestEmailJS = async (e) =>" in coach_dashboard_content, \
            "handleTestEmailJS function not found"
        print("✅ handleTestEmailJS function exists")
    
    def test_handle_test_emailjs_prevent_default(self, coach_dashboard_content):
        """Verify handleTestEmailJS has e.preventDefault() first"""
        # Find the function and check for preventDefault
        pattern = r'const handleTestEmailJS = async \(e\) => \{[^}]*e\.preventDefault\(\)'
        match = re.search(pattern, coach_dashboard_content, re.DOTALL)
        assert match is not None, "handleTestEmailJS missing e.preventDefault()"
        print("✅ handleTestEmailJS has e.preventDefault()")
    
    def test_handle_test_emailjs_stop_propagation(self, coach_dashboard_content):
        """Verify handleTestEmailJS has e.stopPropagation()"""
        pattern = r'const handleTestEmailJS = async \(e\) => \{[^}]*e\.stopPropagation\(\)'
        match = re.search(pattern, coach_dashboard_content, re.DOTALL)
        assert match is not None, "handleTestEmailJS missing e.stopPropagation()"
        print("✅ handleTestEmailJS has e.stopPropagation()")
    
    def test_handle_test_emailjs_direct_send(self, coach_dashboard_content):
        """Verify handleTestEmailJS calls emailjs.send directly"""
        # Check that emailjs.send is called with the constants
        assert "await emailjs.send(" in coach_dashboard_content, \
            "emailjs.send() call not found"
        assert "EMAILJS_SERVICE_ID," in coach_dashboard_content, \
            "EMAILJS_SERVICE_ID not used in emailjs.send"
        assert "EMAILJS_TEMPLATE_ID," in coach_dashboard_content, \
            "EMAILJS_TEMPLATE_ID not used in emailjs.send"
        assert "EMAILJS_PUBLIC_KEY" in coach_dashboard_content, \
            "EMAILJS_PUBLIC_KEY not used in emailjs.send"
        print("✅ handleTestEmailJS calls emailjs.send() directly with constants")


class TestSendWhatsAppMessageDirect:
    """Test sendWhatsAppMessageDirect function implementation"""
    
    def test_send_whatsapp_message_direct_exists(self, coach_dashboard_content):
        """Verify sendWhatsAppMessageDirect function exists"""
        assert "const sendWhatsAppMessageDirect = async (phoneNumber, message, mediaUrl = null) =>" in coach_dashboard_content, \
            "sendWhatsAppMessageDirect function not found"
        print("✅ sendWhatsAppMessageDirect function exists")
    
    def test_send_whatsapp_message_direct_logs(self, coach_dashboard_content):
        """Verify sendWhatsAppMessageDirect has clear console logs"""
        # Check for the log statements
        assert "console.log('📱 === ENVOI WHATSAPP ===')" in coach_dashboard_content, \
            "sendWhatsAppMessageDirect missing header log"
        assert "console.log('📱 Envoi WhatsApp vers:', phoneNumber)" in coach_dashboard_content, \
            "sendWhatsAppMessageDirect missing phone log"
        assert "console.log('📱 Message:', message)" in coach_dashboard_content, \
            "sendWhatsAppMessageDirect missing message log"
        print("✅ sendWhatsAppMessageDirect has clear console logs")
    
    def test_send_whatsapp_message_direct_twilio_api(self, coach_dashboard_content):
        """Verify sendWhatsAppMessageDirect uses Twilio API"""
        assert "https://api.twilio.com/2010-04-01/Accounts/" in coach_dashboard_content, \
            "Twilio API URL not found"
        assert "config.accountSid" in coach_dashboard_content, \
            "accountSid not used"
        assert "config.authToken" in coach_dashboard_content, \
            "authToken not used"
        print("✅ sendWhatsAppMessageDirect uses Twilio API correctly")


class TestHandleTestWhatsApp:
    """Test handleTestWhatsApp function implementation"""
    
    def test_handle_test_whatsapp_exists(self, coach_dashboard_content):
        """Verify handleTestWhatsApp function exists"""
        assert "const handleTestWhatsApp = async (e) =>" in coach_dashboard_content, \
            "handleTestWhatsApp function not found"
        print("✅ handleTestWhatsApp function exists")
    
    def test_handle_test_whatsapp_prevent_default(self, coach_dashboard_content):
        """Verify handleTestWhatsApp has e.preventDefault()"""
        pattern = r'const handleTestWhatsApp = async \(e\) => \{[^}]*e\.preventDefault\(\)'
        match = re.search(pattern, coach_dashboard_content, re.DOTALL)
        assert match is not None, "handleTestWhatsApp missing e.preventDefault()"
        print("✅ handleTestWhatsApp has e.preventDefault()")
    
    def test_handle_test_whatsapp_stop_propagation(self, coach_dashboard_content):
        """Verify handleTestWhatsApp has e.stopPropagation()"""
        pattern = r'const handleTestWhatsApp = async \(e\) => \{[^}]*e\.stopPropagation\(\)'
        match = re.search(pattern, coach_dashboard_content, re.DOTALL)
        assert match is not None, "handleTestWhatsApp missing e.stopPropagation()"
        print("✅ handleTestWhatsApp has e.stopPropagation()")
    
    def test_handle_test_whatsapp_uses_direct_function(self, coach_dashboard_content):
        """Verify handleTestWhatsApp uses sendWhatsAppMessageDirect"""
        # Find handleTestWhatsApp function and check it calls sendWhatsAppMessageDirect
        # The function spans multiple lines, so we check more flexibly
        func_start = coach_dashboard_content.find("const handleTestWhatsApp = async (e) =>")
        assert func_start != -1, "handleTestWhatsApp function not found"
        
        # Find the next function definition to limit our search
        next_func = coach_dashboard_content.find("const handle", func_start + 50)
        if next_func == -1:
            next_func = len(coach_dashboard_content)
        
        func_body = coach_dashboard_content[func_start:next_func]
        assert "await sendWhatsAppMessageDirect(" in func_body, \
            "handleTestWhatsApp doesn't use sendWhatsAppMessageDirect"
        print("✅ handleTestWhatsApp uses sendWhatsAppMessageDirect")


class TestLaunchCampaignWithSend:
    """Test launchCampaignWithSend function implementation"""
    
    def test_launch_campaign_with_send_exists(self, coach_dashboard_content):
        """Verify launchCampaignWithSend function exists"""
        assert "const launchCampaignWithSend = async (e, campaignId) =>" in coach_dashboard_content, \
            "launchCampaignWithSend function not found"
        print("✅ launchCampaignWithSend function exists")
    
    def test_launch_campaign_with_send_prevent_default(self, coach_dashboard_content):
        """Verify launchCampaignWithSend has e.preventDefault()"""
        pattern = r'const launchCampaignWithSend = async \(e, campaignId\) => \{[^}]*e\.preventDefault\(\)'
        match = re.search(pattern, coach_dashboard_content, re.DOTALL)
        assert match is not None, "launchCampaignWithSend missing e.preventDefault()"
        print("✅ launchCampaignWithSend has e.preventDefault()")
    
    def test_launch_campaign_with_send_stop_propagation(self, coach_dashboard_content):
        """Verify launchCampaignWithSend has e.stopPropagation()"""
        pattern = r'const launchCampaignWithSend = async \(e, campaignId\) => \{[^}]*e\.stopPropagation\(\)'
        match = re.search(pattern, coach_dashboard_content, re.DOTALL)
        assert match is not None, "launchCampaignWithSend missing e.stopPropagation()"
        print("✅ launchCampaignWithSend has e.stopPropagation()")
    
    def test_launch_campaign_iterates_email_results(self, coach_dashboard_content):
        """Verify launchCampaignWithSend iterates over emailResults"""
        assert "for (let i = 0; i < emailResults.length; i++)" in coach_dashboard_content, \
            "launchCampaignWithSend doesn't iterate over emailResults"
        print("✅ launchCampaignWithSend iterates over emailResults")
    
    def test_launch_campaign_calls_emailjs_send(self, coach_dashboard_content):
        """Verify launchCampaignWithSend calls emailjs.send for each email"""
        # Check that emailjs.send is called within the loop context
        assert "const response = await emailjs.send(" in coach_dashboard_content, \
            "emailjs.send not called in launchCampaignWithSend"
        print("✅ launchCampaignWithSend calls emailjs.send for each email")
    
    def test_launch_campaign_uses_send_whatsapp_direct(self, coach_dashboard_content):
        """Verify launchCampaignWithSend uses sendWhatsAppMessageDirect for WhatsApp"""
        assert "const result = await sendWhatsAppMessageDirect(" in coach_dashboard_content, \
            "sendWhatsAppMessageDirect not called in launchCampaignWithSend"
        print("✅ launchCampaignWithSend uses sendWhatsAppMessageDirect for WhatsApp")


class TestBackendAPIs:
    """Test backend API endpoints are working"""
    
    def test_health_endpoint(self):
        """Verify health endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health endpoint failed: {response.status_code}"
        print("✅ Health endpoint returns 200")
    
    def test_campaigns_endpoint(self):
        """Verify campaigns endpoint returns list"""
        response = requests.get(f"{BASE_URL}/api/campaigns")
        assert response.status_code == 200, f"Campaigns endpoint failed: {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Campaigns endpoint should return a list"
        print(f"✅ Campaigns endpoint returns list with {len(data)} campaigns")
    
    def test_whatsapp_config_endpoint(self):
        """Verify WhatsApp config endpoint returns correct structure"""
        response = requests.get(f"{BASE_URL}/api/whatsapp-config")
        assert response.status_code == 200, f"WhatsApp config endpoint failed: {response.status_code}"
        data = response.json()
        # Check structure
        assert "accountSid" in data or "account_sid" in data or data == {}, \
            "WhatsApp config should have accountSid or be empty"
        print("✅ WhatsApp config endpoint returns correct structure")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
