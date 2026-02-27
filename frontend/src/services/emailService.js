// emailService.js - Service d'envoi d'emails automatisés via EmailJS
// Compatible Vercel - Configuration stockée dans localStorage
import emailjs from '@emailjs/browser';

// === CONFIGURATION DÉFAUT - IDs validés ===
const DEFAULT_CONFIG = {
  serviceId: 'service_8mrmxim',
  templateId: 'template_3n1u86p',
  publicKey: '5LfgQSIEQoqq_XSqt'
};

// === ÉTAT ===
let cachedConfig = null;
let isInitialized = false;

/**
 * Charge la config depuis localStorage (synchrone)
 */
const loadConfigFromStorage = () => {
  try {
    const stored = localStorage.getItem('emailjs_config');
    if (stored) {
      const parsed = JSON.parse(stored);
      // Valider que tous les champs sont présents
      if (parsed.serviceId && parsed.templateId && parsed.publicKey) {
        return parsed;
      }
    }
  } catch (e) {
    console.error('Error loading EmailJS config:', e);
  }
  return { ...DEFAULT_CONFIG };
};

/**
 * Sauvegarde la config dans localStorage
 */
const saveConfigToStorage = (config) => {
  try {
    localStorage.setItem('emailjs_config', JSON.stringify(config));
    return true;
  } catch (e) {
    console.error('Error saving EmailJS config:', e);
    return false;
  }
};

// Initialiser le cache au chargement du module
cachedConfig = loadConfigFromStorage();

/**
 * Récupère la configuration EmailJS (synchrone)
 */
export const getEmailJSConfig = () => {
  if (!cachedConfig) {
    cachedConfig = loadConfigFromStorage();
  }
  return { ...cachedConfig };
};

/**
 * Sauvegarde la configuration EmailJS
 */
export const saveEmailJSConfig = (config) => {
  cachedConfig = { ...config };
  isInitialized = false; // Forcer la réinitialisation
  return saveConfigToStorage(config);
};

/**
 * Vérifie si EmailJS est configuré
 */
export const isEmailJSConfigured = () => {
  const config = getEmailJSConfig();
  return !!(config.serviceId && config.templateId && config.publicKey);
};

/**
 * Initialise EmailJS une seule fois
 */
export const initEmailJS = () => {
  if (isInitialized) return true;
  
  const config = getEmailJSConfig();
  if (config.publicKey) {
    try {
      emailjs.init(config.publicKey);
      isInitialized = true;
      console.log('✅ EmailJS initialized');
      return true;
    } catch (e) {
      console.error('❌ EmailJS init error:', e);
      return false;
    }
  }
  return false;
};

/**
 * Envoie un email avec un objet JSON plat et simple
 */
export const sendEmail = async (params) => {
  const config = getEmailJSConfig();
  
  // Vérifier la configuration
  if (!config.serviceId || !config.templateId || !config.publicKey) {
    console.error('❌ EmailJS non configuré');
    return { success: false, error: 'EmailJS non configuré' };
  }

  // Initialiser si nécessaire
  initEmailJS();

  // Créer un objet JSON PLAT et SIMPLE - pas de références complexes
  const templateParams = {
    to_email: String(params.to_email || ''),
    to_name: String(params.to_name || 'Client'),
    subject: String(params.subject || 'Afroboost'),
    message: String(params.message || '')
  };

  console.log('📧 Sending email:', { to: templateParams.to_email, subject: templateParams.subject });

  try {
    const response = await emailjs.send(
      config.serviceId,
      config.templateId,
      templateParams,
      config.publicKey
    );
    
    console.log('✅ Email sent:', response.status, response.text);
    return { success: true, response: { status: response.status, text: response.text } };
  } catch (error) {
    const errorMsg = error?.text || error?.message || 'Erreur inconnue';
    console.error('❌ EmailJS error:', errorMsg);
    return { success: false, error: errorMsg };
  }
};

/**
 * Envoie des emails en masse avec progression
 */
export const sendBulkEmails = async (recipients, campaign, onProgress) => {
  const results = {
    sent: 0,
    failed: 0,
    errors: [],
    details: []
  };

  const total = recipients.length;

  // Vérifier la configuration
  if (!isEmailJSConfigured()) {
    console.error('❌ EmailJS not configured');
    return {
      ...results,
      failed: total,
      errors: ['EmailJS non configuré']
    };
  }

  // Initialiser EmailJS
  initEmailJS();

  console.log(`📧 Starting bulk email send to ${total} recipients...`);

  // Envoyer les emails un par un avec délai
  for (let i = 0; i < recipients.length; i++) {
    const recipient = recipients[i];
    
    if (onProgress) {
      onProgress(i + 1, total, 'sending', recipient.name || recipient.email);
    }

    try {
      const result = await sendEmail({
        to_email: recipient.email,
        to_name: recipient.name,
        subject: campaign.name,
        message: campaign.message,
        media_url: campaign.mediaUrl
      });

      if (result.success) {
        results.sent++;
        results.details.push({
          email: recipient.email,
          name: recipient.name,
          status: 'sent'
        });
        console.log(`✅ [${i + 1}/${total}] Email sent to ${recipient.email}`);
      } else {
        results.failed++;
        results.errors.push(`${recipient.email}: ${result.error}`);
        results.details.push({
          email: recipient.email,
          name: recipient.name,
          status: 'failed',
          error: result.error
        });
        console.error(`❌ [${i + 1}/${total}] Failed to send to ${recipient.email}:`, result.error);
      }
    } catch (error) {
      results.failed++;
      const errorMsg = error.message || 'Erreur inconnue';
      results.errors.push(`${recipient.email}: ${errorMsg}`);
      results.details.push({
        email: recipient.email,
        name: recipient.name,
        status: 'failed',
        error: errorMsg
      });
      console.error(`❌ [${i + 1}/${total}] Exception for ${recipient.email}:`, error);
    }

    // Délai entre les envois (300ms pour éviter rate limit)
    if (i < recipients.length - 1) {
      await new Promise(resolve => setTimeout(resolve, 300));
    }
  }

  if (onProgress) {
    onProgress(total, total, 'completed');
  }

  console.log(`📧 Bulk email complete: ${results.sent} sent, ${results.failed} failed`);
  return results;
};

/**
 * Teste la configuration EmailJS avec un payload minimal
 * Correspond exactement au template 'template_3n1u86p'
 */
export const testEmailJSConfig = async (testEmail) => {
  console.log('🧪 Testing EmailJS config with email:', testEmail);
  
  const config = getEmailJSConfig();
  
  // Vérifier que les IDs ne sont pas undefined
  if (!config.serviceId || !config.templateId || !config.publicKey) {
    console.error('❌ EmailJS config incomplete:', config);
    return { 
      success: false, 
      error: 'Configuration EmailJS incomplète. Vérifiez Service ID, Template ID et Public Key.' 
    };
  }
  
  // Initialiser EmailJS
  try {
    emailjs.init(config.publicKey);
  } catch (e) {
    console.error('❌ EmailJS init failed:', e);
  }
  
  // PAYLOAD SIMPLIFIÉ - Exactement ce que le template attend
  const params = {
    to_email: testEmail,
    to_name: "Ami Afroboost",
    subject: "Ton test Afroboost",
    message: "Ceci est un test de configuration EmailJS. Si vous recevez ce message, tout fonctionne !"
  };
  
  console.log('📧 Sending with params:', params);
  console.log('📧 Config:', { 
    serviceId: config.serviceId, 
    templateId: config.templateId, 
    publicKey: config.publicKey.substring(0, 5) + '...' 
  });
  
  try {
    // Appel direct à emailjs.send côté client
    const response = await emailjs.send(
      config.serviceId,
      config.templateId,
      params,
      config.publicKey
    );
    
    console.log('✅ Test email sent successfully!', response);
    return { success: true, response };
  } catch (error) {
    console.error('❌ Test email failed:', error);
    return { 
      success: false, 
      error: error.text || error.message || 'Erreur EmailJS inconnue'
    };
  }
};

export default {
  getEmailJSConfig,
  saveEmailJSConfig,
  isEmailJSConfigured,
  initEmailJS,
  sendEmail,
  sendBulkEmails,
  testEmailJSConfig
};
