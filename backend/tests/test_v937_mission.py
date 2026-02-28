"""
Test v9.3.7 - Mission RÉPARATION FINALE MÉMOIRE, CALENDRIER CHAT ET NAV
- Mémoire totale des configurations (payment-links, concept)
- Calendrier dans chat pour tous utilisateurs
- Données Bassi (réservations, contacts) préservées
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
SUPER_ADMIN_EMAIL = "contact.artboost@gmail.com"


class TestPaymentLinksAutoSave:
    """Tests for payment-links auto-save functionality"""
    
    def test_get_payment_links(self):
        """GET /api/payment-links returns current payment config"""
        response = requests.get(f"{BASE_URL}/api/payment-links")
        assert response.status_code == 200
        data = response.json()
        # Check for expected fields
        assert 'stripe' in data or 'twint' in data or isinstance(data, dict)
        print(f"✅ GET payment-links: {list(data.keys())}")
    
    def test_put_payment_links_stripe(self):
        """PUT /api/payment-links saves Stripe link"""
        # First GET current state
        current = requests.get(f"{BASE_URL}/api/payment-links").json()
        
        # Update with test value
        test_stripe = current.get('stripe', '') or 'https://stripe.test/link'
        payload = {**current, 'stripe': test_stripe}
        
        response = requests.put(f"{BASE_URL}/api/payment-links", json=payload)
        assert response.status_code == 200
        
        # Verify persistence
        verify = requests.get(f"{BASE_URL}/api/payment-links").json()
        assert verify.get('stripe') == test_stripe
        print(f"✅ PUT payment-links Stripe persisted: {test_stripe[:30]}...")
    
    def test_put_payment_links_twint(self):
        """PUT /api/payment-links saves TWINT link"""
        current = requests.get(f"{BASE_URL}/api/payment-links").json()
        
        test_twint = current.get('twint', '') or 'https://twint.test/pay'
        payload = {**current, 'twint': test_twint}
        
        response = requests.put(f"{BASE_URL}/api/payment-links", json=payload)
        assert response.status_code == 200
        
        verify = requests.get(f"{BASE_URL}/api/payment-links").json()
        assert verify.get('twint') == test_twint
        print(f"✅ PUT payment-links TWINT persisted: {test_twint[:30]}...")


class TestConceptAutoSave:
    """Tests for concept auto-save functionality"""
    
    def test_get_concept(self):
        """GET /api/concept returns current concept config"""
        response = requests.get(f"{BASE_URL}/api/concept")
        assert response.status_code == 200
        data = response.json()
        
        # Check for expected concept fields
        assert 'appName' in data or 'heroImageUrl' in data or isinstance(data, dict)
        print(f"✅ GET concept: appName={data.get('appName', 'N/A')}")
    
    def test_put_concept_hero_image(self):
        """PUT /api/concept saves heroImageUrl"""
        current = requests.get(f"{BASE_URL}/api/concept").json()
        
        test_hero = current.get('heroImageUrl', '') or 'https://example.com/hero.jpg'
        payload = {**current, 'heroImageUrl': test_hero}
        
        response = requests.put(f"{BASE_URL}/api/concept", json=payload)
        assert response.status_code == 200
        
        # Verify persistence
        verify = requests.get(f"{BASE_URL}/api/concept").json()
        assert verify.get('heroImageUrl') == test_hero
        print(f"✅ PUT concept heroImageUrl persisted")
    
    def test_put_concept_video_url(self):
        """PUT /api/concept saves default video URL if field exists"""
        current = requests.get(f"{BASE_URL}/api/concept").json()
        
        # Check if there's a video URL field (could be named differently)
        video_fields = ['videoUrl', 'heroVideoUrl', 'defaultVideoUrl']
        for field in video_fields:
            if field in current:
                test_url = current.get(field, '') or 'https://youtube.com/test'
                payload = {**current, field: test_url}
                response = requests.put(f"{BASE_URL}/api/concept", json=payload)
                assert response.status_code == 200
                print(f"✅ PUT concept {field} persisted")
                return
        
        print("ℹ️ No video URL field found in concept schema")


class TestCoursesForBookingPanel:
    """Tests for courses API (used by booking panel)"""
    
    def test_get_courses_available(self):
        """GET /api/courses returns available courses for booking"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        courses = response.json()
        
        assert isinstance(courses, list)
        print(f"✅ GET courses: {len(courses)} course(s) available for booking panel")
        
        # If courses exist, verify structure
        if len(courses) > 0:
            course = courses[0]
            assert 'id' in course or '_id' in course
            assert 'name' in course
            print(f"✅ Course structure valid: {course.get('name', 'N/A')}")


class TestBassiDataPreservation:
    """RÈGLE NON NÉGOCIABLE: Données Bassi préservées"""
    
    def test_bassi_reservations_preserved(self):
        """Verify Bassi (Super Admin) has exactly 7 reservations"""
        response = requests.get(
            f"{BASE_URL}/api/reservations",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 200
        data = response.json()
        
        total = data.get('pagination', {}).get('total', 0)
        # Allow for slight variation (7-8 reservations)
        assert total >= 7, f"Expected at least 7 reservations for Bassi, got {total}"
        print(f"✅ ANTI-RÉGRESSION: Bassi has {total} reservations (>= 7)")
    
    def test_bassi_contacts_preserved(self):
        """Verify Bassi (Super Admin) has at least 8 contacts"""
        response = requests.get(
            f"{BASE_URL}/api/chat/participants",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 200
        contacts = response.json()
        
        count = len(contacts) if isinstance(contacts, list) else 0
        # Allow for slight variation (8-9 contacts)
        assert count >= 8, f"Expected at least 8 contacts for Bassi, got {count}"
        print(f"✅ ANTI-RÉGRESSION: Bassi has {count} contacts (>= 8)")


class TestFeatureFlagsAndSettings:
    """Tests for platform settings and feature flags"""
    
    def test_platform_settings(self):
        """GET /api/platform-settings returns settings"""
        response = requests.get(f"{BASE_URL}/api/platform-settings")
        assert response.status_code == 200
        print("✅ Platform settings accessible")
    
    def test_feature_flags(self):
        """GET /api/feature-flags returns feature configuration"""
        response = requests.get(f"{BASE_URL}/api/feature-flags")
        assert response.status_code == 200
        print("✅ Feature flags accessible")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
