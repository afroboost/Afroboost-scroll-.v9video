// Configuration globale de l'application Afroboost
// Compatible Vercel / Node.js
// Re-export from constants.js pour compatibilité

export * from './constants';

// Objet de config groupé pour import simple
export const APP_CONFIG = {
  // Admin
  ADMIN_EMAIL: 'contact.artboost@gmail.com',
  COACH_DEFAULT_EMAIL: 'coach@afroboost.com',
  
  // API
  API_URL: process.env.REACT_APP_BACKEND_URL || '',
  
  // App Info
  APP_NAME: 'Afroboost',
  APP_VERSION: '2.0.0',
  
  // Defaults
  DEFAULT_LANGUAGE: 'fr',
  SUPPORTED_LANGUAGES: ['fr', 'en', 'de'],
  
  // Limits
  MAX_IMAGES_PER_OFFER: 5,
  MIN_PASSWORD_LENGTH: 6,
  
  // Storage Keys
  STORAGE_KEYS: {
    COACH_AUTH: 'coachAuth',
    USER_LANG: 'af_lang',
    CLIENT_INFO: 'af_client_info',
    RESERVATIONS: 'afroboost_reservations',
    PWA_DISMISSED: 'af_pwa_dismissed'
  }
};

export default APP_CONFIG;
