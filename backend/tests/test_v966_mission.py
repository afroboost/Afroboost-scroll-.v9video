"""
Mission v9.6.6 Tests: Fix Doublons Vidéo et Alignement UI
- Backend: /api/partners/active returns unique partners (no duplicates)
- Backend: Super Admin (afroboost.bassi@gmail.com) has unlimited credits
- Deduplication logic with seen_emails set
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestV966BackendDeduplication:
    """v9.6.6: Tests for partner deduplication and Super Admin credits"""
    
    def test_health_check(self):
        """Verify API is healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✅ Health check passed")
    
    def test_partners_active_returns_unique_by_email(self):
        """v9.6.6: Verify /api/partners/active returns unique partners (no duplicates by email)"""
        response = requests.get(f"{BASE_URL}/api/partners/active")
        assert response.status_code == 200
        
        partners = response.json()
        assert isinstance(partners, list)
        
        # Check for unique emails
        emails = [p.get("email", "").lower() for p in partners if p.get("email")]
        unique_emails = set(emails)
        
        # v9.6.6: All emails should be unique
        assert len(emails) == len(unique_emails), f"Duplicate emails found! {len(emails)} total vs {len(unique_emails)} unique"
        print(f"✅ Partners active: {len(partners)} partners, all unique by email")
    
    def test_partners_active_bassi_has_unique_id(self):
        """v9.6.6: Verify Bassi (first partner) has unique ID 'bassi_main'"""
        response = requests.get(f"{BASE_URL}/api/partners/active")
        assert response.status_code == 200
        
        partners = response.json()
        if len(partners) > 0:
            first_partner = partners[0]
            # v9.6.6: Bassi should be first and have ID "bassi_main"
            assert first_partner.get("id") == "bassi_main", f"First partner ID should be 'bassi_main', got: {first_partner.get('id')}"
            print(f"✅ Bassi has unique ID: {first_partner.get('id')}")
        else:
            pytest.skip("No partners returned")
    
    def test_super_admin_bassi_unlimited_credits(self):
        """v9.6.6: Verify Super Admin (afroboost.bassi@gmail.com) has unlimited credits"""
        response = requests.get(
            f"{BASE_URL}/api/coach/check-credits",
            headers={"X-User-Email": "afroboost.bassi@gmail.com"}
        )
        assert response.status_code == 200
        
        data = response.json()
        # v9.6.6: Super Admin should have unlimited credits
        assert data.get("has_credits") is True, "Super Admin should have credits"
        assert data.get("credits") == -1, f"Super Admin credits should be -1 (unlimited), got: {data.get('credits')}"
        assert data.get("unlimited") is True, "Super Admin should have unlimited flag"
        print(f"✅ Super Admin afroboost.bassi@gmail.com has unlimited credits: {data}")
    
    def test_super_admin_contact_artboost_unlimited_credits(self):
        """v9.6.6: Verify Super Admin (contact.artboost@gmail.com) has unlimited credits"""
        response = requests.get(
            f"{BASE_URL}/api/coach/check-credits",
            headers={"X-User-Email": "contact.artboost@gmail.com"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("has_credits") is True
        assert data.get("credits") == -1
        assert data.get("unlimited") is True
        print(f"✅ Super Admin contact.artboost@gmail.com has unlimited credits: {data}")
    
    def test_partners_active_all_have_unique_ids(self):
        """v9.6.6: Verify all partners have unique IDs"""
        response = requests.get(f"{BASE_URL}/api/partners/active")
        assert response.status_code == 200
        
        partners = response.json()
        ids = [p.get("id") for p in partners if p.get("id")]
        unique_ids = set(ids)
        
        assert len(ids) == len(unique_ids), f"Duplicate IDs found! {len(ids)} total vs {len(unique_ids)} unique"
        print(f"✅ All {len(partners)} partners have unique IDs")
    
    def test_courses_endpoint(self):
        """Verify courses endpoint works"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Courses endpoint: {len(data)} courses")
    
    def test_offers_endpoint(self):
        """Verify offers endpoint works"""
        response = requests.get(f"{BASE_URL}/api/offers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Offers endpoint: {len(data)} offers")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
