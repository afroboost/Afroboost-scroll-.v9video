# campaign_routes.py - Routes campagnes v9.1.0
# Ce fichier est préparé pour la future extraction des routes campagnes de server.py

from fastapi import APIRouter, HTTPException, Request
from .shared import is_super_admin

campaign_router = APIRouter(prefix="/campaigns", tags=["campaigns"])

# TODO: Migrer progressivement les routes /campaigns/* depuis server.py
# Endpoints prévus:
# - GET /campaigns
# - GET /campaigns/logs
# - GET /campaigns/{id}
# - POST /campaigns
# - PUT /campaigns/{id}
# - DELETE /campaigns/{id}
# - POST /campaigns/{id}/launch
# - POST /campaigns/send-email
