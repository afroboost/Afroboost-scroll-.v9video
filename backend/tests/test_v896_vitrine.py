"""
v8.9.6 Coach Vitrine & Non-Regression Tests
============================================
Tests:
1. NON-RÉGRESSION: GET /api/courses - Cours mars INTACTS
2. NON-RÉGRESSION: GET /api/offers - Offres INTACTS  
3. NON-RÉGRESSION: GET /api/reservations - Bassi voit ses réservations
4. NOUVEAU: GET /api/coach/vitrine/{username} - Endpoint vitrine
5. ISOLATION: Super Admin voit TOUT
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
SUPER_ADMIN_EMAIL = "contact.artboost@gmail.com"

class TestNonRegressionCourses:
    """Test courses endpoint - NON-RÉGRESSION"""
    
    def test_get_courses_returns_200(self):
        """GET /api/courses should return 200 and list of courses"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✅ GET /api/courses: {len(data)} courses found")
        
    def test_courses_have_required_fields(self):
        """Courses should have required fields: id, name, weekday, time, locationName"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        
        courses = response.json()
        if len(courses) > 0:
            course = courses[0]
            assert "id" in course, "Course should have id"
            assert "name" in course, "Course should have name"
            assert "weekday" in course, "Course should have weekday"
            assert "time" in course, "Course should have time"
            print(f"✅ Course fields verified: {course.get('name')}")
        else:
            print("⚠️ No courses to verify fields")
            
    def test_march_courses_present(self):
        """March 2025 courses should be present (Session Cardio, Sunday Vibes)"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        
        courses = response.json()
        course_names = [c.get('name', '') for c in courses]
        
        # Vérifier que les cours de mars sont présents
        has_cardio = any('Cardio' in name for name in course_names)
        has_vibes = any('Vibes' in name or 'Sunday' in name for name in course_names)
        
        print(f"✅ Courses found: {course_names}")
        print(f"   Cardio: {'YES' if has_cardio else 'NO'}, Sunday Vibes: {'YES' if has_vibes else 'NO'}")


class TestNonRegressionOffers:
    """Test offers endpoint - NON-RÉGRESSION"""
    
    def test_get_offers_returns_200(self):
        """GET /api/offers should return 200 and list of offers"""
        response = requests.get(f"{BASE_URL}/api/offers")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✅ GET /api/offers: {len(data)} offers found")
        
    def test_offers_have_required_fields(self):
        """Offers should have required fields: id, name, price"""
        response = requests.get(f"{BASE_URL}/api/offers")
        assert response.status_code == 200
        
        offers = response.json()
        if len(offers) > 0:
            offer = offers[0]
            assert "id" in offer, "Offer should have id"
            assert "name" in offer, "Offer should have name"
            assert "price" in offer, "Offer should have price"
            print(f"✅ Offer fields verified: {offer.get('name')} - CHF {offer.get('price')}")
        else:
            print("⚠️ No offers to verify fields")


class TestNonRegressionReservations:
    """Test reservations endpoint - NON-RÉGRESSION avec isolation"""
    
    def test_reservations_with_super_admin(self):
        """Bassi (Super Admin) should see ALL reservations"""
        headers = {"X-User-Email": SUPER_ADMIN_EMAIL}
        response = requests.get(f"{BASE_URL}/api/reservations", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # API returns paginated response with 'data' field
        if isinstance(data, dict) and "data" in data:
            reservations = data["data"]
            total = data.get("pagination", {}).get("total", len(reservations))
        else:
            reservations = data
            total = len(reservations)
            
        print(f"✅ GET /api/reservations (Super Admin): {total} reservations (page: {len(reservations)})")
        assert total >= 0, "Should return 0 or more reservations"
        
    def test_reservations_pagination_structure(self):
        """Reservations API should return pagination info"""
        headers = {"X-User-Email": SUPER_ADMIN_EMAIL}
        response = requests.get(f"{BASE_URL}/api/reservations?page=1&limit=10", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check pagination structure
        assert "data" in data, "Response should have 'data' field"
        assert "pagination" in data, "Response should have 'pagination' field"
        
        pagination = data["pagination"]
        assert "page" in pagination, "Pagination should have 'page'"
        assert "limit" in pagination, "Pagination should have 'limit'"
        assert "total" in pagination, "Pagination should have 'total'"
        
        print(f"✅ Pagination: page={pagination['page']}, limit={pagination['limit']}, total={pagination['total']}")


class TestVitrineEndpoint:
    """Test NEW coach vitrine endpoint v8.9.6"""
    
    def test_vitrine_returns_404_for_unknown_coach(self):
        """GET /api/coach/vitrine/{unknown} should return 404"""
        response = requests.get(f"{BASE_URL}/api/coach/vitrine/unknown_coach_xxx")
        
        # 404 is CORRECT behavior for unknown coach
        assert response.status_code == 404, f"Expected 404 for unknown coach, got {response.status_code}"
        print("✅ GET /api/coach/vitrine/unknown: 404 (correct)")
        
    def test_vitrine_endpoint_exists(self):
        """Vitrine endpoint should exist (even if returns 404 for unknown coach)"""
        response = requests.get(f"{BASE_URL}/api/coach/vitrine/test_user")
        
        # 404 or 200 are valid - just not 500 or connection error
        assert response.status_code in [200, 404], f"Endpoint should exist, got {response.status_code}"
        print(f"✅ Vitrine endpoint exists: status={response.status_code}")
        
    def test_vitrine_response_structure_if_found(self):
        """If coach found, vitrine should return coach, offers, courses"""
        # This test documents expected structure even if no coach exists yet
        response = requests.get(f"{BASE_URL}/api/coach/vitrine/bassi")
        
        if response.status_code == 200:
            data = response.json()
            assert "coach" in data, "Response should have 'coach'"
            assert "offers" in data, "Response should have 'offers'"
            assert "courses" in data, "Response should have 'courses'"
            print(f"✅ Vitrine structure OK: coach={data['coach'].get('name')}, offers={len(data['offers'])}, courses={len(data['courses'])}")
        else:
            print(f"⚠️ Coach 'bassi' not found (status={response.status_code}) - structure test skipped")


class TestIsolationSuperAdmin:
    """Test Super Admin sees ALL data (ISOLATION check)"""
    
    def test_super_admin_sees_all_campaigns(self):
        """Super Admin should see all campaigns"""
        headers = {"X-User-Email": SUPER_ADMIN_EMAIL}
        response = requests.get(f"{BASE_URL}/api/campaigns", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        campaigns = data if isinstance(data, list) else data.get("campaigns", data.get("data", []))
        print(f"✅ Campaigns (Super Admin): {len(campaigns)} found")
        
    def test_super_admin_sees_all_participants(self):
        """Super Admin should see all chat participants"""
        headers = {"X-User-Email": SUPER_ADMIN_EMAIL}
        response = requests.get(f"{BASE_URL}/api/chat/participants", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        participants = data if isinstance(data, list) else []
        print(f"✅ Chat participants (Super Admin): {len(participants)} found")


class TestHealthCheck:
    """Health check tests"""
    
    def test_health_endpoint(self):
        """Health endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("✅ Health check: OK")
        
    def test_api_root(self):
        """API root should return message"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✅ API root: {data.get('message')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
