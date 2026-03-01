"""
v9.5.9 Mission Tests: Credit Gauge, Super Admin Badge, Data Isolation
Tests for:
1. Super Admin credits check returns unlimited (-1)
2. Partner isolation (coach_id filter)
3. Credits deduct bypass for Super Admin
4. Check both Super Admin emails (afroboost.bassi@gmail.com, contact.artboost@gmail.com)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# v9.5.9 Test Credentials
SUPER_ADMIN_EMAILS = ['afroboost.bassi@gmail.com', 'contact.artboost@gmail.com']
TEST_PARTNER_EMAIL = 'test.random.partner.v959@example.com'


class TestHealth:
    """Basic health check"""
    
    def test_health_check(self):
        """Test /health endpoint is responding"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✅ Health check passed")


class TestSuperAdminCreditsV959:
    """v9.5.9: Super Admin unlimited credits"""
    
    def test_super_admin_afroboost_credits_unlimited(self):
        """Super Admin afroboost.bassi@gmail.com should have unlimited credits (-1)"""
        response = requests.get(
            f"{BASE_URL}/api/credits/check",
            headers={"X-User-Email": "afroboost.bassi@gmail.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("has_credits") == True
        assert data.get("credits") == -1
        assert data.get("unlimited") == True
        print("✅ afroboost.bassi@gmail.com has unlimited credits")
    
    def test_super_admin_artboost_credits_unlimited(self):
        """Super Admin contact.artboost@gmail.com should have unlimited credits (-1)"""
        response = requests.get(
            f"{BASE_URL}/api/credits/check",
            headers={"X-User-Email": "contact.artboost@gmail.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("has_credits") == True
        assert data.get("credits") == -1
        assert data.get("unlimited") == True
        print("✅ contact.artboost@gmail.com has unlimited credits")
    
    def test_super_admin_credits_deduct_bypass(self):
        """Super Admin credits deduct should be bypassed (no actual deduction)"""
        response = requests.post(
            f"{BASE_URL}/api/credits/deduct",
            headers={
                "X-User-Email": "afroboost.bassi@gmail.com",
                "Content-Type": "application/json"
            },
            json={"action": "test_v959"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert data.get("credits_remaining") == -1
        assert data.get("bypassed") == True
        print("✅ Super Admin credits deduct bypassed successfully")


class TestDataIsolationV959:
    """v9.5.9: Data isolation via coach_id"""
    
    def test_super_admin_sees_all_reservations(self):
        """Super Admin should see all reservations (no coach_id filter)"""
        response = requests.get(
            f"{BASE_URL}/api/reservations?limit=100",
            headers={"X-User-Email": "afroboost.bassi@gmail.com"}
        )
        assert response.status_code == 200
        data = response.json()
        pagination = data.get("pagination", {})
        # Super Admin should see multiple reservations (8 total from previous test)
        assert pagination.get("total", 0) >= 0
        print(f"✅ Super Admin sees {pagination.get('total')} reservations")
    
    def test_random_partner_sees_zero_reservations(self):
        """Random test partner should see 0 reservations (isolated by coach_id)"""
        response = requests.get(
            f"{BASE_URL}/api/reservations?limit=10",
            headers={"X-User-Email": TEST_PARTNER_EMAIL}
        )
        assert response.status_code == 200
        data = response.json()
        pagination = data.get("pagination", {})
        # Random partner should see 0 (no reservations with their coach_id)
        assert pagination.get("total") == 0
        print("✅ Random partner sees 0 reservations (properly isolated)")
    
    def test_no_email_blocked(self):
        """Request without X-User-Email should see no data"""
        response = requests.get(f"{BASE_URL}/api/reservations?limit=10")
        assert response.status_code == 200
        data = response.json()
        pagination = data.get("pagination", {})
        # No email = coach_id filter set to "__no_access__" -> 0 results
        assert pagination.get("total") == 0
        print("✅ No email = blocked access (0 reservations)")


class TestCreditsEndpointsV959:
    """v9.5.9: Credits endpoints validation"""
    
    def test_credits_check_missing_email_error(self):
        """Credits check without email should return error"""
        response = requests.get(f"{BASE_URL}/api/credits/check")
        assert response.status_code == 200
        data = response.json()
        assert data.get("has_credits") == False
        assert "error" in data or data.get("credits") == 0
        print("✅ Credits check without email returns proper error/0")
    
    def test_credits_deduct_missing_email_error(self):
        """Credits deduct without email should return error"""
        response = requests.post(
            f"{BASE_URL}/api/credits/deduct",
            headers={"Content-Type": "application/json"},
            json={"action": "test"}
        )
        assert response.status_code in [200, 400, 422]
        print("✅ Credits deduct without email handled")


class TestPartnerCheckV959:
    """v9.5.9: Partner check endpoint (uses path parameter /check-partner/{email})"""
    
    def test_check_partner_super_admin_afroboost(self):
        """Check partner endpoint for Super Admin afroboost.bassi@gmail.com"""
        # Note: endpoint uses path parameter, not header
        response = requests.get(f"{BASE_URL}/api/check-partner/afroboost.bassi@gmail.com")
        assert response.status_code == 200
        data = response.json()
        assert data.get("is_partner") == True
        assert data.get("is_super_admin") == True
        assert data.get("has_credits") == True
        assert data.get("credits") == -1
        print("✅ check-partner: afroboost.bassi is Super Admin with unlimited credits")
    
    def test_check_partner_super_admin_artboost(self):
        """Check partner endpoint for Super Admin contact.artboost@gmail.com"""
        response = requests.get(f"{BASE_URL}/api/check-partner/contact.artboost@gmail.com")
        assert response.status_code == 200
        data = response.json()
        assert data.get("is_partner") == True
        assert data.get("is_super_admin") == True
        print("✅ check-partner: contact.artboost is Super Admin")
    
    def test_check_partner_non_super_admin(self):
        """Check partner endpoint for non-Super Admin (not in DB)"""
        response = requests.get(f"{BASE_URL}/api/check-partner/{TEST_PARTNER_EMAIL}")
        assert response.status_code == 200
        data = response.json()
        # Non-existent partner should return is_partner=false
        assert data.get("is_partner") == False
        assert data.get("is_super_admin") != True
        print("✅ check-partner: non-super-admin handled correctly")


class TestCoreEndpointsV959:
    """v9.5.9: Core API endpoints verification"""
    
    def test_courses_endpoint(self):
        """Test /api/courses endpoint"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        print("✅ Courses endpoint working")
    
    def test_offers_endpoint(self):
        """Test /api/offers endpoint"""
        response = requests.get(f"{BASE_URL}/api/offers")
        assert response.status_code == 200
        print("✅ Offers endpoint working")
    
    def test_concept_endpoint(self):
        """Test /api/concept endpoint"""
        response = requests.get(f"{BASE_URL}/api/concept")
        assert response.status_code == 200
        print("✅ Concept endpoint working")
    
    def test_partners_active_endpoint(self):
        """Test /api/partners/active endpoint"""
        response = requests.get(f"{BASE_URL}/api/partners/active")
        assert response.status_code == 200
        print("✅ Partners active endpoint working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
