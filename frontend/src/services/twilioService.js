/**
 * TwilioService.js - Squelette pour l'intégration WhatsApp via Twilio
 * 
 * Ce service sera utilisé pour :
 * - Envoyer des messages WhatsApp aux abonnés
 * - Recevoir des webhooks Twilio pour les réponses
 * - Gérer les templates de messages (HSM)
 * 
 * CONFIGURATION REQUISE (backend/.env) :
 * - TWILIO_ACCOUNT_SID : Identifiant du compte Twilio
 * - TWILIO_AUTH_TOKEN : Token d'authentification
 * - TWILIO_WHATSAPP_NUMBER : Numéro WhatsApp Twilio (format: whatsapp:+14155238886)
 * 
 * ÉTAPES POUR ACTIVER :
 * 1. Créer un compte Twilio (https://www.twilio.com)
 * 2. Activer le Sandbox WhatsApp ou configurer un numéro dédié
 * 3. Configurer les webhooks entrants vers /api/webhooks/twilio
 * 4. Ajouter les credentials dans backend/.env
 * 5. Mettre REACT_APP_TWILIO_ENABLED=true dans frontend/.env
 */

const API = process.env.REACT_APP_BACKEND_URL || '';

/**
 * Vérifie si l'intégration Twilio est activée
 * @returns {boolean}
 */
export const isTwilioEnabled = () => {
  return process.env.REACT_APP_TWILIO_ENABLED === 'true';
};

/**
 * Envoie un message WhatsApp via l'API backend
 * @param {string} to - Numéro de téléphone du destinataire (format international)
 * @param {string} message - Contenu du message
 * @returns {Promise<{success: boolean, sid?: string, error?: string}>}
 */
export const sendWhatsAppMessage = async (to, message) => {
  if (!isTwilioEnabled()) {
    console.warn('[TWILIO] ⚠️ Service désactivé (REACT_APP_TWILIO_ENABLED=false)');
    return { success: false, error: 'Service WhatsApp non configuré' };
  }
  
  try {
    const response = await fetch(`${API}/api/twilio/send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ to, message })
    });
    
    const data = await response.json();
    
    if (data.success) {
      console.log('[TWILIO] ✅ Message envoyé:', data.sid);
      return { success: true, sid: data.sid };
    } else {
      console.error('[TWILIO] ❌ Erreur:', data.error);
      return { success: false, error: data.error };
    }
  } catch (err) {
    console.error('[TWILIO] ❌ Exception:', err.message);
    return { success: false, error: err.message };
  }
};

/**
 * Envoie un message template WhatsApp (HSM)
 * Utilisé pour les notifications proactives (réservations, rappels, etc.)
 * @param {string} to - Numéro de téléphone
 * @param {string} templateName - Nom du template approuvé par WhatsApp
 * @param {object} variables - Variables du template { "1": "valeur1", "2": "valeur2" }
 * @returns {Promise<{success: boolean, sid?: string, error?: string}>}
 */
export const sendWhatsAppTemplate = async (to, templateName, variables = {}) => {
  if (!isTwilioEnabled()) {
    return { success: false, error: 'Service WhatsApp non configuré' };
  }
  
  try {
    const response = await fetch(`${API}/api/twilio/send-template`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ to, templateName, variables })
    });
    
    const data = await response.json();
    return data.success 
      ? { success: true, sid: data.sid }
      : { success: false, error: data.error };
  } catch (err) {
    return { success: false, error: err.message };
  }
};

/**
 * Récupère le statut d'un message WhatsApp
 * @param {string} messageSid - SID du message Twilio
 * @returns {Promise<{status: string, error?: string}>}
 */
export const getMessageStatus = async (messageSid) => {
  if (!isTwilioEnabled()) {
    return { status: 'unknown', error: 'Service non configuré' };
  }
  
  try {
    const response = await fetch(`${API}/api/twilio/status/${messageSid}`);
    const data = await response.json();
    return { status: data.status || 'unknown' };
  } catch (err) {
    return { status: 'error', error: err.message };
  }
};

/**
 * Formate un numéro de téléphone pour Twilio
 * @param {string} phone - Numéro de téléphone (avec ou sans indicatif)
 * @param {string} defaultCountryCode - Code pays par défaut (ex: '+41' pour Suisse)
 * @returns {string} - Numéro formaté pour WhatsApp (whatsapp:+XXXXXXXXXXX)
 */
export const formatWhatsAppNumber = (phone, defaultCountryCode = '+41') => {
  // Nettoyer le numéro
  let cleaned = phone.replace(/[\s\-\.\(\)]/g, '');
  
  // Ajouter le code pays si manquant
  if (!cleaned.startsWith('+')) {
    if (cleaned.startsWith('0')) {
      cleaned = defaultCountryCode + cleaned.substring(1);
    } else {
      cleaned = defaultCountryCode + cleaned;
    }
  }
  
  return `whatsapp:${cleaned}`;
};

// Export par défaut
export default {
  isTwilioEnabled,
  sendWhatsAppMessage,
  sendWhatsAppTemplate,
  getMessageStatus,
  formatWhatsAppNumber
};
