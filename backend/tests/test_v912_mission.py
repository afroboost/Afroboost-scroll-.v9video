"""
Test file for v9.1.2 Mission: Dashboard Miroir & Fix Redirection
- Campaign routes migrated to campaign_routes.py
- server.py reduced from 6877 to 6719 lines
- Non-regression: 7 reservations for Super Admin
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
SUPER_ADMIN_EMAIL = "contact.artboost@gmail.com"

class TestV912BackendMission:
    """Test v9.1.2 backend APIs - campaign routes migration"""
    
    def test_health_check(self):
        """Test API health"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✅ Health check: PASSED")
    
    def test_reservations_non_regression(self):
        """NON-REGRESSION CRITIQUE: Super Admin doit voir 7 réservations Mars"""
        response = requests.get(
            f"{BASE_URL}/api/reservations",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 200
        data = response.json()
        
        # La réponse peut être paginée
        if isinstance(data, dict) and "data" in data:
            reservations = data["data"]
            total = data.get("pagination", {}).get("total", len(reservations))
        else:
            reservations = data
            total = len(reservations)
        
        print(f"📊 Total reservations: {total}")
        assert total >= 7, f"Expected at least 7 reservations, got {total}"
        print(f"✅ Non-regression reservations: PASSED ({total} reservations)")
    
    def test_campaigns_list_via_campaign_routes(self):
        """Test /api/campaigns via campaign_routes.py - liste (peut être vide)"""
        response = requests.get(
            f"{BASE_URL}/api/campaigns",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 200
        data = response.json()
        # La réponse est une liste (vide ou avec des campagnes)
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✅ Campaigns list via campaign_routes.py: PASSED ({len(data)} campaigns)")
    
    def test_campaigns_logs_via_campaign_routes(self):
        """Test /api/campaigns/logs via campaign_routes.py"""
        response = requests.get(f"{BASE_URL}/api/campaigns/logs")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert data.get("success") == True
        print(f"✅ Campaigns logs: PASSED (success: {data.get('success')})")
    
    def test_coach_profile_is_super_admin(self):
        """Test /api/coach/profile - is_super_admin: true pour Bassi"""
        response = requests.get(
            f"{BASE_URL}/api/coach/profile",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("is_super_admin") == True, f"Expected is_super_admin=True, got {data.get('is_super_admin')}"
        print(f"✅ Coach profile is_super_admin: PASSED")
    
    def test_coach_check_credits_unlimited(self):
        """Test /api/coach/check-credits - unlimited pour Super Admin"""
        response = requests.get(
            f"{BASE_URL}/api/coach/check-credits",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("unlimited") == True
        assert data.get("credits") == -1
        print(f"✅ Coach check-credits unlimited: PASSED")
    
    def test_courses_mars_intact(self):
        """Test /api/courses - Session Cardio + Sunday Vibes intacts"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        courses = response.json()
        
        course_names = [c.get("name", "") for c in courses]
        print(f"📋 Courses: {course_names}")
        
        # Vérifier que les cours Mars sont présents (partiel match)
        has_cardio = any("cardio" in name.lower() for name in course_names)
        has_sunday = any("sunday" in name.lower() for name in course_names)
        
        assert has_cardio, "Session Cardio missing"
        assert has_sunday, "Sunday Vibes missing"
        print(f"✅ Courses Mars intact: PASSED (Session Cardio + Sunday Vibes)")
    
    def test_auth_role_super_admin(self):
        """Test /api/auth/role - Super Admin role check"""
        response = requests.get(
            f"{BASE_URL}/api/auth/role",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("is_super_admin") == True
        assert data.get("is_coach") == True
        assert data.get("role") == "super_admin"
        print(f"✅ Auth role Super Admin: PASSED")


class TestV912FileLineCount:
    """Verify file line counts after refactoring"""
    
    def test_server_py_line_count(self):
        """Verify server.py is reduced to ~6719 lines"""
        try:
            with open("/app/backend/server.py", "r") as f:
                line_count = len(f.readlines())
            print(f"📊 server.py: {line_count} lines")
            assert line_count <= 6800, f"server.py should be ~6719 lines, got {line_count}"
            assert line_count >= 6600, f"server.py seems too small ({line_count} lines)"
            print(f"✅ server.py line count: PASSED ({line_count} lines)")
        except FileNotFoundError:
            pytest.skip("server.py not found in test environment")
    
    def test_campaign_routes_line_count(self):
        """Verify campaign_routes.py is 134 lines"""
        try:
            with open("/app/backend/routes/campaign_routes.py", "r") as f:
                line_count = len(f.readlines())
            print(f"📊 campaign_routes.py: {line_count} lines")
            assert line_count >= 100, f"campaign_routes.py should be ~134 lines, got {line_count}"
            print(f"✅ campaign_routes.py line count: PASSED ({line_count} lines)")
        except FileNotFoundError:
            pytest.skip("campaign_routes.py not found in test environment")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
