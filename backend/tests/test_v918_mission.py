"""
Test Suite for Mission v9.1.8 - Miroir Absolu et Propulsion Réel pour Afroboost

Tests:
1. API /api/coach/vitrine/:username - Vitrine publique coach
2. API /api/partner/vitrine/:username - Vitrine publique partner (alias)
3. Platform name 'Afroboost' verification
4. Sessions Cardio mars (Wednesday) preservation
5. Sunday Vibes (Sunday) preservation
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestVitrineAPIs:
    """Test vitrine APIs for coach and partner routes"""
    
    def test_health_check(self):
        """Test API health"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Health check passed")
    
    def test_coach_vitrine_bassi(self):
        """Test GET /api/coach/vitrine/bassi returns vitrine data"""
        response = requests.get(f"{BASE_URL}/api/coach/vitrine/bassi")
        assert response.status_code == 200
        data = response.json()
        
        # Verify coach data
        assert "coach" in data
        coach = data["coach"]
        assert coach["id"] == "bassi"
        assert coach["name"] == "Bassi - Afroboost"
        assert coach["platform_name"] == "Afroboost"  # Key requirement
        assert coach["email"] == "contact.artboost@gmail.com"
        print(f"✅ Coach vitrine /coach/bassi: platform_name={coach['platform_name']}")
        
        # Verify offers
        assert "offers" in data
        assert len(data["offers"]) >= 1
        print(f"✅ Offers count: {len(data['offers'])}")
        
        # Verify courses
        assert "courses" in data
        assert len(data["courses"]) >= 2
        print(f"✅ Courses count: {len(data['courses'])}")
        
    def test_partner_vitrine_bassi(self):
        """Test GET /api/partner/vitrine/bassi returns same vitrine data (alias route)"""
        response = requests.get(f"{BASE_URL}/api/partner/vitrine/bassi")
        assert response.status_code == 200
        data = response.json()
        
        # Verify partner route works as alias for coach
        assert "coach" in data
        coach = data["coach"]
        assert coach["id"] == "bassi"
        assert coach["platform_name"] == "Afroboost"
        print(f"✅ Partner vitrine /partner/bassi: platform_name={coach['platform_name']}")
        
    def test_vitrine_consistency(self):
        """Verify /coach/vitrine/bassi and /partner/vitrine/bassi return identical data"""
        resp_coach = requests.get(f"{BASE_URL}/api/coach/vitrine/bassi")
        resp_partner = requests.get(f"{BASE_URL}/api/partner/vitrine/bassi")
        
        assert resp_coach.status_code == 200
        assert resp_partner.status_code == 200
        
        data_coach = resp_coach.json()
        data_partner = resp_partner.json()
        
        # Verify data is identical
        assert data_coach["coach"]["id"] == data_partner["coach"]["id"]
        assert data_coach["coach"]["platform_name"] == data_partner["coach"]["platform_name"]
        assert len(data_coach["offers"]) == len(data_partner["offers"])
        assert len(data_coach["courses"]) == len(data_partner["courses"])
        print("✅ Coach and Partner vitrine routes return identical data")


class TestCardioSessionsMars:
    """Test sessions Cardio mars are preserved (04.03, 11.03, 18.03, 25.03)"""
    
    def test_cardio_session_exists(self):
        """Verify Session Cardio exists with weekday=3 (Wednesday)"""
        response = requests.get(f"{BASE_URL}/api/coach/vitrine/bassi")
        assert response.status_code == 200
        data = response.json()
        
        courses = data["courses"]
        cardio_session = next((c for c in courses if "Cardio" in c.get("name", "")), None)
        
        assert cardio_session is not None, "Session Cardio not found"
        assert cardio_session["weekday"] == 3, f"Session Cardio should be on Wednesday (3), got {cardio_session['weekday']}"
        assert cardio_session["time"] == "18:30", f"Session Cardio time should be 18:30, got {cardio_session['time']}"
        print(f"✅ Session Cardio: weekday={cardio_session['weekday']} (Wednesday), time={cardio_session['time']}")


class TestSundayVibes:
    """Test Sunday Vibes sessions preserved (01.03, 08.03, 15.03, 22.03)"""
    
    def test_sunday_vibes_exists(self):
        """Verify Sunday Vibes exists with weekday=0 (Sunday)"""
        response = requests.get(f"{BASE_URL}/api/coach/vitrine/bassi")
        assert response.status_code == 200
        data = response.json()
        
        courses = data["courses"]
        sunday_vibes = next((c for c in courses if "Sunday" in c.get("name", "") or "Vibes" in c.get("name", "")), None)
        
        assert sunday_vibes is not None, "Sunday Vibes not found"
        assert sunday_vibes["weekday"] == 0, f"Sunday Vibes should be on Sunday (0), got {sunday_vibes['weekday']}"
        assert sunday_vibes["time"] == "18:30", f"Sunday Vibes time should be 18:30, got {sunday_vibes['time']}"
        print(f"✅ Sunday Vibes: weekday={sunday_vibes['weekday']} (Sunday), time={sunday_vibes['time']}")


class TestPlatformName:
    """Test platform_name 'Afroboost' is correctly set"""
    
    def test_platform_name_afroboost(self):
        """Verify platform_name is 'Afroboost' for bassi vitrine"""
        response = requests.get(f"{BASE_URL}/api/coach/vitrine/bassi")
        assert response.status_code == 200
        data = response.json()
        
        platform_name = data["coach"].get("platform_name")
        assert platform_name == "Afroboost", f"platform_name should be 'Afroboost', got '{platform_name}'"
        print(f"✅ Platform name verified: {platform_name}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
