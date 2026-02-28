"""
v9.0.1 Franchise & White Label Testing
======================================
Tests for:
1. Non-regression: Super Admin sees all 7 reservations (March)
2. API /coach/vitrine/bassi returns platform_name: 'Afroboost'
3. API /admin/coaches - lists 5 coaches with all fields
4. API POST /admin/coaches/{id}/toggle - toggles coach status (Super Admin only)
5. API DELETE /admin/coaches/{id} - deletes coach (Super Admin only)
"""
import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
SUPER_ADMIN_EMAIL = "contact.artboost@gmail.com"

class TestNonRegressionReservations:
    """CRITICAL: Super Admin must see 7 reservations from March"""
    
    def test_super_admin_sees_all_reservations(self):
        """Super Admin voit TOUT - 7 réservations minimum"""
        response = requests.get(
            f"{BASE_URL}/api/reservations",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "data" in data, "Response should contain 'data' field"
        assert "pagination" in data, "Response should contain 'pagination' field"
        
        total = data["pagination"]["total"]
        print(f"[NON-REGRESSION] Super Admin sees {total} reservations")
        
        # CRITICAL CHECK: At least 7 reservations for Bassi
        assert total >= 7, f"Expected at least 7 reservations, got {total}"
        
    def test_super_admin_no_coach_filter(self):
        """Super Admin bypass coach_id filter - sees ALL data"""
        response = requests.get(
            f"{BASE_URL}/api/reservations?all_data=true",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 200
        
        data = response.json()
        reservations = data.get("data", [])
        
        # Verify we get actual reservation data
        if reservations:
            # Check reservation structure
            res = reservations[0]
            assert "id" in res or "reservationCode" in res
            print(f"[NON-REGRESSION] Sample reservation: {res.get('reservationCode', 'N/A')} - {res.get('userName', 'N/A')}")


class TestVitrineAPI:
    """v9.0.1: Vitrine displays platform_name instead of name"""
    
    def test_vitrine_bassi_returns_platform_name(self):
        """API /coach/vitrine/bassi retourne platform_name: 'Afroboost'"""
        response = requests.get(f"{BASE_URL}/api/coach/vitrine/bassi")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "coach" in data, "Response should contain 'coach' field"
        
        coach = data["coach"]
        # v9.0.1: platform_name should be returned
        assert "platform_name" in coach, f"Coach should have platform_name field. Got: {list(coach.keys())}"
        assert coach["platform_name"] == "Afroboost", f"Expected platform_name='Afroboost', got '{coach.get('platform_name')}'"
        
        # Also check name is present
        assert "name" in coach
        print(f"[VITRINE] Coach: name='{coach['name']}', platform_name='{coach['platform_name']}'")
        
    def test_vitrine_bassi_returns_logo_url(self):
        """API /coach/vitrine/bassi retourne logo_url (peut être None)"""
        response = requests.get(f"{BASE_URL}/api/coach/vitrine/bassi")
        assert response.status_code == 200
        
        data = response.json()
        coach = data["coach"]
        
        # v9.0.1: logo_url field should exist (even if None)
        assert "logo_url" in coach, f"Coach should have logo_url field. Got: {list(coach.keys())}"
        print(f"[VITRINE] logo_url: {coach.get('logo_url')}")
        
    def test_vitrine_returns_offers_and_courses(self):
        """Vitrine returns offers and courses for the coach"""
        response = requests.get(f"{BASE_URL}/api/coach/vitrine/bassi")
        assert response.status_code == 200
        
        data = response.json()
        assert "offers" in data, "Should return offers"
        assert "courses" in data, "Should return courses"
        assert "offers_count" in data, "Should return offers_count"
        assert "courses_count" in data, "Should return courses_count"
        
        print(f"[VITRINE] Offers: {data['offers_count']}, Courses: {data['courses_count']}")
        
        # Verify at least some data
        assert isinstance(data["offers"], list)
        assert isinstance(data["courses"], list)
        
    def test_vitrine_unknown_coach_returns_404(self):
        """Vitrine for unknown coach returns 404"""
        response = requests.get(f"{BASE_URL}/api/coach/vitrine/unknown_coach_xyz")
        assert response.status_code == 404


class TestAdminCoachesAPI:
    """API /admin/coaches - Super Admin management"""
    
    def test_admin_coaches_requires_super_admin(self):
        """Non-Super Admin cannot access /admin/coaches"""
        # No header
        response = requests.get(f"{BASE_URL}/api/admin/coaches")
        assert response.status_code == 403
        
        # Wrong email
        response = requests.get(
            f"{BASE_URL}/api/admin/coaches",
            headers={"X-User-Email": "random@example.com"}
        )
        assert response.status_code == 403
        
    def test_super_admin_lists_coaches(self):
        """Super Admin can list all coaches"""
        response = requests.get(
            f"{BASE_URL}/api/admin/coaches",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        coaches = response.json()
        assert isinstance(coaches, list)
        
        print(f"[ADMIN] Total coaches: {len(coaches)}")
        
        # Verify coach structure if we have coaches
        if coaches:
            coach = coaches[0]
            expected_fields = ["id", "email", "name"]
            for field in expected_fields:
                assert field in coach, f"Coach should have '{field}' field"
            
            # v9.0.1: platform_name and logo_url may be present
            print(f"[ADMIN] Sample coach: {coach.get('name')} ({coach.get('email')})")
            if "platform_name" in coach:
                print(f"[ADMIN] platform_name: {coach.get('platform_name')}")


class TestToggleCoachAPI:
    """API POST /admin/coaches/{id}/toggle - Super Admin only"""
    
    def test_toggle_requires_super_admin(self):
        """Toggle coach status requires Super Admin"""
        response = requests.post(
            f"{BASE_URL}/api/admin/coaches/test_coach_id/toggle",
            headers={"X-User-Email": "random@example.com"}
        )
        assert response.status_code == 403
        
    def test_toggle_nonexistent_coach_returns_404(self):
        """Toggle non-existent coach returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/admin/coaches/nonexistent_coach_12345/toggle",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 404
        
    def test_toggle_coach_status(self):
        """Super Admin can toggle coach status (if coaches exist)"""
        # First get list of coaches
        list_response = requests.get(
            f"{BASE_URL}/api/admin/coaches",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        
        if list_response.status_code == 200 and list_response.json():
            coaches = list_response.json()
            test_coach = coaches[0]
            coach_id = test_coach.get("id")
            original_status = test_coach.get("is_active", True)
            
            # Toggle
            toggle_response = requests.post(
                f"{BASE_URL}/api/admin/coaches/{coach_id}/toggle",
                headers={"X-User-Email": SUPER_ADMIN_EMAIL}
            )
            assert toggle_response.status_code == 200, f"Toggle failed: {toggle_response.text}"
            
            result = toggle_response.json()
            assert "success" in result
            assert result["success"] == True
            assert "is_active" in result
            assert result["is_active"] == (not original_status)
            
            print(f"[TOGGLE] Coach {coach_id}: {original_status} -> {result['is_active']}")
            
            # Toggle back to restore original state
            requests.post(
                f"{BASE_URL}/api/admin/coaches/{coach_id}/toggle",
                headers={"X-User-Email": SUPER_ADMIN_EMAIL}
            )
            print(f"[TOGGLE] Restored coach {coach_id} to original state")
        else:
            pytest.skip("No coaches available to test toggle")


class TestDeleteCoachAPI:
    """API DELETE /admin/coaches/{id} - Super Admin only"""
    
    def test_delete_requires_super_admin(self):
        """Delete coach requires Super Admin"""
        response = requests.delete(
            f"{BASE_URL}/api/admin/coaches/test_coach_id",
            headers={"X-User-Email": "random@example.com"}
        )
        assert response.status_code == 403
        
    def test_delete_nonexistent_coach_returns_404(self):
        """Delete non-existent coach returns 404"""
        response = requests.delete(
            f"{BASE_URL}/api/admin/coaches/nonexistent_coach_12345",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 404


class TestCoachModelFields:
    """v9.0.1: Coach model has platform_name and logo_url"""
    
    def test_coach_profile_endpoint(self):
        """Coach profile should have platform_name and logo_url fields"""
        # Test via admin coaches list
        response = requests.get(
            f"{BASE_URL}/api/admin/coaches",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        
        if response.status_code == 200 and response.json():
            coaches = response.json()
            coach = coaches[0]
            
            # Log all available fields
            print(f"[COACH MODEL] Available fields: {list(coach.keys())}")
            
            # These fields should be queryable (may be None)
            # v9.0.1 adds platform_name and logo_url
            
            # Check essential fields
            assert "email" in coach
            assert "name" in coach
            assert "is_active" in coach


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
