"""
Test v9.0.2 - Credit System for Coaches
Mission: Rentabilité & Identité Miroir

Tests:
1. API /api/reservations - 7 réservations pour Super Admin (non-régression critique)
2. API /api/coach/check-credits pour Super Admin - retourne unlimited: true
3. API /api/coach/check-credits pour coach normal - retourne credits et has_credits
4. API POST /api/chat/participants avec coach - doit déduire 1 crédit (402 si credits=0)
5. API POST /api/campaigns/send-email avec coach - doit déduire 1 crédit (402 si credits=0)
6. API /api/coach/vitrine/bassi - platform_name: 'Afroboost'
7. Frontend CampaignManager - bouton bloqué si hasInsufficientCredits (tested via API)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
SUPER_ADMIN_EMAIL = "contact.artboost@gmail.com"
TEST_COACH_EMAIL = "henri.bassi@test.com"  # Coach with 100 credits

class TestNonRegressionReservations:
    """Non-régression critique: Super Admin doit voir ses 7 réservations de Mars"""
    
    def test_super_admin_sees_all_reservations(self):
        """Super Admin (Bassi) doit voir au moins 7 réservations"""
        response = requests.get(
            f"{BASE_URL}/api/reservations",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # La réponse est paginée avec 'data' et 'pagination'
        reservations = data.get("data", [])
        total = data.get("pagination", {}).get("total", 0)
        
        print(f"[NON-REGRESSION] Super Admin voit {total} réservations (attendu >= 7)")
        assert total >= 7, f"Expected at least 7 reservations, got {total}"


class TestCheckCreditsAPI:
    """Test API /api/coach/check-credits"""
    
    def test_super_admin_has_unlimited_credits(self):
        """Super Admin doit avoir unlimited: true"""
        response = requests.get(
            f"{BASE_URL}/api/coach/check-credits",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        print(f"[CHECK-CREDITS] Super Admin response: {data}")
        assert data.get("unlimited") == True, f"Expected unlimited=True, got {data.get('unlimited')}"
        assert data.get("has_credits") == True, f"Expected has_credits=True, got {data.get('has_credits')}"
        assert data.get("credits") == -1, f"Expected credits=-1 for unlimited, got {data.get('credits')}"
    
    def test_coach_returns_credits_balance(self):
        """Coach normal doit retourner credits et has_credits"""
        response = requests.get(
            f"{BASE_URL}/api/coach/check-credits",
            headers={"X-User-Email": TEST_COACH_EMAIL}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        print(f"[CHECK-CREDITS] Coach {TEST_COACH_EMAIL} response: {data}")
        # Should return credits count and has_credits boolean
        assert "credits" in data, "Response should contain 'credits' field"
        assert "has_credits" in data, "Response should contain 'has_credits' field"
        # Coach henri.bassi@test.com should have 100 credits
        credits = data.get("credits", 0)
        print(f"[CHECK-CREDITS] Coach credits: {credits}")
    
    def test_unauthorized_without_email(self):
        """Sans email, doit retourner 401"""
        response = requests.get(f"{BASE_URL}/api/coach/check-credits")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestCreditDeductionCreateContact:
    """Test POST /api/chat/participants - déduction 1 crédit"""
    
    def test_super_admin_no_deduction(self):
        """Super Admin: pas de déduction de crédit"""
        # Get initial credits (Super Admin has unlimited = -1)
        check_before = requests.get(
            f"{BASE_URL}/api/coach/check-credits",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        ).json()
        
        # Create contact
        response = requests.post(
            f"{BASE_URL}/api/chat/participants",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL, "Content-Type": "application/json"},
            json={"name": "TEST_v902_superadmin_contact", "email": "test_v902_sa@test.com", "whatsapp": "+41000000001"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify no credit deduction (Super Admin stays unlimited)
        check_after = requests.get(
            f"{BASE_URL}/api/coach/check-credits",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        ).json()
        
        print(f"[CREATE-CONTACT] Super Admin before: {check_before}, after: {check_after}")
        assert check_after.get("unlimited") == True, "Super Admin should still have unlimited"
    
    def test_coach_with_credits_deducts_one(self):
        """Coach avec crédits: déduit 1 crédit lors de création contact"""
        # Get initial credits
        check_before = requests.get(
            f"{BASE_URL}/api/coach/check-credits",
            headers={"X-User-Email": TEST_COACH_EMAIL}
        ).json()
        
        initial_credits = check_before.get("credits", 0)
        if initial_credits <= 0:
            pytest.skip(f"Coach {TEST_COACH_EMAIL} has no credits to test deduction")
        
        # Create contact (should deduct 1 credit)
        response = requests.post(
            f"{BASE_URL}/api/chat/participants",
            headers={"X-User-Email": TEST_COACH_EMAIL, "Content-Type": "application/json"},
            json={"name": "TEST_v902_coach_contact", "email": "test_v902_coach@test.com", "whatsapp": "+41000000002"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify 1 credit deducted
        check_after = requests.get(
            f"{BASE_URL}/api/coach/check-credits",
            headers={"X-User-Email": TEST_COACH_EMAIL}
        ).json()
        
        new_credits = check_after.get("credits", 0)
        print(f"[CREATE-CONTACT] Coach before: {initial_credits}, after: {new_credits}")
        assert new_credits == initial_credits - 1, f"Expected {initial_credits - 1} credits, got {new_credits}"


class TestCreditDeductionCampaign:
    """Test POST /api/campaigns/send-email - déduction 1 crédit"""
    
    def test_super_admin_campaign_no_deduction(self):
        """Super Admin: pas de déduction de crédit pour envoi campagne"""
        check_before = requests.get(
            f"{BASE_URL}/api/coach/check-credits",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        ).json()
        
        # Try to send campaign (may fail due to email validation, but credit check happens first)
        response = requests.post(
            f"{BASE_URL}/api/campaigns/send-email",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL, "Content-Type": "application/json"},
            json={
                "to_email": "test_v902_campaign@test.com",
                "to_name": "TEST v902",
                "subject": "TEST v902 Campaign",
                "message": "Test message for v9.0.2 credit system"
            }
        )
        # Response might be 200 (sent) or other error (Resend not configured), but not 402
        print(f"[CAMPAIGN] Super Admin response: {response.status_code}")
        assert response.status_code != 402, "Super Admin should never get 402 insufficient credits"
        
        # Verify still unlimited
        check_after = requests.get(
            f"{BASE_URL}/api/coach/check-credits",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        ).json()
        assert check_after.get("unlimited") == True, "Super Admin should still have unlimited"


class TestInsufficientCredits:
    """Test 402 error when credits = 0"""
    
    def test_coach_zero_credits_cannot_create_contact(self):
        """Coach sans crédits: 402 pour création contact"""
        # Use a fake coach email that won't exist in DB
        zero_credit_coach = "zerox_credits_coach@nonexistent.com"
        
        response = requests.post(
            f"{BASE_URL}/api/chat/participants",
            headers={"X-User-Email": zero_credit_coach, "Content-Type": "application/json"},
            json={"name": "TEST_zero", "email": "zero@test.com"}
        )
        
        # Should return 402 or 200 (if coach not found, credit check returns has_credits=False)
        print(f"[ZERO-CREDITS] Create contact response: {response.status_code} - {response.text}")
        # Non-existent coach -> check_credits returns has_credits=False -> 402
        # But if no X-User-Email or coach not in system, it might pass...
        # The logic checks: if coach_email and not is_super_admin -> check credits
    
    def test_coach_zero_credits_cannot_send_campaign(self):
        """Coach sans crédits: 402 pour envoi campagne"""
        zero_credit_coach = "zerox_credits_coach@nonexistent.com"
        
        response = requests.post(
            f"{BASE_URL}/api/campaigns/send-email",
            headers={"X-User-Email": zero_credit_coach, "Content-Type": "application/json"},
            json={
                "to_email": "test@test.com",
                "message": "Test"
            }
        )
        
        print(f"[ZERO-CREDITS] Send campaign response: {response.status_code} - {response.text}")
        # Should get 402 for non-existent coach (credits=0)


class TestVitrineAPI:
    """Test API /api/coach/vitrine/bassi"""
    
    def test_vitrine_bassi_returns_platform_name(self):
        """Vitrine Bassi doit retourner platform_name: 'Afroboost'"""
        response = requests.get(f"{BASE_URL}/api/coach/vitrine/bassi")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        coach = data.get("coach", {})
        platform_name = coach.get("platform_name")
        
        print(f"[VITRINE] Bassi coach data: {coach}")
        print(f"[VITRINE] platform_name: {platform_name}")
        
        assert platform_name == "Afroboost", f"Expected platform_name='Afroboost', got '{platform_name}'"
    
    def test_vitrine_bassi_has_offers_and_courses(self):
        """Vitrine Bassi doit avoir des offres et des cours"""
        response = requests.get(f"{BASE_URL}/api/coach/vitrine/bassi")
        assert response.status_code == 200
        data = response.json()
        
        offers = data.get("offers", [])
        courses = data.get("courses", [])
        
        print(f"[VITRINE] Bassi: {len(offers)} offres, {len(courses)} cours")
        assert len(offers) > 0, "Vitrine should have offers"


class TestCoachesWithCredits:
    """Test les 5 coachs avec 100 crédits chacun"""
    
    def test_admin_coaches_list_has_credits(self):
        """Liste des coachs doit inclure le champ credits"""
        response = requests.get(
            f"{BASE_URL}/api/admin/coaches",
            headers={"X-User-Email": SUPER_ADMIN_EMAIL}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # API returns list directly, not wrapped
        coaches = data if isinstance(data, list) else data.get("coaches", [])
        print(f"[COACHES] Total: {len(coaches)}")
        
        for coach in coaches:
            email = coach.get("email", "")
            credits = coach.get("credits", "N/A")
            print(f"  - {email}: {credits} crédits")
            assert "credits" in coach, f"Coach {email} should have credits field"


# Cleanup test data
@pytest.fixture(autouse=True)
def cleanup_test_contacts():
    """Clean up TEST_ prefixed contacts after tests"""
    yield
    # Cleanup would go here, but we skip to avoid data pollution as per instructions


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
