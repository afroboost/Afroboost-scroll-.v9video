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
const CourseCardVitrine = ({ course, onBookClick }) => {
  // v9.2.8: Générer les prochaines dates pour ce cours
  const getNextOccurrences = (weekday, count = 4) => {
    const now = new Date();
    const results = [];
    const day = now.getDay();
    let diff = weekday - day;
    if (diff < 0) diff += 7;
    let current = new Date(now.getFullYear(), now.getMonth(), now.getDate() + diff);
    for (let i = 0; i < count; i++) {
      results.push(new Date(current));
      current.setDate(current.getDate() + 7);
    }
    return results;
  };
  
  const formatDateShort = (d) => {
    return d.toLocaleDateString('fr-CH', { weekday: 'short', day: '2-digit', month: '2-digit' });
  };
  
  const upcomingDates = course.weekday !== undefined ? getNextOccurrences(course.weekday, 4) : [];
  
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
      
      {/* v9.2.8: Dates cliquables pour réservation */}
      {upcomingDates.length > 0 && (
        <div className="mt-3">
          <p className="text-xs text-white/50 mb-2">Prochaines sessions :</p>
          <div className="flex flex-wrap gap-2">
            {upcomingDates.map((date, idx) => (
              <button
                key={idx}
                onClick={() => onBookClick && onBookClick(course, date)}
                className="px-3 py-1.5 rounded-lg text-xs font-medium transition-all hover:scale-105"
                style={{
                  background: 'rgba(217, 28, 210, 0.2)',
                  border: '1px solid rgba(217, 28, 210, 0.4)',
                  color: '#d91cd2',
                  cursor: 'pointer'
                }}
                data-testid={`book-course-${course.id}-${idx}`}
              >
                {formatDateShort(date)} • {course.time}
              </button>
            ))}
          </div>
        </div>
      )}
      
      {course.weekday !== undefined && upcomingDates.length === 0 && (
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
  
  // v9.2.9: Configuration paiement du coach
  const [paymentConfig, setPaymentConfig] = useState({
    stripe: '', paypal: '', twint: '', coachWhatsapp: ''
  });
  
  // v9.3.2: Concept du coach (contient la vidéo header)
  const [coachConcept, setCoachConcept] = useState(null);
  
  // v9.2.8: Modal de réservation pour les cours
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [selectedBooking, setSelectedBooking] = useState(null); // { course, date }
  const [bookingForm, setBookingForm] = useState({ name: '', email: '', whatsapp: '', promoCode: '' });
  const [bookingLoading, setBookingLoading] = useState(false);
  const [bookingSuccess, setBookingSuccess] = useState(false);
  
  // v9.2.9: Code promo
  const [promoMessage, setPromoMessage] = useState({ type: '', text: '' });
  const [appliedDiscount, setAppliedDiscount] = useState(null);
  const [selectedOffer, setSelectedOffer] = useState(null);
  
  // v9.4.6: État pour le bouton d'installation PWA
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [isInstallable, setIsInstallable] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  
  // v9.4.6: Capturer l'événement beforeinstallprompt
  useEffect(() => {
    const handleBeforeInstallPrompt = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setIsInstallable(true);
      console.log('[PWA] Install prompt captured');
    };
    
    // Vérifier si déjà installé
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
    }
    
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', () => {
      setIsInstalled(true);
      setIsInstallable(false);
      console.log('[PWA] App installed');
    });
    
    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);
  
  // v9.4.6: Fonction pour installer l'app PWA
  const handleInstallPWA = async () => {
    if (!deferredPrompt) {
      // Fallback si pas de prompt disponible
      alert(`Pour installer ${displayName} sur votre écran :\n\n📱 Mobile: Utilisez "Ajouter à l'écran d'accueil" dans le menu de votre navigateur.\n\n💻 PC: Cliquez sur l'icône d'installation dans la barre d'adresse de Chrome.`);
      return;
    }
    
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    console.log('[PWA] Install outcome:', outcome);
    
    if (outcome === 'accepted') {
      setIsInstalled(true);
      setIsInstallable(false);
    }
    setDeferredPrompt(null);
  };

  // v9.2.8: Handler clic sur date de cours
  const handleBookClick = (course, date) => {
    setSelectedBooking({ course, date });
    setShowBookingModal(true);
    setBookingSuccess(false);
    setPromoMessage({ type: '', text: '' });
    setAppliedDiscount(null);
  };
  
  // v9.2.9: Valider code promo
  const validatePromoCode = async (code) => {
    if (!code || code.length < 2) {
      setPromoMessage({ type: '', text: '' });
      setAppliedDiscount(null);
      return;
    }
    
    try {
      const res = await axios.post(`${API}/discount-codes/validate`, { 
        code: code.trim(),
        coach_id: coach?.email || username
      });
      
      if (res.data && res.data.valid) {
        const discountCode = res.data.code;
        let discountText = '';
        
        if (discountCode.type === '100%') {
          discountText = `Code validé : GRATUIT`;
        } else if (discountCode.type === '%') {
          discountText = `Code validé : -${discountCode.value}%`;
        } else {
          discountText = `Code validé : -${discountCode.value} CHF`;
        }
        
        setPromoMessage({ type: 'success', text: `✅ ${discountText}` });
        setAppliedDiscount(discountCode);
      } else {
        setPromoMessage({ type: 'error', text: '❌ Code invalide' });
        setAppliedDiscount(null);
      }
    } catch (err) {
      setPromoMessage({ type: 'error', text: '❌ Code invalide ou expiré' });
      setAppliedDiscount(null);
    }
  };
  
  // v9.2.9: Calculer le prix avec réduction
  const calculateFinalPrice = () => {
    if (!selectedOffer) return 0;
    let total = selectedOffer.price || 0;
    
    if (appliedDiscount) {
      if (appliedDiscount.type === '100%') return 0;
      if (appliedDiscount.type === '%') return total * (1 - parseFloat(appliedDiscount.value) / 100);
      if (appliedDiscount.type === 'CHF') return Math.max(0, total - parseFloat(appliedDiscount.value));
    }
    return total;
  };
  
  // v9.2.8: Soumettre réservation
  const handleBookingSubmit = async (e) => {
    e.preventDefault();
    if (!selectedBooking || bookingLoading) return;
    
    setBookingLoading(true);
    try {
      const res = await axios.post(`${API}/reservations`, {
        userName: bookingForm.name,
        userEmail: bookingForm.email,
        userWhatsapp: bookingForm.whatsapp,
        courseId: selectedBooking.course.id,
        courseName: selectedBooking.course.name || selectedBooking.course.title,
        courseTime: selectedBooking.course.time,
        datetime: selectedBooking.date.toISOString(),
        coach_id: coach?.email || username,
        source: 'vitrine_partenaire',
        appliedDiscount: appliedDiscount ? {
          id: appliedDiscount.id,
          code: appliedDiscount.code,
          type: appliedDiscount.type,
          value: appliedDiscount.value
        } : null
      });
      
      if (res.data) {
        // v9.2.9: Marquer le code comme utilisé
        if (appliedDiscount) {
          try {
            await axios.post(`${API}/discount-codes/${appliedDiscount.id}/use`);
          } catch (e) { console.log('[PROMO] Code déjà utilisé ou erreur'); }
        }
        
        setBookingSuccess(true);
        setBookingForm({ name: '', email: '', whatsapp: '', promoCode: '' });
        setTimeout(() => {
          setShowBookingModal(false);
          setSelectedBooking(null);
          setAppliedDiscount(null);
        }, 3000);
      }
    } catch (err) {
      console.error('[BOOKING] Erreur:', err);
      alert(err.response?.data?.detail || 'Erreur lors de la réservation');
    } finally {
      setBookingLoading(false);
    }
  };

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
        
        // v9.3.0: Charger les liens de paiement du coach
        try {
          const paymentRes = await axios.get(`${API}/payment-links/${encodeURIComponent(res.data.coach.email || username)}`);
          setPaymentConfig(paymentRes.data);
        } catch (e) {
          console.log('[VITRINE] Pas de liens de paiement configurés');
        }
        
        // v9.3.2: Charger le concept du coach (pour la vidéo header)
        try {
          const conceptRes = await axios.get(`${API}/concept`, {
            headers: { 'X-User-Email': res.data.coach.email || username }
          });
          setCoachConcept(conceptRes.data);
          console.log('[VITRINE] Concept chargé:', conceptRes.data?.heroImageUrl);
        } catch (e) {
          console.log('[VITRINE] Pas de concept trouvé, utilisation du placeholder');
        }
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
              {/* v9.2.7: Photo et nom du coach en haut à droite */}
              <div className="flex items-center gap-2 mr-2">
                {coach.logo_url ? (
                  <img 
                    src={coach.logo_url} 
                    alt={displayName}
                    className="w-8 h-8 rounded-full object-cover"
                    style={{ border: '2px solid rgba(217, 28, 210, 0.5)' }}
                  />
                ) : (
                  <div 
                    className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold"
                    style={{ 
                      background: 'linear-gradient(135deg, #8b5cf6 0%, #d91cd2 100%)',
                      color: 'white'
                    }}
                  >
                    {initial}
                  </div>
                )}
                <span className="text-white/80 text-sm font-medium hidden sm:block">{displayName}</span>
              </div>
              
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
          
          {/* v9.3.3: HERO CINÉMATOGRAPHIQUE - Miroir exact de Bassi */}
          <div 
            className="relative mb-8 -mx-4 sm:-mx-6 lg:-mx-8"
            style={{ 
              minHeight: '60vh',
              maxHeight: '80vh',
              overflow: 'hidden'
            }}
            data-testid="vitrine-hero-container"
          >
            {/* Vidéo/Image en arrière-plan FULL WIDTH */}
            <div className="absolute inset-0">
              {coachConcept?.heroImageUrl ? (
                <>
                  {/* YouTube */}
                  {(coachConcept.heroImageUrl.includes('youtube.com') || coachConcept.heroImageUrl.includes('youtu.be')) ? (
                    <iframe
                      className="absolute inset-0 w-full h-full scale-125"
                      src={`https://www.youtube.com/embed/${
                        coachConcept.heroImageUrl.match(/(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/)?.[1] || ''
                      }?autoplay=1&mute=1&loop=1&controls=0&showinfo=0&rel=0&modestbranding=1&playsinline=1&playlist=${
                        coachConcept.heroImageUrl.match(/(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/)?.[1] || ''
                      }`}
                      title="Video Background"
                      frameBorder="0"
                      allow="autoplay; encrypted-media"
                      style={{ border: 'none', pointerEvents: 'none' }}
                      data-testid="vitrine-youtube-hero"
                    />
                  ) : coachConcept.heroImageUrl.includes('vimeo.com') ? (
                    /* Vimeo */
                    <iframe
                      className="absolute inset-0 w-full h-full scale-125"
                      src={`https://player.vimeo.com/video/${
                        coachConcept.heroImageUrl.match(/vimeo\.com\/(?:video\/)?(\d+)/)?.[1] || ''
                      }?autoplay=1&muted=1&loop=1&background=1`}
                      title="Video Background"
                      frameBorder="0"
                      allow="autoplay; fullscreen"
                      style={{ border: 'none', pointerEvents: 'none' }}
                      data-testid="vitrine-vimeo-hero"
                    />
                  ) : coachConcept.heroImageUrl.match(/\.(mp4|webm|mov|avi)$/i) ? (
                    /* MP4/Video */
                    <video
                      autoPlay
                      muted
                      loop
                      playsInline
                      className="absolute inset-0 w-full h-full object-cover"
                      style={{ filter: 'brightness(0.7)' }}
                      data-testid="vitrine-mp4-hero"
                    >
                      <source src={coachConcept.heroImageUrl} type="video/mp4" />
                    </video>
                  ) : (
                    /* Image */
                    <img 
                      src={coachConcept.heroImageUrl}
                      alt="Coach Banner"
                      className="absolute inset-0 w-full h-full object-cover"
                      style={{ filter: 'brightness(0.7)' }}
                      data-testid="vitrine-image-hero"
                    />
                  )}
                </>
              ) : coach.video_url ? (
                <video
                  autoPlay
                  muted
                  loop
                  playsInline
                  className="absolute inset-0 w-full h-full object-cover"
                  style={{ filter: 'brightness(0.7)' }}
                >
                  <source src={coach.video_url} type="video/mp4" />
                </video>
              ) : (
                /* Placeholder animé premium */
                <div 
                  className="absolute inset-0"
                  style={{
                    background: 'linear-gradient(180deg, rgba(10,5,20,1) 0%, rgba(26,10,41,1) 50%, rgba(10,5,20,1) 100%)'
                  }}
                >
                  <div 
                    className="absolute inset-0"
                    style={{
                      background: 'radial-gradient(circle at 50% 30%, rgba(217, 28, 210, 0.2) 0%, transparent 50%)',
                      animation: 'pulse 4s ease-in-out infinite'
                    }}
                  />
                </div>
              )}
            </div>
            
            {/* Overlay gradient pour lisibilité du texte */}
            <div 
              className="absolute inset-0"
              style={{
                background: 'linear-gradient(180deg, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.5) 50%, rgba(10,5,20,0.95) 100%)'
              }}
            />
            
            {/* Contenu flottant PAR-DESSUS la vidéo */}
            <div className="relative z-10 h-full flex flex-col items-center justify-center px-4 py-16">
              {/* Logo Afroboost petit */}
              <div 
                className="mb-4"
                style={{
                  filter: 'drop-shadow(0 0 15px rgba(217, 28, 210, 0.5))'
                }}
              >
                <svg width="50" height="50" viewBox="0 0 24 24" fill="none" stroke="#D91CD2" strokeWidth="1.2">
                  <path d="M12 2L2 7l10 5 10-5-10-5z" />
                  <path d="M2 17l10 5 10-5" />
                  <path d="M2 12l10 5 10-5" />
                </svg>
              </div>
              
              {/* v9.4.6: Textes superposés supprimés - Vidéo épurée */}
              {/* Le nom du coach est déjà en haut à droite (ligne 562), pas besoin de le répéter */}
              
              {/* Bouton Réserver avec couleurs dynamiques (v9.4.6) */}
              <button
                onClick={() => {
                  // Scroll vers les cours
                  document.getElementById('vitrine-courses-section')?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="px-8 py-4 rounded-xl text-lg font-semibold transition-all hover:scale-105"
                style={{
                  background: `linear-gradient(135deg, var(--primary-color, #D91CD2) 0%, var(--secondary-color, #8B5CF6) 100%)`,
                  color: 'white',
                  boxShadow: `0 0 30px var(--glow-color, rgba(217, 28, 210, 0.5)), 0 0 60px var(--glow-color-strong, rgba(139, 92, 246, 0.3))`,
                  border: '1px solid rgba(255,255,255,0.2)'
                }}
                data-testid="vitrine-cta-btn"
              >
                Réserver mon cours
              </button>
            </div>
            
            {/* Animation CSS */}
            <style>{`
              @keyframes pulse {
                0%, 100% { opacity: 0.8; }
                50% { opacity: 1; }
              }
            `}</style>
          </div>

          {/* Section Cours - ID pour le scroll */}
          <div id="vitrine-courses-section">
            {/* v9.4.5: Bloc Profil supprimé - Les infos coach sont déjà dans le header vidéo */}
            
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
                  <CourseCardVitrine 
                    key={course.id} 
                    course={course} 
                    onBookClick={handleBookClick}
                  />
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
          {/* Fin de la section vitrine-courses-section */}
        </div>
      </div>
      
      {/* v9.2.8: Modal de réservation */}
      {showBookingModal && selectedBooking && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ background: 'rgba(0,0,0,0.85)' }}
          onClick={() => setShowBookingModal(false)}
        >
          <div 
            className="rounded-xl p-6 w-full max-w-md"
            style={{
              background: 'linear-gradient(180deg, rgba(20,10,30,0.98) 0%, rgba(10,5,20,0.99) 100%)',
              border: '1px solid rgba(217, 28, 210, 0.4)',
              boxShadow: '0 0 40px rgba(217, 28, 210, 0.2)'
            }}
            onClick={e => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-white">📅 Réservation</h3>
              <button 
                onClick={() => setShowBookingModal(false)}
                className="w-8 h-8 rounded-full flex items-center justify-center text-white/60 hover:text-white hover:bg-white/10"
              >
                ✕
              </button>
            </div>
            
            {bookingSuccess ? (
              <div className="text-center py-8">
                <div className="text-5xl mb-4">✅</div>
                <h4 className="text-xl font-bold text-white mb-2">Réservation confirmée !</h4>
                <p className="text-white/60">Vous recevrez une confirmation par email.</p>
              </div>
            ) : (
              <>
                {/* Détails cours */}
                <div 
                  className="rounded-lg p-4 mb-6"
                  style={{ background: 'rgba(217, 28, 210, 0.1)', border: '1px solid rgba(217, 28, 210, 0.2)' }}
                >
                  <p className="text-white font-semibold">{selectedBooking.course.name || selectedBooking.course.title}</p>
                  <p className="text-purple-400 text-sm mt-1">
                    {selectedBooking.date.toLocaleDateString('fr-CH', { weekday: 'long', day: '2-digit', month: 'long' })}
                    {' • '}{selectedBooking.course.time}
                  </p>
                </div>
                
                {/* Formulaire */}
                <form onSubmit={handleBookingSubmit} className="space-y-4">
                  <div>
                    <label className="text-white/60 text-xs mb-1 block">Nom complet</label>
                    <input
                      type="text"
                      required
                      value={bookingForm.name}
                      onChange={e => setBookingForm(prev => ({ ...prev, name: e.target.value }))}
                      className="w-full px-4 py-3 rounded-lg text-white"
                      style={{ background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)' }}
                      placeholder="Votre nom"
                      data-testid="booking-name-input"
                    />
                  </div>
                  
                  <div>
                    <label className="text-white/60 text-xs mb-1 block">Email</label>
                    <input
                      type="email"
                      required
                      value={bookingForm.email}
                      onChange={e => setBookingForm(prev => ({ ...prev, email: e.target.value }))}
                      className="w-full px-4 py-3 rounded-lg text-white"
                      style={{ background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)' }}
                      placeholder="email@example.com"
                      data-testid="booking-email-input"
                    />
                  </div>
                  
                  <div>
                    <label className="text-white/60 text-xs mb-1 block">WhatsApp</label>
                    <input
                      type="tel"
                      required
                      value={bookingForm.whatsapp}
                      onChange={e => setBookingForm(prev => ({ ...prev, whatsapp: e.target.value }))}
                      className="w-full px-4 py-3 rounded-lg text-white"
                      style={{ background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)' }}
                      placeholder="+41 79 XXX XX XX"
                      data-testid="booking-whatsapp-input"
                    />
                  </div>
                  
                  {/* v9.2.9: Champ Code Promo */}
                  <div>
                    <label className="text-white/60 text-xs mb-1 block">Code Promo (optionnel)</label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={bookingForm.promoCode}
                        onChange={e => {
                          setBookingForm(prev => ({ ...prev, promoCode: e.target.value.toUpperCase() }));
                        }}
                        className="flex-1 px-4 py-3 rounded-lg text-white"
                        style={{ 
                          background: appliedDiscount ? 'rgba(34, 197, 94, 0.15)' : 'rgba(255,255,255,0.08)', 
                          border: appliedDiscount ? '1px solid rgba(34, 197, 94, 0.5)' : '1px solid rgba(255,255,255,0.15)' 
                        }}
                        placeholder="CODE123"
                        data-testid="booking-promo-input"
                      />
                      <button
                        type="button"
                        onClick={() => validatePromoCode(bookingForm.promoCode)}
                        className="px-4 py-3 rounded-lg font-medium transition-all hover:scale-105"
                        style={{ 
                          background: 'rgba(217, 28, 210, 0.3)', 
                          border: '1px solid rgba(217, 28, 210, 0.5)',
                          color: '#D91CD2'
                        }}
                        data-testid="validate-promo-btn"
                      >
                        Valider
                      </button>
                    </div>
                    {promoMessage.text && (
                      <p 
                        className={`mt-2 text-sm font-medium ${promoMessage.type === 'success' ? 'text-green-400' : 'text-red-400'}`}
                        data-testid="promo-message-vitrine"
                      >
                        {promoMessage.text}
                      </p>
                    )}
                  </div>
                  
                  {/* v9.2.9: Résumé prix avec réduction */}
                  {selectedOffer && (
                    <div 
                      className="rounded-lg p-3"
                      style={{ background: 'rgba(139, 92, 246, 0.1)', border: '1px solid rgba(139, 92, 246, 0.3)' }}
                    >
                      <div className="flex justify-between text-sm text-white/70">
                        <span>Offre</span>
                        <span>{selectedOffer.price?.toFixed(2) || '0.00'} CHF</span>
                      </div>
                      {appliedDiscount && (
                        <div className="flex justify-between text-sm text-green-400 mt-1">
                          <span>Réduction ({appliedDiscount.code})</span>
                          <span>
                            -{appliedDiscount.type === '100%' ? '100%' : 
                              appliedDiscount.type === '%' ? `${appliedDiscount.value}%` : 
                              `${appliedDiscount.value} CHF`}
                          </span>
                        </div>
                      )}
                      <div className="flex justify-between text-white font-bold mt-2 pt-2 border-t border-white/10">
                        <span>Total</span>
                        <span>{calculateFinalPrice().toFixed(2)} CHF</span>
                      </div>
                    </div>
                  )}
                  
                  {/* v9.4.5: Section paiement épurée - Intégrée directement */}
                  {(paymentConfig.stripe || paymentConfig.twint || paymentConfig.paypal) && (
                    <div className="py-2">
                      <div className="flex flex-wrap gap-2 justify-center">
                        {paymentConfig.stripe && (
                          <a
                            href={paymentConfig.stripe}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full font-medium transition-all hover:scale-105 text-xs"
                            style={{ 
                              background: 'rgba(99, 91, 255, 0.2)',
                              color: '#A5B4FC',
                              border: '1px solid rgba(99, 91, 255, 0.3)'
                            }}
                            data-testid="stripe-payment-btn"
                          >
                            💳 Stripe
                          </a>
                        )}
                        {paymentConfig.twint && (
                          <a
                            href={paymentConfig.twint}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full font-medium transition-all hover:scale-105 text-xs"
                            style={{ 
                              background: 'rgba(255, 255, 255, 0.1)',
                              color: '#E5E7EB',
                              border: '1px solid rgba(255, 255, 255, 0.2)'
                            }}
                            data-testid="twint-payment-btn"
                          >
                            📱 TWINT
                          </a>
                        )}
                        {paymentConfig.paypal && (
                          <a
                            href={paymentConfig.paypal}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full font-medium transition-all hover:scale-105 text-xs"
                            style={{ 
                              background: 'rgba(0, 112, 186, 0.2)',
                              color: '#93C5FD',
                              border: '1px solid rgba(0, 112, 186, 0.3)'
                            }}
                            data-testid="paypal-payment-btn"
                          >
                            💳 PayPal
                          </a>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {/* Message si pas de liens de paiement configurés */}
                  {!paymentConfig.stripe && !paymentConfig.twint && !paymentConfig.paypal && (
                    <div className="text-center text-white/40 text-xs py-2">
                      💡 Réservez d'abord, le paiement sera confirmé par le coach
                    </div>
                  )}
                  
                  {/* v9.4.5: Bouton Confirmer et Payer - Style épuré */}
                  <button
                    type="submit"
                    disabled={bookingLoading}
                    className="w-full py-4 rounded-xl text-white font-semibold transition-all hover:scale-[1.02]"
                    style={{
                      background: bookingLoading 
                        ? 'rgba(139, 92, 246, 0.5)' 
                        : 'linear-gradient(135deg, #D91CD2 0%, #8b5cf6 100%)',
                      boxShadow: bookingLoading ? 'none' : '0 0 25px rgba(217, 28, 210, 0.4)'
                    }}
                    data-testid="confirm-booking-btn"
                  >
                    {bookingLoading ? (
                      <span className="flex items-center justify-center gap-2">
                        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                        </svg>
                        Réservation en cours...
                      </span>
                    ) : (
                      <span className="flex items-center justify-center gap-2">
                        💳 Confirmer et Payer
                      </span>
                    )}
                  </button>
                </form>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CoachVitrine;
