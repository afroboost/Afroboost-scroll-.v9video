#!/usr/bin/env python3
"""
SCHEDULER DE CAMPAGNES AFROBOOST - MODE DAEMON
==============================================
Script autonome pour l'envoi programmé des campagnes marketing.
Tourne en boucle infinie par défaut (mode daemon).

Usage:
    python scheduler.py              # Mode DAEMON (boucle toutes les 30s)
    python scheduler.py --once       # Exécution unique
    python scheduler.py --dry-run    # Mode test sans envoi réel

Ce script doit être lancé au démarrage du serveur et tourner en continu.
"""

import os
import sys
import time
import logging
import argparse
from datetime import datetime, timezone
from pathlib import Path

# Charger les variables d'environnement
from dotenv import load_dotenv
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB synchrone (pas besoin d'async pour le scheduler)
from pymongo import MongoClient
import requests

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [SCHEDULER] %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration MongoDB
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

if not MONGO_URL:
    logger.error("MONGO_URL non configuré. Arrêt du scheduler.")
    sys.exit(1)

# Configuration API
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8001')

# ==================== TWILIO CONFIGURATION (PRIORITÉ .ENV) ====================
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER', '')

# Nombre maximum de tentatives avant échec
MAX_RETRY_ATTEMPTS = 3

# Intervalle de vérification en secondes (mode daemon)
SCHEDULER_INTERVAL = 30

# Connexion MongoDB
try:
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    client.admin.command('ping')
    logger.info(f"✅ Connexion MongoDB réussie: {DB_NAME}")
except Exception as e:
    logger.error(f"❌ Erreur connexion MongoDB: {e}")
    sys.exit(1)


def get_current_utc_time():
    """Retourne l'heure actuelle en UTC (timezone-aware)."""
    return datetime.now(timezone.utc)


def parse_scheduled_date(date_str):
    """Parse une date ISO et la convertit en datetime UTC."""
    if not date_str:
        return None
    
    try:
        if 'Z' in date_str:
            date_str = date_str.replace('Z', '+00:00')
        
        if '+' in date_str or '-' in date_str[-6:]:
            dt = datetime.fromisoformat(date_str)
        else:
            dt = datetime.fromisoformat(date_str)
            dt = dt.replace(tzinfo=timezone.utc)
        
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        return dt
    except Exception as e:
        logger.warning(f"Impossible de parser la date '{date_str}': {e}")
        return None


def get_twilio_config():
    """
    Récupère la config Twilio avec PRIORITÉ aux variables .env.
    """
    # PRIORITÉ 1: Variables d'environnement (.env)
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER:
        logger.info(f"[WHATSAPP-PROD] ✅ Config .env - Numéro: {TWILIO_FROM_NUMBER}")
        return TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER
    
    # PRIORITÉ 2: Configuration en base de données
    whatsapp_config = db.whatsapp_config.find_one({"id": "whatsapp_config"})
    if whatsapp_config:
        account_sid = whatsapp_config.get("accountSid")
        auth_token = whatsapp_config.get("authToken")
        from_number = whatsapp_config.get("fromNumber")
        
        if account_sid and auth_token and from_number:
            logger.info(f"[WHATSAPP-PROD] ⚠️ Config DB (fallback) - Numéro: {from_number}")
            return account_sid, auth_token, from_number
    
    return None, None, None


def send_whatsapp_message(to_phone, message, media_url=None):
    """
    Envoie un message WhatsApp via Twilio.
    Retourne (success: bool, error: str|None, sid: str|None)
    """
    account_sid, auth_token, from_number = get_twilio_config()
    
    if not account_sid or not auth_token or not from_number:
        logger.warning("[WHATSAPP-PROD] ❌ Configuration Twilio manquante")
        return False, "Configuration Twilio manquante", None
    
    # Formater les numéros
    clean_to = to_phone.replace(" ", "").replace("-", "")
    if not clean_to.startswith("+"):
        clean_to = "+41" + clean_to.lstrip("0") if clean_to.startswith("0") else "+" + clean_to
    
    clean_from = from_number if from_number.startswith("+") else "+" + from_number
    
    # Construire la requête Twilio
    twilio_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    
    data = {
        "From": f"whatsapp:{clean_from}",
        "To": f"whatsapp:{clean_to}",
        "Body": message
    }
    
    if media_url:
        data["MediaUrl"] = media_url
    
    try:
        response = requests.post(
            twilio_url,
            data=data,
            auth=(account_sid, auth_token),
            timeout=30
        )
        
        result = response.json()
        
        if response.status_code >= 400:
            error_msg = result.get("message", "Unknown error")
            print(f"[WHATSAPP-PROD] Message envoyé via {clean_from} vers {clean_to} - Status: ERROR ({error_msg})")
            return False, error_msg, None
        
        sid = result.get("sid", "")
        print(f"[WHATSAPP-PROD] Message envoyé via {clean_from} vers {clean_to} - Status: SUCCESS (SID: {sid})")
        return True, None, sid
        
    except requests.Timeout:
        return False, "Timeout lors de l'envoi", None
    except Exception as e:
        print(f"[WHATSAPP-PROD] Message envoyé via {clean_from} vers {clean_to} - Status: ERROR ({str(e)})")
        return False, str(e), None


def send_campaign_email(to_email, to_name, subject, message, media_url=None):
    """
    Envoie un email de campagne via l'API backend.
    Retourne (success: bool, error: str|None)
    """
    try:
        payload = {
            "to_email": to_email,
            "to_name": to_name,
            "subject": subject,
            "message": message
        }
        if media_url:
            payload["media_url"] = media_url
        
        response = requests.post(
            f"{BACKEND_URL}/api/campaigns/send-email",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return True, None
            else:
                return False, result.get("error", "Erreur inconnue")
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    
    except requests.Timeout:
        return False, "Timeout lors de l'envoi"
    except Exception as e:
        return False, str(e)


def process_campaign(campaign, dry_run=False):
    """
    Traite une campagne programmée:
    - Vérifie les dates d'envoi
    - Envoie aux contacts ciblés (WhatsApp ET Email)
    - Met à jour le statut
    
    Retourne: (processed: bool, success_count: int, fail_count: int)
    """
    campaign_id = campaign.get("id")
    campaign_name = campaign.get("name", "Sans nom")
    
    logger.info(f"📧 Traitement campagne: {campaign_name} ({campaign_id})")
    
    now = get_current_utc_time()
    
    # === GESTION DES DATES ===
    scheduled_at = campaign.get("scheduledAt")
    scheduled_dates = campaign.get("scheduledDates", [])
    sent_dates = campaign.get("sentDates", [])
    
    # Normaliser: si scheduledAt existe et scheduledDates est vide, créer une liste
    if scheduled_at and not scheduled_dates:
        scheduled_dates = [scheduled_at]
    
    if not scheduled_dates:
        logger.warning(f"  ⚠️ Aucune date programmée pour cette campagne")
        return False, 0, 0
    
    # Trouver les dates à traiter (passées et non encore envoyées)
    dates_to_process = []
    for date_str in scheduled_dates:
        scheduled_dt = parse_scheduled_date(date_str)
        if scheduled_dt and scheduled_dt <= now and date_str not in sent_dates:
            dates_to_process.append(date_str)
    
    if not dates_to_process:
        next_date = scheduled_dates[0] if scheduled_dates else 'N/A'
        logger.info(f"  ⏳ Aucune date à traiter maintenant (prochaine: {next_date})")
        return False, 0, 0
    
    logger.info(f"  📅 {len(dates_to_process)} date(s) à traiter: {dates_to_process}")
    
    # === RÉCUPÉRER LES CONTACTS ===
    target_type = campaign.get("targetType", "all")
    selected_contacts = campaign.get("selectedContacts", [])
    
    if target_type == "all":
        contacts = list(db.users.find({}, {"_id": 0}))
    else:
        contacts = list(db.users.find({"id": {"$in": selected_contacts}}, {"_id": 0}))
    
    if not contacts:
        logger.warning(f"  ⚠️ Aucun contact trouvé pour cette campagne")
        db.campaigns.update_one(
            {"id": campaign_id},
            {"$set": {"status": "completed", "updatedAt": now.isoformat()}}
        )
        return True, 0, 0
    
    logger.info(f"  👥 {len(contacts)} contact(s) ciblés")
    
    # === VÉRIFIER LES CANAUX ===
    channels = campaign.get("channels", {})
    whatsapp_enabled = channels.get("whatsapp", False)
    email_enabled = channels.get("email", False)
    
    message = campaign.get("message", "")
    media_url = campaign.get("mediaUrl", "")
    subject = f"📢 {campaign_name}"
    
    success_count = 0
    fail_count = 0
    results = campaign.get("results", [])
    retry_counts = campaign.get("retryCounts", {})
    
    # === ENVOYER AUX CONTACTS ===
    for contact in contacts:
        contact_id = contact.get("id", "")
        contact_email = contact.get("email", "")
        contact_name = contact.get("name", "")
        contact_phone = contact.get("whatsapp", "")
        
        # ==================== ENVOI WHATSAPP ====================
        if whatsapp_enabled and contact_phone:
            retry_key = f"{contact_id}_whatsapp"
            current_retries = retry_counts.get(retry_key, 0)
            
            # Vérifier si déjà envoyé
            already_sent = any(
                r.get("contactId") == contact_id and 
                r.get("channel") == "whatsapp" and 
                r.get("status") == "sent"
                for r in results
            )
            
            if already_sent:
                logger.info(f"    ✓ WhatsApp {contact_phone} - Déjà envoyé")
            elif current_retries >= MAX_RETRY_ATTEMPTS:
                logger.error(f"    ❌ WhatsApp {contact_phone} - Max tentatives atteint")
                fail_count += 1
            else:
                if dry_run:
                    logger.info(f"    🧪 [DRY-RUN] WhatsApp {contact_phone} - Simulé")
                    success = True
                    error = None
                    sid = "dry-run"
                else:
                    logger.info(f"    📤 Envoi WhatsApp à {contact_phone}...")
                    success, error, sid = send_whatsapp_message(
                        to_phone=contact_phone,
                        message=message,
                        media_url=media_url if media_url else None
                    )
                
                if success:
                    logger.info(f"    ✅ WhatsApp {contact_phone} - Envoyé (SID: {sid})")
                    success_count += 1
                    
                    result_entry = {
                        "contactId": contact_id,
                        "contactName": contact_name,
                        "contactEmail": contact_email,
                        "contactPhone": contact_phone,
                        "channel": "whatsapp",
                        "status": "sent",
                        "sentAt": now.isoformat(),
                        "sid": sid
                    }
                    
                    # Mettre à jour ou ajouter le résultat
                    result_found = False
                    for i, r in enumerate(results):
                        if r.get("contactId") == contact_id and r.get("channel") == "whatsapp":
                            results[i] = result_entry
                            result_found = True
                            break
                    if not result_found:
                        results.append(result_entry)
                else:
                    logger.error(f"    ❌ WhatsApp {contact_phone} - Échec: {error}")
                    fail_count += 1
                    retry_counts[retry_key] = current_retries + 1
        
        # ==================== ENVOI EMAIL ====================
        if email_enabled and contact_email:
            retry_key = f"{contact_id}_email"
            current_retries = retry_counts.get(retry_key, 0)
            
            # Vérifier si déjà envoyé
            already_sent = any(
                r.get("contactId") == contact_id and 
                r.get("channel") == "email" and 
                r.get("status") == "sent"
                for r in results
            )
            
            if already_sent:
                logger.info(f"    ✓ Email {contact_email} - Déjà envoyé")
            elif current_retries >= MAX_RETRY_ATTEMPTS:
                logger.error(f"    ❌ Email {contact_email} - Max tentatives atteint")
                fail_count += 1
            else:
                if dry_run:
                    logger.info(f"    🧪 [DRY-RUN] Email {contact_email} - Simulé")
                    success = True
                    error = None
                else:
                    logger.info(f"    📤 Envoi Email à {contact_email}...")
                    success, error = send_campaign_email(
                        to_email=contact_email,
                        to_name=contact_name,
                        subject=subject,
                        message=message,
                        media_url=media_url if media_url else None
                    )
                
                if success:
                    logger.info(f"    ✅ Email {contact_email} - Envoyé")
                    success_count += 1
                    
                    result_entry = {
                        "contactId": contact_id,
                        "contactName": contact_name,
                        "contactEmail": contact_email,
                        "contactPhone": contact_phone,
                        "channel": "email",
                        "status": "sent",
                        "sentAt": now.isoformat()
                    }
                    
                    result_found = False
                    for i, r in enumerate(results):
                        if r.get("contactId") == contact_id and r.get("channel") == "email":
                            results[i] = result_entry
                            result_found = True
                            break
                    if not result_found:
                        results.append(result_entry)
                else:
                    logger.error(f"    ❌ Email {contact_email} - Échec: {error}")
                    fail_count += 1
                    retry_counts[retry_key] = current_retries + 1
    
    # === MISE À JOUR DE LA CAMPAGNE ===
    new_sent_dates = list(set(sent_dates + dates_to_process))
    all_dates_processed = set(new_sent_dates) >= set(scheduled_dates)
    
    # Déterminer le nouveau statut
    if fail_count > 0 and success_count == 0:
        new_status = "failed"
    elif all_dates_processed:
        new_status = "completed"
    else:
        new_status = "scheduled"
    
    # Mettre à jour en base
    update_data = {
        "status": new_status,
        "results": results,
        "sentDates": new_sent_dates,
        "retryCounts": retry_counts,
        "updatedAt": now.isoformat(),
        "lastProcessedAt": now.isoformat()
    }
    
    db.campaigns.update_one(
        {"id": campaign_id},
        {"$set": update_data}
    )
    
    status_emoji = "✅" if new_status == "completed" else ("❌" if new_status == "failed" else "⏳")
    logger.info(f"  {status_emoji} Campagne mise à jour: {new_status} (✓{success_count} / ✗{fail_count})")
    
    return True, success_count, fail_count


def run_scheduler(dry_run=False):
    """
    Exécute un cycle du scheduler.
    """
    now = get_current_utc_time()
    logger.info(f"{'='*60}")
    logger.info(f"🚀 SCHEDULER AFROBOOST - {now.isoformat()}")
    logger.info(f"{'='*60}")
    
    if dry_run:
        logger.info("⚠️ MODE DRY-RUN: Aucun message ne sera réellement envoyé")
    
    # Chercher les campagnes programmées
    campaigns = list(db.campaigns.find(
        {"status": {"$in": ["scheduled", "sending"]}},
        {"_id": 0}
    ))
    
    logger.info(f"📋 {len(campaigns)} campagne(s) programmée(s) trouvée(s)")
    
    if not campaigns:
        logger.info("Aucune campagne à traiter.")
        return
    
    total_success = 0
    total_fail = 0
    campaigns_processed = 0
    
    for campaign in campaigns:
        try:
            processed, success, fail = process_campaign(campaign, dry_run=dry_run)
            if processed:
                campaigns_processed += 1
                total_success += success
                total_fail += fail
        except Exception as e:
            logger.error(f"❌ Erreur lors du traitement de la campagne {campaign.get('id')}: {e}")
            import traceback
            traceback.print_exc()
    
    logger.info(f"{'='*60}")
    logger.info(f"📊 RÉSUMÉ: {campaigns_processed} campagne(s) traitée(s)")
    logger.info(f"   ✅ Succès: {total_success} | ❌ Échecs: {total_fail}")
    logger.info(f"{'='*60}")


def main():
    """Point d'entrée principal du scheduler - MODE DAEMON PAR DÉFAUT."""
    parser = argparse.ArgumentParser(description="Scheduler de campagnes Afroboost (Mode Daemon)")
    parser.add_argument("--once", action="store_true", help="Exécution unique (pas de boucle)")
    parser.add_argument("--dry-run", action="store_true", help="Mode test sans envoi réel")
    parser.add_argument("--interval", type=int, default=SCHEDULER_INTERVAL, help=f"Intervalle en secondes (défaut: {SCHEDULER_INTERVAL})")
    args = parser.parse_args()
    
    # Log de la configuration Twilio au démarrage
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER:
        logger.info(f"[WHATSAPP-PROD] ✅ Configuration Twilio chargée depuis .env")
        logger.info(f"[WHATSAPP-PROD] 📱 Numéro de production: {TWILIO_FROM_NUMBER}")
    else:
        logger.warning(f"[WHATSAPP-PROD] ⚠️ Configuration Twilio incomplète dans .env")
    
    if args.once:
        # Mode exécution unique
        logger.info("📧 Exécution unique...")
        run_scheduler(dry_run=args.dry_run)
    else:
        # MODE DAEMON PAR DÉFAUT - Boucle infinie
        logger.info(f"🔄 MODE DAEMON - Boucle toutes les {args.interval}s (CTRL+C pour arrêter)")
        while True:
            try:
                run_scheduler(dry_run=args.dry_run)
            except Exception as e:
                logger.error(f"Erreur dans la boucle scheduler: {e}")
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
