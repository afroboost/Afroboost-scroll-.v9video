# promo_routes.py - Routes de codes promo v9.2.0
# Extrait de server.py pour modularisation
# v9.3.0: Ajout isolation par coach_id

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)

# Super Admin email - pas de filtre
SUPER_ADMIN_EMAIL = "contact.artboost@gmail.com"

# Router avec préfixe /discount-codes
promo_router = APIRouter(prefix="/discount-codes", tags=["Promo Codes"])

# Référence DB (initialisée depuis server.py)
_db = None

def init_promo_db(database):
    """Initialise la référence DB"""
    global _db
    _db = database
    logger.info("[PROMO_ROUTES] Base de données initialisée")


# === MODÈLES ===
class DiscountCode(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    type: str  # "100%", "%", "CHF"
    value: float
    assignedEmail: Optional[str] = None
    expiresAt: Optional[str] = None
    courses: List[str] = []
    maxUses: Optional[int] = None
    used: int = 0
    active: bool = True
    coach_id: Optional[str] = None  # v9.3.0: Isolation par coach


class DiscountCodeCreate(BaseModel):
    code: str
    type: str
    value: float
    assignedEmail: Optional[str] = None
    expiresAt: Optional[str] = None
    courses: List[str] = []
    maxUses: Optional[int] = None
    coach_id: Optional[str] = None  # v9.3.0: Isolation par coach


# === ROUTES ===
@promo_router.get("", response_model=List[DiscountCode])
async def get_discount_codes():
    """Récupère tous les codes promo"""
    codes = await _db.discount_codes.find({}, {"_id": 0}).to_list(1000)
    return codes


@promo_router.post("", response_model=DiscountCode)
async def create_discount_code(code: DiscountCodeCreate):
    """Crée un nouveau code promo"""
    code_obj = DiscountCode(**code.model_dump())
    await _db.discount_codes.insert_one(code_obj.model_dump())
    return code_obj


@promo_router.put("/{code_id}")
async def update_discount_code(code_id: str, updates: dict):
    """Met à jour un code promo"""
    await _db.discount_codes.update_one({"id": code_id}, {"$set": updates})
    updated = await _db.discount_codes.find_one({"id": code_id}, {"_id": 0})
    return updated


@promo_router.delete("/{code_id}")
async def delete_discount_code(code_id: str):
    """Supprime un code promo"""
    await _db.discount_codes.delete_one({"id": code_id})
    return {"success": True}


@promo_router.post("/validate")
async def validate_discount_code(data: dict):
    """Valide un code promo pour une réservation"""
    code_str = data.get("code", "").strip().upper()  # Normalize: trim + uppercase
    user_email = data.get("email", "").strip()
    course_id = data.get("courseId", "").strip() if data.get("courseId") else ""
    
    # Case-insensitive search using regex
    code = await _db.discount_codes.find_one({
        "code": {"$regex": f"^{code_str}$", "$options": "i"},  # Case insensitive match
        "active": True
    }, {"_id": 0})
    
    if not code:
        return {"valid": False, "message": "Code inconnu ou invalide"}
    
    # Check expiration date
    if code.get("expiresAt"):
        try:
            expiry = code["expiresAt"]
            if isinstance(expiry, str):
                # Handle various date formats
                expiry = expiry.replace('Z', '+00:00')
                if 'T' not in expiry:
                    expiry = expiry + "T23:59:59+00:00"
                expiry_date = datetime.fromisoformat(expiry)
            else:
                expiry_date = expiry
            if expiry_date < datetime.now(timezone.utc):
                return {"valid": False, "message": "Code promo expiré"}
        except Exception as e:
            logger.debug(f"Date parsing: {e}")
    
    # Check max uses
    if code.get("maxUses") and code.get("used", 0) >= code["maxUses"]:
        return {"valid": False, "message": "Code promo épuisé (nombre max d'utilisations atteint)"}
    
    # Check if course is allowed - SKIP if no courseId provided (identification flow)
    # IMPORTANT: empty list = all courses allowed
    allowed_courses = code.get("courses", [])
    if course_id and allowed_courses and len(allowed_courses) > 0:
        if course_id not in allowed_courses:
            return {"valid": False, "message": "Code non applicable à ce cours"}
    
    # Check assigned email (only if assignedEmail is set AND email is provided)
    assigned = code.get("assignedEmail") or ""
    if assigned and isinstance(assigned, str):
        assigned = assigned.strip()
        if assigned and user_email:
            if assigned.lower() != user_email.lower():
                return {"valid": False, "message": "Code réservé à un autre compte"}
    
    # v8.7: Sync CRM si email fourni
    if user_email:
        await _db.chat_participants.update_one(
            {"email": user_email},
            {
                "$set": {
                    "email": user_email,
                    "name": data.get("name", user_email.split("@")[0]),
                    "source": "chat_login",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                },
                "$setOnInsert": {
                    "id": str(uuid.uuid4()),
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            },
            upsert=True
        )
    
    return {"valid": True, "code": code}


@promo_router.post("/{code_id}/use")
async def use_discount_code(code_id: str):
    """Marque un code promo comme utilisé (décompte géré par create_reservation)"""
    return {"success": True, "note": "Decompte gere par create_reservation"}
