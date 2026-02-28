# Routes modulaires pour Afroboost v9.1.0
from .coach_routes import coach_router
from .campaign_routes import campaign_router
from .admin_routes import admin_router

__all__ = ['coach_router', 'campaign_router', 'admin_router']
