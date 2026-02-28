/**
 * BecomeCoachPage - Page "Devenir Partenaire" v9.1.6
 * Permet aux nouveaux partenaires (coachs/vendeurs) de s'inscrire et de payer leur pack
 */
import { useState, useEffect } from "react";
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

const BecomeCoachPage = ({ onClose, onSuccess }) => {
  const [packs, setPacks] = useState([]);
  const [selectedPack, setSelectedPack] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  
  // Formulaire d'inscription
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    promoCode: ''
  });

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

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name || !formData.email || !selectedPack) {
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
          email: formData.email,
          name: formData.name,
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
        email: formData.email,
        name: formData.name,
        phone: formData.phone,
        pack_id: selectedPack.id,
        credits: selectedPack.credits
      });
      
      if (registerRes.data) {
        // v9.2.7: Propulsion DIRECTE vers le dashboard après inscription gratuite
        localStorage.setItem('redirect_to_dash', 'true');
        localStorage.setItem('afroboost_redirect_message', '🎉 Bienvenue ! Votre pack est activé.');
        window.location.hash = '#partner-dashboard';
        window.location.reload(); // Force refresh pour déclencher le modal login
        onSuccess?.(registerRes.data);
      }
    } catch (err) {
      console.error('[REGISTER] Erreur:', err);
      setError(err.response?.data?.detail || 'Erreur lors de l\'inscription');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
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
              <h2 className="text-xl font-semibold text-white mb-4">Vos Informations</h2>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="text-white/70 text-sm mb-1 block">Nom complet *</label>
                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      required
                      className="w-full px-4 py-3 rounded-lg"
                      style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', color: '#fff' }}
                      data-testid="coach-name-input"
                    />
                  </div>
                  <div>
                    <label className="text-white/70 text-sm mb-1 block">Email *</label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                      className="w-full px-4 py-3 rounded-lg"
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
                  disabled={submitting || !formData.name || !formData.email}
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
