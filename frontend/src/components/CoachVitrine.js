/**
 * CoachVitrine - Vitrine publique d'un coach v9.1.5 MIROIR
 * Route: /coach/[username]
 * Design miroir de la page Bassi avec CSS Afroboost
 */
import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { QRCodeSVG } from "qrcode.react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

// Offres par défaut Afroboost si le coach n'a pas créé les siennes
const DEFAULT_STARTER_OFFERS = [
  {
    id: 'default-1',
    name: 'Séance découverte',
    description: 'Première séance offerte pour découvrir le concept',
    price: 0,
    imageUrl: 'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=400&h=300&fit=crop'
  },
  {
    id: 'default-2',
    name: 'Pack 5 séances',
    description: 'Idéal pour commencer votre transformation',
    price: 99,
    imageUrl: 'https://images.unsplash.com/photo-1518611012118-696072aa579a?w=400&h=300&fit=crop'
  },
  {
    id: 'default-3',
    name: 'Abonnement mensuel',
    description: 'Accès illimité à toutes les séances du mois',
    price: 149,
    imageUrl: 'https://images.unsplash.com/photo-1549060279-7e168fcee0c2?w=400&h=300&fit=crop'
  }
];

// Icône de localisation
const LocationIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
    <circle cx="12" cy="10" r="3"/>
  </svg>
);

// Composant carte offre avec style Afroboost
const OfferCardVitrine = ({ offer, onSelect }) => {
  const [showDescription, setShowDescription] = useState(false);
  const defaultImage = "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=400&h=300&fit=crop";
  
  const imageUrl = offer.imageUrl || offer.thumbnail || offer.images?.[0] || defaultImage;
  
  return (
    <div 
      className="flex-shrink-0 snap-start"
      style={{ width: '280px', minWidth: '280px', padding: '4px' }}
    >
      <div 
        className="rounded-xl overflow-hidden cursor-pointer transition-all duration-300 hover:scale-[1.02]"
        style={{
          boxShadow: '0 4px 20px rgba(0,0,0,0.4), 0 0 30px rgba(217, 28, 210, 0.2)',
          background: 'linear-gradient(180deg, rgba(20,10,30,0.98) 0%, rgba(5,0,15,0.99) 100%)',
          border: '1px solid rgba(217, 28, 210, 0.3)'
        }}
        onClick={() => onSelect && onSelect(offer)}
        data-testid={`vitrine-offer-${offer.id}`}
      >
        {/* Image Section */}
        <div style={{ position: 'relative', height: '180px', overflow: 'hidden' }}>
          {!showDescription ? (
            <>
              <img 
                src={imageUrl} 
                alt={offer.name} 
                className="w-full h-full object-cover"
                onError={(e) => { e.target.src = defaultImage; }}
              />
              
              {/* Info Icon "i" - Top Right */}
              {offer.description && (
                <div 
                  className="absolute top-3 right-3 w-7 h-7 rounded-full flex items-center justify-center cursor-pointer transition-all hover:scale-110"
                  style={{ 
                    background: 'rgba(217, 28, 210, 0.85)',
                    boxShadow: '0 0 8px rgba(217, 28, 210, 0.5)'
                  }}
                  onClick={(e) => { e.stopPropagation(); setShowDescription(true); }}
                  title="Voir la description"
                >
                  <span className="text-white text-sm font-bold">i</span>
                </div>
              )}
              
              {/* Badge prix 0 = GRATUIT */}
              {offer.price === 0 && (
                <div 
                  className="absolute top-3 left-3 px-3 py-1 rounded-full text-xs font-bold text-white"
                  style={{ 
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', 
                    boxShadow: '0 0 10px rgba(16, 185, 129, 0.5)' 
                  }}
                >
                  GRATUIT
                </div>
              )}
            </>
          ) : (
            /* Description Panel */
            <div 
              className="w-full h-full flex flex-col justify-center p-4"
              style={{ background: 'linear-gradient(180deg, rgba(139, 92, 246, 0.95) 0%, rgba(217, 28, 210, 0.9) 100%)' }}
            >
              <p className="text-white text-sm leading-relaxed">{offer.description}</p>
              <button 
                className="absolute top-3 right-3 w-7 h-7 rounded-full flex items-center justify-center bg-white/20 hover:bg-white/30 transition-all text-white"
                onClick={(e) => { e.stopPropagation(); setShowDescription(false); }}
                title="Fermer"
              >
                ×
              </button>
            </div>
          )}
        </div>
        
        {/* Content Section */}
        <div className="p-4">
          <p className="font-semibold text-white mb-2" style={{ fontSize: '16px' }}>{offer.name}</p>
          <div className="flex items-baseline gap-2">
            <span 
              className="text-xl font-bold" 
              style={{ 
                color: '#d91cd2', 
                textShadow: '0 0 10px rgba(217, 28, 210, 0.4)' 
              }}
            >
              {offer.price === 0 ? 'Offert' : `CHF ${offer.price}.-`}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

// Composant carte cours avec style Afroboost
const CourseCardVitrine = ({ course }) => {
  return (
    <div 
      className="rounded-xl p-4 transition-all duration-300 hover:scale-[1.01]"
      style={{
        background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(217, 28, 210, 0.1) 100%)',
        border: '1px solid rgba(217, 28, 210, 0.3)',
        boxShadow: '0 4px 15px rgba(0,0,0,0.3)'
      }}
      data-testid={`vitrine-course-${course.id}`}
    >
      <h3 className="text-white font-semibold text-lg mb-2">{course.name || course.title}</h3>
      
      {(course.locationName || course.location) && (
        <div className="flex items-center gap-2 text-white/60 text-sm mb-2">
          <LocationIcon />
          <span>{course.locationName || course.location}</span>
        </div>
      )}
      
      {course.description && (
        <p className="text-white/50 text-sm mb-2">{course.description}</p>
      )}
      
      {course.time && (
        <div className="flex items-center gap-2 mt-3">
          <span className="text-lg">⏰</span>
          <span className="text-purple-400 font-medium">{course.time}</span>
        </div>
      )}
      
      {course.weekday !== undefined && (
        <div className="mt-2 px-3 py-1 inline-block rounded-full text-xs font-medium"
          style={{ background: 'rgba(217, 28, 210, 0.2)', color: '#d91cd2' }}>
          {['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'][course.weekday]}
        </div>
      )}
    </div>
  );
};

const CoachVitrine = ({ username, onClose, onBack }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [coach, setCoach] = useState(null);
  const [offers, setOffers] = useState([]);
  const [courses, setCourses] = useState([]);
  const [showQR, setShowQR] = useState(false);
  const sliderRef = useRef(null);

  // URL de la vitrine pour le QR code
  const vitrineUrl = typeof window !== 'undefined' 
    ? `${window.location.origin}/coach/${username}` 
    : '';

  useEffect(() => {
    const fetchVitrine = async () => {
      if (!username) {
        setError('Aucun coach spécifié');
        setLoading(false);
        return;
      }
      
      try {
        const res = await axios.get(`${API}/coach/vitrine/${encodeURIComponent(username)}`);
        setCoach(res.data.coach);
        
        // v9.1.5: Si le coach n'a pas d'offres, utiliser les offres par défaut Afroboost
        const coachOffers = res.data.offers || [];
        if (coachOffers.length === 0) {
          setOffers(DEFAULT_STARTER_OFFERS);
        } else {
          setOffers(coachOffers);
        }
        
        setCourses(res.data.courses || []);
      } catch (err) {
        console.error('[VITRINE] Erreur:', err);
        setError(err.response?.data?.detail || 'Coach non trouvé');
      } finally {
        setLoading(false);
      }
    };
    
    fetchVitrine();
  }, [username]);

  // Partager la vitrine
  const handleShare = async () => {
    const shareData = {
      title: `${coach?.platform_name || coach?.name} - Coach`,
      text: `Découvrez ${coach?.platform_name || coach?.name} sur Afroboost!`,
      url: vitrineUrl
    };
    
    if (navigator.share) {
      try {
        await navigator.share(shareData);
      } catch (err) {
        console.log('Partage annulé');
      }
    } else {
      // Fallback: copier le lien
      navigator.clipboard.writeText(vitrineUrl);
      alert('Lien copié!');
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: 'linear-gradient(180deg, #0a0a0f 0%, #1a0a1f 100%)' }}>
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-white text-lg">Chargement de la vitrine...</p>
        </div>
      </div>
    );
  }

  if (error || !coach) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center flex-col gap-6 p-6" style={{ background: 'linear-gradient(180deg, #0a0a0f 0%, #1a0a1f 100%)' }}>
        <div className="text-center">
          <div className="text-6xl mb-4">😕</div>
          <p className="text-red-400 text-xl font-semibold mb-2">{error || 'Coach non trouvé'}</p>
          <p className="text-white/50">Cette vitrine n'existe pas ou a été désactivée.</p>
        </div>
        <button 
          onClick={onBack || onClose}
          className="px-6 py-3 rounded-xl text-white font-medium transition-all hover:scale-105"
          style={{ 
            background: 'linear-gradient(135deg, #8b5cf6 0%, #d91cd2 100%)',
            boxShadow: '0 0 20px rgba(217, 28, 210, 0.3)'
          }}
        >
          ← Retour à l'accueil
        </button>
      </div>
    );
  }

  // Nom affiché (platform_name prioritaire)
  const displayName = coach.platform_name || coach.name || 'Coach';
  
  // Initiale pour l'avatar par défaut
  const initial = displayName.charAt(0).toUpperCase();

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto" style={{ background: 'linear-gradient(180deg, #0a0a0f 0%, #1a0a1f 100%)' }}>
      
      {/* QR Code Modal */}
      {showQR && (
        <div 
          className="fixed inset-0 z-[60] flex items-center justify-center p-4"
          style={{ background: 'rgba(0,0,0,0.9)' }}
          onClick={() => setShowQR(false)}
        >
          <div 
            className="bg-white rounded-2xl p-8 max-w-sm w-full text-center"
            onClick={e => e.stopPropagation()}
          >
            <h3 className="text-gray-900 font-bold text-xl mb-4">Partagez cette vitrine</h3>
            <div className="bg-white p-4 rounded-xl inline-block mb-4">
              <QRCodeSVG 
                value={vitrineUrl} 
                size={200}
                bgColor="#ffffff"
                fgColor="#1a0a1f"
                level="M"
              />
            </div>
            <p className="text-gray-600 text-sm mb-4 break-all">{vitrineUrl}</p>
            <button
              onClick={() => {
                navigator.clipboard.writeText(vitrineUrl);
                alert('Lien copié!');
              }}
              className="w-full py-3 rounded-xl text-white font-medium"
              style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #d91cd2 100%)' }}
            >
              📋 Copier le lien
            </button>
          </div>
        </div>
      )}
      
      <div className="min-h-screen py-6 px-4">
        <div className="max-w-4xl mx-auto">
          
          {/* Header avec boutons */}
          <div className="flex justify-between items-center mb-6">
            <button 
              onClick={onBack || onClose}
              className="flex items-center gap-2 text-white/60 hover:text-white transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Retour
            </button>
            
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowQR(true)}
                className="p-2 rounded-lg transition-all hover:scale-110"
                style={{ background: 'rgba(217, 28, 210, 0.2)', border: '1px solid rgba(217, 28, 210, 0.3)' }}
                title="QR Code"
                data-testid="vitrine-qr-btn"
              >
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h2M4 12h2m14 0h2M6 20h2m-2-8h2" />
                </svg>
              </button>
              <button
                onClick={handleShare}
                className="p-2 rounded-lg transition-all hover:scale-110"
                style={{ background: 'rgba(139, 92, 246, 0.2)', border: '1px solid rgba(139, 92, 246, 0.3)' }}
                title="Partager"
                data-testid="vitrine-share-btn"
              >
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                </svg>
              </button>
            </div>
          </div>

          {/* Profil Coach - Design miroir Afroboost */}
          <div 
            className="rounded-2xl p-8 mb-8 text-center relative overflow-hidden"
            style={{ 
              background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(217, 28, 210, 0.1) 100%)',
              border: '1px solid rgba(217, 28, 210, 0.3)',
              boxShadow: '0 0 40px rgba(217, 28, 210, 0.15)'
            }}
          >
            {/* Glow effect */}
            <div 
              className="absolute top-0 left-1/2 -translate-x-1/2 w-64 h-64 rounded-full blur-3xl"
              style={{ background: 'rgba(217, 28, 210, 0.1)' }}
            />
            
            {/* Avatar */}
            <div className="relative z-10">
              {coach.logo_url ? (
                <img 
                  src={coach.logo_url} 
                  alt={displayName}
                  className="w-28 h-28 rounded-full mx-auto mb-4 object-cover"
                  style={{ 
                    border: '4px solid #D91CD2',
                    boxShadow: '0 0 30px rgba(217, 28, 210, 0.4)'
                  }}
                />
              ) : coach.photo_url ? (
                <img 
                  src={coach.photo_url} 
                  alt={displayName}
                  className="w-28 h-28 rounded-full mx-auto mb-4 object-cover"
                  style={{ 
                    border: '4px solid #D91CD2',
                    boxShadow: '0 0 30px rgba(217, 28, 210, 0.4)'
                  }}
                />
              ) : (
                <div 
                  className="w-28 h-28 rounded-full mx-auto mb-4 flex items-center justify-center text-4xl font-bold text-white"
                  style={{ 
                    background: 'linear-gradient(135deg, #8b5cf6 0%, #d91cd2 100%)',
                    border: '4px solid #D91CD2',
                    boxShadow: '0 0 30px rgba(217, 28, 210, 0.4)'
                  }}
                >
                  {initial}
                </div>
              )}
              
              <h1 
                className="text-3xl font-bold text-white mb-2"
                style={{ textShadow: '0 0 20px rgba(217, 28, 210, 0.3)' }}
              >
                {displayName}
              </h1>
              
              {coach.bio && (
                <p className="text-white/70 max-w-md mx-auto">{coach.bio}</p>
              )}
              
              {/* Badge Coach Partenaire */}
              <div 
                className="inline-flex items-center gap-2 mt-4 px-4 py-2 rounded-full text-sm"
                style={{ 
                  background: 'linear-gradient(135deg, rgba(217, 28, 210, 0.3), rgba(139, 92, 246, 0.3))',
                  border: '1px solid rgba(217, 28, 210, 0.4)'
                }}
              >
                <span className="text-white font-medium">Coach Partenaire Afroboost</span>
              </div>
            </div>
          </div>

          {/* Section Offres avec Slider horizontal */}
          <div className="mb-8">
            <h2 
              className="font-semibold text-white mb-4 flex items-center gap-3"
              style={{ fontSize: '20px' }}
            >
              <span className="text-2xl">🎯</span>
              {offers === DEFAULT_STARTER_OFFERS ? 'Offres de démarrage Afroboost' : 'Offres disponibles'}
            </h2>
            
            {offers === DEFAULT_STARTER_OFFERS && (
              <p className="text-white/50 text-sm mb-4 italic">
                Ce coach va bientôt proposer ses propres offres. En attendant, découvrez nos offres de démarrage!
              </p>
            )}
            
            <div 
              ref={sliderRef}
              className="flex gap-4 overflow-x-auto snap-x snap-mandatory pb-4"
              style={{ 
                scrollBehavior: 'smooth',
                WebkitOverflowScrolling: 'touch',
                scrollbarWidth: 'none',
                msOverflowStyle: 'none'
              }}
              data-testid="vitrine-offers-slider"
            >
              {offers.map((offer) => (
                <OfferCardVitrine
                  key={offer.id}
                  offer={offer}
                />
              ))}
            </div>
            
            {/* Indicateurs si plusieurs offres */}
            {offers.length > 1 && (
              <div className="flex justify-center gap-2 mt-2">
                {offers.map((_, idx) => (
                  <div
                    key={idx}
                    className="w-2 h-2 rounded-full bg-white/30"
                  />
                ))}
              </div>
            )}
          </div>

          {/* Section Cours */}
          {courses.length > 0 && (
            <div className="mb-8">
              <h2 
                className="font-semibold text-white mb-4 flex items-center gap-3"
                style={{ fontSize: '20px' }}
              >
                <span className="text-2xl">📅</span>
                Cours & Sessions
              </h2>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {courses.map(course => (
                  <CourseCardVitrine key={course.id} course={course} />
                ))}
              </div>
            </div>
          )}

          {/* Section Contact */}
          <div 
            className="rounded-xl p-6 text-center"
            style={{ 
              background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(217, 28, 210, 0.05) 100%)',
              border: '1px solid rgba(217, 28, 210, 0.2)'
            }}
          >
            <p className="text-white/70 mb-4">
              Intéressé(e) par les services de <strong className="text-white">{displayName}</strong> ?
            </p>
            <button
              onClick={handleShare}
              className="px-6 py-3 rounded-xl text-white font-medium transition-all hover:scale-105"
              style={{ 
                background: 'linear-gradient(135deg, #8b5cf6 0%, #d91cd2 100%)',
                boxShadow: '0 0 20px rgba(217, 28, 210, 0.3)'
              }}
              data-testid="vitrine-contact-btn"
            >
              📤 Partager cette vitrine
            </button>
          </div>
          
          {/* Footer Afroboost */}
          <div className="text-center mt-8 pb-8">
            <p className="text-white/30 text-xs">
              Propulsé par <span style={{ color: '#d91cd2' }}>Afroboost</span> - La plateforme des coachs
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CoachVitrine;
