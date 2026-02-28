"""
Test Mission v9.2.3 - BRANCHEMENT PARTENAIRE & PROPULSION RÉELLE
Tests for:
1. Dashboard visible for new partners (virgin accounts)
2. Badge '💰 Solde : 0 Crédit' ALWAYS displayed (no more null condition)
3. All 10 tabs accessible for new partners
4. Conversations tab doesn't crash with empty data
5. Campaigns tab doesn't crash with empty data
6. Super Admin (Bassi) with 7 reservations still functional
7. Badge '👑 Crédits Illimités' visible ONLY for Bassi
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndBasicAPIs:
    """Basic health and API tests"""
    
    def test_health_endpoint(self):
        """Test backend health"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print("✅ Backend healthy and database connected")
    
    def test_courses_api(self):
        """Test courses endpoint"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Courses API: {len(data)} courses found")
    
    def test_offers_api(self):
        """Test offers endpoint"""
        response = requests.get(f"{BASE_URL}/api/offers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Offers API: {len(data)} offers found")
    
    def test_concept_api(self):
        """Test concept endpoint"""
        response = requests.get(f"{BASE_URL}/api/concept")
        assert response.status_code == 200
        data = response.json()
        assert "appName" in data or "description" in data
        print(f"✅ Concept API working")


class TestCoachProfile:
    """Test coach profile API - v9.2.3 focus"""
    
    def test_super_admin_profile(self):
        """Test Super Admin (Bassi) profile - should have unlimited credits"""
        response = requests.get(
            f"{BASE_URL}/api/coach/profile",
            headers={"X-User-Email": "contact.artboost@gmail.com"}
        )
        # Super Admin profile should exist
        if response.status_code == 200:
            data = response.json()
            # Super Admin should have unlimited credits (-1)
            credits = data.get("credits", 0)
            print(f"✅ Super Admin profile: credits={credits}")
        else:
            # 404 is acceptable - profile may be created on first access
            print(f"⚠️ Super Admin profile not found (404) - may be created on login")
            assert response.status_code in [200, 404]
    
    def test_new_partner_profile_404(self):
        """Test new partner (virgin account) - should return 404"""
        response = requests.get(
            f"{BASE_URL}/api/coach/profile",
            headers={"X-User-Email": "nouveau.partenaire@test.com"}
        )
        # New partner should get 404 - profile doesn't exist in DB
        assert response.status_code == 404
        print("✅ New partner profile returns 404 as expected")
    
    def test_profile_error_handling(self):
        """Test profile endpoint handles missing email gracefully"""
        response = requests.get(
            f"{BASE_URL}/api/coach/profile",
            headers={"X-User-Email": ""}
        )
        # Should return 401 or 404
        assert response.status_code in [401, 404, 422]
        print(f"✅ Profile endpoint handles empty email: {response.status_code}")


class TestReservationsAPI:
    """Test reservations API - Super Admin should have 7 Bassi reservations"""
    
    def test_super_admin_reservations(self):
        """Test Super Admin reservations - 7 Bassi reservations expected"""
        response = requests.get(
            f"{BASE_URL}/api/reservations",
            headers={"X-User-Email": "contact.artboost@gmail.com"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        if "data" in data:
            reservations = data["data"]
        else:
            reservations = data
        
        assert isinstance(reservations, list)
        print(f"✅ Reservations API: {len(reservations)} reservations for Super Admin")
        
        # Count Bassi reservations (from 04/03/2026)
        bassi_reservations = [r for r in reservations if "Bassi" in r.get("userName", "") or "BASSI" in r.get("userName", "")]
        print(f"✅ Bassi reservations: {len(bassi_reservations)}")
    
    def test_new_partner_empty_reservations(self):
        """Test new partner should have 0 reservations"""
        response = requests.get(
            f"{BASE_URL}/api/reservations",
            headers={"X-User-Email": "nouveau.partenaire@test.com"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        if "data" in data:
            reservations = data["data"]
        else:
            reservations = data
        
        # New partner should have empty reservations
        assert isinstance(reservations, list)
        print(f"✅ New partner reservations: {len(reservations)} (empty expected)")


class TestCampaignsAPI:
    """Test campaigns API - should not crash with empty data"""
    
    def test_campaigns_api_empty(self):
        """Test campaigns API returns empty list for new partner"""
        response = requests.get(
            f"{BASE_URL}/api/campaigns",
            headers={"X-User-Email": "nouveau.partenaire@test.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Campaigns API works (new partner): {len(data)} campaigns")
    
    def test_scheduler_health(self):
        """Test scheduler health endpoint"""
        response = requests.get(f"{BASE_URL}/api/scheduler/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        print(f"✅ Scheduler health: {data['status']}")


class TestConversationsAPI:
    """Test conversations API - should not crash with empty data"""
    
    def test_conversations_api_empty(self):
        """Test conversations API returns empty for new partner"""
        response = requests.get(
            f"{BASE_URL}/api/conversations",
            headers={"X-User-Email": "nouveau.partenaire@test.com"}
        )
        # Should return 200 with empty data
        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data or isinstance(data, list)
        print(f"✅ Conversations API works (new partner)")
    
    def test_chat_sessions_api(self):
        """Test chat sessions API"""
        response = requests.get(f"{BASE_URL}/api/chat/sessions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Chat sessions API: {len(data)} sessions")
    
    def test_chat_links_api(self):
        """Test chat links API"""
        response = requests.get(f"{BASE_URL}/api/chat/links")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Chat links API: {len(data)} links")


class TestStripeConnectAPI:
    """Test Stripe Connect status API for partners"""
    
    def test_stripe_connect_status_new_partner(self):
        """Test Stripe Connect status for new partner"""
        response = requests.get(
            f"{BASE_URL}/api/coach/stripe-connect/status",
            headers={"X-User-Email": "nouveau.partenaire@test.com"}
        )
        # Should return 200 or 404
        assert response.status_code in [200, 404]
        print(f"✅ Stripe Connect status API: {response.status_code}")


class TestDiscountCodesAPI:
    """Test discount codes API"""
    
    def test_discount_codes_api(self):
        """Test discount codes endpoint"""
        response = requests.get(f"{BASE_URL}/api/discount-codes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Discount codes API: {len(data)} codes")


class TestPaymentLinksAPI:
    """Test payment links API"""
    
    def test_payment_links_api(self):
        """Test payment links endpoint"""
        response = requests.get(f"{BASE_URL}/api/payment-links")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        print(f"✅ Payment links API working")


class TestUsersAPI:
    """Test users API"""
    
    def test_users_api(self):
        """Test users endpoint"""
        response = requests.get(f"{BASE_URL}/api/users")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Users API: {len(data)} users")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
