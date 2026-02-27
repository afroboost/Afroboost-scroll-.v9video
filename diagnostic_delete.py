#!/usr/bin/env python3
"""
Test rapide et ciblé pour vérifier DELETE /api/chat/participants/{id}
"""

import requests
import json
import uuid

BACKEND_URL = "https://go-live-v7.preview.emergentagent.com"
BASE_API_URL = f"{BACKEND_URL}/api"

def test_delete_participant_corrected():
    """Test DELETE participant avec le bon modèle de données"""
    
    print("🔍 Test DELETE participant - Version corrigée")
    print("=" * 50)
    
    try:
        # Étape 1: Créer un participant avec les bons champs
        test_participant = {
            "name": "Test User Delete v71",
            "whatsapp": "+33612345678",  # Correct field name
            "email": "test.delete.v71@afroboost.com",
            "source": "test_v71",
            "link_token": None
        }
        
        print(f"📝 Création participant: {test_participant}")
        create_response = requests.post(
            f"{BASE_API_URL}/chat/participants",
            json=test_participant,
            timeout=10
        )
        
        print(f"📤 POST Response Status: {create_response.status_code}")
        if create_response.status_code == 200:
            participant_data = create_response.json()
            participant_id = participant_data.get("id")
            print(f"✅ Participant créé avec ID: {participant_id}")
            print(f"📋 Données: {json.dumps(participant_data, indent=2)}")
        else:
            print(f"❌ Erreur création: {create_response.text}")
            return False
        
        # Étape 2: Vérifier existence
        print(f"\n🔍 Vérification existence: GET /api/chat/participants/{participant_id}")
        get_response = requests.get(
            f"{BASE_API_URL}/chat/participants/{participant_id}",
            timeout=10
        )
        
        print(f"📤 GET Response Status: {get_response.status_code}")
        if get_response.status_code == 200:
            print("✅ Participant trouvé")
        else:
            print(f"❌ Participant non trouvé: {get_response.text}")
            return False
        
        # Étape 3: Supprimer le participant
        print(f"\n🗑️ Suppression: DELETE /api/chat/participants/{participant_id}")
        delete_response = requests.delete(
            f"{BASE_API_URL}/chat/participants/{participant_id}",
            timeout=10
        )
        
        print(f"📤 DELETE Response Status: {delete_response.status_code}")
        if delete_response.status_code == 200:
            delete_data = delete_response.json()
            print("✅ Suppression réussie")
            print(f"📊 Compteurs: {json.dumps(delete_data.get('deleted', {}), indent=2)}")
            
            # Étape 4: Vérifier suppression
            print(f"\n🔍 Vérification suppression: GET /api/chat/participants/{participant_id}")
            verify_response = requests.get(
                f"{BASE_API_URL}/chat/participants/{participant_id}",
                timeout=10
            )
            
            print(f"📤 Verification Response Status: {verify_response.status_code}")
            if verify_response.status_code == 404:
                print("✅ Participant bien supprimé (404)")
                return True
            else:
                print(f"❌ Participant encore présent: {verify_response.status_code}")
                return False
        else:
            print(f"❌ Erreur suppression: {delete_response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_current_participants():
    """Voir les participants actuels"""
    try:
        response = requests.get(f"{BASE_API_URL}/chat/participants", timeout=10)
        
        if response.status_code == 200:
            participants = response.json()
            print(f"\n📋 Participants actuels: {len(participants)}")
            for i, p in enumerate(participants):
                print(f"  {i+1}. {p.get('name', 'Unknown')} (ID: {p.get('id', 'No ID')})")
            return True
        else:
            print(f"❌ Erreur récupération participants: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("DIAGNOSTIC DELETE PARTICIPANT v7.1")
    print("=" * 60)
    
    # Voir l'état actuel
    test_current_participants()
    
    # Test du DELETE
    success = test_delete_participant_corrected()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST DELETE PARTICIPANT: SUCCÈS")
    else:
        print("⚠️ TEST DELETE PARTICIPANT: ÉCHEC")