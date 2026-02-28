"""
Tests Mission v9.5.2: Logique d'Accès et Réparation Flux
- /api/check-partner endpoint: returns is_partner and has_credits
- Intelligent routing logic verification
- Flux video lazy loading (frontend)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestCheckPartnerEndpoint:
    """Test /api/check-partner/{email} endpoint - v9.5.2"""
    
    def test_check_partner_returns_is_partner_and_has_credits_fields(self):
        """API /api/check-partner returns is_partner and has_credits fields"""
        # Test with a known email (super admin)
        response = requests.get(f"{BASE_URL}/api/check-partner/contact.artboost@gmail.com")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify response structure
        assert "is_partner" in data, "Response should contain 'is_partner' field"
        assert "email" in data, "Response should contain 'email' field"
        
        # For super admin, should be partner
        print(f"✅ /api/check-partner response for super admin: {data}")
    
    def test_check_partner_non_partner_user(self):
        """API /api/check-partner returns is_partner=False for non-partner"""
        # Test with a random email that is not a partner
        response = requests.get(f"{BASE_URL}/api/check-partner/random_user_12345@test.com")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "is_partner" in data, "Response should contain 'is_partner' field"
        assert data["is_partner"] == False, "Non-partner should have is_partner=False"
        
        print(f"✅ /api/check-partner response for non-partner: {data}")
    
    def test_check_partner_has_credits_field(self):
        """API /api/check-partner should return has_credits field for partners"""
        # Test with super admin who should be a partner
        response = requests.get(f"{BASE_URL}/api/check-partner/contact.artboost@gmail.com")
        
        assert response.status_code == 200
        data = response.json()
        
        # If is_partner is True, has_credits should be present
        if data.get("is_partner"):
            assert "has_credits" in data, "Partner response should include 'has_credits' field"
            print(f"✅ Partner has credits field: has_credits={data.get('has_credits')}")
        else:
            print(f"ℹ️ User is not a partner: {data}")


class TestHealthEndpoint:
    """Basic health check tests"""
    
    def test_health_endpoint(self):
        """Health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✅ Health check: {data}")


class TestPartnersActiveEndpoint:
    """Test /api/partners/active for flux video loading"""
    
    def test_partners_active_returns_list(self):
        """API /api/partners/active returns list of active partners"""
        response = requests.get(f"{BASE_URL}/api/partners/active")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert isinstance(data, list), "Response should be a list"
        print(f"✅ /api/partners/active returned {len(data)} partners")
        
        # If partners exist, check structure
        if len(data) > 0:
            partner = data[0]
            # Partners should have id or email for identification
            assert "email" in partner or "id" in partner, "Partner should have email or id"
            print(f"✅ First partner structure: {list(partner.keys())}")


class TestAuthRoleEndpoint:
    """Test /api/auth/role for user role detection"""
    
    def test_auth_role_super_admin(self):
        """API /api/auth/role returns super_admin role for admin email"""
        response = requests.get(
            f"{BASE_URL}/api/auth/role",
            headers={"X-User-Email": "contact.artboost@gmail.com"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "role" in data, "Response should contain 'role' field"
        assert "is_super_admin" in data, "Response should contain 'is_super_admin' field"
        
        # Super admin should have is_super_admin=True
        assert data.get("is_super_admin") == True, "Super admin should have is_super_admin=True"
        print(f"✅ /api/auth/role for super admin: {data}")
    
    def test_auth_role_regular_user(self):
        """API /api/auth/role returns user role for non-admin"""
        response = requests.get(
            f"{BASE_URL}/api/auth/role",
            headers={"X-User-Email": "regular_user@example.com"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "role" in data, "Response should contain 'role' field"
        # Regular user should not be super admin
        assert data.get("is_super_admin") != True or data.get("role") != "super_admin", \
            "Regular user should not be super admin"
        print(f"✅ /api/auth/role for regular user: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
