/**
 * CoachVitrine - Vitrine publique d'un coach v8.9.6
 * Route: /coach/[username]
 * Affiche le profil du coach + ses offres et cours
 */
import { useState, useEffect } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const CoachVitrine = ({ username, onClose, onBack }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [coach, setCoach] = useState(null);
  const [offers, setOffers] = useState([]);
  const [courses, setCourses] = useState([]);

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
        setOffers(res.data.offers || []);
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

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black z-50 flex items-center justify-center">
        <div className="text-white text-lg">Chargement...</div>
      </div>
    );
  }

  if (error || !coach) {
    return (
      <div className="fixed inset-0 bg-black z-50 flex items-center justify-center flex-col gap-4">
        <div className="text-red-400 text-lg">{error || 'Coach non trouvé'}</div>
        <button 
          onClick={onBack || onClose}
          className="px-4 py-2 rounded-lg bg-purple-500 text-white"
        >
          Retour
        </button>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black z-50 overflow-y-auto">
      <div className="min-h-screen py-8 px-4">
        <div className="max-w-4xl mx-auto">
          {/* Header avec bouton retour */}
          <div className="flex justify-between items-center mb-6">
            <button 
              onClick={onBack || onClose}
              className="text-white/60 hover:text-white flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Retour
            </button>
          </div>

          {/* Profil Coach */}
          <div className="glass rounded-2xl p-6 mb-6 text-center" style={{ border: '1px solid rgba(217, 28, 210, 0.3)' }}>
            {coach.photo_url ? (
              <img 
                src={coach.photo_url} 
                alt={coach.name}
                className="w-24 h-24 rounded-full mx-auto mb-4 object-cover"
                style={{ border: '3px solid #D91CD2' }}
              />
            ) : (
              <div 
                className="w-24 h-24 rounded-full mx-auto mb-4 flex items-center justify-center text-3xl"
                style={{ background: 'rgba(217, 28, 210, 0.2)', border: '3px solid #D91CD2' }}
              >
                {coach.name?.charAt(0)?.toUpperCase() || '?'}
              </div>
            )}
            <h1 className="text-2xl font-bold text-white mb-2">{coach.name}</h1>
            {coach.bio && <p className="text-white/70">{coach.bio}</p>}
          </div>

          {/* Offres du Coach */}
          {offers.length > 0 && (
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-white mb-4">Offres</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {offers.map(offer => (
                  <div 
                    key={offer.id}
                    className="glass rounded-xl p-4"
                    style={{ border: '1px solid rgba(255,255,255,0.1)' }}
                  >
                    {offer.imageUrl && (
                      <img 
                        src={offer.imageUrl} 
                        alt={offer.name}
                        className="w-full h-32 object-cover rounded-lg mb-3"
                      />
                    )}
                    <h3 className="text-white font-medium">{offer.name}</h3>
                    <p className="text-white/50 text-sm mb-2">{offer.description}</p>
                    <div className="flex justify-between items-center">
                      <span className="text-lg font-bold" style={{ color: '#D91CD2' }}>
                        {offer.price} CHF
                      </span>
                      <button className="px-3 py-1 rounded-lg text-sm text-white"
                        style={{ background: 'linear-gradient(135deg, #D91CD2, #8b5cf6)' }}
                      >
                        Réserver
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Cours du Coach */}
          {courses.length > 0 && (
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-white mb-4">Cours</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {courses.map(course => (
                  <div 
                    key={course.id}
                    className="glass rounded-xl p-4"
                    style={{ border: '1px solid rgba(255,255,255,0.1)' }}
                  >
                    <h3 className="text-white font-medium">{course.title}</h3>
                    <p className="text-white/50 text-sm">{course.description}</p>
                    {course.time && <p className="text-purple-400 text-sm mt-2">{course.time}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Message si aucune offre/cours */}
          {offers.length === 0 && courses.length === 0 && (
            <div className="text-center py-8 text-white/50">
              Ce coach n'a pas encore publié d'offres ou de cours.
            </div>
          )}

          {/* Contact */}
          <div className="glass rounded-xl p-4 text-center" style={{ border: '1px solid rgba(217, 28, 210, 0.2)' }}>
            <p className="text-white/70 text-sm">
              Contactez {coach.name} pour plus d'informations
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CoachVitrine;
