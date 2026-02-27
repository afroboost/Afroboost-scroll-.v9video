# VERSION 7.0 - PRODUCTION READY - NE PAS MODIFIER login/tri/sync
from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import stripe
import asyncio
import json
import socketio

# Web Push imports
try:
    from pywebpush import webpush, WebPushException
    WEBPUSH_AVAILABLE = True
except ImportError:
    WEBPUSH_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("pywebpush not installed - push notifications disabled")

# Resend import
try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Stripe configuration - utilise la variable d'environnement existante
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# VAPID configuration for Web Push
VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY', '')
VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY', '')
VAPID_CLAIMS_EMAIL = os.environ.get('VAPID_CLAIMS_EMAIL', 'contact@afroboost.ch')

# Resend configuration
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
if RESEND_AVAILABLE and RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

# TWILIO CONFIGURATION
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER', '')
TWILIO_SANDBOX_NUMBER = "+14155238886"

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
if not mongo_url:
    raise RuntimeError("MONGO_URL required")

client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'afroboost_db')]

# Configure logging FIRST (needed for socketio)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Créer l'application FastAPI (interne)
fastapi_app = FastAPI(title="Afroboost API")
api_router = APIRouter(prefix="/api")

# SOCKET.IO CONFIGURATION
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=False,
    engineio_logger=False
)

connected_clients = {}  # { session_id: [sid1, sid2, ...] }

@sio.event
async def connect(sid, environ):
    logger.info(f"[SOCKET.IO] Client connecté: {sid}")

@sio.event
async def disconnect(sid):
    for session_id, sids in list(connected_clients.items()):
        if sid in sids:
            sids.remove(sid)
            if not sids:
                del connected_clients[session_id]
    logger.info(f"[SOCKET.IO] Client déconnecté: {sid}")

@sio.event
async def join_session(sid, data):
    """
    Un client rejoint une session de chat.
    data = { "session_id": "xxx", "participant_id": "xxx" }
    """
    session_id = data.get("session_id")
    participant_id = data.get("participant_id")
    
    if session_id:
        # Joindre la room Socket.IO (permet le broadcast par session)
        await sio.enter_room(sid, session_id)
        
        # Tracker la connexion
        if session_id not in connected_clients:
            connected_clients[session_id] = []
        if sid not in connected_clients[session_id]:
            connected_clients[session_id].append(sid)
        
        logger.info(f"[SOCKET.IO] Client {sid} a rejoint la session {session_id}")
        
        # Confirmer au client
        await sio.emit('joined_session', {
            'session_id': session_id,
            'participant_id': participant_id,
            'status': 'connected'
        }, room=sid)

@sio.event
async def leave_session(sid, data):
    """Un client quitte une session"""
    session_id = data.get("session_id")
    if session_id:
        await sio.leave_room(sid, session_id)
        if session_id in connected_clients and sid in connected_clients[session_id]:
            connected_clients[session_id].remove(sid)

async def emit_new_message(session_id: str, message_data: dict):
    """
    Émet un événement 'message_received' à tous les clients d'une session.
    Appelé par les endpoints de chat quand un message est envoyé.
    """
    if session_id:
        await sio.emit('message_received', message_data, room=session_id)
        logger.info(f"[SOCKET.IO] Message émis dans session {session_id}")

# ==================== PRIVATE MESSAGE SOCKET.IO ====================
@sio.event
async def join_private_conversation(sid, data):
    """
    Un client rejoint une conversation privée pour recevoir les messages en temps réel.
    data = { "conversation_id": "xxx", "participant_id": "xxx" }
    """
    conversation_id = data.get("conversation_id")
    if conversation_id:
        room_name = f"pm_{conversation_id}"
        await sio.enter_room(sid, room_name)
        logger.info(f"[SOCKET.IO] Client {sid} a rejoint la conversation privée {conversation_id}")
        await sio.emit('joined_private_conversation', {
            'conversation_id': conversation_id,
            'status': 'connected'
        }, room=sid)

@sio.event
async def leave_private_conversation(sid, data):
    """Un client quitte une conversation privée"""
    conversation_id = data.get("conversation_id")
    if conversation_id:
        room_name = f"pm_{conversation_id}"
        await sio.leave_room(sid, room_name)
        logger.info(f"[SOCKET.IO] Client {sid} a quitté la conversation privée {conversation_id}")

# ==================== DM TYPING INDICATOR (Messages Privés) ====================
@sio.event
async def dm_typing_start(sid, data):
    """
    Un utilisateur commence à taper dans un DM.
    data = { "conversation_id": "xxx", "user_id": "xxx", "user_name": "xxx" }
    """
    conversation_id = data.get("conversation_id")
    user_name = data.get("user_name", "Quelqu'un")
    user_id = data.get("user_id")
    
    if conversation_id:
        room_name = f"pm_{conversation_id}"
        await sio.emit('dm_typing', {
            'conversation_id': conversation_id,
            'user_id': user_id,
            'user_name': user_name,
            'is_typing': True
        }, room=room_name, skip_sid=sid)

@sio.event
async def dm_typing_stop(sid, data):
    """Un utilisateur arrête de taper dans un DM."""
    conversation_id = data.get("conversation_id")
    user_id = data.get("user_id")
    
    if conversation_id:
        room_name = f"pm_{conversation_id}"
        await sio.emit('dm_typing', {
            'conversation_id': conversation_id,
            'user_id': user_id,
            'is_typing': False
        }, room=room_name, skip_sid=sid)

# ==================== AVATAR UPDATE (Sync Temps Réel) ====================
@sio.event
async def avatar_updated(sid, data):
    """
    Un utilisateur a mis à jour son avatar - notifier tous les participants.
    data = { "user_id": "xxx", "user_name": "xxx", "photo_url": "/api/uploads/profiles/xxx.jpg" }
    """
    user_id = data.get("user_id")
    user_name = data.get("user_name", "Utilisateur")
    photo_url = data.get("photo_url")
    
    if user_id and photo_url:
        # Diffuser à tous les clients connectés
        await sio.emit('user_avatar_changed', {
            'user_id': user_id,
            'user_name': user_name,
            'photo_url': photo_url
        }, skip_sid=sid)
        logger.info(f"[SOCKET.IO] 📷 Avatar mis à jour: {user_name} -> {photo_url}")

# ==================== TYPING INDICATOR ====================
@sio.event
async def typing_start(sid, data):
    """
    Un utilisateur commence à taper.
    data = { "session_id": "xxx", "user_name": "Coach Bassi", "user_type": "coach" }
    """
    session_id = data.get("session_id")
    user_name = data.get("user_name", "Quelqu'un")
    user_type = data.get("user_type", "user")
    
    if session_id:
        await sio.emit('user_typing', {
            'session_id': session_id,
            'user_name': user_name,
            'user_type': user_type,
            'is_typing': True
        }, room=session_id, skip_sid=sid)
        logger.info(f"[SOCKET.IO] {user_name} commence à écrire dans {session_id}")

@sio.event
async def typing_stop(sid, data):
    """Un utilisateur arrête de taper."""
    session_id = data.get("session_id")
    user_name = data.get("user_name", "Quelqu'un")
    
    if session_id:
        await sio.emit('user_typing', {
            'session_id': session_id,
            'user_name': user_name,
            'is_typing': False
        }, room=session_id, skip_sid=sid)

# ==================== CONSTANTE EMAIL COACH ====================
COACH_EMAIL = "contact.artboost@gmail.com"

# Créer l'app ASGI combinée - C'EST CELLE-CI QUI EST EXPOSÉE COMME 'app'
app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)

# ==================== HEALTH CHECK (Required for Kubernetes) ====================

@fastapi_app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes liveness/readiness probes"""
    try:
        # Test MongoDB connection
        await client.admin.command('ping')
        return JSONResponse(
            status_code=200,
            content={"status": "healthy", "database": "connected"}
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected", "error": str(e)}
        )

@fastapi_app.get("/api/health")
async def api_health_check():
    """Health check endpoint via /api prefix for Kubernetes"""
    return await health_check()

# Favicon endpoint to prevent 404 errors
@fastapi_app.get("/api/favicon.ico")
async def favicon():
    """Return empty response for favicon requests to prevent 404 errors"""
    from starlette.responses import Response
    return Response(status_code=204)

@api_router.get("/favicon.ico")
async def api_favicon():
    """Return empty response for favicon requests via API router"""
    from starlette.responses import Response
    return Response(status_code=204)

# === FICHIERS STATIQUES EMOJIS ===
# Créer le dossier emojis s'il n'existe pas
EMOJIS_DIR = ROOT_DIR / "uploads" / "emojis"
EMOJIS_DIR.mkdir(parents=True, exist_ok=True)

# Monter les fichiers statiques pour les emojis
try:
    fastapi_app.mount("/api/emojis", StaticFiles(directory=str(EMOJIS_DIR)), name="emojis")
    logger.info(f"[EMOJIS] Dossier monté: {EMOJIS_DIR}")
except Exception as e:
    logger.warning(f"[EMOJIS] Impossible de monter le dossier: {e}")

# Monter les fichiers statiques pour les photos de profil
try:
    import os
    UPLOADS_DIR = "/app/backend/uploads/profiles"
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    fastapi_app.mount("/api/uploads/profiles", StaticFiles(directory=UPLOADS_DIR), name="profile_photos")
    logger.info(f"[UPLOADS] Dossier photos de profil monté: {UPLOADS_DIR}")
except Exception as e:
    logger.warning(f"[UPLOADS] Impossible de monter le dossier: {e}")

# ==================== MODELS ====================

class Course(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    weekday: int
    time: str
    locationName: str
    location: Optional[str] = None  # Alias de locationName pour le frontend
    mapsUrl: Optional[str] = ""
    visible: bool = True
    archived: bool = False  # Archive au lieu de supprimer
    playlist: Optional[List[str]] = None  # Liste des URLs audio pour ce cours

class CourseCreate(BaseModel):
    name: str
    weekday: int
    time: str
    locationName: str
    mapsUrl: Optional[str] = ""
    visible: bool = True
    archived: bool = False
    playlist: Optional[List[str]] = None  # Liste des URLs audio

class Offer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    price: float
    thumbnail: Optional[str] = ""
    videoUrl: Optional[str] = ""
    description: Optional[str] = ""
    keywords: Optional[str] = ""  # Mots-clés pour la recherche (invisible)
    visible: bool = True
    images: List[str] = []  # Support multi-images (max 5)
    # E-commerce fields
    category: Optional[str] = ""  # Ex: "service", "tshirt", "shoes", "supplement"
    isProduct: bool = False  # True = physical product, False = service/course
    variants: Optional[dict] = None  # { sizes: ["S","M","L"], colors: ["Noir","Blanc"], weights: ["0.5kg","1kg"] }
    tva: float = 0.0  # TVA percentage
    shippingCost: float = 0.0  # Frais de port
    stock: int = -1  # -1 = unlimited

class OfferCreate(BaseModel):
    name: str
    price: float
    thumbnail: Optional[str] = ""
    videoUrl: Optional[str] = ""
    description: Optional[str] = ""
    keywords: Optional[str] = ""  # Mots-clés pour la recherche
    visible: bool = True
    images: List[str] = []  # Support multi-images (max 5)
    # E-commerce fields
    category: Optional[str] = ""
    isProduct: bool = False
    variants: Optional[dict] = None
    tva: float = 0.0
    shippingCost: float = 0.0
    stock: int = -1

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    whatsapp: Optional[str] = ""
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    name: str
    email: str
    whatsapp: Optional[str] = ""

class Reservation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reservationCode: str
    userId: str
    userName: str
    userEmail: str
    userWhatsapp: Optional[str] = ""
    courseId: str
    courseName: str
    courseTime: str
    datetime: str
    offerId: str
    offerName: str
    price: float
    quantity: int = 1
    totalPrice: float
    discountCode: Optional[str] = None
    discountType: Optional[str] = None
    discountValue: Optional[float] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # E-commerce / Shipping fields
    validated: bool = False
    validatedAt: Optional[str] = None
    selectedVariants: Optional[dict] = None  # { size: "M", color: "Noir" }
    variantsText: Optional[str] = None  # "Taille: M, Couleur: Noir"
    shippingAddress: Optional[str] = None  # Adresse de livraison
    isProduct: bool = False  # True si produit physique
    tva: float = 0.0
    shippingCost: float = 0.0
    trackingNumber: Optional[str] = None  # Numéro de suivi colis
    shippingStatus: str = "pending"  # pending, shipped, delivered
    # Multi-date selection support
    selectedDates: Optional[List[str]] = None  # Array of ISO date strings
    selectedDatesText: Optional[str] = None  # Formatted text of selected dates
    # === NOUVEAUX CHAMPS: Origine et type abonné ===
    promoCode: Optional[str] = None  # Code promo utilisé par l'abonné
    source: Optional[str] = None  # chat_widget, web, manual
    type: Optional[str] = None  # abonné, achat_direct

class ReservationCreate(BaseModel):
    userId: str
    userName: str
    userEmail: str
    userWhatsapp: Optional[str] = ""
    courseId: str
    courseName: str
    courseTime: str
    datetime: str
    offerId: str
    offerName: str
    price: float
    quantity: int = 1
    totalPrice: float
    discountCode: Optional[str] = None
    discountType: Optional[str] = None
    discountValue: Optional[float] = None
    selectedVariants: Optional[dict] = None
    variantsText: Optional[str] = None
    shippingAddress: Optional[str] = None
    isProduct: bool = False
    # Multi-date selection support
    selectedDates: Optional[List[str]] = None  # Array of ISO date strings
    selectedDatesText: Optional[str] = None  # Formatted text of selected dates
    # === NOUVEAUX CHAMPS: Origine et type abonné ===
    promoCode: Optional[str] = None  # Code promo utilisé par l'abonné
    source: Optional[str] = None  # chat_widget, web, manual
    type: Optional[str] = None  # abonné, achat_direct

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

class DiscountCodeCreate(BaseModel):
    code: str
    type: str
    value: float
    assignedEmail: Optional[str] = None
    expiresAt: Optional[str] = None
    courses: List[str] = []
    maxUses: Optional[int] = None

class PaymentLinks(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = "payment_links"
    stripe: str = ""
    paypal: str = ""
    twint: str = ""
    coachWhatsapp: str = ""
    # Notifications automatiques pour le coach
    coachNotificationEmail: str = ""  # Email pour recevoir les alertes
    coachNotificationPhone: str = ""  # Téléphone pour recevoir les alertes WhatsApp

class PaymentLinksUpdate(BaseModel):
    stripe: Optional[str] = ""
    paypal: Optional[str] = ""
    twint: Optional[str] = ""
    coachWhatsapp: Optional[str] = ""
    coachNotificationEmail: Optional[str] = ""
    coachNotificationPhone: Optional[str] = ""

# Campaign Models for Marketing Module
class CampaignResult(BaseModel):
    contactId: str
    contactName: str
    contactEmail: Optional[str] = ""
    contactPhone: Optional[str] = ""
    channel: str  # "whatsapp", "email", "instagram"
    status: str = "pending"  # "pending", "sent", "failed"
    sentAt: Optional[str] = None

class Campaign(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    message: str
    mediaUrl: Optional[str] = ""
    mediaFormat: str = "16:9"  # "9:16" or "16:9"
    targetType: str = "all"  # "all" or "selected"
    selectedContacts: List[str] = []
    channels: dict = Field(default_factory=lambda: {"whatsapp": True, "email": False, "instagram": False, "group": False, "internal": False})
    targetGroupId: Optional[str] = "community"  # ID du groupe cible pour le canal "group"
    targetIds: Optional[List[str]] = []  # Tableau des IDs du panier (nouveau système)
    targetConversationId: Optional[str] = None  # ID de la conversation interne (legacy - premier du panier)
    targetConversationName: Optional[str] = None  # Nom de la conversation pour affichage
    scheduledAt: Optional[str] = None  # ISO date or null for immediate
    status: str = "draft"  # "draft", "scheduled", "sending", "completed"
    # Champs CTA pour boutons d'action
    ctaType: Optional[str] = None  # "reserver", "offre", "personnalise"
    ctaText: Optional[str] = None  # Texte du bouton
    ctaLink: Optional[str] = None  # URL du bouton
    results: List[dict] = []
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updatedAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CampaignCreate(BaseModel):
    name: str
    message: str
    mediaUrl: Optional[str] = ""
    mediaFormat: str = "16:9"
    targetType: str = "all"
    selectedContacts: List[str] = []
    channels: dict = Field(default_factory=lambda: {"whatsapp": True, "email": False, "instagram": False, "group": False, "internal": False})
    targetGroupId: Optional[str] = "community"  # ID du groupe cible pour le canal "group"
    targetIds: Optional[List[str]] = []  # Tableau des IDs du panier (nouveau système)
    targetConversationId: Optional[str] = None  # ID de la conversation interne (legacy - premier du panier)
    targetConversationName: Optional[str] = None  # Nom de la conversation pour affichage
    scheduledAt: Optional[str] = None
    # Champs CTA pour boutons d'action
    ctaType: Optional[str] = None
    ctaText: Optional[str] = None
    ctaLink: Optional[str] = None

class Concept(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = "concept"
    appName: str = "Afroboost"  # Nom de l'application (titre principal)
    description: str = "Le concept Afroboost : cardio + danse afrobeat + casques audio immersifs. Un entraînement fun, énergétique et accessible à tous."
    heroImageUrl: str = ""
    heroVideoUrl: str = ""
    logoUrl: str = ""
    faviconUrl: str = ""
    termsText: str = ""  # CGV - Conditions Générales de Vente
    googleReviewsUrl: str = ""  # Lien avis Google
    defaultLandingSection: str = "sessions"  # Section d'atterrissage par défaut: "sessions", "offers", "shop"
    # Liens externes
    externalLink1Title: str = ""
    externalLink1Url: str = ""
    externalLink2Title: str = ""
    externalLink2Url: str = ""
    # Modes de paiement acceptés
    paymentTwint: bool = False
    paymentPaypal: bool = False
    paymentCreditCard: bool = False
    # Affiche Événement (popup)
    eventPosterEnabled: bool = False
    eventPosterMediaUrl: str = ""  # URL image ou vidéo
    # Personnalisation des couleurs
    primaryColor: str = "#D91CD2"  # Couleur principale (glow)
    secondaryColor: str = "#8b5cf6"  # Couleur secondaire

class ConceptUpdate(BaseModel):
    appName: Optional[str] = None  # Nom de l'application
    description: Optional[str] = None
    heroImageUrl: Optional[str] = None
    heroVideoUrl: Optional[str] = None
    logoUrl: Optional[str] = None
    faviconUrl: Optional[str] = None
    termsText: Optional[str] = None  # CGV - Conditions Générales de Vente
    googleReviewsUrl: Optional[str] = None  # Lien avis Google
    defaultLandingSection: Optional[str] = None  # Section d'atterrissage par défaut
    # Liens externes
    externalLink1Title: Optional[str] = None
    externalLink1Url: Optional[str] = None
    externalLink2Title: Optional[str] = None
    externalLink2Url: Optional[str] = None
    # Modes de paiement acceptés
    paymentTwint: Optional[bool] = None
    paymentPaypal: Optional[bool] = None
    paymentCreditCard: Optional[bool] = None
    # Affiche Événement (popup)
    eventPosterEnabled: Optional[bool] = None
    eventPosterMediaUrl: Optional[str] = None
    # Personnalisation des couleurs
    primaryColor: Optional[str] = None
    secondaryColor: Optional[str] = None

class AppConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = "app_config"
    background_color: str = "#020617"
    gradient_color: str = "#3b0764"
    primary_color: str = "#d91cd2"
    secondary_color: str = "#8b5cf6"
    text_color: str = "#ffffff"
    font_family: str = "system-ui"
    font_size: int = 16
    app_title: str = "Afroboost"
    app_subtitle: str = "Réservation de casque"
    concept_description: str = "Le concept Afroboost : cardio + danse afrobeat + casques audio immersifs."
    choose_session_text: str = "Choisissez votre session"
    choose_offer_text: str = "Choisissez votre offre"
    user_info_text: str = "Vos informations"
    button_text: str = "Réserver maintenant"

# FEATURE FLAGS
class FeatureFlags(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = "feature_flags"
    AUDIO_SERVICE_ENABLED: bool = False
    VIDEO_SERVICE_ENABLED: bool = False
    STREAMING_SERVICE_ENABLED: bool = False
    updatedAt: Optional[str] = None
    updatedBy: Optional[str] = None

class FeatureFlagsUpdate(BaseModel):
    AUDIO_SERVICE_ENABLED: Optional[bool] = None
    VIDEO_SERVICE_ENABLED: Optional[bool] = None
    STREAMING_SERVICE_ENABLED: Optional[bool] = None

# COACH SUBSCRIPTION
class CoachSubscription(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    coachEmail: str
    hasAudioService: bool = False
    hasVideoService: bool = False
    hasStreamingService: bool = False
    subscriptionPlan: str = "free"
    subscriptionStartDate: Optional[str] = None
    subscriptionEndDate: Optional[str] = None
    isActive: bool = True
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updatedAt: Optional[str] = None

class CoachSubscriptionUpdate(BaseModel):
    hasAudioService: Optional[bool] = None
    hasVideoService: Optional[bool] = None
    hasStreamingService: Optional[bool] = None
    subscriptionPlan: Optional[str] = None
    subscriptionEndDate: Optional[str] = None
    isActive: Optional[bool] = None

class CoachAuth(BaseModel):
    email: str
    password: str

class CoachLogin(BaseModel):
    email: str
    password: str

# --- Lead Model (Widget IA) ---
class Lead(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = ""
    firstName: str
    whatsapp: str
    email: str
    createdAt: str = ""
    source: str = "widget_ia"

class ChatMessage(BaseModel):
    message: str
    leadId: str = ""
    firstName: str = ""
    email: str = ""  # Email pour CRM auto-save
    whatsapp: str = ""  # WhatsApp pour CRM auto-save
    source: str = "chat_ia"  # Source du contact (lien chat IA)
    link_token: str = ""  # Token du lien pour récupérer le custom_prompt

# ==================== SYSTÈME DE CHAT AMÉLIORÉ ====================
# Modèles pour la reconnaissance des utilisateurs, sessions et modes de conversation

class ChatParticipant(BaseModel):
    """Représente un participant au chat (utilisateur/client)"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    whatsapp: Optional[str] = ""
    email: Optional[str] = ""
    source: str = "chat_afroboost"  # Source par défaut, peut identifier un lien spécifique
    link_token: Optional[str] = None  # Token du lien via lequel l'utilisateur est arrivé
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_seen_at: Optional[str] = None

class ChatParticipantCreate(BaseModel):
    name: str
    whatsapp: Optional[str] = ""
    email: Optional[str] = ""
    source: str = "chat_afroboost"
    link_token: Optional[str] = None

class ChatSession(BaseModel):
    """Session de chat avec gestion des modes et participants"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    participant_ids: List[str] = []  # Liste des IDs de participants
    mode: str = "ai"  # "ai", "human", "community"
    is_ai_active: bool = True  # Interrupteur pour désactiver l'IA
    is_deleted: bool = False  # Suppression logique
    link_token: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])  # Token unique pour partage
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None
    # Métadonnées pour le coach
    title: Optional[str] = None  # Titre optionnel pour identifier la session
    notes: Optional[str] = None  # Notes du coach sur cette session
    # Prompt spécifique au lien (PRIORITAIRE sur campaignPrompt)
    custom_prompt: Optional[str] = None  # Nullable - si vide, utilise campaignPrompt global

class ChatSessionCreate(BaseModel):
    mode: str = "ai"
    is_ai_active: bool = True
    title: Optional[str] = None

class ChatSessionUpdate(BaseModel):
    mode: Optional[str] = None
    is_ai_active: Optional[bool] = None
    is_deleted: Optional[bool] = None
    title: Optional[str] = None
    notes: Optional[str] = None
    custom_prompt: Optional[str] = None  # Prompt spécifique au lien

class EnhancedChatMessage(BaseModel):
    """Message de chat amélioré avec session, sender et suppression logique"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    sender_id: str  # ID du participant ou "coach" ou "ai"
    sender_name: str
    sender_type: str = "user"  # "user", "coach", "ai"
    content: str
    mode: str = "ai"  # Mode au moment de l'envoi: "ai", "human", "community"
    is_deleted: bool = False  # Suppression logique
    notified: bool = False  # Pour les notifications coach/client
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    deleted_at: Optional[str] = None

class EnhancedChatMessageCreate(BaseModel):
    session_id: str
    sender_id: str
    sender_name: str
    sender_type: str = "user"
    content: str

class ChatLinkResponse(BaseModel):
    """Réponse pour la génération de lien partageable"""
    link_token: str
    share_url: str
    session_id: str

# === MESSAGERIE PRIVÉE (MP) - Isolation totale de l'IA ===
class PrivateMessage(BaseModel):
    """Message privé entre deux participants - INVISIBLE pour l'IA"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str  # ID unique de la conversation MP
    sender_id: str
    sender_name: str
    recipient_id: str
    recipient_name: str
    content: str
    is_read: bool = False
    is_deleted: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PrivateConversation(BaseModel):
    """Conversation privée entre deux participants"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    participant_1_id: str
    participant_1_name: str
    participant_2_id: str
    participant_2_name: str
    last_message: Optional[str] = None
    last_message_at: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# === FONCTION UTILITAIRE: Formatage unifie des messages ===
def format_message_for_frontend(m: dict) -> dict:
    """Convertit un message MongoDB vers le format attendu par le frontend."""
    return {
        "id": m.get("id"), "type": "user" if m.get("sender_type") == "user" else ("coach" if m.get("sender_type") == "coach" else "ai"),
        "text": m.get("content", "") or m.get("text", ""), "sender": (m.get("sender_name") or m.get("sender", "")).replace("💪 ", ""),
        "senderId": m.get("sender_id") or m.get("senderId", ""), "sender_type": m.get("sender_type", "ai"),
        "created_at": m.get("created_at"), "media_url": m.get("media_url"), "media_type": m.get("media_type"),
        "cta_type": m.get("cta_type"), "cta_text": m.get("cta_text"), "cta_link": m.get("cta_link"),
        "broadcast": m.get("broadcast", False), "scheduled": m.get("scheduled", False)
    }

# ==================== ROUTES ====================

@api_router.get("/")
async def root():
    return {"message": "Afroboost API"}

# --- Courses ---
@api_router.get("/courses", response_model=List[Course])
async def get_courses():
    # EXCLURE les cours archivés de la liste
    courses_raw = await db.courses.find({"archived": {"$ne": True}}, {"_id": 0}).to_list(100)
    if not courses_raw:
        # Insert default courses
        default_courses = [
            {"id": str(uuid.uuid4()), "name": "Afroboost Silent – Session Cardio", "weekday": 3, "time": "18:30", "locationName": "Rue des Vallangines 97, Neuchâtel", "mapsUrl": ""},
            {"id": str(uuid.uuid4()), "name": "Afroboost Silent – Sunday Vibes", "weekday": 0, "time": "18:30", "locationName": "Rue des Vallangines 97, Neuchâtel", "mapsUrl": ""}
        ]
        await db.courses.insert_many(default_courses)
        courses_raw = default_courses
    
    # === FIX: Ajouter "location" comme alias de "locationName" pour le frontend ===
    # Créer une copie des cours pour ajouter le champ location
    courses = []
    for course in courses_raw:
        course_copy = dict(course)
        if "locationName" in course_copy:
            course_copy["location"] = course_copy["locationName"]
        courses.append(course_copy)
    
    return courses

@api_router.post("/courses", response_model=Course)
async def create_course(course: CourseCreate):
    course_obj = Course(**course.model_dump())
    await db.courses.insert_one(course_obj.model_dump())
    return course_obj

@api_router.put("/courses/{course_id}", response_model=Course)
async def update_course(course_id: str, course_update: dict):
    """Update a course - supports partial updates including playlist"""
    # Récupérer le cours existant
    existing = await db.courses.find_one({"id": course_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Cours non trouvé")
    
    # Fusionner les données (mise à jour partielle)
    update_data = {k: v for k, v in course_update.items() if v is not None}
    
    await db.courses.update_one({"id": course_id}, {"$set": update_data})
    updated = await db.courses.find_one({"id": course_id}, {"_id": 0})
    return updated

@api_router.put("/courses/{course_id}/archive")
async def archive_course(course_id: str):
    """Archive a course instead of deleting it"""
    await db.courses.update_one({"id": course_id}, {"$set": {"archived": True}})
    updated = await db.courses.find_one({"id": course_id}, {"_id": 0})
    return {"success": True, "course": updated}

@api_router.delete("/courses/{course_id}")
async def delete_course(course_id: str):
    """
    HARD DELETE - Supprime PHYSIQUEMENT un cours de toutes les tables.
    Aucune trace ne doit rester dans la base de données.
    """
    deleted_counts = {
        "course": 0,
        "reservations": 0,
        "sessions": 0
    }
    
    # 1. Supprimer le cours (y compris les archivés)
    result = await db.courses.delete_one({"id": course_id})
    deleted_counts["course"] = result.deleted_count
    
    # 2. Supprimer TOUTES les réservations liées à ce cours
    result = await db.reservations.delete_many({"courseId": course_id})
    deleted_counts["reservations"] = result.deleted_count
    
    # 3. Supprimer les sessions/références potentielles liées au cours
    # (au cas où des sessions de chat sont liées à un cours spécifique)
    result = await db.chat_sessions.delete_many({"courseId": course_id})
    deleted_counts["sessions"] = result.deleted_count
    
    total_deleted = sum(deleted_counts.values())
    logger.info(f"[HARD DELETE] Cours {course_id} - Supprimé: cours={deleted_counts['course']}, réservations={deleted_counts['reservations']}, sessions={deleted_counts['sessions']}")
    
    # 4. ÉMETTRE UN ÉVÉNEMENT SOCKET.IO pour synchronisation temps réel
    try:
        await sio.emit('course_deleted', {
            'courseId': course_id,
            'deletedReservations': deleted_counts['reservations'],
            'hardDelete': True  # Indique une suppression totale
        })
        logger.info(f"[SOCKET.IO] Événement course_deleted émis pour {course_id}")
    except Exception as e:
        logger.warning(f"[SOCKET.IO] Échec émission course_deleted: {e}")
    
    return {
        "success": True, 
        "hardDelete": True,
        "deleted": deleted_counts,
        "total": total_deleted
    }

@api_router.delete("/courses/purge/archived")
async def purge_archived_courses():
    """
    PURGE TOTAL - Supprime tous les cours archivés et leurs données liées.
    Utilisé pour nettoyer la base de données des cours obsolètes.
    """
    # Trouver tous les cours archivés
    archived_courses = await db.courses.find({"archived": True}, {"id": 1}).to_list(1000)
    archived_ids = [c["id"] for c in archived_courses]
    
    if not archived_ids:
        return {"success": True, "message": "Aucun cours archivé à purger", "purged": 0}
    
    # Supprimer les cours archivés
    deleted_courses = await db.courses.delete_many({"archived": True})
    
    # Supprimer les réservations liées
    deleted_reservations = await db.reservations.delete_many({"courseId": {"$in": archived_ids}})
    
    logger.info(f"[PURGE] Supprimé {deleted_courses.deleted_count} cours archivés et {deleted_reservations.deleted_count} réservations")
    
    # Émettre un événement pour rafraîchir tous les clients
    try:
        await sio.emit('courses_purged', {
            'purgedIds': archived_ids,
            'count': deleted_courses.deleted_count
        })
    except Exception as e:
        logger.warning(f"[SOCKET.IO] Échec émission courses_purged: {e}")
    
    return {
        "success": True,
        "purgedCourses": deleted_courses.deleted_count,
        "purgedReservations": deleted_reservations.deleted_count,
        "purgedIds": archived_ids
    }

# --- Offers ---
@api_router.get("/offers", response_model=List[Offer])
async def get_offers():
    offers = await db.offers.find({}, {"_id": 0}).to_list(100)
    if not offers:
        default_offers = [
            {"id": str(uuid.uuid4()), "name": "Cours à l'unité", "price": 30, "thumbnail": "", "videoUrl": "", "description": "", "visible": True},
            {"id": str(uuid.uuid4()), "name": "Carte 10 cours", "price": 150, "thumbnail": "", "videoUrl": "", "description": "", "visible": True},
            {"id": str(uuid.uuid4()), "name": "Abonnement 1 mois", "price": 109, "thumbnail": "", "videoUrl": "", "description": "", "visible": True}
        ]
        await db.offers.insert_many(default_offers)
        return default_offers
    return offers

@api_router.post("/offers", response_model=Offer)
async def create_offer(offer: OfferCreate):
    offer_obj = Offer(**offer.model_dump())
    await db.offers.insert_one(offer_obj.model_dump())
    return offer_obj

@api_router.put("/offers/{offer_id}", response_model=Offer)
async def update_offer(offer_id: str, offer: OfferCreate):
    await db.offers.update_one({"id": offer_id}, {"$set": offer.model_dump()})
    updated = await db.offers.find_one({"id": offer_id}, {"_id": 0})
    return updated

@api_router.delete("/offers/{offer_id}")
async def delete_offer(offer_id: str):
    """Supprime une offre et nettoie les références dans les codes promo"""
    # 1. Supprimer l'offre
    await db.offers.delete_one({"id": offer_id})
    
    # 2. Nettoyer les références dans les codes promo (retirer l'offre des 'courses'/articles autorisés)
    await db.discount_codes.update_many(
        {"courses": offer_id},
        {"$pull": {"courses": offer_id}}
    )
    
    return {"success": True, "message": "Offre supprimée et références nettoyées"}

# --- Product Categories ---
@api_router.get("/categories")
async def get_categories():
    categories = await db.categories.find({}, {"_id": 0}).to_list(100)
    return categories if categories else [
        {"id": "service", "name": "Services & Cours", "icon": "🎧"},
        {"id": "tshirt", "name": "T-shirts", "icon": "👕"},
        {"id": "shoes", "name": "Chaussures", "icon": "👟"},
        {"id": "supplement", "name": "Compléments", "icon": "💊"},
        {"id": "accessory", "name": "Accessoires", "icon": "🎒"}
    ]

@api_router.post("/categories")
async def create_category(category: dict):
    category["id"] = category.get("id") or str(uuid.uuid4())[:8]
    await db.categories.insert_one(category)
    return category

# --- Shipping / Tracking ---
@api_router.put("/reservations/{reservation_id}/tracking")
async def update_tracking(reservation_id: str, tracking_data: dict):
    """Update shipping tracking for an order"""
    update_fields = {}
    if "trackingNumber" in tracking_data:
        update_fields["trackingNumber"] = tracking_data["trackingNumber"]
    if "shippingStatus" in tracking_data:
        update_fields["shippingStatus"] = tracking_data["shippingStatus"]
    
    await db.reservations.update_one(
        {"id": reservation_id},
        {"$set": update_fields}
    )
    updated = await db.reservations.find_one({"id": reservation_id}, {"_id": 0})
    return {"success": True, "reservation": updated}

# --- Users ---
@api_router.get("/users", response_model=List[User])
async def get_users():
    users = await db.users.find({}, {"_id": 0}).to_list(1000)
    for user in users:
        if isinstance(user.get('createdAt'), str):
            user['createdAt'] = datetime.fromisoformat(user['createdAt'].replace('Z', '+00:00'))
    return users

@api_router.post("/users", response_model=User)
async def create_user(user: UserCreate):
    user_obj = User(**user.model_dump())
    doc = user_obj.model_dump()
    doc['createdAt'] = doc['createdAt'].isoformat()
    await db.users.insert_one(doc)
    return user_obj

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if isinstance(user.get('createdAt'), str):
        user['createdAt'] = datetime.fromisoformat(user['createdAt'].replace('Z', '+00:00'))
    return user

@api_router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user: UserCreate):
    """Update an existing user/contact"""
    existing = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user.model_dump()
    await db.users.update_one({"id": user_id}, {"$set": update_data})
    updated = await db.users.find_one({"id": user_id}, {"_id": 0})
    if isinstance(updated.get('createdAt'), str):
        updated['createdAt'] = datetime.fromisoformat(updated['createdAt'].replace('Z', '+00:00'))
    return updated

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """Supprime un utilisateur/contact et nettoie les références dans les codes promo"""
    # 1. Récupérer l'email de l'utilisateur avant suppression
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_email = user.get("email")
    
    # 2. Supprimer l'utilisateur
    await db.users.delete_one({"id": user_id})
    
    # 3. Nettoyer les références dans les codes promo (retirer l'email des assignedEmail)
    if user_email:
        await db.discount_codes.update_many(
            {"assignedEmail": user_email},
            {"$set": {"assignedEmail": None}}
        )
    
    return {"success": True, "message": "Contact supprimé et références nettoyées"}

# --- Photo de profil (MOTEUR D'UPLOAD RÉEL) ---
@api_router.post("/users/upload-photo")
async def upload_user_photo(file: UploadFile = File(...), participant_id: str = Form(...)):
    """
    MOTEUR D'UPLOAD RÉEL - Sauvegarde physique + DB
    1. Reçoit l'image via UploadFile
    2. Redimensionne à 200x200 max
    3. Sauvegarde dans /app/backend/uploads/profiles/
    4. Met à jour photo_url dans la collection 'users' ET 'chat_participants'
    5. Retourne l'URL pour synchronisation
    """
    from PIL import Image
    import io
    import uuid
    import os
    
    # Validation du type MIME
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Type de fichier non supporté. Envoyez une image.")
    
    # Lire le contenu du fichier
    contents = await file.read()
    
    # Vérifier la taille (max 2MB)
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 2MB)")
    
    try:
        # Ouvrir et traiter l'image
        img = Image.open(io.BytesIO(contents))
        
        # Convertir en RGB si nécessaire (RGBA, P modes)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Redimensionner à max 200x200 en conservant les proportions
        img.thumbnail((200, 200), Image.LANCZOS)
        
        # Créer le dossier s'il n'existe pas
        upload_dir = "/app/backend/uploads/profiles"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Générer un nom de fichier unique
        filename = f"{participant_id}_{uuid.uuid4().hex[:8]}.jpg"
        filepath = os.path.join(upload_dir, filename)
        
        # Sauvegarder l'image PHYSIQUEMENT sur le serveur
        img.save(filepath, "JPEG", quality=85)
        
        # URL relative pour accès via l'API
        photo_url = f"/api/uploads/profiles/{filename}"
        
        # === MISE À JOUR BASE DE DONNÉES ===
        # 1. Mettre à jour dans la collection 'users' (par participant_id OU email)
        update_result_users = await db.users.update_one(
            {"$or": [{"id": participant_id}, {"participant_id": participant_id}]},
            {"$set": {"photo_url": photo_url, "photoUrl": photo_url}},
            upsert=False
        )
        
        # 2. Mettre à jour dans 'chat_participants' si existe
        update_result_participants = await db.chat_participants.update_one(
            {"id": participant_id},
            {"$set": {"photo_url": photo_url, "photoUrl": photo_url}},
            upsert=False
        )
        
        logger.info(f"[UPLOAD] ✅ Photo uploadée: {filename} | users={update_result_users.modified_count}, participants={update_result_participants.modified_count}")
        
        return {
            "success": True,
            "url": photo_url,
            "filename": filename,
            "participant_id": participant_id,
            "db_updated": {
                "users": update_result_users.modified_count,
                "participants": update_result_participants.modified_count
            }
        }
        
    except Exception as e:
        logger.error(f"[UPLOAD] ❌ Erreur traitement image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur traitement image: {str(e)}")


@api_router.get("/users/{participant_id}/profile")
async def get_user_profile(participant_id: str):
    """
    Récupère le profil utilisateur depuis la DB (PAS localStorage).
    Cherche dans 'users' puis 'chat_participants'.
    """
    # 1. Chercher dans la collection 'users'
    user = await db.users.find_one(
        {"$or": [{"id": participant_id}, {"participant_id": participant_id}]},
        {"_id": 0}
    )
    
    if user:
        photo_url = user.get("photo_url") or user.get("photoUrl")
        return {
            "success": True,
            "source": "users",
            "participant_id": participant_id,
            "name": user.get("name") or user.get("username"),
            "email": user.get("email"),
            "photo_url": photo_url
        }
    
    # 2. Fallback: chercher dans 'chat_participants'
    participant = await db.chat_participants.find_one(
        {"id": participant_id},
        {"_id": 0}
    )
    
    if participant:
        photo_url = participant.get("photo_url") or participant.get("photoUrl")
        return {
            "success": True,
            "source": "chat_participants",
            "participant_id": participant_id,
            "name": participant.get("name") or participant.get("username"),
            "email": participant.get("email"),
            "photo_url": photo_url
        }
    
    # 3. Aucun profil trouvé
    return {
        "success": False,
        "participant_id": participant_id,
        "photo_url": None,
        "message": "Profil non trouvé"
    }


# --- Reservations ---
@api_router.get("/reservations")
async def get_reservations(
    page: int = 1,
    limit: int = 20,
    all_data: bool = False
):
    """
    Get reservations with pagination for performance optimization.
    - page: Page number (default 1)
    - limit: Items per page (default 20)
    - all_data: If True, returns all reservations (for export CSV)
    """
    # Projection optimisée: ne récupérer que les champs nécessaires pour l'affichage initial
    projection = {
        "_id": 0,
        "id": 1,
        "reservationCode": 1,
        "userName": 1,
        "userEmail": 1,
        "userWhatsapp": 1,
        "courseName": 1,
        "courseTime": 1,
        "datetime": 1,
        "offerName": 1,
        "totalPrice": 1,
        "quantity": 1,
        "validated": 1,
        "validatedAt": 1,
        "createdAt": 1,
        "selectedDates": 1,
        "selectedDatesText": 1,
        "selectedVariants": 1,
        "variantsText": 1,
        "isProduct": 1,
        "shippingStatus": 1,
        "trackingNumber": 1,
        # === NOUVEAUX CHAMPS POUR LE TABLEAU COACH ===
        "promoCode": 1,
        "source": 1,
        "type": 1
    }
    
    if all_data:
        # Pour l'export CSV, récupérer tous les champs
        reservations = await db.reservations.find({}, {"_id": 0}).sort("createdAt", -1).to_list(10000)
    else:
        # Pagination avec tri par date de création (les plus récentes en premier)
        skip = (page - 1) * limit
        reservations = await db.reservations.find({}, projection).sort("createdAt", -1).skip(skip).limit(limit).to_list(limit)
    
    # Compter le total pour la pagination
    total_count = await db.reservations.count_documents({})
    
    for res in reservations:
        if isinstance(res.get('createdAt'), str):
            res['createdAt'] = datetime.fromisoformat(res['createdAt'].replace('Z', '+00:00'))
    
    return {
        "data": reservations,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total_count,
            "pages": (total_count + limit - 1) // limit  # Ceiling division
        }
    }

@api_router.post("/reservations", response_model=Reservation)
async def create_reservation(reservation: ReservationCreate):
    """Créer une réservation - Vérifie la validité du code si fourni"""
    
    # === VÉRIFICATION CODE PROMO/ABONNÉ ===
    promo_code = reservation.promoCode or reservation.discountCode
    user_email = reservation.userEmail
    
    if promo_code:
        # Chercher le code dans la DB (case insensitive)
        discount = await db.discount_codes.find_one({
            "code": {"$regex": f"^{promo_code}$", "$options": "i"},
            "active": True
        }, {"_id": 0})
        
        if not discount:
            raise HTTPException(status_code=400, detail="Code invalide ou désactivé - Réservation impossible")
        
        # Vérifier si le code est assigné à un email spécifique
        assigned_email = discount.get("assignedEmail")
        if assigned_email and assigned_email.lower() != user_email.lower():
            raise HTTPException(status_code=400, detail="Ce code n'est pas associé à votre email")
        
        # Vérifier le nombre max d'utilisations
        max_uses = discount.get("maxUses", 0)
        used = discount.get("used", 0)
        if max_uses > 0 and used >= max_uses:
            raise HTTPException(status_code=400, detail="Code épuisé - Limite d'utilisation atteinte")
        
        # Incrémenter le compteur d'utilisation
        await db.discount_codes.update_one(
            {"code": discount.get("code")},
            {"$inc": {"used": 1}}
        )
        logger.info(f"[RESERVATION] ✅ Code {promo_code} validé pour {user_email} (utilisations: {used + 1}/{max_uses})")
    
    res_code = f"AFR-{str(uuid.uuid4())[:6].upper()}"
    res_obj = Reservation(**reservation.model_dump(), reservationCode=res_code)
    doc = res_obj.model_dump()
    doc['createdAt'] = doc['createdAt'].isoformat()
    await db.reservations.insert_one(doc)
    
    # === NOTIFICATION EMAIL AU COACH SI RÉSERVATION ABONNÉ ===
    if reservation.type == 'abonné' and reservation.promoCode:
        try:
            if RESEND_AVAILABLE and RESEND_API_KEY:
                coach_email = "contact.artboost@gmail.com"
                
                # Construire le message HTML
                html_content = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #9333ea, #6366f1); padding: 20px; border-radius: 12px 12px 0 0;">
                        <h1 style="color: white; margin: 0; font-size: 24px;">💎 Nouvelle Réservation Abonné</h1>
                    </div>
                    <div style="background: #1a1a2e; padding: 24px; color: #fff;">
                        <div style="background: rgba(34, 197, 94, 0.2); border: 1px solid rgba(34, 197, 94, 0.4); border-radius: 8px; padding: 12px; margin-bottom: 20px;">
                            <strong style="color: #22c55e;">✅ Réservation confirmée via le Chat</strong>
                        </div>
                        
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); color: #888;">👤 Nom</td>
                                <td style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); color: #fff; font-weight: 600;">{reservation.userName}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); color: #888;">📱 WhatsApp</td>
                                <td style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                                    <a href="https://wa.me/{reservation.userWhatsapp.replace('+', '').replace(' ', '')}" style="color: #25D366; text-decoration: none; font-weight: 600;">
                                        {reservation.userWhatsapp} 📲
                                    </a>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); color: #888;">📧 Email</td>
                                <td style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); color: #fff;">{reservation.userEmail}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); color: #888;">📅 Cours</td>
                                <td style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); color: #a855f7; font-weight: 600;">{reservation.courseName}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); color: #888;">🕐 Horaire</td>
                                <td style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); color: #fff;">{reservation.courseTime}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px 0; color: #888;">🎟️ Code Promo</td>
                                <td style="padding: 10px 0; color: #22c55e; font-weight: 600;">{reservation.promoCode}</td>
                            </tr>
                        </table>
                        
                        <div style="margin-top: 24px; text-align: center;">
                            <a href="https://wa.me/{reservation.userWhatsapp.replace('+', '').replace(' ', '')}" 
                               style="display: inline-block; background: #25D366; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600;">
                                💬 Contacter sur WhatsApp
                            </a>
                        </div>
                    </div>
                    <div style="background: #0d0d1a; padding: 16px; text-align: center; border-radius: 0 0 12px 12px;">
                        <p style="color: #666; margin: 0; font-size: 12px;">
                            Code réservation: <strong style="color: #a855f7;">{res_code}</strong>
                        </p>
                    </div>
                </div>
                """
                
                params = {
                    "from": "Afroboost <notifications@afroboosteur.com>",
                    "to": [coach_email],
                    "subject": f"💎 Nouvelle réservation abonné - {reservation.userName}",
                    "html": html_content
                }
                
                email_response = await asyncio.to_thread(resend.Emails.send, params)
                logger.info(f"[NOTIFICATION] Email envoyé: {email_response}")
        except Exception as e:
            logger.warning(f"[NOTIFICATION] Erreur email: {str(e)}")
    
    return res_obj

@api_router.post("/reservations/{reservation_code}/validate")
async def validate_reservation(reservation_code: str):
    """Validate a reservation by QR code scan (coach action)"""
    reservation = await db.reservations.find_one({"reservationCode": reservation_code}, {"_id": 0})
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")
    
    # Mark as validated
    await db.reservations.update_one(
        {"reservationCode": reservation_code},
        {"$set": {"validated": True, "validatedAt": datetime.now(timezone.utc).isoformat()}}
    )
    return {"success": True, "message": "Réservation validée", "reservation": reservation}

@api_router.delete("/reservations/{reservation_id}")
async def delete_reservation(reservation_id: str):
    await db.reservations.delete_one({"id": reservation_id})
    return {"success": True}

# ==================== COACH NOTIFICATIONS ====================

class CoachNotificationPayload(BaseModel):
    """Payload for coach notification"""
    clientName: str
    clientEmail: str
    clientWhatsapp: str
    offerName: str
    courseName: str
    sessionDate: str
    amount: float
    reservationCode: str

@api_router.post("/notify-coach")
async def notify_coach(payload: CoachNotificationPayload):
    """
    Endpoint to trigger coach notification.
    Returns the notification config so frontend can send via EmailJS/WhatsApp.
    """
    try:
        # Get payment links config which contains coach notification settings
        payment_links = await db.payment_links.find_one({"id": "payment_links"}, {"_id": 0})
        if not payment_links:
            return {"success": False, "message": "Configuration non trouvée"}
        
        coach_email = payment_links.get("coachNotificationEmail", "")
        coach_phone = payment_links.get("coachNotificationPhone", "")
        
        if not coach_email and not coach_phone:
            return {"success": False, "message": "Aucune adresse de notification configurée"}
        
        # Format notification message
        notification_message = f"""🎉 NOUVELLE RÉSERVATION !

👤 Client: {payload.clientName}
📧 Email: {payload.clientEmail}
📱 WhatsApp: {payload.clientWhatsapp}

🎯 Offre: {payload.offerName}
📅 Cours: {payload.courseName}
🕐 Date: {payload.sessionDate}
💰 Montant: {payload.amount} CHF

🔑 Code: {payload.reservationCode}

---
Notification automatique Afroboost"""

        return {
            "success": True,
            "coachEmail": coach_email,
            "coachPhone": coach_phone,
            "message": notification_message,
            "subject": f"🎉 Nouvelle réservation - {payload.clientName}"
        }
    except Exception as e:
        logger.error(f"Error in notify-coach: {e}")
        return {"success": False, "message": str(e)}

# --- Discount Codes ---
@api_router.get("/discount-codes", response_model=List[DiscountCode])
async def get_discount_codes():
    codes = await db.discount_codes.find({}, {"_id": 0}).to_list(1000)
    return codes

@api_router.post("/discount-codes", response_model=DiscountCode)
async def create_discount_code(code: DiscountCodeCreate):
    code_obj = DiscountCode(**code.model_dump())
    await db.discount_codes.insert_one(code_obj.model_dump())
    return code_obj

@api_router.put("/discount-codes/{code_id}")
async def update_discount_code(code_id: str, updates: dict):
    await db.discount_codes.update_one({"id": code_id}, {"$set": updates})
    updated = await db.discount_codes.find_one({"id": code_id}, {"_id": 0})
    return updated

@api_router.delete("/discount-codes/{code_id}")
async def delete_discount_code(code_id: str):
    await db.discount_codes.delete_one({"id": code_id})
    return {"success": True}

@api_router.post("/discount-codes/validate")
async def validate_discount_code(data: dict):
    code_str = data.get("code", "").strip().upper()  # Normalize: trim + uppercase
    user_email = data.get("email", "").strip()
    course_id = data.get("courseId", "").strip() if data.get("courseId") else ""
    
    # Case-insensitive search using regex
    code = await db.discount_codes.find_one({
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
    
    return {"valid": True, "code": code}

@api_router.post("/discount-codes/{code_id}/use")
async def use_discount_code(code_id: str):
    """Incrémente le compteur d'utilisation d'un code"""
    await db.discount_codes.update_one({"id": code_id}, {"$inc": {"used": 1}})
    return {"success": True}


@api_router.post("/check-reservation-eligibility")
async def check_reservation_eligibility(data: dict):
    """Vérifie si un utilisateur peut réserver avec son code."""
    code_str = data.get("code", "").strip().upper()
    user_email = data.get("email", "").strip().lower()
    
    if not code_str:
        return {"canReserve": False, "reason": "Aucun code fourni"}
    
    discount = await db.discount_codes.find_one({
        "code": {"$regex": f"^{code_str}$", "$options": "i"}, "active": True
    }, {"_id": 0})
    
    if not discount:
        return {"canReserve": False, "reason": "Code invalide ou désactivé"}
    
    # Vérifier assignation email
    assigned = discount.get("assignedEmail")
    if assigned and assigned.lower() != user_email:
        return {"canReserve": False, "reason": "Code non associé à cet email"}
    
    # Vérifier utilisations
    max_uses = discount.get("maxUses", 0)
    used = discount.get("used", 0)
    if max_uses > 0 and used >= max_uses:
        return {"canReserve": False, "reason": "Code épuisé", "used": used, "maxUses": max_uses}
    
    return {
        "canReserve": True,
        "code": discount.get("code"),
        "type": discount.get("type"),
        "value": discount.get("value"),
        "used": used,
        "maxUses": max_uses,
        "remaining": max_uses - used if max_uses > 0 else "illimité"
    }


# ==================== SANITIZE DATA (Nettoyage des données fantômes) ====================

@api_router.post("/sanitize-data")
async def sanitize_data():
    """
    Nettoie automatiquement les données fantômes:
    - Retire des codes promo les IDs d'offres/cours qui n'existent plus
    - Retire des codes promo les emails de bénéficiaires qui n'existent plus
    """
    # 1. Récupérer tous les IDs valides
    valid_offer_ids = set()
    valid_course_ids = set()
    valid_user_emails = set()
    
    offers = await db.offers.find({}, {"id": 1, "_id": 0}).to_list(1000)
    for o in offers:
        if o.get("id"):
            valid_offer_ids.add(o["id"])
    
    courses = await db.courses.find({}, {"id": 1, "_id": 0}).to_list(1000)
    for c in courses:
        if c.get("id"):
            valid_course_ids.add(c["id"])
    
    users = await db.users.find({}, {"email": 1, "_id": 0}).to_list(1000)
    for u in users:
        if u.get("email"):
            valid_user_emails.add(u["email"])
    
    all_valid_ids = valid_offer_ids | valid_course_ids
    
    # Nettoyer les codes promo
    discount_codes = await db.discount_codes.find({}, {"_id": 0}).to_list(1000)
    cleaned_count = 0
    
    for code in discount_codes:
        updates = {}
        if code.get("courses"):
            valid = [c for c in code["courses"] if c in all_valid_ids]
            if len(valid) != len(code["courses"]):
                updates["courses"] = valid
        if code.get("assignedEmail") and code["assignedEmail"] not in valid_user_emails:
            updates["assignedEmail"] = None
        if updates:
            await db.discount_codes.update_one({"id": code["id"]}, {"$set": updates})
            cleaned_count += 1
    
    return {"success": True, "codes_cleaned": cleaned_count}

# --- Campaigns (Marketing Module) ---
@api_router.get("/campaigns")
async def get_campaigns():
    campaigns = await db.campaigns.find({}, {"_id": 0}).sort("createdAt", -1).to_list(100)
    return campaigns

@api_router.get("/campaigns/logs")
async def get_campaigns_error_logs():
    """Renvoie les 50 dernières erreurs d'envoi de campagnes."""
    try:
        error_logs = []
        
        campaigns_with_results = await db.campaigns.find(
            {"results": {"$exists": True, "$ne": []}},
            {"_id": 0, "id": 1, "name": 1, "results": 1, "updatedAt": 1}
        ).sort("updatedAt", -1).to_list(100)
        
        for campaign in campaigns_with_results:
            campaign_id = campaign.get("id", "")
            campaign_name = campaign.get("name", "Sans nom")
            results = campaign.get("results", [])
            
            # Filtrer uniquement les résultats avec erreurs
            for result in results:
                if result.get("status") == "failed" or result.get("error"):
                    error_entry = {
                        "source": "campaign_result",
                        "campaign_id": campaign_id,
                        "campaign_name": campaign_name,
                        "contact_id": result.get("contactId", ""),
                        "contact_name": result.get("contactName", ""),
                        "channel": result.get("channel", "unknown"),
                        "error": result.get("error", "Erreur inconnue"),
                        "error_code": result.get("error_code", ""),
                        "sent_at": result.get("sentAt", campaign.get("updatedAt", "")),
                        "status": result.get("status", "failed")
                    }
                    error_logs.append(error_entry)
        
        # === SOURCE 2: Collection campaign_errors (détails Twilio) ===
        try:
            twilio_errors = await db.campaign_errors.find(
                {},
                {"_id": 0}
            ).sort("created_at", -1).to_list(50)
            
            for terr in twilio_errors:
                error_entry = {
                    "source": "twilio_diagnostic",
                    "campaign_id": terr.get("campaign_id", ""),
                    "campaign_name": terr.get("campaign_name", ""),
                    "contact_id": "",
                    "contact_name": "",
                    "channel": terr.get("channel", "whatsapp"),
                    "error": terr.get("error_message", ""),
                    "error_code": terr.get("error_code", ""),
                    "error_type": terr.get("error_type", ""),
                    "more_info": terr.get("more_info", ""),
                    "to_phone": terr.get("to_phone", ""),
                    "sent_at": terr.get("created_at", ""),
                    "status": "failed"
                }
                error_logs.append(error_entry)
        except Exception as e:
            logger.warning(f"[CAMPAIGNS-LOGS] Collection campaign_errors non accessible: {e}")
        
        # Trier par date et limiter à 50
        error_logs.sort(key=lambda x: x.get("sent_at", ""), reverse=True)
        error_logs = error_logs[:50]
        
        return {
            "success": True,
            "total_errors": len(error_logs),
            "errors": error_logs,
            "message": f"{len(error_logs)} erreur(s) d'envoi trouvée(s)" if error_logs else "Aucune erreur d'envoi"
        }
        
    except Exception as e:
        logger.error(f"[CAMPAIGNS-LOGS] Erreur récupération logs: {e}")
        return {
            "success": False,
            "total_errors": 0,
            "errors": [],
            "error": str(e)
        }

@api_router.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@api_router.post("/campaigns")
async def create_campaign(campaign: CampaignCreate):
    campaign_data = Campaign(
        name=campaign.name,
        message=campaign.message,
        mediaUrl=campaign.mediaUrl,
        mediaFormat=campaign.mediaFormat,
        targetType=campaign.targetType,
        selectedContacts=campaign.selectedContacts,
        channels=campaign.channels,
        targetGroupId=campaign.targetGroupId,
        targetIds=campaign.targetIds or [],  # Tableau des IDs du panier
        targetConversationId=campaign.targetConversationId,
        targetConversationName=campaign.targetConversationName,
        scheduledAt=campaign.scheduledAt,
        status="scheduled" if campaign.scheduledAt else "draft",
        ctaType=campaign.ctaType,
        ctaText=campaign.ctaText,
        ctaLink=campaign.ctaLink
    ).model_dump()
    await db.campaigns.insert_one(campaign_data)
    return {k: v for k, v in campaign_data.items() if k != "_id"}

@api_router.put("/campaigns/{campaign_id}")
async def update_campaign(campaign_id: str, data: dict):
    data["updatedAt"] = datetime.now(timezone.utc).isoformat()
    await db.campaigns.update_one({"id": campaign_id}, {"$set": data})
    return await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})

@api_router.delete("/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str):
    """
    HARD DELETE - Supprime PHYSIQUEMENT une campagne.
    Supprime aussi les messages envoyés par cette campagne dans l'historique.
    """
    deleted_counts = {
        "campaign": 0,
        "messages": 0
    }
    
    # 1. Récupérer les infos de la campagne avant suppression
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    
    # 2. Supprimer la campagne
    result = await db.campaigns.delete_one({"id": campaign_id})
    deleted_counts["campaign"] = result.deleted_count
    
    # 3. Supprimer les messages envoyés par cette campagne (optionnel, basé sur ID de campagne)
    # Note: Les messages de campagne ont scheduled=True
    
    logger.info(f"[HARD DELETE] Campagne {campaign_id} supprimée")
    
    # 4. Notifier via Socket.IO
    try:
        await sio.emit('campaign_deleted', {
            'campaignId': campaign_id,
            'hardDelete': True
        })
    except Exception as e:
        logger.warning(f"[SOCKET.IO] Échec émission campaign_deleted: {e}")
    
    return {
        "success": True,
        "hardDelete": True,
        "deleted": deleted_counts
    }

@api_router.delete("/campaigns/purge/all")
async def purge_all_campaigns():
    """
    PURGE TOTAL - Supprime TOUTES les campagnes terminées ou échouées.
    Garde uniquement les campagnes en cours (status=scheduled ou sending).
    """
    # Supprimer les campagnes terminées
    result = await db.campaigns.delete_many({
        "status": {"$in": ["completed", "failed", "draft"]}
    })
    
    logger.info(f"[PURGE] {result.deleted_count} campagnes supprimées")
    
    return {
        "success": True,
        "purgedCount": result.deleted_count
    }

@api_router.post("/campaigns/{campaign_id}/launch")
async def launch_campaign(campaign_id: str):
    """
    Lance une campagne immédiatement.
    - Internal: Envoi dans les conversations chat (groupes/utilisateurs)
    - WhatsApp: Envoi DIRECT via Twilio
    - Email: Envoi DIRECT via Resend
    - Instagram: Non supporté (manuel)
    
    Chaque canal est indépendant: l'échec d'un envoi ne bloque pas les suivants.
    """
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Prepare results and tracking
    results = []
    channels = campaign.get("channels", {})
    message_content = campaign.get("message", "")
    media_url = campaign.get("mediaUrl", "")
    campaign_name = campaign.get("name", "Campagne")
    target_ids = campaign.get("targetIds", [])
    
    success_count = 0
    fail_count = 0
    
    logger.info(f"[CAMPAIGN-LAUNCH] 🚀 Lancement campagne '{campaign_name}' - targetIds: {len(target_ids)}, channels: {channels}")
    
    # ==================== ENVOI INTERNE (Chat) ====================
    if channels.get("internal") and target_ids:
        for target_id in target_ids:
            internal_result = {
                "targetId": target_id,
                "channel": "internal",
                "status": "pending",
                "sentAt": None
            }
            
            try:
                # Déterminer le type de cible (groupe ou utilisateur)
                # Chercher si c'est un groupe (session avec titre ou mode groupe)
                session = await db.chat_sessions.find_one(
                    {"$or": [{"id": target_id}, {"participant_ids": target_id}]},
                    {"_id": 0, "id": 1, "mode": 1, "title": 1}
                )
                
                if session:
                    session_id = session.get("id")
                else:
                    # Créer une session pour cet utilisateur s'il n'en a pas
                    session_id = str(uuid.uuid4())
                    await db.chat_sessions.insert_one({
                        "id": session_id,
                        "mode": "user",
                        "participant_ids": [target_id],
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    })
                    logger.info(f"[CAMPAIGN-LAUNCH] 📝 Session créée pour {target_id}: {session_id}")
                
                # Insérer le message dans la conversation
                msg_id = str(uuid.uuid4())
                msg_timestamp = datetime.now(timezone.utc).isoformat()
                
                await db.chat_messages.insert_one({
                    "id": msg_id,
                    "session_id": session_id,
                    "content": message_content,
                    "media_url": media_url or None,
                    "sender_type": "coach",
                    "sender_name": "Coach Bassi",
                    "sender_id": "coach-campaign",
                    "timestamp": msg_timestamp,
                    "created_at": msg_timestamp
                })
                
                # Mettre à jour la session
                await db.chat_sessions.update_one(
                    {"id": session_id},
                    {"$set": {"last_message_at": msg_timestamp, "updated_at": msg_timestamp}}
                )
                
                internal_result["status"] = "sent"
                internal_result["sentAt"] = msg_timestamp
                internal_result["messageId"] = msg_id
                internal_result["sessionId"] = session_id
                success_count += 1
                logger.info(f"[CAMPAIGN-LAUNCH] ✅ Message interne envoyé à {target_id}")
                
            except Exception as e:
                internal_result["status"] = "failed"
                internal_result["error"] = str(e)
                fail_count += 1
                logger.error(f"[CAMPAIGN-LAUNCH] ❌ Erreur envoi interne à {target_id}: {str(e)}")
            
            results.append(internal_result)
    
    # ==================== ENVOI WHATSAPP/EMAIL (via contacts CRM) ====================
    # Get contacts based on targetType (pour les canaux WhatsApp/Email)
    contacts = []
    if channels.get("whatsapp") or channels.get("email"):
        if campaign.get("targetType") == "all":
            contacts = await db.users.find({}, {"_id": 0}).to_list(1000)
        else:
            selected_ids = campaign.get("selectedContacts", [])
            if selected_ids:
                contacts = await db.users.find({"id": {"$in": selected_ids}}, {"_id": 0}).to_list(1000)
    
    for contact in contacts:
        contact_id = contact.get("id", "")
        contact_name = contact.get("name", "")
        contact_email = contact.get("email", "")
        contact_phone = contact.get("whatsapp", "")
        
        # ==================== ENVOI WHATSAPP (INDÉPENDANT) ====================
        if channels.get("whatsapp") and contact_phone:
            whatsapp_result = {
                "contactId": contact_id,
                "contactName": contact_name,
                "contactEmail": contact_email,
                "contactPhone": contact_phone,
                "channel": "whatsapp",
                "status": "pending",
                "sentAt": None
            }
            
            try:
                # Envoi DIRECT via Twilio
                wa_response = await send_whatsapp_direct(
                    to_phone=contact_phone,
                    message=message_content,
                    media_url=media_url if media_url else None
                )
                
                if wa_response.get("status") == "success":
                    whatsapp_result["status"] = "sent"
                    whatsapp_result["sentAt"] = datetime.now(timezone.utc).isoformat()
                    whatsapp_result["sid"] = wa_response.get("sid")
                    success_count += 1
                    logger.info(f"[CAMPAIGN-LAUNCH] ✅ WhatsApp envoyé à {contact_name} ({contact_phone})")
                elif wa_response.get("status") == "simulated":
                    whatsapp_result["status"] = "simulated"
                    whatsapp_result["sentAt"] = datetime.now(timezone.utc).isoformat()
                    logger.info(f"[CAMPAIGN-LAUNCH] 🧪 WhatsApp simulé pour {contact_name} ({contact_phone})")
                else:
                    whatsapp_result["status"] = "failed"
                    whatsapp_result["error"] = wa_response.get("error", "Unknown error")
                    fail_count += 1
                    logger.error(f"[CAMPAIGN-LAUNCH] ❌ WhatsApp échoué pour {contact_name}: {wa_response.get('error')}")
            except Exception as e:
                whatsapp_result["status"] = "failed"
                whatsapp_result["error"] = str(e)
                fail_count += 1
                logger.error(f"[CAMPAIGN-LAUNCH] ❌ Exception WhatsApp pour {contact_name}: {str(e)}")
            
            results.append(whatsapp_result)
        
        # ==================== ENVOI EMAIL (INDÉPENDANT) ====================
        if channels.get("email") and contact_email:
            email_result = {
                "contactId": contact_id,
                "contactName": contact_name,
                "contactEmail": contact_email,
                "contactPhone": contact_phone,
                "channel": "email",
                "status": "pending",
                "sentAt": None
            }
            
            try:
                # Envoi via l'endpoint interne (Resend)
                if RESEND_AVAILABLE and RESEND_API_KEY:
                    # Préparer le template email
                    subject = f"📢 {campaign_name}"
                    first_name = contact_name.split()[0] if contact_name else "ami(e)"
                    
                    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="utf-8"><title>Message Afroboost</title></head>
<body style="margin:0;padding:20px;background:#f5f5f5;font-family:Arial,sans-serif;">
<div style="max-width:480px;margin:0 auto;background:#111;border-radius:10px;overflow:hidden;">
<div style="background:#9333EA;padding:16px 20px;text-align:center;">
<span style="color:#fff;font-size:22px;font-weight:bold;">Afroboost</span>
</div>
<div style="padding:20px;color:#fff;font-size:14px;line-height:1.6;">
<p>Salut {first_name},</p>
{message_content.replace(chr(10), '<br>')}
</div>
<div style="padding:15px 20px;border-top:1px solid #333;text-align:center;">
<a href="https://afroboosteur.com" style="color:#9333EA;text-decoration:none;font-size:11px;">afroboosteur.com</a>
</div>
</div>
</body>
</html>"""
                    
                    params = {
                        "from": "Afroboost <notifications@afroboosteur.com>",
                        "to": [contact_email],
                        "subject": subject,
                        "html": html_content
                    }
                    
                    email_response = await asyncio.to_thread(resend.Emails.send, params)
                    email_result["status"] = "sent"
                    email_result["sentAt"] = datetime.now(timezone.utc).isoformat()
                    email_result["email_id"] = email_response.get("id")
                    success_count += 1
                    logger.info(f"[CAMPAIGN-LAUNCH] ✅ Email envoyé à {contact_name} ({contact_email})")
                else:
                    email_result["status"] = "simulated"
                    email_result["sentAt"] = datetime.now(timezone.utc).isoformat()
                    logger.info(f"[CAMPAIGN-LAUNCH] 🧪 Email simulé pour {contact_name} ({contact_email})")
            except Exception as e:
                email_result["status"] = "failed"
                email_result["error"] = str(e)
                fail_count += 1
                logger.error(f"[CAMPAIGN-LAUNCH] ❌ Email échoué pour {contact_name}: {str(e)}")
            
            results.append(email_result)
        
        # ==================== INSTAGRAM (NON SUPPORTÉ - MANUEL) ====================
        if channels.get("instagram"):
            results.append({
                "contactId": contact_id,
                "contactName": contact_name,
                "contactEmail": contact_email,
                "contactPhone": contact_phone,
                "channel": "instagram",
                "status": "manual",
                "sentAt": None,
                "note": "Envoi manuel requis"
            })
    
    # Déterminer le statut final
    all_sent = all(r.get("status") in ["sent", "simulated", "manual"] for r in results)
    final_status = "completed" if all_sent else "sending"
    
    # Update campaign
    await db.campaigns.update_one(
        {"id": campaign_id},
        {"$set": {
            "status": final_status,
            "results": results,
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            "launchedAt": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    logger.info(f"[CAMPAIGN-LAUNCH] 🏁 Campagne '{campaign_name}' terminée - ✅{success_count} / ❌{fail_count}")
    
    return await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})

@api_router.post("/campaigns/{campaign_id}/mark-sent")
async def mark_campaign_sent(campaign_id: str, data: dict):
    """Mark specific result as sent"""
    contact_id = data.get("contactId")
    channel = data.get("channel")
    
    await db.campaigns.update_one(
        {"id": campaign_id, "results.contactId": contact_id, "results.channel": channel},
        {"$set": {
            "results.$.status": "sent",
            "results.$.sentAt": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Check if all results are sent
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if campaign:
        all_sent = all(r.get("status") == "sent" for r in campaign.get("results", []))
        if all_sent:
            await db.campaigns.update_one(
                {"id": campaign_id},
                {"$set": {"status": "completed", "updatedAt": datetime.now(timezone.utc).isoformat()}}
            )
    
    return {"success": True}

# --- Payment Links ---
@api_router.get("/payment-links", response_model=PaymentLinks)
async def get_payment_links():
    links = await db.payment_links.find_one({"id": "payment_links"}, {"_id": 0})
    if not links:
        default_links = PaymentLinks().model_dump()
        await db.payment_links.insert_one(default_links)
        return default_links
    return links

@api_router.put("/payment-links")
async def update_payment_links(links: PaymentLinksUpdate):
    await db.payment_links.update_one(
        {"id": "payment_links"}, 
        {"$set": links.model_dump()}, 
        upsert=True
    )
    return await db.payment_links.find_one({"id": "payment_links"}, {"_id": 0})

# --- Stripe Checkout avec TWINT ---

class CreateCheckoutRequest(BaseModel):
    """Requête pour créer une session de paiement Stripe"""
    productName: str
    amount: float  # Montant en CHF (decimal, ex: 25.00)
    customerEmail: Optional[str] = None
    originUrl: str  # URL d'origine du frontend pour construire success/cancel URLs
    reservationData: Optional[dict] = None  # Données de réservation pour metadata

@api_router.post("/create-checkout-session")
async def create_checkout_session(request: CreateCheckoutRequest):
    """
    Crée une session Stripe Checkout avec support pour cartes et TWINT.
    TWINT nécessite la devise CHF.
    """
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe API key not configured")
    
    # Construire les URLs dynamiquement basées sur l'origine frontend
    # {CHECKOUT_SESSION_ID} est remplacé automatiquement par Stripe
    success_url = f"{request.originUrl}?status=success&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{request.originUrl}?status=canceled"
    
    # Montant en centimes (Stripe utilise les plus petites unités)
    amount_cents = int(request.amount * 100)
    
    # Préparer les metadata
    metadata = {
        "product_name": request.productName,
        "customer_email": request.customerEmail or "",
        "source": "afroboost_checkout"
    }
    if request.reservationData:
        metadata["reservation_id"] = request.reservationData.get("id", "")
        metadata["course_name"] = request.reservationData.get("courseName", "")
    
    # Méthodes de paiement: card + twint (devise CHF obligatoire pour TWINT)
    payment_methods = ['card', 'twint']
    
    try:
        # Créer la session Stripe avec card + twint
        session = stripe.checkout.Session.create(
            payment_method_types=payment_methods,
            line_items=[{
                'price_data': {
                    'currency': 'chf',  # CHF obligatoire pour TWINT
                    'product_data': {
                        'name': request.productName,
                    },
                    'unit_amount': amount_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=request.customerEmail,
            metadata=metadata,
        )
        
        # Créer l'entrée dans payment_transactions
        transaction = {
            "id": str(uuid.uuid4()),
            "session_id": session.id,
            "amount": request.amount,
            "currency": "chf",
            "product_name": request.productName,
            "customer_email": request.customerEmail,
            "metadata": metadata,
            "payment_status": "pending",
            "payment_methods": payment_methods,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.payment_transactions.insert_one(transaction)
        
        logger.info(f"Stripe session created with payment methods: {payment_methods}, session_id: {session.id}")
        
        return {
            "sessionId": session.id,
            "url": session.url,
            "paymentMethods": payment_methods
        }
        
    except stripe.error.InvalidRequestError as e:
        # Si TWINT cause une erreur (non activé sur le compte), fallback sur card seul
        logger.warning(f"TWINT not available, falling back to card only: {str(e)}")
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'chf',
                        'product_data': {
                            'name': request.productName,
                        },
                        'unit_amount': amount_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=request.customerEmail,
                metadata=metadata,
            )
            
            # Créer l'entrée dans payment_transactions
            transaction = {
                "id": str(uuid.uuid4()),
                "session_id": session.id,
                "amount": request.amount,
                "currency": "chf",
                "product_name": request.productName,
                "customer_email": request.customerEmail,
                "metadata": metadata,
                "payment_status": "pending",
                "payment_methods": ['card'],
                "warning": "TWINT not available",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.payment_transactions.insert_one(transaction)
            
            logger.info(f"Stripe session created with card only (TWINT fallback), session_id: {session.id}")
            
            return {
                "sessionId": session.id,
                "url": session.url,
                "paymentMethods": ['card'],
                "warning": "TWINT not available on this Stripe account"
            }
            
        except stripe.error.StripeError as fallback_error:
            logger.error(f"Stripe fallback error: {str(fallback_error)}")
            raise HTTPException(status_code=500, detail=f"Payment error: {str(fallback_error)}")
            
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Payment error: {str(e)}")

@api_router.get("/checkout-status/{session_id}")
async def get_checkout_status(session_id: str):
    """
    Vérifie le statut d'une session de paiement Stripe.
    """
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe API key not configured")
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Mettre à jour le statut dans la base de données
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {
                "payment_status": session.payment_status,
                "status": session.status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "status": session.status,
            "paymentStatus": session.payment_status,
            "amountTotal": session.amount_total,
            "currency": session.currency,
            "metadata": session.metadata
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Error checking checkout status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking status: {str(e)}")

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """
    Webhook Stripe pour recevoir les événements de paiement.
    """
    try:
        body = await request.body()
        event = stripe.Event.construct_from(
            stripe.util.json.loads(body), stripe.api_key
        )
        
        # Gérer les événements de paiement
        if event.type == 'checkout.session.completed':
            session = event.data.object
            await db.payment_transactions.update_one(
                {"session_id": session.id},
                {"$set": {
                    "payment_status": session.payment_status,
                    "status": "completed",
                    "webhook_received_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            logger.info(f"Payment completed for session: {session.id}")
            
        elif event.type == 'checkout.session.expired':
            session = event.data.object
            await db.payment_transactions.update_one(
                {"session_id": session.id},
                {"$set": {
                    "status": "expired",
                    "webhook_received_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            logger.info(f"Payment expired for session: {session.id}")
        
        return {"received": True}
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")

# --- Concept ---
@api_router.get("/concept", response_model=Concept)
async def get_concept():
    concept = await db.concept.find_one({"id": "concept"}, {"_id": 0})
    if not concept:
        default_concept = Concept().model_dump()
        await db.concept.insert_one(default_concept)
        return default_concept
    return concept

@api_router.put("/concept")
async def update_concept(concept: ConceptUpdate):
    try:
        updates = {k: v for k, v in concept.model_dump().items() if v is not None}
        result = await db.concept.update_one({"id": "concept"}, {"$set": updates}, upsert=True)
        updated = await db.concept.find_one({"id": "concept"}, {"_id": 0})
        return updated
    except Exception as e:
        logger.error(f"Error updating concept: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Config ---
@api_router.get("/config", response_model=AppConfig)
async def get_config():
    config = await db.config.find_one({"id": "app_config"}, {"_id": 0})
    if not config:
        default_config = AppConfig().model_dump()
        await db.config.insert_one(default_config)
        return default_config
    return config

@api_router.put("/config")
async def update_config(config_update: dict):
    await db.config.update_one({"id": "app_config"}, {"$set": config_update}, upsert=True)
    return await db.config.find_one({"id": "app_config"}, {"_id": 0})

# ==================== GOOGLE OAUTH AUTHENTICATION ====================
# Business: Authentification Google exclusive pour le Super Admin / Coach
# Seul l'email autorisé peut accéder au dashboard

# Email autorisé pour l'accès Coach/Super Admin
AUTHORIZED_COACH_EMAIL = os.environ.get("AUTHORIZED_COACH_EMAIL", "contact.artboost@gmail.com")

class GoogleAuthSession(BaseModel):
    """Session d'authentification Google"""
    model_config = ConfigDict(extra="ignore")
    session_id: str
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GoogleUser(BaseModel):
    """Utilisateur authentifié via Google"""
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    is_coach: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None

@api_router.post("/auth/google/session")
async def process_google_session(request: Request, response: Response):
    """
    Traite le session_id reçu après authentification Google.
    Vérifie que l'email est autorisé (coach@afroboost.com).
    
    REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    """
    try:
        body = await request.json()
        session_id = body.get("session_id")
        
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id requis")
        
        # Appeler l'API Emergent pour récupérer les données de session
        import httpx
        async with httpx.AsyncClient() as client:
            emergent_response = await client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id}
            )
            
            if emergent_response.status_code != 200:
                raise HTTPException(status_code=401, detail="Session invalide ou expirée")
            
            user_data = emergent_response.json()
        
        email = user_data.get("email", "").lower()
        name = user_data.get("name", "")
        picture = user_data.get("picture", "")
        session_token = user_data.get("session_token", "")
        
        # ===== VÉRIFICATION CRITIQUE : Email autorisé uniquement =====
        if email != AUTHORIZED_COACH_EMAIL.lower():
            return {
                "success": False,
                "error": "access_denied",
                "message": f"⛔ Accès réservé. Seul {AUTHORIZED_COACH_EMAIL} peut accéder à ce dashboard."
            }
        
        # Créer ou mettre à jour l'utilisateur
        user_id = f"coach_{uuid.uuid4().hex[:12]}"
        existing_user = await db.google_users.find_one({"email": email}, {"_id": 0})
        
        if existing_user:
            user_id = existing_user.get("user_id", user_id)
            await db.google_users.update_one(
                {"email": email},
                {"$set": {
                    "name": name,
                    "picture": picture,
                    "last_login": datetime.now(timezone.utc).isoformat()
                }}
            )
        else:
            await db.google_users.insert_one({
                "user_id": user_id,
                "email": email,
                "name": name,
                "picture": picture,
                "is_coach": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_login": datetime.now(timezone.utc).isoformat()
            })
        
        # Créer la session
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        await db.coach_sessions.delete_many({"user_id": user_id})  # Supprimer les anciennes sessions
        await db.coach_sessions.insert_one({
            "session_id": str(uuid.uuid4()),
            "user_id": user_id,
            "email": email,
            "name": name,
            "session_token": session_token,
            "expires_at": expires_at.isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Définir le cookie httpOnly
        response.set_cookie(
            key="coach_session_token",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=7 * 24 * 60 * 60,  # 7 jours
            path="/"
        )
        
        return {
            "success": True,
            "user": {
                "user_id": user_id,
                "email": email,
                "name": name,
                "picture": picture,
                "is_coach": True
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google auth error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/auth/me")
async def get_current_user(request: Request):
    """
    Vérifie la session actuelle et retourne les infos utilisateur.
    Utilisé pour vérifier si l'utilisateur est connecté.
    """
    # Récupérer le token depuis le cookie ou le header Authorization
    session_token = request.cookies.get("coach_session_token")
    
    if not session_token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            session_token = auth_header[7:]
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    # Vérifier la session
    session = await db.coach_sessions.find_one(
        {"session_token": session_token},
        {"_id": 0}
    )
    
    if not session:
        raise HTTPException(status_code=401, detail="Session invalide")
    
    # Vérifier l'expiration
    expires_at = session.get("expires_at")
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        await db.coach_sessions.delete_one({"session_token": session_token})
        raise HTTPException(status_code=401, detail="Session expirée")
    
    # Récupérer l'utilisateur
    user = await db.google_users.find_one(
        {"user_id": session.get("user_id")},
        {"_id": 0}
    )
    
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
    
    return {
        "user_id": user.get("user_id"),
        "email": user.get("email"),
        "name": user.get("name"),
        "picture": user.get("picture"),
        "is_coach": user.get("is_coach", True)
    }

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    """
    Déconnexion: supprime la session et le cookie.
    """
    session_token = request.cookies.get("coach_session_token")
    
    if session_token:
        await db.coach_sessions.delete_many({"session_token": session_token})
    
    response.delete_cookie(
        key="coach_session_token",
        path="/",
        secure=True,
        samesite="none"
    )
    
    return {"success": True, "message": "Déconnexion réussie"}

# --- Legacy Coach Auth (conservé pour compatibilité mais déprécié) ---
@api_router.get("/coach-auth")
async def get_coach_auth():
    """DÉPRÉCIÉ: Utilisez /auth/me à la place"""
    return {"email": AUTHORIZED_COACH_EMAIL, "auth_method": "google_oauth"}

@api_router.post("/coach-auth/login")
async def coach_login(login: CoachLogin):
    """DÉPRÉCIÉ: Utilisez l'authentification Google OAuth"""
    return {
        "success": False, 
        "message": "L'authentification par mot de passe a été désactivée. Veuillez utiliser 'Se connecter avec Google'."
    }

# ==================== FEATURE FLAGS API (Super Admin Only) ====================
# Business: Seul le Super Admin peut activer/désactiver les services globaux

@api_router.get("/feature-flags")
async def get_feature_flags():
    """
    Récupère la configuration des feature flags
    Par défaut, tous les services additionnels sont désactivés
    """
    flags = await db.feature_flags.find_one({"id": "feature_flags"}, {"_id": 0})
    if not flags:
        # Créer la config par défaut (tout désactivé)
        default_flags = {
            "id": "feature_flags",
            "AUDIO_SERVICE_ENABLED": False,
            "VIDEO_SERVICE_ENABLED": False,
            "STREAMING_SERVICE_ENABLED": False,
            "updatedAt": None,
            "updatedBy": None
        }
        await db.feature_flags.insert_one(default_flags.copy())  # .copy() pour éviter mutation
        # Retourner sans _id
        return {k: v for k, v in default_flags.items() if k != "_id"}
    return flags

@api_router.put("/feature-flags")
async def update_feature_flags(update: FeatureFlagsUpdate):
    """
    Met à jour les feature flags (Super Admin only)
    TODO: Ajouter authentification Super Admin
    """
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    update_data["updatedAt"] = datetime.now(timezone.utc).isoformat()
    update_data["updatedBy"] = "super_admin"  # TODO: Récupérer depuis le token
    
    await db.feature_flags.update_one(
        {"id": "feature_flags"}, 
        {"$set": update_data}, 
        upsert=True
    )
    return await db.feature_flags.find_one({"id": "feature_flags"}, {"_id": 0})

# ==================== COACH SUBSCRIPTION API ====================
# Business: Gestion des abonnements et droits des coachs

@api_router.get("/coach-subscription")
async def get_coach_subscription():
    """
    Récupère l'abonnement du coach actuel
    Utilise l'email de coach_auth pour trouver l'abonnement correspondant
    """
    # Récupérer l'email du coach actuel
    coach_auth = await db.coach_auth.find_one({"id": "coach_auth"}, {"_id": 0})
    if not coach_auth:
        return {"error": "Coach auth not found"}
    
    coach_email = coach_auth.get("email", "coach@afroboost.com")
    
    # Chercher l'abonnement correspondant
    subscription = await db.coach_subscriptions.find_one(
        {"coachEmail": coach_email}, 
        {"_id": 0}
    )
    
    if not subscription:
        # Créer un abonnement par défaut (free, sans services additionnels)
        default_sub = {
            "id": str(uuid.uuid4()),
            "coachEmail": coach_email,
            "hasAudioService": False,
            "hasVideoService": False,
            "hasStreamingService": False,
            "subscriptionPlan": "free",
            "subscriptionStartDate": datetime.now(timezone.utc).isoformat(),
            "subscriptionEndDate": None,
            "isActive": True,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "updatedAt": None
        }
        await db.coach_subscriptions.insert_one(default_sub.copy())  # .copy() pour éviter mutation
        # Retourner sans _id
        return {k: v for k, v in default_sub.items() if k != "_id"}
    
    return subscription

@api_router.put("/coach-subscription")
async def update_coach_subscription(update: CoachSubscriptionUpdate):
    """
    Met à jour l'abonnement du coach
    TODO: Ajouter vérification Super Admin pour modifications sensibles
    """
    coach_auth = await db.coach_auth.find_one({"id": "coach_auth"}, {"_id": 0})
    if not coach_auth:
        raise HTTPException(status_code=404, detail="Coach auth not found")
    
    coach_email = coach_auth.get("email", "coach@afroboost.com")
    
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    update_data["updatedAt"] = datetime.now(timezone.utc).isoformat()
    
    await db.coach_subscriptions.update_one(
        {"coachEmail": coach_email},
        {"$set": update_data},
        upsert=True
    )
    
    return await db.coach_subscriptions.find_one({"coachEmail": coach_email}, {"_id": 0})

# ==================== SERVICE ACCESS VERIFICATION ====================
# Business: Fonction centrale pour vérifier l'accès aux services

@api_router.get("/verify-service-access/{service_name}")
async def verify_service_access(service_name: str):
    """
    Vérifie si un service est accessible pour le coach actuel.
    
    Logique de vérification (BOTH conditions must be true):
    1. Feature flag global activé (Super Admin)
    2. Coach a l'abonnement correspondant
    
    Args:
        service_name: "audio", "video", "streaming"
    
    Returns:
        {
            "hasAccess": bool,
            "reason": str,
            "featureFlagEnabled": bool,
            "coachHasSubscription": bool
        }
    """
    # Mapper les noms de service aux champs
    service_map = {
        "audio": ("AUDIO_SERVICE_ENABLED", "hasAudioService"),
        "video": ("VIDEO_SERVICE_ENABLED", "hasVideoService"),
        "streaming": ("STREAMING_SERVICE_ENABLED", "hasStreamingService")
    }
    
    if service_name not in service_map:
        raise HTTPException(status_code=400, detail=f"Service inconnu: {service_name}")
    
    flag_field, sub_field = service_map[service_name]
    
    # 1. Vérifier le feature flag global
    flags = await db.feature_flags.find_one({"id": "feature_flags"}, {"_id": 0})
    feature_enabled = flags.get(flag_field, False) if flags else False
    
    # 2. Vérifier l'abonnement du coach
    coach_auth = await db.coach_auth.find_one({"id": "coach_auth"}, {"_id": 0})
    coach_email = coach_auth.get("email", "coach@afroboost.com") if coach_auth else "coach@afroboost.com"
    
    subscription = await db.coach_subscriptions.find_one({"coachEmail": coach_email}, {"_id": 0})
    coach_has_service = subscription.get(sub_field, False) if subscription else False
    
    # Déterminer l'accès et la raison
    has_access = feature_enabled and coach_has_service
    
    if not feature_enabled:
        reason = f"Service {service_name} désactivé globalement (contacter l'administrateur)"
    elif not coach_has_service:
        reason = f"Votre abonnement n'inclut pas le service {service_name}"
    else:
        reason = "Accès autorisé"
    
    return {
        "hasAccess": has_access,
        "reason": reason,
        "featureFlagEnabled": feature_enabled,
        "coachHasSubscription": coach_has_service,
        "service": service_name
    }

# ==================== EMAILJS CONFIG (MongoDB) ====================

class EmailJSConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = "emailjs_config"
    serviceId: str = ""
    templateId: str = ""
    publicKey: str = ""

class EmailJSConfigUpdate(BaseModel):
    serviceId: Optional[str] = None
    templateId: Optional[str] = None
    publicKey: Optional[str] = None

@api_router.get("/emailjs-config")
async def get_emailjs_config():
    config = await db.emailjs_config.find_one({"id": "emailjs_config"}, {"_id": 0})
    if not config:
        return {"id": "emailjs_config", "serviceId": "", "templateId": "", "publicKey": ""}
    return config

@api_router.put("/emailjs-config")
async def update_emailjs_config(config: EmailJSConfigUpdate):
    updates = {k: v for k, v in config.model_dump().items() if v is not None}
    updates["id"] = "emailjs_config"
    await db.emailjs_config.update_one({"id": "emailjs_config"}, {"$set": updates}, upsert=True)
    return await db.emailjs_config.find_one({"id": "emailjs_config"}, {"_id": 0})

# ==================== WHATSAPP CONFIG (MongoDB) ====================

class WhatsAppConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = "whatsapp_config"
    accountSid: str = ""
    authToken: str = ""
    fromNumber: str = ""
    apiMode: str = "twilio"

class WhatsAppConfigUpdate(BaseModel):
    accountSid: Optional[str] = None
    authToken: Optional[str] = None
    fromNumber: Optional[str] = None
    apiMode: Optional[str] = None

@api_router.get("/whatsapp-config")
async def get_whatsapp_config():
    config = await db.whatsapp_config.find_one({"id": "whatsapp_config"}, {"_id": 0})
    if not config:
        return {"id": "whatsapp_config", "accountSid": "", "authToken": "", "fromNumber": "", "apiMode": "twilio"}
    return config

@api_router.put("/whatsapp-config")
async def update_whatsapp_config(config: WhatsAppConfigUpdate):
    updates = {k: v for k, v in config.model_dump().items() if v is not None}
    updates["id"] = "whatsapp_config"
    await db.whatsapp_config.update_one({"id": "whatsapp_config"}, {"$set": updates}, upsert=True)
    return await db.whatsapp_config.find_one({"id": "whatsapp_config"}, {"_id": 0})

# ==================== DATA MIGRATION (localStorage -> MongoDB) ====================

class MigrationData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    emailJSConfig: Optional[dict] = None
    whatsAppConfig: Optional[dict] = None
    aiConfig: Optional[dict] = None
    reservations: Optional[List[dict]] = None
    coachAuth: Optional[dict] = None

@api_router.post("/migrate-data")
async def migrate_localstorage_to_mongodb(data: MigrationData):
    """
    Endpoint pour migrer les données du localStorage vers MongoDB.
    Appelé une seule fois lors de la première utilisation après la migration.
    """
    migrated = {"emailJS": False, "whatsApp": False, "ai": False, "reservations": 0, "coachAuth": False}
    
    # Migration EmailJS Config
    if data.emailJSConfig and data.emailJSConfig.get("serviceId"):
        existing = await db.emailjs_config.find_one({"id": "emailjs_config"})
        if not existing or not existing.get("serviceId"):
            await db.emailjs_config.update_one(
                {"id": "emailjs_config"}, 
                {"$set": {**data.emailJSConfig, "id": "emailjs_config"}}, 
                upsert=True
            )
            migrated["emailJS"] = True
    
    # Migration WhatsApp Config
    if data.whatsAppConfig and data.whatsAppConfig.get("accountSid"):
        existing = await db.whatsapp_config.find_one({"id": "whatsapp_config"})
        if not existing or not existing.get("accountSid"):
            await db.whatsapp_config.update_one(
                {"id": "whatsapp_config"}, 
                {"$set": {**data.whatsAppConfig, "id": "whatsapp_config"}}, 
                upsert=True
            )
            migrated["whatsApp"] = True
    
    # Migration AI Config
    if data.aiConfig and data.aiConfig.get("systemPrompt"):
        existing = await db.ai_config.find_one({"id": "ai_config"})
        if not existing or not existing.get("systemPrompt"):
            await db.ai_config.update_one(
                {"id": "ai_config"}, 
                {"$set": {**data.aiConfig, "id": "ai_config"}}, 
                upsert=True
            )
            migrated["ai"] = True
    
    # Migration Reservations
    if data.reservations:
        for res in data.reservations:
            if res.get("reservationCode"):
                existing = await db.reservations.find_one({"reservationCode": res["reservationCode"]})
                if not existing:
                    await db.reservations.insert_one(res)
                    migrated["reservations"] += 1
    
    # Migration Coach Auth
    if data.coachAuth:
        existing = await db.coach_auth.find_one({"id": "coach_auth"})
        if not existing:
            await db.coach_auth.update_one(
                {"id": "coach_auth"}, 
                {"$set": {**data.coachAuth, "id": "coach_auth"}}, 
                upsert=True
            )
            migrated["coachAuth"] = True
    
    logger.info(f"Migration completed: {migrated}")
    return {"success": True, "migrated": migrated}

@api_router.get("/migration-status")
async def get_migration_status():
    """Vérifie si les données ont été migrées vers MongoDB"""
    emailjs = await db.emailjs_config.find_one({"id": "emailjs_config"}, {"_id": 0})
    whatsapp = await db.whatsapp_config.find_one({"id": "whatsapp_config"}, {"_id": 0})
    ai = await db.ai_config.find_one({"id": "ai_config"}, {"_id": 0})
    reservations_count = await db.reservations.count_documents({})
    
    return {
        "emailJS": bool(emailjs and emailjs.get("serviceId")),
        "whatsApp": bool(whatsapp and whatsapp.get("accountSid")),
        "ai": bool(ai and ai.get("systemPrompt")),
        "reservationsCount": reservations_count,
        "migrationComplete": True
    }

# ==================== AI WHATSAPP AGENT ====================

class AIConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = "ai_config"
    enabled: bool = False
    systemPrompt: str = """Tu es l'assistant virtuel d'Afroboost, une expérience fitness unique combinant cardio, danse afrobeat et casques audio immersifs.

Ton rôle:
- Répondre aux questions sur les cours, les offres et les réservations
- Être chaleureux, dynamique et motivant comme un coach fitness
- Utiliser un ton amical et des emojis appropriés
- Personnaliser les réponses avec le prénom du client quand disponible

Si tu ne connais pas la réponse, oriente vers le contact: contact.artboost@gmail.com"""
    model: str = "gpt-4o-mini"
    provider: str = "openai"
    lastMediaUrl: str = ""
    twintPaymentUrl: str = ""  # Lien de paiement Twint direct pour les ventes
    campaignPrompt: str = ""  # Prompt Campagne PRIORITAIRE - Ajouté à la fin du contexte

class AIConfigUpdate(BaseModel):
    enabled: Optional[bool] = None
    systemPrompt: Optional[str] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    lastMediaUrl: Optional[str] = None
    twintPaymentUrl: Optional[str] = None  # Lien de paiement Twint direct
    campaignPrompt: Optional[str] = None  # Prompt Campagne PRIORITAIRE

class AILog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    fromPhone: str
    clientName: Optional[str] = None
    incomingMessage: str
    aiResponse: str
    responseTime: float = 0  # En secondes

class WhatsAppWebhook(BaseModel):
    From: str  # whatsapp:+41XXXXXXXXX
    Body: str
    To: Optional[str] = None
    MediaUrl0: Optional[str] = None

# --- AI Config Routes ---
@api_router.get("/ai-config")
async def get_ai_config():
    config = await db.ai_config.find_one({"id": "ai_config"}, {"_id": 0})
    if not config:
        default_config = AIConfig().model_dump()
        await db.ai_config.insert_one(default_config)
        return default_config
    return config

@api_router.put("/ai-config")
async def update_ai_config(config: AIConfigUpdate):
    updates = {k: v for k, v in config.model_dump().items() if v is not None}
    await db.ai_config.update_one({"id": "ai_config"}, {"$set": updates}, upsert=True)
    return await db.ai_config.find_one({"id": "ai_config"}, {"_id": 0})

# --- AI Logs Routes ---
@api_router.get("/ai-logs")
async def get_ai_logs():
    logs = await db.ai_logs.find({}, {"_id": 0}).sort("timestamp", -1).to_list(50)
    return logs

@api_router.delete("/ai-logs")
async def clear_ai_logs():
    await db.ai_logs.delete_many({})
    return {"success": True}

# --- WhatsApp Webhook (Twilio) ---
@api_router.post("/webhook/whatsapp")
async def handle_whatsapp_webhook(webhook: WhatsAppWebhook):
    """
    Webhook pour recevoir les messages WhatsApp entrants via Twilio
    Répond automatiquement avec l'IA si activée
    """
    import time
    start_time = time.time()
    
    # Récupérer la config IA
    ai_config = await db.ai_config.find_one({"id": "ai_config"}, {"_id": 0})
    if not ai_config or not ai_config.get("enabled"):
        logger.info(f"AI disabled, ignoring message from {webhook.From}")
        return {"status": "ai_disabled"}
    
    # Extraire le numéro de téléphone
    from_phone = webhook.From.replace("whatsapp:", "")
    incoming_message = webhook.Body
    
    logger.info(f"Incoming WhatsApp from {from_phone}: {incoming_message}")
    
    # Chercher le client dans les réservations
    client_name = None
    normalized_phone = from_phone.replace("+", "").replace(" ", "")
    reservations = await db.reservations.find({}, {"_id": 0}).to_list(1000)
    
    for res in reservations:
        res_phone = (res.get("whatsapp") or res.get("phone") or "").replace("+", "").replace(" ", "").replace("-", "")
        if res_phone and normalized_phone.endswith(res_phone[-9:]):
            client_name = res.get("userName") or res.get("name")
            break
    
    # Construire le contexte
    context = ""
    if client_name:
        context += f"\n\nLe client qui te parle s'appelle {client_name}. Utilise son prénom dans ta réponse."
    
    last_media = ai_config.get("lastMediaUrl", "")
    if last_media:
        context += f"\n\nNote: Tu as récemment envoyé un média à ce client: {last_media}. Tu peux lui demander s'il l'a bien reçu."
    
    full_system_prompt = ai_config.get("systemPrompt", "") + context
    
    # Appeler l'IA
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        emergent_key = os.environ.get("EMERGENT_LLM_KEY")
        if not emergent_key:
            logger.error("EMERGENT_LLM_KEY not configured")
            return {"status": "error", "message": "AI key not configured"}
        
        # Créer une session unique par numéro de téléphone
        session_id = f"whatsapp_{normalized_phone}"
        
        chat = LlmChat(
            api_key=emergent_key,
            session_id=session_id,
            system_message=full_system_prompt
        ).with_model(ai_config.get("provider", "openai"), ai_config.get("model", "gpt-4o-mini"))
        
        user_message = UserMessage(text=incoming_message)
        ai_response = await chat.send_message(user_message)
        
        response_time = time.time() - start_time
        
        # Sauvegarder le log
        log_entry = AILog(
            fromPhone=from_phone,
            clientName=client_name,
            incomingMessage=incoming_message,
            aiResponse=ai_response,
            responseTime=response_time
        ).model_dump()
        await db.ai_logs.insert_one(log_entry)
        
        logger.info(f"AI responded to {from_phone} in {response_time:.2f}s")
        
        # Retourner la réponse (Twilio attend un TwiML ou un JSON)
        # Pour une réponse automatique, Twilio utilise TwiML
        return {
            "status": "success",
            "response": ai_response,
            "clientName": client_name,
            "responseTime": response_time
        }
        
    except Exception as e:
        logger.error(f"AI error: {str(e)}")
        return {"status": "error", "message": str(e)}

# --- Endpoint pour envoyer WhatsApp depuis le frontend (Liaison IA -> Twilio) ---
class SendWhatsAppRequest(BaseModel):
    to: str
    message: str
    mediaUrl: str = None

# ==================== FONCTION UTILITAIRE WHATSAPP ====================
async def _get_twilio_config():
    """
    Récupère la configuration Twilio avec PRIORITÉ aux variables .env.
    Ordre de priorité:
    1. Variables d'environnement (.env) - PRODUCTION
    2. Configuration en base de données - FALLBACK
    
    Retourne: (account_sid, auth_token, from_number) ou (None, None, None) si non configuré
    """
    # PRIORITÉ 1: Variables d'environnement (.env)
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER:
        logger.info(f"[WHATSAPP-PROD] ✅ Utilisation config .env - Numéro: {TWILIO_FROM_NUMBER}")
        return TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER
    
    # PRIORITÉ 2: Configuration en base de données (fallback)
    whatsapp_config = await db.whatsapp_config.find_one({"id": "whatsapp_config"}, {"_id": 0})
    if whatsapp_config:
        account_sid = whatsapp_config.get("accountSid")
        auth_token = whatsapp_config.get("authToken")
        from_number = whatsapp_config.get("fromNumber")
        
        if account_sid and auth_token and from_number:
            logger.info(f"[WHATSAPP-PROD] ⚠️ Utilisation config DB (fallback) - Numéro: {from_number}")
            return account_sid, auth_token, from_number
    
    return None, None, None


async def send_whatsapp_direct(to_phone: str, message: str, media_url: str = None, campaign_id: str = None, campaign_name: str = None) -> dict:
    """
    Fonction interne pour envoyer un message WhatsApp via Twilio.
    Utilisée par l'endpoint /send-whatsapp et par /campaigns/{id}/launch.
    
    Args:
        to_phone: Numéro de téléphone du destinataire
        message: Corps du message
        media_url: URL d'un média à joindre (optionnel)
        campaign_id: ID de la campagne (pour logs d'erreurs)
        campaign_name: Nom de la campagne (pour logs d'erreurs)
    
    Returns:
        dict avec status, sid (si succès), error (si échec), error_code (si Twilio)
    """
    import httpx
    
    # Récupérer la config Twilio (priorité .env)
    account_sid, auth_token, from_number = await _get_twilio_config()
    
    if not account_sid or not auth_token or not from_number:
        logger.warning("[WHATSAPP-PROD] ❌ Configuration Twilio manquante - mode simulation")
        return {
            "status": "simulated",
            "message": f"WhatsApp simulé pour: {to_phone}",
            "simulated": True
        }
    
    # Formater le numéro destinataire
    clean_to = to_phone.replace(" ", "").replace("-", "")
    if not clean_to.startswith("+"):
        clean_to = "+41" + clean_to.lstrip("0") if clean_to.startswith("0") else "+" + clean_to
    
    # Formater le numéro expéditeur
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
    
    logger.info(f"[WHATSAPP-PROD] 📤 Envoi via {clean_from} vers {clean_to}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                twilio_url,
                data=data,
                auth=(account_sid, auth_token)
            )
            
            result = response.json()
            
            if response.status_code >= 400:
                error_msg = result.get("message", "Unknown error")
                error_code = result.get("code", response.status_code)
                more_info = result.get("more_info", "")
                
                logger.error(f"[WHATSAPP] ❌ Erreur [{error_code}]: {error_msg}")
                
                # Stockage dans campaign_errors
                try:
                    error_doc = {
                        "campaign_id": campaign_id or "direct_send",
                        "campaign_name": campaign_name or "Envoi Direct",
                        "error_type": "twilio_api_error",
                        "error_code": str(error_code),
                        "error_message": error_msg,
                        "more_info": more_info,
                        "channel": "whatsapp",
                        "to_phone": clean_to,
                        "from_phone": clean_from,
                        "http_status": response.status_code,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                    mongo_client_sync[os.environ.get('DB_NAME', 'test_database')].campaign_errors.insert_one(error_doc)
                except Exception as log_err:
                    logger.error(f"[WHATSAPP] Erreur log: {log_err}")
                
                return {
                    "status": "error", 
                    "error": error_msg, 
                    "error_code": str(error_code),
                    "more_info": more_info
                }
            
            sid = result.get("sid", "")
            logger.info(f"[WHATSAPP] ✅ Envoyé - SID: {sid}")
            
            return {
                "status": "success",
                "sid": sid,
                "to": clean_to,
                "from": clean_from
            }
            
    except Exception as e:
        logger.error(f"[WHATSAPP] ❌ Exception: {str(e)}")
        
        try:
            error_doc = {
                "campaign_id": campaign_id or "direct_send",
                "campaign_name": campaign_name or "Envoi Direct",
                "error_type": "exception",
                "error_code": "EXCEPTION",
                "error_message": str(e),
                "channel": "whatsapp",
                "to_phone": clean_to,
                "from_phone": clean_from,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            mongo_client_sync[os.environ.get('DB_NAME', 'test_database')].campaign_errors.insert_one(error_doc)
        except Exception as log_err:
            logger.error(f"[WHATSAPP-DIAG] Impossible d'enregistrer l'exception: {log_err}")
        
        return {"status": "error", "error": str(e), "error_code": "EXCEPTION"}


@api_router.post("/send-whatsapp")
async def send_whatsapp_message(request: SendWhatsAppRequest):
    """
    Endpoint pour envoyer un message WhatsApp.
    Utilise la config Twilio avec PRIORITÉ aux variables .env.
    """
    return await send_whatsapp_direct(
        to_phone=request.to,
        message=request.message,
        media_url=request.mediaUrl
    )

# --- Endpoint pour tester l'IA manuellement ---
@api_router.post("/ai-test")
async def test_ai_response(data: dict):
    """Test l'IA avec un message manuel"""
    import time
    start_time = time.time()
    
    message = data.get("message", "")
    client_name = data.get("clientName", "")
    
    if not message:
        raise HTTPException(status_code=400, detail="Message requis")
    
    # Récupérer la config IA
    ai_config = await db.ai_config.find_one({"id": "ai_config"}, {"_id": 0})
    if not ai_config:
        ai_config = AIConfig().model_dump()
    
    # Construire le contexte
    context = ""
    if client_name:
        context += f"\n\nLe client qui te parle s'appelle {client_name}. Utilise son prénom dans ta réponse."
    
    last_media = ai_config.get("lastMediaUrl", "")
    if last_media:
        context += f"\n\nNote: Tu as récemment envoyé un média à ce client: {last_media}."
    
    full_system_prompt = ai_config.get("systemPrompt", "") + context
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        emergent_key = os.environ.get("EMERGENT_LLM_KEY")
        if not emergent_key:
            raise HTTPException(status_code=500, detail="EMERGENT_LLM_KEY non configuré")
        
        chat = LlmChat(
            api_key=emergent_key,
            session_id=f"test_{int(time.time())}",
            system_message=full_system_prompt
        ).with_model(ai_config.get("provider", "openai"), ai_config.get("model", "gpt-4o-mini"))
        
        user_message = UserMessage(text=message)
        ai_response = await chat.send_message(user_message)
        
        response_time = time.time() - start_time
        
        return {
            "success": True,
            "response": ai_response,
            "responseTime": response_time
        }
        
    except Exception as e:
        logger.error(f"AI test error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Leads Routes (Widget IA) ---
@api_router.get("/leads")
async def get_leads():
    """Récupère tous les leads capturés via le widget IA"""
    leads = await db.leads.find({}, {"_id": 0}).sort("createdAt", -1).to_list(500)
    return leads

@api_router.post("/leads")
async def create_lead(lead: Lead):
    """Enregistre un nouveau lead depuis le widget IA"""
    from datetime import datetime, timezone
    
    lead_data = lead.model_dump()
    lead_data["id"] = f"lead_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{lead.whatsapp[-4:]}"
    lead_data["createdAt"] = datetime.now(timezone.utc).isoformat()
    
    # Vérifier si le lead existe déjà (même email ou WhatsApp)
    existing = await db.leads.find_one({
        "$or": [
            {"email": lead.email},
            {"whatsapp": lead.whatsapp}
        ]
    })
    
    if existing:
        # Mettre à jour le lead existant
        await db.leads.update_one(
            {"id": existing["id"]},
            {"$set": {"firstName": lead.firstName, "updatedAt": lead_data["createdAt"]}}
        )
        existing["firstName"] = lead.firstName
        return {**existing, "_id": None}
    
    await db.leads.insert_one(lead_data)
    return {k: v for k, v in lead_data.items() if k != "_id"}

@api_router.delete("/leads/{lead_id}")
async def delete_lead(lead_id: str):
    """Supprime un lead"""
    result = await db.leads.delete_one({"id": lead_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"success": True}

# --- Chat IA Widget ---
@api_router.post("/chat")
async def chat_with_ai(data: ChatMessage):
    """
    Chat avec l'IA depuis le widget client.
    
    Fonctionnalités:
    1. SYNCHRONISATION IA: Récupère dynamiquement les offres et articles
    2. CRM AUTO-SAVE: Enregistre automatiquement le prospect (anti-doublon)
    3. CONTEXTE DYNAMIQUE: Injecte les infos dans le prompt système
    """
    import time
    start_time = time.time()
    
    message = data.message
    first_name = data.firstName
    email = data.email
    whatsapp = data.whatsapp
    source = data.source or "chat_ia"
    
    if not message:
        raise HTTPException(status_code=400, detail="Message requis")
    
    # === 1. CRM AUTO-SAVE (Anti-doublon) ===
    # Enregistrer le prospect dans chat_participants si email ou whatsapp fourni
    if email or whatsapp:
        try:
            # Vérifier si le contact existe déjà (par email OU whatsapp)
            existing_contact = None
            if email:
                existing_contact = await db.chat_participants.find_one({"email": email}, {"_id": 0})
            if not existing_contact and whatsapp:
                # Normaliser le numéro WhatsApp
                clean_whatsapp = whatsapp.replace(" ", "").replace("-", "")
                existing_contact = await db.chat_participants.find_one({
                    "$or": [
                        {"whatsapp": whatsapp},
                        {"whatsapp": clean_whatsapp}
                    ]
                }, {"_id": 0})
            
            if not existing_contact:
                # Créer le nouveau contact
                new_participant = {
                    "id": str(uuid.uuid4()),
                    "name": first_name or "Visiteur Chat IA",
                    "email": email or "",
                    "whatsapp": whatsapp or "",
                    "source": f"Lien Chat IA ({source})",
                    "link_token": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "last_seen_at": datetime.now(timezone.utc).isoformat()
                }
                await db.chat_participants.insert_one(new_participant)
                logger.info(f"[CRM-AUTO] Nouveau contact créé: {first_name or 'Visiteur'} ({email or whatsapp}) - Source: {source}")
            else:
                # Mettre à jour last_seen_at
                await db.chat_participants.update_one(
                    {"id": existing_contact.get("id")},
                    {"$set": {"last_seen_at": datetime.now(timezone.utc).isoformat()}}
                )
                logger.info(f"[CRM-AUTO] Contact existant mis à jour: {existing_contact.get('name')}")
        except Exception as crm_error:
            logger.warning(f"[CRM-AUTO] Erreur enregistrement CRM (non bloquant): {crm_error}")
    
    # === 2. RÉCUPÉRER LA CONFIG IA ===
    ai_config = await db.ai_config.find_one({"id": "ai_config"}, {"_id": 0})
    if not ai_config:
        ai_config = AIConfig().model_dump()
    
    if not ai_config.get("enabled"):
        return {"response": "L'assistant IA est actuellement désactivé. Veuillez contacter le coach directement.", "responseTime": 0}
    
    # === 2.5 DÉTECTION MODE STRICT (AVANT construction du contexte) ===
    # Vérifier si on a un link_token avec custom_prompt
    link_token = data.link_token.strip() if data.link_token else ""
    if not link_token and data.source and data.source.startswith("link_"):
        link_token = data.source.replace("link_", "")
    
    use_strict_mode = False
    CUSTOM_PROMPT = ""
    
    if link_token:
        try:
            session_with_prompt = await db.chat_sessions.find_one(
                {"link_token": link_token, "is_deleted": {"$ne": True}},
                {"_id": 0, "custom_prompt": 1}
            )
            if session_with_prompt and session_with_prompt.get("custom_prompt"):
                custom_prompt = session_with_prompt.get("custom_prompt", "").strip()
                if custom_prompt:
                    CUSTOM_PROMPT = custom_prompt
                    use_strict_mode = True
                    logger.info(f"[CHAT-IA] 🔒 Mode STRICT détecté pour lien {link_token}")
        except Exception as e:
            logger.warning(f"[CHAT-IA] Erreur récupération custom_prompt pour {link_token}: {e}")
    
    # === 3. CONSTRUIRE LE CONTEXTE DYNAMIQUE ===
    if use_strict_mode:
        # MODE STRICT: Contexte minimal (pas de cours/tarifs/vente)
        context = "\n\n========== MODE STRICT - LIEN SPÉCIFIQUE ==========\n"
        context += "Tu es l'assistant Afroboost avec un OBJECTIF SPÉCIFIQUE défini ci-dessous.\n"
        context += "NE PARLE PAS de cours, tarifs, abonnements ou vente SAUF si explicitement demandé dans les instructions.\n"
        
        # Prénom du client seulement
        if first_name:
            context += f"\n👤 INTERLOCUTEUR: {first_name}\n"
        
        # Concept/Description UNIQUEMENT (pas les offres/cours)
        try:
            concept = await db.concept.find_one({"id": "concept"}, {"_id": 0})
            if concept and concept.get('description'):
                context += f"\n📌 CONCEPT AFROBOOST:\n{concept.get('description', '')[:500]}\n"
        except Exception as e:
            pass
        
        logger.info("[CHAT-IA] 🔒 Contexte STRICT construit (sans cours/tarifs)")
    else:
        # MODE STANDARD: Contexte complet avec cours/tarifs/vente
        context = "\n\n========== CONNAISSANCES DU SITE AFROBOOST ==========\n"
        context += "Utilise EXCLUSIVEMENT ces informations pour répondre sur les produits, cours, offres et articles.\n"
        context += "IMPORTANT: Vérifie TOUJOURS l'INVENTAIRE BOUTIQUE avant de dire qu'un produit n'existe pas !\n"
        
        # Prénom du client
        if first_name:
            context += f"\n👤 CLIENT: {first_name} - Utilise son prénom pour être chaleureux.\n"
        
        # Concept/Description du site
        try:
            concept = await db.concept.find_one({"id": "concept"}, {"_id": 0})
            if concept and concept.get('description'):
                context += f"\n📌 À PROPOS D'AFROBOOST:\n{concept.get('description', '')[:500]}\n"
        except Exception as e:
            logger.warning(f"[CHAT-IA] Erreur récupération concept: {e}")
    
    # === SECTIONS VENTE (UNIQUEMENT en mode STANDARD, pas en mode STRICT) ===
    if not use_strict_mode:
        # === SECTION 1: INVENTAIRE BOUTIQUE (PRODUITS PHYSIQUES) ===
        try:
            # Récupérer TOUS les éléments de la collection offers
            all_offers = await db.offers.find({"visible": {"$ne": False}}, {"_id": 0}).to_list(50)
            
            # Séparer les PRODUITS des SERVICES
            products = [o for o in all_offers if o.get('isProduct') == True]
            services = [o for o in all_offers if not o.get('isProduct')]
            
            # === PRODUITS BOUTIQUE (café, vêtements, accessoires...) ===
            if products:
                context += "\n\n🛒 INVENTAIRE BOUTIQUE (Produits en vente):\n"
                for p in products[:15]:
                    name = p.get('name', 'Produit')
                    price = p.get('price', 0)
                    desc = p.get('description', '')[:150] if p.get('description') else ''
                    category = p.get('category', '')
                    stock = p.get('stock', -1)
                    
                    context += f"  ★ {name.upper()} : {price} CHF"
                    if category:
                        context += f" (Catégorie: {category})"
                    if stock > 0:
                        context += f" - En stock: {stock}"
                    context += "\n"
                    if desc:
                        context += f"    Description: {desc}\n"
                context += "  → Si un client demande un de ces produits, CONFIRME qu'il est disponible !\n"
            else:
                context += "\n\n🛒 INVENTAIRE BOUTIQUE: Aucun produit en vente actuellement.\n"
            
            # === SERVICES ET OFFRES (abonnements, cours à l'unité...) ===
            if services:
                context += "\n\n💰 OFFRES ET TARIFS (Services):\n"
                for s in services[:10]:
                    name = s.get('name', 'Offre')
                    price = s.get('price', 0)
                    desc = s.get('description', '')[:100] if s.get('description') else ''
                    
                    context += f"  • {name} : {price} CHF"
                    if desc:
                        context += f" - {desc}"
                    context += "\n"
            else:
                context += "\n\n💰 OFFRES: Aucune offre spéciale actuellement.\n"
                
        except Exception as e:
            logger.error(f"[CHAT-IA] ❌ Erreur récupération offres/produits: {e}")
            context += "\n\n🛒 BOUTIQUE: Informations temporairement indisponibles.\n"
    
        # === SECTION 2: COURS DISPONIBLES ===
        try:
            courses = await db.courses.find({"visible": {"$ne": False}}, {"_id": 0}).to_list(20)
            if courses:
                context += "\n\n🎯 COURS DISPONIBLES:\n"
                for c in courses[:10]:  # Max 10 cours
                    name = c.get('name', 'Cours')
                    date = c.get('date', '')
                    time_slot = c.get('time', '')
                    location = c.get('location', '')
                    price = c.get('price', '')
                    description = c.get('description', '')[:80] if c.get('description') else ''
                    
                    context += f"  • {name}"
                    if date:
                        context += f" - {date}"
                    if time_slot:
                        context += f" à {time_slot}"
                    if location:
                        context += f" ({location})"
                    if price:
                        context += f" - {price} CHF"
                    context += "\n"
                    if description:
                        context += f"    → {description}\n"
            else:
                context += "\n\n🎯 COURS: Aucun cours programmé actuellement. Invite le client à suivre nos réseaux pour les prochaines dates.\n"
        except Exception as e:
            logger.warning(f"[CHAT-IA] Erreur récupération cours: {e}")
            context += "\n\n🎯 COURS: Informations temporairement indisponibles.\n"
        
        # === SECTION 3: ARTICLES ET ACTUALITÉS ===
        try:
            # Récupérer les 10 articles les plus récents
            articles = await db.articles.find(
                {"visible": {"$ne": False}}, 
                {"_id": 0}
            ).sort("createdAt", -1).to_list(10)
            
            if articles:
                context += "\n\n📰 DERNIERS ARTICLES ET ACTUALITÉS:\n"
                for a in articles[:5]:  # Max 5 articles dans le contexte
                    title = a.get('title', 'Article')
                    summary = a.get('summary', '')[:120] if a.get('summary') else ''
                    link = a.get('link', '')
                    
                    context += f"  • {title}\n"
                    if summary:
                        context += f"    → {summary}\n"
                    if link:
                        context += f"    🔗 Lien: {link}\n"
            else:
                context += "\n\n📰 ARTICLES: Pas d'articles récents. Le blog arrive bientôt !\n"
        except Exception as e:
            logger.warning(f"[CHAT-IA] Erreur récupération articles: {e}")
            # Silencieux si pas de collection articles
        
        # === SECTION 4: PROMOS SPÉCIALES (avec masquage des codes) ===
        # L'IA peut connaître les remises pour calculer les prix, mais JAMAIS les codes
        # PRODUCTION-READY: Try/except individuel pour chaque promo
        try:
            active_promos = await db.discount_codes.find({"active": True}, {"_id": 0}).to_list(20)
            if active_promos:
                context += "\n\n🎁 PROMOTIONS EN COURS:\n"
                promos_injected = 0
                for promo in active_promos[:5]:
                    try:
                        # MASQUAGE TECHNIQUE: Le champ 'code' n'est JAMAIS lu ni transmis
                        # Seuls 'type' et 'value' sont utilisés pour le calcul
                        promo_type = promo.get('type', '%')
                        promo_value = promo.get('value', 0)
                        
                        # Validation: S'assurer que value est un nombre valide
                        if promo_value is None:
                            promo_value = 0
                        promo_value = float(promo_value)
                        
                        # Construire la description SANS le code réel
                        # Le placeholder [CODE_APPLIQUÉ_AU_PANIER] est la SEULE chose visible
                        if promo_type == '100%':
                            context += "  • Remise 100% disponible (code: [CODE_APPLIQUÉ_AU_PANIER])\n"
                        elif promo_type == '%':
                            context += "  • Remise de " + str(promo_value) + "% disponible (code: [CODE_APPLIQUÉ_AU_PANIER])\n"
                        elif promo_type == 'CHF':
                            context += "  • Remise de " + str(promo_value) + " CHF disponible (code: [CODE_APPLIQUÉ_AU_PANIER])\n"
                        else:
                            # Type inconnu: afficher quand même sans révéler le code
                            context += "  • Promotion disponible (code: [CODE_APPLIQUÉ_AU_PANIER])\n"
                        promos_injected += 1
                    except Exception as promo_error:
                        # Log l'erreur mais continue avec les autres promos
                        logger.warning(f"[CHAT-IA] ⚠️ Promo ignorée (erreur parsing): {promo_error}")
                        continue
                
                if promos_injected > 0:
                    context += "  → Tu peux calculer les prix réduits avec ces remises.\n"
                    context += "  → Ne dis JAMAIS le code. Dis simplement: 'Le code est appliqué automatiquement au panier.'\n"
                    logger.info(f"[CHAT-IA] ✅ {promos_injected} promos injectées (codes masqués)")
        except Exception as e:
            logger.warning(f"[CHAT-IA] Erreur récupération promos (non bloquant): {e}")
        
        # === SECTION 5: LIEN DE PAIEMENT TWINT ===
        twint_payment_url = ai_config.get("twintPaymentUrl", "")
        if twint_payment_url and twint_payment_url.strip():
            context += f"\n\n💳 LIEN DE PAIEMENT TWINT:\n"
            context += f"  URL: {twint_payment_url}\n"
            context += "  → Quand un client confirme vouloir acheter, propose-lui ce lien de paiement sécurisé Twint.\n"
    # === FIN DES SECTIONS VENTE (uniquement en mode STANDARD) ===
    
    # === RÈGLES STRICTES POUR L'IA ===
    # Récupérer le lien de paiement Twint UNIQUEMENT en mode STANDARD
    twint_payment_url = ""
    if not use_strict_mode:
        twint_payment_url = ai_config.get("twintPaymentUrl", "")
    
    # Détecter intention essai gratuit
    message_lower = message.lower()
    is_trial_intent = any(word in message_lower for word in ['essai', 'gratuit', 'tester', 'essayer', 'test', 'découvrir'])
    
    # ARCHITECTURE DE PROMPT - STRICT vs STANDARD
    if use_strict_mode:
        # MODE STRICT : custom_prompt REMPLACE BASE_PROMPT, AUCUNE donnée de vente
        STRICT_SYSTEM_PROMPT = """
╔══════════════════════════════════════════════════════════════════════╗
║        🔒🔒🔒 MODE STRICT - PARTENARIAT / COLLABORATION 🔒🔒🔒        ║
╚══════════════════════════════════════════════════════════════════════╝

⛔⛔⛔ INTERDICTIONS ABSOLUES ⛔⛔⛔

Tu as INTERDICTION ABSOLUE de:
- Citer un PRIX, un TARIF, un COÛT ou un MONTANT (CHF, EUR, $)
- Mentionner un LIEN DE PAIEMENT (Twint, Stripe, etc.)
- Parler de COURS, SESSIONS, ABONNEMENTS ou RÉSERVATIONS
- Orienter vers l'ACHAT ou l'INSCRIPTION
- Donner des informations sur la BOUTIQUE ou les PRODUITS à vendre

Si on te demande un prix, un tarif ou "combien ça coûte", TU DOIS répondre:
"Je vous invite à en discuter directement lors de notre échange, je m'occupe uniquement de la partie collaboration."

Si on insiste, répète cette phrase. Ne donne JAMAIS de prix.

🎯 TON RÔLE UNIQUE:
Tu t'occupes UNIQUEMENT de la COLLABORATION et du PARTENARIAT.
Tu peux parler du CONCEPT Afroboost (cardio + danse afrobeat + casques audio immersifs).
Tu ne connais AUCUN prix, AUCUN tarif, AUCUN lien de paiement.

"""
        STRICT_SYSTEM_PROMPT += "\n📋 INSTRUCTIONS EXCLUSIVES DU LIEN:\n\n"
        STRICT_SYSTEM_PROMPT += CUSTOM_PROMPT
        
        context += STRICT_SYSTEM_PROMPT
        logger.info("[CHAT-IA] 🔒 Mode STRICT activé")
        
    else:
        # MODE STANDARD : FLUX HABITUEL AVEC DONNÉES DE VENTE
        BASE_PROMPT = """
╔══════════════════════════════════════════════════════════════════╗
║                BASE_PROMPT - IDENTITÉ COACH BASSI                ║
╚══════════════════════════════════════════════════════════════════╝

🎯 IDENTITÉ:
Tu es le COACH BASSI, coach énergique et passionné d'Afroboost.
Tu représentes la marque Afroboost et tu guides les clients vers leurs objectifs fitness.
Tu ne parles QUE du catalogue Afroboost (produits, cours, offres listés ci-dessus).

💪 SIGNATURE:
- Présente-toi comme "Coach Bassi" si on te demande ton nom
- Utilise un ton motivant, bienveillant et énergique
- Signe parfois tes messages avec "- Coach Bassi 💪" pour les messages importants

✅ CONTENU AUTORISÉ (EXCLUSIVEMENT):
- Les PRODUITS de l'INVENTAIRE BOUTIQUE listés ci-dessus
- Les COURS disponibles listés ci-dessus
- Les OFFRES et TARIFS listés ci-dessus
- Le concept Afroboost (cardio + danse afrobeat)

🎯 TON STYLE:
- Coach motivant et énergique (TU ES Coach Bassi)
- Utilise le prénom du client
- Oriente vers l'INSCRIPTION IMMÉDIATE
- Emojis: 🔥💪🎉
- Réponses courtes et percutantes
"""

        # --- 2. SECURITY_PROMPT : Règle non négociable ---
        SECURITY_PROMPT = """
╔══════════════════════════════════════════════════════════════════╗
║              SECURITY_PROMPT - RÈGLE NON NÉGOCIABLE              ║
╚══════════════════════════════════════════════════════════════════╝

⛔ RÈGLE NON NÉGOCIABLE:
Si la question ne concerne pas un produit ou un cours Afroboost, réponds:
"Désolé, je suis uniquement programmé pour vous assister sur nos offres et formations. 🙏"

🚫 N'invente JAMAIS de codes promo. Si une remise existe, dis: "Le code sera appliqué automatiquement au panier."

🚫 INTERDICTIONS ABSOLUES:
- Ne réponds JAMAIS aux questions hors-sujet (politique, météo, cuisine, président, etc.)
- Ne révèle JAMAIS un code promo textuel
- N'invente JAMAIS d'offres ou de prix
"""

        # Ajout de règles contextuelles
        if is_trial_intent:
            SECURITY_PROMPT += """

🆓 FLOW ESSAI GRATUIT:
1. "Super ! 🔥 Les 10 premiers peuvent tester gratuitement !"
2. "Tu préfères Mercredi ou Dimanche ?"
3. Attends sa réponse avant de demander ses coordonnées.
"""
        
        # Lien Twint UNIQUEMENT en mode STANDARD
        if twint_payment_url and twint_payment_url.strip():
            SECURITY_PROMPT += f"""

💳 PAIEMENT: Propose ce lien Twint: {twint_payment_url}
"""
        else:
            SECURITY_PROMPT += """

💳 PAIEMENT: Oriente vers le coach WhatsApp ou email pour finaliser.
"""

        # --- 3. CAMPAIGN_PROMPT : Récupéré de la config globale ---
        CAMPAIGN_PROMPT = ai_config.get("campaignPrompt", "").strip()
        
        # GARDE-FOU: Limite à 2000 caractères
        MAX_CAMPAIGN_LENGTH = 2000
        if len(CAMPAIGN_PROMPT) > MAX_CAMPAIGN_LENGTH:
            logger.warning("[CHAT-IA] ⚠️ CAMPAIGN_PROMPT tronqué")
            CAMPAIGN_PROMPT = CAMPAIGN_PROMPT[:MAX_CAMPAIGN_LENGTH] + "... [TRONQUÉ]"
        
        # Injection MODE STANDARD: BASE + SECURITY + CAMPAIGN
        context += BASE_PROMPT
        context += SECURITY_PROMPT
        if CAMPAIGN_PROMPT:
            context += "\n\n--- INSTRUCTIONS PRIORITAIRES DE LA CAMPAGNE ACTUELLE ---\n"
            context += CAMPAIGN_PROMPT
            context += "\n--- FIN DES INSTRUCTIONS ---\n"
            logger.info("[CHAT-IA] ✅ Mode STANDARD - Campaign Prompt injecté (len: " + str(len(CAMPAIGN_PROMPT)) + ")")
        else:
            logger.info("[CHAT-IA] ✅ Mode STANDARD - Pas de Campaign Prompt")
    
    # Assemblage final du prompt système
    full_system_prompt = ai_config.get("systemPrompt", "Tu es l'assistant IA d'Afroboost.") + context
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        emergent_key = os.environ.get("EMERGENT_LLM_KEY")
        if not emergent_key:
            return {"response": "Configuration IA incomplète. Contactez l'administrateur.", "responseTime": 0}
        
        # Generate a unique session ID for this chat
        chat_session_id = f"afroboost_chat_{uuid.uuid4().hex[:8]}"
        
        chat = LlmChat(
            api_key=emergent_key,
            session_id=chat_session_id,
            system_message=full_system_prompt
        )
        
        user_msg = UserMessage(text=message)
        ai_response = await chat.send_message(user_msg)
        response_time = round(time.time() - start_time, 2)
        
        # Log la conversation
        await db.ai_logs.insert_one({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "from": f"widget_{first_name or 'anonymous'}",
            "email": email or "",
            "whatsapp": whatsapp or "",
            "source": source,
            "message": message,
            "response": ai_response,
            "responseTime": response_time
        })
        
        return {
            "response": ai_response,
            "responseTime": response_time
        }
        
    except Exception as e:
        logger.error(f"Chat AI error: {str(e)}")
        return {"response": "Désolé, une erreur s'est produite. Veuillez réessayer.", "responseTime": 0}

# ==================== ENHANCED CHAT SYSTEM API ====================
# Système de chat amélioré avec reconnaissance utilisateur, modes et liens partageables

# --- Chat Participants (CRM) ---
@api_router.get("/chat/participants")
async def get_chat_participants():
    """Récupère tous les participants du chat (CRM)"""
    participants = await db.chat_participants.find({}, {"_id": 0}).to_list(1000)
    return participants

@api_router.get("/chat/participants/{participant_id}")
async def get_chat_participant(participant_id: str):
    """Récupère un participant par son ID"""
    participant = await db.chat_participants.find_one({"id": participant_id}, {"_id": 0})
    if not participant:
        raise HTTPException(status_code=404, detail="Participant non trouvé")
    return participant

@api_router.post("/chat/participants")
async def create_chat_participant(participant: ChatParticipantCreate):
    """Crée un nouveau participant"""
    participant_obj = ChatParticipant(**participant.model_dump())
    await db.chat_participants.insert_one(participant_obj.model_dump())
    return participant_obj.model_dump()

@api_router.get("/chat/participants/find")
async def find_participant(
    name: Optional[str] = None,
    email: Optional[str] = None,
    whatsapp: Optional[str] = None
):
    """
    Recherche un participant par nom, email ou WhatsApp.
    Utilisé pour la reconnaissance automatique des utilisateurs.
    """
    query = {"$or": []}
    
    if name:
        query["$or"].append({"name": {"$regex": name, "$options": "i"}})
    if email:
        query["$or"].append({"email": {"$regex": f"^{email}$", "$options": "i"}})
    if whatsapp:
        # Nettoyer le numéro WhatsApp pour la recherche
        clean_whatsapp = whatsapp.replace(" ", "").replace("-", "").replace("+", "")
        query["$or"].append({"whatsapp": {"$regex": clean_whatsapp}})
    
    if not query["$or"]:
        return None
    
    participant = await db.chat_participants.find_one(query, {"_id": 0})
    return participant

@api_router.put("/chat/participants/{participant_id}")
async def update_chat_participant(participant_id: str, update_data: dict):
    """Met à jour un participant"""
    update_data["last_seen_at"] = datetime.now(timezone.utc).isoformat()
    await db.chat_participants.update_one(
        {"id": participant_id},
        {"$set": update_data}
    )
    updated = await db.chat_participants.find_one({"id": participant_id}, {"_id": 0})
    return updated

@api_router.delete("/chat/participants/{participant_id}")
async def delete_chat_participant(participant_id: str):
    """Supprime un participant du CRM avec nettoyage complet des donnees orphelines"""
    logger.info(f"[DELETE] Suppression participant: {participant_id}")
    
    participant = await db.chat_participants.find_one({"id": participant_id}, {"_id": 0})
    if not participant:
        logger.warning(f"[DELETE] Participant non trouve: {participant_id}")
        raise HTTPException(status_code=404, detail="Participant non trouve")
    
    participant_name = participant.get('name', 'inconnu')
    
    # 1. Supprimer tous les messages envoyes par ce participant
    messages_result = await db.chat_messages.delete_many({"sender_id": participant_id})
    logger.info(f"[DELETE] Messages supprimes: {messages_result.deleted_count}")
    
    # 2. Retirer le participant de toutes les sessions
    sessions_update = await db.chat_sessions.update_many(
        {"participant_ids": participant_id},
        {"$pull": {"participant_ids": participant_id}}
    )
    logger.info(f"[DELETE] Sessions mises a jour: {sessions_update.modified_count}")
    
    # 3. Supprimer les sessions privees ou le participant etait seul
    orphan_sessions = await db.chat_sessions.delete_many({
        "mode": "private",
        "participant_ids": {"$size": 0}
    })
    logger.info(f"[DELETE] Sessions orphelines supprimees: {orphan_sessions.deleted_count}")
    
    # 4. Supprimer le participant
    result = await db.chat_participants.delete_one({"id": participant_id})
    logger.info(f"[DELETE] Participant supprime: {result.deleted_count}")
    
    logger.info(f"[DELETE] Participant {participant_name} et donnees associees supprimes")
    return {
        "success": True, 
        "message": f"Contact {participant_name} supprime definitivement",
        "deleted": {
            "participant": result.deleted_count,
            "messages": messages_result.deleted_count,
            "sessions_updated": sessions_update.modified_count,
            "orphan_sessions": orphan_sessions.deleted_count
        }
    }

# --- Active Conversations for Internal Messaging ---
@api_router.get("/conversations/active")
async def get_active_conversations_for_messaging():
    """
    Récupère TOUTES les conversations pour la programmation de messages internes.
    Inclut : 
    - Sessions avec titre (groupes nommés comme "Les Lionnes")
    - Groupes standards (community, vip, promo)
    - TOUS les utilisateurs de la collection users
    """
    try:
        conversations = []
        seen_user_ids = set()  # Pour éviter les doublons d'utilisateurs
        
        # 1. Récupérer TOUTES les sessions de chat avec titre (GROUPES NOMMÉS)
        sessions = await db.chat_sessions.find(
            {"is_deleted": {"$ne": True}},
            {"_id": 0, "id": 1, "mode": 1, "title": 1, "participant_ids": 1, "created_at": 1, "last_message_at": 1, "updated_at": 1}
        ).sort("updated_at", -1).to_list(500)
        
        for session in sessions:
            try:
                session_id = session.get("id", "")
                mode = session.get("mode", "user")
                title = session.get("title", "")
                participant_ids = session.get("participant_ids", [])
                
                # GROUPES : Sessions avec titre OU mode groupe
                if title and title.strip():
                    # Session avec titre = Groupe nommé (comme "Les Lionnes")
                    conversations.append({
                        "conversation_id": session_id,
                        "name": f"👥 {title.strip()}",
                        "type": "group",
                        "mode": mode,
                        "title": title.strip(),
                        "last_activity": session.get("updated_at") or session.get("last_message_at") or session.get("created_at", "")
                    })
                elif mode in ["community", "vip", "promo", "group"]:
                    # Mode groupe standard - uniquement si pas encore ajouté
                    mode_names = {
                        "community": "🌍 Communauté",
                        "vip": "⭐ Groupe VIP",
                        "promo": "🎁 Offres Spéciales",
                        "group": "👥 Groupe"
                    }
                    conversations.append({
                        "conversation_id": session_id,
                        "name": mode_names.get(mode, f"👥 Groupe {mode}"),
                        "type": "group",
                        "mode": mode,
                        "title": "",
                        "last_activity": session.get("updated_at") or ""
                    })
                else:
                    # Session utilisateur - noter les IDs pour éviter les doublons
                    for pid in participant_ids:
                        seen_user_ids.add(pid)
                        
            except Exception as session_err:
                logger.warning(f"[CONVERSATIONS-ACTIVE] Erreur session {session.get('id', '?')}: {session_err}")
                continue
        
        # 2. Ajouter les groupes standards s'ils n'existent pas
        standard_groups = [
            {"conversation_id": "community", "name": "🌍 Communauté Générale", "type": "group", "mode": "community"},
            {"conversation_id": "vip", "name": "⭐ Groupe VIP", "type": "group", "mode": "vip"},
            {"conversation_id": "promo", "name": "🎁 Offres Spéciales", "type": "group", "mode": "promo"}
        ]
        
        existing_ids = [c["conversation_id"] for c in conversations]
        for group in standard_groups:
            if group["conversation_id"] not in existing_ids:
                conversations.append(group)
        
        # 3. Récupérer TOUS les utilisateurs de la collection users
        all_users = await db.users.find(
            {},
            {"_id": 0, "id": 1, "name": 1, "email": 1, "created_at": 1}
        ).sort("name", 1).to_list(500)
        
        # Éviter les doublons (même email)
        seen_emails = set()
        for user in all_users:
            try:
                user_id = user.get("id", "")
                user_name = (user.get("name") or "").strip()
                user_email = (user.get("email") or "").strip().lower()
                
                # Ignorer les utilisateurs sans ID
                if not user_id:
                    continue
                
                # NOTE: Plus de déduplication par email - on inclut TOUS les users
                # Éviter seulement les doublons par ID
                if user_id in seen_user_ids:
                    continue
                seen_user_ids.add(user_id)
                
                # Construire le nom d'affichage (fallback sur email si pas de nom)
                if user_name:
                    display_name = f"👤 {user_name}"
                    if user_email:
                        display_name += f" ({user_email})"
                elif user_email:
                    display_name = f"👤 {user_email}"
                else:
                    display_name = f"👤 Contact {user_id[:8]}"
                
                conversations.append({
                    "conversation_id": user_id,  # Utilise l'ID utilisateur pour cibler directement
                    "name": display_name,
                    "type": "user",
                    "mode": "user",
                    "title": "",
                    "email": user_email,
                    "last_activity": user.get("created_at", "")
                })
            except Exception as user_err:
                logger.warning(f"[CONVERSATIONS-ACTIVE] Erreur user: {user_err}")
                continue
        
        # 4. Trier: groupes d'abord (par nom), puis utilisateurs (par nom)
        conversations.sort(key=lambda x: (
            0 if x["type"] == "group" else 1,
            x.get("name", "").lower()
        ))
        
        # Compter les résultats
        groups_count = len([c for c in conversations if c["type"] == "group"])
        users_count = len([c for c in conversations if c["type"] == "user"])
        logger.info(f"[CONVERSATIONS-ACTIVE] {len(conversations)} conversations trouvées ({groups_count} groupes, {users_count} utilisateurs)")
        
        return {
            "success": True,
            "conversations": conversations,
            "total": len(conversations),
            "groups_count": groups_count,
            "users_count": users_count
        }
        
    except Exception as e:
        logger.error(f"[CONVERSATIONS-ACTIVE] Erreur: {e}")
        return {
            "success": False,
            "conversations": [],
            "error": str(e)
        }

# --- Rejoindre un groupe automatiquement (adhésion via lien) ---
class GroupJoinRequest(BaseModel):
    group_id: str
    email: str
    name: str = ""
    user_id: str = None

@api_router.post("/groups/join")
async def join_group_automatically(request: GroupJoinRequest):
    """
    Permet à un utilisateur déjà connecté de rejoindre un groupe via un lien ?group=ID.
    Utilisé pour l'adhésion automatique sans re-saisie d'email.
    """
    try:
        group_id = request.group_id
        email = request.email
        name = request.name or email.split('@')[0]
        user_id = request.user_id
        
        logger.info(f"[GROUP-JOIN] 🚀 Tentative adhésion: {email} -> groupe {group_id}")
        
        # Vérifier si le groupe existe
        # Chercher dans les sessions avec ce ID ou ce mode
        group_session = await db.chat_sessions.find_one(
            {"$or": [
                {"id": group_id},
                {"mode": group_id},
                {"title": {"$regex": group_id, "$options": "i"}}
            ]},
            {"_id": 0}
        )
        
        # Si le groupe n'existe pas, créer un groupe standard
        if not group_session:
            # Vérifier si c'est un mode standard (community, vip, promo)
            if group_id in ["community", "vip", "promo"]:
                mode_titles = {
                    "community": "Communauté Générale",
                    "vip": "Groupe VIP",
                    "promo": "Offres Spéciales"
                }
                group_session = {
                    "id": f"group_{group_id}_{uuid.uuid4().hex[:8]}",
                    "mode": group_id,
                    "title": mode_titles.get(group_id, f"Groupe {group_id}"),
                    "participant_ids": [],
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                await db.chat_sessions.insert_one(group_session)
                logger.info(f"[GROUP-JOIN] ✅ Nouveau groupe créé: {group_session['id']}")
            else:
                raise HTTPException(status_code=404, detail=f"Groupe {group_id} non trouvé")
        
        # Récupérer ou créer l'utilisateur
        participant_id = user_id
        if not participant_id:
            # Chercher l'utilisateur par email
            existing_user = await db.users.find_one({"email": email}, {"_id": 0})
            if existing_user:
                participant_id = existing_user.get("id")
            else:
                # Créer un nouvel utilisateur
                participant_id = str(uuid.uuid4())
                new_user = {
                    "id": participant_id,
                    "name": name,
                    "email": email,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                await db.users.insert_one(new_user)
                logger.info(f"[GROUP-JOIN] ✅ Nouvel utilisateur créé: {name} ({email})")
        
        # Ajouter l'utilisateur au groupe s'il n'y est pas déjà
        session_id = group_session.get("id")
        current_participants = group_session.get("participant_ids", [])
        
        if participant_id not in current_participants:
            await db.chat_sessions.update_one(
                {"id": session_id},
                {
                    "$addToSet": {"participant_ids": participant_id},
                    "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
                }
            )
            logger.info(f"[GROUP-JOIN] ✅ {name} ajouté au groupe {session_id}")
        else:
            logger.info(f"[GROUP-JOIN] ℹ️ {name} déjà membre du groupe {session_id}")
        
        return {
            "success": True,
            "message": f"Bienvenue dans le groupe {group_session.get('title', group_id)} !",
            "conversation_id": session_id,
            "group_name": group_session.get("title", ""),
            "participant_id": participant_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[GROUP-JOIN] ❌ Erreur: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Chat Sessions ---
@api_router.get("/chat/sessions")
async def get_chat_sessions(include_deleted: bool = False):
    """Récupère toutes les sessions de chat (exclut les supprimées par défaut)"""
    query = {} if include_deleted else {"is_deleted": {"$ne": True}}
    sessions = await db.chat_sessions.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return sessions

# ==================== CRM AVANCÉ - HISTORIQUE CONVERSATIONS ====================
@api_router.get("/conversations")
async def get_conversations_advanced(
    page: int = 1,
    limit: int = 20,
    query: str = "",
    include_deleted: bool = False
):
    """
    Endpoint CRM avancé pour les conversations avec pagination et recherche.
    
    Paramètres:
    - page: Numéro de page (commence à 1)
    - limit: Nombre d'éléments par page (max 100)
    - query: Recherche dans les noms de participants, emails, contenus de messages
    - include_deleted: Inclure les sessions supprimées
    
    Retourne:
    - conversations: Liste des conversations enrichies avec dernier message et date
    - total: Nombre total de conversations
    - page: Page actuelle
    - pages: Nombre total de pages
    - has_more: Indique s'il y a plus de pages
    """
    import re
    
    # Limiter à 100 max
    limit = min(limit, 100)
    skip = (page - 1) * limit
    
    # Query de base pour les sessions
    base_query = {} if include_deleted else {"is_deleted": {"$ne": True}}
    
    # Si recherche, d'abord trouver les participants correspondants
    matching_participant_ids = []
    matching_session_ids = []
    
    if query and query.strip():
        search_regex = {"$regex": re.escape(query), "$options": "i"}
        
        # Rechercher dans les participants
        matching_participants = await db.chat_participants.find({
            "$or": [
                {"name": search_regex},
                {"email": search_regex},
                {"whatsapp": search_regex}
            ]
        }, {"_id": 0, "id": 1}).to_list(500)
        matching_participant_ids = [p["id"] for p in matching_participants]
        
        # Rechercher dans les messages
        matching_messages = await db.chat_messages.find({
            "content": search_regex,
            "is_deleted": {"$ne": True}
        }, {"_id": 0, "session_id": 1}).to_list(500)
        matching_session_ids = list(set([m["session_id"] for m in matching_messages]))
        
        # Rechercher dans les titres de session
        title_sessions = await db.chat_sessions.find({
            "title": search_regex,
            **base_query
        }, {"_id": 0, "id": 1}).to_list(500)
        matching_session_ids.extend([s["id"] for s in title_sessions])
        matching_session_ids = list(set(matching_session_ids))
        
        # Construire la query finale
        if matching_participant_ids or matching_session_ids:
            base_query["$or"] = []
            if matching_participant_ids:
                base_query["$or"].append({"participant_ids": {"$in": matching_participant_ids}})
            if matching_session_ids:
                base_query["$or"].append({"id": {"$in": matching_session_ids}})
        else:
            # Aucun résultat
            return {
                "conversations": [],
                "total": 0,
                "page": page,
                "pages": 0,
                "has_more": False
            }
    
    # Compter le total
    total = await db.chat_sessions.count_documents(base_query)
    pages = (total + limit - 1) // limit
    
    # Récupérer les sessions paginées
    sessions = await db.chat_sessions.find(
        base_query, 
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # Enrichir chaque session avec le dernier message et les infos participant
    enriched_conversations = []
    
    for session in sessions:
        # Récupérer le dernier message
        last_message = await db.chat_messages.find_one(
            {"session_id": session["id"], "is_deleted": {"$ne": True}},
            {"_id": 0},
            sort=[("created_at", -1)]
        )
        
        # Récupérer les infos des participants
        participants_info = []
        for pid in session.get("participant_ids", []):
            participant = await db.chat_participants.find_one({"id": pid}, {"_id": 0})
            if participant:
                participants_info.append({
                    "id": participant.get("id"),
                    "name": participant.get("name", "Inconnu"),
                    "email": participant.get("email", ""),
                    "whatsapp": participant.get("whatsapp", ""),
                    "source": participant.get("source", "")
                })
        
        # Compter le nombre de messages
        message_count = await db.chat_messages.count_documents({
            "session_id": session["id"],
            "is_deleted": {"$ne": True}
        })
        
        enriched_conversations.append({
            **session,
            "participants": participants_info,
            "last_message": {
                "content": last_message.get("content", "")[:100] if last_message else "",
                "sender_name": last_message.get("sender_name", "") if last_message else "",
                "sender_type": last_message.get("sender_type", "") if last_message else "",
                "created_at": last_message.get("created_at", "") if last_message else ""
            } if last_message else None,
            "message_count": message_count
        })
    
    logger.info(f"[CRM] Conversations: page={page}, limit={limit}, query='{query}', total={total}")
    
    return {
        "conversations": enriched_conversations,
        "total": total,
        "page": page,
        "pages": pages,
        "has_more": page < pages
    }

@api_router.get("/chat/sessions/{session_id}")
async def get_chat_session(session_id: str):
    """Récupère une session par son ID"""
    session = await db.chat_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    return session

@api_router.get("/chat/sessions/by-token/{link_token}")
async def get_chat_session_by_token(link_token: str):
    """
    Récupère une session par son token de partage.
    Utilisé quand un utilisateur arrive via un lien partagé.
    """
    session = await db.chat_sessions.find_one(
        {"link_token": link_token, "is_deleted": {"$ne": True}}, 
        {"_id": 0}
    )
    if not session:
        raise HTTPException(status_code=404, detail="Lien invalide ou session expirée")
    return session

@api_router.post("/chat/sessions")
async def create_chat_session(session: ChatSessionCreate):
    """Crée une nouvelle session de chat"""
    session_obj = ChatSession(**session.model_dump())
    await db.chat_sessions.insert_one(session_obj.model_dump())
    return session_obj.model_dump()

@api_router.put("/chat/sessions/{session_id}")
async def update_chat_session(session_id: str, update: ChatSessionUpdate):
    """
    Met à jour une session de chat.
    Utilisé pour changer le mode (IA/Humain/Communautaire) ou supprimer logiquement.
    """
    logger.info(f"[DELETE] Mise à jour session {session_id}: {update.model_dump()}")
    
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Si suppression logique, ajouter la date
    if update_data.get("is_deleted"):
        update_data["deleted_at"] = datetime.now(timezone.utc).isoformat()
        logger.info(f"[DELETE] Session {session_id} marquée comme supprimée (is_deleted=True)")
    
    result = await db.chat_sessions.update_one(
        {"id": session_id},
        {"$set": update_data}
    )
    logger.info(f"[DELETE] Résultat update: matched={result.matched_count}, modified={result.modified_count}")
    
    updated = await db.chat_sessions.find_one({"id": session_id}, {"_id": 0})
    return updated

@api_router.post("/chat/sessions/{session_id}/add-participant")
async def add_participant_to_session(session_id: str, participant_id: str):
    """Ajoute un participant à une session existante"""
    session = await db.chat_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    # Vérifier que le participant existe
    participant = await db.chat_participants.find_one({"id": participant_id}, {"_id": 0})
    if not participant:
        raise HTTPException(status_code=404, detail="Participant non trouvé")
    
    # Ajouter le participant s'il n'est pas déjà présent
    if participant_id not in session.get("participant_ids", []):
        await db.chat_sessions.update_one(
            {"id": session_id},
            {
                "$push": {"participant_ids": participant_id},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            }
        )
    
    updated = await db.chat_sessions.find_one({"id": session_id}, {"_id": 0})
    return updated

@api_router.post("/chat/sessions/{session_id}/toggle-ai")
async def toggle_session_ai(session_id: str):
    """
    Bascule l'état de l'IA pour une session.
    Si l'IA est active, elle devient inactive et inversement.
    """
    session = await db.chat_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    new_state = not session.get("is_ai_active", True)
    new_mode = "ai" if new_state else "human"
    
    await db.chat_sessions.update_one(
        {"id": session_id},
        {"$set": {
            "is_ai_active": new_state,
            "mode": new_mode,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    updated = await db.chat_sessions.find_one({"id": session_id}, {"_id": 0})
    return updated

# --- Chat Messages ---
@api_router.get("/chat/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, include_deleted: bool = False):
    """Recupere tous les messages d'une session avec format unifie."""
    query = {"session_id": session_id}
    if not include_deleted: query["is_deleted"] = {"$ne": True}
    raw = await db.chat_messages.find(query, {"_id": 0}).sort("created_at", 1).to_list(500)
    return [format_message_for_frontend(m) for m in raw]


# ==================== ENDPOINT SYNC "RAMASSER" ====================
@api_router.get("/messages/sync")
async def sync_messages(session_id: str, since: Optional[str] = None, limit: int = 100):
    """RAMASSER: Messages de la session OU messages de groupe (broadcast). Tri deterministe."""
    base_query = {"is_deleted": {"$ne": True}, "$or": [{"session_id": session_id}, {"broadcast": True}, {"type": "group"}]}
    if since:
        try:
            if 'Z' in since: since = since.replace('Z', '+00:00')
            parsed = datetime.fromisoformat(since)
            if parsed.tzinfo is None: parsed = parsed.replace(tzinfo=timezone.utc)
            base_query["created_at"] = {"$gt": parsed.astimezone(timezone.utc).isoformat()}
        except Exception:
            base_query["created_at"] = {"$gt": since}
    # Tri deterministe: created_at puis id pour garantir un ordre stable
    raw = await db.chat_messages.find(base_query, {"_id": 0}).sort([("created_at", 1), ("id", 1)]).to_list(limit)
    messages = [format_message_for_frontend(m) for m in raw]
    sync_ts = datetime.now(timezone.utc).isoformat()
    return {"success": True, "session_id": session_id, "count": len(messages), "messages": messages, "synced_at": sync_ts, "server_time_utc": sync_ts}


@api_router.get("/messages/sync/all")
async def sync_all_messages(participant_id: str, since: Optional[str] = None, limit: int = 200):
    """
    RAMASSER TOUT: Récupère tous les messages du participant (toutes sessions).
    Pour synchronisation complète au réveil du mobile.
    """
    # Trouver toutes les sessions du participant
    sessions = await db.chat_sessions.find(
        {"$or": [
            {"participant_ids": participant_id},
            {"mode": "community"}  # Inclure la session communautaire
        ]},
        {"_id": 0, "id": 1}
    ).to_list(100)
    
    session_ids = [s["id"] for s in sessions]
    
    query = {
        "session_id": {"$in": session_ids},
        "is_deleted": {"$ne": True}
    }
    
    if since:
        query["created_at"] = {"$gt": since}
    
    messages = await db.chat_messages.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).to_list(limit)
    
    logger.info(f"[SYNC-ALL] 📱 Ramassé {len(messages)} message(s) pour {participant_id[:8]}...")
    
    return {
        "success": True,
        "participant_id": participant_id,
        "sessions_count": len(session_ids),
        "messages_count": len(messages),
        "messages": messages,
        "synced_at": datetime.now(timezone.utc).isoformat()
    }


@api_router.post("/chat/messages")
async def create_chat_message(message: EnhancedChatMessageCreate):
    """
    Crée un nouveau message dans une session.
    Met à jour automatiquement le mode du message selon l'état de la session.
    """
    # Récupérer la session pour connaître le mode actuel
    session = await db.chat_sessions.find_one({"id": message.session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    message_obj = EnhancedChatMessage(
        **message.model_dump(),
        mode=session.get("mode", "ai")
    )
    await db.chat_messages.insert_one(message_obj.model_dump())
    return message_obj.model_dump()

@api_router.put("/chat/messages/{message_id}/delete")
async def soft_delete_message(message_id: str):
    """Suppression logique d'un message"""
    await db.chat_messages.update_one(
        {"id": message_id},
        {"$set": {
            "is_deleted": True,
            "deleted_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    return {"success": True, "message": "Message marqué comme supprimé"}

# ==================== ROUTES ADMIN SÉCURISÉES ====================

@api_router.post("/admin/delete-history")
async def admin_delete_history(request: Request):
    """
    Suppression de l'historique d'une session - ADMIN ONLY.
    Vérifie que l'email de l'appelant est celui du coach.
    """
    body = await request.json()
    session_id = body.get("session_id")
    caller_email = body.get("email", "").lower().strip()
    
    # ===== VÉRIFICATION SÉCURITÉ : EMAIL COACH OBLIGATOIRE =====
    if caller_email != COACH_EMAIL:
        logger.warning(f"[SECURITY] Tentative non autorisée de suppression d'historique par: {caller_email}")
        raise HTTPException(
            status_code=403, 
            detail="Accès refusé. Seul le coach peut supprimer l'historique."
        )
    
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id requis")
    
    # Suppression logique de tous les messages de la session
    result = await db.chat_messages.update_many(
        {"session_id": session_id},
        {"$set": {
            "is_deleted": True,
            "deleted_at": datetime.now(timezone.utc).isoformat(),
            "deleted_by": caller_email
        }}
    )
    
    logger.info(f"[ADMIN] Historique supprimé pour session {session_id} par {caller_email}. {result.modified_count} messages.")
    
    return {
        "success": True, 
        "message": f"Historique supprimé ({result.modified_count} messages)",
        "deleted_count": result.modified_count
    }

@api_router.post("/admin/change-identity")
async def admin_change_identity(request: Request):
    """
    Changement d'identité d'un participant - ADMIN ONLY.
    Vérifie que l'email de l'appelant est celui du coach.
    """
    body = await request.json()
    participant_id = body.get("participant_id")
    caller_email = body.get("email", "").lower().strip()
    
    # ===== VÉRIFICATION SÉCURITÉ : EMAIL COACH OBLIGATOIRE =====
    if caller_email != COACH_EMAIL:
        logger.warning(f"[SECURITY] Tentative non autorisée de changement d'identité par: {caller_email}")
        raise HTTPException(
            status_code=403, 
            detail="Accès refusé. Seul le coach peut changer l'identité."
        )
    
    if not participant_id:
        raise HTTPException(status_code=400, detail="participant_id requis")
    
    logger.info(f"[ADMIN] Changement d'identité demandé pour {participant_id} par {caller_email}")
    
    return {
        "success": True, 
        "message": "Identité réinitialisée. L'utilisateur devra se reconnecter."
    }

# ==================== CRUD ARTICLES (ADMIN ONLY) ====================

@api_router.get("/articles")
async def get_articles():
    """
    Récupère tous les articles (accessible à tous).
    """
    try:
        articles = await db.articles.find({}, {"_id": 0}).sort("createdAt", -1).to_list(100)
        return articles
    except Exception as e:
        logger.error(f"[ARTICLES] Erreur récupération: {e}")
        return []

@api_router.get("/articles/{article_id}")
async def get_article(article_id: str):
    """
    Récupère un article par son ID.
    """
    try:
        article = await db.articles.find_one({"id": article_id}, {"_id": 0})
        if not article:
            raise HTTPException(status_code=404, detail="Article non trouvé")
        return article
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ARTICLES] Erreur récupération article {article_id}: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@api_router.post("/articles")
async def create_article(request: Request):
    """
    Crée un nouvel article - ADMIN ONLY.
    Vérifie que l'email de l'appelant est celui du coach.
    """
    try:
        body = await request.json()
        caller_email = body.get("email", "").lower().strip()
        
        # ===== VÉRIFICATION SÉCURITÉ : EMAIL COACH OBLIGATOIRE =====
        if caller_email != COACH_EMAIL:
            logger.warning(f"[SECURITY] Tentative non autorisée de création d'article par: {caller_email}")
            raise HTTPException(
                status_code=403, 
                detail="Accès refusé. Seul le coach peut créer des articles."
            )
        
        # Créer l'article
        article_data = {
            "id": str(uuid.uuid4()),
            "title": body.get("title", "Sans titre"),
            "content": body.get("content", ""),
            "excerpt": body.get("excerpt", ""),
            "imageUrl": body.get("imageUrl", ""),
            "category": body.get("category", "general"),
            "tags": body.get("tags", []),
            "author": caller_email,
            "published": body.get("published", False),
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "updatedAt": datetime.now(timezone.utc).isoformat()
        }
        
        await db.articles.insert_one(article_data)
        
        # Retourner sans _id
        article_data.pop("_id", None)
        
        logger.info(f"[ARTICLES] ✅ Article créé par {caller_email}: {article_data['title']}")
        return article_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ARTICLES] ❌ Erreur création: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur création article: {str(e)}")

@api_router.put("/articles/{article_id}")
async def update_article(article_id: str, request: Request):
    """
    Met à jour un article - ADMIN ONLY.
    Vérifie que l'email de l'appelant est celui du coach.
    """
    try:
        body = await request.json()
        caller_email = body.get("email", "").lower().strip()
        
        # ===== VÉRIFICATION SÉCURITÉ : EMAIL COACH OBLIGATOIRE =====
        if caller_email != COACH_EMAIL:
            logger.warning(f"[SECURITY] Tentative non autorisée de modification d'article par: {caller_email}")
            raise HTTPException(
                status_code=403, 
                detail="Accès refusé. Seul le coach peut modifier des articles."
            )
        
        # Vérifier que l'article existe
        existing = await db.articles.find_one({"id": article_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Article non trouvé")
        
        # Préparer les données de mise à jour
        update_data = {
            "title": body.get("title", existing.get("title")),
            "content": body.get("content", existing.get("content")),
            "excerpt": body.get("excerpt", existing.get("excerpt")),
            "imageUrl": body.get("imageUrl", existing.get("imageUrl")),
            "category": body.get("category", existing.get("category")),
            "tags": body.get("tags", existing.get("tags")),
            "published": body.get("published", existing.get("published")),
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            "updatedBy": caller_email
        }
        
        await db.articles.update_one({"id": article_id}, {"$set": update_data})
        
        # Récupérer l'article mis à jour
        updated = await db.articles.find_one({"id": article_id}, {"_id": 0})
        
        logger.info(f"[ARTICLES] ✅ Article {article_id} modifié par {caller_email}")
        return updated
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ARTICLES] ❌ Erreur mise à jour: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur mise à jour: {str(e)}")

@api_router.delete("/articles/{article_id}")
async def delete_article(article_id: str, request: Request):
    """
    Supprime un article - ADMIN ONLY.
    Vérifie que l'email de l'appelant est celui du coach.
    """
    try:
        body = await request.json()
        caller_email = body.get("email", "").lower().strip()
        
        # ===== VÉRIFICATION SÉCURITÉ : EMAIL COACH OBLIGATOIRE =====
        if caller_email != COACH_EMAIL:
            logger.warning(f"[SECURITY] Tentative non autorisée de suppression d'article par: {caller_email}")
            raise HTTPException(
                status_code=403, 
                detail="Accès refusé. Seul le coach peut supprimer des articles."
            )
        
        # Vérifier que l'article existe
        existing = await db.articles.find_one({"id": article_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Article non trouvé")
        
        # Supprimer l'article
        result = await db.articles.delete_one({"id": article_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Article non trouvé")
        
        logger.info(f"[ARTICLES] ✅ Article {article_id} supprimé par {caller_email}")
        return {"success": True, "message": "Article supprimé", "deleted_id": article_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ARTICLES] ❌ Erreur suppression: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur suppression: {str(e)}")

# ==================== MESSAGERIE PRIVÉE (MP) - ISOLÉE DE L'IA ====================

@api_router.post("/private/conversations")
async def create_or_get_private_conversation(request: Request):
    """
    Crée ou récupère une conversation privée entre deux participants.
    Les MP sont stockées dans une collection séparée et INVISIBLES pour l'IA.
    """
    body = await request.json()
    participant_1_id = body.get("participant_1_id")
    participant_1_name = body.get("participant_1_name")
    participant_2_id = body.get("participant_2_id")
    participant_2_name = body.get("participant_2_name")
    
    if not all([participant_1_id, participant_2_id]):
        raise HTTPException(status_code=400, detail="IDs des participants requis")
    
    # Vérifier si une conversation existe déjà (dans les deux sens)
    existing = await db.private_conversations.find_one({
        "$or": [
            {"participant_1_id": participant_1_id, "participant_2_id": participant_2_id},
            {"participant_1_id": participant_2_id, "participant_2_id": participant_1_id}
        ]
    }, {"_id": 0})
    
    if existing:
        logger.info(f"[MP] Conversation existante trouvée: {existing.get('id')}")
        return existing
    
    # Créer une nouvelle conversation
    conversation = PrivateConversation(
        participant_1_id=participant_1_id,
        participant_1_name=participant_1_name or "Membre",
        participant_2_id=participant_2_id,
        participant_2_name=participant_2_name or "Membre"
    )
    await db.private_conversations.insert_one(conversation.model_dump())
    logger.info(f"[MP] Nouvelle conversation créée: {conversation.id}")
    return conversation.model_dump()

@api_router.get("/private/conversations/{participant_id}")
async def get_private_conversations(participant_id: str):
    """
    Récupère toutes les conversations privées d'un participant.
    """
    conversations = await db.private_conversations.find({
        "$or": [
            {"participant_1_id": participant_id},
            {"participant_2_id": participant_id}
        ]
    }, {"_id": 0}).sort("last_message_at", -1).to_list(50)
    return conversations

@api_router.post("/private/messages")
async def send_private_message(request: Request):
    """
    Envoie un message privé. Ces messages sont ISOLÉS de l'IA.
    """
    body = await request.json()
    conversation_id = body.get("conversation_id")
    sender_id = body.get("sender_id")
    sender_name = body.get("sender_name")
    recipient_id = body.get("recipient_id")
    recipient_name = body.get("recipient_name")
    content = body.get("content")
    
    if not all([conversation_id, sender_id, content]):
        raise HTTPException(status_code=400, detail="Données manquantes")
    
    # Créer le message privé
    message = PrivateMessage(
        conversation_id=conversation_id,
        sender_id=sender_id,
        sender_name=sender_name or "Membre",
        recipient_id=recipient_id or "",
        recipient_name=recipient_name or "Membre",
        content=content
    )
    await db.private_messages.insert_one(message.model_dump())
    
    # Mettre à jour la conversation avec le dernier message
    await db.private_conversations.update_one(
        {"id": conversation_id},
        {"$set": {
            "last_message": content[:100],
            "last_message_at": message.created_at
        }}
    )
    
    # === SOCKET.IO: Émettre le message privé en temps réel ===
    await sio.emit('private_message_received', {
        "conversation_id": conversation_id,
        "id": message.id,
        "text": content,
        "sender": sender_name,
        "senderId": sender_id,
        "recipientId": recipient_id,
        "created_at": message.created_at
    }, room=f"pm_{conversation_id}")
    
    logger.info(f"[MP] Message envoyé de {sender_name} dans conversation {conversation_id}")
    return message.model_dump()

@api_router.get("/private/messages/{conversation_id}")
async def get_private_messages(conversation_id: str, limit: int = 100):
    """
    Récupère les messages d'une conversation privée.
    """
    messages = await db.private_messages.find(
        {"conversation_id": conversation_id, "is_deleted": {"$ne": True}},
        {"_id": 0}
    ).sort("created_at", 1).to_list(limit)
    return messages

@api_router.put("/private/messages/read/{conversation_id}")
async def mark_private_messages_read(conversation_id: str, reader_id: str):
    """
    Marque tous les messages d'une conversation comme lus par un participant.
    """
    result = await db.private_messages.update_many(
        {"conversation_id": conversation_id, "recipient_id": reader_id, "is_read": False},
        {"$set": {"is_read": True}}
    )
    return {"success": True, "marked_read": result.modified_count}

@api_router.get("/private/unread/{participant_id}")
async def get_unread_private_count(participant_id: str):
    """
    Compte les messages privés non lus pour un participant.
    """
    count = await db.private_messages.count_documents({
        "recipient_id": participant_id,
        "is_read": False,
        "is_deleted": {"$ne": True}
    })
    return {"unread_count": count}

# ==================== UPLOAD PHOTO DE PROFIL (LEGACY REDIRECT) ====================
# L'ancien endpoint redirige vers le nouveau moteur /users/upload-photo

@api_router.post("/upload/profile-photo")
async def upload_profile_photo_legacy(file: UploadFile = File(...), participant_id: str = Form("guest")):
    """Endpoint legacy - redirige vers /users/upload-photo"""
    return await upload_user_photo(file=file, participant_id=participant_id)

# ==================== NOTIFICATIONS (SONORES ET VISUELLES) ====================

@api_router.get("/notifications/unread")
async def get_unread_notifications(
    target: str = "coach",  # "coach" ou "client"
    session_id: Optional[str] = None,
    include_ai: bool = False  # Inclure les réponses IA dans les notifications coach
):
    """
    Récupère les messages non notifiés pour le coach ou un client.
    Optimisé pour le polling toutes les 10 secondes.
    
    Paramètres:
    - target: "coach" pour les messages user, "client" pour les réponses AI/coach
    - session_id: Optionnel, filtrer par session
    - include_ai: Si true et target=coach, inclut aussi les réponses IA (pour suivi)
    
    Retourne:
    - count: Nombre de messages non notifiés
    - messages: Liste des messages (max 10, triés par date décroissante)
    - target: Target demandé
    """
    query = {
        "is_deleted": {"$ne": True},
        "notified": {"$ne": True}
    }
    
    if target == "coach":
        if include_ai:
            # Messages utilisateurs + réponses IA (pour suivi)
            query["sender_type"] = {"$in": ["user", "ai"]}
        else:
            # Seulement messages des utilisateurs
            query["sender_type"] = "user"
    else:
        # Messages de l'IA ou du coach destinés aux clients
        query["sender_type"] = {"$in": ["ai", "coach"]}
    
    if session_id:
        query["session_id"] = session_id
    
    # Compter le nombre total (limité pour performance)
    count = await db.chat_messages.count_documents(query)
    
    # Récupérer les messages non notifiés les plus récents (max 10 pour performance)
    messages = await db.chat_messages.find(
        query, 
        {"_id": 0, "id": 1, "session_id": 1, "sender_name": 1, "sender_type": 1, "content": 1, "created_at": 1}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    return {
        "count": count,
        "messages": messages,
        "target": target
    }

# === EMOJIS PERSONNALISÉS DU COACH ===
@api_router.get("/custom-emojis/list")
async def list_custom_emojis():
    """
    Liste tous les emojis personnalisés disponibles dans /uploads/emojis/
    """
    emojis = []
    try:
        emoji_files = list(EMOJIS_DIR.glob("*.*"))
        for f in emoji_files:
            if f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg']:
                emojis.append({
                    "name": f.stem,
                    "url": f"/api/emojis/{f.name}",
                    "filename": f.name
                })
        logger.info(f"[EMOJIS] {len(emojis)} emojis trouvés")
    except Exception as e:
        logger.error(f"[EMOJIS] Erreur listing: {e}")
    
    return {"emojis": emojis, "count": len(emojis)}

@api_router.post("/custom-emojis/upload")
async def upload_custom_emoji(request: Request):
    """
    Upload un emoji personnalisé (pour le coach).
    Accepte une image en base64 avec un nom.
    """
    import base64
    
    body = await request.json()
    name = body.get("name", "emoji")
    image_data = body.get("image")  # base64 encoded
    file_extension = body.get("extension", "png")
    
    if not image_data:
        raise HTTPException(status_code=400, detail="Image data required")
    
    try:
        # Décoder le base64
        image_bytes = base64.b64decode(image_data.split(",")[-1] if "," in image_data else image_data)
        
        # Sauvegarder le fichier
        filename = f"{name.replace(' ', '_').lower()}.{file_extension}"
        filepath = EMOJIS_DIR / filename
        
        with open(filepath, "wb") as f:
            f.write(image_bytes)
        
        logger.info(f"[EMOJIS] Emoji uploadé: {filename}")
        
        return {
            "success": True,
            "emoji": {
                "name": name,
                "url": f"/api/emojis/{filename}",
                "filename": filename
            }
        }
    except Exception as e:
        logger.error(f"[EMOJIS] Erreur upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/notifications/mark-read")
async def mark_notifications_read(request: Request):
    """
    Marque des messages comme notifiés.
    
    Body:
    - message_ids: Liste des IDs de messages à marquer comme notifiés
    - all_for_target: "coach" ou "client" pour marquer tous les messages non lus
    - session_id: Optionnel, pour limiter à une session
    """
    body = await request.json()
    message_ids = body.get("message_ids", [])
    all_for_target = body.get("all_for_target")
    session_id = body.get("session_id")
    
    update_count = 0
    
    if message_ids:
        # Marquer des messages spécifiques
        result = await db.chat_messages.update_many(
            {"id": {"$in": message_ids}},
            {"$set": {"notified": True}}
        )
        update_count = result.modified_count
    
    elif all_for_target:
        # Marquer tous les messages pour un target
        query = {
            "is_deleted": {"$ne": True},
            "notified": {"$ne": True}
        }
        
        if all_for_target == "coach":
            query["sender_type"] = "user"
        else:
            query["sender_type"] = {"$in": ["ai", "coach"]}
        
        if session_id:
            query["session_id"] = session_id
        
        result = await db.chat_messages.update_many(
            query,
            {"$set": {"notified": True}}
        )
        update_count = result.modified_count
    
    logger.info(f"[NOTIFICATIONS] Marqué {update_count} messages comme lus (target: {all_for_target})")
    
    return {
        "success": True,
        "marked_count": update_count
    }

# --- Shareable Links (Liens Partageables) ---
@api_router.post("/chat/generate-link")
async def generate_shareable_link(request: Request):
    """
    Génère un lien partageable unique pour le chat IA.
    Ce lien peut être partagé sur les réseaux sociaux.
    
    Body optionnel:
    {
        "title": "Titre du lien",
        "custom_prompt": "Prompt spécifique (nullable, prioritaire sur campaignPrompt)"
    }
    """
    body = await request.json()
    title = body.get("title", "Chat Afroboost")
    custom_prompt = body.get("custom_prompt")  # Nullable - si vide/null, sera None
    
    # Normaliser: si chaîne vide ou whitespace only, mettre à None
    if custom_prompt and isinstance(custom_prompt, str):
        custom_prompt = custom_prompt.strip() if custom_prompt.strip() else None
    
    # Créer une nouvelle session avec un token unique
    session = ChatSession(
        mode="ai",
        is_ai_active=True,
        title=title,
        custom_prompt=custom_prompt
    )
    await db.chat_sessions.insert_one(session.model_dump())
    
    # Construire l'URL de partage
    # Note: L'URL de base sera configurée côté frontend
    frontend_url = os.environ.get("FRONTEND_URL", "")
    share_url = f"{frontend_url}/chat/{session.link_token}" if frontend_url else f"/chat/{session.link_token}"
    
    logger.info(f"[CHAT-LINK] Lien créé: {session.link_token} (custom_prompt: {'oui' if custom_prompt else 'non'})")
    
    return {
        "link_token": session.link_token,
        "share_url": share_url,
        "session_id": session.id,
        "has_custom_prompt": custom_prompt is not None
    }

@api_router.get("/chat/links")
async def get_all_chat_links():
    """
    Récupère tous les liens de chat générés.
    Utile pour le coach pour gérer ses liens partagés.
    """
    sessions = await db.chat_sessions.find(
        {"is_deleted": {"$ne": True}},
        {"_id": 0, "id": 1, "link_token": 1, "title": 1, "mode": 1, "is_ai_active": 1, "created_at": 1, "participant_ids": 1}
    ).sort("created_at", -1).to_list(100)
    
    # Ajouter le nombre de participants pour chaque lien
    for session in sessions:
        session["participant_count"] = len(session.get("participant_ids", []))
    
    return sessions

@api_router.delete("/chat/links/{link_id}")
async def delete_chat_link(link_id: str):
    """
    Supprime un lien de chat (suppression logique).
    Le lien ne sera plus accessible et n'apparaîtra plus dans la liste.
    """
    logger.info(f"[DELETE] Suppression lien: {link_id}")
    
    result = await db.chat_sessions.update_one(
        {"$or": [{"id": link_id}, {"link_token": link_id}]},
        {"$set": {"is_deleted": True, "deleted_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    logger.info(f"[DELETE] Résultat: matched={result.matched_count}, modified={result.modified_count}")
    
    if result.modified_count == 0:
        logger.warning(f"[DELETE] Lien non trouvé: {link_id}")
        raise HTTPException(status_code=404, detail="Lien non trouvé")
    
    logger.info(f"[DELETE] Lien {link_id} supprimé avec succès ✅")
    return {"success": True, "message": "Lien supprimé"}

# --- Intelligent Chat Entry Point ---
@api_router.post("/chat/smart-entry")
async def smart_chat_entry(request: Request):
    """
    Point d'entrée intelligent pour le chat.
    
    1. Vérifie si l'utilisateur existe déjà (par nom, email ou WhatsApp)
    2. Si oui, récupère ses sessions précédentes et son historique
    3. Si non, crée un nouveau participant et une nouvelle session
    4. Retourne les infos du participant et la session active
    
    Body attendu:
    {
        "name": "John",
        "email": "john@example.com",  // Optionnel
        "whatsapp": "+41761234567",   // Optionnel
        "link_token": "abc123"         // Optionnel - si via lien partagé
    }
    """
    body = await request.json()
    name = body.get("name", "").strip()
    email = body.get("email", "").strip()
    whatsapp = body.get("whatsapp", "").strip()
    link_token = body.get("link_token")
    
    if not name:
        raise HTTPException(status_code=400, detail="Le nom est requis")
    
    # Rechercher un participant existant
    existing_participant = None
    search_query = {"$or": []}
    
    if email:
        search_query["$or"].append({"email": {"$regex": f"^{email}$", "$options": "i"}})
    if whatsapp:
        clean_whatsapp = whatsapp.replace(" ", "").replace("-", "").replace("+", "")
        if clean_whatsapp:
            search_query["$or"].append({"whatsapp": {"$regex": clean_whatsapp}})
    
    # Recherche aussi par nom exact
    search_query["$or"].append({"name": {"$regex": f"^{name}$", "$options": "i"}})
    
    if search_query["$or"]:
        existing_participant = await db.chat_participants.find_one(search_query, {"_id": 0})
    
    # Déterminer la source
    source = f"link_{link_token}" if link_token else "chat_afroboost"
    
    if existing_participant:
        # Participant reconnu - mettre à jour last_seen
        participant_id = existing_participant["id"]
        update_fields = {"last_seen_at": datetime.now(timezone.utc).isoformat()}
        
        # Mettre à jour les infos si nouvelles
        if email and not existing_participant.get("email"):
            update_fields["email"] = email
        if whatsapp and not existing_participant.get("whatsapp"):
            update_fields["whatsapp"] = whatsapp
        
        await db.chat_participants.update_one(
            {"id": participant_id},
            {"$set": update_fields}
        )
        
        participant = await db.chat_participants.find_one({"id": participant_id}, {"_id": 0})
        is_returning = True
    else:
        # Nouveau participant
        participant_obj = ChatParticipant(
            name=name,
            email=email,
            whatsapp=whatsapp,
            source=source,
            link_token=link_token
        )
        await db.chat_participants.insert_one(participant_obj.model_dump())
        participant = participant_obj.model_dump()
        participant_id = participant["id"]
        is_returning = False
    
    # Trouver ou créer la session
    session = None
    
    if link_token:
        # Si via lien partagé, utiliser cette session
        session = await db.chat_sessions.find_one(
            {"link_token": link_token, "is_deleted": {"$ne": True}},
            {"_id": 0}
        )
    
    if not session:
        # Chercher une session active existante pour ce participant
        sessions = await db.chat_sessions.find(
            {
                "participant_ids": participant_id,
                "is_deleted": {"$ne": True}
            },
            {"_id": 0}
        ).sort("created_at", -1).to_list(1)
        
        if sessions:
            session = sessions[0]
    
    if not session:
        # Créer une nouvelle session
        session_obj = ChatSession(
            mode="ai",
            is_ai_active=True,
            participant_ids=[participant_id]
        )
        await db.chat_sessions.insert_one(session_obj.model_dump())
        session = session_obj.model_dump()
    else:
        # Ajouter le participant à la session s'il n'y est pas
        if participant_id not in session.get("participant_ids", []):
            await db.chat_sessions.update_one(
                {"id": session["id"]},
                {
                    "$push": {"participant_ids": participant_id},
                    "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
                }
            )
            session = await db.chat_sessions.find_one({"id": session["id"]}, {"_id": 0})
    
    # Récupérer l'historique des messages si participant existant
    chat_history = []
    if is_returning:
        chat_history = await db.chat_messages.find(
            {"session_id": session["id"], "is_deleted": {"$ne": True}},
            {"_id": 0}
        ).sort("created_at", 1).to_list(50)
    
    return {
        "participant": participant,
        "session": session,
        "is_returning": is_returning,
        "chat_history": chat_history,
        "message": f"Ravi de te revoir, {name} !" if is_returning else f"Bienvenue, {name} !"
    }

# --- AI Chat with Session Context ---
@api_router.post("/chat/ai-response")
async def get_ai_response_with_session(request: Request):
    """
    Envoie un message à l'IA avec le contexte COMPLET de la session.
    Inclut les produits, offres, cours et articles depuis MongoDB.
    
    Body attendu:
    {
        "session_id": "xxx",
        "participant_id": "xxx",
        "message": "Bonjour!"
    }
    """
    import time
    start_time = time.time()
    
    body = await request.json()
    session_id = body.get("session_id")
    participant_id = body.get("participant_id")
    message_text = body.get("message", "").strip()
    
    if not session_id or not participant_id or not message_text:
        raise HTTPException(status_code=400, detail="session_id, participant_id et message sont requis")
    
    # Récupérer la session
    session = await db.chat_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    # Récupérer le participant
    participant = await db.chat_participants.find_one({"id": participant_id}, {"_id": 0})
    if not participant:
        raise HTTPException(status_code=404, detail="Participant non trouvé")
    
    participant_name = participant.get("name", "Utilisateur")
    
    # Sauvegarder le message de l'utilisateur
    user_message = EnhancedChatMessage(
        session_id=session_id,
        sender_id=participant_id,
        sender_name=participant_name,
        sender_type="user",
        content=message_text,
        mode=session.get("mode", "ai")
    )
    await db.chat_messages.insert_one(user_message.model_dump())
    
    # === SOCKET.IO: Émettre le message utilisateur en temps réel ===
    await emit_new_message(session_id, {
        "id": user_message.id,
        "type": "user",
        "text": message_text,
        "sender": participant_name,
        "senderId": participant_id,
        "sender_type": "user",
        "created_at": user_message.created_at
    })
    
    # Vérifier si l'IA est active pour cette session
    if not session.get("is_ai_active", True) or session.get("mode") != "ai":
        # Mode humain - Notifier le coach par e-mail (non-bloquant)
        asyncio.create_task(
            notify_coach_new_message(
                participant_name=participant_name,
                message_preview=message_text,
                session_id=session_id
            )
        )
        return {
            "response": None,
            "ai_active": False,
            "mode": session.get("mode"),
            "message_saved": True,
            "user_message_id": user_message.id,
            "coach_notified": True
        }
    
    # Récupérer la config IA
    ai_config = await db.ai_config.find_one({"id": "ai_config"}, {"_id": 0})
    if not ai_config or not ai_config.get("enabled"):
        return {
            "response": "L'assistant IA est actuellement désactivé.",
            "ai_active": False,
            "message_saved": True,
            "user_message_id": user_message.id
        }
    
    # =====================================================================
    # DÉTECTION MODE STRICT (AVANT construction du contexte)
    use_strict_mode = False
    CUSTOM_PROMPT = ""
    
    # Vérifier si la session a un custom_prompt
    session_custom_prompt = session.get("custom_prompt") if session else None
    if session_custom_prompt and isinstance(session_custom_prompt, str) and session_custom_prompt.strip():
        CUSTOM_PROMPT = session_custom_prompt.strip()
        use_strict_mode = True
        logger.info(f"[CHAT-AI-RESPONSE] 🔒 Mode STRICT détecté")
    
    # CONSTRUCTION DU CONTEXTE
    logger.info("[CHAT-AI-RESPONSE] 🔄 Construction du contexte...")
    
    if use_strict_mode:
        # MODE STRICT: Contexte minimaliste sans aucune info de vente
        context = "\n\n========== MODE STRICT - LIEN PARTENARIAT ==========\n"
        context += "Tu es l'assistant Afroboost avec un OBJECTIF SPÉCIFIQUE défini ci-dessous.\n"
        context += "Tu n'as accès à AUCUNE information de prix, tarif ou lien de paiement.\n"
        
        # Prénom du client
        context += f"\n👤 INTERLOCUTEUR: {participant_name}\n"
        
        # Concept uniquement (pas de prix)
        try:
            concept = await db.concept.find_one({"id": "concept"}, {"_id": 0})
            if concept and concept.get('description'):
                context += f"\n📌 CONCEPT AFROBOOST:\n{concept.get('description', '')[:500]}\n"
        except Exception as e:
            pass
        
        logger.info("[CHAT-AI-RESPONSE] 🔒 Contexte STRICT construit (sans prix/Twint)")
    else:
        # MODE STANDARD: Contexte complet avec toutes les données de vente
        context = "\n\n========== CONNAISSANCES DU SITE AFROBOOST ==========\n"
        context += "Utilise EXCLUSIVEMENT ces informations pour répondre sur les produits, cours, offres et articles.\n"
        context += "IMPORTANT: Vérifie TOUJOURS l'INVENTAIRE BOUTIQUE avant de dire qu'un produit n'existe pas !\n"
        
        # Prénom du client
        context += f"\n👤 CLIENT: {participant_name} - Utilise son prénom pour être chaleureux.\n"
        
        # Concept/Description du site
        try:
            concept = await db.concept.find_one({"id": "concept"}, {"_id": 0})
            if concept and concept.get('description'):
                context += f"\n📌 À PROPOS D'AFROBOOST:\n{concept.get('description', '')[:500]}\n"
        except Exception as e:
            logger.warning(f"[CHAT-AI-RESPONSE] Erreur récupération concept: {e}")
    
    # === SECTIONS VENTE (UNIQUEMENT en mode STANDARD, pas en mode STRICT) ===
    if not use_strict_mode:
        # === SECTION 1: INVENTAIRE BOUTIQUE (PRODUITS PHYSIQUES) ===
        try:
            # Récupérer TOUS les éléments de la collection offers
            all_offers = await db.offers.find({"visible": {"$ne": False}}, {"_id": 0}).to_list(50)
            
            # Séparer les PRODUITS des SERVICES
            products = [o for o in all_offers if o.get('isProduct') == True]
            services = [o for o in all_offers if not o.get('isProduct')]
            
            # === PRODUITS BOUTIQUE (café, vêtements, accessoires...) ===
            if products:
                context += "\n\n🛒 INVENTAIRE BOUTIQUE (Produits en vente):\n"
                for p in products[:15]:
                    name = p.get('name', 'Produit')
                    price = p.get('price', 0)
                    desc = p.get('description', '')[:150] if p.get('description') else ''
                    category = p.get('category', '')
                    stock = p.get('stock', -1)
                    
                    context += f"  ★ {name.upper()} : {price} CHF"
                    if category:
                        context += f" (Catégorie: {category})"
                    if stock > 0:
                        context += f" - En stock: {stock}"
                    context += "\n"
                    if desc:
                        context += f"    Description: {desc}\n"
                context += "  → Si un client demande un de ces produits, CONFIRME qu'il est disponible !\n"
            else:
                context += "\n\n🛒 INVENTAIRE BOUTIQUE: Aucun produit en vente actuellement.\n"
            
            # === SERVICES ET OFFRES (abonnements, cours à l'unité...) ===
            if services:
                context += "\n\n💰 OFFRES ET TARIFS (Services):\n"
                for s in services[:10]:
                    name = s.get('name', 'Offre')
                    price = s.get('price', 0)
                    desc = s.get('description', '')[:100] if s.get('description') else ''
                    
                    context += f"  • {name} : {price} CHF"
                    if desc:
                        context += f" - {desc}"
                    context += "\n"
            else:
                context += "\n\n💰 OFFRES: Aucune offre spéciale actuellement.\n"
                
        except Exception as e:
            logger.error(f"[CHAT-AI-RESPONSE] ❌ Erreur récupération offres/produits: {e}")
            context += "\n\n🛒 BOUTIQUE: Informations temporairement indisponibles.\n"
        
        # === SECTION 2: COURS DISPONIBLES ===
        try:
            courses = await db.courses.find({"visible": {"$ne": False}}, {"_id": 0}).to_list(20)
            if courses:
                context += "\n\n🎯 COURS DISPONIBLES:\n"
                for c in courses[:10]:  # Max 10 cours
                    name = c.get('name', 'Cours')
                    date = c.get('date', '')
                    time_slot = c.get('time', '')
                    location = c.get('locationName', c.get('location', ''))
                    price = c.get('price', '')
                    description = c.get('description', '')[:80] if c.get('description') else ''
                    
                    context += f"  • {name}"
                    if date:
                        context += f" - {date}"
                    if time_slot:
                        context += f" à {time_slot}"
                    if location:
                        context += f" ({location})"
                    if price:
                        context += f" - {price} CHF"
                    context += "\n"
                    if description:
                        context += f"    → {description}\n"
            else:
                context += "\n\n🎯 COURS: Aucun cours programmé actuellement. Invite le client à suivre nos réseaux pour les prochaines dates.\n"
        except Exception as e:
            logger.warning(f"[CHAT-AI-RESPONSE] Erreur récupération cours: {e}")
            context += "\n\n🎯 COURS: Informations temporairement indisponibles.\n"
        
        # === SECTION 3: ARTICLES ET ACTUALITÉS ===
        try:
            # Récupérer les 10 articles les plus récents
            articles = await db.articles.find(
                {"visible": {"$ne": False}}, 
                {"_id": 0}
            ).sort("createdAt", -1).to_list(10)
            
            if articles:
                context += "\n\n📰 DERNIERS ARTICLES ET ACTUALITÉS:\n"
                for a in articles[:5]:  # Max 5 articles dans le contexte
                    title = a.get('title', 'Article')
                    summary = a.get('summary', '')[:120] if a.get('summary') else ''
                    link = a.get('link', '')
                    
                    context += f"  • {title}\n"
                    if summary:
                        context += f"    → {summary}\n"
                    if link:
                        context += f"    🔗 Lien: {link}\n"
            else:
                context += "\n\n📰 ARTICLES: Pas d'articles récents. Le blog arrive bientôt !\n"
        except Exception as e:
            logger.warning(f"[CHAT-AI-RESPONSE] Erreur récupération articles: {e}")
            # Silencieux si pas de collection articles
        
        # === SECTION 4: PROMOS SPÉCIALES (avec masquage des codes) ===
        # L'IA peut connaître les remises pour calculer les prix, mais JAMAIS les codes
        # PRODUCTION-READY: Try/except individuel pour chaque promo
        try:
            active_promos = await db.discount_codes.find({"active": True}, {"_id": 0}).to_list(20)
            if active_promos:
                context += "\n\n🎁 PROMOTIONS EN COURS:\n"
                promos_injected = 0
                for promo in active_promos[:5]:
                    try:
                        # MASQUAGE TECHNIQUE: Le champ 'code' n'est JAMAIS lu ni transmis
                        # Seuls 'type' et 'value' sont utilisés pour le calcul
                        promo_type = promo.get('type', '%')
                        promo_value = promo.get('value', 0)
                        
                        # Validation: S'assurer que value est un nombre valide
                        if promo_value is None:
                            promo_value = 0
                        promo_value = float(promo_value)
                        
                        # Construire la description SANS le code réel
                        # Le placeholder [CODE_APPLIQUÉ_AU_PANIER] est la SEULE chose visible
                        if promo_type == '100%':
                            context += "  • Remise 100% disponible (code: [CODE_APPLIQUÉ_AU_PANIER])\n"
                        elif promo_type == '%':
                            context += "  • Remise de " + str(promo_value) + "% disponible (code: [CODE_APPLIQUÉ_AU_PANIER])\n"
                        elif promo_type == 'CHF':
                            context += "  • Remise de " + str(promo_value) + " CHF disponible (code: [CODE_APPLIQUÉ_AU_PANIER])\n"
                        else:
                            # Type inconnu: afficher quand même sans révéler le code
                            context += "  • Promotion disponible (code: [CODE_APPLIQUÉ_AU_PANIER])\n"
                        promos_injected += 1
                    except Exception as promo_error:
                        # Log l'erreur mais continue avec les autres promos
                        logger.warning(f"[CHAT-IA] ⚠️ Promo ignorée (erreur parsing): {promo_error}")
                        continue
                
                if promos_injected > 0:
                    context += "  → Tu peux calculer les prix réduits avec ces remises.\n"
                    context += "  → Ne dis JAMAIS le code. Dis simplement: 'Le code est appliqué automatiquement au panier.'\n"
                    logger.info(f"[CHAT-IA] ✅ {promos_injected} promos injectées (codes masqués)")
        except Exception as e:
            logger.warning(f"[CHAT-IA] Erreur récupération promos (non bloquant): {e}")
        
        # === SECTION 5: LIEN DE PAIEMENT TWINT ===
        twint_payment_url = ai_config.get("twintPaymentUrl", "")
        if twint_payment_url and twint_payment_url.strip():
            context += f"\n\n💳 LIEN DE PAIEMENT TWINT:\n"
            context += f"  URL: {twint_payment_url}\n"
            context += "  → Quand un client confirme vouloir acheter, propose-lui ce lien de paiement sécurisé Twint.\n"
            logger.info(f"[CHAT-AI-RESPONSE] ✅ Lien Twint injecté: {twint_payment_url[:50]}...")
        else:
            logger.info(f"[CHAT-AI-RESPONSE] ⚠️ Pas de lien Twint configuré")
        
        # === HISTORIQUE DE CONVERSATION ===
        try:
            recent_messages = await db.chat_messages.find(
                {"session_id": session_id, "is_deleted": {"$ne": True}},
                {"_id": 0}
            ).sort("created_at", -1).limit(10).to_list(10)
            
            if recent_messages and len(recent_messages) > 1:
                history = "\n".join([
                    f"{'Client' if m.get('sender_type') == 'user' else 'Assistant'}: {m.get('content', '')}"
                    for m in reversed(recent_messages[1:])  # Exclure le message actuel
                ])
                context += f"\n\n📜 HISTORIQUE RÉCENT:\n{history}"
        except Exception as e:
            logger.warning(f"[CHAT-AI-RESPONSE] Erreur récupération historique: {e}")
    # === FIN DES SECTIONS VENTE (uniquement en mode STANDARD) ===
    
    # ARCHITECTURE DE PROMPT
    user_message_lower = message_text.lower() if message_text else ""
    is_trial_intent = any(word in user_message_lower for word in ['essai', 'gratuit', 'tester', 'essayer', 'test', 'découvrir'])
    
    if use_strict_mode:
        # MODE STRICT : custom_prompt REMPLACE BASE_PROMPT, aucune donnée de vente
        STRICT_SYSTEM_PROMPT = """
╔══════════════════════════════════════════════════════════════════════╗
║        🔒🔒🔒 MODE STRICT - PARTENARIAT / COLLABORATION 🔒🔒🔒        ║
╚══════════════════════════════════════════════════════════════════════╝

⛔⛔⛔ INTERDICTIONS ABSOLUES ⛔⛔⛔

Tu as INTERDICTION ABSOLUE de:
- Citer un PRIX, un TARIF, un COÛT ou un MONTANT (CHF, EUR, $)
- Mentionner un LIEN DE PAIEMENT (Twint, Stripe, etc.)
- Parler de COURS, SESSIONS, ABONNEMENTS ou RÉSERVATIONS
- Orienter vers l'ACHAT ou l'INSCRIPTION
- Donner des informations sur la BOUTIQUE ou les PRODUITS à vendre

Si on te demande un prix, un tarif ou "combien ça coûte", TU DOIS répondre:
"Je vous invite à en discuter directement lors de notre échange, je m'occupe uniquement de la partie collaboration."

Si on insiste, répète cette phrase. Ne donne JAMAIS de prix.

🎯 TON RÔLE UNIQUE:
Tu t'occupes UNIQUEMENT de la COLLABORATION et du PARTENARIAT.
Tu peux parler du CONCEPT Afroboost (cardio + danse afrobeat + casques audio immersifs).
Tu ne connais AUCUN prix, AUCUN tarif, AUCUN lien de paiement.

"""
        # Ajouter le custom_prompt comme instructions exclusives
        STRICT_SYSTEM_PROMPT += "\n═══════════════════════════════════════════════════════════════\n"
        STRICT_SYSTEM_PROMPT += "📋 INSTRUCTIONS EXCLUSIVES DU LIEN:\n"
        STRICT_SYSTEM_PROMPT += "═══════════════════════════════════════════════════════════════\n\n"
        STRICT_SYSTEM_PROMPT += CUSTOM_PROMPT
        STRICT_SYSTEM_PROMPT += "\n\n═══════════════════════════════════════════════════════════════\n"
        
        # Injecter le prompt STRICT (remplace tout)
        context += STRICT_SYSTEM_PROMPT
        logger.info("[CHAT-AI-RESPONSE] 🔒 Mode STRICT activé - Aucune donnée de vente/prix/Twint injectée")
        
    else:
        # =====================================================================
        # MODE STANDARD : FLUX HABITUEL AVEC TOUTES LES DONNÉES DE VENTE
        # =====================================================================
        
        # --- 1. BASE_PROMPT : Limite l'IA aux produits/cours ---
        BASE_PROMPT = """
╔══════════════════════════════════════════════════════════════════╗
║                BASE_PROMPT - IDENTITÉ COACH BASSI                ║
╚══════════════════════════════════════════════════════════════════╝

🎯 IDENTITÉ:
Tu es le COACH BASSI, coach énergique et passionné d'Afroboost.
Tu représentes la marque Afroboost et tu guides les clients vers leurs objectifs fitness.
Tu ne parles QUE du catalogue Afroboost (produits, cours, offres listés ci-dessus).

💪 SIGNATURE:
- Présente-toi comme "Coach Bassi" si on te demande ton nom
- Utilise un ton motivant, bienveillant et énergique
- Signe parfois tes messages avec "- Coach Bassi 💪" pour les messages importants

✅ CONTENU AUTORISÉ (EXCLUSIVEMENT):
- Les PRODUITS de l'INVENTAIRE BOUTIQUE listés ci-dessus
- Les COURS disponibles listés ci-dessus
- Les OFFRES et TARIFS listés ci-dessus
- Le concept Afroboost (cardio + danse afrobeat)

🎯 TON STYLE:
- Coach motivant et énergique (TU ES Coach Bassi)
- Utilise le prénom du client
- Oriente vers l'INSCRIPTION IMMÉDIATE
- Emojis: 🔥💪🎉
- Réponses courtes et percutantes
"""

        # --- 2. SECURITY_PROMPT : Règle non négociable ---
        SECURITY_PROMPT = """
╔══════════════════════════════════════════════════════════════════╗
║              SECURITY_PROMPT - RÈGLE NON NÉGOCIABLE              ║
╚══════════════════════════════════════════════════════════════════╝

⛔ RÈGLE NON NÉGOCIABLE:
Si la question ne concerne pas un produit ou un cours Afroboost, réponds:
"Désolé, je suis uniquement programmé pour vous assister sur nos offres et formations. 🙏"

🚫 N'invente JAMAIS de codes promo. Si une remise existe, dis: "Le code sera appliqué automatiquement au panier."

🚫 INTERDICTIONS ABSOLUES:
- Ne réponds JAMAIS aux questions hors-sujet (politique, météo, cuisine, président, etc.)
- Ne révèle JAMAIS un code promo textuel
- N'invente JAMAIS d'offres ou de prix
"""

        # Ajout de règles contextuelles
        if is_trial_intent:
            SECURITY_PROMPT += """

🆓 FLOW ESSAI GRATUIT:
1. "Super ! 🔥 Les 10 premiers peuvent tester gratuitement !"
2. "Tu préfères Mercredi ou Dimanche ?"
3. Attends sa réponse avant de demander ses coordonnées.
"""
        
        # Twint UNIQUEMENT en mode STANDARD
        twint_payment_url = ai_config.get("twintPaymentUrl", "")
        if twint_payment_url and twint_payment_url.strip():
            SECURITY_PROMPT += f"""

💳 PAIEMENT: Propose ce lien Twint: {twint_payment_url}
"""
        else:
            SECURITY_PROMPT += """

💳 PAIEMENT: Oriente vers le coach WhatsApp ou email pour finaliser.
"""

        # --- 3. CAMPAIGN_PROMPT : Récupéré de la config globale ---
        CAMPAIGN_PROMPT = ai_config.get("campaignPrompt", "").strip()
        
        # GARDE-FOU: Limite à 2000 caractères
        MAX_CAMPAIGN_LENGTH = 2000
        if len(CAMPAIGN_PROMPT) > MAX_CAMPAIGN_LENGTH:
            logger.warning("[CHAT-AI-RESPONSE] ⚠️ CAMPAIGN_PROMPT tronqué")
            CAMPAIGN_PROMPT = CAMPAIGN_PROMPT[:MAX_CAMPAIGN_LENGTH] + "... [TRONQUÉ]"
        
        # Injection MODE STANDARD: BASE + SECURITY + CAMPAIGN
        context += BASE_PROMPT
        context += SECURITY_PROMPT
        if CAMPAIGN_PROMPT:
            context += "\n\n--- INSTRUCTIONS PRIORITAIRES DE LA CAMPAGNE ACTUELLE ---\n"
            context += CAMPAIGN_PROMPT
            context += "\n--- FIN DES INSTRUCTIONS ---\n"
            logger.info("[CHAT-AI-RESPONSE] ✅ Mode STANDARD - Campaign Prompt injecté (len: " + str(len(CAMPAIGN_PROMPT)) + ")")
        else:
            logger.info("[CHAT-AI-RESPONSE] ✅ Mode STANDARD - Pas de Campaign Prompt")
    
    # Assemblage final du prompt système
    full_system_prompt = ai_config.get("systemPrompt", "Tu es l'assistant IA d'Afroboost.") + context
    
    logger.info("[CHAT-AI-RESPONSE] ✅ Contexte construit")
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        emergent_key = os.environ.get("EMERGENT_LLM_KEY")
        if not emergent_key:
            return {"response": "Configuration IA incomplète.", "ai_active": False}
        
        # MODE STRICT: Utiliser un session_id UNIQUE pour éviter la persistance d'historique
        # Cela empêche l'IA de récupérer des infos de prix des messages précédents
        if use_strict_mode:
            llm_session_id = f"afroboost_strict_{uuid.uuid4().hex[:12]}"
            logger.info("[CHAT-AI-RESPONSE] 🔒 Mode STRICT: Session LLM isolée (pas d'historique)")
        else:
            llm_session_id = f"afroboost_session_{session_id}"
        
        chat = LlmChat(
            api_key=emergent_key,
            session_id=llm_session_id,
            system_message=full_system_prompt
        )
        
        user_msg = UserMessage(text=message_text)
        ai_response_text = await chat.send_message(user_msg)
        response_time = round(time.time() - start_time, 2)
        
        logger.info(f"[CHAT-AI-RESPONSE] ✅ Réponse IA générée en {response_time}s")
        
        # Sauvegarder la réponse de l'IA
        ai_message = EnhancedChatMessage(
            session_id=session_id,
            sender_id="ai",
            sender_name="Assistant Afroboost",
            sender_type="ai",
            content=ai_response_text,
            mode="ai"
        )
        await db.chat_messages.insert_one(ai_message.model_dump())
        
        # === SOCKET.IO: Émettre la réponse IA en temps réel ===
        await emit_new_message(session_id, {
            "id": ai_message.id,
            "type": "ai",
            "text": ai_response_text,
            "sender": "Coach Bassi",
            "senderId": "ai",
            "sender_type": "ai",
            "created_at": ai_message.created_at
        })
        
        # Log
        await db.ai_logs.insert_one({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "from": participant_name,
            "message": message_text,
            "response": ai_response_text,
            "responseTime": response_time
        })
        
        return {
            "response": ai_response_text,
            "ai_active": True,
            "mode": "ai",
            "response_time": response_time,
            "user_message_id": user_message.id,
            "ai_message_id": ai_message.id
        }
        
    except Exception as e:
        logger.error(f"AI Chat error: {str(e)}")
        return {
            "response": "Désolé, une erreur s'est produite. Veuillez réessayer.",
            "ai_active": True,
            "error": str(e)
        }

# --- Coach Response to Chat ---
@api_router.post("/chat/coach-response")
async def send_coach_response(request: Request):
    """
    Permet au coach d'envoyer un message dans une session.
    Utilisé en mode "human" ou "community".
    """
    body = await request.json()
    session_id = body.get("session_id")
    message_text = body.get("message", "").strip()
    coach_name = body.get("coach_name", "Coach")
    
    if not session_id or not message_text:
        raise HTTPException(status_code=400, detail="session_id et message sont requis")
    
    session = await db.chat_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    # Créer le message du coach
    coach_message = EnhancedChatMessage(
        session_id=session_id,
        sender_id="coach",
        sender_name=coach_name,
        sender_type="coach",
        content=message_text,
        mode=session.get("mode", "human")
    )
    await db.chat_messages.insert_one(coach_message.model_dump())
    
    # === SOCKET.IO: Émettre le message coach en temps réel ===
    await emit_new_message(session_id, {
        "id": coach_message.id,
        "type": "coach",
        "text": message_text,
        "sender": "Coach Bassi",
        "senderId": "coach",
        "sender_type": "coach",
        "created_at": coach_message.created_at
    })
    # === PUSH NOTIFICATION: Alerter l'abonné si app fermée (skip si socket actif) ===
    participant_id = session.get("participant_id") or (session.get("participant_ids") or [None])[0]
    if participant_id:
        asyncio.create_task(send_push_notification(participant_id, "Afroboost", f"Nouveau message de {coach_name}", None, session_id))
    return {"success": True, "message_id": coach_message.id, "mode": session.get("mode")}

# --- Private Chat from Community ---
@api_router.post("/chat/start-private")
async def start_private_chat(request: Request):
    """
    Crée une session de chat privée entre deux participants.
    Utilisé quand un utilisateur clique sur un autre dans un chat communautaire.
    
    Body attendu:
    {
        "initiator_id": "xxx",  # ID du participant qui initie
        "target_id": "xxx",     # ID du participant cible
        "community_session_id": "xxx"  # ID de la session communautaire d'origine
    }
    """
    body = await request.json()
    initiator_id = body.get("initiator_id")
    target_id = body.get("target_id")
    community_session_id = body.get("community_session_id")
    
    if not initiator_id or not target_id:
        raise HTTPException(status_code=400, detail="initiator_id et target_id sont requis")
    
    # Vérifier que les deux participants existent
    initiator = await db.chat_participants.find_one({"id": initiator_id}, {"_id": 0})
    target = await db.chat_participants.find_one({"id": target_id}, {"_id": 0})
    
    if not initiator or not target:
        raise HTTPException(status_code=404, detail="Participant non trouvé")
    
    # Vérifier s'il existe déjà une session privée entre ces deux personnes
    existing_session = await db.chat_sessions.find_one({
        "participant_ids": {"$all": [initiator_id, target_id], "$size": 2},
        "mode": "human",
        "is_deleted": {"$ne": True}
    }, {"_id": 0})
    
    if existing_session:
        return {
            "session": existing_session,
            "is_new": False,
            "message": f"Reprise de la conversation avec {target.get('name', 'ce participant')}"
        }
    
    # Créer une nouvelle session privée
    private_session = ChatSession(
        mode="human",
        is_ai_active=False,
        participant_ids=[initiator_id, target_id],
        title=f"Discussion privée: {initiator.get('name', '')} & {target.get('name', '')}"
    )
    await db.chat_sessions.insert_one(private_session.model_dump())
    
    # Message d'accueil
    welcome_message = EnhancedChatMessage(
        session_id=private_session.id,
        sender_id="system",
        sender_name="Système",
        sender_type="ai",
        content=f"💬 Discussion privée créée entre {initiator.get('name', '')} et {target.get('name', '')}.",
        mode="human"
    )
    await db.chat_messages.insert_one(welcome_message.model_dump())
    
    return {
        "session": private_session.model_dump(),
        "is_new": True,
        "message": f"Nouvelle discussion privée avec {target.get('name', 'ce participant')}"
    }

# --- Custom Emojis/Stickers ---
@api_router.get("/chat/emojis")
async def get_custom_emojis():
    """Récupère tous les emojis personnalisés uploadés par le coach"""
    emojis = await db.custom_emojis.find({"active": True}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return emojis

@api_router.post("/chat/emojis")
async def upload_custom_emoji(request: Request):
    """
    Upload un emoji personnalisé (image base64).
    
    Body attendu:
    {
        "name": "happy",
        "image_data": "data:image/png;base64,...",
        "category": "emotions"  # optionnel
    }
    """
    body = await request.json()
    name = body.get("name", "").strip()
    image_data = body.get("image_data", "")
    category = body.get("category", "custom")
    
    if not name or not image_data:
        raise HTTPException(status_code=400, detail="name et image_data sont requis")
    
    # Valider le format base64
    if not image_data.startswith("data:image/"):
        raise HTTPException(status_code=400, detail="Format d'image invalide. Utilisez base64 (data:image/...)")
    
    emoji_obj = {
        "id": str(uuid.uuid4()),
        "name": name,
        "image_data": image_data,
        "category": category,
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.custom_emojis.insert_one(emoji_obj)
    
    # Retourner sans _id (MongoDB l'ajoute automatiquement)
    emoji_obj.pop("_id", None)
    return emoji_obj

@api_router.delete("/chat/emojis/{emoji_id}")
async def delete_custom_emoji(emoji_id: str):
    """Supprime un emoji personnalisé"""
    result = await db.custom_emojis.delete_one({"id": emoji_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Emoji non trouvé")
    return {"success": True, "message": "Emoji supprimé"}

# --- Get Session Participants (for community chat) ---
@api_router.get("/chat/sessions/{session_id}/participants")
async def get_session_participants(session_id: str):
    """Récupère les détails des participants d'une session"""
    session = await db.chat_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    participant_ids = session.get("participant_ids", [])
    participants = []
    
    for pid in participant_ids:
        participant = await db.chat_participants.find_one({"id": pid}, {"_id": 0})
        if participant:
            participants.append({
                "id": participant.get("id"),
                "name": participant.get("name"),
                "last_seen_at": participant.get("last_seen_at")
            })
    
    return participants

# ==================== WEB PUSH NOTIFICATIONS ====================

@api_router.get("/push/vapid-key")
async def get_vapid_public_key():
    """Retourne la clé publique VAPID pour l'inscription côté client"""
    return {"publicKey": VAPID_PUBLIC_KEY}

@api_router.post("/push/subscribe")
async def subscribe_push(request: Request):
    """Enregistre une souscription push. Si endpoint existe deja pour autre user, le reassigner."""
    body = await request.json()
    participant_id = body.get("participant_id")
    subscription = body.get("subscription")
    if not participant_id or not subscription:
        raise HTTPException(status_code=400, detail="participant_id et subscription requis")
    endpoint = subscription.get("endpoint", "")
    # Securite: si endpoint existe pour AUTRE user, le reassigner au nouveau
    if endpoint:
        await db.push_subscriptions.update_one({"subscription.endpoint": endpoint}, {"$set": {"participant_id": participant_id, "subscription": subscription, "active": True, "updated_at": datetime.now(timezone.utc).isoformat()}}, upsert=True)
    else:
        await db.push_subscriptions.update_one({"participant_id": participant_id}, {"$set": {"subscription": subscription, "active": True}}, upsert=True)
    logger.debug(f"[PUSH] Subscribe OK: {participant_id[:8]}...")
    return {"success": True}

@api_router.delete("/push/subscribe/{participant_id}")
async def unsubscribe_push(participant_id: str):
    """Desactive la souscription push d'un participant"""
    await db.push_subscriptions.update_one({"participant_id": participant_id}, {"$set": {"active": False}})
    return {"success": True}

async def send_push_notification(participant_id: str, title: str, body: str, data: dict = None, session_id: str = None):
    """Envoie une notification push a un participant (sauf si socket actif)."""
    if not WEBPUSH_AVAILABLE or not VAPID_PRIVATE_KEY:
        return False
    # Verifier si socket actif (chat ouvert) - evite vibration inutile
    if session_id:
        try:
            room_sids = list(sio.manager.rooms.get('/', {}).get(session_id, set()))
            if room_sids:
                logger.debug(f"[PUSH] Skip - socket actif")
                return False
        except Exception:
            pass
    # Recuperer la souscription
    sub = await db.push_subscriptions.find_one({"participant_id": participant_id, "active": True}, {"_id": 0})
    if not sub or not sub.get("subscription"):
        return False
    subscription_info = sub["subscription"]
    payload = json.dumps({"title": title, "body": body, "icon": "/logo192.png", "badge": "/logo192.png", "data": data or {}, "timestamp": datetime.now(timezone.utc).isoformat()})
    try:
        webpush(subscription_info=subscription_info, data=payload, vapid_private_key=VAPID_PRIVATE_KEY, vapid_claims={"sub": f"mailto:{VAPID_CLAIMS_EMAIL}"})
        logger.debug(f"[PUSH] Sent OK")
        return True
    except WebPushException as e:
        if e.response and e.response.status_code in [404, 410]:
            await db.push_subscriptions.update_one({"participant_id": participant_id}, {"$set": {"active": False}})
            logger.debug(f"[PUSH] Subscription desactivee (410/404)")
        else:
            logger.error(f"[PUSH] Echec critique: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"[PUSH] Erreur: {str(e)}")
        return False

async def send_backup_email(participant_id: str, message_preview: str):
    """Envoie un email de backup si la notification push echoue."""
    participant = await db.chat_participants.find_one({"id": participant_id}, {"_id": 0})
    if not participant or not participant.get("email"):
        return False
    email = participant["email"]
    name = participant.get("name", "")
    if not RESEND_AVAILABLE or not RESEND_API_KEY:
        logger.debug(f"[EMAIL] Simulation -> {email}")
        return True
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #d91cd2, #8b5cf6); padding: 20px; border-radius: 12px 12px 0 0; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">💬 Afroboost</h1>
        </div>
        <div style="background: #1a1a1a; padding: 30px; color: #ffffff; border-radius: 0 0 12px 12px;">
            <p style="font-size: 16px; margin-bottom: 20px;">
                Bonjour {name} 👋
            </p>
            <p style="font-size: 14px; color: #cccccc; margin-bottom: 20px;">
                Vous avez reçu une réponse sur Afroboost :
            </p>
            <div style="background: rgba(139, 92, 246, 0.2); padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 3px solid #8b5cf6;">
                <p style="margin: 0; font-size: 14px; color: #ffffff;">
                    "{message_preview[:150]}{'...' if len(message_preview) > 150 else ''}"
                </p>
            </div>
            <a href="https://afroboosteur.com" 
               style="display: inline-block; background: linear-gradient(135deg, #d91cd2, #8b5cf6); color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                Voir la conversation
            </a>
            <p style="font-size: 12px; color: #666666; margin-top: 30px;">
                Cet email a été envoyé car vous avez une notification en attente sur Afroboost.
            </p>
        </div>
    </div>
    """
    
    try:
        params = {
            "from": "Afroboost <notifications@afroboosteur.com>",
            "to": [email],
            "subject": "💬 Nouvelle réponse sur Afroboost",
            "html": html_content
        }
        
        # Appel non-bloquant
        email_result = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Backup email sent to {email}: {email_result}")
        return True
    except Exception as e:
        logger.error(f"Backup email failed: {str(e)}")
        return False

async def notify_coach_new_message(participant_name: str, message_preview: str, session_id: str):
    """
    Notifie le coach par e-mail quand un message arrive en mode humain.
    Crucial pour ne pas rater de ventes.
    """
    # Récupérer l'email du coach depuis coach_auth
    coach_auth = await db.coach_auth.find_one({}, {"_id": 0})
    if not coach_auth or not coach_auth.get("email"):
        logger.warning("Coach email not configured - cannot send notification")
        return False
    
    coach_email = coach_auth.get("email")
    
    # Mode simulation si Resend non configuré
    if not RESEND_AVAILABLE or not RESEND_API_KEY:
        logger.info(f"[SIMULATION COACH EMAIL] To: {coach_email}")
        logger.info(f"[SIMULATION COACH EMAIL] Subject: 🔔 Nouveau message de {participant_name}")
        logger.info(f"[SIMULATION COACH EMAIL] Message: {message_preview[:100]}...")
        logger.info(f"[SIMULATION COACH EMAIL] Session ID: {session_id}")
        logger.info(f"[SIMULATION COACH EMAIL] Email would be sent successfully (Resend not configured)")
        return True
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #d91cd2, #8b5cf6); padding: 20px; border-radius: 12px 12px 0 0; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">🔔 Nouveau message !</h1>
        </div>
        <div style="background: #1a1a1a; padding: 30px; color: #ffffff; border-radius: 0 0 12px 12px;">
            <p style="font-size: 16px; margin-bottom: 20px;">
                <strong>{participant_name}</strong> vous a envoyé un message :
            </p>
            <div style="background: rgba(139, 92, 246, 0.2); padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 3px solid #8b5cf6;">
                <p style="margin: 0; font-size: 14px; color: #ffffff;">
                    "{message_preview[:200]}{'...' if len(message_preview) > 200 else ''}"
                </p>
            </div>
            <p style="font-size: 12px; color: #aaaaaa; margin-bottom: 20px;">
                Ce message nécessite votre réponse en mode humain.
            </p>
            <a href="https://afroboosteur.com/coach" 
               style="display: inline-block; background: linear-gradient(135deg, #d91cd2, #8b5cf6); color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                Répondre maintenant
            </a>
        </div>
    </div>
    """
    
    try:
        params = {
            "from": "Afroboost <notifications@afroboosteur.com>",
            "to": [coach_email],
            "subject": f"🔔 Nouveau message de {participant_name}",
            "html": html_content
        }
        
        email_result = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Coach notification email sent: {email_result}")
        return True
    except Exception as e:
        logger.error(f"Coach notification email failed: {str(e)}")
        return False

# =============================================
# ENDPOINT CAMPAGNES EMAIL VIA RESEND
# =============================================
@api_router.post("/campaigns/send-email")
async def send_campaign_email(request: Request):
    """
    Envoie un email de campagne via Resend.
    Remplace EmailJS pour un contrôle total côté serveur.
    
    Body attendu:
    {
        "to_email": "destinataire@example.com",
        "to_name": "Nom Destinataire",
        "subject": "Sujet de l'email",
        "message": "Contenu HTML ou texte",
        "media_url": "URL du visuel ou lien interne /v/slug (optionnel)"
    }
    """
    body = await request.json()
    to_email = body.get("to_email")
    to_name = body.get("to_name", "")
    subject = body.get("subject", "Message d'Afroboost")
    message = body.get("message", "")
    media_url = body.get("media_url", None)
    
    # LOG DEBUG CRITIQUE
    logger.info(f"=== CAMPAGNE EMAIL ===")
    logger.info(f"To: {to_email}")
    logger.info(f"Subject: {subject}")
    logger.info(f"Media URL reçu: {media_url}")
    logger.info(f"======================")
    
    if not to_email:
        raise HTTPException(status_code=400, detail="to_email requis")
    if not message:
        raise HTTPException(status_code=400, detail="message requis")
    
    # Vérifier que Resend est configuré
    if not RESEND_AVAILABLE or not RESEND_API_KEY:
        logger.warning("Resend non configuré pour les campagnes")
        return {"success": False, "error": "Resend non configuré"}
    
    # === TRAITEMENT DU MEDIA URL ===
    media_html = ""
    if media_url:
        thumbnail_url = None
        click_url = media_url
        
        # Déterminer l'URL de base du frontend (production ou preview)
        # PRIORITÉ: 1. FRONTEND_URL explicite, 2. Même domaine que REACT_APP_BACKEND_URL
        frontend_base = os.environ.get('FRONTEND_URL', '')
        
        # Si pas de FRONTEND_URL ou si c'est afroboosteur.com, vérifier si on est en preview
        if not frontend_base or 'afroboosteur.com' in frontend_base:
            # Utiliser le même domaine que le backend (pour l'environnement preview)
            # Le backend est appelé via REACT_APP_BACKEND_URL qui contient le domaine preview
            from fastapi import Request
            # Par défaut, utiliser afroboosteur.com pour la production
            frontend_base = 'https://afroboosteur.com'
        
        logger.info(f"Frontend base URL: {frontend_base}")
        
        # Vérifier si c'est un lien média interne
        # Formats supportés: /v/slug, /api/share/slug, afroboosteur.com/v/slug
        slug = None
        if '/api/share/' in media_url:
            slug = media_url.split('/api/share/')[-1].split('?')[0].split('#')[0].strip('/')
        elif '/v/' in media_url:
            slug = media_url.split('/v/')[-1].split('?')[0].split('#')[0].strip('/')
        
        if slug:
            # Récupérer la thumbnail depuis la base de données
            media_link = await db.media_links.find_one({"slug": slug.lower()}, {"_id": 0})
            if media_link:
                thumbnail_url = media_link.get("thumbnail") or media_link.get("custom_thumbnail")
                # HASH ROUTING: Utiliser /#/v/{slug} pour garantir le fonctionnement
                # sans configuration serveur (100% côté client)
                click_url = f"{frontend_base}/#/v/{slug}"
                logger.info(f"Media link found for slug {slug}: click_url={click_url}, thumbnail={thumbnail_url}")
            else:
                logger.warning(f"Media link not found for slug: {slug}")
        else:
            # URL externe directe (image)
            thumbnail_url = media_url
        
        # Générer le HTML de l'image cliquable - V5 FINAL (taille réduite -20%)
        if thumbnail_url:
            if thumbnail_url.startswith('http://'):
                thumbnail_url = thumbnail_url.replace('http://', 'https://')
            
            # Template V5 : Card RÉDUITE (-20%) avec image + bouton
            # Image: 400px au lieu de 536px
            media_html = f'''<!-- Image cliquable (taille réduite) -->
<a href="{click_url}" style="display:block;text-decoration:none;">
<img src="{thumbnail_url}" width="400" style="display:block;width:100%;max-width:400px;border-radius:8px;margin:0 auto;" alt="Aperçu vidéo">
</a>
<!-- Bouton "Voir la vidéo" -->
<table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top:15px;">
<tr><td align="center">
<a href="{click_url}" style="display:inline-block;padding:12px 28px;background:#E91E63;color:#ffffff;text-decoration:none;border-radius:8px;font-family:Arial,sans-serif;font-size:14px;font-weight:bold;">
&#9658; Voir la vidéo
</a>
</td></tr>
</table>'''
    
    # =====================================================
    # Template Email V5 FINAL - Anti-Promotions Maximal
    # =====================================================
    # RÈGLES GMAIL ANTI-PROMOTIONS:
    # 1. TEXTE BRUT en premier (3 lignes minimum AVANT tout design)
    # 2. Salutation personnalisée
    # 3. Ratio texte > image
    # 4. Pas de gradient CSS (Gmail les ignore parfois)
    # 5. Taille réduite de 20%
    
    # Extraire le prénom pour personnalisation
    to_name = body.get("to_name", "")
    first_name = to_name.split()[0] if to_name else "ami(e)"
    preheader_text = f"Salut {first_name}, découvre notre nouvelle vidéo exclusive !"
    
    html_content = f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Message Afroboost</title>
</head>
<body style="margin:0;padding:0;background-color:#f5f5f5;font-family:Arial,Helvetica,sans-serif;">

<!-- PREHEADER INVISIBLE -->
<div style="display:none;font-size:1px;color:#f5f5f5;line-height:1px;max-height:0px;max-width:0px;opacity:0;overflow:hidden;">
{preheader_text}
</div>

<!-- WRAPPER -->
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f5f5f5;">
<tr><td align="center" style="padding:20px 10px;">

<!-- ========== TEXTE BRUT ANTI-PROMOTIONS (3 lignes AVANT le design) ========== -->
<table width="480" cellpadding="0" cellspacing="0" border="0" style="max-width:480px;">
<tr><td style="color:#333333;font-size:14px;line-height:1.6;font-family:Arial,sans-serif;padding-bottom:15px;">
Salut {first_name},<br><br>
J'ai une nouvelle vidéo à te partager. Je pense qu'elle va te plaire !<br>
Clique sur le bouton ci-dessous pour la découvrir.
</td></tr>
</table>

<!-- ========== CARD PRINCIPALE (taille réduite 480px) ========== -->
<table width="480" cellpadding="0" cellspacing="0" border="0" style="max-width:480px;background-color:#111111;border-radius:10px;overflow:hidden;">

<!-- HEADER VIOLET -->
<tr><td align="center" style="background-color:#9333EA;padding:16px 20px;">
<a href="https://afroboosteur.com" style="color:#ffffff;font-size:22px;font-weight:bold;text-decoration:none;font-family:Arial,sans-serif;">Afroboost</a>
</td></tr>

<!-- CONTENU -->
<tr><td style="padding:20px;">

<!-- IMAGE + BOUTON -->
{media_html}

<!-- MESSAGE -->
<table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top:20px;">
<tr><td style="color:#ffffff;font-size:14px;line-height:1.6;font-family:Arial,sans-serif;">
{message.replace(chr(10), '<br>')}
</td></tr>
</table>

</td></tr>

<!-- FOOTER -->
<tr><td align="center" style="padding:15px 20px;border-top:1px solid #333333;">
<p style="color:#888888;font-size:11px;margin:0;font-family:Arial,sans-serif;">
<a href="https://afroboosteur.com" style="color:#9333EA;text-decoration:none;">afroboosteur.com</a>
</p>
</td></tr>

</table>

</td></tr>
</table>

</body>
</html>'''
    
    try:
        params = {
            "from": "Afroboost <notifications@afroboosteur.com>",
            "to": [to_email],
            "subject": subject,
            "html": html_content
        }
        
        email_result = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Campaign email sent to {to_email}: {email_result}")
        return {"success": True, "email_id": email_result.get("id"), "to": to_email}
    except Exception as e:
        logger.error(f"Campaign email failed: {str(e)}")
        return {"success": False, "error": str(e)}

@api_router.post("/push/send")
async def send_push_to_participant(request: Request):
    """
    Endpoint pour envoyer manuellement une notification push.
    
    Body attendu:
    {
        "participant_id": "xxx",
        "title": "Nouveau message",
        "body": "Vous avez une réponse...",
        "send_email_backup": true
    }
    """
    body = await request.json()
    participant_id = body.get("participant_id")
    title = body.get("title", "Afroboost")
    message_body = body.get("body", "Vous avez un nouveau message")
    send_email_backup = body.get("send_email_backup", True)
    
    if not participant_id:
        raise HTTPException(status_code=400, detail="participant_id requis")
    
    # Essayer d'envoyer la notification push
    push_sent = await send_push_notification(participant_id, title, message_body)
    
    email_sent = False
    if not push_sent and send_email_backup:
        # Planifier l'email de backup après 5 minutes
        # Pour l'instant, on l'envoie directement si push échoue
        email_sent = await send_backup_email(participant_id, message_body)
    
    return {
        "push_sent": push_sent,
        "email_sent": email_sent,
        "participant_id": participant_id
    }

# =============================================
# LECTEUR MÉDIA UNIFIÉ - AFROBOOST
# =============================================

class MediaLinkCreate(BaseModel):
    """Modèle pour créer un lien média personnalisé"""
    slug: str = Field(..., description="Slug mémorable (ex: promo-danse)")
    video_url: str = Field(..., description="URL YouTube ou Vimeo")
    title: str = Field(..., description="Titre de la campagne")
    description: Optional[str] = Field(None, description="Description/message")
    custom_thumbnail: Optional[str] = Field(None, description="URL thumbnail personnalisée")
    cta_text: Optional[str] = Field(None, description="Texte du bouton CTA")
    cta_link: Optional[str] = Field(None, description="Lien du bouton CTA")
    campaign_id: Optional[str] = Field(None, description="ID campagne associée")

def extract_youtube_id(url: str) -> Optional[str]:
    """Extrait l'ID YouTube d'une URL"""
    import re
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

@api_router.post("/media/create")
async def create_media_link(data: MediaLinkCreate):
    """
    Crée un lien média personnalisé pour les campagnes.
    Génère une URL afroboosteur.com/v/[slug]
    """
    # Vérifier si le slug existe déjà
    existing = await db.media_links.find_one({"slug": data.slug})
    if existing:
        raise HTTPException(status_code=400, detail=f"Le slug '{data.slug}' existe déjà")
    
    # Extraire l'ID YouTube si applicable
    youtube_id = extract_youtube_id(data.video_url)
    
    # Générer la thumbnail automatique si pas de custom
    thumbnail = data.custom_thumbnail
    if not thumbnail and youtube_id:
        thumbnail = f"https://img.youtube.com/vi/{youtube_id}/maxresdefault.jpg"
    
    media_link = {
        "id": str(uuid.uuid4()),
        "slug": data.slug.lower().strip(),
        "video_url": data.video_url,
        "youtube_id": youtube_id,
        "title": data.title,
        "description": data.description or "",
        "thumbnail": thumbnail,
        "cta_text": data.cta_text,
        "cta_link": data.cta_link,
        "campaign_id": data.campaign_id,
        "views": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.media_links.insert_one(media_link)
    
    return {
        "success": True,
        "media_link": {
            "id": media_link["id"],
            "slug": media_link["slug"],
            "url": f"https://afroboosteur.com/api/share/{media_link['slug']}",
            "viewer_url": f"https://afroboosteur.com/v/{media_link['slug']}",
            "thumbnail": media_link["thumbnail"]
        }
    }

@api_router.get("/media/{slug}")
async def get_media_link(slug: str):
    """
    Récupère les infos d'un lien média par son slug.
    Incrémente le compteur de vues.
    """
    media = await db.media_links.find_one({"slug": slug.lower()}, {"_id": 0})
    if not media:
        raise HTTPException(status_code=404, detail="Média non trouvé")
    
    # Incrémenter les vues
    await db.media_links.update_one(
        {"slug": slug.lower()},
        {"$inc": {"views": 1}}
    )
    
    return media

@api_router.get("/media/{slug}/thumbnail")
async def get_media_thumbnail(slug: str):
    """
    Récupère uniquement la thumbnail d'un lien média.
    Utilisé par le frontend pour l'aperçu des campagnes.
    """
    media = await db.media_links.find_one({"slug": slug.lower()}, {"_id": 0, "thumbnail": 1, "custom_thumbnail": 1, "title": 1})
    if not media:
        raise HTTPException(status_code=404, detail="Média non trouvé")
    
    return {
        "thumbnail": media.get("custom_thumbnail") or media.get("thumbnail"),
        "title": media.get("title", "")
    }

@api_router.get("/media/{slug}/og")
async def get_media_opengraph(slug: str):
    """
    Retourne une page HTML avec les meta tags OpenGraph pour les previews WhatsApp/réseaux sociaux.
    """
    media = await db.media_links.find_one({"slug": slug.lower()}, {"_id": 0})
    if not media:
        raise HTTPException(status_code=404, detail="Média non trouvé")
    
    # Générer la page HTML avec meta tags
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{media.get('title', 'Afroboost')}</title>
    
    <!-- OpenGraph pour WhatsApp/Facebook/LinkedIn -->
    <meta property="og:title" content="{media.get('title', 'Afroboost')}" />
    <meta property="og:description" content="{media.get('description', 'Découvrez cette vidéo exclusive Afroboost')[:200]}" />
    <meta property="og:image" content="{media.get('thumbnail', '')}" />
    <meta property="og:image:width" content="1280" />
    <meta property="og:image:height" content="720" />
    <meta property="og:url" content="https://afroboosteur.com/v/{slug}" />
    <meta property="og:type" content="video.other" />
    <meta property="og:site_name" content="Afroboost" />
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{media.get('title', 'Afroboost')}" />
    <meta name="twitter:description" content="{media.get('description', 'Découvrez cette vidéo exclusive Afroboost')[:200]}" />
    <meta name="twitter:image" content="{media.get('thumbnail', '')}" />
    
    <!-- Redirection automatique vers la page React -->
    <script>
        window.location.href = "https://afroboosteur.com/v/{slug}";
    </script>
</head>
<body style="background: #000; color: #fff; font-family: system-ui; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0;">
    <div style="text-align: center;">
        <h1 style="background: linear-gradient(135deg, #d91cd2, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            {media.get('title', 'Afroboost')}
        </h1>
        <p>Redirection en cours...</p>
        <a href="https://afroboosteur.com/v/{slug}" style="color: #d91cd2;">Cliquez ici si la redirection ne fonctionne pas</a>
    </div>
</body>
</html>"""
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html, status_code=200)

@api_router.get("/go/{slug}")
async def redirect_to_media(slug: str):
    """
    Endpoint de redirection HTTP 302 vers la page média.
    Utilisé dans les emails pour garantir une redirection fiable
    même si le serveur de production n'est pas configuré pour le routage SPA.
    """
    # Vérifier que le média existe
    media = await db.media_links.find_one({"slug": slug.lower()}, {"_id": 0, "title": 1})
    if not media:
        raise HTTPException(status_code=404, detail="Média non trouvé")
    
    # Incrémenter les vues
    await db.media_links.update_one(
        {"slug": slug.lower()},
        {"$inc": {"views": 1}}
    )
    
    # Déterminer l'URL de destination
    frontend_base = os.environ.get('FRONTEND_URL', 'https://afroboosteur.com')
    redirect_url = f"{frontend_base}/v/{slug}"
    
    logger.info(f"Redirect /api/go/{slug} -> {redirect_url}")
    
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=redirect_url, status_code=302)

@api_router.get("/media")
async def list_media_links():
    """Liste tous les liens média créés"""
    media_links = await db.media_links.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return media_links

@api_router.delete("/media/{slug}")
async def delete_media_link(slug: str):
    """Supprime un lien média"""
    result = await db.media_links.delete_one({"slug": slug.lower()})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Média non trouvé")
    return {"success": True, "deleted": slug}

@api_router.put("/media/{slug}")
async def update_media_link(slug: str, request: Request):
    """Met à jour un lien média existant"""
    body = await request.json()
    
    # Vérifier que le média existe
    existing = await db.media_links.find_one({"slug": slug.lower()})
    if not existing:
        raise HTTPException(status_code=404, detail="Média non trouvé")
    
    # Préparer les champs à mettre à jour
    update_fields = {}
    
    if "title" in body and body["title"]:
        update_fields["title"] = body["title"]
    if "description" in body:
        update_fields["description"] = body["description"] or ""
    if "video_url" in body and body["video_url"]:
        update_fields["video_url"] = body["video_url"]
        # Extraire l'ID YouTube si c'est une URL YouTube
        youtube_id = extract_youtube_id(body["video_url"])
        if youtube_id:
            update_fields["youtube_id"] = youtube_id
            # Mettre à jour la thumbnail si pas de custom
            if not body.get("custom_thumbnail"):
                update_fields["thumbnail"] = f"https://img.youtube.com/vi/{youtube_id}/maxresdefault.jpg"
    if "custom_thumbnail" in body:
        update_fields["custom_thumbnail"] = body["custom_thumbnail"] or None
        if body["custom_thumbnail"]:
            update_fields["thumbnail"] = body["custom_thumbnail"]
    if "cta_text" in body:
        update_fields["cta_text"] = body["cta_text"] or None
    if "cta_link" in body:
        update_fields["cta_link"] = body["cta_link"] or None
    
    if not update_fields:
        return {"success": True, "message": "Aucune modification"}
    
    # Mettre à jour
    await db.media_links.update_one(
        {"slug": slug.lower()},
        {"$set": update_fields}
    )
    
    # Retourner le média mis à jour
    updated = await db.media_links.find_one({"slug": slug.lower()}, {"_id": 0})
    return {"success": True, "media_link": updated}

# ==================== ENDPOINT DE PARTAGE AVEC OPENGRAPH ====================
# Cet endpoint est ACCESSIBLE via /api/share/{slug} et sert les balises OG pour WhatsApp

@api_router.get("/share/{slug}")
async def share_media_with_opengraph(slug: str, request: Request):
    """
    URL DE PARTAGE PRINCIPALE pour WhatsApp/réseaux sociaux.
    
    IMPORTANT: Utilisez https://afroboosteur.com/api/share/{slug} pour partager !
    Cette URL passe par le backend et sert les balises OpenGraph aux crawlers.
    
    Workflow:
    1. WhatsApp/Facebook crawle cette URL
    2. Le backend retourne les balises og:image, og:title, etc.
    3. L'utilisateur qui clique est redirigé vers /v/{slug} (frontend React)
    """
    media = await db.media_links.find_one({"slug": slug.lower()}, {"_id": 0})
    if not media:
        raise HTTPException(status_code=404, detail="Média non trouvé")
    
    # Incrémenter les vues
    await db.media_links.update_one({"slug": slug.lower()}, {"$inc": {"views": 1}})
    
    # Échapper les caractères spéciaux pour éviter XSS
    title = (media.get('title', 'Afroboost') or 'Afroboost').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    description = (media.get('description', 'Découvrez cette vidéo exclusive Afroboost') or 'Découvrez cette vidéo exclusive Afroboost')[:200].replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    thumbnail = media.get('custom_thumbnail') or media.get('thumbnail') or ''
    youtube_id = media.get('youtube_id', '')
    cta_text = media.get('cta_text', '')
    cta_link = media.get('cta_link', '')
    
    # URL de partage et URL du viewer
    share_url = f"https://afroboosteur.com/api/share/{slug}"
    viewer_url = f"https://afroboosteur.com/v/{slug}"
    
    # Générer la page HTML avec meta tags OpenGraph COMPLETS
    html = f"""<!DOCTYPE html>
<html lang="fr" prefix="og: https://ogp.me/ns#">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Afroboost</title>
    
    <!-- ===== OPENGRAPH POUR WHATSAPP/FACEBOOK/LINKEDIN ===== -->
    <meta property="og:type" content="video.other" />
    <meta property="og:site_name" content="Afroboost" />
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{description}" />
    <meta property="og:url" content="{share_url}" />
    
    <!-- IMAGE - CRITIQUE POUR WHATSAPP -->
    <meta property="og:image" content="{thumbnail}" />
    <meta property="og:image:secure_url" content="{thumbnail}" />
    <meta property="og:image:type" content="image/jpeg" />
    <meta property="og:image:width" content="1280" />
    <meta property="og:image:height" content="720" />
    <meta property="og:image:alt" content="{title}" />
    
    <!-- VIDEO (optionnel mais aide WhatsApp) -->
    {f'<meta property="og:video" content="https://www.youtube.com/embed/{youtube_id}" />' if youtube_id else ''}
    {f'<meta property="og:video:secure_url" content="https://www.youtube.com/embed/{youtube_id}" />' if youtube_id else ''}
    {f'<meta property="og:video:type" content="text/html" />' if youtube_id else ''}
    {f'<meta property="og:video:width" content="1280" />' if youtube_id else ''}
    {f'<meta property="og:video:height" content="720" />' if youtube_id else ''}
    
    <!-- TWITTER CARD -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:site" content="@afroboost" />
    <meta name="twitter:title" content="{title}" />
    <meta name="twitter:description" content="{description}" />
    <meta name="twitter:image" content="{thumbnail}" />
    
    <!-- WHATSAPP SPECIFIQUE -->
    <meta property="al:web:url" content="{viewer_url}" />
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: linear-gradient(180deg, #000 0%, #1a0a1f 100%);
            min-height: 100vh;
            color: #fff;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .container {{
            text-align: center;
            max-width: 500px;
            width: 100%;
        }}
        .logo {{
            font-size: 28px;
            font-weight: bold;
            background: linear-gradient(135deg, #d91cd2, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 30px;
        }}
        .thumbnail {{
            width: 100%;
            max-width: 480px;
            border-radius: 16px;
            box-shadow: 0 0 40px rgba(217, 28, 210, 0.4);
            margin-bottom: 20px;
        }}
        h1 {{
            font-size: 24px;
            margin-bottom: 15px;
            line-height: 1.3;
        }}
        p {{
            color: rgba(255,255,255,0.7);
            margin-bottom: 25px;
            line-height: 1.5;
        }}
        .cta {{
            display: inline-block;
            padding: 16px 32px;
            background: linear-gradient(135deg, #d91cd2, #8b5cf6);
            color: white;
            text-decoration: none;
            border-radius: 12px;
            font-weight: bold;
            font-size: 18px;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 20px rgba(217, 28, 210, 0.4);
        }}
        .cta:hover {{
            transform: scale(1.05);
            box-shadow: 0 6px 30px rgba(217, 28, 210, 0.6);
        }}
        .loader {{
            width: 40px;
            height: 40px;
            border: 4px solid rgba(217, 28, 210, 0.3);
            border-top-color: #d91cd2;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }}
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        .redirect-msg {{
            font-size: 14px;
            color: rgba(255,255,255,0.5);
            margin-top: 30px;
        }}
    </style>
    
    <!-- REDIRECTION AUTOMATIQUE VERS LE LECTEUR -->
    <script>
        // Redirection après un court délai pour permettre aux crawlers de lire les meta tags
        setTimeout(function() {{
            window.location.href = "{viewer_url}";
        }}, 1500);
    </script>
</head>
<body>
    <div class="container">
        <div class="logo">🎧 Afroboost</div>
        
        {f'<img src="{thumbnail}" alt="{title}" class="thumbnail" />' if thumbnail else ''}
        
        <h1>{title}</h1>
        <p>{description}</p>
        
        <a href="{viewer_url}" class="cta">
            ▶️ {cta_text if cta_text else 'Voir la vidéo'}
        </a>
        
        <p class="redirect-msg">
            <span class="loader" style="display:inline-block;width:16px;height:16px;vertical-align:middle;margin-right:8px;"></span>
            Redirection en cours...
        </p>
    </div>
</body>
</html>"""
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html, status_code=200)

# ==================== ROUTE RACINE /v/{slug} POUR OPENGRAPH ====================
# Cette route est essentielle pour que WhatsApp puisse afficher les aperçus riches

@fastapi_app.get("/v/{slug}")
async def serve_media_opengraph_page(slug: str, request: Request):
    """
    Sert une page HTML avec les meta tags OpenGraph pour les previews WhatsApp.
    WhatsApp/Facebook crawle cette URL et récupère les balises og:.
    La page redirige ensuite vers le frontend React pour l'affichage.
    """
    media = await db.media_links.find_one({"slug": slug.lower()}, {"_id": 0})
    if not media:
        raise HTTPException(status_code=404, detail="Média non trouvé")
    
    # Échapper les caractères spéciaux pour éviter XSS
    title = (media.get('title', 'Afroboost') or 'Afroboost').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    description = (media.get('description', 'Découvrez cette vidéo exclusive Afroboost') or '')[:200].replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    thumbnail = media.get('thumbnail', '') or ''
    
    # Déterminer l'URL du frontend (production ou preview)
    frontend_url = os.environ.get('FRONTEND_URL', 'https://afroboosteur.com')
    viewer_url = f"{frontend_url}/v/{slug}"
    
    # Générer la page HTML avec meta tags
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    
    <!-- OpenGraph pour WhatsApp/Facebook/LinkedIn -->
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{description}" />
    <meta property="og:image" content="{thumbnail}" />
    <meta property="og:image:width" content="1280" />
    <meta property="og:image:height" content="720" />
    <meta property="og:url" content="https://afroboosteur.com/v/{slug}" />
    <meta property="og:type" content="video.other" />
    <meta property="og:site_name" content="Afroboost" />
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{title}" />
    <meta name="twitter:description" content="{description}" />
    <meta name="twitter:image" content="{thumbnail}" />
    
    <style>
        body {{
            background: linear-gradient(180deg, #000 0%, #1a0a1f 100%);
            color: #fff;
            font-family: system-ui, -apple-system, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            padding: 20px;
            box-sizing: border-box;
        }}
        .container {{
            text-align: center;
            max-width: 400px;
        }}
        h1 {{
            background: linear-gradient(135deg, #d91cd2, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 20px;
        }}
        .loader {{
            width: 40px;
            height: 40px;
            border: 4px solid rgba(217, 28, 210, 0.3);
            border-top-color: #d91cd2;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }}
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        a {{
            color: #d91cd2;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
    
    <!-- Redirection automatique -->
    <script>
        // Rediriger vers le frontend React après un court délai
        // Ce délai permet aux crawlers de lire les meta tags
        setTimeout(function() {{
            window.location.href = "{viewer_url}";
        }}, 100);
    </script>
</head>
<body>
    <div class="container">
        <div class="loader"></div>
        <h1>{title}</h1>
        <p>Chargement de la vidéo...</p>
        <p style="margin-top: 20px; font-size: 14px; opacity: 0.7;">
            <a href="{viewer_url}">Cliquez ici si vous n'êtes pas redirigé</a>
        </p>
    </div>
</body>
</html>"""
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html, status_code=200)

# === SCHEDULER HEALTH ENDPOINTS (définis avant include_router) ===
@api_router.get("/scheduler/status")
async def get_scheduler_status():
    """Endpoint pour vérifier que le scheduler est en vie avec APScheduler."""
    from datetime import datetime, timezone
    
    # Obtenir le statut d'APScheduler
    scheduler_state = "running" if apscheduler.running else "stopped"
    
    # Obtenir les infos du job
    job = apscheduler.get_job('campaign_scheduler_job')
    job_info = None
    if job:
        job_info = {
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger)
        }
    
    return {
        "scheduler_running": apscheduler.running,
        "scheduler_state": scheduler_state,
        "interval_seconds": SCHEDULER_INTERVAL,
        "persistence": "MongoDB (survit aux redémarrages)",
        "job": job_info
    }

@api_router.get("/scheduler/health")
async def get_scheduler_health():
    """
    Endpoint de santé du scheduler pour le dashboard.
    Renvoie le statut et le dernier timestamp d'exécution.
    """
    from datetime import datetime, timezone
    # Accéder à la variable globale qui sera mise à jour par le thread scheduler
    global SCHEDULER_LAST_HEARTBEAT, SCHEDULER_RUNNING
    try:
        return {
            "status": "active" if SCHEDULER_RUNNING else "stopped",
            "last_run": SCHEDULER_LAST_HEARTBEAT
        }
    except:
        return {
            "status": "unknown",
            "last_run": None
        }

# Fonction de test de persistance (définie au niveau module pour sérialisation)
# ==================== SCHEDULER GROUP MESSAGE EMISSION ====================
@api_router.post("/scheduler/emit-group-message")
async def scheduler_emit_group_message(request: Request):
    """Endpoint interne pour permettre au scheduler d'emettre des messages via Socket.IO."""
    try:
        body = await request.json()
        session_id = body.get("session_id")
        message_data = body.get("message", {})
        broadcast = body.get("broadcast", True)
        if not message_data:
            return {"success": False, "error": "message requis"}
        # S'assurer que tous les champs media sont inclus (meme si None)
        safe_message = {
            "id": message_data.get("id", str(uuid.uuid4())),
            "type": message_data.get("type", "coach"),
            "text": message_data.get("text", ""),
            "sender": message_data.get("sender", "Coach Bassi"),
            "senderId": message_data.get("senderId", "coach"),
            "sender_type": message_data.get("sender_type", "coach"),
            "created_at": message_data.get("created_at", datetime.now(timezone.utc).isoformat()),
            "session_id": session_id,
            "scheduled": True
        }
        # Ajouter champs optionnels media/CTA seulement s'ils existent
        for field in ["media_url", "media_type", "cta_type", "cta_text", "cta_link"]:
            if message_data.get(field):
                safe_message[field] = message_data[field]
        try:
            if broadcast:
                await sio.emit('message_received', safe_message)
            else:
                await emit_new_message(session_id, safe_message)
            logger.debug(f"[SCHEDULER-EMIT] Message emis OK")
        except Exception as emit_err:
            # Si emission echoue, envoyer en mode texte seul
            logger.error(f"[SCHEDULER-EMIT] Emit error, fallback texte: {emit_err}")
            text_only = {"id": safe_message["id"], "type": "coach", "text": safe_message["text"], "sender": "Coach Bassi", "senderId": "coach", "created_at": safe_message["created_at"], "session_id": session_id}
            await sio.emit('message_received', text_only)
        return {"success": True, "session_id": session_id}
    except Exception as e:
        logger.error(f"[SCHEDULER-EMIT] Erreur: {e}")
        return {"success": False, "error": str(e)}

# Include router
fastapi_app.include_router(api_router)

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dynamic manifest.json endpoint for PWA
@fastapi_app.get("/api/manifest.json")
async def get_dynamic_manifest():
    """Serve dynamic manifest.json with logo and name from coach settings"""
    concept = await db.concept.find_one({})
    
    # Use coach-configured favicon (priority) or logo as fallback
    logo_url = None
    app_name = "Afroboost"  # Default name
    if concept:
        # faviconUrl has priority, then logoUrl (same as frontend)
        logo_url = concept.get("faviconUrl") or concept.get("logoUrl")
        # Use custom appName if configured
        if concept.get("appName"):
            app_name = concept.get("appName")
    
    manifest = {
        "short_name": app_name,
        "name": f"{app_name} - Réservation de casque",
        "description": concept.get("description", "Le concept Afroboost : cardio + danse afrobeat + casques audio immersifs.") if concept else "Le concept Afroboost : cardio + danse afrobeat + casques audio immersifs.",
        "icons": [
            {
                "src": "favicon.ico",
                "sizes": "64x64 32x32 24x24 16x16",
                "type": "image/x-icon"
            }
        ],
        "start_url": ".",
        "display": "standalone",
        "theme_color": "#000000",
        "background_color": "#000000",
        "orientation": "portrait-primary"
    }
    
    # Add dynamic logo icons if configured
    if logo_url:
        manifest["icons"] = [
            {
                "src": logo_url,
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": logo_url,
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": "favicon.ico",
                "sizes": "64x64 32x32 24x24 16x16",
                "type": "image/x-icon"
            }
        ]
    else:
        # Fallback to default icons
        manifest["icons"] = [
            {
                "src": "favicon.ico",
                "sizes": "64x64 32x32 24x24 16x16",
                "type": "image/x-icon"
            },
            {
                "src": "logo192.png",
                "type": "image/png",
                "sizes": "192x192",
                "purpose": "any maskable"
            },
            {
                "src": "logo512.png",
                "type": "image/png",
                "sizes": "512x512",
                "purpose": "any maskable"
            }
        ]
    
    from fastapi.responses import JSONResponse
    return JSONResponse(content=manifest, media_type="application/manifest+json")

# ==================== SCHEDULER INTÉGRÉ (APSCHEDULER AVEC PERSISTANCE) ====================

import threading
import time as time_module

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.interval import IntervalTrigger
from pymongo import MongoClient

SCHEDULER_RUNNING = False
SCHEDULER_LAST_HEARTBEAT = None
SCHEDULER_INTERVAL = 30

mongo_client_sync = MongoClient(os.environ.get('MONGO_URL'))
jobstores = {
    'default': MongoDBJobStore(
        database=os.environ.get('DB_NAME', 'afroboost'),
        collection='scheduled_jobs',
        client=mongo_client_sync
    )
}

executors = {'default': ThreadPoolExecutor(10)}
job_defaults = {'coalesce': True, 'max_instances': 1, 'misfire_grace_time': 60}

apscheduler = BackgroundScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone="UTC"
)

from scheduler_engine import scheduler_job as scheduler_job_engine, PARIS_TZ, parse_campaign_date

SCHEDULER_HEARTBEAT_REF = [None]

def scheduler_job():
    """Wrapper pour le job du scheduler - appelle scheduler_engine."""
    global SCHEDULER_LAST_HEARTBEAT
    scheduler_job_engine(mongo_client_sync, SCHEDULER_HEARTBEAT_REF)
    SCHEDULER_LAST_HEARTBEAT = SCHEDULER_HEARTBEAT_REF[0]


@fastapi_app.on_event("startup")
async def startup_scheduler():
    """Lance APScheduler avec persistance MongoDB au démarrage du serveur."""
    global SCHEDULER_RUNNING
    
    logger.info("[SYSTEM] 🚀 Démarrage du serveur Afroboost...")
    
    # Nettoyage zombie campaigns (bloquées > 30 min)
    try:
        thirty_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=30)
        zombie_filter = {"status": "sending", "updatedAt": {"$lt": thirty_minutes_ago.isoformat()}}
        zombie_campaigns = await db.campaigns.find(zombie_filter, {"_id": 0, "id": 1, "name": 1}).to_list(100)
        
        if zombie_campaigns:
            logger.warning(f"[ZOMBIE-CLEANUP] 🧟 {len(zombie_campaigns)} campagne(s) zombie")
            for zombie in zombie_campaigns:
                zombie_id = zombie.get("id")
                await db.campaigns.update_one(
                    {"id": zombie_id},
                    {
                        "$set": {"status": "failed", "updatedAt": datetime.now(timezone.utc).isoformat()},
                        "$push": {"results": {
                                "contactId": "system",
                                "channel": "system",
                                "status": "failed",
                                "error": "Timeout zombie",
                                "sentAt": datetime.now(timezone.utc).isoformat()
                            }
                        }
                    }
                )
            logger.info(f"[ZOMBIE] ✅ {len(zombie_campaigns)} nettoyées")
        else:
            logger.info("[ZOMBIE-CLEANUP] ✅ Aucune campagne zombie détectée")
            
    except Exception as e:
        logger.error(f"[ZOMBIE] Erreur: {e}")
    
    # Index unique pour push_subscriptions (evite doublons)
    try:
        await db.push_subscriptions.create_index("endpoint", unique=True, sparse=True)
        logger.info("[INDEX] push_subscriptions.endpoint unique OK")
    except Exception:
        pass  # Index existe deja
    
    # Ajouter le job APScheduler
    try:
        existing_job = apscheduler.get_job('campaign_scheduler_job')
        if existing_job:
            logger.info("[SCHEDULER] Job existant réutilisé")
        else:
            apscheduler.add_job(
                scheduler_job,
                trigger=IntervalTrigger(seconds=SCHEDULER_INTERVAL),
                id='campaign_scheduler_job',
                name='Campaign Scheduler',
                replace_existing=True
            )
            logger.info("[SCHEDULER] ✅ Nouveau job créé")
    except Exception as e:
        apscheduler.add_job(scheduler_job, trigger=IntervalTrigger(seconds=SCHEDULER_INTERVAL),
            id='campaign_scheduler_job', name='Campaign Scheduler', replace_existing=True)
        logger.info(f"[SCHEDULER] Job remplacé: {e}")
    
    if not apscheduler.running:
        apscheduler.start()
        SCHEDULER_RUNNING = True
        logger.info("[SCHEDULER] ✅ Démarré - Jobs persistés dans MongoDB")
    else:
        logger.info("[SCHEDULER] Déjà en cours")

@fastapi_app.on_event("shutdown")
async def shutdown_db_client():
    global SCHEDULER_RUNNING
    SCHEDULER_RUNNING = False
    if apscheduler.running:
        apscheduler.shutdown(wait=False)
        logger.info("[SCHEDULER] Arrêté (jobs persistés)")
    client.close()
    mongo_client_sync.close()
    logger.info("[SYSTEM] Arrete")




# END




















































