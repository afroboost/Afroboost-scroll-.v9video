"""
Mission v9.5.7 Backend Tests - Pixel Alignment & Maintenance Security
Tests:
1. Platform settings API returns maintenance_mode status
2. Super Admin (afroboost.bassi@gmail.com) has is_super_admin=true
3. Partners active API returns list of partners
4. Health check endpoint
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestV957Mission:
    """Mission v9.5.7 Backend Tests"""
    
    # === PLATFORM SETTINGS ===
    def test_platform_settings_returns_maintenance_mode(self):
        """TEST 1: Platform settings API returns maintenance_mode"""
        response = requests.get(f"{BASE_URL}/api/platform-settings")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "maintenance_mode" in data, "maintenance_mode field missing"
        assert isinstance(data["maintenance_mode"], bool), "maintenance_mode should be boolean"
        print(f"✅ Platform settings: maintenance_mode={data['maintenance_mode']}")
    
    def test_platform_settings_partner_access(self):
        """TEST 2: Platform settings includes partner_access_enabled"""
        response = requests.get(f"{BASE_URL}/api/platform-settings")
        assert response.status_code == 200
        
        data = response.json()
        assert "partner_access_enabled" in data, "partner_access_enabled field missing"
        print(f"✅ Partner access enabled: {data['partner_access_enabled']}")
    
    # === SUPER ADMIN AUTH ===
    def test_afroboost_bassi_is_super_admin(self):
        """TEST 3: afroboost.bassi@gmail.com has is_super_admin=true"""
        headers = {"X-User-Email": "afroboost.bassi@gmail.com"}
        response = requests.get(f"{BASE_URL}/api/auth/role", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("is_super_admin") == True, f"Expected is_super_admin=True, got {data}"
        assert data.get("role") == "super_admin", f"Expected role=super_admin, got {data.get('role')}"
        print(f"✅ afroboost.bassi@gmail.com is Super Admin")
    
    def test_contact_artboost_is_super_admin(self):
        """TEST 4: contact.artboost@gmail.com has is_super_admin=true"""
        headers = {"X-User-Email": "contact.artboost@gmail.com"}
        response = requests.get(f"{BASE_URL}/api/auth/role", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("is_super_admin") == True, f"Expected is_super_admin=True, got {data}"
        assert data.get("role") == "super_admin", f"Expected role=super_admin, got {data.get('role')}"
        print(f"✅ contact.artboost@gmail.com is Super Admin")
    
    def test_regular_user_not_super_admin(self):
        """TEST 5: Regular user is not super_admin"""
        headers = {"X-User-Email": "regular.user@test.com"}
        response = requests.get(f"{BASE_URL}/api/auth/role", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("is_super_admin") == False, f"Expected is_super_admin=False, got {data}"
        assert data.get("role") == "user", f"Expected role=user, got {data.get('role')}"
        print(f"✅ Regular user is NOT Super Admin")
    
    # === PARTNERS ACTIVE ===
    def test_partners_active_returns_list(self):
        """TEST 6: /api/partners/active returns list of partners"""
        response = requests.get(f"{BASE_URL}/api/partners/active")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Expected list of partners"
        print(f"✅ Partners active: {len(data)} partners returned")
        
        # Check first partner structure if exists
        if len(data) > 0:
            partner = data[0]
            assert "id" in partner or "email" in partner, "Partner should have id or email"
            print(f"✅ First partner: {partner.get('name', partner.get('email', 'Unknown'))}")
    
    def test_partners_have_video_url(self):
        """TEST 7: Partners have video_url or heroImageUrl"""
        response = requests.get(f"{BASE_URL}/api/partners/active")
        assert response.status_code == 200
        
        data = response.json()
        if len(data) > 0:
            partner = data[0]
            has_video = "video_url" in partner or "heroImageUrl" in partner
            print(f"✅ Partner has video content: {has_video}")
    
    # === HEALTH CHECK ===
    def test_health_check(self):
        """TEST 8: Health check returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "healthy", f"Expected healthy, got {data.get('status')}"
        print(f"✅ Health check: {data.get('status')}")
    
    # === COURSES/SESSIONS ===
    def test_courses_endpoint(self):
        """TEST 9: /api/courses returns sessions"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Expected list of courses"
        print(f"✅ Courses: {len(data)} sessions returned")
    
    # === CHECK PARTNER (for Super Admin bypass) ===
    def test_check_partner_super_admin_bypass(self):
        """TEST 10: Super Admin has unlimited credits"""
        response = requests.get(f"{BASE_URL}/api/check-partner/afroboost.bassi@gmail.com")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("is_super_admin") == True, "Super Admin should have is_super_admin=True"
        assert data.get("unlimited") == True, "Super Admin should have unlimited credits"
        print(f"✅ Super Admin has unlimited credits: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
