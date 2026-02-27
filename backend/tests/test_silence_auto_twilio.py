"""
Test Suite: Mode Silence Auto & Twilio Skeleton - Iteration 52
Tests for:
1. silenceAutoEnabled state with localStorage persistence (afroboost_silence_auto)
2. toggleSilenceAuto() function
3. isInSilenceHours() logic (22h-08h)
4. playSoundIfEnabled checks silenceAutoEnabled AND isInSilenceHours()
5. MemoizedMessageBubble React.memo optimization
6. typingTimeoutRef cleanup in useEffect
7. REACT_APP_TWILIO_ENABLED in .env
8. twilioService.js skeleton with isTwilioEnabled()
"""

import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# === BACKEND API TESTS ===

class TestBackendHealth:
    """Basic API health checks"""
    
    def test_api_health(self):
        """TEST 1: API health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'healthy'
        print("✅ TEST 1 - API Health Check PASSED")
    
    def test_promo_code_validation(self):
        """TEST 2: Promo code basxx validates with correct email"""
        response = requests.post(f"{BASE_URL}/api/discount-codes/validate", json={
            "code": "basxx",
            "email": "bassicustomshoes@gmail.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get('valid') == True
        print("✅ TEST 2 - Promo code basxx validates PASSED")


class TestChatWidgetSilenceAuto:
    """Tests for Mode Silence Auto feature in ChatWidget.js"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Load ChatWidget.js content for analysis"""
        self.chatwidget_path = '/app/frontend/src/components/ChatWidget.js'
        with open(self.chatwidget_path, 'r') as f:
            self.chatwidget_content = f.read()
    
    def test_silence_auto_state_exists(self):
        """TEST 3: silenceAutoEnabled state with localStorage persistence"""
        assert 'silenceAutoEnabled' in self.chatwidget_content
        assert "localStorage.getItem('afroboost_silence_auto')" in self.chatwidget_content
        print("✅ TEST 3 - silenceAutoEnabled state with localStorage PASSED")
    
    def test_toggle_silence_auto_function(self):
        """TEST 4: toggleSilenceAuto() function defined"""
        assert 'toggleSilenceAuto' in self.chatwidget_content
        assert "setSilenceAutoEnabled" in self.chatwidget_content
        assert "localStorage.setItem('afroboost_silence_auto'" in self.chatwidget_content
        print("✅ TEST 4 - toggleSilenceAuto() function PASSED")
    
    def test_is_in_silence_hours_function(self):
        """TEST 5: isInSilenceHours() function checks 22h-08h"""
        assert 'isInSilenceHours' in self.chatwidget_content
        # Check for hour >= 22 OR hour < 8 logic
        assert 'hour >= 22' in self.chatwidget_content or 'hour >= 22 || hour < 8' in self.chatwidget_content
        assert 'hour < 8' in self.chatwidget_content
        print("✅ TEST 5 - isInSilenceHours() function (22h-08h) PASSED")
    
    def test_play_sound_if_enabled_checks_silence(self):
        """TEST 6: playSoundIfEnabled checks silenceAutoEnabled AND isInSilenceHours()"""
        # Find playSoundIfEnabled function
        assert 'playSoundIfEnabled' in self.chatwidget_content
        # Check that it verifies silenceAutoEnabled AND isInSilenceHours()
        assert 'silenceAutoEnabled && isInSilenceHours()' in self.chatwidget_content
        print("✅ TEST 6 - playSoundIfEnabled checks silence mode PASSED")
    
    def test_toggle_silence_auto_button_exists(self):
        """TEST 7: Toggle button with data-testid='toggle-silence-auto-btn'"""
        assert 'data-testid="toggle-silence-auto-btn"' in self.chatwidget_content
        print("✅ TEST 7 - Toggle silence auto button exists PASSED")
    
    def test_toggle_silence_auto_moon_icon(self):
        """TEST 8: Toggle button has moon (crescent) SVG icon"""
        # Moon icon SVG path: "M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"
        assert 'M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z' in self.chatwidget_content
        print("✅ TEST 8 - Moon icon (crescent) SVG PASSED")
    
    def test_toggle_silence_auto_text_changes(self):
        """TEST 9: Toggle text changes (Silence Auto ✓ / Silence Auto (22h-08h))"""
        assert "Silence Auto ✓" in self.chatwidget_content
        assert "Silence Auto (22h-08h)" in self.chatwidget_content
        print("✅ TEST 9 - Toggle text changes PASSED")
    
    def test_toggle_silence_auto_yellow_when_active(self):
        """TEST 10: Toggle shows yellow (#FBBF24) when active"""
        assert "silenceAutoEnabled ? '#FBBF24'" in self.chatwidget_content
        print("✅ TEST 10 - Yellow color when active PASSED")
    
    def test_toggle_closes_menu_after_click(self):
        """TEST 11: Toggle closes user menu after click"""
        # Check that toggleSilenceAuto is called with setShowUserMenu(false)
        assert 'toggleSilenceAuto(); setShowUserMenu(false)' in self.chatwidget_content
        print("✅ TEST 11 - Toggle closes menu after click PASSED")


class TestMemoizedMessageBubble:
    """Tests for React.memo optimization"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Load ChatWidget.js content"""
        with open('/app/frontend/src/components/ChatWidget.js', 'r') as f:
            self.content = f.read()
    
    def test_memoized_message_bubble_exists(self):
        """TEST 12: MemoizedMessageBubble with memo() exists"""
        assert 'MemoizedMessageBubble' in self.content
        assert 'memo(MessageBubble' in self.content
        print("✅ TEST 12 - MemoizedMessageBubble with memo() PASSED")
    
    def test_memo_comparison_function(self):
        """TEST 13: memo() has comparison function for optimization"""
        # Check for comparison function that checks msg.id, msg.text, etc.
        assert 'prevProps.msg.id === nextProps.msg.id' in self.content
        assert 'prevProps.msg.text === nextProps.msg.text' in self.content
        print("✅ TEST 13 - memo() comparison function PASSED")
    
    def test_memoized_bubble_used_in_render(self):
        """TEST 14: MemoizedMessageBubble is used in render"""
        assert '<MemoizedMessageBubble' in self.content
        print("✅ TEST 14 - MemoizedMessageBubble used in render PASSED")


class TestTypingTimeoutCleanup:
    """Tests for typingTimeoutRef cleanup"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Load ChatWidget.js content"""
        with open('/app/frontend/src/components/ChatWidget.js', 'r') as f:
            self.content = f.read()
    
    def test_typing_timeout_ref_exists(self):
        """TEST 15: typingTimeoutRef useRef exists"""
        assert 'typingTimeoutRef = useRef' in self.content
        print("✅ TEST 15 - typingTimeoutRef useRef exists PASSED")
    
    def test_typing_timeout_cleanup_in_useeffect(self):
        """TEST 16: typingTimeoutRef cleanup in useEffect return"""
        # Check for clearTimeout(typingTimeoutRef.current) in cleanup
        assert 'clearTimeout(typingTimeoutRef.current)' in self.content
        # Check for setting to null
        assert 'typingTimeoutRef.current = null' in self.content
        print("✅ TEST 16 - typingTimeoutRef cleanup in useEffect PASSED")


class TestTwilioEnvVariable:
    """Tests for REACT_APP_TWILIO_ENABLED in .env"""
    
    def test_twilio_enabled_in_env(self):
        """TEST 17: REACT_APP_TWILIO_ENABLED exists in frontend/.env"""
        with open('/app/frontend/.env', 'r') as f:
            env_content = f.read()
        assert 'REACT_APP_TWILIO_ENABLED' in env_content
        print("✅ TEST 17 - REACT_APP_TWILIO_ENABLED in .env PASSED")
    
    def test_twilio_enabled_is_false(self):
        """TEST 18: REACT_APP_TWILIO_ENABLED=false (not active yet)"""
        with open('/app/frontend/.env', 'r') as f:
            env_content = f.read()
        assert 'REACT_APP_TWILIO_ENABLED=false' in env_content
        print("✅ TEST 18 - REACT_APP_TWILIO_ENABLED=false PASSED")


class TestTwilioService:
    """Tests for twilioService.js skeleton"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Load twilioService.js content"""
        with open('/app/frontend/src/services/twilioService.js', 'r') as f:
            self.content = f.read()
    
    def test_twilio_service_file_exists(self):
        """TEST 19: twilioService.js file exists"""
        assert os.path.exists('/app/frontend/src/services/twilioService.js')
        print("✅ TEST 19 - twilioService.js file exists PASSED")
    
    def test_is_twilio_enabled_function(self):
        """TEST 20: isTwilioEnabled() function exists"""
        assert 'isTwilioEnabled' in self.content
        assert "process.env.REACT_APP_TWILIO_ENABLED === 'true'" in self.content
        print("✅ TEST 20 - isTwilioEnabled() function PASSED")
    
    def test_send_whatsapp_message_function(self):
        """TEST 21: sendWhatsAppMessage() function exists"""
        assert 'sendWhatsAppMessage' in self.content
        assert 'async' in self.content  # Should be async
        print("✅ TEST 21 - sendWhatsAppMessage() function PASSED")
    
    def test_format_whatsapp_number_function(self):
        """TEST 22: formatWhatsAppNumber() function exists"""
        assert 'formatWhatsAppNumber' in self.content
        assert 'whatsapp:' in self.content  # Should format with whatsapp: prefix
        print("✅ TEST 22 - formatWhatsAppNumber() function PASSED")
    
    def test_twilio_service_exports(self):
        """TEST 23: twilioService.js exports all functions"""
        assert 'export const isTwilioEnabled' in self.content
        assert 'export const sendWhatsAppMessage' in self.content
        assert 'export const formatWhatsAppNumber' in self.content
        print("✅ TEST 23 - twilioService.js exports PASSED")
    
    def test_twilio_service_checks_enabled_before_send(self):
        """TEST 24: sendWhatsAppMessage checks isTwilioEnabled() before sending"""
        # Find sendWhatsAppMessage function and check it calls isTwilioEnabled
        assert 'if (!isTwilioEnabled())' in self.content
        print("✅ TEST 24 - sendWhatsAppMessage checks isTwilioEnabled() PASSED")


class TestSilenceAutoLogic:
    """Tests for the silence auto logic flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Load ChatWidget.js content"""
        with open('/app/frontend/src/components/ChatWidget.js', 'r') as f:
            self.content = f.read()
    
    def test_silence_auto_default_false(self):
        """TEST 25: silenceAutoEnabled defaults to false"""
        # Check that it returns false by default
        assert "return saved === 'true'" in self.content or "saved === 'true'" in self.content
        # The catch block should return false
        assert 'catch { return false; }' in self.content or 'catch (e) { return false; }' in self.content or '} catch { return false; }' in self.content
        print("✅ TEST 25 - silenceAutoEnabled defaults to false PASSED")
    
    def test_silence_auto_console_log(self):
        """TEST 26: toggleSilenceAuto logs with moon emoji"""
        assert "[SILENCE AUTO] 🌙" in self.content
        print("✅ TEST 26 - toggleSilenceAuto logs with moon emoji PASSED")
    
    def test_play_sound_logs_silence_mode(self):
        """TEST 27: playSoundIfEnabled logs when silence mode active"""
        assert "[SOUND] 🌙 Mode silence actif" in self.content
        print("✅ TEST 27 - playSoundIfEnabled logs silence mode PASSED")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
