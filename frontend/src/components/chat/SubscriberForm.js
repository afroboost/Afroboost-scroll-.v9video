/**
 * SubscriberForm.js - Formulaire d'identification abonné
 * 
 * Extrait de ChatWidget.js pour alléger le fichier principal.
 * Gère:
 * - La saisie des 4 champs (Nom, WhatsApp, Email, Code Promo)
 * - L'affichage des erreurs de validation
 * - L'état de chargement pendant la validation
 */

import React, { memo } from 'react';

/**
 * Formulaire d'identification pour les abonnés
 * @param {object} formData - Données du formulaire {name, whatsapp, email, code}
 * @param {function} setFormData - Setter pour mettre à jour les données
 * @param {function} onSubmit - Handler de soumission
 * @param {function} onCancel - Handler d'annulation (retour au chat visiteur)
 * @param {string} error - Message d'erreur à afficher
 * @param {boolean} isLoading - État de chargement (validation en cours)
 */
const SubscriberForm = ({ 
  formData, 
  setFormData, 
  onSubmit, 
  onCancel, 
  error, 
  isLoading 
}) => {
  return (
    <form 
      onSubmit={onSubmit}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
        minHeight: 'min-content'
      }}
    >
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '8px' }}>
        <span style={{ fontSize: '28px' }}>💎</span>
        <p className="text-white text-sm mt-2">
          Identifiez-vous comme abonné
        </p>
        <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: '11px', marginTop: '4px' }}>
          Accès à vos avantages et réservations rapides
        </p>
      </div>
      
      {/* Message d'erreur */}
      {error && (
        <div style={{ 
          background: 'rgba(239, 68, 68, 0.2)', 
          color: '#ef4444', 
          padding: '8px 12px', 
          borderRadius: '8px',
          fontSize: '12px'
        }}>
          {error}
        </div>
      )}
      
      {/* Champ Nom */}
      <div>
        <label className="block text-white text-xs mb-1" style={{ opacity: 0.7 }}>Nom complet *</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          placeholder="Votre nom complet"
          className="w-full px-3 py-2 rounded-lg text-sm"
          style={{
            background: 'rgba(255,255,255,0.1)',
            border: '1px solid rgba(255,255,255,0.2)',
            color: '#fff',
            outline: 'none'
          }}
          data-testid="subscriber-name"
        />
      </div>
      
      {/* Champ WhatsApp */}
      <div>
        <label className="block text-white text-xs mb-1" style={{ opacity: 0.7 }}>Numéro WhatsApp *</label>
        <input
          type="tel"
          value={formData.whatsapp}
          onChange={(e) => setFormData({ ...formData, whatsapp: e.target.value })}
          placeholder="+41 79 123 45 67"
          className="w-full px-3 py-2 rounded-lg text-sm"
          style={{
            background: 'rgba(255,255,255,0.1)',
            border: '1px solid rgba(255,255,255,0.2)',
            color: '#fff',
            outline: 'none'
          }}
          data-testid="subscriber-whatsapp"
        />
      </div>
      
      {/* Champ Email */}
      <div>
        <label className="block text-white text-xs mb-1" style={{ opacity: 0.7 }}>Email *</label>
        <input
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          placeholder="votre@email.com"
          className="w-full px-3 py-2 rounded-lg text-sm"
          style={{
            background: 'rgba(255,255,255,0.1)',
            border: '1px solid rgba(255,255,255,0.2)',
            color: '#fff',
            outline: 'none'
          }}
          data-testid="subscriber-email"
        />
      </div>
      
      {/* Champ Code Promo */}
      <div>
        <label className="block text-white text-xs mb-1" style={{ opacity: 0.7 }}>Code Promo *</label>
        <input
          type="text"
          value={formData.code}
          onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
          placeholder="Votre code abonné"
          className="w-full px-3 py-2 rounded-lg text-sm"
          style={{
            background: 'rgba(147, 51, 234, 0.2)',
            border: '1px solid rgba(147, 51, 234, 0.4)',
            color: '#fff',
            outline: 'none',
            textTransform: 'uppercase',
            fontWeight: '600',
            letterSpacing: '1px'
          }}
          data-testid="subscriber-code"
        />
      </div>
      
      {/* Bouton de validation */}
      <button
        type="submit"
        disabled={isLoading}
        className="py-3 rounded-lg font-semibold text-sm transition-all"
        style={{
          background: 'linear-gradient(135deg, #9333ea, #6366f1)',
          color: '#fff',
          border: 'none',
          cursor: isLoading ? 'wait' : 'pointer',
          opacity: isLoading ? 0.7 : 1,
          marginTop: '8px'
        }}
        data-testid="subscriber-submit"
      >
        {isLoading ? '⏳ Validation...' : '💎 Valider mon abonnement'}
      </button>
      
      {/* Bouton retour */}
      <button
        type="button"
        onClick={onCancel}
        className="py-2 text-sm"
        style={{
          background: 'none',
          color: 'rgba(255,255,255,0.6)',
          border: 'none',
          cursor: 'pointer',
          textDecoration: 'underline'
        }}
        data-testid="back-to-visitor"
      >
        ← Retour au chat visiteur
      </button>
    </form>
  );
};

// Mémoïsation pour éviter les re-rendus inutiles
export default memo(SubscriberForm);
