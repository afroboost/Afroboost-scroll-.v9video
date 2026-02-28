/**
 * BecomeCoachPage - Page "Devenir Partenaire" v9.4.7
 * Permet aux nouveaux partenaires (coachs/vendeurs) de s'inscrire et de payer leur pack
 * v9.4.7: Ajout connexion Google sur cette page avec création de profil "En attente de paiement"
 */
import { useState, useEffect, useRef } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

// Icônes SVG minimalistes
const CheckIcon = () => (
  <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
);

const CrownIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 2L9 9l-7 2 5 5-1 7 6-3 6 3-1-7 5-5-7-2-3-7z" />
  </svg>
);

// Icône Google officielle
const GoogleIcon = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" xmlns="http://www.w3.org/2000/svg">
    <g fill="none" fillRule="evenodd">
      <path d="M17.64 9.205c0-.639-.057-1.252-.164-1.841H9v3.481h4.844a4.14 4.14 0 01-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" fill="#4285F4"/>
      <path d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 009 18z" fill="#34A853"/>
      <path d="M3.964 10.71A5.41 5.41 0 013.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 000 9c0 1.452.348 2.827.957 4.042l3.007-2.332z" fill="#FBBC05"/>
      <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 00.957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z" fill="#EA4335"/>
    </g>
  </svg>
);

const BecomeCoachPage = ({ onClose, onSuccess }) => {
  const [packs, setPacks] = useState([]);
  const [selectedPack, setSelectedPack] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  
  // v9.4.7: État utilisateur connecté via Google
  const [googleUser, setGoogleUser] = useState(null);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const hasProcessedRef = useRef(false);
  
  // Formulaire d'inscription (fallback si pas de Google)
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    promoCode: ''
  });

  // v9.4.7: Vérifier si déjà authentifié au chargement
  useEffect(() => {
    const checkExistingAuth = async () => {
      try {
        const response = await axios.get(`${API}/auth/me`, {
          withCredentials: true
        });
        if (response.data && response.data.email) {
          console.log('[BECOME-COACH] ✅ Déjà connecté:', response.data.email);
          setGoogleUser(response.data);
          // Pré-remplir le formulaire avec les données Google
          setFormData(prev => ({
            ...prev,
            name: response.data.name || '',
            email: response.data.email || ''
          }));
        }
      } catch (err) {
        console.log('[BECOME-COACH] 🔒 Non connecté');
      } finally {
        setIsCheckingAuth(false);
      }
    };
    checkExistingAuth();
  }, []);

  // v9.4.7: Traiter le session_id dans l'URL (callback OAuth sur cette page)
  useEffect(() => {
    const processOAuthCallback = async () => {
      if (hasProcessedRef.current) return;
      
      const hash = window.location.hash;
      if (!hash.includes('session_id=')) return;
      
      hasProcessedRef.current = true;
      setSubmitting(true);
      setError(null);
      
      const sessionId = hash.split('session_id=')[1]?.split('&')[0];
      if (!sessionId) {
        setError("Session invalide");
        setSubmitting(false);
        return;
      }
      
      // Nettoyer l'URL
      window.history.replaceState(null, '', window.location.pathname);
      
      try {
        const response = await axios.post(`${API}/auth/google/session`, 
          { session_id: sessionId },
          { withCredentials: true }
        );
        
        if (response.data.success) {
          const user = response.data.user;
          console.log('[BECOME-COACH] ✅ Google login:', user.email);
          setGoogleUser(user);
          setFormData(prev => ({
            ...prev,
            name: user.name || prev.name,
            email: user.email || prev.email
          }));
          
          // v9.4.7: Créer automatiquement un profil "En attente de paiement"
          await createPendingProfile(user);
        } else {
          setError(response.data.message || "Erreur d'authentification");
        }
      } catch (err) {
        console.error('[BECOME-COACH] ❌ Erreur OAuth:', err);
        setError(err.response?.data?.message || "Erreur d'authentification");
      } finally {
        setSubmitting(false);
      }
    };
    
    processOAuthCallback();
  }, []);

  // v9.4.7: Créer un profil "En attente de paiement" pour les nouveaux utilisateurs Google
  const createPendingProfile = async (user) => {
    try {
      // Vérifier si déjà partenaire
      const checkRes = await axios.get(`${API}/check-partner/${user.email}`);
      if (checkRes.data.is_partner) {
        console.log('[BECOME-COACH] Utilisateur déjà partenaire');
        return;
      }
      
      // Créer un profil en attente (0 crédits = en attente de paiement)
      await axios.post(`${API}/coach/register`, {
        email: user.email,
        name: user.name || user.email.split('@')[0],
        phone: '',
        credits: 0, // 0 crédits = en attente de paiement
        pack_id: null,
        status: 'pending_payment'
      });
      console.log('[BECOME-COACH] ✅ Profil "En attente" créé:', user.email);
    } catch (err) {
      // Ignorer si profil existe déjà (erreur 400)
      if (err.response?.status !== 400) {
        console.error('[BECOME-COACH] Erreur création profil:', err);
      }
    }
  };

  // Charger les packs disponibles
  useEffect(() => {
    const fetchPacks = async () => {
      try {
        const res = await axios.get(`${API}/admin/coach-packs`);
        setPacks(res.data || []);
        if (res.data && res.data.length > 0) {
          setSelectedPack(res.data[0]);
        }
      } catch (err) {
        console.error('[COACH-PACKS] Erreur:', err);
        setError('Impossible de charger les offres');
      } finally {
        setLoading(false);
      }
    };
    fetchPacks();
  }, []);

  // Connexion Google
  const handleGoogleLogin = () => {
    setSubmitting(true);
    setError(null);
    // Rediriger vers Google OAuth avec retour sur cette page
    const redirectUrl = window.location.origin + window.location.pathname + '#become-coach';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Utiliser les données Google si disponibles
    const email = googleUser?.email || formData.email;
    const name = googleUser?.name || formData.name;
    
    if (!name || !email || !selectedPack) {
      setError('Veuillez remplir tous les champs obligatoires');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      // Si pack a un prix Stripe, rediriger vers Stripe Checkout
      if (selectedPack.stripe_price_id && selectedPack.price > 0) {
        const response = await axios.post(`${API}/stripe/create-coach-checkout`, {
          price_id: selectedPack.stripe_price_id,
          pack_id: selectedPack.id,
          email: email,
          name: name,
          phone: formData.phone,
          promo_code: formData.promoCode
        });
        
        if (response.data.checkout_url) {
          window.location.href = response.data.checkout_url;
          return;
        }
      }
      
      // Pack gratuit ou sans Stripe - inscription directe
      const registerRes = await axios.post(`${API}/coach/register`, {
        email: email,
        name: name,
        phone: formData.phone,
        pack_id: selectedPack.id,
        credits: selectedPack.credits
      });
      
      if (registerRes.data) {
        // v9.2.7: Propulsion DIRECTE vers le dashboard après inscription gratuite
        localStorage.setItem('redirect_to_dash', 'true');
        localStorage.setItem('afroboost_redirect_message', '🎉 Bienvenue ! Votre pack est activé.');
        window.location.hash = '#partner-dashboard';
        window.location.reload();
        onSuccess?.(registerRes.data);
      }
    } catch (err) {
      console.error('[REGISTER] Erreur:', err);
      setError(err.response?.data?.detail || 'Erreur lors de l\'inscription');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading || isCheckingAuth) {
    return (
      <div className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center">
        <div className="text-white text-lg">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/95 z-50 overflow-y-auto">
      <div className="min-h-screen py-8 px-4">
        {/* Header */}
        <div className="max-w-4xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-2xl sm:text-3xl font-bold text-white flex items-center gap-3">
              <span style={{ color: '#D91CD2' }}><CrownIcon /></span>
              Devenir Partenaire Afroboost
            </h1>
            <button 
              onClick={onClose}
              className="text-white/60 hover:text-white text-2xl p-2"
              data-testid="close-become-coach"
            >
              ✕
            </button>
          </div>

          {/* v9.4.7: Bouton Google Login si pas connecté */}
          {!googleUser && (
            <div className="glass rounded-2xl p-6 mb-8 text-center" style={{ border: '1px solid rgba(217, 28, 210, 0.5)' }}>
              <h2 className="text-xl font-semibold text-white mb-4">Commencez par vous connecter</h2>
              <p className="text-white/60 text-sm mb-6">
                Connectez-vous avec Google pour simplifier votre inscription
              </p>
              <button
                onClick={handleGoogleLogin}
                disabled={submitting}
                className="inline-flex items-center justify-center gap-3 py-3 px-6 rounded-lg font-medium transition-all duration-200"
                style={{
                  background: '#ffffff',
                  color: '#1f1f1f',
                  cursor: submitting ? 'wait' : 'pointer',
                  opacity: submitting ? 0.7 : 1
                }}
                data-testid="google-login-pack-btn"
              >
                {submitting ? (
                  <div className="animate-spin w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full"></div>
                ) : (
                  <GoogleIcon />
                )}
                <span>{submitting ? 'Connexion...' : 'Se connecter avec Google'}</span>
              </button>
              <p className="text-white/40 text-xs mt-4">
                ou remplissez le formulaire ci-dessous
              </p>
            </div>
          )}

          {/* v9.4.7: Badge utilisateur connecté */}
          {googleUser && (
            <div className="glass rounded-2xl p-4 mb-6 flex items-center gap-4" style={{ border: '1px solid rgba(34, 197, 94, 0.5)', background: 'rgba(34, 197, 94, 0.1)' }}>
              <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center">
                <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div>
                <p className="text-green-400 font-medium">Connecté en tant que</p>
                <p className="text-white text-lg">{googleUser.name || googleUser.email}</p>
                <p className="text-white/60 text-sm">{googleUser.email}</p>
              </div>
            </div>
          )}

          {/* Avantages */}
          <div className="glass rounded-2xl p-6 mb-8" style={{ border: '1px solid rgba(217, 28, 210, 0.3)' }}>
            <h2 className="text-xl font-semibold text-white mb-4">Pourquoi devenir Partenaire Afroboost ?</h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="flex items-start gap-3">
                <CheckIcon />
                <div>
                  <h3 className="text-white font-medium">CRM Automatisé</h3>
                  <p className="text-white/60 text-sm">Tous vos contacts centralisés</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <CheckIcon />
                <div>
                  <h3 className="text-white font-medium">Chat IA Intégré</h3>
                  <p className="text-white/60 text-sm">Assistant virtuel pour vos clients</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <CheckIcon />
                <div>
                  <h3 className="text-white font-medium">Page de Vente Perso</h3>
                  <p className="text-white/60 text-sm">Votre vitrine professionnelle</p>
                </div>
              </div>
            </div>
          </div>

          {/* Packs */}
          <h2 className="text-xl font-semibold text-white mb-4">Choisissez votre Pack</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
            {packs.map(pack => (
              <div
                key={pack.id}
                onClick={() => setSelectedPack(pack)}
                className={`glass rounded-xl p-5 cursor-pointer transition-all hover:scale-105 ${
                  selectedPack?.id === pack.id 
                    ? 'ring-2 ring-purple-500' 
                    : ''
                }`}
                style={{ 
                  border: selectedPack?.id === pack.id 
                    ? '2px solid #D91CD2' 
                    : '1px solid rgba(255,255,255,0.1)'
                }}
                data-testid={`pack-${pack.id}`}
              >
                <h3 className="text-lg font-bold text-white mb-2">{pack.name}</h3>
                <div className="text-3xl font-bold mb-2" style={{ color: '#D91CD2' }}>
                  {pack.price} CHF
                </div>
                <div className="text-white/70 text-sm mb-3">
                  {pack.credits} crédits inclus
                </div>
                {pack.description && (
                  <p className="text-white/50 text-xs mb-3">{pack.description}</p>
                )}
                {pack.features && pack.features.length > 0 && (
                  <ul className="space-y-1">
                    {pack.features.map((feature, idx) => (
                      <li key={idx} className="flex items-center gap-2 text-xs text-white/70">
                        <CheckIcon />
                        {feature}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
            
            {packs.length === 0 && (
              <div className="col-span-full text-center py-8">
                <p className="text-white/60">Aucun pack disponible pour le moment</p>
              </div>
            )}
          </div>

          {/* Formulaire */}
          {selectedPack && (
            <div className="glass rounded-2xl p-6" style={{ border: '1px solid rgba(217, 28, 210, 0.3)' }}>
              <h2 className="text-xl font-semibold text-white mb-4">
                {googleUser ? 'Confirmer vos informations' : 'Vos Informations'}
              </h2>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="text-white/70 text-sm mb-1 block">Nom complet *</label>
                    <input
                      type="text"
                      name="name"
                      value={googleUser?.name || formData.name}
                      onChange={handleInputChange}
                      required
                      disabled={!!googleUser}
                      className="w-full px-4 py-3 rounded-lg disabled:opacity-60"
                      style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', color: '#fff' }}
                      data-testid="coach-name-input"
                    />
                  </div>
                  <div>
                    <label className="text-white/70 text-sm mb-1 block">Email *</label>
                    <input
                      type="email"
                      name="email"
                      value={googleUser?.email || formData.email}
                      onChange={handleInputChange}
                      required
                      disabled={!!googleUser}
                      className="w-full px-4 py-3 rounded-lg disabled:opacity-60"
                      style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', color: '#fff' }}
                      data-testid="coach-email-input"
                    />
                  </div>
                  <div>
                    <label className="text-white/70 text-sm mb-1 block">Téléphone</label>
                    <input
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 rounded-lg"
                      style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', color: '#fff' }}
                      data-testid="coach-phone-input"
                    />
                  </div>
                  <div>
                    <label className="text-white/70 text-sm mb-1 block">Code Promo</label>
                    <input
                      type="text"
                      name="promoCode"
                      value={formData.promoCode}
                      onChange={handleInputChange}
                      placeholder="Optionnel"
                      className="w-full px-4 py-3 rounded-lg"
                      style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', color: '#fff' }}
                      data-testid="coach-promo-input"
                    />
                  </div>
                </div>

                {error && (
                  <div className="p-3 rounded-lg bg-red-500/20 border border-red-500/50 text-red-300 text-sm">
                    {error}
                  </div>
                )}

                {/* Récapitulatif */}
                <div className="pt-4 border-t border-white/10">
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-white/70">Pack sélectionné:</span>
                    <span className="text-white font-semibold">{selectedPack.name}</span>
                  </div>
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-white/70">Crédits inclus:</span>
                    <span className="text-white font-semibold">{selectedPack.credits}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-white text-lg">Total:</span>
                    <span className="text-2xl font-bold" style={{ color: '#D91CD2' }}>
                      {selectedPack.price} CHF
                    </span>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={submitting || (!googleUser && (!formData.name || !formData.email))}
                  className="w-full py-4 rounded-xl text-white font-bold text-lg transition-all hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{ background: 'linear-gradient(135deg, #D91CD2, #8b5cf6)' }}
                  data-testid="submit-coach-registration"
                >
                  {submitting ? 'Traitement...' : selectedPack.price > 0 ? `Payer ${selectedPack.price} CHF` : 'S\'inscrire gratuitement'}
                </button>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BecomeCoachPage;
