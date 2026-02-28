# Routes modulaires pour Afroboost v9.1.0
# Structure préparée pour migration progressive depuis server.py
# Les routes restent dans server.py pour la stabilité

from .shared import (
    SUPER_ADMIN_EMAIL, 
    DEFAULT_COACH_ID, 
    ROLE_SUPER_ADMIN, 
    ROLE_COACH, 
    ROLE_USER,
    is_super_admin, 
    get_coach_filter
)

# Routers vides préparés pour future migration
from .admin_routes import admin_router
from .coach_routes import coach_router
from .campaign_routes import campaign_router

__all__ = [
    'SUPER_ADMIN_EMAIL', 'DEFAULT_COACH_ID', 
    'ROLE_SUPER_ADMIN', 'ROLE_COACH', 'ROLE_USER',
    'is_super_admin', 'get_coach_filter',
    'admin_router', 'coach_router', 'campaign_router'
]
