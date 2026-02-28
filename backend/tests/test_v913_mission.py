"""
Test Mission v9.1.3: Propulsion Dashboard & Miroir Visuel
- Propulsion automatique: #coach-dashboard ouvre modal connexion immédiatement
- Dashboard jumeau: Tous les coaches ont FULL ACCESS (plus de grisage d'onglets)
- Marque blanche: Header affiche platform_name ou 'Mon Espace Afroboost'
- NON-RÉGRESSION: 7 réservations Mars, cours Mars intacts
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
SUPER_ADMIN_EMAIL = "contact.artboost@gmail.com"

class TestV913NonRegression:
    """Non-regression tests - Critical features must still work"""
    
    def test_health_check(self):
        """Test API is running"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✅ Health check passed")
    
    def test_reservations_super_admin_7(self):
        """CRITICAL: Super Admin must see 7 reservations (non-regression)"""
        response = requests.get(
            f"{BASE_URL}/api/reservations",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check pagination structure
        assert "data" in data
        assert "pagination" in data
        
        total = data["pagination"].get("total", len(data["data"]))
        assert total >= 7, f"Expected at least 7 reservations, got {total}"
        print(f"✅ Super Admin sees {total} reservations (>=7 required)")
    
    def test_courses_mars_intact(self):
        """CRITICAL: Mars courses must be intact (Session Cardio + Sunday Vibes)"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        courses = response.json()
        
        assert len(courses) >= 2, f"Expected at least 2 courses, got {len(courses)}"
        
        course_names = [c.get("name", "") for c in courses]
        
        # Check Session Cardio (weekday 3 = Wednesday)
        cardio_course = next((c for c in courses if "Cardio" in c.get("name", "")), None)
        assert cardio_course is not None, "Session Cardio not found"
        assert cardio_course.get("weekday") == 3, "Session Cardio should be on Wednesday (3)"
        print(f"✅ Session Cardio found: weekday={cardio_course.get('weekday')}, time={cardio_course.get('time')}")
        
        # Check Sunday Vibes (weekday 0 = Sunday)
        vibes_course = next((c for c in courses if "Vibes" in c.get("name", "") or "Sunday" in c.get("name", "")), None)
        assert vibes_course is not None, "Sunday Vibes not found"
        assert vibes_course.get("weekday") == 0, "Sunday Vibes should be on Sunday (0)"
        print(f"✅ Sunday Vibes found: weekday={vibes_course.get('weekday')}, time={vibes_course.get('time')}")


class TestV913CoachProfile:
    """Test coach profile with marque blanche support"""
    
    def test_coach_profile_returns_data(self):
        """API /api/coach/profile should return coach data"""
        response = requests.get(
            f"{BASE_URL}/api/coach/profile",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Required fields
        assert "email" in data
        assert "is_super_admin" in data or "role" in data
        assert "credits" in data
        
        # Super Admin should have unlimited credits (-1)
        assert data.get("credits") == -1, "Super Admin should have unlimited credits (-1)"
        assert data.get("is_super_admin") == True, "Should be Super Admin"
        
        print(f"✅ Coach profile: email={data.get('email')}, credits={data.get('credits')}, is_super_admin={data.get('is_super_admin')}")
    
    def test_coach_profile_platform_name_field(self):
        """API should support platform_name for marque blanche"""
        response = requests.get(
            f"{BASE_URL}/api/coach/profile",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 200
        data = response.json()
        
        # platform_name is optional, but the API should work
        # If present, it should be a string
        platform_name = data.get("platform_name")
        if platform_name is not None:
            assert isinstance(platform_name, str), "platform_name should be a string"
            print(f"✅ platform_name found: '{platform_name}'")
        else:
            print("✅ platform_name not set (will use default 'Mon Espace Afroboost')")


class TestV913DashboardFeatures:
    """Test dashboard features - no grayed tabs, marque blanche"""
    
    def test_auth_role_super_admin(self):
        """API /api/auth/role should return super_admin for Bassi"""
        response = requests.get(
            f"{BASE_URL}/api/auth/role",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("role") == "super_admin", f"Expected super_admin, got {data.get('role')}"
        print(f"✅ Auth role: {data.get('role')}")
    
    def test_check_credits_unlimited(self):
        """API /api/coach/check-credits should return unlimited for Super Admin"""
        response = requests.get(
            f"{BASE_URL}/api/coach/check-credits",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Super Admin should have unlimited credits
        assert data.get("unlimited") == True or data.get("credits") == -1, "Super Admin should have unlimited credits"
        print(f"✅ Credits check: unlimited={data.get('unlimited')}, credits={data.get('credits')}")


class TestV913Offers:
    """Test offers are available"""
    
    def test_offers_list(self):
        """API /api/offers should return list of offers"""
        response = requests.get(f"{BASE_URL}/api/offers")
        assert response.status_code == 200
        offers = response.json()
        
        assert isinstance(offers, list), "Offers should be a list"
        print(f"✅ Found {len(offers)} offers")
        
        # Print offer names for verification
        for offer in offers[:5]:  # Limit to first 5
            print(f"   - {offer.get('name', 'Unknown')}: CHF {offer.get('price', 0)}")


class TestV913Concept:
    """Test concept configuration"""
    
    def test_concept_config(self):
        """API /api/concept should return configuration"""
        response = requests.get(f"{BASE_URL}/api/concept")
        assert response.status_code == 200
        data = response.json()
        
        # Should have basic fields
        assert isinstance(data, dict), "Concept should be a dict"
        print(f"✅ Concept loaded: appName={data.get('appName', 'N/A')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
