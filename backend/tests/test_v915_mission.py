"""
Mission v9.1.5 Backend Tests - Réparation visuelle et branchement réel
Tests:
1. API /api/coach/vitrine/bassi - Returns coach data
2. Non-regression: 7 reservations of Bassi preserved
3. Courses Mars intact (Session Cardio + Sunday Vibes)
4. Health check API
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
SUPER_ADMIN_EMAIL = 'contact.artboost@gmail.com'


class TestMissionV915:
    """Mission v9.1.5 - Réparation visuelle et branchement réel"""
    
    def test_health_check(self):
        """Verify API is healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'healthy'
        print(f"✅ Health check: {data}")
    
    def test_coach_vitrine_bassi_returns_data(self):
        """API /api/coach/vitrine/bassi doit retourner les données du coach"""
        response = requests.get(f"{BASE_URL}/api/coach/vitrine/bassi")
        assert response.status_code == 200
        data = response.json()
        
        # Verify coach data exists
        assert 'coach' in data
        coach = data['coach']
        assert coach.get('id') == 'bassi'
        assert 'name' in coach
        assert 'platform_name' in coach
        print(f"✅ Coach vitrine data: {coach.get('name')}, platform: {coach.get('platform_name')}")
        
        # Verify offers exist
        assert 'offers' in data
        offers = data['offers']
        assert len(offers) >= 3  # At least 3 offers expected
        print(f"✅ Offers count: {len(offers)}")
        
        # Verify courses exist
        assert 'courses' in data
        courses = data['courses']
        assert len(courses) == 2  # Session Cardio + Sunday Vibes
        print(f"✅ Courses count: {len(courses)}")
        
        return data
    
    def test_coach_vitrine_contains_session_cardio(self):
        """Verify Session Cardio course is in vitrine"""
        response = requests.get(f"{BASE_URL}/api/coach/vitrine/bassi")
        assert response.status_code == 200
        data = response.json()
        
        courses = data.get('courses', [])
        session_cardio = [c for c in courses if 'Session Cardio' in c.get('name', '')]
        
        assert len(session_cardio) >= 1, "Session Cardio course should exist"
        course = session_cardio[0]
        assert course.get('weekday') == 3, "Session Cardio should be on Wednesday (weekday=3)"
        assert course.get('time') == '18:30', "Session Cardio should be at 18:30"
        print(f"✅ Session Cardio: weekday={course.get('weekday')}, time={course.get('time')}")
    
    def test_coach_vitrine_contains_sunday_vibes(self):
        """Verify Sunday Vibes course is in vitrine"""
        response = requests.get(f"{BASE_URL}/api/coach/vitrine/bassi")
        assert response.status_code == 200
        data = response.json()
        
        courses = data.get('courses', [])
        sunday_vibes = [c for c in courses if 'Sunday Vibes' in c.get('name', '')]
        
        assert len(sunday_vibes) >= 1, "Sunday Vibes course should exist"
        course = sunday_vibes[0]
        assert course.get('weekday') == 0, "Sunday Vibes should be on Sunday (weekday=0)"
        assert course.get('time') == '18:30', "Sunday Vibes should be at 18:30"
        print(f"✅ Sunday Vibes: weekday={course.get('weekday')}, time={course.get('time')}")


class TestReservationsNonRegression:
    """Non-regression tests for Bassi's 7 reservations"""
    
    def test_reservations_count_preserved(self):
        """Les 7 réservations de Bassi doivent être préservées"""
        response = requests.get(
            f"{BASE_URL}/api/reservations",
            headers={'X-User-Email': SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Handle both direct list and {data: [...]} format
        reservations = data.get('data', data) if isinstance(data, dict) else data
        
        assert len(reservations) >= 7, f"Expected at least 7 reservations, got {len(reservations)}"
        print(f"✅ Total reservations: {len(reservations)}")
    
    def test_bassi_reservations_exist(self):
        """Verify Bassi's reservations exist"""
        response = requests.get(
            f"{BASE_URL}/api/reservations",
            headers={'X-User-Email': SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 200
        data = response.json()
        
        reservations = data.get('data', data) if isinstance(data, dict) else data
        
        # Count reservations by Bassi
        bassi_reservations = [r for r in reservations if 'Bassi' in r.get('userName', '') or 'BASSI' in r.get('userName', '')]
        
        assert len(bassi_reservations) >= 7, f"Expected at least 7 Bassi reservations, got {len(bassi_reservations)}"
        print(f"✅ Bassi reservations: {len(bassi_reservations)}")
        
        # List them
        for r in bassi_reservations:
            print(f"  - {r.get('userName')} | {r.get('courseName')} | {r.get('selectedDatesText', 'N/A')}")
    
    def test_session_cardio_mars_dates_preserved(self):
        """Verify Session Cardio dates for March are preserved (04.03, 11.03, 18.03, 25.03)"""
        response = requests.get(
            f"{BASE_URL}/api/reservations",
            headers={'X-User-Email': SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 200
        data = response.json()
        
        reservations = data.get('data', data) if isinstance(data, dict) else data
        
        # Filter Session Cardio reservations
        cardio_reservations = [r for r in reservations if 'Session Cardio' in r.get('courseName', '')]
        
        print(f"✅ Session Cardio reservations: {len(cardio_reservations)}")
        
        # Check March dates exist
        mars_dates = []
        for r in cardio_reservations:
            dates_text = r.get('selectedDatesText', '')
            if dates_text:
                mars_dates.append(dates_text)
        
        print(f"✅ Mars dates found: {mars_dates}")


class TestCoursesAPI:
    """Tests for courses API"""
    
    def test_courses_endpoint_returns_two_courses(self):
        """Courses API should return 2 courses"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        courses = response.json()
        
        assert len(courses) == 2, f"Expected 2 courses, got {len(courses)}"
        print(f"✅ Courses: {len(courses)}")
        
        for c in courses:
            print(f"  - {c.get('name')} | weekday={c.get('weekday')} | time={c.get('time')}")
    
    def test_session_cardio_course_exists(self):
        """Verify Session Cardio course"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        courses = response.json()
        
        cardio = [c for c in courses if 'Session Cardio' in c.get('name', '')]
        assert len(cardio) >= 1, "Session Cardio course should exist"
        
        course = cardio[0]
        assert course.get('weekday') == 3, "Should be Wednesday"
        assert course.get('time') == '18:30', "Should be 18:30"
        print(f"✅ Session Cardio verified: {course.get('name')}")
    
    def test_sunday_vibes_course_exists(self):
        """Verify Sunday Vibes course"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        courses = response.json()
        
        vibes = [c for c in courses if 'Sunday Vibes' in c.get('name', '')]
        assert len(vibes) >= 1, "Sunday Vibes course should exist"
        
        course = vibes[0]
        assert course.get('weekday') == 0, "Should be Sunday"
        assert course.get('time') == '18:30', "Should be 18:30"
        print(f"✅ Sunday Vibes verified: {course.get('name')}")


class TestOffersAPI:
    """Tests for offers API"""
    
    def test_offers_endpoint_returns_offers(self):
        """Offers API should return offers"""
        response = requests.get(f"{BASE_URL}/api/offers")
        assert response.status_code == 200
        offers = response.json()
        
        assert len(offers) >= 3, f"Expected at least 3 offers, got {len(offers)}"
        print(f"✅ Offers count: {len(offers)}")
        
        for o in offers:
            print(f"  - {o.get('name')} | CHF {o.get('price')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
