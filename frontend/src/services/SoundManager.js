/**
 * SoundManager.js - Gestionnaire centralisé des sons et du mode Silence
 * 
 * Extrait de ChatWidget.js pour alléger le fichier principal.
 * Gère:
 * - Les préférences sonores (localStorage)
 * - Le mode Silence Auto (22h-08h)
 * - Le wrapper playSoundIfEnabled() avec toutes les vérifications
 */

import { playNotificationSound } from './notificationService';

// === CONSTANTES ===
const SOUND_ENABLED_KEY = 'afroboost_sound_enabled';
const SILENCE_AUTO_KEY = 'afroboost_silence_auto';
const SILENCE_START_HOUR = 22;  // 22h
const SILENCE_END_HOUR = 8;     // 08h

/**
 * Récupère l'état des sons depuis localStorage
 * @returns {boolean} - true si les sons sont activés (défaut: true)
 */
export const getSoundEnabled = () => {
  try {
    const saved = localStorage.getItem(SOUND_ENABLED_KEY);
    return saved !== null ? saved === 'true' : true;
  } catch {
    return true;
  }
};

/**
 * Sauvegarde l'état des sons dans localStorage
 * @param {boolean} enabled - Nouvel état
 */
export const setSoundEnabled = (enabled) => {
  try {
    localStorage.setItem(SOUND_ENABLED_KEY, String(enabled));
    console.log('[SOUND] 🔊', enabled ? 'Activé' : 'Désactivé');
  } catch (e) {
    console.warn('[SOUND] ⚠️ Erreur sauvegarde:', e.message);
  }
};

/**
 * Récupère l'état du mode Silence Auto depuis localStorage
 * @returns {boolean} - true si le mode silence est activé (défaut: false)
 */
export const getSilenceAutoEnabled = () => {
  try {
    const saved = localStorage.getItem(SILENCE_AUTO_KEY);
    return saved === 'true';
  } catch {
    return false;
  }
};

/**
 * Sauvegarde l'état du mode Silence Auto dans localStorage
 * @param {boolean} enabled - Nouvel état
 */
export const setSilenceAutoEnabled = (enabled) => {
  try {
    localStorage.setItem(SILENCE_AUTO_KEY, String(enabled));
    console.log('[SILENCE AUTO] 🌙', enabled ? 'Activé (22h-08h)' : 'Désactivé');
  } catch (e) {
    console.warn('[SILENCE AUTO] ⚠️ Erreur sauvegarde:', e.message);
  }
};

/**
 * Vérifie si l'heure actuelle est dans la plage de silence (22h-08h)
 * @returns {boolean} - true si on est dans la plage de silence
 */
export const isInSilenceHours = () => {
  const hour = new Date().getHours();
  return hour >= SILENCE_START_HOUR || hour < SILENCE_END_HOUR;
};

/**
 * Retourne la plage de silence formatée
 * @returns {string} - Ex: "22h-08h"
 */
export const getSilenceHoursLabel = () => {
  return `${SILENCE_START_HOUR}h-${SILENCE_END_HOUR.toString().padStart(2, '0')}h`;
};

/**
 * Vérifie si les sons doivent être joués en fonction de toutes les conditions
 * @param {boolean} soundEnabled - État du toggle son
 * @param {boolean} silenceAutoEnabled - État du mode silence auto
 * @returns {boolean} - true si les sons peuvent être joués
 */
export const canPlaySound = (soundEnabled, silenceAutoEnabled) => {
  // Vérifier le mode silence auto (22h-08h)
  if (silenceAutoEnabled && isInSilenceHours()) {
    return false;
  }
  // Vérifier la préférence manuelle
  return soundEnabled;
};

/**
 * Joue un son de notification si toutes les conditions sont remplies
 * @param {string} type - Type de son ('message', 'private', 'coach', 'user')
 * @param {boolean} soundEnabled - État du toggle son
 * @param {boolean} silenceAutoEnabled - État du mode silence auto
 * @returns {boolean} - true si le son a été joué
 */
export const playSoundIfAllowed = (type = 'message', soundEnabled, silenceAutoEnabled) => {
  // Vérifier le mode silence auto (22h-08h)
  if (silenceAutoEnabled && isInSilenceHours()) {
    console.log('[SOUND] 🌙 Mode silence actif (22h-08h)');
    return false;
  }
  
  // Vérifier la préférence manuelle
  if (soundEnabled) {
    playNotificationSound(type);
    return true;
  }
  
  return false;
};

/**
 * Hook personnalisé pour gérer l'état des sons
 * À utiliser avec useState dans le composant parent
 * @returns {object} - Configuration initiale des états
 */
export const getInitialSoundState = () => ({
  soundEnabled: getSoundEnabled(),
  silenceAutoEnabled: getSilenceAutoEnabled()
});

// === TYPES DE SONS DISPONIBLES ===
export const SOUND_TYPES = {
  MESSAGE: 'message',      // Son standard pour les messages groupe (Pop)
  PRIVATE: 'private',      // Son distinct pour les DM (Ding cristallin)
  COACH: 'coach',          // Son pour les réponses du coach
  USER: 'user'             // Son subtil pour notifications utilisateur
};

// Export par défaut
export default {
  getSoundEnabled,
  setSoundEnabled,
  getSilenceAutoEnabled,
  setSilenceAutoEnabled,
  isInSilenceHours,
  getSilenceHoursLabel,
  canPlaySound,
  playSoundIfAllowed,
  getInitialSoundState,
  SOUND_TYPES
};
