// messagingGateway.js - Passerelles techniques pour l'envoi de messages
// Ces fonctions sont des canaux de sortie PURS - aucune logique de décision
// L'agent IA reste le déclencheur principal et utilise ces passerelles pour expédier

import emailjs from '@emailjs/browser';

// === CONSTANTES EMAILJS - NE PAS MODIFIER ===
const EMAILJS_SERVICE_ID = "service_8mrmxim";
const EMAILJS_TEMPLATE_ID = "template_3n1u86p";
const EMAILJS_PUBLIC_KEY = "5LfgQSIEQoqq_XSqt";

// === WEBHOOK WHATSAPP (backend Twilio) ===
const WHATSAPP_WEBHOOK_URL = "https://afroboost-audio-1.emergent.host/api/webhook/whatsapp";
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

// === INITIALISATION SDK AU CHARGEMENT DU MODULE ===
let emailjsInitialized = false;
try {
  emailjs.init(EMAILJS_PUBLIC_KEY);
  emailjsInitialized = true;
  console.log('✅ [Gateway] EmailJS SDK initialisé');
} catch (e) {
  console.error('❌ [Gateway] Erreur init EmailJS:', e);
}

/**
 * === LIAISON IA -> EMAILJS ===
 * Fonction de soudure entre l'agent IA et le canal EmailJS
 * Bypass du crash PostHog avec try/catch robuste
 * 
 * @param {string} aiMessage - Message généré par l'IA
 * @param {string} clientEmail - Email du destinataire
 * @param {string} clientName - Nom du destinataire (optionnel)
 * @param {string} subject - Sujet de l'email (optionnel)
 * @returns {Promise<{success: boolean, ...}>}
 */
export const sendAIResponseViaEmail = async (aiMessage, clientEmail, clientName = 'Client', subject = 'Afroboost - Réponse') => {
  // === BYPASS CRASH POSTHOG ===
  // L'autonomie de l'IA est prioritaire sur le tracking
  try {
    console.log('[IA->EmailJS] ========================================');
    console.log('[IA->EmailJS] Liaison IA -> EmailJS activée');
    console.log('[IA->EmailJS] Destinataire:', clientEmail);
    console.log('[IA->EmailJS] Message IA:', aiMessage?.substring(0, 100) + '...');
    console.log('[IA->EmailJS] ========================================');
    
    // Validation basique
    if (!clientEmail || !clientEmail.includes('@')) {
      console.error('[IA->EmailJS] ❌ Email invalide:', clientEmail);
      return { success: false, error: 'Email invalide', channel: 'email' };
    }
    
    if (!aiMessage || aiMessage.trim() === '') {
      console.error('[IA->EmailJS] ❌ Message IA vide');
      return { success: false, error: 'Message IA vide', channel: 'email' };
    }
    
    // Paramètres du template - format plat uniquement
    const templateParams = {
      message: String(aiMessage),
      to_email: String(clientEmail),
      to_name: String(clientName),
      subject: String(subject)
    };
    
    console.log('[IA->EmailJS] Template params:', JSON.stringify(templateParams));
    
    // === ENVOI VIA EMAILJS ===
    const response = await emailjs.send(
      EMAILJS_SERVICE_ID,
      EMAILJS_TEMPLATE_ID,
      templateParams,
      EMAILJS_PUBLIC_KEY
    );
    
    // === VALIDATION SUCCÈS ===
    console.log('IA : Message envoyé via EmailJS');
    console.log('[IA->EmailJS] ✅ Réponse:', response.status, response.text);
    
    return { 
      success: true, 
      response, 
      channel: 'email',
      aiMessageSent: aiMessage.substring(0, 50) + '...'
    };
    
  } catch (error) {
    // BYPASS: Ne pas laisser l'erreur bloquer l'IA
    console.error('[IA->EmailJS] ❌ Erreur (bypass PostHog):', error);
    
    // Vérifier si c'est une erreur PostHog/DataClone
    if (error.name === 'DataCloneError' || error.message?.includes('clone')) {
      console.warn('[IA->EmailJS] ⚠️ Erreur PostHog ignorée - tentative alternative');
      // L'erreur PostHog ne doit pas bloquer
      return { 
        success: false, 
        error: 'PostHog blocking - message may have been sent',
        postHogBlocked: true,
        channel: 'email'
      };
    }
    
    return { 
      success: false, 
      error: error?.text || error?.message || 'Erreur inconnue',
      channel: 'email'
    };
  }
};

/**
 * === LIAISON IA -> WHATSAPP ===
 * Fonction de soudure entre l'agent IA et le canal WhatsApp via webhook
 * 
 * @param {string} aiMessage - Message généré par l'IA
 * @param {string} phoneNumber - Numéro de téléphone du destinataire
 * @param {object} twilioConfig - Config Twilio (optionnel si webhook utilisé)
 * @returns {Promise<{success: boolean, ...}>}
 */
export const sendAIResponseViaWhatsApp = async (aiMessage, phoneNumber, twilioConfig = null) => {
  // === BYPASS CRASH POSTHOG ===
  try {
    console.log('[IA->WhatsApp] ========================================');
    console.log('[IA->WhatsApp] Liaison IA -> WhatsApp activée');
    console.log('[IA->WhatsApp] Destinataire:', phoneNumber);
    console.log('[IA->WhatsApp] Message IA:', aiMessage?.substring(0, 100) + '...');
    console.log('[IA->WhatsApp] ========================================');
    
    // Validation basique
    if (!phoneNumber) {
      console.error('[IA->WhatsApp] ❌ Numéro invalide');
      return { success: false, error: 'Numéro invalide', channel: 'whatsapp' };
    }
    
    if (!aiMessage || aiMessage.trim() === '') {
      console.error('[IA->WhatsApp] ❌ Message IA vide');
      return { success: false, error: 'Message IA vide', channel: 'whatsapp' };
    }
    
    // Formater le numéro au format E.164
    let formattedPhone = phoneNumber.replace(/[^\d+]/g, '');
    if (!formattedPhone.startsWith('+')) {
      formattedPhone = formattedPhone.startsWith('0') 
        ? '+41' + formattedPhone.substring(1) 
        : '+' + formattedPhone;
    }
    
    // === OPTION 1: Via Twilio direct si config fournie ===
    if (twilioConfig && twilioConfig.accountSid && twilioConfig.authToken) {
      const { accountSid, authToken, fromNumber } = twilioConfig;
      
      const formData = new URLSearchParams();
      formData.append('From', `whatsapp:${fromNumber.startsWith('+') ? fromNumber : '+' + fromNumber}`);
      formData.append('To', `whatsapp:${formattedPhone}`);
      formData.append('Body', String(aiMessage));
      
      const response = await fetch(
        `https://api.twilio.com/2010-04-01/Accounts/${accountSid}/Messages.json`,
        {
          method: 'POST',
          headers: {
            'Authorization': 'Basic ' + btoa(`${accountSid}:${authToken}`),
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: formData
        }
      );
      
      const data = await response.json();
      
      if (!response.ok) {
        console.error('[IA->WhatsApp] ❌ Erreur Twilio:', data);
        return { success: false, error: data.message, channel: 'whatsapp' };
      }
      
      console.log('IA : Message envoyé via WhatsApp (Twilio)');
      console.log('[IA->WhatsApp] ✅ SID:', data.sid);
      
      return { success: true, sid: data.sid, channel: 'whatsapp' };
    }
    
    // === OPTION 2: Via webhook backend ===
    const webhookUrl = `${BACKEND_URL}/api/send-whatsapp`;
    
    console.log('[IA->WhatsApp] Tentative via webhook:', webhookUrl);
    
    try {
      const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          to: formattedPhone,
          message: String(aiMessage)
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('IA : Message envoyé via WhatsApp (webhook)');
        return { success: true, data, channel: 'whatsapp', viaWebhook: true };
      }
    } catch (webhookError) {
      console.warn('[IA->WhatsApp] Webhook non disponible:', webhookError.message);
    }
    
    // === OPTION 3: Mode simulation ===
    console.warn('[IA->WhatsApp] ⚠️ Mode simulation activé');
    console.log('IA : Message WhatsApp simulé pour:', formattedPhone);
    
    return { 
      success: true, 
      simulated: true, 
      channel: 'whatsapp',
      message: `WhatsApp prêt pour: ${formattedPhone}`
    };
    
  } catch (error) {
    console.error('[IA->WhatsApp] ❌ Erreur (bypass PostHog):', error);
    
    // Vérifier si c'est une erreur PostHog
    if (error.name === 'DataCloneError' || error.message?.includes('clone')) {
      console.warn('[IA->WhatsApp] ⚠️ Erreur PostHog ignorée');
      return { 
        success: false, 
        error: 'PostHog blocking',
        postHogBlocked: true,
        channel: 'whatsapp'
      };
    }
    
    return { success: false, error: error.message, channel: 'whatsapp' };
  }
};

/**
 * === DISPATCH IA UNIFIÉ ===
 * Point d'entrée unique pour l'agent IA - route vers le bon canal
 * L'IA appelle cette fonction avec le message généré et la destination
 * 
 * @param {object} aiOutput - Sortie de l'agent IA
 * @param {string} aiOutput.message - Message généré par l'IA
 * @param {string} aiOutput.channel - 'email' ou 'whatsapp'
 * @param {string} aiOutput.destination - Email ou numéro de téléphone
 * @param {string} aiOutput.clientName - Nom du client (optionnel)
 * @param {object} aiOutput.twilioConfig - Config Twilio (optionnel)
 * @returns {Promise<{success: boolean, ...}>}
 */
export const dispatchAIResponse = async (aiOutput) => {
  const { message, channel, destination, clientName, twilioConfig } = aiOutput;
  
  console.log('[IA-Dispatch] ========================================');
  console.log('[IA-Dispatch] Agent IA demande envoi');
  console.log('[IA-Dispatch] Canal:', channel);
  console.log('[IA-Dispatch] Destination:', destination);
  console.log('[IA-Dispatch] ========================================');
  
  // === BYPASS CRASH POSTHOG - Encapsulation totale ===
  try {
    if (channel === 'email') {
      return await sendAIResponseViaEmail(message, destination, clientName);
    }
    
    if (channel === 'whatsapp') {
      return await sendAIResponseViaWhatsApp(message, destination, twilioConfig);
    }
    
    console.error('[IA-Dispatch] ❌ Canal inconnu:', channel);
    return { success: false, error: `Canal inconnu: ${channel}` };
    
  } catch (dispatchError) {
    console.error('[IA-Dispatch] ❌ Erreur dispatch (bypass):', dispatchError);
    
    // Ne jamais bloquer l'IA
    return { 
      success: false, 
      error: dispatchError.message,
      bypassed: true
    };
  }
};

/**
 * PASSERELLE EMAIL - Canal technique pur
 * Reçoit les paramètres de l'agent IA et les transmet à EmailJS
 * AUCUNE logique de décision - juste transmission
 * 
 * @param {string} to_email - Email du destinataire
 * @param {string} to_name - Nom du destinataire (défaut: 'Client')
 * @param {string} subject - Sujet (défaut: 'Afroboost')
 * @param {string} message - Corps du message généré par l'IA
 * @returns {Promise<{success: boolean, response?: any, error?: string}>}
 */
export const sendEmailGateway = async (to_email, to_name = 'Client', subject = 'Afroboost', message = '') => {
  // Payload plat - texte uniquement, aucun objet complexe
  const params = {
    to_email: String(to_email),
    to_name: String(to_name),
    subject: String(subject),
    message: String(message)
  };
  
  console.log('[Gateway] ========================================');
  console.log('[Gateway] DEMANDE EMAILJS - Canal de sortie IA');
  console.log('[Gateway] Destination:', to_email);
  console.log('[Gateway] Payload:', JSON.stringify(params));
  console.log('[Gateway] ========================================');
  
  try {
    const response = await emailjs.send(
      EMAILJS_SERVICE_ID,
      EMAILJS_TEMPLATE_ID,
      params,
      EMAILJS_PUBLIC_KEY
    );
    
    console.log('[Gateway] ✅ Email transmis:', response.status);
    return { success: true, response, channel: 'email' };
  } catch (error) {
    console.error('[Gateway] ❌ Erreur transmission email:', error);
    return { 
      success: false, 
      error: error?.text || error?.message || 'Erreur inconnue',
      channel: 'email'
    };
  }
};

/**
 * PASSERELLE WHATSAPP - Canal technique pur
 * Reçoit les paramètres de l'agent IA et les transmet à Twilio
 * AUCUNE logique de décision - juste transmission
 * 
 * @param {string} phoneNumber - Numéro de téléphone du destinataire
 * @param {string} message - Message généré par l'IA
 * @param {object} twilioConfig - {accountSid, authToken, fromNumber}
 * @returns {Promise<{success: boolean, sid?: string, error?: string}>}
 */
export const sendWhatsAppGateway = async (phoneNumber, message, twilioConfig = {}) => {
  const { accountSid, authToken, fromNumber } = twilioConfig;
  
  console.log('[Gateway] ========================================');
  console.log('[Gateway] DEMANDE WHATSAPP/TWILIO - Canal de sortie IA');
  console.log('[Gateway] Destination:', phoneNumber);
  console.log('[Gateway] Message:', message?.substring(0, 50) + '...');
  console.log('[Gateway] Config présente:', !!accountSid && !!authToken && !!fromNumber);
  console.log('[Gateway] ========================================');
  
  // Si pas de config Twilio, mode simulation (pour développement)
  if (!accountSid || !authToken || !fromNumber) {
    console.warn('[Gateway] ⚠️ Twilio non configuré - Mode simulation');
    // Ne pas bloquer l'agent IA, retourner succès simulé
    return { 
      success: true, 
      simulated: true, 
      channel: 'whatsapp',
      message: `WhatsApp prêt pour: ${phoneNumber}` 
    };
  }
  
  // Formater le numéro au format E.164
  let formattedPhone = phoneNumber.replace(/[^\d+]/g, '');
  if (!formattedPhone.startsWith('+')) {
    formattedPhone = formattedPhone.startsWith('0') 
      ? '+41' + formattedPhone.substring(1) 
      : '+' + formattedPhone;
  }
  
  // Payload plat - URLSearchParams pour Twilio
  const formData = new URLSearchParams();
  formData.append('From', `whatsapp:${fromNumber.startsWith('+') ? fromNumber : '+' + fromNumber}`);
  formData.append('To', `whatsapp:${formattedPhone}`);
  formData.append('Body', String(message));
  
  try {
    const response = await fetch(
      `https://api.twilio.com/2010-04-01/Accounts/${accountSid}/Messages.json`,
      {
        method: 'POST',
        headers: {
          'Authorization': 'Basic ' + btoa(`${accountSid}:${authToken}`),
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData
      }
    );
    
    const data = await response.json();
    
    if (!response.ok) {
      console.error('[Gateway] ❌ Erreur Twilio:', data);
      return { 
        success: false, 
        error: data.message || `HTTP ${response.status}`,
        channel: 'whatsapp'
      };
    }
    
    console.log('[Gateway] ✅ WhatsApp transmis, SID:', data.sid);
    return { success: true, sid: data.sid, channel: 'whatsapp' };
  } catch (error) {
    console.error('[Gateway] ❌ Erreur transmission WhatsApp:', error);
    return { 
      success: false, 
      error: error.message,
      channel: 'whatsapp'
    };
  }
};

/**
 * PASSERELLE UNIFIÉE - Point d'entrée unique pour l'agent IA
 * L'IA choisit le canal (email ou whatsapp) et cette fonction route
 * 
 * @param {string} channel - 'email' ou 'whatsapp'
 * @param {object} params - Paramètres selon le canal
 * @returns {Promise<{success: boolean, ...}>}
 */
export const sendMessageGateway = async (channel, params) => {
  console.log('[Gateway] 🤖 Agent IA demande envoi via canal:', channel);
  
  if (channel === 'email') {
    return sendEmailGateway(
      params.to_email,
      params.to_name,
      params.subject,
      params.message
    );
  }
  
  if (channel === 'whatsapp') {
    return sendWhatsAppGateway(
      params.phoneNumber,
      params.message,
      params.twilioConfig
    );
  }
  
  return { success: false, error: `Canal inconnu: ${channel}` };
};

// === EXPORTS ===
export default {
  sendEmailGateway,
  sendWhatsAppGateway,
  sendMessageGateway,
  EMAILJS_SERVICE_ID,
  EMAILJS_TEMPLATE_ID,
  EMAILJS_PUBLIC_KEY,
  isInitialized: () => emailjsInitialized
};
