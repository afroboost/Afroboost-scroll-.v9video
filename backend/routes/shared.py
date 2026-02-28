# shared.py - Constantes et helpers partagés v9.1.0
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# Super Admin
SUPER_ADMIN_EMAIL = "contact.artboost@gmail.com"
DEFAULT_COACH_ID = "bassi_default"
ROLE_SUPER_ADMIN = "super_admin"
ROLE_COACH = "coach"
ROLE_USER = "user"

def is_super_admin(email: str) -> bool:
    """Vérifie si l'email est celui du Super Admin"""
    return email and email.lower().strip() == SUPER_ADMIN_EMAIL.lower()

def get_coach_filter(email: str) -> dict:
    """Retourne le filtre MongoDB pour l'isolation des données coach"""
    if is_super_admin(email):
        return {}
    return {"coach_id": email.lower().strip()}
