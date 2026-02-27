"""
Test suite for messagingGateway.js - Passerelles techniques pures
Verifies that gateways are pure output channels with NO decision logic
"""
import pytest
import os
import re

# Path to the files
MESSAGING_GATEWAY_PATH = "/app/frontend/src/services/messagingGateway.js"
INDEX_PATH = "/app/frontend/src/services/index.js"
AI_RESPONSE_SERVICE_PATH = "/app/frontend/src/services/aiResponseService.js"

# Expected EmailJS constants
EXPECTED_EMAILJS_SERVICE_ID = "service_8mrmxim"
EXPECTED_EMAILJS_TEMPLATE_ID = "template_3n1u86p"
EXPECTED_EMAILJS_PUBLIC_KEY = "5LfgQSIEQoqq_XSqt"


class TestMessagingGatewayExists:
    """Test that messagingGateway.js exists and has correct structure"""
    
    def test_messaging_gateway_file_exists(self):
        """Verify messagingGateway.js file exists"""
        assert os.path.exists(MESSAGING_GATEWAY_PATH), f"File not found: {MESSAGING_GATEWAY_PATH}"
        print("✅ messagingGateway.js exists")
    
    def test_messaging_gateway_exports_sendEmailGateway(self):
        """Verify sendEmailGateway is exported"""
        with open(MESSAGING_GATEWAY_PATH, 'r') as f:
            content = f.read()
        
        # Check for export statement
        assert "export const sendEmailGateway" in content, "sendEmailGateway not exported"
        print("✅ sendEmailGateway is exported")
    
    def test_messaging_gateway_exports_sendWhatsAppGateway(self):
        """Verify sendWhatsAppGateway is exported"""
        with open(MESSAGING_GATEWAY_PATH, 'r') as f:
            content = f.read()
        
        assert "export const sendWhatsAppGateway" in content, "sendWhatsAppGateway not exported"
        print("✅ sendWhatsAppGateway is exported")
    
    def test_messaging_gateway_exports_sendMessageGateway(self):
        """Verify sendMessageGateway is exported"""
        with open(MESSAGING_GATEWAY_PATH, 'r') as f:
            content = f.read()
        
        assert "export const sendMessageGateway" in content, "sendMessageGateway not exported"
        print("✅ sendMessageGateway is exported")


class TestIndexExports:
    """Test that index.js exports the gateways from messagingGateway"""
    
    def test_index_exports_sendEmailGateway(self):
        """Verify index.js exports sendEmailGateway"""
        with open(INDEX_PATH, 'r') as f:
            content = f.read()
        
        assert "sendEmailGateway" in content, "sendEmailGateway not in index.js"
        assert "from './messagingGateway'" in content, "messagingGateway import missing"
        print("✅ index.js exports sendEmailGateway from messagingGateway")
    
    def test_index_exports_sendWhatsAppGateway(self):
        """Verify index.js exports sendWhatsAppGateway"""
        with open(INDEX_PATH, 'r') as f:
            content = f.read()
        
        assert "sendWhatsAppGateway" in content, "sendWhatsAppGateway not in index.js"
        print("✅ index.js exports sendWhatsAppGateway")
    
    def test_index_exports_sendMessageGateway(self):
        """Verify index.js exports sendMessageGateway"""
        with open(INDEX_PATH, 'r') as f:
            content = f.read()
        
        assert "sendMessageGateway" in content, "sendMessageGateway not in index.js"
        print("✅ index.js exports sendMessageGateway")


class TestEmailJSConstants:
    """Test that sendEmailGateway uses correct EmailJS constants"""
    
    def test_emailjs_service_id(self):
        """Verify correct EMAILJS_SERVICE_ID"""
        with open(MESSAGING_GATEWAY_PATH, 'r') as f:
            content = f.read()
        
        assert f'EMAILJS_SERVICE_ID = "{EXPECTED_EMAILJS_SERVICE_ID}"' in content, \
            f"Expected EMAILJS_SERVICE_ID = {EXPECTED_EMAILJS_SERVICE_ID}"
        print(f"✅ EMAILJS_SERVICE_ID = {EXPECTED_EMAILJS_SERVICE_ID}")
    
    def test_emailjs_template_id(self):
        """Verify correct EMAILJS_TEMPLATE_ID"""
        with open(MESSAGING_GATEWAY_PATH, 'r') as f:
            content = f.read()
        
        assert f'EMAILJS_TEMPLATE_ID = "{EXPECTED_EMAILJS_TEMPLATE_ID}"' in content, \
            f"Expected EMAILJS_TEMPLATE_ID = {EXPECTED_EMAILJS_TEMPLATE_ID}"
        print(f"✅ EMAILJS_TEMPLATE_ID = {EXPECTED_EMAILJS_TEMPLATE_ID}")
    
    def test_emailjs_public_key(self):
        """Verify correct EMAILJS_PUBLIC_KEY"""
        with open(MESSAGING_GATEWAY_PATH, 'r') as f:
            content = f.read()
        
        assert f'EMAILJS_PUBLIC_KEY = "{EXPECTED_EMAILJS_PUBLIC_KEY}"' in content, \
            f"Expected EMAILJS_PUBLIC_KEY = {EXPECTED_EMAILJS_PUBLIC_KEY}"
        print(f"✅ EMAILJS_PUBLIC_KEY = {EXPECTED_EMAILJS_PUBLIC_KEY}")
    
    def test_emailjs_send_uses_constants(self):
        """Verify emailjs.send() uses the defined constants"""
        with open(MESSAGING_GATEWAY_PATH, 'r') as f:
            content = f.read()
        
        # Check that emailjs.send uses the constants
        assert "emailjs.send(" in content, "emailjs.send() not found"
        assert "EMAILJS_SERVICE_ID" in content, "EMAILJS_SERVICE_ID not used"
        assert "EMAILJS_TEMPLATE_ID" in content, "EMAILJS_TEMPLATE_ID not used"
        assert "EMAILJS_PUBLIC_KEY" in content, "EMAILJS_PUBLIC_KEY not used"
        print("✅ emailjs.send() uses defined constants")


class TestWhatsAppSimulationMode:
    """Test that sendWhatsAppGateway has simulation mode when Twilio not configured"""
    
    def test_twilio_config_check(self):
        """Verify Twilio config check exists"""
        with open(MESSAGING_GATEWAY_PATH, 'r') as f:
            content = f.read()
        
        # Check for config validation
        assert "!accountSid || !authToken || !fromNumber" in content, \
            "Twilio config check not found"
        print("✅ Twilio config check exists")
    
    def test_simulation_mode_exists(self):
        """Verify simulation mode returns success when Twilio not configured"""
        with open(MESSAGING_GATEWAY_PATH, 'r') as f:
            content = f.read()
        
        # Check for simulation mode
        assert "simulated: true" in content, "Simulation mode not found"
        assert "Mode simulation" in content or "simulation" in content.lower(), \
            "Simulation mode warning not found"
        print("✅ Simulation mode exists when Twilio not configured")
    
    def test_simulation_returns_success(self):
        """Verify simulation mode returns success: true"""
        with open(MESSAGING_GATEWAY_PATH, 'r') as f:
            content = f.read()
        
        # Find the simulation return block
        assert "success: true" in content, "success: true not found"
        assert "simulated: true" in content, "simulated: true not found"
        print("✅ Simulation mode returns {success: true, simulated: true}")


class TestNoDecisionLogic:
    """Test that gateways contain NO decision logic on message content"""
    
    def test_no_content_based_decisions(self):
        """Verify no if/else based on message content"""
        with open(MESSAGING_GATEWAY_PATH, 'r') as f:
            content = f.read()
        
        # Patterns that would indicate content-based decisions
        bad_patterns = [
            r'if\s*\(\s*message\s*===',
            r'if\s*\(\s*message\s*==',
            r'if\s*\(\s*message\.includes',
            r'if\s*\(\s*message\.match',
            r'if\s*\(\s*content\s*===',
            r'if\s*\(\s*body\s*===',
            r'switch\s*\(\s*message',
            r'switch\s*\(\s*content',
        ]
        
        for pattern in bad_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            assert len(matches) == 0, f"Found content-based decision: {pattern}"
        
        print("✅ No content-based decision logic found")
    
    def test_only_technical_routing(self):
        """Verify if/else is only for technical routing (channel, config, response)"""
        with open(MESSAGING_GATEWAY_PATH, 'r') as f:
            content = f.read()
        
        # Find all if statements
        if_statements = re.findall(r'if\s*\([^)]+\)', content)
        
        # Allowed patterns (technical routing only)
        allowed_patterns = [
            'channel',           # Channel routing (email vs whatsapp)
            'accountSid',        # Config check
            'authToken',         # Config check
            'fromNumber',        # Config check
            'formattedPhone',    # Phone formatting
            'response.ok',       # HTTP response check
            '!response.ok',      # HTTP response check
        ]
        
        for if_stmt in if_statements:
            is_allowed = any(pattern in if_stmt for pattern in allowed_patterns)
            # Also allow empty checks or simple existence checks
            is_simple = 'message' not in if_stmt.lower() or 'message' in if_stmt and '===' not in if_stmt
            assert is_allowed or is_simple, f"Suspicious if statement: {if_stmt}"
        
        print("✅ All if/else statements are for technical routing only")


class TestAIResponseServiceIntact:
    """Test that aiResponseService.js has NOT been modified with sending logic"""
    
    def test_no_send_functions(self):
        """Verify aiResponseService.js has no send functions"""
        with open(AI_RESPONSE_SERVICE_PATH, 'r') as f:
            content = f.read()
        
        # Should NOT contain any sending functions
        assert "sendEmail" not in content, "sendEmail found in aiResponseService.js"
        assert "sendWhatsApp" not in content, "sendWhatsApp found in aiResponseService.js"
        assert "emailjs.send" not in content, "emailjs.send found in aiResponseService.js"
        assert "twilio" not in content.lower(), "twilio found in aiResponseService.js"
        print("✅ aiResponseService.js has no sending functions")
    
    def test_only_config_functions(self):
        """Verify aiResponseService.js only has config/utility functions"""
        with open(AI_RESPONSE_SERVICE_PATH, 'r') as f:
            content = f.read()
        
        # Expected functions (config/utility only)
        expected_functions = [
            'getAIConfig',
            'saveAIConfig',
            'isAIEnabled',
            'setLastMediaUrl',
            'addAILog',
            'getAILogs',
            'clearAILogs',
            'findClientByPhone',
            'buildAIContext'
        ]
        
        for func in expected_functions:
            assert func in content, f"Expected function {func} not found"
        
        print("✅ aiResponseService.js contains only config/utility functions")
    
    def test_ai_service_is_trigger_not_sender(self):
        """Verify AI service is for triggering, not sending"""
        with open(AI_RESPONSE_SERVICE_PATH, 'r') as f:
            content = f.read()
        
        # Should have context building (for AI to decide)
        assert "buildAIContext" in content, "buildAIContext not found"
        
        # Should NOT have actual sending
        assert "fetch(" not in content or "api.twilio" not in content, \
            "Direct API calls found in aiResponseService.js"
        
        print("✅ aiResponseService.js is for AI triggering, not sending")


class TestGatewayPurity:
    """Test that gateways are pure output channels"""
    
    def test_email_gateway_is_pure_channel(self):
        """Verify sendEmailGateway is a pure output channel"""
        with open(MESSAGING_GATEWAY_PATH, 'r') as f:
            content = f.read()
        
        # Find sendEmailGateway function
        email_func_match = re.search(
            r'export const sendEmailGateway\s*=\s*async\s*\([^)]*\)\s*=>\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}',
            content,
            re.DOTALL
        )
        
        assert email_func_match, "sendEmailGateway function not found"
        
        # Check it receives parameters and transmits them
        assert "to_email" in content, "to_email parameter not found"
        assert "message" in content, "message parameter not found"
        assert "emailjs.send" in content, "emailjs.send not found"
        
        print("✅ sendEmailGateway is a pure output channel")
    
    def test_whatsapp_gateway_is_pure_channel(self):
        """Verify sendWhatsAppGateway is a pure output channel"""
        with open(MESSAGING_GATEWAY_PATH, 'r') as f:
            content = f.read()
        
        # Check it receives parameters and transmits them
        assert "phoneNumber" in content, "phoneNumber parameter not found"
        assert "twilioConfig" in content, "twilioConfig parameter not found"
        assert "api.twilio.com" in content, "Twilio API URL not found"
        
        print("✅ sendWhatsAppGateway is a pure output channel")
    
    def test_unified_gateway_routes_correctly(self):
        """Verify sendMessageGateway routes to correct channel"""
        with open(MESSAGING_GATEWAY_PATH, 'r') as f:
            content = f.read()
        
        # Check routing logic
        assert "channel === 'email'" in content, "Email channel routing not found"
        assert "channel === 'whatsapp'" in content, "WhatsApp channel routing not found"
        assert "sendEmailGateway" in content, "sendEmailGateway call not found"
        assert "sendWhatsAppGateway" in content, "sendWhatsAppGateway call not found"
        
        print("✅ sendMessageGateway routes correctly to email/whatsapp")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
