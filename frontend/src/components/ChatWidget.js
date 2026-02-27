// /components/ChatWidget.js - Widget IA flottant avec capture de leads et reconnaissance automatique
// Architecture modulaire Afroboost - Utilise l'API chat améliorée
// Fonctionnalités: Socket.IO temps réel, notifications push, sons, liens cliquables, suppression historique

import React, { useState, useEffect, useRef, useCallback, memo } from 'react';
import axios from 'axios';
import { io } from 'socket.io-client';
import { 
  parseMessageContent, 
  notifyPrivateMessage,
  stopTitleFlash,
  showNewMessageNotification,
  requestNotificationPermission,
  getNotificationPermissionStatus,
  unlockAudio
} from '../services/notificationService';
import { 
  isPushSupported, 
  promptForNotifications, 
  registerServiceWorker,
  isSubscribed,
  subscribeToPush
} from '../services/pushNotificationService';
import { 
  isInSilenceHours, 
  getSilenceHoursLabel,
  playSoundIfAllowed,
  SOUND_TYPES 
} from '../services/SoundManager';
import EmojiPicker from './EmojiPicker';
import SubscriberForm from './chat/SubscriberForm';
import PrivateChatView from './chat/PrivateChatView';
import BookingPanel from './chat/BookingPanel';
import MessageSkeleton from './chat/MessageSkeleton';
import MediaMessage from './chat/MediaMessage';
import { parseMediaUrl, isMediaUrl } from '../services/MediaParser';

const API = process.env.REACT_APP_BACKEND_URL + '/api';
const SOCKET_URL = process.env.REACT_APP_BACKEND_URL; // URL Socket.IO (même que backend)

// Clés localStorage pour la mémorisation client (persistance de session)
const CHAT_CLIENT_KEY = 'af_chat_client';
const CHAT_SESSION_KEY = 'af_chat_session';
const AFROBOOST_IDENTITY_KEY = 'afroboost_identity'; // Clé unifiée pour l'identité
const AFROBOOST_PROFILE_KEY = 'afroboost_profile'; // Profil abonné avec code promo validé
const MESSAGE_CACHE_KEY = 'afroboost_last_msgs'; // Cache hybride pour chargement instantané

// Icône Plein Écran
const FullscreenIcon = () => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
    <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
  </svg>
);

// Icône Réduire Plein Écran
const ExitFullscreenIcon = () => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
    <path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"/>
  </svg>
);

// Icône Emoji
const EmojiIcon = () => (
  <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-5-6c.78 2.34 2.72 4 5 4s4.22-1.66 5-4H7zm8.5-3c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11z"/>
  </svg>
);

// Icône WhatsApp SVG
const WhatsAppIcon = () => (
  <svg viewBox="0 0 24 24" width="28" height="28" fill="white">
    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
  </svg>
);

// Icône Fermer
const CloseIcon = () => (
  <svg viewBox="0 0 24 24" width="20" height="20" fill="white">
    <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
  </svg>
);

// Icône Envoyer
const SendIcon = () => (
  <svg viewBox="0 0 24 24" width="20" height="20" fill="white">
    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
  </svg>
);

// Icône Corbeille
const TrashIcon = () => (
  <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
    <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
  </svg>
);

// Icône Groupe
const GroupIcon = () => (
  <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
    <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
  </svg>
);

/**
 * Formate l'horodatage d'un message
 * - "À l'instant" si < 60 secondes
 * - "14:05" pour aujourd'hui
 * - "Hier, 09:15" pour hier
 * - "08/02, 18:30" pour les autres jours
 */
const formatMessageTime = (dateStr) => {
  if (!dateStr) return '';
  
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return '';
    
    const now = new Date();
    const diffSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    // Message envoyé il y a moins de 60 secondes
    if (diffSeconds < 60 && diffSeconds >= 0) {
      return 'À l\'instant';
    }
    
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const msgDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    
    // Format heure locale 24h (Europe/Paris)
    const timeStr = date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', hour12: false });
    
    if (msgDate.getTime() === today.getTime()) {
      return timeStr;
    } else if (msgDate.getTime() === yesterday.getTime()) {
      return `Hier, ${timeStr}`;
    } else {
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      return `${day}/${month}, ${timeStr}`;
    }
  } catch (e) {
    return '';
  }
};

// === COMPOSANTS MÉDIA INLINE ===
const InlineYouTubePlayer = ({ videoId, thumbnailUrl }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  
  return (
    <div style={{ marginTop: '8px', borderRadius: '12px', overflow: 'hidden', maxWidth: '100%' }} data-testid="inline-youtube">
      {!isPlaying ? (
        <button
          onClick={() => setIsPlaying(true)}
          style={{
            width: '100%',
            aspectRatio: '16/9',
            background: `url(${thumbnailUrl}) center/cover no-repeat`,
            border: 'none',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative'
          }}
          data-testid="youtube-thumbnail-btn"
        >
          <div style={{
            width: '56px',
            height: '56px',
            borderRadius: '50%',
            background: 'rgba(0,0,0,0.75)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <svg width="24" height="24" fill="#fff" viewBox="0 0 24 24">
              <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
          </div>
        </button>
      ) : (
        <iframe
          src={`https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1&rel=0&playsinline=1`}
          style={{ width: '100%', aspectRatio: '16/9', border: 'none' }}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          title="YouTube Video"
        />
      )}
    </div>
  );
};

const InlineDriveImage = ({ directUrl, previewUrl }) => {
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  
  // Timeout de 3 secondes pour les images Drive
  useEffect(() => {
    const timer = setTimeout(() => {
      if (loading) {
        setError(true);
        setLoading(false);
      }
    }, 3000);
    return () => clearTimeout(timer);
  }, [loading]);
  
  if (error) {
    return (
      <a 
        href={previewUrl || directUrl} 
        target="_blank" 
        rel="noopener noreferrer"
        style={{
          display: 'block',
          marginTop: '8px',
          padding: '12px',
          background: 'linear-gradient(135deg, #1a1a2e, #16213e)',
          borderRadius: '12px',
          textDecoration: 'none',
          color: '#fff',
          textAlign: 'center'
        }}
        data-testid="drive-fallback"
      >
        <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginBottom: '4px' }}>
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
        </svg>
        <div style={{ fontSize: '12px' }}>Voir l'image sur Drive</div>
      </a>
    );
  }
  
  return (
    <img
      src={directUrl}
      alt="Google Drive"
      onLoad={() => setLoading(false)}
      onError={() => { setError(true); setLoading(false); }}
      style={{
        marginTop: '8px',
        maxWidth: '100%',
        borderRadius: '12px',
        display: loading ? 'none' : 'block'
      }}
      data-testid="inline-drive-image"
    />
  );
};

const InlineImage = ({ src }) => (
  <img
    src={src}
    alt="Image"
    style={{
      marginTop: '8px',
      maxWidth: '100%',
      borderRadius: '12px',
      display: 'block'
    }}
    data-testid="inline-image"
  />
);

const InlineCtaButton = ({ label, url }) => {
  // Validation stricte : label ET url doivent être non-vides
  if (!label || !url || typeof label !== 'string' || typeof url !== 'string') return null;
  const trimmedLabel = label.trim();
  const trimmedUrl = url.trim();
  if (!trimmedLabel || !trimmedUrl) return null;
  
  // Auto-ajout de https:// si manquant
  const safeUrl = trimmedUrl.startsWith('http://') || trimmedUrl.startsWith('https://') 
    ? trimmedUrl 
    : `https://${trimmedUrl}`;
  
  return (
    <a
      href={safeUrl}
      target="_blank"
      rel="noopener noreferrer"
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
        marginTop: '10px',
        padding: '12px 20px',
        background: 'linear-gradient(135deg, #9333ea, #d91cd2)',
        borderRadius: '12px',
        color: '#fff',
        fontWeight: '600',
        fontSize: '14px',
        textDecoration: 'none',
        transition: 'transform 0.2s, opacity 0.2s'
      }}
      onMouseEnter={(e) => { e.target.style.transform = 'scale(1.02)'; e.target.style.opacity = '0.9'; }}
      onMouseLeave={(e) => { e.target.style.transform = 'scale(1)'; e.target.style.opacity = '1'; }}
      data-testid="inline-cta-button"
    >
      {trimmedLabel}
      <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
        <polyline points="15 3 21 3 21 9"/>
        <line x1="10" y1="14" x2="21" y2="3"/>
      </svg>
    </a>
  );
};

/**
 * Composant pour afficher un message avec liens cliquables et emojis
 * Affiche le nom de l'expéditeur au-dessus de chaque bulle
 * Couleurs: Violet (#8B5CF6) pour le Coach, Gris foncé pour les membres/IA
 */
const MessageBubble = ({ msg, isUser, onParticipantClick, isCommunity, currentUserId, profilePhotoUrl, onReservationClick }) => {
  // Convertir le texte en HTML avec liens cliquables ET emojis parsés
  const htmlContent = parseMessageContent(msg.text);
  const isOtherUser = isCommunity && msg.type === 'user' && msg.senderId && msg.senderId !== currentUserId;
  
  // === DÉTECTION AUTOMATIQUE DES MÉDIAS DANS LE TEXTE ===
  const detectMediaInText = (text) => {
    if (!text) return null;
    const urlPattern = /https?:\/\/[^\s<>"{}|\\^`\[\]]+/g;
    const urls = text.match(urlPattern) || [];
    for (const url of urls) {
      if (isMediaUrl(url)) {
        return parseMediaUrl(url);
      }
    }
    return null;
  };
  
  const detectedMedia = detectMediaInText(msg.text);
  
  // Déterminer si c'est un message du Coach HUMAIN (pas l'IA)
  const isCoachMessage = msg.type === 'coach' || msg.is_admin === true || msg.role === 'coach';
  
  // Message IA (assistant automatique - Coach Bassi)
  const isAIMessage = msg.type === 'ai';
  
  // Déterminer le nom à afficher
  const getDisplayName = () => {
    if (isCoachMessage) return 'Coach Bassi';
    if (isAIMessage) return 'Coach Bassi';
    return msg.sender || msg.senderName || 'Membre';
  };
  const displayName = getDisplayName();
  
  // Couleur du nom selon le type
  const getNameColor = () => {
    if (isCoachMessage) return '#FBBF24'; // Jaune/Or pour Coach
    if (isAIMessage) return '#A78BFA';    // Violet clair pour IA
    return '#22D3EE';                      // Cyan pour membres
  };
  
  // Couleur de la bulle selon le type
  const getBubbleBackground = () => {
    if (isUser) {
      // Messages envoyés par l'utilisateur actuel (à droite)
      return 'linear-gradient(135deg, #d91cd2, #8b5cf6)';
    }
    if (isCoachMessage) {
      // Messages du Coach HUMAIN: Violet solide
      return '#8B5CF6';
    }
    // Messages IA et autres membres: Gris foncé
    return '#2D2D2D';
  };
  
  // Récupérer l'avatar (photo ou initiale)
  const getAvatar = () => {
    // Si c'est un message de l'utilisateur actuel avec une photo
    if (isUser && profilePhotoUrl) {
      return (
        <img 
          src={profilePhotoUrl} 
          alt="avatar"
          style={{
            width: '24px',
            height: '24px',
            borderRadius: '50%',
            objectFit: 'cover',
            border: '1px solid rgba(255,255,255,0.2)'
          }}
        />
      );
    }
    // Avatar par défaut (initiale)
    if (msg.senderPhotoUrl) {
      return (
        <img 
          src={msg.senderPhotoUrl} 
          alt="avatar"
          style={{
            width: '24px',
            height: '24px',
            borderRadius: '50%',
            objectFit: 'cover',
            border: '1px solid rgba(255,255,255,0.2)'
          }}
        />
      );
    }
    return null;
  };
  
  // === DÉTECTION MÉDIA AVEC CTA ===
  // Si le message contient un média (media_url) et/ou un CTA - BLINDAGE
  const hasMedia = msg?.media_url && typeof msg.media_url === 'string' && msg.media_url.startsWith('http');
  const hasCta = msg?.cta_type && msg?.cta_text;
  
  // Si c'est un message média avec CTA, utiliser MediaMessage
  if (hasMedia || hasCta) {
    const ctaConfig = hasCta ? {
      type: msg.cta_type === 'reserver' ? 'RESERVER' : 
            msg.cta_type === 'offre' ? 'OFFRE' : 'PERSONNALISE',
      text: msg.cta_text,
      url: msg.cta_link || '#'
    } : null;
    
    return (
      <div
        style={{
          alignSelf: isUser ? 'flex-end' : 'flex-start',
          maxWidth: '320px',
          display: 'flex',
          flexDirection: 'column',
          gap: '4px'
        }}
      >
        {/* Nom au-dessus si pas utilisateur */}
        {!isUser && (
          <div style={{
            fontSize: '10px',
            fontWeight: '600',
            marginLeft: '4px',
            color: getNameColor()
          }}>
            {displayName}
          </div>
        )}
        
        {/* Composant MediaMessage avec CTA */}
        <MediaMessage
          mediaUrl={hasMedia ? msg.media_url : null}
          description={msg.text}
          cta={ctaConfig}
          onReservationClick={onReservationClick}
          isCompact={true}
        />
      </div>
    );
  }
  
  // === MESSAGE STANDARD (sans média) ===
  
  return (
    <div
      style={{
        alignSelf: isUser ? 'flex-end' : 'flex-start',
        maxWidth: '85%',
        display: 'flex',
        flexDirection: isUser ? 'row-reverse' : 'row',
        gap: '8px',
        alignItems: 'flex-end'
      }}
    >
      {/* Avatar rond si disponible */}
      {getAvatar()}
      
      <div style={{ flex: 1 }}>
        {/* NOM AU-DESSUS DE LA BULLE - Toujours visible pour les messages reçus */}
        {!isUser && (
          <div
            style={{
              fontSize: '10px',
              fontWeight: '600',
              marginBottom: '3px',
              marginLeft: '4px',
              color: getNameColor(),
              letterSpacing: '0.3px',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            {isOtherUser && onParticipantClick ? (
              <button
                onClick={() => onParticipantClick(msg.senderId, msg.sender)}
                style={{
                  fontSize: '10px',
                  fontWeight: '600',
                  background: 'none',
                  border: 'none',
                  color: '#22D3EE',
                  cursor: 'pointer',
                  padding: 0,
                  textDecoration: 'underline',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
                title="Cliquer pour envoyer un message privé"
              >
                {/* Icône DM */}
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                {displayName}
              </button>
            ) : (
              displayName
            )}
          </div>
        )}
        
        <div
          style={{
            background: getBubbleBackground(),
            color: '#fff',
            padding: '10px 14px',
            borderRadius: isUser 
              ? '16px 16px 4px 16px' 
              : '16px 16px 16px 4px',
            fontSize: '13px',
            lineHeight: '1.4',
            border: isCoachMessage && !isUser ? '1px solid rgba(251, 191, 36, 0.4)' : 'none'
          }}
        >
          {/* Rendu du texte avec liens cliquables */}
          <span 
            dangerouslySetInnerHTML={{ __html: htmlContent }}
            style={{ wordBreak: 'break-word' }}
          />
        </div>
        
        {/* === MÉDIA INLINE DÉTECTÉ AUTOMATIQUEMENT === */}
        {detectedMedia && detectedMedia.type === 'youtube' && (
          <InlineYouTubePlayer videoId={detectedMedia.videoId} thumbnailUrl={detectedMedia.thumbnailUrl} />
        )}
        {detectedMedia && detectedMedia.type === 'drive' && (
          <InlineDriveImage directUrl={detectedMedia.directUrl} previewUrl={detectedMedia.previewUrl} />
        )}
        {detectedMedia && detectedMedia.type === 'image' && (
          <InlineImage src={detectedMedia.directUrl} />
        )}
        
        {/* === BOUTON CTA SI PRÉSENT === */}
        {(msg.cta_text && msg.cta_link) && (
          <InlineCtaButton label={msg.cta_text} url={msg.cta_link} />
        )}
        
        {/* Horodatage sous la bulle - visible et clair */}
        {msg.created_at && (
          <div style={{
            fontSize: '10px',
            color: '#999',
            marginTop: '4px',
            textAlign: isUser ? 'right' : 'left',
            fontWeight: '400'
          }}>
            {formatMessageTime(msg.created_at)}
          </div>
        )}
      </div>
    </div>
  );
};

// === OPTIMISATION: memo pour éviter les re-rendus inutiles ===
// Compare uniquement les props critiques: ID du message et URLs d'avatar
const MemoizedMessageBubble = memo(MessageBubble, (prevProps, nextProps) => {
  // Si l'ID change, on doit re-rendre
  if (prevProps.msg.id !== nextProps.msg.id) return false;
  
  // Si l'avatar change (utilisateur a uploadé une nouvelle photo), on doit re-rendre
  if (prevProps.msg.senderPhotoUrl !== nextProps.msg.senderPhotoUrl) return false;
  if (prevProps.profilePhotoUrl !== nextProps.profilePhotoUrl) return false;
  
  // Sinon, pas besoin de re-rendre (même message, même avatar)
  return true;
});

/**
 * Widget de chat IA flottant avec reconnaissance automatique et historique
 * Utilise l'API /api/chat/smart-entry pour identifier les utilisateurs
 */
export const ChatWidget = () => {
  // === VÉRIFICATION DU PROFIL ABONNÉ (afroboost_profile) ===
  const getStoredProfile = () => {
    try {
      const savedProfile = localStorage.getItem(AFROBOOST_PROFILE_KEY);
      if (savedProfile) {
        const profile = JSON.parse(savedProfile);
        if (profile && profile.code && profile.name) {
          return profile;
        }
      }
    } catch (e) {
      console.warn('[PROFILE] Erreur lecture profil:', e.message);
    }
    return null;
  };

  // === CACHE HYBRIDE: Chargement instantané via sessionStorage ===
  // Stocke les 20 derniers messages pour affichage immédiat (0ms)
  const getCachedMessages = () => {
    try {
      const cached = sessionStorage.getItem(MESSAGE_CACHE_KEY);
      if (cached) {
        const messages = JSON.parse(cached);
        if (Array.isArray(messages) && messages.length > 0) {
          console.log('[CACHE] Messages cachés trouvés:', messages.length);
          return messages;
        }
      }
    } catch (e) {
      console.warn('[CACHE] Erreur lecture cache:', e.message);
    }
    return [];
  };

  const saveCachedMessages = (messages) => {
    try {
      // Stocker les 20 derniers messages uniquement
      const toCache = messages.slice(-20);
      sessionStorage.setItem(MESSAGE_CACHE_KEY, JSON.stringify(toCache));
      console.log('[CACHE] 💾 Messages mis en cache:', toCache.length);
    } catch (e) {
      console.warn('[CACHE] Erreur écriture cache:', e.message);
    }
  };

  // === VÉRIFICATION PERSISTANCE AU MONTAGE (AVANT tout render) ===
  // Déterminer le step initial IMMÉDIATEMENT basé sur localStorage
  // AVEC FALLBACK ROBUSTE pour données corrompues
  // === ZERO-FLASH: Vérifie aussi ?group=ID pour adhésion instantanée ===
  const [pendingGroupJoin, setPendingGroupJoin] = useState(() => {
    // Détecter le paramètre ?group=ID AVANT le premier render
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const groupId = urlParams.get('group');
      if (groupId) {
        console.log('[ZERO-FLASH] 🚀 Paramètre group détecté:', groupId);
        return groupId;
      }
    } catch (e) {
      console.warn('[ZERO-FLASH] Erreur lecture URL:', e.message);
    }
    return null;
  });
  
  const getInitialStep = () => {
    try {
      // PRIORITÉ 1: Vérifier si c'est un abonné identifié (afroboost_profile)
      const profile = getStoredProfile();
      
      // ZERO-FLASH: Si profil existe ET ?group=ID -> direct au chat (pas de formulaire)
      const urlParams = new URLSearchParams(window.location.search);
      const groupId = urlParams.get('group');
      
      if (profile && groupId) {
        console.log('[ZERO-FLASH] Abonné reconnu + lien groupe -> DIRECT chat');
        return 'chat'; // Adhésion instantanée, formulaire JAMAIS affiché
      }
      
      if (profile) {
        console.log('[PERSISTENCE] Abonné reconnu:', profile.name, '- Code:', profile.code);
        return 'chat'; // Abonné -> DIRECT au chat en mode plein écran
      }
      
      const savedIdentity = localStorage.getItem(AFROBOOST_IDENTITY_KEY);
      const savedClient = localStorage.getItem(CHAT_CLIENT_KEY);
      
      if (savedIdentity || savedClient) {
        const rawData = savedIdentity || savedClient;
        
        // Vérification de la validité JSON
        if (!rawData || rawData === 'undefined' || rawData === 'null') {
          throw new Error('Données localStorage invalides');
        }
        
        const data = JSON.parse(rawData);
        
        // Vérification des données minimales requises
        if (data && typeof data === 'object' && data.firstName && typeof data.firstName === 'string' && data.firstName.trim()) {
          console.log('[PERSISTENCE] Utilisateur reconnu:', data.firstName);
          return 'chat'; // Utilisateur déjà identifié -> DIRECT au chat
        } else {
          throw new Error('Données utilisateur incomplètes');
        }
      }
    } catch (e) {
      // FALLBACK: Nettoyer les données corrompues et rediriger vers le formulaire
      console.warn('[PERSISTENCE] Données corrompues détectées, nettoyage...', e.message);
      try {
        localStorage.removeItem(AFROBOOST_IDENTITY_KEY);
        localStorage.removeItem(CHAT_CLIENT_KEY);
        localStorage.removeItem(CHAT_SESSION_KEY);
        localStorage.removeItem(AFROBOOST_PROFILE_KEY);
      } catch (cleanupError) {
        console.error('[PERSISTENCE] Erreur lors du nettoyage localStorage:', cleanupError);
      }
    }
    return 'form'; // Nouvel utilisateur ou données corrompues -> formulaire
  };
  
  // === DÉTERMINER SI MODE PLEIN ÉCRAN INITIAL (Abonné = plein écran OU lien groupe) ===
  const getInitialFullscreen = () => {
    const profile = getStoredProfile();
    // Si profil + lien groupe -> plein écran immédiat
    const urlParams = new URLSearchParams(window.location.search);
    const groupId = urlParams.get('group');
    return !!profile || (!!profile && !!groupId);
  };
  
  // === OUVRIR LE CHAT AUTOMATIQUEMENT SI LIEN GROUPE ===
  const getInitialOpen = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const groupId = urlParams.get('group');
    const profile = getStoredProfile();
    // Si lien groupe + profil -> ouvrir immédiatement
    if (groupId && profile) {
      console.log('[ZERO-FLASH] 🚀 Chat ouvert automatiquement');
      return true;
    }
    return false;
  };

  const [isOpen, setIsOpen] = useState(getInitialOpen); // ZERO-FLASH: Ouvrir si lien groupe
  const [step, setStep] = useState(getInitialStep); // Initialisation DYNAMIQUE
  const [leadData, setLeadData] = useState(() => {
    // Charger les données du localStorage IMMÉDIATEMENT
    try {
      const savedIdentity = localStorage.getItem(AFROBOOST_IDENTITY_KEY);
      const savedClient = localStorage.getItem(CHAT_CLIENT_KEY);
      if (savedIdentity || savedClient) {
        const data = JSON.parse(savedIdentity || savedClient);
        if (data && data.firstName) {
          return {
            firstName: data.firstName || '',
            email: data.email || '',
            whatsapp: data.whatsapp || ''
          };
        }
      }
    } catch (e) {}
    return { firstName: '', whatsapp: '', email: '' };
  });
  
  // === CACHE HYBRIDE: Initialiser avec les messages cachés pour affichage instantané ===
  const [messages, setMessages] = useState(() => getCachedMessages());
  const [isLoadingHistory, setIsLoadingHistory] = useState(true); // État skeleton
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isReturningClient, setIsReturningClient] = useState(() => {
    // Déterminer si c'est un client de retour IMMÉDIATEMENT
    try {
      const savedIdentity = localStorage.getItem(AFROBOOST_IDENTITY_KEY);
      const savedClient = localStorage.getItem(CHAT_CLIENT_KEY);
      return !!(savedIdentity || savedClient);
    } catch (e) {}
    return false;
  });
  const [sessionData, setSessionData] = useState(() => {
    // Charger la session depuis localStorage IMMÉDIATEMENT
    try {
      const savedSession = localStorage.getItem(CHAT_SESSION_KEY);
      if (savedSession) {
        return JSON.parse(savedSession);
      }
    } catch (e) {}
    return null;
  });
  const [participantId, setParticipantId] = useState(() => {
    try {
      const savedIdentity = localStorage.getItem(AFROBOOST_IDENTITY_KEY);
      const savedClient = localStorage.getItem(CHAT_CLIENT_KEY);
      if (savedIdentity || savedClient) {
        const data = JSON.parse(savedIdentity || savedClient);
        return data?.participantId || null;
      }
    } catch (e) {}
    return null;
  });
  const [showMenu, setShowMenu] = useState(false);
  const [isCommunityMode, setIsCommunityMode] = useState(false);
  const [lastMessageCount, setLastMessageCount] = useState(0);
  const [privateChatTarget, setPrivateChatTarget] = useState(null);
  const [messageCount, setMessageCount] = useState(0); // Compteur de messages pour prompt notif
  const [pushEnabled, setPushEnabled] = useState(false);
  const [isCoachMode, setIsCoachMode] = useState(() => {
    // Vérifier si c'est le coach IMMÉDIATEMENT
    try {
      const savedIdentity = localStorage.getItem(AFROBOOST_IDENTITY_KEY);
      const savedClient = localStorage.getItem(CHAT_CLIENT_KEY);
      if (savedIdentity || savedClient) {
        const data = JSON.parse(savedIdentity || savedClient);
        return data?.email?.toLowerCase() === 'contact.artboost@gmail.com';
      }
    } catch (e) {}
    return false;
  });
  const [coachSessions, setCoachSessions] = useState([]); // Liste des sessions pour le coach
  const [selectedCoachSession, setSelectedCoachSession] = useState(null); // Session sélectionnée par le coach
  const [isFullscreen, setIsFullscreen] = useState(getInitialFullscreen); // Mode plein écran (ABONNÉ = activé)
  const [showEmojiPicker, setShowEmojiPicker] = useState(false); // Sélecteur d'emojis (composant EmojiPicker)
  
  // === FORMULAIRE ABONNÉ (4 champs: Nom, WhatsApp, Email, Code Promo) ===
  const [showSubscriberForm, setShowSubscriberForm] = useState(false); // Afficher le formulaire abonné
  const [subscriberFormData, setSubscriberFormData] = useState({ name: '', whatsapp: '', email: '', code: '' });
  const [validatingCode, setValidatingCode] = useState(false); // Loading pendant validation du code
  
  // === PROFIL ABONNÉ VALIDÉ (afroboost_profile) ===
  const [afroboostProfile, setAfroboostProfile] = useState(getStoredProfile);
  const [profilePhoto, setProfilePhoto] = useState(() => {
    try {
      const profile = getStoredProfile();
      return profile?.photoUrl || null;
    } catch { return null; }
  });
  const [uploadingPhoto, setUploadingPhoto] = useState(false);
  
  // === MODALE RECADRAGE PHOTO ===
  const [showCropModal, setShowCropModal] = useState(false);
  const [cropImageSrc, setCropImageSrc] = useState(null);
  const [cropPosition, setCropPosition] = useState({ x: 0, y: 0, scale: 1 });
  const cropCanvasRef = useRef(null);
  
  // === MENU UTILISATEUR (Partage + Mode Visiteur) ===
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showCoachMenu, setShowCoachMenu] = useState(false); // Menu coach minimaliste
  const [linkCopied, setLinkCopied] = useState(false);
  const [isVisitorMode, setIsVisitorMode] = useState(false); // Mode visiteur (chat réduit mais profil conservé)
  const [isVisitorPreview, setIsVisitorPreview] = useState(false); // Admin: aperçu mode visiteur
  const [showiOSPrompt, setShowiOSPrompt] = useState(false); // Message iOS pour PWA
  const [isLoggingOut, setIsLoggingOut] = useState(false); // Etat de deconnexion en cours
  
  // === PRÉFÉRENCES SONORES (persistées dans localStorage via SoundManager) ===
  const [soundEnabled, setSoundEnabledState] = useState(() => {
    try {
      const saved = localStorage.getItem('afroboost_sound_enabled');
      return saved !== null ? saved === 'true' : true;
    } catch { return true; }
  });
  
  const [silenceAutoEnabled, setSilenceAutoEnabledState] = useState(() => {
    try {
      const saved = localStorage.getItem('afroboost_silence_auto');
      return saved === 'true';
    } catch { return false; }
  });
  
  // Toggle le mode Silence Auto (utilise SoundManager)
  const toggleSilenceAuto = () => {
    const newValue = !silenceAutoEnabled;
    setSilenceAutoEnabledState(newValue);
    localStorage.setItem('afroboost_silence_auto', String(newValue));
    console.log('[SILENCE AUTO] 🌙', newValue ? `Activé (${getSilenceHoursLabel()})` : 'Désactivé');
  };
  
  // Toggle les sons (utilise SoundManager)
  const toggleSound = () => {
    const newValue = !soundEnabled;
    setSoundEnabledState(newValue);
    localStorage.setItem('afroboost_sound_enabled', String(newValue));
    console.log('[SOUND] 🔊', newValue ? 'Activé' : 'Désactivé');
  };
  
  // === WRAPPER SIMPLIFIÉ (délègue à SoundManager) ===
  const playSoundIfEnabled = useCallback((type = SOUND_TYPES.MESSAGE) => {
    playSoundIfAllowed(type, soundEnabled, silenceAutoEnabled);
  }, [soundEnabled, silenceAutoEnabled]);
  
  // Fonction pour copier le lien du site
  const handleShareLink = async () => {
    try {
      const shareUrl = window.location.origin;
      await navigator.clipboard.writeText(shareUrl);
      setLinkCopied(true);
      setTimeout(() => setLinkCopied(false), 2000);
      console.log('[SHARE] Lien copié:', shareUrl);
    } catch (err) {
      console.error('[SHARE] Erreur copie:', err);
      // Fallback pour navigateurs sans clipboard API
      const textArea = document.createElement('textarea');
      textArea.value = window.location.origin;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setLinkCopied(true);
      setTimeout(() => setLinkCopied(false), 2000);
    }
    setShowUserMenu(false);
  };
  
  // Fonction pour passer en mode visiteur (réduit le chat sans effacer le profil)
  const handleVisitorMode = () => {
    setIsFullscreen(false);
    setIsVisitorMode(true);
    setShowUserMenu(false);
    setShowReservationPanel(false);
    console.log('[MODE] Mode visiteur activé (profil conservé)');
  };
  
  // Fonction pour réactiver le mode abonné
  const handleReactivateSubscriber = () => {
    if (afroboostProfile?.code) {
      setIsFullscreen(true);
      setIsVisitorMode(false);
      console.log('[MODE] Mode abonné réactivé');
    }
  };
  
  // === FONCTION DE DÉCONNEXION STRICTE (HARD RESET) ===
  const handleLogout = async () => {
    if (isLoggingOut) return; // Eviter double clic
    setIsLoggingOut(true);
    
    // Timeout de securite: force redirect apres 3s
    const forceRedirect = setTimeout(() => window.location.replace('/'), 3000);
    
    try {
      // 1. Desabonner des notifications push (garde la PWA installee)
      if ('serviceWorker' in navigator) {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();
        if (subscription) await subscription.unsubscribe();
      }
      
      // 2. Vider les caches
      if ('caches' in window) {
        const cacheNames = await caches.keys();
        await Promise.all(cacheNames.map(name => caches.delete(name)));
      }
      
      // 3. Nettoyer le stockage
      localStorage.clear();
      sessionStorage.clear();
      
      // 4. Reinitialiser les etats
      setSessionData(null);
      setParticipantId(null);
      setMessages([]);
      setAfroboostProfile(null);
      setStep('welcome');
      
      clearTimeout(forceRedirect);
    } catch (err) {
      console.error('[LOGOUT] Erreur:', err);
      localStorage.clear();
      sessionStorage.clear();
    }
    window.location.replace('/');
  };
  
  // === OUVRIR UN DM (Message Privé) ===
  const openDirectMessage = async (memberId, memberName) => {
    if (!participantId) return;
    
    try {
      console.log('[DM] 📩 Ouverture DM avec:', memberName);
      
      // Créer ou récupérer la conversation privée
      const res = await axios.post(`${API}/private/conversations`, {
        participant_1_id: participantId,
        participant_1_name: afroboostProfile?.name || leadData?.firstName || 'Moi',
        participant_2_id: memberId,
        participant_2_name: memberName
      });
      
      const conversation = res.data;
      setActivePrivateChat(conversation);
      
      // Charger les messages existants
      const messagesRes = await axios.get(`${API}/private/messages/${conversation.id}`);
      setPrivateMessages(messagesRes.data || []);
      
      // Rejoindre la room Socket.IO pour les mises à jour temps réel
      if (socketRef.current) {
        socketRef.current.emit('join_private_conversation', {
          conversation_id: conversation.id,
          participant_id: participantId
        });
      }
      
      // Marquer comme lu
      await axios.put(`${API}/private/messages/read/${conversation.id}?reader_id=${participantId}`);
      
      // Persister la conversation active pour F5
      localStorage.setItem('afroboost_active_dm', JSON.stringify(conversation));
      
      console.log('[DM] Conversation ouverte:', conversation.id);
    } catch (err) {
      console.error('[DM] Erreur ouverture DM:', err);
    }
  };
  
  // === FERMER LE DM ===
  const closeDirectMessage = () => {
    if (activePrivateChat && socketRef.current) {
      socketRef.current.emit('leave_private_conversation', {
        conversation_id: activePrivateChat.id
      });
    }
    setActivePrivateChat(null);
    setPrivateMessages([]);
    setPrivateInput('');
    localStorage.removeItem('afroboost_active_dm');
    console.log('[DM] 📭 DM fermé');
  };
  
  // === ENVOYER UN MESSAGE PRIVÉ ===
  const sendPrivateMessage = async () => {
    if (!privateInput.trim() || !activePrivateChat) return;
    
    try {
      const recipientId = activePrivateChat.participant_1_id === participantId 
        ? activePrivateChat.participant_2_id 
        : activePrivateChat.participant_1_id;
      const recipientName = activePrivateChat.participant_1_id === participantId
        ? activePrivateChat.participant_2_name
        : activePrivateChat.participant_1_name;
      
      const res = await axios.post(`${API}/private/messages`, {
        conversation_id: activePrivateChat.id,
        sender_id: participantId,
        sender_name: afroboostProfile?.name || leadData?.firstName || 'Moi',
        recipient_id: recipientId,
        recipient_name: recipientName,
        content: privateInput.trim()
      });
      
      // Ajouter le message localement
      setPrivateMessages(prev => [...prev, res.data]);
      setPrivateInput('');
      
      console.log('[DM] Message envoyé');
    } catch (err) {
      console.error('[DM] Erreur envoi message:', err);
    }
  };
  
  // === COMPRESSION IMAGE CÔTÉ CLIENT ===
  const compressImage = (file, maxWidth = 200, maxHeight = 200, quality = 0.8) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          // Calculer les nouvelles dimensions
          let { width, height } = img;
          if (width > maxWidth || height > maxHeight) {
            const ratio = Math.min(maxWidth / width, maxHeight / height);
            width = Math.round(width * ratio);
            height = Math.round(height * ratio);
          }
          
          // Créer le canvas pour la compression
          const canvas = document.createElement('canvas');
          canvas.width = width;
          canvas.height = height;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0, width, height);
          
          // Convertir en blob compressé
          canvas.toBlob(
            (blob) => {
              if (blob) {
                resolve(new File([blob], file.name, { type: 'image/jpeg' }));
              } else {
                reject(new Error('Compression échouée'));
              }
            },
            'image/jpeg',
            quality
          );
        };
        img.onerror = reject;
        img.src = e.target.result;
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };
  
  // === OUVRIR MODALE DE RECADRAGE ===
  const handlePhotoSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
      alert('Veuillez sélectionner une image');
      return;
    }
    
    // Lire l'image et ouvrir la modale de recadrage
    const reader = new FileReader();
    reader.onload = (event) => {
      setCropImageSrc(event.target.result);
      setCropPosition({ x: 0, y: 0, scale: 1 });
      setShowCropModal(true);
    };
    reader.readAsDataURL(file);
  };
  
  // === RECADRER ET UPLOADER LA PHOTO ===
  const handleCropAndUpload = async () => {
    if (!cropImageSrc) return;
    
    setUploadingPhoto(true);
    setShowCropModal(false);
    
    try {
      // Créer le canvas de recadrage circulaire
      const canvas = document.createElement('canvas');
      const size = 200;
      canvas.width = size;
      canvas.height = size;
      const ctx = canvas.getContext('2d');
      
      // Charger l'image
      const img = new Image();
      await new Promise((resolve, reject) => {
        img.onload = resolve;
        img.onerror = reject;
        img.src = cropImageSrc;
      });
      
      // Calculer les dimensions de recadrage
      const minDim = Math.min(img.width, img.height);
      const scale = cropPosition.scale;
      const cropSize = minDim / scale;
      const offsetX = ((img.width - cropSize) / 2) + (cropPosition.x * img.width / 200);
      const offsetY = ((img.height - cropSize) / 2) + (cropPosition.y * img.height / 200);
      
      // Dessiner l'image recadrée dans un cercle
      ctx.beginPath();
      ctx.arc(size/2, size/2, size/2, 0, Math.PI * 2);
      ctx.closePath();
      ctx.clip();
      
      ctx.drawImage(
        img, 
        Math.max(0, offsetX), 
        Math.max(0, offsetY), 
        cropSize, 
        cropSize,
        0, 0, size, size
      );
      
      // Convertir en blob
      const blob = await new Promise((resolve) => {
        canvas.toBlob(resolve, 'image/jpeg', 0.85);
      });
      
      const compressedFile = new File([blob], 'profile.jpg', { type: 'image/jpeg' });
      console.log('[PHOTO] Recadrage terminé:', Math.round(compressedFile.size / 1024), 'KB');
      
      // Upload vers le NOUVEAU endpoint qui sauvegarde en DB
      const formData = new FormData();
      formData.append('file', compressedFile);
      formData.append('participant_id', participantId || 'guest');
      
      const res = await axios.post(`${API}/users/upload-photo`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      if (res.data?.success && res.data?.url) {
        const photoUrl = res.data.url;
        setProfilePhoto(photoUrl);
        
        // === MISE À JOUR DU PROFIL LOCAL (sync avec DB) ===
        const profile = getStoredProfile() || {};
        profile.photoUrl = photoUrl;
        localStorage.setItem(AFROBOOST_PROFILE_KEY, JSON.stringify(profile));
        setAfroboostProfile(profile);
        
        // === ÉMETTRE LA MISE À JOUR D'AVATAR EN TEMPS RÉEL ===
        emitAvatarUpdate(photoUrl);
        
        console.log('[PHOTO] Photo uploadée et sauvegardée en DB:', photoUrl, res.data.db_updated);
      }
    } catch (err) {
      console.error('[PHOTO] Erreur:', err);
      alert('Erreur lors de l\'upload');
    } finally {
      setUploadingPhoto(false);
      setCropImageSrc(null);
    }
  };
  
  // === UPLOAD PHOTO DE PROFIL (legacy - rediriger vers crop) ===
  const handlePhotoUpload = async (e) => {
    handlePhotoSelect(e);
  };
  
  // === RESTAURER DM ACTIVE APRÈS F5 ===
  useEffect(() => {
    const savedDM = localStorage.getItem('afroboost_active_dm');
    if (savedDM && participantId) {
      try {
        const conversation = JSON.parse(savedDM);
        openDirectMessage(
          conversation.participant_1_id === participantId 
            ? conversation.participant_2_id 
            : conversation.participant_1_id,
          conversation.participant_1_id === participantId
            ? conversation.participant_2_name
            : conversation.participant_1_name
        );
      } catch (e) {}
    }
  }, [participantId]);
  
  // === INDICATEUR DE SAISIE (Typing Indicator) ===
  const [typingUser, setTypingUser] = useState(null); // Qui est en train d'écrire
  const typingTimeoutRef = useRef(null); // Timer pour cacher l'indicateur après 3s
  const lastTypingEmitRef = useRef(0); // Éviter le spam d'événements typing
  
  // === MESSAGERIE PRIVÉE (MP) ===
  const [privateChats, setPrivateChats] = useState([]); // Liste des conversations MP actives
  const [activePrivateChat, setActivePrivateChat] = useState(null); // MP actuellement ouverte
  const [privateMessages, setPrivateMessages] = useState([]); // Messages de la MP active
  const [privateInput, setPrivateInput] = useState(''); // Input de la MP
  const [unreadPrivateCount, setUnreadPrivateCount] = useState(0); // Compteur MP non lus (pastille rouge)
  const [dmTypingUser, setDmTypingUser] = useState(null); // Indicateur "en train d'écrire" pour DM
  const dmTypingTimeoutRef = useRef(null); // Timer pour cacher l'indicateur DM après 3s
  const lastDmTypingEmitRef = useRef(0); // Éviter le spam d'événements DM typing
  const messagesEndRef = useRef(null);
  const socketRef = useRef(null); // Référence Socket.IO
  const chatContainerRef = useRef(null); // Ref pour le mode plein écran
  
  // === SUBSCRIBER DATA (Mémorisation code promo) ===
  const [subscriberData, setSubscriberData] = useState(() => {
    try {
      const saved = localStorage.getItem('subscriber_data');
      return saved ? JSON.parse(saved) : null;
    } catch { return null; }
  });
  const [showReservationPanel, setShowReservationPanel] = useState(false);
  const [availableCourses, setAvailableCourses] = useState([]); // Cours pour réservation
  const [loadingCourses, setLoadingCourses] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState(null); // Cours sélectionné
  const [reservationLoading, setReservationLoading] = useState(false); // Chargement réservation
  const [reservationError, setReservationError] = useState(''); // Erreur réservation
  const [reservationEligibility, setReservationEligibility] = useState(null); // Éligibilité code

  // === VÉRIFICATION ÉLIGIBILITÉ RÉSERVATION ===
  const checkReservationEligibility = useCallback(async () => {
    if (!afroboostProfile?.code || !afroboostProfile?.email) {
      setReservationEligibility({ canReserve: false, reason: "Profil incomplet" });
      return false;
    }
    
    try {
      const response = await fetch(`${API}/check-reservation-eligibility`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: afroboostProfile.code,
          email: afroboostProfile.email
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setReservationEligibility(data);
        return data.canReserve;
      }
      return false;
    } catch (err) {
      console.error('[ELIGIBILITY] Erreur:', err);
      setReservationEligibility({ canReserve: false, reason: "Erreur de vérification" });
      return false;
    }
  }, [afroboostProfile?.code, afroboostProfile?.email]);

  // === HANDLER CLIC BOUTON RÉSERVATION ===
  const handleReservationClick = useCallback(async () => {
    // BLINDAGE: Bloquer en mode Vue Visiteur
    if (isVisitorPreview) {
      console.log('[ADMIN] Réservation bloquée en mode Vue Visiteur');
      return;
    }
    
    if (showReservationPanel) {
      // Fermer le panel
      setShowReservationPanel(false);
      setSelectedCourse(null);
      return;
    }
    
    // Vérifier l'éligibilité avant d'ouvrir
    const canReserve = await checkReservationEligibility();
    
    if (!canReserve) {
      const reason = reservationEligibility?.reason || "Code invalide";
      setReservationError(`${reason}. Réservation impossible.`);
      // Afficher l'erreur pendant 5 secondes
      setTimeout(() => setReservationError(''), 5000);
      return;
    }
    
    // Charger les cours et ouvrir
    loadAvailableCourses();
    setShowReservationPanel(true);
    setSelectedCourse(null);
  }, [showReservationPanel, checkReservationEligibility, reservationEligibility, isVisitorPreview]);

  // === HANDLER CONFIRMATION RÉSERVATION (extrait pour BookingPanel) ===
  const handleConfirmReservation = useCallback(async () => {
    if (!selectedCourse || !afroboostProfile) return;
    
    // Reset error state
    setReservationError('');
    setReservationLoading(true);
    
    // Utiliser les données du profil abonné (afroboostProfile)
    const reservationData = {
      userName: afroboostProfile?.name?.trim() || leadData?.firstName?.trim() || 'Abonné',
      userEmail: (afroboostProfile?.email || leadData?.email || '').trim(),
      userWhatsapp: (afroboostProfile?.whatsapp || leadData?.whatsapp || '').trim(),
      userId: participantId || `guest-${Date.now()}`, // ID utilisateur requis
      courseId: selectedCourse.id,
      courseName: selectedCourse.name,
      courseTime: selectedCourse.time,
      datetime: new Date().toISOString(),
      promoCode: (afroboostProfile?.code || '').trim().toUpperCase(),
      source: 'chat_widget_abonne',
      type: 'abonné',
      offerId: selectedCourse.id,
      offerName: selectedCourse.name,
      price: selectedCourse.price || 0,
      totalPrice: selectedCourse.price || 0
    };
    
    // LOG pour debug
    console.log('[RESERVATION] 📤 Envoi des données:', JSON.stringify(reservationData, null, 2));
    
    try {
      const res = await axios.post(`${API}/reservations`, reservationData);
      console.log('[RESERVATION] Réponse serveur:', res.data);
      
      if (res.data) {
        // Succès : fermer le panneau et afficher message
        setShowReservationPanel(false);
        setSelectedCourse(null);
        setReservationError('');
        
        // Message de confirmation dans le chat
        const confirmMsg = {
          type: 'ai',
          text: `Réservation confirmée !\n${selectedCourse.name}\n${selectedCourse.time}\nCode: ${afroboostProfile?.code || 'N/A'}\n${reservationData.userName}`,
          sender: 'Coach Bassi'
        };
        setMessages(prev => [...prev, confirmMsg]);
      }
    } catch (err) {
      console.error('[RESERVATION] Erreur:', err.response?.data || err.message);
      // Afficher l'erreur dans l'UI (pas alert)
      const errorMsg = err.response?.data?.detail || err.response?.data?.message || 'Erreur serveur, réessayez.';
      setReservationError(errorMsg);
    } finally {
      // TOUJOURS réactiver le bouton
      setReservationLoading(false);
    }
  }, [selectedCourse, afroboostProfile, leadData, participantId, setMessages]);

  // Email du coach autorisé
  const COACH_EMAIL = 'contact.artboost@gmail.com';
  
  // Sauvegarder subscriber_data quand un code promo est validé
  const saveSubscriberData = useCallback((code, name, type = 'abonné') => {
    const data = { code, name, type, savedAt: new Date().toISOString() };
    localStorage.setItem('subscriber_data', JSON.stringify(data));
    setSubscriberData(data);
    console.log('[SUBSCRIBER] Données abonné sauvegardées:', data);
  }, []);
  
  // === VALIDATION DU CODE PROMO ET ENREGISTREMENT PROFIL ABONNÉ ===
  const handleSubscriberFormSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    const { name, whatsapp, email, code } = subscriberFormData;
    
    // Validation des champs
    if (!name?.trim() || !whatsapp?.trim() || !email?.trim() || !code?.trim()) {
      setError('Tous les champs sont obligatoires');
      return;
    }
    
    setValidatingCode(true);
    
    try {
      // Valider le code promo via l'API
      const res = await axios.post(`${API}/discount-codes/validate`, {
        code: code.trim(),
        email: email.trim()
      });
      
      if (!res.data?.valid) {
        setError(res.data?.message || 'Code promo invalide');
        setValidatingCode(false);
        return;
      }
      
      // Code valide ! Sauvegarder le profil abonné
      const profile = {
        name: name.trim(),
        whatsapp: whatsapp.trim(),
        email: email.trim(),
        code: code.trim().toUpperCase(),
        codeDetails: res.data.code, // Détails du code (type, valeur, etc.)
        savedAt: new Date().toISOString()
      };
      
      localStorage.setItem(AFROBOOST_PROFILE_KEY, JSON.stringify(profile));
      setAfroboostProfile(profile);
      
      // Sauvegarder aussi dans subscriber_data pour compatibilité
      saveSubscriberData(profile.code, profile.name, 'abonné');
      
      // Mettre à jour leadData pour le chat
      setLeadData({ firstName: profile.name, whatsapp: profile.whatsapp, email: profile.email });
      
      console.log('[SUBSCRIBER] Profil abonné validé et sauvegardé:', profile.name);
      
      // Activer le mode plein écran et passer au chat
      setIsFullscreen(true);
      setShowSubscriberForm(false);
      
      // Démarrer le chat avec smart-entry
      await handleSmartEntry({ 
        firstName: profile.name, 
        whatsapp: profile.whatsapp, 
        email: profile.email 
      });
      
    } catch (err) {
      console.error('[SUBSCRIBER] Erreur validation:', err);
      setError(err.response?.data?.message || 'Erreur lors de la validation du code');
    } finally {
      setValidatingCode(false);
    }
  };
  
  // Charger les cours disponibles
  const loadAvailableCourses = useCallback(async () => {
    setLoadingCourses(true);
    try {
      const res = await axios.get(`${API}/courses`);
      const courses = res.data || [];
      setAvailableCourses(courses);
      console.log('[COURSES] Chargés:', courses.length);
    } catch (err) {
      console.error('[COURSES] Erreur:', err);
    }
    setLoadingCourses(false);
  }, []);

  // === CHARGER LA PHOTO DEPUIS LA DB (pas localStorage) ===
  // Se déclenche quand participantId est disponible
  useEffect(() => {
    const loadPhotoFromDB = async () => {
      if (!participantId) return;
      
      try {
        const res = await axios.get(`${API}/users/${participantId}/profile`);
        if (res.data?.success && res.data?.photo_url) {
          console.log('[PHOTO] Photo chargée depuis DB:', res.data.photo_url);
          setProfilePhoto(res.data.photo_url);
          
          // Synchroniser localStorage avec la DB
          const profile = getStoredProfile() || {};
          if (profile.photoUrl !== res.data.photo_url) {
            profile.photoUrl = res.data.photo_url;
            localStorage.setItem(AFROBOOST_PROFILE_KEY, JSON.stringify(profile));
            setAfroboostProfile(profile);
          }
        }
      } catch (err) {
        console.log('[PHOTO] ℹ️ Profil DB non trouvé, utilise localStorage');
      }
    };
    
    loadPhotoFromDB();
  }, [participantId]);

  // === FONCTIONS MODE PLEIN ÉCRAN (CSS - plus fiable) ===
  const toggleFullscreen = () => {
    setIsFullscreen(prev => !prev);
  };

  // Écouter les changements de fullscreen (touche Escape, etc.)
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  // === ECOUTEUR MODE VUE VISITEUR (Communication CoachDashboard -> ChatWidget) ===
  useEffect(() => {
    const handleVisitorPreviewToggle = (event) => {
      const newState = event.detail?.enabled;
      if (typeof newState === 'boolean') {
        setIsVisitorPreview(newState);
        console.log('[ADMIN] Vue Visiteur via Dashboard:', newState ? 'activee' : 'desactivee');
      }
    };
    
    window.addEventListener('afroboost:visitorPreview', handleVisitorPreviewToggle);
    return () => window.removeEventListener('afroboost:visitorPreview', handleVisitorPreviewToggle);
  }, []);

  // Enregistrer le Service Worker au montage
  useEffect(() => {
    if (isPushSupported()) {
      registerServiceWorker().then(() => {
        setPushEnabled(isSubscribed());
      });
    }
  }, []);

  // === ADHESION AUTOMATIQUE VIA LIEN ?group=ID (ZERO-FLASH) ===
  // Utilise pendingGroupJoin détecté AVANT le premier render
  // L'adhésion se fait silencieusement, le formulaire n'est JAMAIS affiché
  useEffect(() => {
    const executeAutoJoin = async () => {
      // Utiliser pendingGroupJoin détecté au montage
      if (!pendingGroupJoin) return;
      
      try {
        // Vérifier si l'utilisateur est déjà connecté
        const storedProfile = getStoredProfile();
        if (!storedProfile || !storedProfile.email) {
          console.log('[ZERO-FLASH] Utilisateur non connecté, formulaire requis');
          setPendingGroupJoin(null); // Reset
          return;
        }
        
        console.log('[ZERO-FLASH] 🚀 Adhésion instantanée au groupe:', pendingGroupJoin);
        
        // Appeler l'API pour rejoindre le groupe silencieusement
        const response = await axios.post(`${API}/groups/join`, {
          group_id: pendingGroupJoin,
          email: storedProfile.email,
          name: storedProfile.name,
          user_id: participantId || storedProfile.id
        });
        
        if (response.data.success) {
          console.log('[ZERO-FLASH] Groupe rejoint:', response.data.group_name || pendingGroupJoin);
          
          // Charger l'historique du groupe
          if (response.data.conversation_id) {
            try {
              const historyRes = await axios.get(`${API}/chat/sessions/${response.data.conversation_id}/messages`);
              if (historyRes.data && historyRes.data.length > 0) {
                const restoredMessages = historyRes.data.map(msg => ({
                  id: msg.id,
                  type: msg.sender_type === 'user' ? 'user' : msg.sender_type === 'coach' ? 'coach' : 'ai',
                  text: msg.content,
                  sender: msg.sender_name
                }));
                setMessages(restoredMessages);
              }
            } catch (histErr) {
              console.warn('[ZERO-FLASH] Historique non chargé:', histErr.message);
            }
          }
        }
        
        // Nettoyer l'URL (enlever ?group=ID) - fait une seule fois
        const cleanUrl = window.location.pathname;
        window.history.replaceState({}, '', cleanUrl);
        setPendingGroupJoin(null); // Reset après traitement
        
      } catch (err) {
        console.error('[ZERO-FLASH] Erreur adhésion:', err.response?.data?.detail || err.message);
        setPendingGroupJoin(null); // Reset même en cas d'erreur
      }
    };
    
    executeAutoJoin();
  }, [pendingGroupJoin, participantId]); // eslint-disable-line react-hooks/exhaustive-deps

  // === PERSISTANCE HISTORIQUE - Charger l'historique au montage si connecté ===
  useEffect(() => {
    const loadChatHistory = async () => {
      // Vérifier si l'utilisateur est connecté
      const storedProfile = getStoredProfile();
      const savedSession = sessionData || (() => {
        try {
          return JSON.parse(localStorage.getItem(CHAT_SESSION_KEY));
        } catch { return null; }
      })();
      
      if (!storedProfile && !savedSession?.id) {
        console.log('[HISTORY] Pas de session active, historique non chargé');
        setIsLoadingHistory(false); // Masquer skeleton
        return;
      }
      
      // Charger même si on a des messages en cache (pour mise à jour)
      if (step !== 'chat') {
        setIsLoadingHistory(false);
        return;
      }
      
      try {
        console.log('[HISTORY] 📜 Chargement de l\'historique depuis l\'API...');
        
        // Essayer de charger l'historique via smart-entry ou directement
        if (savedSession?.id) {
          const response = await axios.get(`${API}/chat/sessions/${savedSession.id}/messages`);
          if (response.data && response.data.length > 0) {
            const restoredMessages = response.data.map(msg => ({
              id: msg.id,
              type: msg.sender_type === 'user' ? 'user' : msg.sender_type === 'coach' ? 'coach' : 'ai',
              text: msg.content,
              sender: msg.sender_name
            }));
            setMessages(restoredMessages);
            setLastMessageCount(restoredMessages.length);
            // === CACHE HYBRIDE: Sauvegarder dans sessionStorage ===
            saveCachedMessages(restoredMessages);
            console.log('[HISTORY]', restoredMessages.length, 'messages restaurés et mis en cache');
          }
        }
      } catch (err) {
        console.warn('[HISTORY] Historique non disponible:', err.message);
      } finally {
        // Masquer le skeleton après le chargement (succès ou échec)
        setIsLoadingHistory(false);
      }
    };
    
    loadChatHistory();
  }, [step, sessionData]); // eslint-disable-line react-hooks/exhaustive-deps

  // === CACHE HYBRIDE: Mettre à jour le cache à chaque nouveau message ===
  useEffect(() => {
    if (messages.length > 0) {
      saveCachedMessages(messages);
    }
  }, [messages]);

  // Extraire le token de lien depuis l'URL si présent
  const getLinkTokenFromUrl = () => {
    const path = window.location.pathname;
    const match = path.match(/\/chat\/([a-zA-Z0-9-]+)/);
    return match ? match[1] : null;
  };

  // === SOCKET.IO CONNEXION ET GESTION TEMPS RÉEL ===
  useEffect(() => {
    // Connexion Socket.IO quand on a une session active
    if (sessionData?.id && step === 'chat' && !socketRef.current) {
      console.log('[SOCKET.IO] 🔌 Connexion WebSocket à', SOCKET_URL);
      
      const socket = io(SOCKET_URL, {
        transports: ['websocket'], // WEBSOCKET UNIQUEMENT - Zéro polling
        reconnection: true,
        reconnectionAttempts: 3,
        reconnectionDelay: 500,
        timeout: 5000,
        upgrade: false // Pas de fallback
      });
      
      socketRef.current = socket;
      
      socket.on('connect', () => {
        console.log('[SOCKET.IO] WebSocket connecté! Session:', sessionData.id);
        // Rejoindre la room de la session
        socket.emit('join_session', {
          session_id: sessionData.id,
          participant_id: participantId
        });
      });
      
      socket.on('joined_session', (data) => {
        console.log('[SOCKET.IO] Session rejointe:', data);
      });
      
      // Gestion erreur WebSocket
      socket.on('connect_error', (error) => {
        console.error('[SOCKET.IO] Erreur WebSocket:', error.message);
        // Tenter une reconnexion avec polling en dernier recours
        if (socket.io.opts.transports[0] === 'websocket') {
          console.log('[SOCKET.IO] Tentative fallback polling...');
          socket.io.opts.transports = ['polling', 'websocket'];
          socket.connect();
        }
      });
      
      // === RECONNEXION: Récupérer les messages manqués ===
      socket.on('reconnect', async (attemptNumber) => {
        console.log(`[SOCKET.IO] Reconnexion réussie (tentative ${attemptNumber})`);
        // Rejoindre à nouveau la session
        socket.emit('join_session', {
          session_id: sessionData.id,
          participant_id: participantId
        });
        // Récupérer les messages manqués pendant la déconnexion
        try {
          const response = await fetch(`${API}/chat/sessions/${sessionData.id}/messages`);
          if (response.ok) {
            const data = await response.json();
            if (data.messages && data.messages.length > 0) {
              console.log(`[SOCKET.IO] 📥 ${data.messages.length} messages récupérés après reconnexion`);
              setMessages(prev => {
                // Fusionner sans doublons
                const newMsgs = data.messages.filter(m => !prev.some(p => p.id === m.id));
                if (newMsgs.length > 0) {
                  return [...prev, ...newMsgs].sort((a, b) => 
                    new Date(a.created_at || 0) - new Date(b.created_at || 0)
                  );
                }
                return prev;
              });
            }
          }
        } catch (err) {
          console.warn('[SOCKET.IO] Erreur récupération messages:', err);
        }
      });
      
      // Écouter les nouveaux messages en temps réel
      socket.on('message_received', (messageData) => {
        console.log('[SOCKET.IO] Message recu:', messageData);
        setTypingUser(null);
        
        // Ne pas dupliquer nos propres messages
        if (messageData.senderId === participantId && messageData.type === 'user') return;
        
        // ANTI-DOUBLONS: Verifier ID avant d'ajouter
        setMessages(prev => {
          const msgId = messageData.id || messageData._id;
          if (!msgId || prev.some(m => m.id === msgId || m._id === msgId)) {
            console.log('[SOCKET.IO] Doublon ignore:', msgId);
            return prev;
          }
          return [...prev, {
            id: msgId, type: messageData.type, text: messageData.text || '',
            sender: messageData.sender || '', senderId: messageData.senderId || '',
            created_at: messageData.created_at || new Date().toISOString(),
            media_url: messageData.media_url || null, media_type: messageData.media_type || null,
            cta_type: messageData.cta_type || null, cta_text: messageData.cta_text || null,
            cta_link: messageData.cta_link || null
          }];
        });
        
        // Notifications si pas en train de regarder le chat
        const isUserWatchingChat = isOpen && document.hasFocus();
        if (messageData.senderId !== participantId && !isUserWatchingChat) {
          playSoundIfEnabled(messageData.type === 'coach' ? 'coach' : 'message');
          const senderName = messageData.sender || (messageData.type === 'coach' ? 'Coach Bassi' : 'Afroboost');
          showNewMessageNotification(senderName, messageData.text);
        }
      });
      
      // === ÉCOUTER L'INDICATEUR DE SAISIE ===
      socket.on('user_typing', (data) => {
        console.log('[SOCKET.IO] ⌨️ Typing event:', data);
        
        if (data.is_typing) {
          // Afficher l'indicateur
          setTypingUser({
            name: data.user_name,
            type: data.user_type
          });
          
          // Cacher automatiquement après 3 secondes d'inactivité
          if (typingTimeoutRef.current) {
            clearTimeout(typingTimeoutRef.current);
          }
          typingTimeoutRef.current = setTimeout(() => {
            setTypingUser(null);
          }, 3000);
        } else {
          // Cacher l'indicateur
          setTypingUser(null);
        }
      });
      
      // === SYNCHRONISATION TEMPS RÉEL : Suppression de cours ===
      socket.on('course_deleted', (data) => {
        console.log('[SOCKET.IO] 🗑️ Cours supprimé:', data.courseId);
        
        // 1. Retirer le cours de la liste locale
        setAvailableCourses(prev => prev.filter(course => course.id !== data.courseId));
        
        // 2. HARD DELETE: Vider le cache local pour forcer un rafraîchissement
        if (data.hardDelete) {
          // Supprimer les caches liés aux cours du sessionStorage
          try {
            const keysToRemove = [];
            for (let i = 0; i < sessionStorage.length; i++) {
              const key = sessionStorage.key(i);
              if (key && (key.includes('courses') || key.includes('reservations') || key.includes('calendar'))) {
                keysToRemove.push(key);
              }
            }
            keysToRemove.forEach(key => sessionStorage.removeItem(key));
            console.log('[CACHE] 🧹 Cache cours/réservations vidé');
          } catch (e) {
            console.warn('[CACHE] Erreur nettoyage:', e);
          }
        }
        
        // 3. Notification pour l'utilisateur
        if (data.deletedReservations > 0) {
          console.log(`[SOCKET.IO] ${data.deletedReservations} réservation(s) annulée(s)`);
        }
      });
      
      // === SYNCHRONISATION TEMPS RÉEL : Purge des cours archivés ===
      socket.on('courses_purged', (data) => {
        console.log('[SOCKET.IO] 🧹 Purge cours archivés:', data.count, 'cours supprimés');
        // Retirer tous les cours purgés
        setAvailableCourses(prev => prev.filter(course => !data.purgedIds.includes(course.id)));
        // Vider tout le cache
        try {
          sessionStorage.clear();
          console.log('[CACHE] 🧹 Cache entièrement vidé après purge');
        } catch (e) {
          console.warn('[CACHE] Erreur:', e);
        }
      });
      
      socket.on('disconnect', () => {
        console.log('[SOCKET.IO] Déconnecté');
      });
      
      socket.on('connect_error', (error) => {
        console.warn('[SOCKET.IO] Erreur connexion:', error.message);
      });
    }
    
    // Cleanup - Nettoyage complet pour éviter les fuites de mémoire
    return () => {
      if (socketRef.current) {
        const socket = socketRef.current;
        console.log('[SOCKET.IO] 🔌 Nettoyage listeners et déconnexion...');
        
        // Supprimer explicitement tous les listeners avant déconnexion
        socket.off('connect');
        socket.off('joined_session');
        socket.off('connect_error');
        socket.off('disconnect');
        socket.off('message_received');
        socket.off('user_typing');
        socket.off('course_deleted');
        socket.off('courses_purged');
        socket.off('reconnect');
        
        socket.disconnect();
        socketRef.current = null;
      }
      
      // Nettoyer les timers typing
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
        typingTimeoutRef.current = null;
      }
    };
  }, [sessionData?.id, step, participantId]);

  // === ÉTAT DE SYNCHRONISATION (indicateur visuel) ===
  const [isSyncing, setIsSyncing] = useState(false);
  
  // === RÉCUPÉRATION MESSAGES AU RETOUR - ARCHITECTURE "RAMASSER" RÉSILIENTE ===
  // Garantit ZÉRO PERTE de message avec retry automatique et gestion hors-ligne
  useEffect(() => {
    if (!sessionData?.id || step !== 'chat') return;
    
    // Stocker la dernière date de sync dans localStorage (UTC ISO 8601)
    const LAST_SYNC_KEY = `afroboost_last_sync_${sessionData.id}`;
    let lastSyncTime = localStorage.getItem(LAST_SYNC_KEY) || null;
    
    // Constantes de configuration
    const MAX_RETRIES = 3;
    const RETRY_DELAY = 2000;
    const ONLINE_DELAY = 800; // Délai après retour réseau pour stabiliser la connexion
    const REQUEST_TIMEOUT = 10000;
    
    // Fonction de récupération RÉSILIENTE avec retry
    const fetchLatestMessages = async (retryCount = 0, source = 'manual') => {
      // Vérifier si on est en ligne
      if (!navigator.onLine) {
        console.log('[RAMASSER] 📵 Hors ligne - Attente connexion...');
        return; // On laisse le listener 'online' rappeler
      }
      
      setIsSyncing(true);
      
      try {
        // Construire l'URL avec timestamp UTC
        let url = `${API}/messages/sync?session_id=${sessionData.id}&limit=100`;
        if (lastSyncTime) {
          // S'assurer que le timestamp est en UTC
          url += `&since=${encodeURIComponent(lastSyncTime)}`;
        }
        
        console.log(`[RAMASSER] Sync depuis ${source} (since=${lastSyncTime ? lastSyncTime.substring(0, 19) : 'null'})`);
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);
        
        const response = await fetch(url, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        // Mettre à jour lastSyncTime avec le timestamp UTC du serveur
        if (data.synced_at) {
          lastSyncTime = data.synced_at;
          localStorage.setItem(LAST_SYNC_KEY, lastSyncTime);
        }
        
        if (data.messages && data.messages.length > 0) {
          console.log(`[RAMASSER] ${data.count} message(s) recupere(s)`);
          setMessages(prev => {
            // ANTI-DOUBLONS: Set avec id ET _id
            const existingIds = new Set(prev.flatMap(m => [m.id, m._id].filter(Boolean)));
            const newMsgs = data.messages.filter(m => {
              const msgId = m.id || m._id;
              return msgId && !existingIds.has(msgId);
            });
            if (newMsgs.length > 0) {
              console.log(`[RAMASSER] ${newMsgs.length} NOUVEAUX messages ajoutes`);
              return [...prev, ...newMsgs].sort((a, b) => (a.created_at || '0').localeCompare(b.created_at || '0'));
            }
            return prev;
          });
        }
        
        setIsSyncing(false);
        
      } catch (err) {
        console.warn(`[RAMASSER] Tentative ${retryCount + 1}/${MAX_RETRIES} échouée:`, err.message);
        
        // Retry si pas épuisé et toujours en ligne
        if (retryCount < MAX_RETRIES - 1 && navigator.onLine) {
          console.log(`[RAMASSER] Retry dans ${RETRY_DELAY/1000}s...`);
          await new Promise(r => setTimeout(r, RETRY_DELAY));
          return fetchLatestMessages(retryCount + 1, source);
        }
        
        // Fallback vers l'ancien endpoint
        console.log('[RAMASSER] Tentative fallback...');
        try {
          const fallback = await fetch(`${API}/chat/sessions/${sessionData.id}/messages`);
          if (fallback.ok) {
            const data = await fallback.json();
            if (Array.isArray(data) && data.length > 0) {
              setMessages(prev => {
                const existingIds = new Set(prev.map(m => m.id));
                const newMsgs = data.filter(m => m.id && !existingIds.has(m.id));
                if (newMsgs.length > 0) {
                  console.log(`[RAMASSER-FALLBACK] ${newMsgs.length} messages récupérés`);
                  return [...prev, ...newMsgs].sort((a, b) => 
                    (a.created_at || '0').localeCompare(b.created_at || '0')
                  );
                }
                return prev;
              });
            }
          }
        } catch (fallbackErr) {
          console.warn('[RAMASSER] Fallback échoué:', fallbackErr.message);
        }
        
        setIsSyncing(false);
      }
    };
    
    // Listener visibilité (changement d'onglet ou retour de veille) - PRIORITÉ HAUTE
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        console.log('[VISIBILITY] 👀 App visible - Sync immédiate');
        // Sync immédiate sans délai pour visibilitychange (utilisateur actif)
        fetchLatestMessages(0, 'visibility');
      }
    };
    
    // Listener focus (clic sur la fenêtre)
    const handleFocus = () => {
      console.log('[FOCUS] App focus');
      fetchLatestMessages(0, 'focus');
    };
    
    // Listener online (retour réseau) - AVEC DÉLAI 800ms
    const handleOnline = () => {
      console.log('[ONLINE] 📶 Réseau rétabli - Attente stabilisation...');
      setTimeout(() => {
        console.log('[ONLINE] 📶 Sync après stabilisation');
        fetchLatestMessages(0, 'online');
      }, ONLINE_DELAY);
    };
    
    // Listener changement de connexion (4G <-> Wi-Fi) via Network Information API
    let connectionChangeTimeout = null;
    const handleConnectionChange = () => {
      // Éviter les appels multiples rapides
      if (connectionChangeTimeout) clearTimeout(connectionChangeTimeout);
      connectionChangeTimeout = setTimeout(() => {
        if (navigator.onLine) {
          console.log('[CONNECTION] Type réseau changé - Sync...');
          fetchLatestMessages(0, 'connection_change');
        }
      }, 1000); // 1s de délai pour stabiliser
    };
    
    // Ajouter les listeners
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('focus', handleFocus);
    window.addEventListener('online', handleOnline);
    
    // Network Information API (si disponible)
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    if (connection) {
      connection.addEventListener('change', handleConnectionChange);
    }
    
    // Récupération initiale au montage
    fetchLatestMessages(0, 'mount');
    
    // Cleanup
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('focus', handleFocus);
      window.removeEventListener('online', handleOnline);
      if (connection) {
        connection.removeEventListener('change', handleConnectionChange);
      }
      if (connectionChangeTimeout) clearTimeout(connectionChangeTimeout);
    };
  }, [sessionData?.id, step]);

  // === MESSAGERIE PRIVÉE (MP) - FENÊTRE FLOTTANTE ===
  const openPrivateChat = async (targetId, targetName) => {
    if (!participantId || !targetId || targetId === participantId) return;
    
    setIsLoading(true);
    try {
      // Créer ou récupérer la conversation privée
      const response = await axios.post(`${API}/private/conversations`, {
        participant_1_id: participantId,
        participant_1_name: leadData.firstName,
        participant_2_id: targetId,
        participant_2_name: targetName
      });
      
      const conversation = response.data;
      
      // Charger les messages existants
      const messagesRes = await axios.get(`${API}/private/messages/${conversation.id}`);
      
      // Ouvrir la fenêtre flottante MP
      setActivePrivateChat({
        id: conversation.id,
        recipientId: targetId,
        recipientName: targetName
      });
      setPrivateMessages(messagesRes.data.map(m => ({
        id: m.id,
        text: m.content,
        sender: m.sender_name,
        senderId: m.sender_id,
        isMine: m.sender_id === participantId,
        createdAt: m.created_at
      })));
      
      // === SOCKET.IO: Rejoindre la room de conversation privée ===
      if (socketRef.current) {
        socketRef.current.emit('join_private_conversation', {
          conversation_id: conversation.id,
          participant_id: participantId
        });
      }
      
      console.log(`💬 MP ouverte avec ${targetName}`);
      
    } catch (err) {
      console.error('Erreur ouverture MP:', err);
      alert('Erreur lors de l\'ouverture de la conversation privée');
    } finally {
      setIsLoading(false);
    }
  };

  // Fermer la fenêtre MP
  const closePrivateChat = () => {
    // === SOCKET.IO: Quitter la room de conversation privée ===
    if (socketRef.current && activePrivateChat?.id) {
      socketRef.current.emit('leave_private_conversation', {
        conversation_id: activePrivateChat.id
      });
    }
    setActivePrivateChat(null);
    setPrivateMessages([]);
    setPrivateInput('');
  };

  // === SOCKET.IO pour les MP - Remplace le polling ===
  useEffect(() => {
    if (!socketRef.current) return;
    
    const socket = socketRef.current;
    
    // Handler principal pour les messages privés
    const handlePrivateMessage = (data) => {
      console.log('[SOCKET.IO] 📩 Message privé reçu:', data);
      
      // Ne pas compter nos propres messages
      if (data.senderId === participantId) return;
      
      // Vérifier si c'est pour notre conversation active
      if (activePrivateChat && data.conversation_id === activePrivateChat.id) {
        // Message dans la conversation ouverte -> ajouter à la liste
        setPrivateMessages(prev => {
          const exists = prev.some(m => m.id === data.id);
          if (exists) return prev;
          
          return [...prev, {
            id: data.id,
            text: data.text,
            sender: data.sender,
            senderId: data.senderId,
            isMine: false,
            createdAt: data.created_at
          }];
        });
        
        // Son de notification DM (fenêtre déjà ouverte) - son "private" distinct
        playSoundIfEnabled('private');
        
        // Marquer comme lu
        axios.put(`${API}/private/messages/read/${activePrivateChat.id}?reader_id=${participantId}`).catch(() => {});
      } else {
        // Message pour une autre conversation ou pas de conversation ouverte
        // -> NOTIFICATION COMPLÈTE (badge + son si activé + titre clignotant)
        setUnreadPrivateCount(prev => prev + 1);
        playSoundIfEnabled('private'); // Son "ding" cristallin si activé
        notifyPrivateMessage(data.sender || 'Quelqu\'un');
      }
    };
    
    socket.on('private_message_received', handlePrivateMessage);
    
    return () => {
      socket.off('private_message_received', handlePrivateMessage);
    };
  }, [activePrivateChat, participantId, soundEnabled]);

  // === SOCKET.IO pour le TYPING INDICATOR dans les DM ===
  useEffect(() => {
    if (!socketRef.current) return;
    
    const socket = socketRef.current;
    
    const handleDmTyping = (data) => {
      // Ignorer nos propres événements de frappe
      if (data.user_id === participantId) return;
      
      // Vérifier si c'est pour notre conversation active
      if (activePrivateChat && data.conversation_id === activePrivateChat.id) {
        if (data.is_typing) {
          setDmTypingUser({ name: data.user_name });
          
          // Auto-hide après 3 secondes
          if (dmTypingTimeoutRef.current) {
            clearTimeout(dmTypingTimeoutRef.current);
          }
          dmTypingTimeoutRef.current = setTimeout(() => {
            setDmTypingUser(null);
          }, 3000);
        } else {
          setDmTypingUser(null);
        }
      }
    };
    
    socket.on('dm_typing', handleDmTyping);
    
    return () => {
      socket.off('dm_typing', handleDmTyping);
      if (dmTypingTimeoutRef.current) {
        clearTimeout(dmTypingTimeoutRef.current);
      }
    };
  }, [activePrivateChat, participantId]);

  // === SOCKET.IO pour la mise à jour d'AVATAR en temps réel ===
  useEffect(() => {
    if (!socketRef.current) return;
    
    const socket = socketRef.current;
    
    const handleAvatarChanged = (data) => {
      console.log('[SOCKET.IO] 📷 Avatar mis à jour:', data);
      
      // Mettre à jour les messages privés si l'avatar de l'interlocuteur change
      if (activePrivateChat && data.user_id !== participantId) {
        setPrivateMessages(prev => prev.map(msg => {
          if (msg.senderId === data.user_id) {
            return { ...msg, senderPhotoUrl: data.photo_url };
          }
          return msg;
        }));
      }
      
      // Mettre à jour les messages du chat principal (communautaire)
      setMessages(prev => prev.map(msg => {
        if (msg.senderId === data.user_id) {
          return { ...msg, senderPhotoUrl: data.photo_url };
        }
        return msg;
      }));
    };
    
    socket.on('user_avatar_changed', handleAvatarChanged);
    
    return () => {
      socket.off('user_avatar_changed', handleAvatarChanged);
    };
  }, [activePrivateChat, participantId]);

  // === DÉMARRER UNE DISCUSSION PRIVÉE (COMPAT ANCIEN CODE) ===
  const startPrivateChat = async (targetId, targetName) => {
    // Utilise la nouvelle fonction openPrivateChat avec fenêtre flottante
    // Réinitialiser le compteur et arrêter le clignotement quand on ouvre une conversation
    setUnreadPrivateCount(0);
    stopTitleFlash();
    openPrivateChat(targetId, targetName);
  };

  // Insérer un emoji dans l'input (utilisé par EmojiPicker)
  const insertEmoji = (emojiName) => {
    // Si c'est un emoji natif (🔥), l'ajouter directement
    if (emojiName.length <= 2 && /[\u{1F300}-\u{1F9FF}]/u.test(emojiName)) {
      setInputMessage(prev => prev + emojiName);
    } else {
      // Sinon c'est un emoji personnalisé -> tag
      const emojiTag = `[emoji:${emojiName}]`;
      setInputMessage(prev => prev + emojiTag);
    }
    setShowEmojiPicker(false);
  };

  // === MÉMORISATION CLIENT: Charger la session et configurer le chat ===
  useEffect(() => {
    const savedSession = localStorage.getItem(CHAT_SESSION_KEY);

    if (savedSession) {
      try {
        const session = JSON.parse(savedSession);
        setSessionData(session);
        setIsCommunityMode(session.mode === 'community');
      } catch (err) {
        localStorage.removeItem(CHAT_SESSION_KEY);
      }
    }

    // Si on arrive via un lien partagé, ouvrir automatiquement le widget
    const linkToken = getLinkTokenFromUrl();
    if (linkToken) {
      setIsOpen(true);
    }
  }, []);
  
  // === FERMER LE MENU UTILISATEUR AU CLIC EXTÉRIEUR ===
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (showUserMenu && !e.target.closest('.afro-share-menu')) {
        setShowUserMenu(false);
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [showUserMenu]);

  // === MODE COACH: Charger les sessions actives ===
  const loadCoachSessions = async () => {
    try {
      const res = await axios.get(`${API}/chat/sessions`);
      // Filtrer les sessions non supprimées avec des messages récents
      const activeSessions = res.data.filter(s => !s.is_deleted);
      setCoachSessions(activeSessions);
    } catch (err) {
      console.error('Error loading coach sessions:', err);
    }
  };

  // === MODE COACH: Charger les messages d'une session ===
  const loadCoachSessionMessages = async (session) => {
    setSelectedCoachSession(session);
    try {
      const res = await axios.get(`${API}/chat/sessions/${session.id}/messages`);
      const formattedMessages = res.data.map(m => ({
        id: m.id,
        type: m.sender_type === 'user' ? 'user' : m.sender_type === 'coach' ? 'coach' : 'ai',
        text: m.content,
        sender: m.sender_name,
        senderId: m.sender_id
      }));
      setMessages(formattedMessages);
      setLastMessageCount(formattedMessages.length);
    } catch (err) {
      console.error('Error loading session messages:', err);
    }
  };

  // === MODE COACH: Envoyer une réponse ===
  const sendCoachResponse = async () => {
    if (!selectedCoachSession || !inputMessage.trim()) return;
    
    setIsLoading(true);
    try {
      await axios.post(`${API}/chat/coach-response`, {
        session_id: selectedCoachSession.id,
        message: inputMessage.trim(),
        coach_name: 'Coach'
      });
      setInputMessage('');
      // Recharger les messages
      await loadCoachSessionMessages(selectedCoachSession);
      playSoundIfEnabled('coach');
    } catch (err) {
      console.error('Error sending coach response:', err);
      alert('Erreur lors de l\'envoi du message');
    } finally {
      setIsLoading(false);
    }
  };

  // Charger les sessions quand le mode coach est activé
  useEffect(() => {
    if (isCoachMode && isOpen) {
      loadCoachSessions();
      setStep('coach');
    }
  }, [isCoachMode, isOpen]);
  
  // === FERMER LES MENUS AU CLIC EXTÉRIEUR ===
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (showCoachMenu && !e.target.closest('.coach-icons-menu')) {
        setShowCoachMenu(false);
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [showCoachMenu]);

  // Scroll vers le bas des messages
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // === TIMER DYNAMIQUE: Rafraîchit les timestamps toutes les 60s ===
  const [, setTimestampTick] = useState(0);
  useEffect(() => {
    const timer = setInterval(() => {
      setTimestampTick(t => t + 1);
    }, 60000); // 60 secondes
    return () => clearInterval(timer);
  }, []);

  // === SMART ENTRY: Point d'entrée intelligent avec reconnaissance ===
  const handleSmartEntry = async (clientData, linkToken = null) => {
    try {
      const response = await axios.post(`${API}/chat/smart-entry`, {
        name: clientData.firstName,
        email: clientData.email,
        whatsapp: clientData.whatsapp,
        link_token: linkToken
      });

      const { participant, session, is_returning, chat_history, message } = response.data;

      // Sauvegarder les données
      const fullClientData = {
        ...clientData,
        participantId: participant.id
      };
      // Sauvegarder avec les deux clés pour compatibilité
      localStorage.setItem(CHAT_CLIENT_KEY, JSON.stringify(fullClientData));
      localStorage.setItem(AFROBOOST_IDENTITY_KEY, JSON.stringify({
        ...fullClientData,
        savedAt: new Date().toISOString()
      }));
      localStorage.setItem(CHAT_SESSION_KEY, JSON.stringify(session));

      setParticipantId(participant.id);
      setSessionData(session);
      setIsReturningClient(is_returning);
      setIsCommunityMode(session.mode === 'community');
      
      // === MISE À JOUR DU MODE COACH APRÈS CONNEXION ===
      const isCoach = clientData.email?.toLowerCase() === COACH_EMAIL;
      setIsCoachMode(isCoach);
      console.log(`[AUTH] Email: ${clientData.email}, isCoach: ${isCoach}`);

      // Restaurer l'historique si utilisateur reconnu
      if (is_returning && chat_history && chat_history.length > 0) {
        const restoredMessages = chat_history.map(msg => ({
          id: msg.id,
          type: msg.sender_type === 'user' ? 'user' : msg.sender_type === 'coach' ? 'coach' : 'ai',
          text: msg.content,
          sender: msg.sender_name
        }));
        setMessages([
          { type: 'ai', text: message },
          ...restoredMessages
        ]);
        setLastMessageCount(chat_history.length + 1);
      } else {
        setMessages([{
          type: 'ai',
          text: message
        }]);
        setLastMessageCount(1);
      }

      setStep('chat');
      
      // === DEMANDE AUTORISATION NOTIFICATIONS SUR CLIC CONNEXION ===
      // Anti-blocage mobile: demande liee a une action utilisateur (clic)
      const currentPermission = getNotificationPermissionStatus();
      if (currentPermission !== 'granted' && currentPermission !== 'denied') {
        console.log('[NOTIFICATIONS] Demande autorisation sur clic connexion...');
        const permission = await requestNotificationPermission();
        if (permission === 'granted') {
          setPushEnabled(true);
          // S'abonner aux notifications push avec l'ID du participant
          const subscribed = await subscribeToPush(participant.id);
          console.log('[PUSH] Abonnement:', subscribed ? 'OK' : 'Echec');
        }
      } else if (currentPermission === 'granted' && !isSubscribed()) {
        // Permission deja accordee mais pas encore abonne -> s'abonner
        const subscribed = await subscribeToPush(participant.id);
        if (subscribed) setPushEnabled(true);
      }
      
      // Debloquer l'audio pour iOS (necessite action utilisateur)
      unlockAudio();
      
      // === MESSAGE iOS PWA ===
      // Detecter iOS et afficher message pour ajout ecran d'accueil
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
      const isStandalone = window.navigator.standalone === true;
      const alreadyShown = localStorage.getItem('af_ios_prompt_shown');
      
      if (isIOS && !isStandalone && !alreadyShown) {
        setShowiOSPrompt(true);
        localStorage.setItem('af_ios_prompt_shown', 'true');
        // Auto-fermeture apres 5 secondes
        setTimeout(() => setShowiOSPrompt(false), 5000);
      }
      
      return { success: true, session, participant };

    } catch (err) {
      console.error('Smart entry error:', err);
      // Fallback: continuer sans le backend amélioré
      setMessages([{
        type: 'ai',
        text: `Enchanté ${clientData.firstName} ! Comment puis-je t'aider ?`
      }]);
      setStep('chat');
      return { success: false };
    }
  };

  // Valider et enregistrer le lead
  const handleSubmitLead = async (e) => {
    e.preventDefault();
    setError('');
    
    // Validation
    if (!leadData.firstName.trim()) {
      setError('Le prénom est requis');
      return;
    }
    if (!leadData.whatsapp.trim()) {
      setError('Le numéro WhatsApp est requis');
      return;
    }
    if (!leadData.email.trim() || !leadData.email.includes('@')) {
      setError('Un email valide est requis');
      return;
    }
    
    setIsLoading(true);
    
    try {
      const clientData = {
        firstName: leadData.firstName.trim(),
        whatsapp: leadData.whatsapp.trim(),
        email: leadData.email.trim().toLowerCase()
      };

      // Utiliser le smart entry pour la reconnaissance automatique
      const linkToken = getLinkTokenFromUrl();
      await handleSmartEntry(clientData, linkToken);

      // Backup: créer aussi un lead (ancien système)
      try {
        await axios.post(`${API}/leads`, {
          firstName: clientData.firstName,
          whatsapp: clientData.whatsapp,
          email: clientData.email,
          source: linkToken ? `link_${linkToken}` : 'widget_ia'
        });
      } catch (leadErr) {
        console.warn('Lead creation failed, continuing anyway:', leadErr);
      }
      
    } catch (err) {
      console.error('Error:', err);
      // Fallback
      localStorage.setItem(CHAT_CLIENT_KEY, JSON.stringify({
        firstName: leadData.firstName.trim(),
        whatsapp: leadData.whatsapp.trim(),
        email: leadData.email.trim().toLowerCase()
      }));
      
      setStep('chat');
      setMessages([{
        type: 'ai',
        text: `Enchanté ${leadData.firstName} ! Comment puis-je t'aider ?`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // === CLIENT RECONNU: Ouvrir directement le chat ===
  const handleReturningClientStart = async () => {
    setIsLoading(true);
    
    try {
      const linkToken = getLinkTokenFromUrl();
      await handleSmartEntry(leadData, linkToken);
    } catch (err) {
      console.error('Error:', err);
      setStep('chat');
      setMessages([{
        type: 'ai',
        text: `Bonjour ${leadData.firstName} ! 😊 Comment puis-je t'aider ?`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // === Ouvrir le widget ===
  const handleOpenWidget = () => {
    setIsOpen(true);
    
    // Si client reconnu et pas encore en mode chat, ouvrir directement le chat
    if (isReturningClient && step === 'form') {
      handleReturningClientStart();
    }
  };

  // Envoyer un message au chat avec contexte de session
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;
    
    const userMessage = inputMessage.trim();
    setInputMessage('');
    // Ajouter le senderId pour identifier les messages de l'utilisateur actuel
    setMessages(prev => [...prev, { type: 'user', text: userMessage, senderId: participantId }]);
    setLastMessageCount(prev => prev + 1);
    setMessageCount(prev => prev + 1);
    setIsLoading(true);
    
    try {
      // Si on a une session active, utiliser l'API améliorée
      if (sessionData && participantId) {
        const response = await axios.post(`${API}/chat/ai-response`, {
          session_id: sessionData.id,
          participant_id: participantId,
          message: userMessage
        });
        
        if (response.data.response) {
          // Jouer un son pour la réponse
          playSoundIfEnabled('message');
          
          setMessages(prev => [...prev, { 
            type: 'ai', 
            text: response.data.response
          }]);
          setLastMessageCount(prev => prev + 1);
        } else if (!response.data.ai_active) {
          // IA désactivée - message en attente
          setMessages(prev => [...prev, { 
            type: 'ai', 
            text: isCommunityMode 
              ? "Message envoyé au groupe ! Les autres participants verront votre message."
              : "Message reçu ! Le coach vous répondra bientôt. 💬"
          }]);
        }
      } else {
        // Fallback: ancien système - maintenant avec CRM auto-save
        const response = await axios.post(`${API}/chat`, {
          message: userMessage,
          firstName: leadData.firstName,
          email: leadData.email || '',       // Pour CRM auto-save
          whatsapp: leadData.whatsapp || '', // Pour CRM auto-save
          source: 'chat_ia',                 // Source pour tracking
          leadId: ''
        });
        
        playSoundIfEnabled('message');
        
        setMessages(prev => [...prev, { 
          type: 'ai', 
          text: response.data.response || "Désolé, je n'ai pas pu traiter votre message."
        }]);
      }
      
      // === PROMPT NOTIFICATIONS PUSH après le premier message ===
      if (messageCount === 1 && participantId && !pushEnabled) {
        // Attendre un peu avant de demander (non intrusif)
        setTimeout(async () => {
          const result = await promptForNotifications(participantId);
          if (result.subscribed) {
            setPushEnabled(true);
            console.log('Push notifications enabled');
          }
        }, 2000);
      }
      
    } catch (err) {
      console.error('Chat error:', err);
      setMessages(prev => [...prev, { 
        type: 'ai', 
        text: "Désolé, une erreur s'est produite. Veuillez réessayer."
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // === SUPPRIMER L'HISTORIQUE - ROUTE SÉCURISÉE ADMIN ===
  const handleDeleteHistory = async () => {
    if (!sessionData?.id) return;
    
    const confirm = window.confirm('Êtes-vous sûr de vouloir supprimer votre historique de conversation ?');
    if (!confirm) return;
    
    try {
      // Utiliser la route sécurisée qui vérifie l'email
      const response = await axios.post(`${API}/admin/delete-history`, {
        session_id: sessionData.id,
        email: leadData.email || ''
      });
      
      if (response.data.success) {
        // Vider l'affichage local
        setMessages([{
          type: 'ai',
          text: '🗑️ Historique supprimé. Comment puis-je vous aider ?'
        }]);
        setLastMessageCount(1);
        setShowMenu(false);
        console.log('[ADMIN] Historique supprimé:', response.data.deleted_count, 'messages');
      }
      
    } catch (err) {
      console.error('[SECURITY] Delete history error:', err.response?.data?.detail || err.message);
      if (err.response?.status === 403) {
        alert('⛔ Accès refusé. Seul le coach peut supprimer l\'historique.');
      } else {
        alert('Erreur lors de la suppression de l\'historique');
      }
    }
  };

  // Réinitialiser le widget
  const handleClose = () => {
    setIsOpen(false);
    setShowMenu(false);
  };

  // === CHANGER D'IDENTITÉ - ROUTE SÉCURISÉE ADMIN ===
  const handleChangeIdentity = async () => {
    try {
      // Vérifier côté serveur (optionnel mais recommandé)
      await axios.post(`${API}/admin/change-identity`, {
        participant_id: participantId,
        email: leadData.email || ''
      });
      
      // Réinitialiser localement (y compris le profil abonné)
      localStorage.removeItem(CHAT_CLIENT_KEY);
      localStorage.removeItem(CHAT_SESSION_KEY);
      localStorage.removeItem(AFROBOOST_IDENTITY_KEY);
      localStorage.removeItem(AFROBOOST_PROFILE_KEY);
      localStorage.removeItem('subscriber_data');
      setLeadData({ firstName: '', whatsapp: '', email: '' });
      setIsReturningClient(false);
      setStep('form');
      setMessages([]);
      setSessionData(null);
      setParticipantId(null);
      setShowMenu(false);
      setLastMessageCount(0);
      setIsCoachMode(false);
      setAfroboostProfile(null);
      setSubscriberData(null);
      setIsFullscreen(false);
      setShowSubscriberForm(false);
      setSubscriberFormData({ name: '', whatsapp: '', email: '', code: '' });
      console.log('[ADMIN] Identité et profil abonné réinitialisés');
      
    } catch (err) {
      console.error('[SECURITY] Change identity error:', err.response?.data?.detail || err.message);
      if (err.response?.status === 403) {
        alert('⛔ Accès refusé. Seul le coach peut changer l\'identité.');
      } else {
        // En cas d'erreur réseau, on fait quand même le reset local (coach mode)
        localStorage.removeItem(CHAT_CLIENT_KEY);
        localStorage.removeItem(CHAT_SESSION_KEY);
        localStorage.removeItem(AFROBOOST_IDENTITY_KEY);
        localStorage.removeItem(AFROBOOST_PROFILE_KEY);
        localStorage.removeItem('subscriber_data');
        setLeadData({ firstName: '', whatsapp: '', email: '' });
        setStep('form');
        setMessages([]);
        setSessionData(null);
        setParticipantId(null);
        setShowMenu(false);
        setIsCoachMode(false);
        setAfroboostProfile(null);
        setSubscriberData(null);
        setIsFullscreen(false);
      }
    }
  };

  // === FONCTION POUR ÉMETTRE L'ÉVÉNEMENT TYPING ===
  const emitTyping = (isTyping) => {
    if (!socketRef.current || !sessionData?.id) return;
    
    const now = Date.now();
    // Éviter le spam (max 1 événement par seconde)
    if (isTyping && now - lastTypingEmitRef.current < 1000) return;
    lastTypingEmitRef.current = now;
    
    const eventName = isTyping ? 'typing_start' : 'typing_stop';
    socketRef.current.emit(eventName, {
      session_id: sessionData.id,
      user_name: isCoachMode ? 'Coach Bassi' : leadData.firstName || 'Utilisateur',
      user_type: isCoachMode ? 'coach' : 'user'
    });
  };

  // === FONCTION POUR ÉMETTRE L'ÉVÉNEMENT TYPING DANS LES DM ===
  const emitDmTyping = (isTyping) => {
    if (!socketRef.current || !activePrivateChat?.id) return;
    
    const now = Date.now();
    // Éviter le spam (max 1 événement par seconde)
    if (isTyping && now - lastDmTypingEmitRef.current < 1000) return;
    lastDmTypingEmitRef.current = now;
    
    try {
      const eventName = isTyping ? 'dm_typing_start' : 'dm_typing_stop';
      socketRef.current.emit(eventName, {
        conversation_id: activePrivateChat.id,
        user_id: participantId,
        user_name: afroboostProfile?.name || leadData?.firstName || 'Utilisateur'
      });
    } catch (e) {
      // NULL-SAFE: Ne pas bloquer le chat si l'événement échoue
      console.warn('[DM-TYPING] Erreur émission:', e.message);
    }
  };

  // === FONCTION POUR ÉMETTRE LA MISE À JOUR D'AVATAR ===
  const emitAvatarUpdate = (photoUrl) => {
    if (!socketRef.current || !participantId) return;
    
    try {
      socketRef.current.emit('avatar_updated', {
        user_id: participantId,
        user_name: afroboostProfile?.name || leadData?.firstName || 'Utilisateur',
        photo_url: photoUrl
      });
      console.log('[AVATAR] 📷 Diffusion mise à jour avatar');
    } catch (e) {
      console.warn('[AVATAR] Erreur diffusion avatar:', e.message);
    }
  };

  // Handler pour l'input avec émission typing
  const handleInputChangeWithTyping = (e) => {
    const value = e.target.value;
    setInputMessage(value);
    
    // Émettre l'événement typing
    if (value.length > 0) {
      emitTyping(true);
    }
  };

  // Arrêter l'indicateur typing quand on perd le focus ou envoie
  const handleInputBlur = () => {
    emitTyping(false);
  };

  return (
    <>
      {/* Style pour les liens dans les messages et responsive mobile */}
      <style>{`
        .chat-link {
          color: #a78bfa;
          text-decoration: underline;
          word-break: break-all;
        }
        .chat-link:hover {
          color: #c4b5fd;
        }
        
        /* Emoji inline dans les messages */
        .chat-emoji {
          width: 20px;
          height: 20px;
          vertical-align: middle;
          display: inline-block;
          margin: 0 2px;
        }
        
        /* Animation pastille notification MP */
        @keyframes pulse {
          0%, 100% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
          }
          50% {
            transform: scale(1.1);
            box-shadow: 0 0 0 8px rgba(239, 68, 68, 0);
          }
        }
        
        /* Animation points typing DM (minimaliste) */
        @keyframes dmTypingDot {
          0%, 80%, 100% {
            opacity: 0.3;
            transform: scale(0.8);
          }
          40% {
            opacity: 1;
            transform: scale(1);
          }
        }
        
        /* Chat widget responsive - plus grand sur mobile */
        @media (max-width: 640px) {
          .chat-widget-window {
            bottom: 0 !important;
            right: 0 !important;
            left: 0 !important;
            width: 100% !important;
            max-width: 100% !important;
            height: 85vh !important;
            max-height: 85vh !important;
            border-radius: 16px 16px 0 0 !important;
          }
          .chat-widget-button {
            bottom: 100px !important; /* Décalé vers le haut pour ne pas gêner la barre d'input */
            right: 16px !important;
            width: 60px !important;
            height: 60px !important;
          }
        }
        
        @media (min-width: 641px) and (max-width: 1024px) {
          .chat-widget-window {
            width: 400px !important;
            height: 70vh !important;
            max-height: 70vh !important;
          }
        }
      `}</style>

      {/* === MESSAGE iOS PWA (ajout ecran d'accueil) === */}
      {showiOSPrompt && (
        <div
          style={{
            position: 'fixed',
            bottom: '170px',
            right: '20px',
            maxWidth: '280px',
            background: 'linear-gradient(135deg, #1a1a2e, #16213e)',
            borderRadius: '12px',
            padding: '12px 16px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
            zIndex: 60,
            border: '1px solid rgba(255,255,255,0.1)',
            animation: 'fadeIn 0.3s ease-out'
          }}
          data-testid="ios-pwa-prompt"
        >
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
            {/* Icone Share SVG minimaliste */}
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" strokeWidth="2" style={{ flexShrink: 0, marginTop: '2px' }}>
              <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/>
              <polyline points="16 6 12 2 8 6"/>
              <line x1="12" y1="2" x2="12" y2="15"/>
            </svg>
            <div>
              <div style={{ fontSize: '12px', color: '#fff', lineHeight: '1.4' }}>
                Pour recevoir les alertes, ajoutez cette application a votre ecran d'accueil.
              </div>
              <div style={{ fontSize: '10px', color: '#888', marginTop: '4px' }}>
                Partager &gt; Sur l'ecran d'accueil
              </div>
            </div>
            {/* Bouton fermer */}
            <button
              onClick={() => setShowiOSPrompt(false)}
              style={{
                background: 'none',
                border: 'none',
                color: '#666',
                cursor: 'pointer',
                padding: '0',
                marginLeft: 'auto',
                flexShrink: 0
              }}
              aria-label="Fermer"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Bouton flottant WhatsApp - Positionné à DROITE, au-dessus de la barre */}
      {!isOpen && (
        <button
          onClick={handleOpenWidget}
          className="chat-widget-button fixed z-50 shadow-lg transition-all duration-300 hover:scale-110"
          style={{
            bottom: '100px', /* Décalé vers le haut pour ne pas gêner le bouton Envoyer */
            right: '20px',
            left: 'auto', /* Force le positionnement à droite */
            width: '56px',
            height: '56px',
            borderRadius: '50%',
            background: '#25D366',
            border: 'none',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 15px rgba(37, 211, 102, 0.4)',
            position: 'fixed', /* Assurer position fixe */
            zIndex: 50 /* Inférieur à la barre de saisie */
          }}
          data-testid="chat-widget-button"
        >
          <WhatsAppIcon />
          
          {/* Badge MP non lus (pastille rouge) */}
          {unreadPrivateCount > 0 && (
            <span 
              style={{
                position: 'absolute',
                top: '-6px',
                right: '-6px',
                minWidth: '22px',
                height: '22px',
                borderRadius: '11px',
                background: '#ef4444',
                border: '2px solid #0a0a0a',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '11px',
                fontWeight: 'bold',
                color: '#fff',
                padding: '0 4px',
                animation: 'pulse 1.5s infinite'
              }}
              data-testid="unread-mp-badge"
            >
              {unreadPrivateCount > 99 ? '99+' : unreadPrivateCount}
            </span>
          )}
          
          {/* Badge si client reconnu (affiché seulement si pas de MP non lus) */}
          {isReturningClient && unreadPrivateCount === 0 && (
            <span 
              style={{
                position: 'absolute',
                top: '-4px',
                right: '-4px',
                width: '18px',
                height: '18px',
                borderRadius: '50%',
                background: '#d91cd2',
                border: '2px solid #0a0a0a',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '10px',
                color: '#fff'
              }}
            >
              ✓
            </span>
          )}
        </button>
      )}

      {/* Fenêtre de chat - Responsive avec dvh pour compatibilité clavier mobile */}
      {isOpen && (
        <div
          ref={chatContainerRef}
          className="chat-widget-window fixed z-50 shadow-2xl"
          style={{
            bottom: isFullscreen ? '0' : '80px',
            right: isFullscreen ? '0' : '20px',
            left: isFullscreen ? '0' : 'auto',
            top: isFullscreen ? '0' : 'auto',
            width: isFullscreen ? '100vw' : '380px',
            maxWidth: isFullscreen ? '100vw' : 'calc(100vw - 40px)',
            height: isFullscreen ? '100dvh' : '70vh', /* dvh pour compatibilité clavier mobile */
            maxHeight: isFullscreen ? '100dvh' : '85vh',
            minHeight: isFullscreen ? '100dvh' : '400px',
            borderRadius: isFullscreen ? '0' : '16px',
            background: '#0a0a0a',
            border: isFullscreen ? 'none' : '1px solid rgba(217, 28, 210, 0.3)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden'
          }}
          data-testid="chat-widget-window"
        >
          {/* Header */}
          <div 
            style={{
              background: isCommunityMode 
                ? 'linear-gradient(135deg, #8b5cf6, #6366f1)' 
                : 'linear-gradient(135deg, #25D366, #128C7E)',
              padding: '12px 16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexShrink: 0
            }}
          >
            <div className="flex items-center gap-3">
              <div 
                style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  background: 'rgba(255,255,255,0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                {isCommunityMode ? <GroupIcon /> : <WhatsAppIcon />}
              </div>
              <div>
                <div className="text-white font-semibold text-sm">
                  {isCommunityMode ? 'Communauté Afroboost' : 'Afroboost'}
                </div>
                <div className="text-white text-xs" style={{ opacity: 0.8 }}>
                  {/* Indicateur de synchronisation */}
                  {isSyncing ? (
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <span style={{ 
                        width: '8px', 
                        height: '8px', 
                        borderRadius: '50%', 
                        background: '#fbbf24',
                        animation: 'pulse 1s infinite'
                      }}></span>
                      Synchronisation...
                    </span>
                  ) : (
                    /* Afficher le statut abonné si profil validé */
                    afroboostProfile?.code && step === 'chat'
                      ? `Abonné - ${afroboostProfile.name}`
                      : isReturningClient && step === 'chat' 
                        ? leadData.firstName 
                        : isCommunityMode 
                          ? 'Chat Groupe'
                          : sessionData?.is_ai_active === false 
                            ? 'Mode Coach'
                            : 'Coach Bassi'
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {/* Bouton Plein Écran - TOUJOURS visible en mode abonné */}
              {step === 'chat' && (
                <button
                  onClick={toggleFullscreen}
                  title={isFullscreen ? "Quitter le plein écran" : "Mode plein écran"}
                  style={{
                    background: afroboostProfile?.code 
                      ? 'linear-gradient(135deg, rgba(147, 51, 234, 0.4), rgba(99, 102, 241, 0.4))'
                      : 'rgba(255,255,255,0.2)',
                    border: afroboostProfile?.code ? '1px solid rgba(147, 51, 234, 0.5)' : 'none',
                    borderRadius: '8px',
                    width: '32px',
                    height: '32px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff'
                  }}
                  data-testid="fullscreen-btn"
                >
                  {isFullscreen ? <ExitFullscreenIcon /> : <FullscreenIcon />}
                </button>
              )}
              
              {/* === ICÔNES MINIMALISTES (Partage + Menu) === */}
              {step === 'chat' && (
                <div className="relative afro-share-menu" style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  {/* Icône Partager (filaire fine) */}
                  <button
                    onClick={handleShareLink}
                    title={linkCopied ? "Lien copié !" : "Partager"}
                    style={{
                      background: 'none',
                      border: 'none',
                      padding: '4px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      opacity: linkCopied ? 1 : 0.6,
                      transition: 'opacity 0.2s ease'
                    }}
                    data-testid="share-link-btn"
                  >
                    {linkCopied ? (
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#22c55e" strokeWidth="1.5">
                        <polyline points="20 6 9 17 4 12"></polyline>
                      </svg>
                    ) : (
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.5">
                        <circle cx="18" cy="5" r="3"></circle>
                        <circle cx="6" cy="12" r="3"></circle>
                        <circle cx="18" cy="19" r="3"></circle>
                        <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
                        <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
                      </svg>
                    )}
                  </button>
                  
                  {/* Icône Menu (⋮) filaire fine */}
                  <button
                    onClick={() => setShowUserMenu(!showUserMenu)}
                    style={{
                      background: 'none',
                      border: 'none',
                      padding: '4px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      opacity: 0.6,
                      transition: 'opacity 0.2s ease'
                    }}
                    data-testid="user-menu-btn"
                  >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="#fff">
                      <circle cx="12" cy="5" r="1.5"></circle>
                      <circle cx="12" cy="12" r="1.5"></circle>
                      <circle cx="12" cy="19" r="1.5"></circle>
                    </svg>
                  </button>
                  
                  {/* Menu déroulant utilisateur */}
                  {showUserMenu && (
                    <div
                      style={{
                        position: 'absolute',
                        top: '35px',
                        right: '0',
                        background: '#1a1a1a',
                        borderRadius: '8px',
                        border: '1px solid rgba(255,255,255,0.1)',
                        overflow: 'hidden',
                        minWidth: '180px',
                        zIndex: 100,
                        boxShadow: '0 4px 20px rgba(0,0,0,0.5)'
                      }}
                    >
                      {/* Upload Photo de profil */}
                      <label
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '10px',
                          padding: '10px 14px',
                          color: '#fff',
                          fontSize: '12px',
                          cursor: 'pointer'
                        }}
                        className="hover:bg-white/10"
                      >
                        <input
                          type="file"
                          accept="image/*"
                          onChange={(e) => {
                            handlePhotoUpload(e);
                            setShowUserMenu(false);
                          }}
                          style={{ display: 'none' }}
                        />
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                          <circle cx="8.5" cy="8.5" r="1.5"></circle>
                          <polyline points="21 15 16 10 5 21"></polyline>
                        </svg>
                        {uploadingPhoto ? 'Upload...' : 'Photo de profil'}
                        {profilePhoto && (
                          <img 
                            src={profilePhoto} 
                            alt="" 
                            style={{ width: '20px', height: '20px', borderRadius: '50%', marginLeft: 'auto' }}
                          />
                        )}
                      </label>
                      
                      <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)' }} />
                      
                      {/* Mode Visiteur - seulement si abonné */}
                      {afroboostProfile?.code && (
                        <>
                          <button
                            onClick={() => { handleVisitorMode(); setShowUserMenu(false); }}
                            style={{
                              width: '100%',
                              padding: '10px 14px',
                              textAlign: 'left',
                              fontSize: '12px',
                              color: '#fff',
                              background: 'none',
                              border: 'none',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '10px'
                            }}
                            className="hover:bg-white/10"
                            data-testid="visitor-mode-btn"
                          >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                              <circle cx="12" cy="12" r="3"></circle>
                            </svg>
                            Mode Visiteur
                          </button>
                          <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)' }} />
                        </>
                      )}
                      
                      {/* Toggle Son (icône haut-parleur filaire) */}
                      <button
                        onClick={() => { toggleSound(); setShowUserMenu(false); }}
                        style={{
                          width: '100%',
                          padding: '10px 14px',
                          textAlign: 'left',
                          fontSize: '12px',
                          color: '#fff',
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '10px'
                        }}
                        className="hover:bg-white/10"
                        data-testid="toggle-sound-btn"
                      >
                        {soundEnabled ? (
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                            <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                            <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
                          </svg>
                        ) : (
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                            <line x1="23" y1="9" x2="17" y2="15"></line>
                            <line x1="17" y1="9" x2="23" y2="15"></line>
                          </svg>
                        )}
                        {soundEnabled ? 'Son activé' : 'Son désactivé'}
                      </button>
                      
                      {/* Silence Auto (22h-08h) - Mode Ne Pas Déranger */}
                      <button
                        onClick={() => { toggleSilenceAuto(); setShowUserMenu(false); }}
                        style={{
                          width: '100%',
                          padding: '10px 14px',
                          textAlign: 'left',
                          fontSize: '12px',
                          color: silenceAutoEnabled ? '#FBBF24' : '#fff',
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '10px'
                        }}
                        className="hover:bg-white/10"
                        data-testid="toggle-silence-auto-btn"
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                        </svg>
                        {silenceAutoEnabled ? 'Silence Auto (actif)' : `Silence Auto (${getSilenceHoursLabel()})`}
                      </button>
                      
                      <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)' }} />
                      
                      {/* Rafraîchir */}
                      <button
                        onClick={() => { window.location.reload(); }}
                        style={{
                          width: '100%',
                          padding: '10px 14px',
                          textAlign: 'left',
                          fontSize: '12px',
                          color: '#fff',
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '10px'
                        }}
                        className="hover:bg-white/10"
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="23 4 23 10 17 10"></polyline>
                          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
                        </svg>
                        Rafraîchir
                      </button>
                      
                      <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)' }} />
                      
                      {/* Bouton Déconnexion */}
                      <button
                        onClick={() => { handleLogout(); }}
                        disabled={isLoggingOut}
                        style={{
                          width: '100%',
                          padding: '10px 14px',
                          textAlign: 'left',
                          fontSize: '12px',
                          color: isLoggingOut ? '#888' : '#ef4444',
                          background: 'none',
                          border: 'none',
                          cursor: isLoggingOut ? 'wait' : 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '10px',
                          opacity: isLoggingOut ? 0.6 : 1
                        }}
                        className="hover:bg-white/10"
                        data-testid="logout-btn"
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                          <polyline points="16 17 21 12 16 7"></polyline>
                          <line x1="21" y1="12" x2="9" y2="12"></line>
                        </svg>
                        {isLoggingOut ? 'Deconnexion...' : 'Se deconnecter'}
                      </button>
                    </div>
                  )}
                </div>
              )}
              
              {/* Menu burger - VISIBLE UNIQUEMENT POUR LE COACH/ADMIN (masque en mode Vue Visiteur) */}
              {(step === 'chat' || step === 'coach') && isCoachMode && !isVisitorPreview && (
                <div className="relative">
                  <button
                    onClick={() => setShowMenu(!showMenu)}
                    style={{
                      background: 'rgba(255,255,255,0.2)',
                      border: 'none',
                      borderRadius: '8px',
                      width: '32px',
                      height: '32px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#fff',
                      fontSize: '16px'
                    }}
                    data-testid="chat-menu-btn"
                  >
                    ⋮
                  </button>
                  
                  {/* Menu déroulant - ADMIN ONLY */}
                  {showMenu && (
                    <div
                      style={{
                        position: 'absolute',
                        top: '40px',
                        right: '0',
                        background: '#1a1a1a',
                        borderRadius: '8px',
                        border: '1px solid rgba(255,255,255,0.1)',
                        overflow: 'hidden',
                        minWidth: '180px',
                        zIndex: 100
                      }}
                    >
                      <button
                        onClick={handleDeleteHistory}
                        className="w-full px-4 py-3 text-left text-sm hover:bg-white/10 flex items-center gap-2"
                        style={{ color: '#ef4444', border: 'none', background: 'none' }}
                        data-testid="delete-history-btn"
                      >
                        <TrashIcon /> Supprimer l'historique
                      </button>
                      <button
                        onClick={handleChangeIdentity}
                        className="w-full px-4 py-3 text-left text-sm hover:bg-white/10 flex items-center gap-2"
                        style={{ color: '#fff', border: 'none', background: 'none' }}
                        data-testid="change-identity-btn"
                      >
                        Changer d'identité
                      </button>
                    </div>
                  )}
                </div>
              )}
              
              <button
                onClick={handleClose}
                style={{
                  background: 'rgba(255,255,255,0.2)',
                  border: 'none',
                  borderRadius: '50%',
                  width: '32px',
                  height: '32px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
                data-testid="chat-close-btn"
              >
                <CloseIcon />
              </button>
            </div>
          </div>
          
          {/* Badge Mode Aperçu (Admin) - Sous la barre de navigation */}
          {isVisitorPreview && isCoachMode && (
            <div
              style={{
                height: '2px',
                background: 'linear-gradient(90deg, #9333ea, #ec4899)',
                position: 'relative',
                flexShrink: 0,
                zIndex: 50,
                boxShadow: '0 1px 4px rgba(0, 0, 0, 0.15)'
              }}
            >
              <span
                style={{
                  position: 'absolute',
                  top: '2px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  background: '#0a0a0a',
                  padding: '2px 8px',
                  borderRadius: '0 0 4px 4px',
                  fontSize: '9px',
                  color: '#9333ea',
                  fontWeight: '500',
                  letterSpacing: '0.5px',
                  textTransform: 'uppercase',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.2)'
                }}
                data-testid="visitor-preview-badge"
              >
                Aperçu
              </span>
            </div>
          )}

          {/* Contenu avec scroll */}
          <div style={{ 
            flex: 1, 
            overflow: 'hidden', 
            display: 'flex', 
            flexDirection: 'column',
            minHeight: 0
          }}>
            
            {/* Formulaire de capture avec scroll */}
            {step === 'form' && (
              <div 
                style={{
                  flex: 1,
                  overflowY: 'auto',
                  padding: '20px',
                  display: 'flex',
                  flexDirection: 'column'
                }}
              >
                {/* === FORMULAIRE ABONNÉ (4 champs avec code promo) === */}
                {showSubscriberForm ? (
                  <SubscriberForm
                    formData={subscriberFormData}
                    setFormData={setSubscriberFormData}
                    onSubmit={handleSubscriberFormSubmit}
                    onCancel={() => { setShowSubscriberForm(false); setError(''); }}
                    error={error}
                    isLoading={validatingCode}
                  />
                ) : (
                  /* === FORMULAIRE VISITEUR CLASSIQUE (3 champs) === */
                  <form 
                    onSubmit={handleSubmitLead}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '12px',
                      minHeight: 'min-content'
                    }}
                  >
                    <p className="text-white text-sm text-center mb-2">
                      Avant de commencer, présentez-vous !
                    </p>
                    
                    {error && (
                      <div style={{ 
                        background: 'rgba(239, 68, 68, 0.2)', 
                        color: '#ef4444', 
                        padding: '8px 12px', 
                        borderRadius: '8px',
                        fontSize: '12px'
                      }}>
                        {error}
                      </div>
                    )}
                    
                    <div>
                      <label className="block text-white text-xs mb-1" style={{ opacity: 0.7 }}>Prénom *</label>
                      <input
                        type="text"
                        value={leadData.firstName}
                        onChange={(e) => setLeadData({ ...leadData, firstName: e.target.value })}
                        placeholder="Votre prénom"
                        className="w-full px-3 py-2 rounded-lg text-sm"
                        style={{
                          background: 'rgba(255,255,255,0.1)',
                          border: '1px solid rgba(255,255,255,0.2)',
                          color: '#fff',
                          outline: 'none'
                        }}
                        data-testid="lead-firstname"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-white text-xs mb-1" style={{ opacity: 0.7 }}>Numéro WhatsApp *</label>
                      <input
                        type="tel"
                        value={leadData.whatsapp}
                        onChange={(e) => setLeadData({ ...leadData, whatsapp: e.target.value })}
                        placeholder="+41 79 123 45 67"
                        className="w-full px-3 py-2 rounded-lg text-sm"
                        style={{
                          background: 'rgba(255,255,255,0.1)',
                          border: '1px solid rgba(255,255,255,0.2)',
                          color: '#fff',
                          outline: 'none'
                        }}
                        data-testid="lead-whatsapp"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-white text-xs mb-1" style={{ opacity: 0.7 }}>Email *</label>
                      <input
                        type="email"
                        value={leadData.email}
                        onChange={(e) => setLeadData({ ...leadData, email: e.target.value })}
                        placeholder="votre@email.com"
                        className="w-full px-3 py-2 rounded-lg text-sm"
                        style={{
                          background: 'rgba(255,255,255,0.1)',
                          border: '1px solid rgba(255,255,255,0.2)',
                          color: '#fff',
                          outline: 'none'
                        }}
                        data-testid="lead-email"
                      />
                    </div>
                    
                    <button
                      type="submit"
                      disabled={isLoading}
                      className="py-3 rounded-lg font-semibold text-sm transition-all"
                      style={{
                        background: '#25D366',
                        color: '#fff',
                        border: 'none',
                        cursor: isLoading ? 'wait' : 'pointer',
                        opacity: isLoading ? 0.7 : 1,
                        marginTop: '8px'
                      }}
                      data-testid="lead-submit"
                    >
                      {isLoading ? 'Chargement...' : 'Commencer le chat 💬'}
                    </button>
                    
                    {/* === SÉPARATEUR === */}
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '12px',
                      margin: '8px 0'
                    }}>
                      <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.2)' }} />
                      <span style={{ color: 'rgba(255,255,255,0.5)', fontSize: '11px' }}>ou</span>
                      <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.2)' }} />
                    </div>
                    
                    {/* === BOUTON ABONNÉ === */}
                    <button
                      type="button"
                      onClick={() => { setShowSubscriberForm(true); setError(''); }}
                      className="py-3 rounded-lg font-semibold text-sm transition-all"
                      style={{
                        background: 'linear-gradient(135deg, rgba(147, 51, 234, 0.3), rgba(99, 102, 241, 0.3))',
                        color: '#a855f7',
                        border: '1px solid rgba(147, 51, 234, 0.4)',
                        cursor: 'pointer'
                      }}
                      data-testid="subscriber-btn"
                    >
                      S'identifier comme abonné
                    </button>
                    
                    <p className="text-center text-xs" style={{ color: 'rgba(255,255,255,0.4)', marginTop: '8px' }}>
                      Vos données sont protégées et utilisées uniquement pour vous contacter.
                    </p>
                  </form>
                )}
              </div>
            )}

            {/* === MODE COACH: Interface de gestion des conversations === */}
            {step === 'coach' && isCoachMode && (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
                {/* Header Coach MINIMALISTE - Masque en mode Vue Visiteur */}
                {!isVisitorPreview && (
                <div style={{ 
                  background: 'rgba(217, 28, 210, 0.2)', 
                  padding: '8px 16px', 
                  borderBottom: '1px solid rgba(217, 28, 210, 0.3)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <span style={{ color: '#d91cd2', fontSize: '12px', fontWeight: 'bold' }}>
                    Mode Coach
                  </span>
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }} className="coach-icons-menu">
                    {/* Icône Partage (SVG minimaliste) */}
                    <button
                      onClick={handleShareLink}
                      title={linkCopied ? "Lien copié !" : "Partager"}
                      style={{ 
                        background: 'none', 
                        border: 'none', 
                        padding: '4px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        opacity: linkCopied ? 1 : 0.7,
                        transition: 'opacity 0.2s ease'
                      }}
                      data-testid="coach-chat-share"
                    >
                      {linkCopied ? (
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#22c55e" strokeWidth="2">
                          <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                      ) : (
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.5">
                          <circle cx="18" cy="5" r="3"></circle>
                          <circle cx="6" cy="12" r="3"></circle>
                          <circle cx="18" cy="19" r="3"></circle>
                          <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
                          <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
                        </svg>
                      )}
                    </button>
                    
                    {/* Icône Menu (⋮) avec badge notifications */}
                    <div style={{ position: 'relative' }}>
                      <button
                        onClick={() => setShowCoachMenu(!showCoachMenu)}
                        style={{ 
                          background: 'none', 
                          border: 'none', 
                          padding: '4px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          opacity: 0.7,
                          transition: 'opacity 0.2s ease'
                        }}
                        data-testid="coach-chat-menu"
                      >
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="#fff">
                          <circle cx="12" cy="5" r="2"></circle>
                          <circle cx="12" cy="12" r="2"></circle>
                          <circle cx="12" cy="19" r="2"></circle>
                        </svg>
                      </button>
                      
                      {/* Badge notification (point rouge) */}
                      {coachSessions.length > 0 && (
                        <span style={{
                          position: 'absolute',
                          top: '0',
                          right: '0',
                          width: '8px',
                          height: '8px',
                          borderRadius: '50%',
                          background: '#ef4444',
                          border: '1px solid rgba(0,0,0,0.3)'
                        }} />
                      )}
                      
                      {/* Menu déroulant coach */}
                      {showCoachMenu && (
                        <div
                          style={{
                            position: 'absolute',
                            top: '30px',
                            right: '0',
                            background: '#1a1a1a',
                            borderRadius: '8px',
                            border: '1px solid rgba(255,255,255,0.1)',
                            overflow: 'hidden',
                            minWidth: '160px',
                            zIndex: 100,
                            boxShadow: '0 4px 20px rgba(0,0,0,0.5)'
                          }}
                        >
                          {/* Toggle Vue Visiteur (Admin) */}
                          <button
                            onClick={() => {
                              setIsVisitorPreview(!isVisitorPreview);
                              setShowCoachMenu(false);
                              console.log('[ADMIN] Vue Visiteur:', !isVisitorPreview ? 'activée' : 'désactivée');
                            }}
                            style={{
                              width: '100%',
                              padding: '10px 14px',
                              textAlign: 'left',
                              fontSize: '12px',
                              color: isVisitorPreview ? '#9333ea' : '#fff',
                              background: 'none',
                              border: 'none',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px'
                            }}
                            className="hover:bg-white/10"
                            data-testid="visitor-preview-toggle"
                          >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                              <circle cx="12" cy="12" r="3"></circle>
                            </svg>
                            {isVisitorPreview ? 'Vue Visiteur (actif)' : 'Vue Visiteur'}
                          </button>
                          <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)' }} />
                          <button
                            onClick={async () => {
                              setShowCoachMenu(false);
                              console.log('[COACH] Rafraîchissement...');
                              await loadCoachSessions();
                            }}
                            style={{
                              width: '100%',
                              padding: '10px 14px',
                              textAlign: 'left',
                              fontSize: '12px',
                              color: '#fff',
                              background: 'none',
                              border: 'none',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px'
                            }}
                            className="hover:bg-white/10"
                          >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                              <polyline points="23 4 23 10 17 10"></polyline>
                              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
                            </svg>
                            Rafraîchir
                          </button>
                          <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)' }} />
                          <button
                            onClick={() => {
                              setShowCoachMenu(false);
                              localStorage.clear();
                              sessionStorage.clear();
                              
                              setIsCoachMode(false);
                              setStep('form');
                              setMessages([]);
                              setSessionData(null);
                              setLeadData({ firstName: '', whatsapp: '', email: '' });
                              setSelectedCoachSession(null);
                              setCoachSessions([]);
                              
                              console.log('[COACH] Déconnexion');
                              window.history.replaceState(null, '', window.location.pathname);
                              window.location.reload();
                            }}
                            style={{
                              width: '100%',
                              padding: '10px 14px',
                              textAlign: 'left',
                              fontSize: '12px',
                              color: '#ef4444',
                              background: 'none',
                              border: 'none',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px'
                            }}
                            className="hover:bg-white/10"
                          >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                              <polyline points="16 17 21 12 16 7"></polyline>
                              <line x1="21" y1="12" x2="9" y2="12"></line>
                            </svg>
                            Déconnexion
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                )}

                {/* Liste des sessions ou messages */}
                {!selectedCoachSession ? (
                  <div style={{ flex: 1, overflowY: 'auto', padding: '12px' }}>
                    <div style={{ color: '#fff', fontSize: '12px', marginBottom: '12px', opacity: 0.7 }}>
                      Conversations actives ({coachSessions.length})
                    </div>
                    {coachSessions.length === 0 ? (
                      <div style={{ color: '#fff', opacity: 0.5, textAlign: 'center', padding: '20px', fontSize: '13px' }}>
                        Aucune conversation active
                      </div>
                    ) : (
                      coachSessions.map(session => (
                        <div
                          key={session.id}
                          onClick={() => loadCoachSessionMessages(session)}
                          style={{
                            background: 'rgba(255,255,255,0.05)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '8px',
                            padding: '10px',
                            marginBottom: '8px',
                            cursor: 'pointer'
                          }}
                        >
                          <div style={{ color: '#fff', fontSize: '13px', fontWeight: '500' }}>
                            {session.title || `Session ${session.id.slice(0, 8)}`}
                          </div>
                          <div style={{ color: '#888', fontSize: '11px', marginTop: '4px' }}>
                            {session.mode === 'human' ? 'Mode Humain' : session.mode === 'community' ? 'Communauté' : 'IA'}
                            {' • '}
                            {new Date(session.created_at).toLocaleDateString('fr-FR')}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                ) : (
                  <>
                    {/* Header session sélectionnée */}
                    <div style={{ 
                      padding: '8px 12px', 
                      borderBottom: '1px solid rgba(255,255,255,0.1)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}>
                      <button
                        onClick={() => setSelectedCoachSession(null)}
                        style={{ 
                          background: 'none', 
                          border: 'none', 
                          color: '#d91cd2', 
                          cursor: 'pointer',
                          fontSize: '14px'
                        }}
                      >
                        ← Retour
                      </button>
                      <span style={{ color: '#fff', fontSize: '12px' }}>
                        {selectedCoachSession.title || `Session ${selectedCoachSession.id.slice(0, 8)}`}
                      </span>
                    </div>

                    {/* Messages - SMOOTH SCROLL: overflow-anchor none pour stabilité mobile */}
                    <div style={{ 
                      flex: 1, 
                      overflowY: 'auto', 
                      overflowAnchor: 'none', /* Fix sauts visuels mobile */
                      padding: '12px', 
                      display: 'flex', 
                      flexDirection: 'column', 
                      gap: '8px' 
                    }}>
                      {messages.map((msg, idx) => (
                        <MemoizedMessageBubble 
                          key={msg.id || idx} 
                          msg={msg} 
                          isUser={msg.type === 'coach'}
                          onReservationClick={() => {}}
                        />
                      ))}
                      <div ref={messagesEndRef} />
                    </div>

                    {/* Input coach */}
                    <div style={{ padding: '12px', borderTop: '1px solid rgba(255,255,255,0.1)', display: 'flex', gap: '8px' }}>
                      <input
                        type="text"
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && sendCoachResponse()}
                        placeholder="Votre réponse..."
                        style={{
                          flex: 1,
                          background: 'rgba(255,255,255,0.1)',
                          border: '1px solid rgba(255,255,255,0.2)',
                          borderRadius: '20px',
                          padding: '8px 16px',
                          color: '#fff',
                          fontSize: '13px',
                          outline: 'none'
                        }}
                      />
                      <button
                        type="button"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          sendCoachResponse();
                        }}
                        disabled={isLoading || !inputMessage.trim()}
                        style={{
                          background: inputMessage.trim() ? 'linear-gradient(135deg, #d91cd2, #8b5cf6)' : 'rgba(255,255,255,0.1)',
                          border: 'none',
                          borderRadius: '50%',
                          width: '40px',
                          height: '40px',
                          cursor: inputMessage.trim() ? 'pointer' : 'not-allowed',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          opacity: inputMessage.trim() ? 1 : 0.5
                        }}
                        data-testid="coach-widget-send-btn"
                      >
                        <span style={{ pointerEvents: 'none' }}><SendIcon /></span>
                      </button>
                    </div>
                  </>
                )}
              </div>
            )}
            
            {/* Zone de chat */}
            {step === 'chat' && (
              <>
                {/* Indicateur mode non-IA */}
                {sessionData && !sessionData.is_ai_active && (
                  <div 
                    style={{
                      background: isCommunityMode ? 'rgba(139, 92, 246, 0.2)' : 'rgba(234, 179, 8, 0.2)',
                      padding: '8px 16px',
                      textAlign: 'center',
                      fontSize: '11px',
                      color: isCommunityMode ? '#a78bfa' : '#fbbf24',
                      borderBottom: '1px solid rgba(255,255,255,0.1)'
                    }}
                  >
                    {isCommunityMode 
                      ? 'Mode Communauté - Plusieurs participants' 
                      : privateChatTarget
                      ? `💬 Discussion privée avec ${privateChatTarget.name}`
                      : 'Mode Humain - Le coach vous répondra'}
                  </div>
                )}

                {/* Messages Container - SMOOTH SCROLL: overflow-anchor none pour stabilité mobile */}
                <div 
                  style={{
                    flex: 1,
                    overflowY: 'auto',
                    overflowAnchor: 'none', /* Fix sauts visuels mobile clavier */
                    padding: '16px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '12px',
                    minHeight: 0
                  }}
                >
                  {/* === SKELETON LOADING: Animation pendant le chargement initial === */}
                  {isLoadingHistory && messages.length === 0 && (
                    <MessageSkeleton count={4} />
                  )}
                  
                  {/* === MESSAGES: Affichés dès que disponibles (cache ou API) === */}
                  {messages.map((msg, idx) => (
                    <MemoizedMessageBubble 
                      key={msg.id || idx} 
                      msg={msg} 
                      isUser={msg.type === 'user' && msg.senderId === participantId}
                      onParticipantClick={startPrivateChat}
                      isCommunity={isCommunityMode}
                      currentUserId={participantId}
                      profilePhotoUrl={profilePhoto}
                      onReservationClick={() => setShowReservationPanel(true)}
                    />
                  ))}
                  
                  {/* === INDICATEUR DE SAISIE (Typing Indicator) === */}
                  {typingUser && (
                    <div style={{ alignSelf: 'flex-start', marginTop: '4px' }}>
                      <div
                        style={{
                          background: 'rgba(167, 139, 250, 0.2)',
                          color: '#a78bfa',
                          padding: '8px 14px',
                          borderRadius: '16px 16px 16px 4px',
                          fontSize: '12px',
                          fontStyle: 'italic',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px'
                        }}
                      >
                        <span className="animate-pulse">...</span>
                        <span>{typingUser.type === 'coach' ? 'Coach Bassi' : typingUser.name} est en train d'écrire...</span>
                        <span className="animate-bounce" style={{ animationDelay: '0.1s' }}>.</span>
                        <span className="animate-bounce" style={{ animationDelay: '0.2s' }}>.</span>
                        <span className="animate-bounce" style={{ animationDelay: '0.3s' }}>.</span>
                      </div>
                    </div>
                  )}
                  
                  {isLoading && (
                    <div style={{ alignSelf: 'flex-start' }}>
                      <div
                        style={{
                          background: 'rgba(255,255,255,0.1)',
                          color: '#fff',
                          padding: '10px 14px',
                          borderRadius: '16px 16px 16px 4px',
                          fontSize: '13px'
                        }}
                      >
                        <span className="animate-pulse">...</span>
                      </div>
                    </div>
                  )}
                  
                  <div ref={messagesEndRef} />
                </div>
                
                {/* === PANNEAU DE RÉSERVATION - Extrait vers BookingPanel.js === */}
                {showReservationPanel && afroboostProfile && (
                  <div style={{
                    padding: '12px',
                    borderTop: '1px solid rgba(147, 51, 234, 0.3)',
                    background: 'rgba(0,0,0,0.7)',
                    maxHeight: '300px',
                    overflowY: 'auto'
                  }}>
                    <BookingPanel
                      afroboostProfile={afroboostProfile}
                      availableCourses={availableCourses}
                      selectedCourse={selectedCourse}
                      setSelectedCourse={setSelectedCourse}
                      loadingCourses={loadingCourses}
                      reservationLoading={reservationLoading}
                      reservationError={reservationError}
                      onConfirmReservation={handleConfirmReservation}
                      onClose={() => { setShowReservationPanel(false); setSelectedCourse(null); }}
                    />
                  </div>
                )}
                
                {/* === BOUTON RÉACTIVATION MODE ABONNÉ (Visible en mode visiteur avec profil) === */}
                {!isFullscreen && isVisitorMode && afroboostProfile?.code && step === 'chat' && (
                  <div 
                    style={{
                      padding: '8px 12px',
                      borderTop: '1px solid rgba(147, 51, 234, 0.3)',
                      background: 'linear-gradient(135deg, rgba(147, 51, 234, 0.15), rgba(99, 102, 241, 0.15))',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px'
                    }}
                  >
                    <button
                      onClick={handleReactivateSubscriber}
                      style={{
                        background: 'linear-gradient(135deg, #9333ea, #6366f1)',
                        border: 'none',
                        borderRadius: '20px',
                        padding: '8px 16px',
                        color: '#fff',
                        fontSize: '12px',
                        fontWeight: '600',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        boxShadow: '0 2px 10px rgba(147, 51, 234, 0.3)'
                      }}
                      data-testid="reactivate-subscriber-btn"
                    >
                      Repasser en mode Réservation
                    </button>
                    <span style={{ fontSize: '10px', color: 'rgba(255,255,255,0.5)' }}>
                      ({afroboostProfile.name})
                    </span>
                  </div>
                )}
                
                {/* Input message - Mobile optimized with safe-area + z-index élevé */}
                <div 
                  style={{
                    padding: '12px',
                    paddingBottom: 'max(12px, env(safe-area-inset-bottom, 12px))',
                    borderTop: '1px solid rgba(255,255,255,0.1)',
                    display: 'flex',
                    alignItems: 'center', /* Alignement vertical centré */
                    gap: '8px',
                    flexShrink: 0,
                    position: 'sticky', /* Sticky pour rester visible */
                    bottom: 0,
                    zIndex: 9999, /* Z-index très élevé pour passer devant tout */
                    background: 'rgba(0,0,0,0.98)' /* Fond opaque */
                  }}
                  data-testid="chat-input-bar"
                >
                  {/* === GAUCHE: Emoji + Réservations === */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px', flexShrink: 0 }}>
                    {/* === SÉLECTEUR D'EMOJIS (Composant externe) === */}
                    <EmojiPicker 
                      isOpen={showEmojiPicker}
                      onClose={() => setShowEmojiPicker(false)}
                      onSelect={insertEmoji}
                      position="bottom"
                    />
                    
                    {/* Bouton Emoji */}
                    <button
                      type="button"
                      onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                      style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '50%',
                        background: showEmojiPicker ? '#9333ea' : 'rgba(255,255,255,0.1)',
                        border: 'none',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                        fontSize: '18px'
                      }}
                      data-testid="emoji-btn"
                    >
                      😊
                    </button>
                    
                    {/* Icône Calendrier (Réservation) - UNIQUEMENT visible pour abonnés avec code promo */}
                    {afroboostProfile?.code && (
                      <button
                        type="button"
                        onClick={handleReservationClick}
                        style={{
                          width: '40px',
                          height: '40px',
                          borderRadius: '50%',
                          background: showReservationPanel ? '#9333ea' : 'rgba(147, 51, 234, 0.3)',
                          border: '1px solid rgba(147, 51, 234, 0.5)',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          flexShrink: 0
                        }}
                        title="Réserver un cours (Abonné)"
                        data-testid="calendar-btn"
                      >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={showReservationPanel ? '#fff' : '#a855f7'} strokeWidth="2">
                          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                          <line x1="16" y1="2" x2="16" y2="6"></line>
                          <line x1="8" y1="2" x2="8" y2="6"></line>
                          <line x1="3" y1="10" x2="21" y2="10"></line>
                        </svg>
                      </button>
                    )}
                  </div>
                  
                  {/* === MILIEU: Input texte (flex-grow: 1) === */}
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={handleInputChangeWithTyping}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        emitTyping(false);
                        handleSendMessage();
                      }
                    }}
                    onBlur={handleInputBlur}
                    placeholder="Écrivez votre message..."
                    style={{
                      flex: 1,
                      minWidth: 0, /* Permet au flex de réduire */
                      background: 'rgba(255,255,255,0.1)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '24px',
                      color: '#fff',
                      outline: 'none',
                      fontSize: '16px', /* FIX ZOOM SAFARI iOS */
                      padding: '10px 16px',
                      lineHeight: '1.2'
                    }}
                    data-testid="chat-input"
                  />
                  
                  {/* === DROITE: Bouton Envoyer (toujours à l'extrême droite) === */}
                  <button
                    type="button"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      handleSendMessage();
                    }}
                    disabled={isLoading || !inputMessage.trim()}
                    style={{
                      width: '44px',
                      height: '44px',
                      borderRadius: '50%',
                      background: '#25D366',
                      border: 'none',
                      cursor: isLoading || !inputMessage.trim() ? 'not-allowed' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      opacity: isLoading || !inputMessage.trim() ? 0.5 : 1,
                      flexShrink: 0,
                      marginLeft: 'auto' /* Force à droite */
                    }}
                    data-testid="chat-send-btn"
                  >
                    <span style={{ pointerEvents: 'none' }}><SendIcon /></span>
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* === FENÊTRE FLOTTANTE MP (Composant extrait) === */}
      <PrivateChatView
        activeChat={activePrivateChat ? {
          ...activePrivateChat,
          recipientName: activePrivateChat.recipientName || 
            (activePrivateChat.participant_1_id === participantId 
              ? activePrivateChat.participant_2_name 
              : activePrivateChat.participant_1_name)
        } : null}
        messages={privateMessages}
        inputValue={privateInput}
        setInputValue={setPrivateInput}
        onSend={sendPrivateMessage}
        onClose={closePrivateChat}
        onInputChange={emitDmTyping}
        onInputBlur={() => emitDmTyping(false)}
        typingUser={dmTypingUser}
        isMainChatOpen={isOpen}
      />
      
      {/* === MODALE RECADRAGE PHOTO DE PROFIL === */}
      {showCropModal && cropImageSrc && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.9)',
            zIndex: 10000,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px'
          }}
          data-testid="crop-modal"
        >
          {/* Header minimaliste */}
          <div style={{ 
            color: '#fff', 
            fontSize: '14px', 
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
              <circle cx="8.5" cy="8.5" r="1.5"></circle>
              <polyline points="21 15 16 10 5 21"></polyline>
            </svg>
            Centrer votre visage
          </div>
          
          {/* Zone de prévisualisation circulaire */}
          <div style={{
            width: '200px',
            height: '200px',
            borderRadius: '50%',
            overflow: 'hidden',
            border: '2px solid rgba(255,255,255,0.3)',
            position: 'relative',
            background: '#1a1a1a'
          }}>
            <img
              src={cropImageSrc}
              alt="Aperçu"
              style={{
                position: 'absolute',
                width: `${100 * cropPosition.scale}%`,
                height: 'auto',
                minHeight: `${100 * cropPosition.scale}%`,
                objectFit: 'cover',
                left: `${50 - (50 * cropPosition.scale) + cropPosition.x}%`,
                top: `${50 - (50 * cropPosition.scale) + cropPosition.y}%`,
                transform: 'translate(0, 0)',
                cursor: 'move'
              }}
              draggable={false}
            />
          </div>
          
          {/* Contrôle de zoom */}
          <div style={{ 
            marginTop: '20px', 
            display: 'flex', 
            alignItems: 'center', 
            gap: '12px',
            color: '#888',
            fontSize: '12px'
          }}>
            <span>-</span>
            <input
              type="range"
              min="1"
              max="3"
              step="0.1"
              value={cropPosition.scale}
              onChange={(e) => setCropPosition(prev => ({ ...prev, scale: parseFloat(e.target.value) }))}
              style={{
                width: '150px',
                accentColor: '#9333ea'
              }}
            />
            <span>+</span>
          </div>
          
          {/* Boutons de position */}
          <div style={{ 
            marginTop: '16px', 
            display: 'flex', 
            gap: '8px' 
          }}>
            <button
              onClick={() => setCropPosition(prev => ({ ...prev, y: prev.y - 5 }))}
              style={{ background: 'rgba(255,255,255,0.1)', border: 'none', borderRadius: '4px', padding: '8px', color: '#fff', cursor: 'pointer' }}
            >↑</button>
          </div>
          <div style={{ 
            display: 'flex', 
            gap: '8px' 
          }}>
            <button
              onClick={() => setCropPosition(prev => ({ ...prev, x: prev.x - 5 }))}
              style={{ background: 'rgba(255,255,255,0.1)', border: 'none', borderRadius: '4px', padding: '8px', color: '#fff', cursor: 'pointer' }}
            >←</button>
            <button
              onClick={() => setCropPosition({ x: 0, y: 0, scale: 1 })}
              style={{ background: 'rgba(255,255,255,0.1)', border: 'none', borderRadius: '4px', padding: '8px', color: '#888', cursor: 'pointer', fontSize: '10px' }}
            >Reset</button>
            <button
              onClick={() => setCropPosition(prev => ({ ...prev, x: prev.x + 5 }))}
              style={{ background: 'rgba(255,255,255,0.1)', border: 'none', borderRadius: '4px', padding: '8px', color: '#fff', cursor: 'pointer' }}
            >→</button>
          </div>
          <div style={{ 
            display: 'flex', 
            gap: '8px' 
          }}>
            <button
              onClick={() => setCropPosition(prev => ({ ...prev, y: prev.y + 5 }))}
              style={{ background: 'rgba(255,255,255,0.1)', border: 'none', borderRadius: '4px', padding: '8px', color: '#fff', cursor: 'pointer' }}
            >↓</button>
          </div>
          
          {/* Boutons d'action */}
          <div style={{ 
            marginTop: '24px', 
            display: 'flex', 
            gap: '12px' 
          }}>
            <button
              onClick={() => { setShowCropModal(false); setCropImageSrc(null); }}
              style={{
                background: 'none',
                border: '1px solid rgba(255,255,255,0.3)',
                borderRadius: '8px',
                padding: '10px 24px',
                color: '#fff',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              Annuler
            </button>
            <button
              onClick={handleCropAndUpload}
              disabled={uploadingPhoto}
              style={{
                background: 'linear-gradient(135deg, #9333ea, #6366f1)',
                border: 'none',
                borderRadius: '8px',
                padding: '10px 24px',
                color: '#fff',
                cursor: uploadingPhoto ? 'wait' : 'pointer',
                fontSize: '12px',
                fontWeight: '600',
                opacity: uploadingPhoto ? 0.7 : 1
              }}
              data-testid="crop-confirm-btn"
            >
              {uploadingPhoto ? '⏳ Upload...' : '✓ Valider'}
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default ChatWidget;
