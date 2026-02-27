"""
Afroboost API Tests - Testing all CRUD operations and features
Tests: Courses, Offers, Users, Reservations, Discount Codes, Payment Links, Concept, Coach Auth
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

@pytest.fixture(scope="session")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestHealthAndRoot:
    """Basic API health checks"""
    
    def test_api_root(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Afroboost API"


class TestCourses:
    """Course CRUD operations"""
    
    def test_get_courses(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have default courses
        if len(data) > 0:
            assert "id" in data[0]
            assert "name" in data[0]
            assert "weekday" in data[0]
            assert "time" in data[0]
    
    def test_create_course(self, api_client):
        course_data = {
            "name": "TEST_Course_" + str(uuid.uuid4())[:6],
            "weekday": 1,
            "time": "19:00",
            "locationName": "Test Location",
            "mapsUrl": "https://maps.google.com/test"
        }
        response = api_client.post(f"{BASE_URL}/api/courses", json=course_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == course_data["name"]
        assert data["weekday"] == 1
        assert "id" in data
        
        # Cleanup
        api_client.delete(f"{BASE_URL}/api/courses/{data['id']}")


class TestOffers:
    """Offer CRUD operations with description field"""
    
    def test_get_offers(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/offers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "id" in data[0]
            assert "name" in data[0]
            assert "price" in data[0]
    
    def test_create_offer_with_description(self, api_client):
        """Test creating offer with description field for info icon tooltip"""
        offer_data = {
            "name": "TEST_Offer_" + str(uuid.uuid4())[:6],
            "price": 50.0,
            "thumbnail": "https://example.com/image.jpg",
            "description": "Test description for info icon tooltip (max 150 chars)",
            "visible": True
        }
        response = api_client.post(f"{BASE_URL}/api/offers", json=offer_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == offer_data["name"]
        assert data["price"] == 50.0
        assert data["description"] == offer_data["description"]
        assert "id" in data
        
        # Cleanup
        api_client.delete(f"{BASE_URL}/api/offers/{data['id']}")
    
    def test_update_offer_description(self, api_client):
        """Test updating offer description"""
        # Create offer first
        offer_data = {
            "name": "TEST_UpdateOffer_" + str(uuid.uuid4())[:6],
            "price": 30.0,
            "description": "Initial description",
            "visible": True
        }
        create_response = api_client.post(f"{BASE_URL}/api/offers", json=offer_data)
        assert create_response.status_code == 200
        offer_id = create_response.json()["id"]
        
        # Update description
        update_data = {
            "name": offer_data["name"],
            "price": 30.0,
            "description": "Updated description for tooltip",
            "visible": True
        }
        update_response = api_client.put(f"{BASE_URL}/api/offers/{offer_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["description"] == "Updated description for tooltip"
        
        # Cleanup
        api_client.delete(f"{BASE_URL}/api/offers/{offer_id}")


class TestUsers:
    """User CRUD operations"""
    
    def test_get_users(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/users")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_user(self, api_client):
        user_data = {
            "name": "TEST_User_" + str(uuid.uuid4())[:6],
            "email": f"test_{uuid.uuid4().hex[:6]}@example.com",
            "whatsapp": "+41791234567"
        }
        response = api_client.post(f"{BASE_URL}/api/users", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == user_data["name"]
        assert data["email"] == user_data["email"]


class TestDiscountCodes:
    """Discount code CRUD and validation - including delete functionality"""
    
    def test_get_discount_codes(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/discount-codes")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_discount_code(self, api_client):
        code_data = {
            "code": "TEST_CODE_" + str(uuid.uuid4())[:4].upper(),
            "type": "%",
            "value": 20.0,
            "assignedEmail": None,
            "courses": [],
            "maxUses": 10
        }
        response = api_client.post(f"{BASE_URL}/api/discount-codes", json=code_data)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == code_data["code"]
        assert data["type"] == "%"
        assert data["value"] == 20.0
        assert "id" in data
        
        # Cleanup
        api_client.delete(f"{BASE_URL}/api/discount-codes/{data['id']}")
    
    def test_create_100_percent_discount_code(self, api_client):
        """Test creating 100% free discount code"""
        code_data = {
            "code": "TEST_FREE_" + str(uuid.uuid4())[:4].upper(),
            "type": "100%",
            "value": 100.0,
            "assignedEmail": None,
            "courses": [],
            "maxUses": 5
        }
        response = api_client.post(f"{BASE_URL}/api/discount-codes", json=code_data)
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "100%"
        
        # Cleanup
        api_client.delete(f"{BASE_URL}/api/discount-codes/{data['id']}")
    
    def test_delete_discount_code(self, api_client):
        """Test delete discount code functionality (red trash button)"""
        # Create a code first
        code_data = {
            "code": "TEST_DELETE_" + str(uuid.uuid4())[:4].upper(),
            "type": "CHF",
            "value": 10.0,
            "courses": []
        }
        create_response = api_client.post(f"{BASE_URL}/api/discount-codes", json=code_data)
        assert create_response.status_code == 200
        code_id = create_response.json()["id"]
        
        # Delete the code
        delete_response = api_client.delete(f"{BASE_URL}/api/discount-codes/{code_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["success"] == True
        
        # Verify it's deleted
        all_codes = api_client.get(f"{BASE_URL}/api/discount-codes").json()
        assert not any(c["id"] == code_id for c in all_codes)
    
    def test_validate_discount_code(self, api_client):
        """Test discount code validation endpoint"""
        # Create a code first
        code_data = {
            "code": "TEST_VALID_" + str(uuid.uuid4())[:4].upper(),
            "type": "%",
            "value": 15.0,
            "courses": []
        }
        create_response = api_client.post(f"{BASE_URL}/api/discount-codes", json=code_data)
        code_id = create_response.json()["id"]
        
        # Validate the code
        validate_response = api_client.post(f"{BASE_URL}/api/discount-codes/validate", json={
            "code": code_data["code"],
            "email": "test@example.com",
            "courseId": ""
        })
        assert validate_response.status_code == 200
        data = validate_response.json()
        assert data["valid"] == True
        
        # Cleanup
        api_client.delete(f"{BASE_URL}/api/discount-codes/{code_id}")
    
    def test_use_discount_code(self, api_client):
        """Test incrementing usage count"""
        # Create a code first
        code_data = {
            "code": "TEST_USE_" + str(uuid.uuid4())[:4].upper(),
            "type": "%",
            "value": 10.0,
            "courses": []
        }
        create_response = api_client.post(f"{BASE_URL}/api/discount-codes", json=code_data)
        code_id = create_response.json()["id"]
        
        # Use the code
        use_response = api_client.post(f"{BASE_URL}/api/discount-codes/{code_id}/use")
        assert use_response.status_code == 200
        
        # Cleanup
        api_client.delete(f"{BASE_URL}/api/discount-codes/{code_id}")


class TestConcept:
    """Concept configuration with logoUrl for Splash Screen & PWA"""
    
    def test_get_concept(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/concept")
        assert response.status_code == 200
        data = response.json()
        assert "description" in data
        assert "heroImageUrl" in data
        assert "logoUrl" in data  # New field for Splash Screen & PWA
    
    def test_update_concept_with_logo_url(self, api_client):
        """Test updating concept with logoUrl for Splash Screen"""
        update_data = {
            "description": "Test concept description",
            "heroImageUrl": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "logoUrl": "https://example.com/logo.png"
        }
        response = api_client.put(f"{BASE_URL}/api/concept", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["logoUrl"] == "https://example.com/logo.png"
        
        # Verify persistence
        get_response = api_client.get(f"{BASE_URL}/api/concept")
        assert get_response.json()["logoUrl"] == "https://example.com/logo.png"


class TestPaymentLinks:
    """Payment links configuration"""
    
    def test_get_payment_links(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/payment-links")
        assert response.status_code == 200
        data = response.json()
        assert "stripe" in data
        assert "paypal" in data
        assert "twint" in data
        assert "coachWhatsapp" in data
    
    def test_update_payment_links(self, api_client):
        update_data = {
            "stripe": "https://buy.stripe.com/test",
            "paypal": "https://paypal.me/test",
            "twint": "https://twint.ch/test",
            "coachWhatsapp": "+41791234567"
        }
        response = api_client.put(f"{BASE_URL}/api/payment-links", json=update_data)
        assert response.status_code == 200


class TestCoachAuth:
    """Coach authentication"""
    
    def test_coach_login_success(self, api_client):
        """Test coach login with correct credentials"""
        login_data = {
            "email": "coach@afroboost.com",
            "password": "afroboost123"
        }
        response = api_client.post(f"{BASE_URL}/api/coach-auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
    
    def test_coach_login_failure(self, api_client):
        """Test coach login with wrong credentials"""
        login_data = {
            "email": "wrong@email.com",
            "password": "wrongpassword"
        }
        response = api_client.post(f"{BASE_URL}/api/coach-auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False


class TestReservations:
    """Reservation CRUD operations"""
    
    def test_get_reservations(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/reservations")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_reservation(self, api_client):
        """Test creating a full reservation"""
        reservation_data = {
            "userId": "test-user-id",
            "userName": "TEST_User",
            "userEmail": "test@example.com",
            "userWhatsapp": "+41791234567",
            "courseId": "test-course-id",
            "courseName": "Test Course",
            "courseTime": "18:30",
            "datetime": "2025-01-15T18:30:00.000Z",
            "offerId": "test-offer-id",
            "offerName": "Test Offer",
            "price": 30.0,
            "quantity": 1,
            "totalPrice": 30.0,
            "discountCode": None,
            "discountType": None,
            "discountValue": None
        }
        response = api_client.post(f"{BASE_URL}/api/reservations", json=reservation_data)
        assert response.status_code == 200
        data = response.json()
        assert "reservationCode" in data
        assert data["reservationCode"].startswith("AFR-")
        assert data["userName"] == "TEST_User"
        
        # Cleanup
        api_client.delete(f"{BASE_URL}/api/reservations/{data['id']}")


class TestConfig:
    """App configuration"""
    
    def test_get_config(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/config")
        assert response.status_code == 200
        data = response.json()
        assert "app_title" in data
        assert data["app_title"] == "Afroboost"
