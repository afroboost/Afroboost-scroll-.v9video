/**
 * PartnersCarousel - Scroll vertical style Reels v9.4.8
 * Format 16:9 strict, snap scroll vertical, UI overlay minimaliste
 */
import { useState, useEffect, useRef } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

// Icône Coeur pour Like
const HeartIcon = ({ filled, className = "" }) => (
  <svg 
    width="28" 
    height="28" 
    viewBox="0 0 24 24" 
    fill={filled ? "currentColor" : "none"} 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round"
    className={className}
  >
    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
  </svg>
);

// Icône Son
const SoundIcon = ({ muted }) => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    {muted ? (
      <>
        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
        <line x1="23" y1="9" x2="17" y2="15" />
        <line x1="17" y1="9" x2="23" y2="15" />
      </>
    ) : (
      <>
        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
        <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" />
      </>
    )}
  </svg>
);

// Composant vidéo partenaire - Style Reels minimaliste
const PartnerVideoCard = ({ partner, onClick, onToggleMute, isMuted, onLike, isLiked }) => {
  const videoRef = useRef(null);
  const [hasError, setHasError] = useState(false);
  
  // Extraire l'ID YouTube
  const getYoutubeId = (url) => {
    if (!url) return null;
    const match = url.match(/(?:youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
    return match ? match[1] : null;
  };
  
  // Extraire l'ID Vimeo
  const getVimeoId = (url) => {
    if (!url) return null;
    const match = url.match(/vimeo\.com\/(?:video\/)?(\d+)/);
    return match ? match[1] : null;
  };
  
  const videoUrl = partner.video_url || partner.heroImageUrl;
  const youtubeId = getYoutubeId(videoUrl);
  const vimeoId = getVimeoId(videoUrl);
  const isDirectVideo = videoUrl && videoUrl.match(/\.(mp4|webm|mov|avi)$/i);
  const isImage = videoUrl && videoUrl.match(/\.(jpg|jpeg|png|gif|webp)$/i);
  
  const initial = (partner.name || partner.platform_name || 'P').charAt(0).toUpperCase();
  const displayName = partner.platform_name || partner.name || 'Partenaire';

  return (
    <div 
      className="snap-start snap-always w-full flex-shrink-0 flex items-center justify-center cursor-pointer px-4"
      style={{ 
        height: '70vh',
        minHeight: '350px',
        maxHeight: '550px',
        background: '#000000'
      }}
      onClick={() => onClick(partner)}
      data-testid={`partner-card-${partner.id || partner.email}`}
    >
      {/* Container 16:9 centré - prend toute la largeur disponible */}
      <div 
        className="relative w-full"
        style={{
          aspectRatio: '16/9',
          maxWidth: '100%'
        }}
      >
        {/* Vidéo/Image - Format 16:9 strict */}
        <div className="absolute inset-0 overflow-hidden rounded-xl">
          {youtubeId ? (
            <iframe
              className="absolute inset-0 w-full h-full"
              src={`https://www.youtube.com/embed/${youtubeId}?autoplay=1&mute=${isMuted ? 1 : 0}&loop=1&playlist=${youtubeId}&controls=0&showinfo=0&rel=0&modestbranding=1&playsinline=1`}
              title={displayName}
              frameBorder="0"
              allow="autoplay; encrypted-media"
              style={{ pointerEvents: 'none' }}
            />
          ) : vimeoId ? (
            <iframe
              className="absolute inset-0 w-full h-full"
              src={`https://player.vimeo.com/video/${vimeoId}?autoplay=1&muted=${isMuted ? 1 : 0}&loop=1&background=1`}
              title={displayName}
              frameBorder="0"
              allow="autoplay"
              style={{ pointerEvents: 'none' }}
            />
          ) : isDirectVideo ? (
            <video
              ref={videoRef}
              autoPlay
              loop
              muted={isMuted}
              playsInline
              className="absolute inset-0 w-full h-full object-cover"
              onError={() => setHasError(true)}
            >
              <source src={videoUrl} type="video/mp4" />
            </video>
          ) : isImage ? (
            <img 
              src={videoUrl} 
              alt={displayName}
              className="absolute inset-0 w-full h-full object-cover"
              onError={() => setHasError(true)}
            />
          ) : (
            /* Placeholder animé élégant */
            <div 
              className="absolute inset-0"
              style={{
                background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.4) 0%, rgba(217, 28, 210, 0.4) 100%)'
              }}
            >
              <div 
                className="absolute inset-0 flex items-center justify-center"
                style={{
                  background: 'radial-gradient(circle at 50% 50%, rgba(217, 28, 210, 0.3) 0%, transparent 70%)'
                }}
              >
                <span className="text-6xl opacity-60">🎬</span>
              </div>
            </div>
          )}
          
          {hasError && (
            <div className="absolute inset-0 flex items-center justify-center" style={{ background: 'rgba(139, 92, 246, 0.3)' }}>
              <span className="text-5xl">🎬</span>
            </div>
          )}
        </div>
        
        {/* Overlay gradient discret en bas */}
        <div 
          className="absolute inset-0 pointer-events-none rounded-xl"
          style={{
            background: 'linear-gradient(0deg, rgba(0,0,0,0.7) 0%, transparent 50%)'
          }}
        />
        
        {/* === UI OVERLAY MINIMALISTE === */}
        
        {/* Bouton Son - Haut droite */}
        {(youtubeId || vimeoId || isDirectVideo) && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleMute();
            }}
            className="absolute top-3 right-3 p-2.5 rounded-full transition-all hover:scale-110"
            style={{
              background: 'rgba(0,0,0,0.6)',
              backdropFilter: 'blur(4px)',
              color: 'white'
            }}
            data-testid={`mute-btn-${partner.id || partner.email}`}
          >
            <SoundIcon muted={isMuted} />
          </button>
        )}
        
        {/* Like Button - Droite milieu */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onLike();
          }}
          className="absolute right-3 top-1/2 -translate-y-1/2 p-2 transition-all hover:scale-125 active:scale-95"
          style={{
            color: isLiked ? 'var(--primary-color, #D91CD2)' : 'white',
            filter: isLiked ? 'drop-shadow(0 0 10px var(--primary-color, #D91CD2))' : 'drop-shadow(0 2px 4px rgba(0,0,0,0.5))'
          }}
          data-testid={`like-btn-${partner.id || partner.email}`}
        >
          <HeartIcon filled={isLiked} />
        </button>
        
        {/* Profil + Nom - Bas gauche */}
        <div className="absolute bottom-3 left-3 flex items-center gap-2.5">
          {/* Photo de profil - Petite bulle avec bordure couleur primaire */}
          {partner.photo_url || partner.logo_url ? (
            <img 
              src={partner.photo_url || partner.logo_url} 
              alt={displayName}
              className="w-11 h-11 rounded-full object-cover"
              style={{ 
                border: '2.5px solid var(--primary-color, #D91CD2)',
                boxShadow: '0 0 12px var(--glow-color, rgba(217, 28, 210, 0.5))'
              }}
            />
          ) : (
            <div 
              className="w-11 h-11 rounded-full flex items-center justify-center text-base font-bold"
              style={{ 
                background: 'linear-gradient(135deg, var(--primary-color, #D91CD2) 0%, var(--secondary-color, #8b5cf6) 100%)',
                color: 'white',
                boxShadow: '0 0 12px var(--glow-color, rgba(217, 28, 210, 0.5))'
              }}
            >
              {initial}
            </div>
          )}
          
          {/* Nom du partenaire - Texte fin */}
          <span 
            className="text-white text-base font-medium"
            style={{
              textShadow: '0 2px 4px rgba(0,0,0,0.9)'
            }}
          >
            {displayName}
          </span>
        </div>
      </div>
    </div>
  );
};

const PartnersCarousel = ({ onPartnerClick }) => {
  const [partners, setPartners] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeIndex, setActiveIndex] = useState(0);
  const [mutedStates, setMutedStates] = useState({});
  const [likedStates, setLikedStates] = useState({});
  const sliderRef = useRef(null);
  
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
        console.error('[PARTNERS-REELS] Erreur:', err);
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
  
  // Clic sur un partenaire
  const handlePartnerClick = (partner) => {
    const username = partner.email || partner.id || partner.name?.toLowerCase().replace(/\s+/g, '-');
    if (onPartnerClick) {
      onPartnerClick(partner);
    } else {
      window.location.href = `/coach/${username}`;
    }
  };
  
  if (loading) {
    return (
      <div className="flex items-center justify-center" style={{ height: '70vh', minHeight: '350px', background: '#000000' }}>
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
      {/* Container scroll vertical avec snap */}
      <div 
        ref={sliderRef}
        onScroll={handleScroll}
        className="snap-y snap-mandatory overflow-y-auto"
        style={{ 
          height: '70vh',
          minHeight: '350px',
          maxHeight: '550px',
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
            onClick={handlePartnerClick}
            isMuted={mutedStates[partner.id || partner.email] !== false}
            onToggleMute={() => handleToggleMute(partner.id || partner.email)}
            isLiked={likedStates[partner.id || partner.email] || false}
            onLike={() => handleToggleLike(partner.id || partner.email)}
          />
        ))}
      </div>
      
      {/* Indicateurs verticaux - Droite */}
      {partners.length > 1 && (
        <div className="absolute right-3 top-1/2 -translate-y-1/2 flex flex-col gap-2 z-10">
          {partners.map((_, idx) => (
            <button
              key={idx}
              onClick={() => {
                setActiveIndex(idx);
                if (sliderRef.current) {
                  sliderRef.current.scrollTo({
                    top: idx * sliderRef.current.clientHeight,
                    behavior: 'smooth'
                  });
                }
              }}
              className="transition-all duration-300 rounded-full"
              style={{
                width: '4px',
                height: idx === activeIndex ? '24px' : '8px',
                background: idx === activeIndex ? 'var(--primary-color, #D91CD2)' : 'rgba(255,255,255,0.3)'
              }}
              aria-label={`Voir partenaire ${idx + 1}`}
              data-testid={`partner-dot-${idx}`}
            />
          ))}
        </div>
      )}
      
      {/* Compteur discret en bas */}
      <div 
        className="absolute bottom-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full text-xs text-white/70"
        style={{ background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)' }}
      >
        {activeIndex + 1} / {partners.length}
      </div>
    </div>
  );
};

export default PartnersCarousel;
