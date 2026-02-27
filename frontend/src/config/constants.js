// Constants de configuration Afroboost
// Fichier centralisé pour le déploiement Vercel

// Admin & Contact
export const ADMIN_EMAIL = 'contact.artboost@gmail.com';
export const COACH_DEFAULT_EMAIL = 'coach@afroboost.com';
export const COACH_DEFAULT_PASSWORD = 'afroboost123';

// App Info
export const APP_NAME = 'Afroboost';
export const APP_VERSION = '2.0.0';
export const APP_YEAR = '2026';

// Languages
export const DEFAULT_LANGUAGE = 'fr';
export const SUPPORTED_LANGUAGES = ['fr', 'en', 'de'];

// Limits & Defaults
export const MAX_IMAGES_PER_OFFER = 5;
export const MIN_PASSWORD_LENGTH = 6;
export const DEFAULT_QUANTITY = 1;
export const SPLASH_DURATION_MS = 2000;

// LocalStorage Keys
export const STORAGE_KEYS = {
  COACH_AUTH: 'coachAuth',
  USER_LANG: 'af_lang',
  CLIENT_INFO: 'af_client_info',
  RESERVATIONS: 'afroboost_reservations',
  PWA_DISMISSED: 'af_pwa_dismissed'
};

// Default Images (fallbacks)
export const DEFAULT_OFFER_IMAGE = 'https://picsum.photos/seed/default/400/300';
export const DEFAULT_LOGO = '/logo512.png';

// API Endpoints (pour référence)
export const API_ENDPOINTS = {
  COURSES: '/api/courses',
  OFFERS: '/api/offers',
  RESERVATIONS: '/api/reservations',
  USERS: '/api/users',
  PAYMENT_LINKS: '/api/payment-links',
  CONCEPT: '/api/concept',
  DISCOUNT_CODES: '/api/discount-codes',
  COACH_AUTH: '/api/coach-auth'
};
