/**
 * PartnersCarousel - Flux vertical Reels v9.4.9 MASTER FUSION
 * - Scroll vertical snap 16:9 strict
 * - UI overlay ultra-minimaliste
 * - Fallback vidéo Bassi si lien invalide
 * - Like collé à la photo de profil
 * - Zone bio 2 lignes max
 */
import { useState, useEffect, useRef } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

// Vidéo par défaut Afroboost (fallback sécurité)
const DEFAULT_VIDEO_URL = "https://www.youtube.com/watch?v=GRoUFFQr3uc";

// Icône Coeur pour Like - Taille réduite pour être collé à la photo
const HeartIcon = ({ filled }) => (
  <svg 
    width="22" 
    height="22" 
    viewBox="0 0 24 24" 
    fill={filled ? "currentColor" : "none"} 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round"
  >
    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
  </svg>
);

// Icône Son discrète
const SoundIcon = ({ muted }) => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    {muted ? (
      <>
        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
        <line x1="23" y1="9" x2="17" y2="15" />
        <line x1="17" y1="9" x2="23" y2="15" />
      </>
    ) : (
      <>
        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
        <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
      </>
    )}
  </svg>
);

// === UTILITAIRES VIDEO ===
const getYoutubeId = (url) => {
  if (!url) return null;
  // Supporte: youtube.com/watch, youtu.be, youtube.com/shorts, youtube.com/embed
  const match = url.match(/(?:youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
  return match ? match[1] : null;
};

const getVimeoId = (url) => {
  if (!url) return null;
  const match = url.match(/vimeo\.com\/(?:video\/)?(\d+)/);
  return match ? match[1] : null;
};

const isDirectVideoFile = (url) => {
  if (!url) return false;
  return /\.(mp4|webm|mov|avi|m4v)(\?|$)/i.test(url);
};

// v9.4.9: Déterminer le type de média et appliquer le fallback si nécessaire
const getMediaInfo = (videoUrl) => {
  const url = videoUrl || DEFAULT_VIDEO_URL;
  const youtubeId = getYoutubeId(url);
  const vimeoId = getVimeoId(url);
  const isDirectVideo = isDirectVideoFile(url);
  
  return {
    url,
    youtubeId,
    vimeoId,
    isDirectVideo,
    hasValidMedia: !!(youtubeId || vimeoId || isDirectVideo),
    isFallback: !videoUrl || (!youtubeId && !vimeoId && !isDirectVideo)
  };
};

// === COMPOSANT VIDEO CARD ===
const PartnerVideoCard = ({ partner, onClick, onToggleMute, isMuted, onLike, isLiked, onNavigate }) => {
  const videoRef = useRef(null);
  const [hasError, setHasError] = useState(false);
  
  // v9.4.9: Utiliser le fallback si pas de vidéo valide
  const videoUrl = partner.video_url || partner.heroImageUrl;
  const mediaInfo = getMediaInfo(videoUrl);
  
  // Si erreur de chargement, utiliser le fallback
  const activeMedia = hasError ? getMediaInfo(DEFAULT_VIDEO_URL) : mediaInfo;
  
  const initial = (partner.name || partner.platform_name || 'P').charAt(0).toUpperCase();
  const displayName = partner.platform_name || partner.name || 'Partenaire';
  const bio = partner.bio || partner.description || '';

  // Handler clic sur l'ensemble Photo/Nom/Bio -> redirection vitrine
  const handleProfileClick = (e) => {
    e.stopPropagation();
    onNavigate(partner);
  };

  return (
    <div 
      className="snap-start snap-always w-full flex-shrink-0 flex items-center justify-center"
      style={{ 
        height: '75vh',
        minHeight: '400px',
        maxHeight: '600px',
        background: '#000000'
      }}
      data-testid={`partner-card-${partner.id || partner.email}`}
    >
      {/* Container 16:9 strict centré */}
      <div 
        className="relative w-full mx-2"
        style={{
          aspectRatio: '16/9',
          maxWidth: 'calc(100% - 16px)'
        }}
      >
        {/* === VIDÉO/IMAGE - Format 16:9 strict === */}
        <div 
          className="absolute inset-0 overflow-hidden"
          style={{ borderRadius: '12px' }}
          onClick={() => onNavigate(partner)}
        >
          {activeMedia.youtubeId ? (
            <iframe
              className="absolute inset-0 w-full h-full"
              src={`https://www.youtube.com/embed/${activeMedia.youtubeId}?autoplay=1&mute=${isMuted ? 1 : 0}&loop=1&playlist=${activeMedia.youtubeId}&controls=0&showinfo=0&rel=0&modestbranding=1&playsinline=1`}
              title={displayName}
              frameBorder="0"
              allow="autoplay; encrypted-media"
              style={{ pointerEvents: 'none' }}
              onError={() => setHasError(true)}
            />
          ) : activeMedia.vimeoId ? (
            <iframe
              className="absolute inset-0 w-full h-full"
              src={`https://player.vimeo.com/video/${activeMedia.vimeoId}?autoplay=1&muted=${isMuted ? 1 : 0}&loop=1&background=1`}
              title={displayName}
              frameBorder="0"
              allow="autoplay"
              style={{ pointerEvents: 'none' }}
              onError={() => setHasError(true)}
            />
          ) : activeMedia.isDirectVideo ? (
            <video
              ref={videoRef}
              autoPlay
              loop
              muted={isMuted}
              playsInline
              className="absolute inset-0 w-full h-full object-cover"
              onError={() => setHasError(true)}
            >
              <source src={activeMedia.url} type="video/mp4" />
            </video>
          ) : (
            /* Placeholder avec gradient Afroboost */
            <div 
              className="absolute inset-0"
              style={{
                background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.5) 0%, rgba(217, 28, 210, 0.4) 100%)'
              }}
            >
              <div 
                className="absolute inset-0 flex items-center justify-center"
                style={{
                  background: 'radial-gradient(circle at 50% 50%, rgba(217, 28, 210, 0.3) 0%, transparent 70%)'
                }}
              >
                <span className="text-5xl opacity-70">🎬</span>
              </div>
            </div>
          )}
        </div>
        
        {/* Overlay gradient très discret en bas pour lisibilité */}
        <div 
          className="absolute inset-0 pointer-events-none"
          style={{
            borderRadius: '12px',
            background: 'linear-gradient(0deg, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0.2) 30%, transparent 60%)'
          }}
        />
        
        {/* === UI OVERLAY ULTRA-MINIMALISTE v9.4.9 === */}
        
        {/* Bouton Son discret - Haut droite */}
        {(activeMedia.youtubeId || activeMedia.vimeoId || activeMedia.isDirectVideo) && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleMute();
            }}
            className="absolute top-3 right-3 p-2 rounded-full transition-all hover:scale-110"
            style={{
              background: 'rgba(0,0,0,0.5)',
              backdropFilter: 'blur(4px)',
              color: 'white'
            }}
            data-testid={`mute-btn-${partner.id || partner.email}`}
          >
            <SoundIcon muted={isMuted} />
          </button>
        )}
        
        {/* === BLOC BAS GAUCHE: Photo + Like + Nom + Bio === */}
        <div 
          className="absolute bottom-3 left-3 right-12 cursor-pointer"
          onClick={handleProfileClick}
          data-testid={`profile-overlay-${partner.id || partner.email}`}
        >
          {/* Ligne 1: Photo + Like + Nom */}
          <div className="flex items-center gap-2 mb-1">
            {/* Photo de profil - Petite bulle */}
            {partner.photo_url || partner.logo_url ? (
              <img 
                src={partner.photo_url || partner.logo_url} 
                alt={displayName}
                className="w-10 h-10 rounded-full object-cover flex-shrink-0"
                style={{ 
                  border: '2px solid var(--primary-color, #D91CD2)',
                  boxShadow: '0 0 10px var(--glow-color, rgba(217, 28, 210, 0.4))'
                }}
              />
            ) : (
              <div 
                className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0"
                style={{ 
                  background: 'linear-gradient(135deg, var(--primary-color, #D91CD2) 0%, var(--secondary-color, #8b5cf6) 100%)',
                  color: 'white',
                  boxShadow: '0 0 10px var(--glow-color, rgba(217, 28, 210, 0.4))'
                }}
              >
                {initial}
              </div>
            )}
            
            {/* Bouton Like COLLÉ à la photo */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                onLike();
              }}
              className="p-1 transition-all hover:scale-125 active:scale-95 flex-shrink-0"
              style={{
                color: isLiked ? 'var(--primary-color, #D91CD2)' : 'white',
                filter: isLiked ? 'drop-shadow(0 0 8px var(--primary-color, #D91CD2))' : 'none'
              }}
              data-testid={`like-btn-${partner.id || partner.email}`}
            >
              <HeartIcon filled={isLiked} />
            </button>
            
            {/* Nom du partenaire */}
            <span 
              className="text-white text-base font-semibold truncate"
              style={{ textShadow: '0 1px 3px rgba(0,0,0,0.9)' }}
            >
              {displayName}
            </span>
          </div>
          
          {/* Ligne 2: Bio (max 2 lignes) */}
          {bio && (
            <p 
              className="text-white/70 text-xs leading-tight ml-12"
              style={{ 
                textShadow: '0 1px 2px rgba(0,0,0,0.8)',
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden'
              }}
            >
              {bio}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

// === COMPOSANT PRINCIPAL ===
const PartnersCarousel = ({ onPartnerClick }) => {
  const [partners, setPartners] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeIndex, setActiveIndex] = useState(0);
  const [mutedStates, setMutedStates] = useState({});
  const [likedStates, setLikedStates] = useState({});
  const sliderRef = useRef(null);
  
  // v9.4.9: Restaurer la position de scroll si on revient du flux
  useEffect(() => {
    const savedIndex = sessionStorage.getItem('afroboost_flux_index');
    if (savedIndex) {
      const idx = parseInt(savedIndex, 10);
      setActiveIndex(idx);
      // Scroll vers cette position après chargement
      setTimeout(() => {
        if (sliderRef.current) {
          sliderRef.current.scrollTo({
            top: idx * sliderRef.current.clientHeight,
            behavior: 'auto'
          });
        }
      }, 100);
      sessionStorage.removeItem('afroboost_flux_index');
    }
  }, [partners]);
  
  // Charger les partenaires actifs
  useEffect(() => {
    const fetchPartners = async () => {
      try {
        const res = await axios.get(`${API}/partners/active`);
        setPartners(res.data || []);
        
        // Initialiser tous en mode muet
        const initialMuted = {};
        (res.data || []).forEach(p => {
          initialMuted[p.id || p.email] = true;
        });
        setMutedStates(initialMuted);
        
        // Charger les likes depuis localStorage
        const savedLikes = localStorage.getItem('afroboost_partner_likes');
        if (savedLikes) {
          setLikedStates(JSON.parse(savedLikes));
        }
      } catch (err) {
        console.error('[FLUX-REELS] Erreur:', err);
        setError('Impossible de charger les partenaires');
      } finally {
        setLoading(false);
      }
    };
    fetchPartners();
  }, []);
  
  // Toggle mute
  const handleToggleMute = (partnerId) => {
    setMutedStates(prev => ({
      ...prev,
      [partnerId]: !prev[partnerId]
    }));
  };
  
  // Toggle like avec persistence
  const handleToggleLike = (partnerId) => {
    setLikedStates(prev => {
      const newState = { ...prev, [partnerId]: !prev[partnerId] };
      localStorage.setItem('afroboost_partner_likes', JSON.stringify(newState));
      return newState;
    });
  };
  
  // Scroll handler vertical
  const handleScroll = () => {
    if (sliderRef.current) {
      const scrollTop = sliderRef.current.scrollTop;
      const cardHeight = sliderRef.current.clientHeight;
      const newIndex = Math.round(scrollTop / cardHeight);
      if (newIndex !== activeIndex && newIndex >= 0 && newIndex < partners.length) {
        setActiveIndex(newIndex);
      }
    }
  };
  
  // v9.4.9: Navigation vers vitrine avec sauvegarde de position
  const handleNavigate = (partner) => {
    // Sauvegarder la position actuelle pour le retour
    sessionStorage.setItem('afroboost_flux_index', activeIndex.toString());
    
    const username = partner.email || partner.id || partner.name?.toLowerCase().replace(/\s+/g, '-');
    if (onPartnerClick) {
      onPartnerClick(partner);
    } else {
      window.location.href = `/coach/${username}`;
    }
  };
  
  if (loading) {
    return (
      <div className="flex items-center justify-center" style={{ height: '75vh', minHeight: '400px', background: '#000000' }}>
        <div className="text-center">
          <div className="animate-spin w-10 h-10 border-3 rounded-full mx-auto mb-3" style={{ borderColor: 'var(--primary-color, #D91CD2)', borderTopColor: 'transparent' }}></div>
          <p className="text-white/50 text-sm">Chargement...</p>
        </div>
      </div>
    );
  }
  
  if (error || partners.length === 0) {
    return null;
  }
  
  return (
    <div 
      className="relative -mx-4"
      style={{ background: '#000000' }}
      data-testid="partners-reels-section"
    >
      {/* v9.4.9: Container scroll vertical SANS indicateurs ni compteur */}
      <div 
        ref={sliderRef}
        onScroll={handleScroll}
        className="snap-y snap-mandatory overflow-y-auto"
        style={{ 
          height: '75vh',
          minHeight: '400px',
          maxHeight: '600px',
          scrollBehavior: 'smooth',
          scrollbarWidth: 'none',
          msOverflowStyle: 'none',
          WebkitOverflowScrolling: 'touch'
        }}
        data-testid="partners-vertical-slider"
      >
        {partners.map((partner, index) => (
          <PartnerVideoCard
            key={partner.id || partner.email || index}
            partner={partner}
            onClick={handleNavigate}
            isMuted={mutedStates[partner.id || partner.email] !== false}
            onToggleMute={() => handleToggleMute(partner.id || partner.email)}
            isLiked={likedStates[partner.id || partner.email] || false}
            onLike={() => handleToggleLike(partner.id || partner.email)}
            onNavigate={handleNavigate}
          />
        ))}
      </div>
      
      {/* v9.4.9: PAS de compteur, PAS d'indicateurs - Interface épurée */}
    </div>
  );
};

export default PartnersCarousel;
