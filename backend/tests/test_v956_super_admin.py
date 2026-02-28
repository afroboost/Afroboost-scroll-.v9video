"""
Test Suite for Mission v9.5.6 - Super Admin Access and Partner Features
Tests:
- Super Admin access for both afroboost.bassi@gmail.com and contact.artboost@gmail.com
- /api/auth/role returns correct role for super admins
- /api/check-partner/{email} returns is_partner=true, has_credits=true for super admins
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Super Admin emails to test
SUPER_ADMIN_EMAILS = [
    'afroboost.bassi@gmail.com',
    'contact.artboost@gmail.com'
]

class TestSuperAdminAccess:
    """Tests for Super Admin access verification - v9.5.6"""
    
    def test_afroboost_bassi_auth_role(self):
        """Test that afroboost.bassi@gmail.com gets super_admin role"""
        email = 'afroboost.bassi@gmail.com'
        response = requests.get(
            f"{BASE_URL}/api/auth/role",
            headers={"X-User-Email": email}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("role") == "super_admin", f"Expected role=super_admin, got {data.get('role')}"
        assert data.get("is_super_admin") == True, f"Expected is_super_admin=True, got {data.get('is_super_admin')}"
        assert data.get("is_coach") == True, f"Expected is_coach=True, got {data.get('is_coach')}"
        assert data.get("email") == email, f"Expected email={email}, got {data.get('email')}"
        print(f"✅ afroboost.bassi@gmail.com: role=super_admin, is_super_admin=True, is_coach=True")
    
    def test_contact_artboost_auth_role(self):
        """Test that contact.artboost@gmail.com gets super_admin role"""
        email = 'contact.artboost@gmail.com'
        response = requests.get(
            f"{BASE_URL}/api/auth/role",
            headers={"X-User-Email": email}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("role") == "super_admin", f"Expected role=super_admin, got {data.get('role')}"
        assert data.get("is_super_admin") == True, f"Expected is_super_admin=True, got {data.get('is_super_admin')}"
        assert data.get("is_coach") == True, f"Expected is_coach=True, got {data.get('is_coach')}"
        assert data.get("email") == email, f"Expected email={email}, got {data.get('email')}"
        print(f"✅ contact.artboost@gmail.com: role=super_admin, is_super_admin=True, is_coach=True")
    
    def test_afroboost_bassi_check_partner(self):
        """Test that afroboost.bassi@gmail.com returns is_partner=true with unlimited credits"""
        email = 'afroboost.bassi@gmail.com'
        response = requests.get(f"{BASE_URL}/api/check-partner/{email}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("is_partner") == True, f"Expected is_partner=True, got {data.get('is_partner')}"
        assert data.get("has_credits") == True, f"Expected has_credits=True, got {data.get('has_credits')}"
        assert data.get("credits") == -1, f"Expected credits=-1 (unlimited), got {data.get('credits')}"
        assert data.get("unlimited") == True, f"Expected unlimited=True, got {data.get('unlimited')}"
        assert data.get("is_super_admin") == True, f"Expected is_super_admin=True, got {data.get('is_super_admin')}"
        print(f"✅ afroboost.bassi@gmail.com: is_partner=True, has_credits=True, unlimited=True")
    
    def test_contact_artboost_check_partner(self):
        """Test that contact.artboost@gmail.com returns is_partner=true with unlimited credits"""
        email = 'contact.artboost@gmail.com'
        response = requests.get(f"{BASE_URL}/api/check-partner/{email}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("is_partner") == True, f"Expected is_partner=True, got {data.get('is_partner')}"
        assert data.get("has_credits") == True, f"Expected has_credits=True, got {data.get('has_credits')}"
        assert data.get("credits") == -1, f"Expected credits=-1 (unlimited), got {data.get('credits')}"
        assert data.get("unlimited") == True, f"Expected unlimited=True, got {data.get('unlimited')}"
        assert data.get("is_super_admin") == True, f"Expected is_super_admin=True, got {data.get('is_super_admin')}"
        print(f"✅ contact.artboost@gmail.com: is_partner=True, has_credits=True, unlimited=True")
    
    def test_regular_user_is_not_super_admin(self):
        """Test that a regular email does NOT get super_admin role"""
        email = 'regular.user@example.com'
        response = requests.get(
            f"{BASE_URL}/api/auth/role",
            headers={"X-User-Email": email}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("role") != "super_admin", f"Regular user should NOT be super_admin"
        assert data.get("is_super_admin") == False, f"Expected is_super_admin=False for regular user"
        print(f"✅ Regular user correctly identified as non-super_admin")
    
    def test_regular_user_check_partner(self):
        """Test that a regular email returns is_partner=false"""
        email = 'regular.user@example.com'
        response = requests.get(f"{BASE_URL}/api/check-partner/{email}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("is_partner") == False, f"Expected is_partner=False for regular user"
        print(f"✅ Regular user correctly returns is_partner=False")


class TestPartnerAPI:
    """Tests for active partners API - v9.5.6"""
    
    def test_partners_active_endpoint(self):
        """Test that /api/partners/active returns list of active partners"""
        response = requests.get(f"{BASE_URL}/api/partners/active")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Expected list response"
        print(f"✅ /api/partners/active returns {len(data)} partners")


class TestCoreAPIs:
    """Tests for core API endpoints - v9.5.6"""
    
    def test_health_check(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ Health check passed")
    
    def test_courses_endpoint(self):
        """Test courses endpoint"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Expected list response"
        print(f"✅ /api/courses returns {len(data)} courses")
    
    def test_offers_endpoint(self):
        """Test offers endpoint"""
        response = requests.get(f"{BASE_URL}/api/offers")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Expected list response"
        print(f"✅ /api/offers returns {len(data)} offers")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
