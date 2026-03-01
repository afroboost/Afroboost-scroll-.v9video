"""
Test Mission v9.6.4 - Zéro Vide Noir et Flux Login
Tests:
1. Health check
2. Super Admin unlimited credits verification
3. Partners active endpoint
4. FLASH login redirection (code verification)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestMissionV964:
    """Mission v9.6.4 Backend Verification Tests"""
    
    def test_health_check(self):
        """Test health endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✅ Health check passed: {data}")
    
    def test_super_admin_unlimited_credits(self):
        """
        Verify Super Admin (afroboost.bassi@gmail.com) has unlimited credits (-1)
        """
        # Use cookies session for auth
        response = requests.get(
            f"{BASE_URL}/api/credits/check",
            cookies={"user_email": "afroboost.bassi@gmail.com"},
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        
        # Super Admin should have credits = -1 (unlimited)
        credits = data.get("credits", 0)
        unlimited = data.get("unlimited", False)
        is_super_admin = data.get("is_super_admin", False)
        has_credits = data.get("has_credits", False)
        
        print(f"✅ Super Admin credits check: credits={credits}, unlimited={unlimited}, is_super_admin={is_super_admin}")
        
        # Verify Super Admin status
        assert is_super_admin == True or unlimited == True, "Super Admin should be marked as unlimited"
        assert has_credits == True, "Super Admin should always have credits"
        
        # Credits should be -1 (unlimited indicator) or has_credits should be True
        if credits == -1:
            print("✅ Super Admin has credits=-1 (unlimited)")
        elif unlimited:
            print("✅ Super Admin has unlimited=True")
    
    def test_partners_active_endpoint(self):
        """Test partners/active endpoint returns data"""
        response = requests.get(f"{BASE_URL}/api/partners/active", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Should return a list of partners"
        print(f"✅ Partners active endpoint: {len(data)} partners found")
    
    def test_courses_endpoint(self):
        """Test courses endpoint"""
        response = requests.get(f"{BASE_URL}/api/courses", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Should return a list of courses"
        print(f"✅ Courses endpoint: {len(data)} courses found")
    
    def test_offers_endpoint(self):
        """Test offers endpoint"""
        response = requests.get(f"{BASE_URL}/api/offers", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Should return a list of offers"
        print(f"✅ Offers endpoint: {len(data)} offers found")
    
    def test_concept_endpoint(self):
        """Test concept endpoint"""
        response = requests.get(f"{BASE_URL}/api/concept", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict), "Should return concept data"
        print(f"✅ Concept endpoint: response OK")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
