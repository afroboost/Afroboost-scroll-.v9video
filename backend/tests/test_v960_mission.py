"""
Test Suite for Mission v9.6.0: Réparation Structurelle et Épure
- Backend: Super Admin auth/role returns is_super_admin=true
- Backend: check-partner returns is_partner=true, has_credits=true for Super Admin
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestV960SuperAdminAuth:
    """Test Super Admin authentication and role verification"""
    
    def test_health_check(self):
        """Verify API is running"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print("✅ Health check passed")
    
    def test_super_admin_afroboost_auth_role(self):
        """Test auth/role returns is_super_admin=true for afroboost.bassi@gmail.com"""
        response = requests.get(
            f"{BASE_URL}/api/auth/role",
            headers={'X-User-Email': 'afroboost.bassi@gmail.com'}
        )
        assert response.status_code == 200, f"Auth role failed: {response.status_code}"
        data = response.json()
        
        # Verify super admin status
        assert data.get('is_super_admin') == True, f"Expected is_super_admin=true, got {data.get('is_super_admin')}"
        assert data.get('role') == 'super_admin', f"Expected role='super_admin', got {data.get('role')}"
        assert data.get('email') == 'afroboost.bassi@gmail.com'
        print(f"✅ Super Admin auth/role verified: {data}")
    
    def test_super_admin_check_partner_status(self):
        """Test check-partner returns is_partner=true, has_credits=true for Super Admin"""
        response = requests.get(f"{BASE_URL}/api/check-partner/afroboost.bassi%40gmail.com")
        assert response.status_code == 200, f"Check partner failed: {response.status_code}"
        data = response.json()
        
        # Verify partner status for Super Admin
        assert data.get('is_partner') == True, f"Expected is_partner=true, got {data.get('is_partner')}"
        assert data.get('has_credits') == True, f"Expected has_credits=true, got {data.get('has_credits')}"
        assert data.get('is_super_admin') == True, f"Expected is_super_admin=true, got {data.get('is_super_admin')}"
        assert data.get('unlimited') == True, f"Expected unlimited=true, got {data.get('unlimited')}"
        assert data.get('credits') == -1, f"Expected credits=-1 (unlimited), got {data.get('credits')}"
        print(f"✅ Super Admin check-partner verified: {data}")
    
    def test_super_admin_credits_check(self):
        """Test credits/check returns unlimited credits for Super Admin"""
        response = requests.get(
            f"{BASE_URL}/api/credits/check",
            headers={'X-User-Email': 'afroboost.bassi@gmail.com'}
        )
        assert response.status_code == 200, f"Credits check failed: {response.status_code}"
        data = response.json()
        
        # Verify unlimited credits
        assert data.get('credits') == -1, f"Expected credits=-1, got {data.get('credits')}"
        assert data.get('unlimited') == True, f"Expected unlimited=true, got {data.get('unlimited')}"
        print(f"✅ Super Admin credits check verified: {data}")
    
    def test_super_admin_credits_deduct_bypass(self):
        """Test credits/deduct is bypassed for Super Admin"""
        response = requests.post(
            f"{BASE_URL}/api/credits/deduct",
            headers={'X-User-Email': 'afroboost.bassi@gmail.com'},
            json={'action': 'test_action'}
        )
        assert response.status_code == 200, f"Credits deduct failed: {response.status_code}"
        data = response.json()
        
        # Verify bypass for Super Admin
        assert data.get('bypassed') == True, f"Expected bypassed=true for Super Admin, got {data}"
        print(f"✅ Super Admin credits deduct bypass verified: {data}")

class TestV960Endpoints:
    """Test core endpoints remain functional"""
    
    def test_partners_active_endpoint(self):
        """Test /partners/active returns partner list"""
        response = requests.get(f"{BASE_URL}/api/partners/active")
        assert response.status_code == 200, f"Partners active failed: {response.status_code}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✅ Partners active endpoint returns {len(data)} partners")
    
    def test_courses_endpoint(self):
        """Test /courses returns course list"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200, f"Courses endpoint failed: {response.status_code}"
        print("✅ Courses endpoint working")
    
    def test_concept_endpoint(self):
        """Test /concept returns concept data"""
        response = requests.get(f"{BASE_URL}/api/concept")
        assert response.status_code == 200, f"Concept endpoint failed: {response.status_code}"
        print("✅ Concept endpoint working")
    
    def test_offers_endpoint(self):
        """Test /offers returns offer list"""
        response = requests.get(f"{BASE_URL}/api/offers")
        assert response.status_code == 200, f"Offers endpoint failed: {response.status_code}"
        print("✅ Offers endpoint working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
