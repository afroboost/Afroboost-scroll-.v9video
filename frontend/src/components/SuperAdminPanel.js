/**
 * SuperAdminPanel - Panneau de contrôle Super Admin v8.9
 * Permet de gérer les packs coach, les tarifs et les coachs partenaires
 */
import { useState, useEffect } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

// Icônes SVG
const CrownIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 2L9 9l-7 2 5 5-1 7 6-3 6 3-1-7 5-5-7-2-3-7z" />
  </svg>
);

const PlusIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
  </svg>
);

const EditIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
  </svg>
);

const TrashIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
  </svg>
);

const SuperAdminPanel = ({ userEmail, onClose }) => {
  const [activeTab, setActiveTab] = useState('packs');
  const [packs, setPacks] = useState([]);
  const [coaches, setCoaches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingPack, setEditingPack] = useState(null);
  const [showPackForm, setShowPackForm] = useState(false);
  const [error, setError] = useState(null);
  
  const [packForm, setPackForm] = useState({
    name: '',
    price: '',
    credits: '',
    description: '',
    features: ''
  });

  // Charger les données
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [packsRes, coachesRes] = await Promise.all([
          axios.get(`${API}/admin/coach-packs/all`, { headers: { 'X-User-Email': userEmail } }),
          axios.get(`${API}/admin/coaches`, { headers: { 'X-User-Email': userEmail } })
        ]);
        setPacks(packsRes.data || []);
        setCoaches(coachesRes.data || []);
      } catch (err) {
        console.error('[ADMIN] Erreur:', err);
        setError(err.response?.data?.detail || 'Erreur de chargement');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [userEmail]);

  // Créer/Modifier un pack
  const handleSavePack = async () => {
    try {
      const data = {
        name: packForm.name,
        price: parseFloat(packForm.price) || 0,
        credits: parseInt(packForm.credits) || 0,
        description: packForm.description,
        features: packForm.features.split('\n').filter(f => f.trim()),
        visible: true
      };

      if (editingPack) {
        await axios.put(`${API}/admin/coach-packs/${editingPack.id}`, data, {
          headers: { 'X-User-Email': userEmail }
        });
      } else {
        await axios.post(`${API}/admin/coach-packs`, data, {
          headers: { 'X-User-Email': userEmail }
        });
      }

      // Recharger les packs
      const res = await axios.get(`${API}/admin/coach-packs/all`, { headers: { 'X-User-Email': userEmail } });
      setPacks(res.data || []);
      
      setShowPackForm(false);
      setEditingPack(null);
      setPackForm({ name: '', price: '', credits: '', description: '', features: '' });
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la sauvegarde');
    }
  };

  // Supprimer un pack
  const handleDeletePack = async (packId) => {
    if (!window.confirm('Supprimer ce pack ?')) return;
    try {
      await axios.delete(`${API}/admin/coach-packs/${packId}`, {
        headers: { 'X-User-Email': userEmail }
      });
      setPacks(prev => prev.filter(p => p.id !== packId));
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la suppression');
    }
  };

  // Éditer un pack
  const startEditPack = (pack) => {
    setEditingPack(pack);
    setPackForm({
      name: pack.name || '',
      price: pack.price?.toString() || '',
      credits: pack.credits?.toString() || '',
      description: pack.description || '',
      features: (pack.features || []).join('\n')
    });
    setShowPackForm(true);
  };

  // Ajouter des crédits à un coach
  const handleAddCredits = async (coachEmail, credits) => {
    try {
      await axios.post(`${API}/coach/add-credits`, {
        coach_email: coachEmail,
        credits: credits
      }, { headers: { 'X-User-Email': userEmail } });
      
      // Recharger les coachs
      const res = await axios.get(`${API}/admin/coaches`, { headers: { 'X-User-Email': userEmail } });
      setCoaches(res.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de l\'ajout des crédits');
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/95 z-50 flex items-center justify-center">
        <div className="text-white">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/95 z-50 overflow-y-auto">
      <div className="min-h-screen py-6 px-4">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-3">
              <span style={{ color: '#D91CD2' }}><CrownIcon /></span>
              <h1 className="text-2xl font-bold text-white">Panneau Super Admin</h1>
            </div>
            <button 
              onClick={onClose}
              className="text-white/60 hover:text-white text-2xl p-2"
              data-testid="close-admin-panel"
            >
              ✕
            </button>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-6 border-b border-white/10 pb-2">
            <button
              onClick={() => setActiveTab('packs')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'packs' 
                  ? 'bg-purple-500/30 text-white' 
                  : 'text-white/60 hover:text-white hover:bg-white/10'
              }`}
              data-testid="tab-packs"
            >
              Packs Coach ({packs.length})
            </button>
            <button
              onClick={() => setActiveTab('coaches')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'coaches' 
                  ? 'bg-purple-500/30 text-white' 
                  : 'text-white/60 hover:text-white hover:bg-white/10'
              }`}
              data-testid="tab-coaches"
            >
              Coachs Partenaires ({coaches.length})
            </button>
          </div>

          {/* Erreur */}
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-500/20 border border-red-500/50 text-red-300 text-sm">
              {error}
              <button onClick={() => setError(null)} className="ml-2 text-red-400 hover:text-red-300">✕</button>
            </div>
          )}

          {/* Tab Packs */}
          {activeTab === 'packs' && (
            <div className="space-y-4">
              {/* Bouton Créer */}
              <button
                onClick={() => {
                  setEditingPack(null);
                  setPackForm({ name: '', price: '', credits: '', description: '', features: '' });
                  setShowPackForm(true);
                }}
                className="flex items-center gap-2 px-4 py-2 rounded-lg text-white font-medium transition-all hover:scale-105"
                style={{ background: 'linear-gradient(135deg, #D91CD2, #8b5cf6)' }}
                data-testid="create-pack-btn"
              >
                <PlusIcon />
                Créer un Pack
              </button>

              {/* Formulaire Pack */}
              {showPackForm && (
                <div className="glass rounded-xl p-5" style={{ border: '1px solid rgba(217, 28, 210, 0.3)' }}>
                  <h3 className="text-lg font-semibold text-white mb-4">
                    {editingPack ? 'Modifier le Pack' : 'Nouveau Pack'}
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="text-white/70 text-sm mb-1 block">Nom *</label>
                      <input
                        type="text"
                        value={packForm.name}
                        onChange={(e) => setPackForm(prev => ({ ...prev, name: e.target.value }))}
                        className="w-full px-4 py-3 rounded-lg"
                        style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', color: '#fff' }}
                        data-testid="pack-name-input"
                      />
                    </div>
                    <div>
                      <label className="text-white/70 text-sm mb-1 block">Prix (CHF) *</label>
                      <input
                        type="number"
                        value={packForm.price}
                        onChange={(e) => setPackForm(prev => ({ ...prev, price: e.target.value }))}
                        className="w-full px-4 py-3 rounded-lg"
                        style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', color: '#fff' }}
                        data-testid="pack-price-input"
                      />
                    </div>
                    <div>
                      <label className="text-white/70 text-sm mb-1 block">Crédits inclus *</label>
                      <input
                        type="number"
                        value={packForm.credits}
                        onChange={(e) => setPackForm(prev => ({ ...prev, credits: e.target.value }))}
                        className="w-full px-4 py-3 rounded-lg"
                        style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', color: '#fff' }}
                        data-testid="pack-credits-input"
                      />
                    </div>
                    <div>
                      <label className="text-white/70 text-sm mb-1 block">Description</label>
                      <input
                        type="text"
                        value={packForm.description}
                        onChange={(e) => setPackForm(prev => ({ ...prev, description: e.target.value }))}
                        className="w-full px-4 py-3 rounded-lg"
                        style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', color: '#fff' }}
                        data-testid="pack-description-input"
                      />
                    </div>
                    <div className="sm:col-span-2">
                      <label className="text-white/70 text-sm mb-1 block">Fonctionnalités (une par ligne)</label>
                      <textarea
                        value={packForm.features}
                        onChange={(e) => setPackForm(prev => ({ ...prev, features: e.target.value }))}
                        rows={3}
                        placeholder="CRM automatisé&#10;Chat IA intégré&#10;Page de vente"
                        className="w-full px-4 py-3 rounded-lg resize-none"
                        style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', color: '#fff' }}
                        data-testid="pack-features-input"
                      />
                    </div>
                  </div>
                  <div className="flex justify-end gap-3 mt-4">
                    <button
                      onClick={() => { setShowPackForm(false); setEditingPack(null); }}
                      className="px-4 py-2 rounded-lg text-white/70 hover:text-white hover:bg-white/10"
                    >
                      Annuler
                    </button>
                    <button
                      onClick={handleSavePack}
                      disabled={!packForm.name || !packForm.price || !packForm.credits}
                      className="px-6 py-2 rounded-lg text-white font-medium transition-all hover:scale-105 disabled:opacity-50"
                      style={{ background: 'linear-gradient(135deg, #D91CD2, #8b5cf6)' }}
                      data-testid="save-pack-btn"
                    >
                      {editingPack ? 'Modifier' : 'Créer'}
                    </button>
                  </div>
                </div>
              )}

              {/* Liste des Packs */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {packs.map(pack => (
                  <div 
                    key={pack.id}
                    className="glass rounded-xl p-5"
                    style={{ border: '1px solid rgba(255,255,255,0.1)' }}
                    data-testid={`pack-card-${pack.id}`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="text-lg font-bold text-white">{pack.name}</h3>
                      <div className="flex gap-1">
                        <button
                          onClick={() => startEditPack(pack)}
                          className="p-1.5 rounded-lg text-white/60 hover:text-white hover:bg-white/10"
                        >
                          <EditIcon />
                        </button>
                        <button
                          onClick={() => handleDeletePack(pack.id)}
                          className="p-1.5 rounded-lg text-red-400 hover:text-red-300 hover:bg-red-500/10"
                        >
                          <TrashIcon />
                        </button>
                      </div>
                    </div>
                    <div className="text-2xl font-bold mb-1" style={{ color: '#D91CD2' }}>
                      {pack.price} CHF
                    </div>
                    <div className="text-white/60 text-sm mb-2">{pack.credits} crédits</div>
                    {pack.description && <p className="text-white/50 text-xs mb-2">{pack.description}</p>}
                    <div className="flex items-center gap-2 text-xs text-white/40">
                      {pack.stripe_price_id ? (
                        <span className="px-2 py-0.5 rounded-full bg-green-500/20 text-green-400">Stripe OK</span>
                      ) : (
                        <span className="px-2 py-0.5 rounded-full bg-yellow-500/20 text-yellow-400">Sans Stripe</span>
                      )}
                      {!pack.visible && (
                        <span className="px-2 py-0.5 rounded-full bg-red-500/20 text-red-400">Masqué</span>
                      )}
                    </div>
                  </div>
                ))}

                {packs.length === 0 && (
                  <div className="col-span-full text-center py-8 text-white/60">
                    Aucun pack créé. Créez votre premier pack coach !
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Tab Coaches */}
          {activeTab === 'coaches' && (
            <div className="space-y-4">
              {coaches.length === 0 ? (
                <div className="text-center py-8 text-white/60">
                  Aucun coach partenaire enregistré
                </div>
              ) : (
                <div className="glass rounded-xl overflow-hidden" style={{ border: '1px solid rgba(255,255,255,0.1)' }}>
                  <table className="w-full">
                    <thead className="bg-white/5">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-white/70">Coach</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-white/70">Email</th>
                        <th className="px-4 py-3 text-center text-xs font-medium text-white/70">Crédits</th>
                        <th className="px-4 py-3 text-center text-xs font-medium text-white/70">Stripe</th>
                        <th className="px-4 py-3 text-center text-xs font-medium text-white/70">Statut</th>
                        <th className="px-4 py-3 text-center text-xs font-medium text-white/70">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {coaches.map(coach => (
                        <tr key={coach.id} className="border-t border-white/5" data-testid={`coach-row-${coach.id}`}>
                          <td className="px-4 py-3 text-sm text-white">{coach.name}</td>
                          <td className="px-4 py-3 text-sm text-white/70">{coach.email}</td>
                          <td className="px-4 py-3 text-center">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              coach.credits > 10 ? 'bg-green-500/20 text-green-400' :
                              coach.credits > 0 ? 'bg-yellow-500/20 text-yellow-400' :
                              'bg-red-500/20 text-red-400'
                            }`}>
                              {coach.credits}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-center">
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              coach.stripe_connect_id ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
                            }`}>
                              {coach.stripe_connect_id ? '✓ Connecté' : '—'}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-center">
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              coach.is_active ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                            }`}>
                              {coach.is_active ? 'Actif' : 'Inactif'}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-center">
                            <button
                              onClick={() => {
                                const credits = prompt('Combien de crédits ajouter ?', '10');
                                if (credits && parseInt(credits) > 0) {
                                  handleAddCredits(coach.email, parseInt(credits));
                                }
                              }}
                              className="px-2 py-1 rounded text-xs font-medium text-purple-400 hover:bg-purple-500/20"
                              data-testid={`add-credits-${coach.id}`}
                            >
                              + Crédits
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SuperAdminPanel;
