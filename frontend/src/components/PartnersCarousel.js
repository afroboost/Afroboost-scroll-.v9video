/**
 * PartnersCarousel - Flux vertical Reels v9.5.1 ÉPURE TOTALE
 * - Logo Afroboost en haut au centre
 * - Icône recherche en haut à droite
 * - 1 Clic = Play/Pause, Double-clic = Vitrine
 * - Bouton Réserver réduit de 50%
 * - Description en bas, sous le nom
 * - Style Apple/Reels minimaliste
 */
import { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

// Vidéo par défaut Afroboost (fallback sécurité)
const DEFAULT_VIDEO_URL = "https://www.youtube.com/watch?v=GRoUFFQr3uc";

// Logo Afroboost SVG compact
const AfroboostLogo = () => (
  <svg width="28" height="28" viewBox="0 0 40 40" fill="none">
    <defs>
      <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="var(--primary-color, #D91CD2)" />
        <stop offset="100%" stopColor="var(--secondary-color, #8b5cf6)" />
      </linearGradient>
    </defs>
    <circle cx="20" cy="20" r="18" stroke="url(#logoGrad)" strokeWidth="2.5" fill="none" />
    <path d="M20 10 L26 28 H14 L20 10Z" fill="url(#logoGrad)" />
    <circle cx="20" cy="18" r="4" fill="url(#logoGrad)" />
  </svg>
);

// Icône Recherche
const SearchIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8" />
    <path d="m21 21-4.35-4.35" />
  </svg>
);

// Icône Coeur pour Like
const HeartIcon = ({ filled }) => (
  <svg 
    width="20" 
    height="20" 
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
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
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

// Icône Calendrier pour Réserver (compact)
const CalendarIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
    <line x1="16" y1="2" x2="16" y2="6" />
    <line x1="8" y1="2" x2="8" y2="6" />
    <line x1="3" y1="10" x2="21" y2="10" />
  </svg>
);

// === UTILITAIRES VIDEO ===
const getYoutubeId = (url) => {
  if (!url) return null;
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

// === COMPOSANT VIDEO CARD v9.5.1 ===
const PartnerVideoCard = ({ partner, onToggleMute, isMuted, onLike, isLiked, onNavigate, isPaused, onTogglePause }) => {
  const videoRef = useRef(null);
  const [hasError, setHasError] = useState(false);
  const lastClickTime = useRef(0);
  
  const videoUrl = partner.video_url || partner.heroImageUrl;
  const mediaInfo = getMediaInfo(videoUrl);
  const activeMedia = hasError ? getMediaInfo(DEFAULT_VIDEO_URL) : mediaInfo;
  
  const initial = (partner.name || partner.platform_name || 'P').charAt(0).toUpperCase();
  const displayName = partner.platform_name || partner.name || 'Partenaire';
  const bio = partner.bio || partner.description || '';

  // v9.5.1: Gestion clic simple (pause) vs double-clic (navigation)
  const handleVideoClick = useCallback((e) => {
    const now = Date.now();
    const timeDiff = now - lastClickTime.current;
    
    if (timeDiff < 300) {
      // Double-clic -> Navigation vers vitrine
      e.preventDefault();
      onNavigate(partner);
    } else {
      // Simple clic -> Play/Pause
      onTogglePause();
    }
    
    lastClickTime.current = now;
  }, [onNavigate, onTogglePause, partner]);

  // v9.5.1: Bouton Réserver compact (50% plus petit)
  const handleReserve = (e) => {
    e.stopPropagation();
    onNavigate(partner);
  };

  return (
    <div 
      className="snap-start snap-always w-full flex-shrink-0 flex items-center justify-center pt-14"
      style={{ 
        height: 'calc(100vh - 80px)',
        minHeight: '500px',
        maxHeight: '800px',
        background: '#000000'
      }}
      data-testid={`partner-card-${partner.id || partner.email}`}
    >
      {/* Container 16:9 strict - Optimisé pour mobile */}
      <div 
        className="relative w-full"
        style={{
          aspectRatio: '16/9',
          maxWidth: '100%',
          margin: '0 8px'
        }}
      >
        {/* === VIDÉO/IMAGE - Format 16:9 strict === */}
        <div 
          className="absolute inset-0 overflow-hidden cursor-pointer"
          style={{ borderRadius: '16px' }}
          onClick={handleVideoClick}
        >
          {activeMedia.youtubeId ? (
            <iframe
              className="absolute inset-0 w-full h-full"
              src={`https://www.youtube.com/embed/${activeMedia.youtubeId}?autoplay=${isPaused ? 0 : 1}&mute=${isMuted ? 1 : 0}&loop=1&playlist=${activeMedia.youtubeId}&controls=0&showinfo=0&rel=0&modestbranding=1&playsinline=1`}
              title={displayName}
              frameBorder="0"
              allow="autoplay; encrypted-media"
              style={{ pointerEvents: 'none' }}
              onError={() => setHasError(true)}
            />
          ) : activeMedia.vimeoId ? (
            <iframe
              className="absolute inset-0 w-full h-full"
              src={`https://player.vimeo.com/video/${activeMedia.vimeoId}?autoplay=${isPaused ? 0 : 1}&muted=${isMuted ? 1 : 0}&loop=1&background=1`}
              title={displayName}
              frameBorder="0"
              allow="autoplay"
              style={{ pointerEvents: 'none' }}
              onError={() => setHasError(true)}
            />
          ) : activeMedia.isDirectVideo ? (
            <video
              ref={videoRef}
              autoPlay={!isPaused}
              loop
              muted={isMuted}
              playsInline
              className="absolute inset-0 w-full h-full object-cover"
              onError={() => setHasError(true)}
            >
              <source src={activeMedia.url} type="video/mp4" />
            </video>
          ) : (
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
          
          {/* Indicateur Pause au centre */}
          {isPaused && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/30">
              <div 
                className="w-16 h-16 rounded-full flex items-center justify-center"
                style={{ background: 'rgba(255,255,255,0.2)', backdropFilter: 'blur(8px)' }}
              >
                <svg width="32" height="32" viewBox="0 0 24 24" fill="white">
                  <polygon points="5 3 19 12 5 21 5 3" />
                </svg>
              </div>
            </div>
          )}
        </div>
        
        {/* Overlay gradient discret en bas */}
        <div 
          className="absolute inset-0 pointer-events-none"
          style={{
            borderRadius: '16px',
            background: 'linear-gradient(0deg, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.1) 35%, transparent 60%)'
          }}
        />
        
        {/* === UI OVERLAY v9.5.1 ÉPURE TOTALE === */}
        
        {/* Bouton Son - Haut droite (discret) */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggleMute();
          }}
          className="absolute top-3 right-3 p-2 rounded-full transition-all hover:scale-110"
          style={{
            background: 'rgba(0,0,0,0.4)',
            backdropFilter: 'blur(4px)',
            color: 'white'
          }}
          data-testid={`mute-btn-${partner.id || partner.email}`}
        >
          <SoundIcon muted={isMuted} />
        </button>
        
        {/* v9.5.1: Bouton Réserver COMPACT - Bas droite */}
        <button
          onClick={handleReserve}
          className="absolute bottom-3 right-3 flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all hover:scale-105"
          style={{
            background: 'var(--primary-color, #D91CD2)',
            color: 'white',
            boxShadow: '0 2px 8px rgba(0,0,0,0.3)'
          }}
          data-testid={`reserve-btn-${partner.id || partner.email}`}
        >
          <CalendarIcon />
          <span>Réserver</span>
        </button>
        
        {/* === BLOC BAS GAUCHE: Photo + Like + Nom + Bio === */}
        <div 
          className="absolute bottom-3 left-3 right-20"
          data-testid={`profile-overlay-${partner.id || partner.email}`}
        >
          {/* Ligne 1: Photo + Like + Nom */}
          <div className="flex items-center gap-2 mb-0.5">
            {/* Photo de profil */}
            <div 
              className="cursor-pointer"
              onClick={(e) => {
                e.stopPropagation();
                onNavigate(partner);
              }}
            >
              {partner.photo_url || partner.logo_url ? (
                <img 
                  src={partner.photo_url || partner.logo_url} 
                  alt={displayName}
                  className="w-9 h-9 rounded-full object-cover"
                  style={{ 
                    border: '2px solid var(--primary-color, #D91CD2)',
                    boxShadow: '0 0 8px var(--glow-color, rgba(217, 28, 210, 0.4))'
                  }}
                />
              ) : (
                <div 
                  className="w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold"
                  style={{ 
                    background: 'linear-gradient(135deg, var(--primary-color, #D91CD2) 0%, var(--secondary-color, #8b5cf6) 100%)',
                    color: 'white',
                    boxShadow: '0 0 8px var(--glow-color, rgba(217, 28, 210, 0.4))'
                  }}
                >
                  {initial}
                </div>
              )}
            </div>
            
            {/* Bouton Like */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                onLike();
              }}
              className="p-0.5 transition-all hover:scale-125 active:scale-95"
              style={{
                color: isLiked ? 'var(--primary-color, #D91CD2)' : 'white',
                filter: isLiked ? 'drop-shadow(0 0 6px var(--primary-color, #D91CD2))' : 'none'
              }}
              data-testid={`like-btn-${partner.id || partner.email}`}
            >
              <HeartIcon filled={isLiked} />
            </button>
            
            {/* Nom du partenaire */}
            <span 
              className="text-white text-sm font-semibold truncate cursor-pointer"
              style={{ textShadow: '0 1px 3px rgba(0,0,0,0.9)' }}
              onClick={(e) => {
                e.stopPropagation();
                onNavigate(partner);
              }}
            >
              {displayName}
            </span>
          </div>
          
          {/* v9.5.1: Description tout en bas, très sobre */}
          {bio && (
            <p 
              className="text-white/60 text-xs leading-tight pl-11"
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

// === COMPOSANT PRINCIPAL v9.5.1 ===
const PartnersCarousel = ({ onPartnerClick, onSearch }) => {
  const [partners, setPartners] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeIndex, setActiveIndex] = useState(0);
  const [mutedStates, setMutedStates] = useState({});
  const [likedStates, setLikedStates] = useState({});
  const [pausedStates, setPausedStates] = useState({});
  const sliderRef = useRef(null);
  
  // Restaurer la position de scroll si on revient du flux
  useEffect(() => {
    const savedIndex = sessionStorage.getItem('afroboost_flux_index');
    if (savedIndex) {
      const idx = parseInt(savedIndex, 10);
      setActiveIndex(idx);
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
        
        const initialMuted = {};
        const initialPaused = {};
        (res.data || []).forEach(p => {
          initialMuted[p.id || p.email] = true;
          initialPaused[p.id || p.email] = false;
        });
        setMutedStates(initialMuted);
        setPausedStates(initialPaused);
        
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
  
  const handleToggleMute = (partnerId) => {
    setMutedStates(prev => ({ ...prev, [partnerId]: !prev[partnerId] }));
  };
  
  const handleToggleLike = (partnerId) => {
    setLikedStates(prev => {
      const newState = { ...prev, [partnerId]: !prev[partnerId] };
      localStorage.setItem('afroboost_partner_likes', JSON.stringify(newState));
      return newState;
    });
  };
  
  const handleTogglePause = (partnerId) => {
    setPausedStates(prev => ({ ...prev, [partnerId]: !prev[partnerId] }));
  };
  
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
  
  // v9.5.1: Navigation vers vitrine - éviter les doublons
  const handleNavigate = useCallback((partner) => {
    sessionStorage.setItem('afroboost_flux_index', activeIndex.toString());
    
    const username = partner.email || partner.id || partner.name?.toLowerCase().replace(/\s+/g, '-');
    const targetPath = `/coach/${username}`;
    
    // Éviter les doublons de navigation
    if (window.location.pathname !== targetPath) {
      if (onPartnerClick) {
        onPartnerClick(partner);
      } else {
        window.location.href = targetPath;
      }
    }
  }, [activeIndex, onPartnerClick]);
  
  if (loading) {
    return (
      <div className="flex items-center justify-center" style={{ height: 'calc(100vh - 120px)', minHeight: '450px', background: '#000000' }}>
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
      className="relative"
      style={{ background: '#000000' }}
      data-testid="partners-reels-section"
    >
      {/* v9.5.1: HEADER avec Logo Afroboost + Recherche */}
      <div 
        className="absolute top-0 left-0 right-0 z-20 flex items-center justify-between px-4 py-3"
        style={{ background: 'linear-gradient(180deg, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0.6) 60%, transparent 100%)' }}
      >
        {/* Espace gauche (équilibrage) */}
        <div className="w-10"></div>
        
        {/* Logo Afroboost au centre */}
        <div className="flex items-center gap-2" data-testid="afroboost-logo">
          <AfroboostLogo />
          <span 
            className="text-white font-bold text-base"
            style={{ textShadow: '0 1px 3px rgba(0,0,0,0.5)' }}
          >
            Afroboost
          </span>
        </div>
        
        {/* Icône Recherche à droite */}
        <button
          onClick={() => onSearch?.()}
          className="w-10 h-10 flex items-center justify-center rounded-full transition-all hover:scale-110"
          style={{ 
            background: 'rgba(255,255,255,0.1)',
            color: 'white'
          }}
          data-testid="search-btn"
        >
          <SearchIcon />
        </button>
      </div>
      
      {/* Container scroll vertical - Avec header absolu pour utiliser tout l'espace */}
      <div 
        ref={sliderRef}
        onScroll={handleScroll}
        className="snap-y snap-mandatory overflow-y-auto"
        style={{ 
          height: 'calc(100vh - 80px)',
          minHeight: '500px',
          maxHeight: '800px',
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
            isMuted={mutedStates[partner.id || partner.email] !== false}
            onToggleMute={() => handleToggleMute(partner.id || partner.email)}
            isLiked={likedStates[partner.id || partner.email] || false}
            onLike={() => handleToggleLike(partner.id || partner.email)}
            isPaused={pausedStates[partner.id || partner.email] || false}
            onTogglePause={() => handleTogglePause(partner.id || partner.email)}
            onNavigate={handleNavigate}
          />
        ))}
      </div>
    </div>
  );
};

export default PartnersCarousel;
