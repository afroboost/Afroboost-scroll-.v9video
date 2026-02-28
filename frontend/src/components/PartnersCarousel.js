/**
 * PartnersCarousel - Carousel horizontal des vidéos partenaires v9.4.7
 * Affiche les vidéos de profil des partenaires actifs avec swipe
 */
import { useState, useEffect, useRef } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

// Icône haut-parleur pour le son
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
        <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" />
      </>
    )}
  </svg>
);

// Composant vidéo partenaire individuel
const PartnerVideoCard = ({ partner, onClick, isActive, onToggleMute, isMuted }) => {
  const videoRef = useRef(null);
  const [hasError, setHasError] = useState(false);
  
  // Extraire l'ID YouTube si c'est une URL YouTube
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
  
  // Déterminer le type de média
  const videoUrl = partner.video_url || partner.heroImageUrl;
  const youtubeId = getYoutubeId(videoUrl);
  const vimeoId = getVimeoId(videoUrl);
  const isDirectVideo = videoUrl && videoUrl.match(/\.(mp4|webm|mov|avi)$/i);
  const isImage = videoUrl && videoUrl.match(/\.(jpg|jpeg|png|gif|webp)$/i);
  
  // Photo de profil ou initiale
  const initial = (partner.name || partner.platform_name || 'P').charAt(0).toUpperCase();
  const displayName = partner.platform_name || partner.name || 'Partenaire';

  return (
    <div 
      className="flex-shrink-0 snap-start cursor-pointer transition-all duration-300 hover:scale-105"
      style={{ 
        width: '280px', 
        minWidth: '280px',
        padding: '8px'
      }}
      onClick={() => onClick(partner)}
      data-testid={`partner-card-${partner.id || partner.email}`}
    >
      <div 
        className="relative rounded-2xl overflow-hidden"
        style={{
          height: '400px',
          background: 'linear-gradient(180deg, rgba(10,5,20,1) 0%, rgba(26,10,41,1) 100%)',
          border: isActive ? '3px solid #D91CD2' : '1px solid rgba(217, 28, 210, 0.3)',
          boxShadow: isActive 
            ? '0 0 30px rgba(217, 28, 210, 0.5)' 
            : '0 4px 20px rgba(0,0,0,0.5)'
        }}
      >
        {/* Vidéo/Image de fond */}
        <div className="absolute inset-0">
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
              style={{ filter: 'brightness(0.7)' }}
              onError={() => setHasError(true)}
            />
          ) : (
            /* Placeholder animé si pas de média */
            <div 
              className="absolute inset-0"
              style={{
                background: 'radial-gradient(circle at 50% 30%, rgba(217, 28, 210, 0.3) 0%, transparent 60%)'
              }}
            />
          )}
          
          {hasError && (
            <div className="absolute inset-0 flex items-center justify-center bg-purple-900/50">
              <span className="text-4xl">🎬</span>
            </div>
          )}
        </div>
        
        {/* Overlay gradient */}
        <div 
          className="absolute inset-0"
          style={{
            background: 'linear-gradient(0deg, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.3) 40%, transparent 60%)'
          }}
        />
        
        {/* Bouton son discret */}
        {(youtubeId || vimeoId || isDirectVideo) && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleMute();
            }}
            className="absolute top-3 right-3 p-2 rounded-full transition-all hover:scale-110"
            style={{
              background: isMuted ? 'rgba(217, 28, 210, 0.8)' : 'rgba(0,0,0,0.6)',
              border: '1px solid rgba(255,255,255,0.3)'
            }}
            data-testid={`mute-btn-${partner.id || partner.email}`}
          >
            <SoundIcon muted={isMuted} />
          </button>
        )}
        
        {/* Contenu en bas */}
        <div className="absolute bottom-0 left-0 right-0 p-4">
          {/* Photo de profil */}
          <div className="flex items-center gap-3 mb-3">
            {partner.photo_url || partner.logo_url ? (
              <img 
                src={partner.photo_url || partner.logo_url} 
                alt={displayName}
                className="w-12 h-12 rounded-full object-cover"
                style={{ border: '2px solid rgba(217, 28, 210, 0.6)' }}
                onClick={(e) => {
                  e.stopPropagation();
                  onClick(partner);
                }}
              />
            ) : (
              <div 
                className="w-12 h-12 rounded-full flex items-center justify-center text-lg font-bold"
                style={{ 
                  background: 'linear-gradient(135deg, #D91CD2 0%, #8b5cf6 100%)',
                  color: 'white'
                }}
              >
                {initial}
              </div>
            )}
            <div className="flex-1 min-w-0">
              <h3 className="text-white font-semibold text-lg truncate">{displayName}</h3>
              {partner.bio && (
                <p className="text-white/60 text-xs truncate">{partner.bio}</p>
              )}
            </div>
          </div>
          
          {/* Bouton Voir */}
          <button
            className="w-full py-2.5 rounded-xl text-sm font-semibold transition-all hover:scale-105"
            style={{
              background: 'linear-gradient(135deg, var(--primary-color, #D91CD2) 0%, var(--secondary-color, #8b5cf6) 100%)',
              color: 'white',
              boxShadow: '0 0 15px rgba(217, 28, 210, 0.4)'
            }}
            data-testid={`view-partner-${partner.id || partner.email}`}
          >
            Voir la page
          </button>
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
  const sliderRef = useRef(null);
  
  // Charger les partenaires actifs avec leurs vidéos
  useEffect(() => {
    const fetchPartners = async () => {
      try {
        const res = await axios.get(`${API}/partners/active`);
        setPartners(res.data || []);
        
        // Initialiser tous les partenaires en mode muet
        const initialMuted = {};
        (res.data || []).forEach(p => {
          initialMuted[p.id || p.email] = true;
        });
        setMutedStates(initialMuted);
      } catch (err) {
        console.error('[PARTNERS-CAROUSEL] Erreur:', err);
        setError('Impossible de charger les partenaires');
      } finally {
        setLoading(false);
      }
    };
    fetchPartners();
  }, []);
  
  // Toggle mute pour un partenaire
  const handleToggleMute = (partnerId) => {
    setMutedStates(prev => ({
      ...prev,
      [partnerId]: !prev[partnerId]
    }));
  };
  
  // Scroll handler
  const handleScroll = () => {
    if (sliderRef.current) {
      const scrollLeft = sliderRef.current.scrollLeft;
      const cardWidth = 296; // 280px + 16px padding
      const newIndex = Math.round(scrollLeft / cardWidth);
      if (newIndex !== activeIndex && newIndex >= 0 && newIndex < partners.length) {
        setActiveIndex(newIndex);
      }
    }
  };
  
  // Clic sur un partenaire
  const handlePartnerClick = (partner) => {
    // Rediriger vers la vitrine du partenaire
    const username = partner.email || partner.id || partner.name?.toLowerCase().replace(/\s+/g, '-');
    if (onPartnerClick) {
      onPartnerClick(partner);
    } else {
      window.location.hash = `#coach/${username}`;
    }
  };
  
  if (loading) {
    return (
      <div className="py-8 text-center">
        <div className="animate-spin w-8 h-8 border-3 border-purple-500 border-t-transparent rounded-full mx-auto"></div>
        <p className="text-white/50 text-sm mt-2">Chargement des partenaires...</p>
      </div>
    );
  }
  
  if (error || partners.length === 0) {
    return null; // Ne rien afficher si pas de partenaires
  }
  
  return (
    <div className="mb-8" data-testid="partners-carousel-section">
      {/* Titre */}
      <div className="flex items-center justify-between mb-4 px-2">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="text-xl">🎬</span>
          Nos Partenaires
        </h2>
        <span className="text-white/50 text-sm">
          {partners.length} partenaire{partners.length > 1 ? 's' : ''}
        </span>
      </div>
      
      {/* Carousel */}
      <div 
        ref={sliderRef}
        onScroll={handleScroll}
        className="flex gap-2 overflow-x-auto snap-x snap-mandatory pb-4"
        style={{ 
          scrollBehavior: 'smooth',
          WebkitOverflowScrolling: 'touch',
          scrollbarWidth: 'none',
          msOverflowStyle: 'none'
        }}
        data-testid="partners-slider"
      >
        {partners.map((partner, index) => (
          <PartnerVideoCard
            key={partner.id || partner.email || index}
            partner={partner}
            onClick={handlePartnerClick}
            isActive={index === activeIndex}
            isMuted={mutedStates[partner.id || partner.email] !== false}
            onToggleMute={() => handleToggleMute(partner.id || partner.email)}
          />
        ))}
      </div>
      
      {/* Indicateurs de pagination */}
      {partners.length > 1 && (
        <div className="flex justify-center gap-2 mt-2">
          {partners.map((_, idx) => (
            <button
              key={idx}
              onClick={() => {
                setActiveIndex(idx);
                if (sliderRef.current) {
                  sliderRef.current.scrollTo({
                    left: idx * 296,
                    behavior: 'smooth'
                  });
                }
              }}
              className={`transition-all duration-300 rounded-full ${
                idx === activeIndex 
                  ? 'w-6 h-2 bg-pink-500' 
                  : 'w-2 h-2 bg-white/30 hover:bg-white/50'
              }`}
              aria-label={`Voir partenaire ${idx + 1}`}
              data-testid={`partner-dot-${idx}`}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default PartnersCarousel;
