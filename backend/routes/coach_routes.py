# coach_routes.py - Routes coach v9.1.0
# Ce fichier est préparé pour la future extraction des routes coach de server.py

from fastapi import APIRouter, HTTPException, Request
from .shared import is_super_admin, SUPER_ADMIN_EMAIL, DEFAULT_COACH_ID

coach_router = APIRouter(prefix="/coach", tags=["coach"])

# TODO: Migrer progressivement les routes /coach/* depuis server.py
# Endpoints prévus:
# - GET /coach/profile
# - GET /coach/check-credits
# - POST /coach/register
# - POST /coach/deduct-credit
# - POST /coach/add-credits
# - GET /coach/vitrine/{username}
# - POST /coach/stripe-connect/onboard
# - GET /coach/stripe-connect/status
