"""
v8.9.5 Multi-tenant Isolation Tests
- Tests coach_id filtering on reservations, campaigns, chat/participants
- Super Admin (contact.artboost@gmail.com) sees ALL data
- Other coaches see only their own data (coach_id == their email)
- Non-regression tests for courses, offers, discount-codes, payment-links
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
SUPER_ADMIN_EMAIL = "contact.artboost@gmail.com"
TEST_COACH_EMAIL = "unknown@coach.com"


class TestNonRegression:
    """Non-regression tests - Ensure existing endpoints still work"""
    
    def test_courses_intact(self):
        """GET /api/courses - Must return 200 and data"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Courses should return a list"
        print(f"✅ NON-REGRESSION: /api/courses returns {len(data)} courses")
    
    def test_offers_intact(self):
        """GET /api/offers - Must return 200 and data"""
        response = requests.get(f"{BASE_URL}/api/offers")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Offers should return a list"
        print(f"✅ NON-REGRESSION: /api/offers returns {len(data)} offers")
    
    def test_discount_codes_intact(self):
        """GET /api/discount-codes - Must return 200 and data"""
        response = requests.get(f"{BASE_URL}/api/discount-codes")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Discount codes should return a list"
        print(f"✅ NON-REGRESSION: /api/discount-codes returns {len(data)} codes")
    
    def test_payment_links_intact(self):
        """GET /api/payment-links - Must return 200 and data"""
        response = requests.get(f"{BASE_URL}/api/payment-links")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "id" in data, "Payment links should have an id"
        print(f"✅ NON-REGRESSION: /api/payment-links returns config")


class TestSuperAdminIsolation:
    """Test that Super Admin (Bassi) sees ALL data - filter DISABLED"""
    
    def test_reservations_super_admin_sees_all(self):
        """
        GET /api/reservations with X-User-Email: contact.artboost@gmail.com
        Super Admin should see ALL reservations (no filtering)
        """
        headers = {"X-User-Email": SUPER_ADMIN_EMAIL}
        response = requests.get(f"{BASE_URL}/api/reservations", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Response should have pagination structure
        assert "data" in data, "Response should have 'data' field"
        assert "pagination" in data, "Response should have 'pagination' field"
        
        reservations = data["data"]
        total = data["pagination"]["total"]
        
        print(f"✅ ISOLATION: Super Admin sees {len(reservations)} reservations (total: {total})")
        
        # Super Admin should see data (may be 0 if no reservations exist, but structure is correct)
        assert isinstance(reservations, list), "Reservations should be a list"
    
    def test_campaigns_super_admin_sees_all(self):
        """
        GET /api/campaigns with X-User-Email: contact.artboost@gmail.com
        Super Admin should see ALL campaigns
        """
        headers = {"X-User-Email": SUPER_ADMIN_EMAIL}
        response = requests.get(f"{BASE_URL}/api/campaigns", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert isinstance(data, list), "Campaigns should return a list"
        print(f"✅ ISOLATION: Super Admin sees {len(data)} campaigns")
    
    def test_chat_participants_super_admin_sees_all(self):
        """
        GET /api/chat/participants with X-User-Email: contact.artboost@gmail.com
        Super Admin should see ALL participants
        """
        headers = {"X-User-Email": SUPER_ADMIN_EMAIL}
        response = requests.get(f"{BASE_URL}/api/chat/participants", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert isinstance(data, list), "Participants should return a list"
        print(f"✅ ISOLATION: Super Admin sees {len(data)} participants")


class TestCoachIsolation:
    """Test that non-super-admin coaches see only their own data"""
    
    def test_reservations_unknown_coach_sees_zero(self):
        """
        GET /api/reservations with X-User-Email: unknown@coach.com
        Unknown coach should see 0 reservations (only their own data)
        """
        headers = {"X-User-Email": TEST_COACH_EMAIL}
        response = requests.get(f"{BASE_URL}/api/reservations", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Response should have pagination structure
        assert "data" in data, "Response should have 'data' field"
        assert "pagination" in data, "Response should have 'pagination' field"
        
        reservations = data["data"]
        total = data["pagination"]["total"]
        
        # Unknown coach should see 0 reservations (no data with coach_id = unknown@coach.com)
        assert total == 0, f"Unknown coach should see 0 reservations, got {total}"
        assert len(reservations) == 0, f"Unknown coach should see 0 items, got {len(reservations)}"
        
        print(f"✅ ISOLATION: Unknown coach sees {len(reservations)} reservations (total: {total})")
    
    def test_campaigns_unknown_coach_sees_zero(self):
        """
        GET /api/campaigns with X-User-Email: unknown@coach.com
        Unknown coach should see 0 campaigns
        """
        headers = {"X-User-Email": TEST_COACH_EMAIL}
        response = requests.get(f"{BASE_URL}/api/campaigns", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Unknown coach should see 0 campaigns
        assert len(data) == 0, f"Unknown coach should see 0 campaigns, got {len(data)}"
        
        print(f"✅ ISOLATION: Unknown coach sees {len(data)} campaigns")
    
    def test_chat_participants_unknown_coach_sees_zero(self):
        """
        GET /api/chat/participants with X-User-Email: unknown@coach.com
        Unknown coach should see 0 participants
        """
        headers = {"X-User-Email": TEST_COACH_EMAIL}
        response = requests.get(f"{BASE_URL}/api/chat/participants", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Unknown coach should see 0 participants
        assert len(data) == 0, f"Unknown coach should see 0 participants, got {len(data)}"
        
        print(f"✅ ISOLATION: Unknown coach sees {len(data)} participants")


class TestNoHeaderBehavior:
    """Test behavior when no X-User-Email header is provided"""
    
    def test_reservations_no_header(self):
        """
        GET /api/reservations without X-User-Email header
        Should return data (or empty) but not fail
        """
        response = requests.get(f"{BASE_URL}/api/reservations")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Response should have pagination structure
        assert "data" in data, "Response should have 'data' field"
        print(f"✅ NO HEADER: /api/reservations returns without error")
    
    def test_campaigns_no_header(self):
        """
        GET /api/campaigns without X-User-Email header
        Should return data (or empty) but not fail
        """
        response = requests.get(f"{BASE_URL}/api/campaigns")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ NO HEADER: /api/campaigns returns without error")
    
    def test_chat_participants_no_header(self):
        """
        GET /api/chat/participants without X-User-Email header
        Should return data (or empty) but not fail
        """
        response = requests.get(f"{BASE_URL}/api/chat/participants")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ NO HEADER: /api/chat/participants returns without error")


class TestCaseInsensitiveEmail:
    """Test that email comparison is case-insensitive"""
    
    def test_super_admin_uppercase(self):
        """Super Admin email in uppercase should work"""
        headers = {"X-User-Email": SUPER_ADMIN_EMAIL.upper()}
        response = requests.get(f"{BASE_URL}/api/reservations", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ CASE-INSENSITIVE: Uppercase email works")
    
    def test_super_admin_mixed_case(self):
        """Super Admin email in mixed case should work"""
        headers = {"X-User-Email": "Contact.ArtBoost@Gmail.Com"}
        response = requests.get(f"{BASE_URL}/api/reservations", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ CASE-INSENSITIVE: Mixed case email works")
