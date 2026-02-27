"""
Test Suite: Sound Notifications & Socket.IO Cleanup - Iteration 51
Tests for:
1. Toggle son: bouton 'Son activé/désactivé' dans le menu utilisateur avec icône haut-parleur filaire
2. Persistance son: localStorage 'afroboost_sound_enabled' sauvegarde la préférence
3. Sons distincts: playNotificationSound('private') pour DM, playNotificationSound('message') pour groupe
4. Wrapper playSoundIfEnabled: vérifie soundEnabled avant de jouer un son
5. Nettoyage Socket.IO: socket.off() appelé pour tous les listeners lors du démontage
6. Avatar refresh: messages mis à jour quand user_avatar_changed est reçu
"""

import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAPIHealth:
    """Basic API health checks"""
    
    def test_api_health(self):
        """TEST 1 - API Health Check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'healthy'
        print("✅ TEST 1 - API Health Check PASSED")

    def test_promo_code_validation(self):
        """TEST 2 - Promo code basxx validates with correct email"""
        response = requests.post(f"{BASE_URL}/api/discount-codes/validate", json={
            "code": "basxx",
            "email": "bassicustomshoes@gmail.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get('valid') == True
        print("✅ TEST 2 - Promo code basxx validates PASSED")


class TestFrontendSoundFeatures:
    """Tests for sound notification features in ChatWidget.js"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Load ChatWidget.js content for analysis"""
        self.chatwidget_path = '/app/frontend/src/components/ChatWidget.js'
        with open(self.chatwidget_path, 'r') as f:
            self.chatwidget_content = f.read()
        
        self.notification_service_path = '/app/frontend/src/services/notificationService.js'
        with open(self.notification_service_path, 'r') as f:
            self.notification_content = f.read()
    
    def test_sound_enabled_state_exists(self):
        """TEST 3 - soundEnabled state is defined with localStorage persistence"""
        assert "const [soundEnabled, setSoundEnabled] = useState" in self.chatwidget_content
        assert "localStorage.getItem('afroboost_sound_enabled')" in self.chatwidget_content
        print("✅ TEST 3 - soundEnabled state with localStorage persistence PASSED")
    
    def test_toggle_sound_function_exists(self):
        """TEST 4 - toggleSound() function is defined"""
        assert "const toggleSound = () =>" in self.chatwidget_content
        assert "setSoundEnabled(newValue)" in self.chatwidget_content
        assert "localStorage.setItem('afroboost_sound_enabled'" in self.chatwidget_content
        print("✅ TEST 4 - toggleSound() function PASSED")
    
    def test_play_sound_if_enabled_wrapper(self):
        """TEST 5 - playSoundIfEnabled() wrapper checks soundEnabled before playing"""
        assert "const playSoundIfEnabled = (type = 'message') =>" in self.chatwidget_content
        assert "if (soundEnabled)" in self.chatwidget_content
        assert "playNotificationSound(type)" in self.chatwidget_content
        print("✅ TEST 5 - playSoundIfEnabled() wrapper PASSED")
    
    def test_toggle_sound_button_exists(self):
        """TEST 6 - Toggle sound button with data-testid='toggle-sound-btn' exists"""
        assert 'data-testid="toggle-sound-btn"' in self.chatwidget_content
        print("✅ TEST 6 - Toggle sound button with data-testid PASSED")
    
    def test_toggle_sound_button_has_speaker_icon(self):
        """TEST 7 - Toggle sound button has wireframe speaker SVG icon"""
        # Check for speaker polygon (speaker shape)
        assert 'polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"' in self.chatwidget_content
        # Check for sound waves (enabled state)
        assert 'path d="M15.54 8.46a5 5 0 0 1 0 7.07"' in self.chatwidget_content
        # Check for X lines (disabled state)
        assert 'line x1="23" y1="9" x2="17" y2="15"' in self.chatwidget_content
        print("✅ TEST 7 - Toggle sound button has wireframe speaker SVG icon PASSED")
    
    def test_toggle_sound_button_text_changes(self):
        """TEST 8 - Toggle sound button text changes based on state"""
        assert "soundEnabled ? 'Son activé' : 'Son désactivé'" in self.chatwidget_content
        print("✅ TEST 8 - Toggle sound button text changes PASSED")
    
    def test_sound_toggle_closes_menu(self):
        """TEST 9 - Toggle sound closes user menu after click"""
        # Check that toggleSound and setShowUserMenu(false) are called together
        assert "toggleSound(); setShowUserMenu(false)" in self.chatwidget_content
        print("✅ TEST 9 - Toggle sound closes user menu PASSED")


class TestNotificationServiceSounds:
    """Tests for distinct sounds in notificationService.js"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Load notificationService.js content for analysis"""
        self.notification_service_path = '/app/frontend/src/services/notificationService.js'
        with open(self.notification_service_path, 'r') as f:
            self.notification_content = f.read()
    
    def test_play_notification_sound_function_exists(self):
        """TEST 10 - playNotificationSound function exists with type parameter"""
        assert "export const playNotificationSound = async (type = 'message')" in self.notification_content
        print("✅ TEST 10 - playNotificationSound function exists PASSED")
    
    def test_private_sound_type_exists(self):
        """TEST 11 - 'private' sound type is defined (Ding for DM)"""
        assert "case 'private':" in self.notification_content
        # Check for triple ascending beep (440 -> 554 -> 659 Hz)
        assert "oscillator.frequency.setValueAtTime(440, now)" in self.notification_content
        assert "oscillator.frequency.setValueAtTime(554, now + 0.1)" in self.notification_content
        assert "oscillator.frequency.setValueAtTime(659, now + 0.2)" in self.notification_content
        print("✅ TEST 11 - 'private' sound type (Ding) PASSED")
    
    def test_message_sound_type_exists(self):
        """TEST 12 - 'message' sound type is defined (Pop for group)"""
        assert "default:" in self.notification_content
        # Check for standard beep (587 Hz - Ré5)
        assert "oscillator.frequency.setValueAtTime(587, now)" in self.notification_content
        print("✅ TEST 12 - 'message' sound type (Pop) PASSED")
    
    def test_coach_sound_type_exists(self):
        """TEST 13 - 'coach' sound type is defined"""
        assert "case 'coach':" in self.notification_content
        # Check for double harmonious beep (523 -> 659 Hz)
        assert "oscillator.frequency.setValueAtTime(523, now)" in self.notification_content
        assert "oscillator.frequency.setValueAtTime(659, now + 0.12)" in self.notification_content
        print("✅ TEST 13 - 'coach' sound type PASSED")


class TestSocketIOCleanup:
    """Tests for Socket.IO cleanup on component unmount"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Load ChatWidget.js content for analysis"""
        self.chatwidget_path = '/app/frontend/src/components/ChatWidget.js'
        with open(self.chatwidget_path, 'r') as f:
            self.chatwidget_content = f.read()
    
    def test_socket_off_connect(self):
        """TEST 14 - socket.off('connect') is called on cleanup"""
        assert "socket.off('connect')" in self.chatwidget_content
        print("✅ TEST 14 - socket.off('connect') cleanup PASSED")
    
    def test_socket_off_joined_session(self):
        """TEST 15 - socket.off('joined_session') is called on cleanup"""
        assert "socket.off('joined_session')" in self.chatwidget_content
        print("✅ TEST 15 - socket.off('joined_session') cleanup PASSED")
    
    def test_socket_off_connect_error(self):
        """TEST 16 - socket.off('connect_error') is called on cleanup"""
        assert "socket.off('connect_error')" in self.chatwidget_content
        print("✅ TEST 16 - socket.off('connect_error') cleanup PASSED")
    
    def test_socket_off_disconnect(self):
        """TEST 17 - socket.off('disconnect') is called on cleanup"""
        assert "socket.off('disconnect')" in self.chatwidget_content
        print("✅ TEST 17 - socket.off('disconnect') cleanup PASSED")
    
    def test_socket_off_message_received(self):
        """TEST 18 - socket.off('message_received') is called on cleanup"""
        assert "socket.off('message_received')" in self.chatwidget_content
        print("✅ TEST 18 - socket.off('message_received') cleanup PASSED")
    
    def test_socket_off_user_typing(self):
        """TEST 19 - socket.off('user_typing') is called on cleanup"""
        assert "socket.off('user_typing')" in self.chatwidget_content
        print("✅ TEST 19 - socket.off('user_typing') cleanup PASSED")
    
    def test_socket_off_private_message_received(self):
        """TEST 20 - socket.off('private_message_received') is called on cleanup"""
        assert "socket.off('private_message_received'" in self.chatwidget_content
        print("✅ TEST 20 - socket.off('private_message_received') cleanup PASSED")
    
    def test_socket_off_dm_typing(self):
        """TEST 21 - socket.off('dm_typing') is called on cleanup"""
        assert "socket.off('dm_typing'" in self.chatwidget_content
        print("✅ TEST 21 - socket.off('dm_typing') cleanup PASSED")
    
    def test_socket_off_user_avatar_changed(self):
        """TEST 22 - socket.off('user_avatar_changed') is called on cleanup"""
        assert "socket.off('user_avatar_changed'" in self.chatwidget_content
        print("✅ TEST 22 - socket.off('user_avatar_changed') cleanup PASSED")
    
    def test_socket_disconnect_called(self):
        """TEST 23 - socket.disconnect() is called on cleanup"""
        assert "socket.disconnect()" in self.chatwidget_content
        print("✅ TEST 23 - socket.disconnect() cleanup PASSED")


class TestAvatarRefresh:
    """Tests for avatar refresh when user_avatar_changed is received"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Load ChatWidget.js content for analysis"""
        self.chatwidget_path = '/app/frontend/src/components/ChatWidget.js'
        with open(self.chatwidget_path, 'r') as f:
            self.chatwidget_content = f.read()
    
    def test_handle_avatar_changed_function_exists(self):
        """TEST 24 - handleAvatarChanged function is defined"""
        assert "const handleAvatarChanged = (data) =>" in self.chatwidget_content
        print("✅ TEST 24 - handleAvatarChanged function exists PASSED")
    
    def test_avatar_changed_listener_registered(self):
        """TEST 25 - user_avatar_changed Socket.IO listener is registered"""
        assert "socket.on('user_avatar_changed', handleAvatarChanged)" in self.chatwidget_content
        print("✅ TEST 25 - user_avatar_changed listener registered PASSED")
    
    def test_private_messages_updated_on_avatar_change(self):
        """TEST 26 - Private messages are updated when avatar changes"""
        assert "setPrivateMessages(prev => prev.map(msg =>" in self.chatwidget_content
        assert "senderPhotoUrl: data.photo_url" in self.chatwidget_content
        print("✅ TEST 26 - Private messages updated on avatar change PASSED")
    
    def test_main_messages_updated_on_avatar_change(self):
        """TEST 27 - Main chat messages are updated when avatar changes"""
        assert "setMessages(prev => prev.map(msg =>" in self.chatwidget_content
        print("✅ TEST 27 - Main chat messages updated on avatar change PASSED")


class TestSoundUsageInChat:
    """Tests for sound usage in chat flows"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Load ChatWidget.js content for analysis"""
        self.chatwidget_path = '/app/frontend/src/components/ChatWidget.js'
        with open(self.chatwidget_path, 'r') as f:
            self.chatwidget_content = f.read()
    
    def test_private_sound_used_for_dm(self):
        """TEST 28 - playSoundIfEnabled('private') is used for DM notifications"""
        assert "playSoundIfEnabled('private')" in self.chatwidget_content
        print("✅ TEST 28 - playSoundIfEnabled('private') used for DM PASSED")
    
    def test_message_sound_used_for_group(self):
        """TEST 29 - playSoundIfEnabled('message') is used for group messages"""
        assert "playSoundIfEnabled('message')" in self.chatwidget_content
        print("✅ TEST 29 - playSoundIfEnabled('message') used for group PASSED")
    
    def test_coach_sound_used_for_coach_response(self):
        """TEST 30 - playSoundIfEnabled('coach') is used for coach responses"""
        assert "playSoundIfEnabled('coach')" in self.chatwidget_content
        print("✅ TEST 30 - playSoundIfEnabled('coach') used for coach response PASSED")


class TestLocalStoragePersistence:
    """Tests for localStorage persistence of sound preference"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Load ChatWidget.js content for analysis"""
        self.chatwidget_path = '/app/frontend/src/components/ChatWidget.js'
        with open(self.chatwidget_path, 'r') as f:
            self.chatwidget_content = f.read()
    
    def test_sound_preference_loaded_on_mount(self):
        """TEST 31 - Sound preference is loaded from localStorage on component mount"""
        # Check that useState initializer reads from localStorage
        assert "const saved = localStorage.getItem('afroboost_sound_enabled')" in self.chatwidget_content
        assert "return saved !== null ? saved === 'true' : true" in self.chatwidget_content
        print("✅ TEST 31 - Sound preference loaded on mount PASSED")
    
    def test_sound_preference_saved_on_toggle(self):
        """TEST 32 - Sound preference is saved to localStorage on toggle"""
        assert "localStorage.setItem('afroboost_sound_enabled', String(newValue))" in self.chatwidget_content
        print("✅ TEST 32 - Sound preference saved on toggle PASSED")
    
    def test_sound_enabled_by_default(self):
        """TEST 33 - Sound is enabled by default (true) when no localStorage value"""
        # Check default value is true
        assert "return saved !== null ? saved === 'true' : true" in self.chatwidget_content
        print("✅ TEST 33 - Sound enabled by default PASSED")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
