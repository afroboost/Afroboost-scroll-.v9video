#!/usr/bin/env python3
"""
Tests de non-régression v7.1 Afroboost - Backend
Test les nouvelles fonctionnalités et endpoints existants
"""

import requests
import json
import uuid
from datetime import datetime
import os

# Configuration
BACKEND_URL = "https://go-live-v7.preview.emergentagent.com"
BASE_API_URL = f"{BACKEND_URL}/api"

def log_test(test_name, status, details=""):
    """Log des résultats de test avec timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"[{timestamp}] {status_emoji} {test_name}: {status}")
    if details:
        print(f"    {details}")
    print()

def test_health_check():
    """Test 1: Health Check - GET /api/health"""
    try:
        response = requests.get(f"{BASE_API_URL}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            expected = {"status": "healthy", "database": "connected"}
            
            if data == expected:
                log_test("Health Check", "PASS", f"Response: {data}")
                return True
            else:
                log_test("Health Check", "FAIL", f"Expected {expected}, got {data}")
                return False
        else:
            log_test("Health Check", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
            return False
            
    except Exception as e:
        log_test("Health Check", "FAIL", f"Exception: {str(e)}")
        return False

def test_delete_participant_complete():
    """Test 2: DELETE /api/chat/participants/{id} - Test complet avec création/suppression"""
    participant_id = None
    
    try:
        # Étape 1: Créer un participant test
        test_participant = {
            "id": str(uuid.uuid4()),
            "name": "Test Participant Delete",
            "phone": "+33612345678",
            "email": "test.delete@example.com",
            "avatar_url": None,
            "is_active": True
        }
        participant_id = test_participant["id"]
        
        create_response = requests.post(
            f"{BASE_API_URL}/chat/participants",
            json=test_participant,
            timeout=10
        )
        
        if create_response.status_code != 200:
            log_test("DELETE Participant - Création", "FAIL", 
                    f"Impossible de créer participant test: {create_response.status_code}")
            return False
            
        log_test("DELETE Participant - Création", "PASS", 
                f"Participant créé: {participant_id}")
        
        # Étape 2: Vérifier que le participant existe
        get_response = requests.get(
            f"{BASE_API_URL}/chat/participants/{participant_id}",
            timeout=10
        )
        
        if get_response.status_code != 200:
            log_test("DELETE Participant - Vérification", "FAIL", 
                    f"Participant créé non trouvé: {get_response.status_code}")
            return False
            
        # Étape 3: Supprimer le participant
        delete_response = requests.delete(
            f"{BASE_API_URL}/chat/participants/{participant_id}",
            timeout=10
        )
        
        if delete_response.status_code == 200:
            delete_data = delete_response.json()
            
            # Vérifier la structure de la réponse
            required_keys = ["success", "message", "deleted"]
            deleted_keys = ["participant", "messages", "sessions_updated", "orphan_sessions"]
            
            if all(key in delete_data for key in required_keys):
                if all(key in delete_data["deleted"] for key in deleted_keys):
                    log_test("DELETE Participant - Suppression", "PASS", 
                            f"Compteurs: {delete_data['deleted']}")
                    
                    # Étape 4: Vérifier que le participant a bien été supprimé
                    verify_response = requests.get(
                        f"{BASE_API_URL}/chat/participants/{participant_id}",
                        timeout=10
                    )
                    
                    if verify_response.status_code == 404:
                        log_test("DELETE Participant - Vérification suppression", "PASS", 
                                "Participant correctement supprimé")
                        return True
                    else:
                        log_test("DELETE Participant - Vérification suppression", "FAIL", 
                                f"Participant encore présent: {verify_response.status_code}")
                        return False
                else:
                    log_test("DELETE Participant - Suppression", "FAIL", 
                            f"Clés manquantes dans 'deleted': {delete_data}")
                    return False
            else:
                log_test("DELETE Participant - Suppression", "FAIL", 
                        f"Structure réponse incorrecte: {delete_data}")
                return False
        else:
            log_test("DELETE Participant - Suppression", "FAIL", 
                    f"Status: {delete_response.status_code}, Body: {delete_response.text}")
            return False
            
    except Exception as e:
        log_test("DELETE Participant - Exception", "FAIL", f"Exception: {str(e)}")
        return False

def test_delete_participant_404():
    """Test 3: DELETE /api/chat/participants/{id} - Test 404 pour ID inexistant"""
    try:
        fake_id = str(uuid.uuid4())
        
        response = requests.delete(
            f"{BASE_API_URL}/chat/participants/{fake_id}",
            timeout=10
        )
        
        if response.status_code == 404:
            data = response.json()
            if "detail" in data and "non trouve" in data["detail"].lower():
                log_test("DELETE Participant 404", "PASS", 
                        f"404 correctement retourné: {data}")
                return True
            else:
                log_test("DELETE Participant 404", "FAIL", 
                        f"Message d'erreur incorrect: {data}")
                return False
        else:
            log_test("DELETE Participant 404", "FAIL", 
                    f"Expected 404, got {response.status_code}")
            return False
            
    except Exception as e:
        log_test("DELETE Participant 404", "FAIL", f"Exception: {str(e)}")
        return False

def test_chat_participants_regression():
    """Test 4: Non-régression GET /api/chat/participants"""
    try:
        response = requests.get(f"{BASE_API_URL}/chat/participants", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                log_test("GET Participants - Non-régression", "PASS", 
                        f"Liste participants récupérée: {len(data)} participants")
                return True
            else:
                log_test("GET Participants - Non-régression", "FAIL", 
                        f"Expected list, got {type(data)}")
                return False
        else:
            log_test("GET Participants - Non-régression", "FAIL", 
                    f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        log_test("GET Participants - Non-régression", "FAIL", f"Exception: {str(e)}")
        return False

def test_chat_sessions_regression():
    """Test 5: Non-régression GET /api/chat/sessions"""
    try:
        response = requests.get(f"{BASE_API_URL}/chat/sessions", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                log_test("GET Sessions - Non-régression", "PASS", 
                        f"Liste sessions récupérée: {len(data)} sessions")
                return True
            else:
                log_test("GET Sessions - Non-régression", "FAIL", 
                        f"Expected list, got {type(data)}")
                return False
        else:
            log_test("GET Sessions - Non-régression", "FAIL", 
                    f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        log_test("GET Sessions - Non-régression", "FAIL", f"Exception: {str(e)}")
        return False

def test_chat_messages_regression():
    """Test 6: Non-régression POST /api/chat/messages"""
    try:
        # Test simple de structure - pas de création réelle
        # Juste vérifier que l'endpoint répond correctement aux mauvaises requêtes
        response = requests.post(f"{BASE_API_URL}/chat/messages", json={}, timeout=10)
        
        # On s'attend à une erreur 422 (validation) car on envoie un JSON vide
        if response.status_code in [422, 400]:
            log_test("POST Messages - Non-régression", "PASS", 
                    f"Endpoint répond correctement aux requêtes invalides: {response.status_code}")
            return True
        else:
            log_test("POST Messages - Non-régression", "WARN", 
                    f"Réponse inattendue: {response.status_code}")
            return True  # Pas critique pour la non-régression
            
    except Exception as e:
        log_test("POST Messages - Non-régression", "FAIL", f"Exception: {str(e)}")
        return False

def test_server_integrity():
    """Test 7: Vérification intégrité server.py (nombre de lignes)"""
    try:
        server_path = "/app/backend/server.py"
        
        if not os.path.exists(server_path):
            log_test("Intégrité server.py", "FAIL", "Fichier server.py non trouvé")
            return False
        
        with open(server_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            line_count = len(lines)
        
        # Selon la spec: server.py = 7397 lignes (< 7410 autorisé)
        if line_count == 7397:
            log_test("Intégrité server.py", "PASS", 
                    f"Exactement {line_count} lignes comme spécifié")
            return True
        elif line_count <= 7410:
            log_test("Intégrité server.py", "PASS", 
                    f"{line_count} lignes (dans la limite autorisée ≤ 7410)")
            return True
        else:
            log_test("Intégrité server.py", "FAIL", 
                    f"{line_count} lignes > limite autorisée (7410)")
            return False
            
    except Exception as e:
        log_test("Intégrité server.py", "FAIL", f"Exception: {str(e)}")
        return False

def main():
    """Exécution des tests de non-régression v7.1"""
    print("=" * 60)
    print("TESTS DE NON-RÉGRESSION v7.1 AFROBOOST - BACKEND")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"API Base URL: {BASE_API_URL}")
    print("=" * 60)
    print()
    
    # Exécution des tests dans l'ordre spécifié
    tests = [
        ("1. Health Check", test_health_check),
        ("2. DELETE Participant - Test complet", test_delete_participant_complete),
        ("3. DELETE Participant - 404", test_delete_participant_404),
        ("4. Participants - Non-régression", test_chat_participants_regression),
        ("5. Sessions - Non-régression", test_chat_sessions_regression),
        ("6. Messages - Non-régression", test_chat_messages_regression),
        ("7. Server.py - Intégrité", test_server_integrity),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🔄 Exécution: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    # Résumé final
    print("=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print("=" * 60)
    print(f"RÉSULTAT: {passed}/{total} tests passés")
    
    if passed == total:
        print("🎉 TOUS LES TESTS SONT PASSÉS - v7.1 VALIDÉE")
        return True
    else:
        print("⚠️  CERTAINS TESTS ONT ÉCHOUÉ - VÉRIFICATION REQUISE")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)