"""
Test suite for visibility regression fix
Tests that offers/courses with visible=false are properly filtered
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestVisibilityFiltering:
    """Tests for the visibility filtering regression fix"""
    
    def test_api_health(self):
        """Test API is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✅ API health check passed")
    
    def test_get_offers_returns_all(self):
        """Test that /api/offers returns all offers (including hidden ones)"""
        response = requests.get(f"{BASE_URL}/api/offers")
        assert response.status_code == 200
        offers = response.json()
        assert isinstance(offers, list)
        assert len(offers) > 0
        print(f"✅ Got {len(offers)} offers from API")
        
        # Check that we have both visible and hidden offers
        visible_offers = [o for o in offers if o.get('visible') == True]
        hidden_offers = [o for o in offers if o.get('visible') == False]
        
        print(f"   Visible offers: {len(visible_offers)}")
        print(f"   Hidden offers: {len(hidden_offers)}")
        
        # Verify specific offers exist
        offer_names = [o.get('name') for o in offers]
        assert "Cours à l'unité" in offer_names, "Expected 'Cours à l'unité' in offers"
        assert "TESTORRR" in offer_names, "Expected 'TESTORRR' in offers"
        assert "shoes" in offer_names, "Expected 'shoes' in offers"
        assert "pappa" in offer_names, "Expected 'pappa' in offers"
    
    def test_cours_unite_is_hidden(self):
        """Test that 'Cours à l'unité' has visible=false"""
        response = requests.get(f"{BASE_URL}/api/offers")
        assert response.status_code == 200
        offers = response.json()
        
        cours_unite = next((o for o in offers if o.get('name') == "Cours à l'unité"), None)
        assert cours_unite is not None, "'Cours à l'unité' not found"
        assert cours_unite.get('visible') == False, "'Cours à l'unité' should have visible=false"
        print("✅ 'Cours à l'unité' correctly has visible=false")
    
    def test_testorrr_is_visible(self):
        """Test that 'TESTORRR' has visible=true"""
        response = requests.get(f"{BASE_URL}/api/offers")
        assert response.status_code == 200
        offers = response.json()
        
        testorrr = next((o for o in offers if o.get('name') == "TESTORRR"), None)
        assert testorrr is not None, "'TESTORRR' not found"
        assert testorrr.get('visible') == True, "'TESTORRR' should have visible=true"
        assert testorrr.get('isProduct') == False, "'TESTORRR' should be a service (isProduct=false)"
        print("✅ 'TESTORRR' correctly has visible=true and isProduct=false")
    
    def test_products_are_visible(self):
        """Test that products (shoes, pappa) have visible=true"""
        response = requests.get(f"{BASE_URL}/api/offers")
        assert response.status_code == 200
        offers = response.json()
        
        shoes = next((o for o in offers if o.get('name') == "shoes"), None)
        assert shoes is not None, "'shoes' not found"
        assert shoes.get('visible') == True, "'shoes' should have visible=true"
        assert shoes.get('isProduct') == True, "'shoes' should be a product"
        print("✅ 'shoes' correctly has visible=true and isProduct=true")
        
        pappa = next((o for o in offers if o.get('name') == "pappa"), None)
        assert pappa is not None, "'pappa' not found"
        assert pappa.get('visible') == True, "'pappa' should have visible=true"
        assert pappa.get('isProduct') == True, "'pappa' should be a product"
        print("✅ 'pappa' correctly has visible=true and isProduct=true")


class TestCoursesVisibility:
    """Tests for courses visibility filtering"""
    
    def test_get_courses(self):
        """Test that /api/courses returns courses"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        courses = response.json()
        assert isinstance(courses, list)
        assert len(courses) > 0
        print(f"✅ Got {len(courses)} courses from API")
    
    def test_visible_courses(self):
        """Test that visible courses exist"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        courses = response.json()
        
        visible_courses = [c for c in courses if c.get('visible') == True and c.get('archived') != True]
        print(f"✅ Found {len(visible_courses)} visible non-archived courses")
        
        # Check for expected visible courses
        course_names = [c.get('name') for c in visible_courses]
        assert any("Session Cardio" in name for name in course_names), "Expected 'Session Cardio' course"
        assert any("Sunday Vibes" in name for name in course_names), "Expected 'Sunday Vibes' course"
    
    def test_hidden_course_exists(self):
        """Test that hidden course (copie) has visible=false"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        courses = response.json()
        
        copie_course = next((c for c in courses if "copie" in c.get('name', '')), None)
        if copie_course:
            assert copie_course.get('visible') == False, "'copie' course should have visible=false"
            print("✅ 'copie' course correctly has visible=false")
        else:
            print("⚠️ 'copie' course not found (may have been deleted)")
    
    def test_archived_course_exists(self):
        """Test that archived course (hello) has archived=true"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        courses = response.json()
        
        hello_course = next((c for c in courses if c.get('name') == "hello"), None)
        if hello_course:
            assert hello_course.get('archived') == True, "'hello' course should have archived=true"
            print("✅ 'hello' course correctly has archived=true")
        else:
            print("⚠️ 'hello' course not found (may have been deleted)")


class TestManifestJson:
    """Tests for dynamic manifest.json endpoint"""
    
    def test_manifest_endpoint(self):
        """Test that /api/manifest.json returns valid manifest"""
        response = requests.get(f"{BASE_URL}/api/manifest.json")
        assert response.status_code == 200
        manifest = response.json()
        
        assert "short_name" in manifest
        assert "name" in manifest
        assert "icons" in manifest
        print(f"✅ Manifest endpoint returns valid JSON")
        print(f"   short_name: {manifest.get('short_name')}")
        print(f"   name: {manifest.get('name')}")
    
    def test_manifest_uses_appname(self):
        """Test that manifest uses appName from concept"""
        # First get the concept
        concept_response = requests.get(f"{BASE_URL}/api/concept")
        assert concept_response.status_code == 200
        concept = concept_response.json()
        app_name = concept.get('appName', 'Afroboost')
        
        # Then check manifest
        manifest_response = requests.get(f"{BASE_URL}/api/manifest.json")
        assert manifest_response.status_code == 200
        manifest = manifest_response.json()
        
        assert manifest.get('short_name') == app_name, f"Manifest short_name should be '{app_name}'"
        assert app_name in manifest.get('name', ''), f"Manifest name should contain '{app_name}'"
        print(f"✅ Manifest correctly uses appName: '{app_name}'")
    
    def test_manifest_has_icons(self):
        """Test that manifest has icon configuration"""
        response = requests.get(f"{BASE_URL}/api/manifest.json")
        assert response.status_code == 200
        manifest = response.json()
        
        icons = manifest.get('icons', [])
        assert len(icons) > 0, "Manifest should have at least one icon"
        print(f"✅ Manifest has {len(icons)} icons configured")


class TestConceptEndpoint:
    """Tests for concept endpoint"""
    
    def test_get_concept(self):
        """Test that /api/concept returns concept data"""
        response = requests.get(f"{BASE_URL}/api/concept")
        assert response.status_code == 200
        concept = response.json()
        
        assert "appName" in concept
        assert "description" in concept
        assert "logoUrl" in concept
        print(f"✅ Concept endpoint returns valid data")
        print(f"   appName: {concept.get('appName')}")
    
    def test_concept_has_appname(self):
        """Test that concept has appName field"""
        response = requests.get(f"{BASE_URL}/api/concept")
        assert response.status_code == 200
        concept = response.json()
        
        app_name = concept.get('appName')
        assert app_name is not None, "Concept should have appName"
        assert len(app_name) > 0, "appName should not be empty"
        print(f"✅ Concept has appName: '{app_name}'")
    
    def test_concept_has_logourl(self):
        """Test that concept has logoUrl field"""
        response = requests.get(f"{BASE_URL}/api/concept")
        assert response.status_code == 200
        concept = response.json()
        
        logo_url = concept.get('logoUrl')
        assert logo_url is not None, "Concept should have logoUrl"
        print(f"✅ Concept has logoUrl configured: {len(logo_url) > 0}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
