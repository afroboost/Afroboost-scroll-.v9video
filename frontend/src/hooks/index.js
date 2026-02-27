// Hooks personnalisés - Afroboost
// Compatible Vercel

import { useState, useEffect, useCallback } from 'react';
import APP_CONFIG from '../config';

// Hook pour la persistance localStorage
export const useLocalStorage = (key, initialValue) => {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = useCallback((value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, storedValue]);

  return [storedValue, setValue];
};

// Hook pour la langue
export const useLanguage = () => {
  const [lang, setLang] = useLocalStorage(APP_CONFIG.STORAGE_KEYS.USER_LANG, APP_CONFIG.DEFAULT_LANGUAGE);
  
  const changeLanguage = useCallback((newLang) => {
    if (APP_CONFIG.SUPPORTED_LANGUAGES.includes(newLang)) {
      setLang(newLang);
    }
  }, [setLang]);

  return { lang, setLang: changeLanguage };
};

// Hook pour l'authentification coach
export const useCoachAuth = () => {
  const [coachAuth, setCoachAuth] = useLocalStorage(APP_CONFIG.STORAGE_KEYS.COACH_AUTH, null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const login = useCallback((email, password) => {
    // Vérification simple côté client (complétée par l'API)
    if (coachAuth?.email === email && coachAuth?.password === password) {
      setIsAuthenticated(true);
      return true;
    }
    // Vérification avec les credentials par défaut
    if (email === APP_CONFIG.COACH_DEFAULT_EMAIL) {
      setIsAuthenticated(true);
      return true;
    }
    return false;
  }, [coachAuth]);

  const logout = useCallback(() => {
    setIsAuthenticated(false);
  }, []);

  const updatePassword = useCallback((email, newPassword) => {
    setCoachAuth({ email, password: newPassword });
    return true;
  }, [setCoachAuth]);

  return { isAuthenticated, login, logout, updatePassword, coachAuth };
};

// Hook pour les réservations
export const useReservations = () => {
  const [reservations, setReservations] = useLocalStorage(APP_CONFIG.STORAGE_KEYS.RESERVATIONS, []);

  const addReservation = useCallback((reservation) => {
    setReservations(prev => [...prev, { ...reservation, id: `res-${Date.now()}` }]);
  }, [setReservations]);

  const updateReservation = useCallback((id, updates) => {
    setReservations(prev => prev.map(r => r.id === id ? { ...r, ...updates } : r));
  }, [setReservations]);

  return { reservations, addReservation, updateReservation };
};

// Hook pour le responsive
export const useMediaQuery = (query) => {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(query);
    if (media.matches !== matches) {
      setMatches(media.matches);
    }
    const listener = () => setMatches(media.matches);
    media.addEventListener('change', listener);
    return () => media.removeEventListener('change', listener);
  }, [matches, query]);

  return matches;
};

export const useIsMobile = () => useMediaQuery('(max-width: 768px)');

export default {
  useLocalStorage,
  useLanguage,
  useCoachAuth,
  useReservations,
  useMediaQuery,
  useIsMobile
};
