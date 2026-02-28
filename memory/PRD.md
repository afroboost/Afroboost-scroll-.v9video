# Afroboost - Document de Référence Produit (PRD)

## v9.3.2 - ÉTANCHÉITÉ TOTALE, MIROIR RÉEL & FIX BOUTON ✅ (28 Février 2026)

### STATUT: MISSION v9.3.2 COMPLÈTE - "INTERFACE MIROIR ET ÉTANCHÉITÉ VERROUILLÉE"

| Objectif | Statut |
|----------|--------|
| Fix Header Vitrine (vidéo unique) | ✅ |
| Formulaire paiement & code promo | ✅ |
| Étanchéité des comptes | ✅ |
| Bouton Chat persistant | ✅ |
| Anti-Régression (7 réservations Bassi) | ✅ |

### Étanchéité v9.3.2

| Ressource | Bassi (Super Admin) | Nouveau Partenaire |
|-----------|---------------------|-------------------|
| Réservations | 7 | 0 |
| Contacts | 8 | 0 |
| Codes Promo | Tous | Seulement les siens |
| Concept | Global | Personnel |

### Header Vidéo Vitrine v9.3.2

Supporte maintenant :
- **YouTube** : Extraction automatique de l'ID vidéo
- **Vimeo** : Mode background autoplay
- **MP4/WebM/MOV** : Lecture native HTML5
- **Images** : Fallback pour photos/bannières
- **Placeholder** : Animation logo si aucun média configuré

### Tests v9.3.2 - Iteration 95
- Backend: **100%** (12/12 tests) ✅
- Frontend: **100%** ✅
- Non-régression: **7 réservations Bassi, 8 contacts** ✅

---

## v9.3.1 - SÉCURITÉ STORAGE, FIX BOUTON & PAIEMENT ✅ (28 Février 2026)

### STATUT: MISSION v9.3.1 COMPLÈTE - "ÉTANCHÉITÉ STORAGE ET BOUTON INTELLIGENT ACTIVÉS"

| Objectif | Statut |
|----------|--------|
| Isolation physique storage | ✅ |
| Bouton Chat intelligent (côté serveur) | ✅ |
| Paiement activé dans vitrine | ✅ |
| Nettoyage doublons Stripe | ✅ |
| Anti-Régression (7 réservations Bassi) | ✅ |

### Nouvelles APIs v9.3.1

| Endpoint | Description |
|----------|-------------|
| POST /api/coach/upload-asset | Upload isolé par coach_id dans /uploads/coaches/{coach_folder}/ |
| GET /api/check-partner/{email} | Vérifie côté serveur si un utilisateur est partenaire |

### Storage Isolé v9.3.1

```
/app/backend/uploads/
├── profiles/           # Photos de profil utilisateurs
├── coaches/            # v9.3.1: Assets isolés par coach
│   ├── bassi_at_example_com/
│   │   ├── image_abc123.jpg
│   │   └── video_def456.mp4
│   └── autre_coach_at_gmail_com/
│       └── logo_xyz789.png
└── emojis/             # Emojis personnalisés
```

### Tests v9.3.1 - Iteration 94
- Backend: **100%** (11/11 tests) ✅
- Frontend: **100%** ✅
- Non-régression: **7 réservations Bassi** ✅

---

## v9.3.0 - ÉTANCHÉITÉ TOTALE & MIROIR FONCTIONNEL ✅ (28 Février 2026)

### STATUT: MISSION v9.3.0 COMPLÈTE - "ÉTANCHÉITÉ ASSURÉE ET VITRINE RÉPARÉE"

| Objectif | Statut |
|----------|--------|
| Isolation médias/contacts par coach_id | ✅ |
| Bouton Chat intelligent (persistance) | ✅ |
| Vitrine miroir avec paiements | ✅ |
| Nettoyage Dashboard | ✅ |
| Anti-Régression (7 réservations Bassi) | ✅ |

### Isolation par coach_id v9.3.0

| Collection | ID Super Admin | ID Partenaire |
|------------|----------------|---------------|
| concept | `concept` | `concept_{email}` |
| payment_links | `payment_links` | `payment_links_{email}` |
| discount_codes | Tous | Seulement les siens |

### Nouvelles APIs v9.3.0

| Endpoint | Description |
|----------|-------------|
| GET /api/payment-links/{email} | Liens de paiement publics d'un coach |

### Tests v9.3.0 - Iteration 93
- Backend: **100%** (17/17 tests) ✅
- Frontend: **100%** ✅
- Non-régression: **7 réservations Bassi** ✅

---

## v9.2.9 - MIROIR TOTAL, PAIEMENT & NETTOYAGE ✅ (28 Février 2026)

### STATUT: MISSION v9.2.9 COMPLÈTE - "MIROIR TOTAL ET FORMULAIRES ACTIVÉS"

| Objectif | Statut |
|----------|--------|
| Formulaire CODE PROMO (vitrine) | ✅ |
| Header vidéo dynamique | ✅ |
| Nettoyage Dashboard (1 seul bouton) | ✅ |
| Séparation accès Admin | ✅ |
| Anti-Régression (7 réservations Bassi) | ✅ |

### Fonctionnalités v9.2.9

| Fonctionnalité | Description |
|----------------|-------------|
| Header Vidéo Vitrine | Logo animé + nom du coach si pas de video_url |
| CODE PROMO Vitrine | Champ optionnel avec bouton "Valider" dans le modal de réservation |
| Onglet "Ma Page" | Remplace "Paiements", affiche QR Code et lien unique |
| Configuration Paiements | Section collapsible dans "Ma Page" |

### Modifications v9.2.9

| Fichier | Modification |
|---------|--------------|
| CoachVitrine.js | Lignes 269-304: validatePromoCode avec coach_id |
| CoachVitrine.js | Lignes 568-645: Header vidéo animé |
| CoachVitrine.js | Lignes 916-956: Champ CODE PROMO |
| CoachDashboard.js | Lignes 3600-3604: Onglet "page-vente" |
| CoachDashboard.js | Lignes 5133-5194: Contenu "Ma Page" avec QR |

### Tests v9.2.9 - Iteration 92
- Backend: **100%** (11/11 tests) ✅
- Frontend: **100%** ✅
- Non-régression: **7 réservations Bassi** ✅

---

## v9.2.8 - SÉCURITÉ MAXIMALE, ISOLATION & COMMANDES ✅ (28 Février 2026)

### STATUT: MISSION v9.2.8 COMPLÈTE - "COMMANDES BRANCHÉES ET SÉCURITÉ VERROUILLÉE"

| Objectif | Statut |
|----------|--------|
| Quick Controls activés | ✅ |
| Interrupteur Accès Partenaires | ✅ |
| Interrupteur Mode Maintenance | ✅ |
| Page maintenance premium | ✅ |
| Horaires cliquables vitrine | ✅ |
| Anti-Régression (7 réservations Bassi) | ✅ |

### Fonctionnalités v9.2.8

| Fonctionnalité | Description |
|----------------|-------------|
| Page Maintenance | Design premium avec logo animé, barre de progression, contact email |
| Toggle Accès Partenaires | Si OFF → bouton "Devenir Partenaire" masqué dans le chat |
| Toggle Mode Maintenance | Si ON → page maintenance pour tous sauf Super Admin |
| Dates Cliquables Vitrine | Chaque date de cours ouvre un modal de réservation |
| Modal Réservation | Formulaire Nom/Email/WhatsApp avec confirmation visuelle |

### API Platform Settings

```
GET /api/platform-settings
Response: { partner_access_enabled, maintenance_mode, is_super_admin }

PUT /api/platform-settings (Super Admin only)
Headers: X-User-Email: contact.artboost@gmail.com
Body: { partner_access_enabled?: boolean, maintenance_mode?: boolean }
```

### Tests v9.2.8 - Iteration 91
- Backend: **100%** (9/9 tests) ✅
- Frontend: **100%** ✅
- Non-régression: **7 réservations Bassi** ✅

---

## v9.2.7 - INTERRUPTEURS MINIMALISTES & FIX PARCOURS ✅ (28 Février 2026)

### STATUT: MISSION v9.2.7 COMPLÈTE - "INTERRUPTEURS MINIMALISTES ET PARCOURS RÉPARÉ"

| Objectif | Statut |
|----------|--------|
| Quick Control (icône 3 points) | ✅ |
| Toggles Super Admin (Accès Partenaires, Mode Maintenance) | ✅ |
| Parcours Pack 0 CHF → Dashboard | ✅ |
| Vitrine: photo + nom en haut à droite | ✅ |
| Anti-Régression (7 réservations Bassi) | ✅ |

### Modifications v9.2.7

| Fichier | Modification |
|---------|--------------|
| backend/server.py | Lignes 5962-6034: API `/api/platform-settings` GET/PUT |
| CoachDashboard.js | Lignes 344-390: États Quick Control + refs |
| CoachDashboard.js | Lignes 3875-3970: UI Quick Control avec toggles |
| CoachVitrine.js | Lignes 348-368: Photo et nom coach en haut à droite |
| BecomeCoachPage.js | Lignes 101-106: Redirect vers `#partner-dashboard` après pack gratuit |

### API Platform Settings v9.2.7

```
GET /api/platform-settings
Headers: X-User-Email: contact.artboost@gmail.com
Response: { partner_access_enabled, maintenance_mode, is_super_admin }

PUT /api/platform-settings (Super Admin only)
Headers: X-User-Email: contact.artboost@gmail.com
Body: { partner_access_enabled?: boolean, maintenance_mode?: boolean }
```

### Tests v9.2.7 - Iteration 90
- Backend: **100%** ✅
- Frontend: **100%** ✅
- Non-régression: **7 réservations Bassi** ✅

---

## v9.2.6 - PARCOURS RÉEL & VITRINE MIROIR ✅ (28 Février 2026)

### STATUT: MISSION v9.2.6 COMPLÈTE - "PARCOURS PARTENAIRE RÉPARÉ ET VITRINE MIROIR ACTIVÉE"

| Objectif | Statut |
|----------|--------|
| Connexion via Chat (Identité Unique) | ✅ |
| Redirection Post-Achat (Zéro Accueil) | ✅ |
| Vitrine & Dashboard Miroir | ✅ |
| Anti-Régression (7 réservations Bassi) | ✅ |

### Modifications v9.2.6

| Fichier | Modification |
|---------|--------------|
| backend/server.py | Ligne 2069: `COACH_DASHBOARD_URL = "https://afroboost.com/#partner-dashboard"` |
| ChatWidget.js | Lignes 3384-3418: Bouton "Accéder à mon Dashboard" pour partenaires inscrits |

### Fonctionnalités v9.2.6

| Fonctionnalité | Description |
|----------------|-------------|
| Bouton Dashboard Chat | Menu utilisateur du chat affiche "Accéder à mon Dashboard" si `isRegisteredCoach \|\| isCoachMode` |
| Redirection Stripe | `success_url` pointe vers `https://afroboost.com/#partner-dashboard?success=true&auth=success` |
| Auto-Login Modal | Si accès à `#partner-dashboard` sans être connecté → modal Google Login auto-ouvert |
| Design Miroir Vitrine | `/coach/:username` utilise couleurs Afroboost (#D91CD2) et animations identiques |

### Tests v9.2.6 - Iteration 89
- Backend: **100%** ✅
- Frontend: **100%** ✅
- Non-régression: **7 réservations Bassi (04/03/2026)** ✅

### Vérifications Clés v9.2.6
- Page d'accueil: 4 dates de mars (04.03, 11.03, 18.03, 25.03) à 18:30
- Chat widget: Bouton "Devenir Partenaire" ouvre inscription avec 3 packs
- Hash detection: `#partner-dashboard` ouvre modal connexion Google si non connecté
- API: 7 réservations Bassi visibles
- Vitrine: Couleurs #D91CD2 et design Afroboost

---

## v9.2.5 - RÉPARATION VISUELLE FORCÉE & BRANCHEMENT RÉEL ✅ (28 Février 2026)

### STATUT: MISSION v9.2.5 COMPLÈTE

| Composant | Description |
|-----------|-------------|
| LoadingFallback | Composant de secours avec squelette dashboard (lignes 3565-3625) |
| dashboardReady | État de chargement (ligne 318) |
| success_url | `#partner-dashboard?success=true&auth=success` |
| Propulsion | App.js détecte `auth=success` et redirige automatiquement |

### Modifications v9.2.5

| Fichier | Modification |
|---------|--------------|
| CoachDashboard.js | LoadingFallback component + dashboardReady state |
| server.py | success_url → `#partner-dashboard?success=true&auth=success` |
| App.js | Détection `auth=success` pour propulsion garantie |

### Comportement v9.2.5

| Situation | Affichage |
|-----------|-----------|
| Chargement en cours | LoadingFallback (squelette avec logo Afroboost) |
| Partenaire vierge | Dashboard complet avec 0 crédit rouge |
| Super Admin | Dashboard complet avec 👑 + 7 réservations |
| Retour Stripe ?auth=success | Propulsion FORCÉE vers dashboard |

### Tests v9.2.5 - Iteration 88
- Backend: **100%** ✅
- Frontend: **100%** ✅
- Non-régression: **7 réservations Bassi (04/03/2026)** ✅

---

## v9.2.4 - FORCE AFFICHAGE PARTENAIRE & FIX REDIRECTION ✅ (28 Février 2026)

### STATUT: MISSION v9.2.4 COMPLÈTE

| Problème | Solution |
|----------|----------|
| Dashboard blanc possible | `safeCoachUser = coachUser \|\| {}` protection |
| Redirection perdue après Google OAuth | `localStorage.redirect_to_dash` = MÉMOIRE MORTE |
| Hash non reconnu | `#partner-dashboard` alias de `#coach-dashboard` |

### Modifications v9.2.4

| Fichier | Modification |
|---------|--------------|
| CoachDashboard.js | Ligne 315: `safeCoachUser = coachUser \|\| {}` |
| App.js | Lignes 42-73: `detectStripeSuccess()` + `redirect_to_dash` |
| App.js | Lignes 2146-2181: Support `#partner-dashboard` |
| App.js | Lignes 3295-3312: `handleGoogleLogin` vérifie `redirect_to_dash` |

### Flux de Propulsion v9.2.4 (MÉMOIRE MORTE)

```
1. Stripe ?success=true détecté AVANT React
   ↓
2. localStorage.redirect_to_dash = 'true' 
   localStorage.afroboost_redirect_message = '🎉 Paiement validé...'
   ↓
3. URL nettoyée, hash = #partner-dashboard
   ↓
4. Si déjà connecté → Dashboard immédiat
   Si non connecté → Modal login avec message bienvenue
   ↓
5. handleGoogleLogin vérifie redirect_to_dash
   ↓
6. Redirection FORCÉE vers dashboard + message affiché
```

### Tests v9.2.4 - Iteration 87
- Backend: **100%** ✅
- Frontend: **100%** ✅
- Non-régression: **7 réservations Bassi (04/03/2026)** ✅

---

## v9.2.3 - BRANCHEMENT PARTENAIRE & PROPULSION RÉELLE ✅ (28 Février 2026)

### STATUT: MISSION v9.2.3 COMPLÈTE

| Problème | Solution |
|----------|----------|
| Dashboard blanc pour nouveaux partenaires | `coachCredits` initialisé à `isSuperAdmin ? -1 : 0` |
| Badge non affiché si crédits = null | Suppression condition `coachCredits !== null` |
| Propulsion Stripe tardive | Détection AVANT React avec `detectStripeSuccess()` |
| Intent perdu après redirect | Stockage dans `localStorage.afroboost_redirect_intent` |

### Modifications v9.2.3

| Fichier | Modification |
|---------|--------------|
| App.js | Lignes 38-70: `detectStripeSuccess()` exécuté AVANT React |
| CoachDashboard.js | Ligne 337: `coachCredits = isSuperAdmin ? -1 : 0` |
| CoachDashboard.js | Lignes 3711-3724: Badge TOUJOURS visible (plus de null check) |

### Comportement "Compte Vierge" v9.2.3

| État | Affichage |
|------|-----------|
| Profil inexistant (404) | Dashboard avec crédits = 0 |
| Données vides | Onglets fonctionnels, messages "Aucune..." |
| Campagnes | Avertissement "⚠️ Crédits insuffisants" + bouton "Acheter" |
| Conversations | "Liens actifs" visible, formulaires accessibles |

### Tests v9.2.3 - Iteration 86
- Backend: **100% (18/18 tests)** ✅
- Frontend: **100%** ✅
- Non-régression: **7 réservations Bassi (04/03/2026)** ✅

---

## v9.2.2 - VISIBILITÉ PARTENAIRE & FIX REDIRECTION ✅ (28 Février 2026)

### STATUT: MISSION v9.2.2 COMPLÈTE

| Problème | Solution |
|----------|----------|
| Dashboard invisible pour partenaires | Gestion d'erreur profil + valeurs par défaut |
| Accès réservé à Bassi | Ouverture à TOUS les emails dans auth_routes.py |
| Propulsion nécessitait session_id | success=true suffit maintenant |
| Pas de profil coach auto | Création automatique à la connexion Google |

### Modifications v9.2.2

| Fichier | Modification |
|---------|--------------|
| CoachDashboard.js | Lignes 348-380: Gestion erreur profil avec valeurs par défaut |
| auth_routes.py | Lignes 68-128: Accès pour tous + création auto profil coach |
| App.js | Lignes 2208-2263: Propulsion v9.2.2 sans session_id |

### Comportement par rôle v9.2.2

| Rôle | Badge | Dashboard Title | Bouton Admin | Stripe Connect |
|------|-------|-----------------|--------------|----------------|
| Super Admin (Bassi) | 👑 Crédits Illimités | Afroboost | ✅ Visible | ❌ Masqué |
| Partenaire | 💰 Solde : X Crédits | Mon Espace Partenaire | ❌ Masqué | ✅ Visible |
| Partenaire (0 crédit) | 💰 Solde : 0 Crédit (ROUGE) | Mon Espace Partenaire | ❌ Masqué | ✅ Visible |

### Tests v9.2.2 - Iteration 85
- Backend: **100% (15/15 tests)** ✅
- Frontend: **100%** ✅
- Non-régression: **7 réservations Bassi (04/03/2026)** ✅

---

## v9.2.1 - RÉPARATION VISIBILITÉ & CONNEXION ✅ (28 Février 2026)

### STATUT: MISSION v9.2.1 COMPLÈTE - BUG FIX

| Bug | Cause | Solution |
|-----|-------|----------|
| Dashboard blanc/invisible | `API_URL` undefined | Remplacé par `API` (défini ligne 195) |
| Onglet Conversations crash | `handleTestNotification` manquant | Ajouté à la ligne 2078 |
| Erreur bloque tout | Pas d'isolation | Ajouté `SectionErrorBoundary` |

### Corrections v9.2.1

| Fichier | Modification |
|---------|--------------|
| CoachDashboard.js | + `handleTestNotification` (lignes 2078-2113) |
| CoachDashboard.js | + `SectionErrorBoundary` (lignes 31-59) |
| CoachDashboard.js | Fix `API_URL={API}` (ligne 5645) |

### Tests v9.2.1 - Iteration 84
- Backend: **100% ✅**
- Frontend: **100% ✅**
- Dashboard visible: **✅**
- Badge Super Admin: **✅**
- 7 réservations: **✅**
- Dates mars: **04.03, 11.03, 18.03, 25.03 ✅**

---

## v9.2.0 - DÉCOUPAGE DASHBOARD & SÉCURITÉ ✅ (28 Février 2026)

### STATUT: MISSION v9.2.0 COMPLÈTE

| Composant | Avant | Après | Changement |
|-----------|-------|-------|------------|
| CoachDashboard.js | 6633 | 5749 | -884 lignes |
| CRMSection.js | 0 | 673 | +673 lignes (nouveau) |
| server.py | 6257 | 6191 | -66 lignes |
| promo_routes.py | 0 | 159 | +159 lignes (nouveau) |

### Modularisation v9.2.0

| Module | Lignes | Routes extraites |
|--------|--------|------------------|
| coach/CRMSection.js | 673 | Section Conversations/CRM UI |
| routes/promo_routes.py | 159 | /discount-codes CRUD + validate |
| routes/auth_routes.py | 232 | /auth/* + /coach-auth/* |
| routes/coach_routes.py | existant | /coach/*, /partner/* |
| routes/campaign_routes.py | existant | /campaigns/* |
| routes/reservation_routes.py | existant | /reservations/* |

### Protection Badge Crédits v9.2.0

| Email | Badge affiché |
|-------|---------------|
| contact.artboost@gmail.com | 👑 Crédits Illimités (violet néon) |
| Tout autre email | 💰 Solde : X Crédits (violet ou rouge si < 5) |

### Tests v9.2.0 - Iteration 83
- Backend: **12/12 pytest ✅**
- Frontend: **2/2 Playwright ✅**
- Non-régression: **7 réservations ✅**
- Dates mars: **04.03, 11.03, 18.03, 25.03 ✅**

---

## v9.1.9 - PROPULSION TOTALE & VISIBILITÉ CRÉDITS ✅ (28 Février 2026)

### STATUT: MISSION v9.1.9 COMPLÈTE

| Critère | Validation |
|---------|------------|
| Propulsion zéro clic | ✅ **Dashboard direct si déjà authentifié** |
| Badge crédits visible | ✅ **"💰 Solde : X Crédits" violet néon #D91CD2** |
| Badge Super Admin | ✅ **"👑 Crédits Illimités"** |
| Modularisation auth | ✅ **routes/auth_routes.py créé (232 lignes)** |
| server.py allégé | ✅ **6257 lignes** (était 6436, -180 lignes) |
| Non-régression | **7 réservations ✅** |
| Sessions Mars | **04.03, 11.03, 18.03, 25.03 ✅** |
| Tests | **9/9 pytest + 4 Playwright ✅** |

### Propulsion Zéro Clic v9.1.9

| URL | Utilisateur | Action |
|-----|-------------|--------|
| `?success=true&session_id=xxx` | Déjà authentifié | Dashboard IMMÉDIAT (pas de modal) |
| `?success=true&session_id=xxx` | Non connecté | Modal "🎉 Paiement validé ! Bienvenue Partenaire" |

### Badge Crédits v9.1.9

| Rôle | Affichage | Couleur |
|------|-----------|---------|
| Partenaire (crédits >= 5) | "💰 Solde : X Crédits" | Violet néon #D91CD2 |
| Partenaire (crédits < 5) | "💰 Solde : X Crédits" | Rouge #ef4444 |
| Super Admin | "👑 Crédits Illimités" | Violet néon #D91CD2 |

### Modularisation Backend v9.1.9

| Fichier | Lignes | Routes |
|---------|--------|--------|
| routes/auth_routes.py | 232 | /auth/google/session, /auth/me, /auth/logout |
| routes/coach_routes.py | existant | /coach/*, /partner/* |
| routes/campaign_routes.py | existant | /campaigns/* |
| routes/reservation_routes.py | existant | /reservations/* |
| server.py | 6257 | Core API (objectif < 6000) |

### Tests v9.1.9 - Iteration 82
- Backend: **9/9 pytest ✅**
- Frontend: **4/4 Playwright ✅**
- Features: **100% ✅**

---

## v9.1.8 - DASHBOARD MIROIR ET PROPULSION VERROUILLÉS ✅ (28 Février 2026)

### STATUT: MISSION v9.1.8 COMPLÈTE - MIROIR ABSOLU

| Critère | Validation |
|---------|------------|
| Propulsion post-paiement | ✅ **"🎉 Paiement validé ! Bienvenue Partenaire"** |
| Dashboard jumeau | ✅ **CoachDashboard.js unique pour TOUS** |
| Route /partner/:username | ✅ **Alias de /coach/:username** |
| API /api/partner/vitrine | ✅ **Même données que /api/coach/vitrine** |
| Non-régression | **7 réservations ✅** |
| Sessions Mars | **04.03, 11.03, 18.03, 25.03 ✅** |
| Tests | **11/11 + 7 pytest + 4 Playwright ✅** |

### Propulsion Partenaire v9.1.8

| URL | Action |
|-----|--------|
| `?success=true&session_id=xxx` | Modal connexion avec "🎉 Paiement validé ! Bienvenue Partenaire" |
| Partenaire déjà connecté | Dashboard affiché + message temporaire |
| Partenaire non connecté | Modal "Connexion Partenaire" ouvert |

### Routes Vitrine v9.1.8

| Route Frontend | API Backend | Résultat |
|----------------|-------------|----------|
| `/partner/:username` | `/api/partner/vitrine/:username` | Vitrine partenaire |
| `/coach/:username` | `/api/coach/vitrine/:username` | Vitrine partenaire (legacy) |

### Dashboard Miroir v9.1.8

| Rôle | Fichier | Accès |
|------|---------|-------|
| Super Admin | `CoachDashboard.js` | TOUS les onglets + "👑 Crédits Illimités" |
| Partenaire Normal | `CoachDashboard.js` | MÊMES onglets, données isolées |

### Tests v9.1.8 - Iteration 81
- Backend: **7/7 pytest ✅**
- Frontend: **4/4 Playwright ✅**
- Features: **11/11 ✅**

---

## v9.1.7 - SUPER ADMIN OMNISCIENT ET LOGIQUE PRÉSERVÉE ✅ (28 Février 2026)

### STATUT: MISSION v9.1.7 COMPLÈTE

| Critère | Validation |
|---------|------------|
| Bypass Super Admin | ✅ **Réservations, Campagnes, Contacts, Codes promo** |
| Packs Coach | ✅ **3 packs visibles, /all sécurisé** |
| Crédits Illimités | ✅ **credits=-1, badge "👑 Crédits Illimités"** |
| Non-régression | **7 réservations ✅** |
| Sessions Mars | **04.03, 11.03, 18.03, 25.03 ✅** |
| Tests | **12/12 ✅** |

### Vérification Super Admin Omniscient

| Endpoint | Super Admin | Coach Normal |
|----------|-------------|--------------|
| /api/reservations | TOUTES (7) | Ses données |
| /api/chat/participants | TOUS (8) | Ses contacts |
| /api/campaigns | TOUTES | Ses campagnes |
| /api/discount-codes | GLOBAL | GLOBAL |
| /api/admin/coach-packs/all | ✅ Accès | ❌ 403 |

### Bypass implémentés
- `reservation_routes.py:66` - `is_super_admin()` → query vide `{}`
- `campaign_routes.py:50-51` - `is_super_admin()` → pas de filtre
- `server.py:3634` - `is_super_admin()` → tous les contacts
- `coach_routes.py:62-68` - `/all` réservé au Super Admin

### Tests v9.1.7 - Iteration 79
- Backend: **12/12 ✅**
- Frontend: **100% ✅**

---

## v9.1.6 - SYSTÈME PARTENAIRE ET CONTRÔLE TOTAL ✅ (28 Février 2026)

### STATUT: MISSION v9.1.6 COMPLÈTE

| Critère | Validation |
|---------|------------|
| Rebranding "Partenaire" | ✅ **ChatWidget, Vitrine, Dashboard** |
| Super Admin bypass | ✅ **Voit TOUT (contacts, campagnes, réservations)** |
| Crédits illimités | ✅ **"👑 Crédits Illimités" pour Bassi** |
| Non-régression | **7 réservations ✅** |
| server.py | **6436 lignes** (< 6500) |
| Tests | **11/11 ✅** |

### Accomplissements v9.1.6

| Feature | Description |
|---------|-------------|
| Rebranding ChatWidget | "Devenir Coach Partenaire" → "Devenir Partenaire" |
| Rebranding Vitrine | "Coach Partenaire Afroboost" → "Partenaire Afroboost" |
| Rebranding Dashboard | "Mon Espace Afroboost" → "Mon Espace Partenaire" |
| Badge Super Admin | "⭐ Super Admin" → "👑 Crédits Illimités" |
| Bypass coach_id | Super Admin voit TOUTES les données (réservations, contacts, campagnes) |

### Tests v9.1.6 - Iteration 78
- Backend: **11/11 ✅**
- Frontend: **100% ✅**
- Cours Mars: **INTACTS** (04.03, 11.03, 18.03, 25.03)
- Sunday Vibes: **INTACTS** (01.03, 08.03, 15.03, 22.03)

### Bypass Super Admin vérifié
- `is_super_admin()` identifie `contact.artboost@gmail.com`
- `get_coach_filter()` retourne `{}` pour Super Admin
- `check_credits()` retourne `{unlimited: true}` pour Super Admin
- Toutes les routes filtrées (réservations, contacts, campagnes) bypassed

---

## v9.1.5 - BRANCHEMENT RÉEL ET VITRINE MIROIR ✅ (28 Février 2026)

### STATUT: MISSION v9.1.5 COMPLÈTE

| Critère | Validation |
|---------|------------|
| Redirection auto login | ✅ **handleGoogleLogin → #coach-dashboard** |
| Bouton dynamique chat | ✅ **Mon Espace Coach / Devenir Coach** |
| Vitrine miroir | ✅ **Design Afroboost + offres par défaut** |
| Non-régression | **7 réservations ✅** |
| server.py | **6435 lignes** (< 6500) |
| Tests | **11/11 backend + frontend ✅** |

### Accomplissements v9.1.5

| Feature | Description |
|---------|-------------|
| Propulsion auto | handleGoogleLogin force `window.location.hash = '#coach-dashboard'` |
| Bouton dynamique | Visiteur: "Devenir Coach Partenaire" → Coach: "🏠 Mon Espace Coach" |
| Détection coach | isCoachMode vérifie `afroboost_coach_mode` dans localStorage |
| Vitrine miroir | Design CSS Afroboost avec gradient, QR code, bouton partage |
| Offres par défaut | DEFAULT_STARTER_OFFERS si coach n'a pas créé les siennes |

### Tests v9.1.5 - Iteration 77
- Backend: **11/11 ✅**
- Frontend: **100% ✅**
- Cours Mars: **INTACTS**
- 7 réservations Bassi: **PRÉSERVÉES**

### API Vérifiées
- `GET /api/coach/vitrine/bassi` → 3 offres, 2 cours
- `GET /api/reservations` → 7 réservations Super Admin
- `GET /api/courses` → Session Cardio + Sunday Vibes

---

## v9.1.3 - DASHBOARD MIROIR ET PROPULSION ACTIFS ✅ (28 Février 2026)

### STATUT: PROPULSION ZÉRO-CLIC ACTIVE

| Critère | Validation |
|---------|------------|
| Propulsion | ✅ **ZÉRO-CLIC** après Stripe |
| Dashboard jumeau | ✅ **FULL ACCESS** pour tous |
| Marque blanche | ✅ **platform_name** supporté |
| Non-régression | **7 réservations ✅** |
| Tests | **13/13 ✅** |

### Accomplissements v9.1.3

| Feature | Description |
|---------|-------------|
| Propulsion automatique | #coach-dashboard → modal immédiat (sans clic) |
| Stripe session | session_id parsé dans le hash pour retour Stripe |
| Dashboard jumeau | requiresCredits SUPPRIMÉ - accès complet |
| Marque blanche header | platform_name ou "Mon Espace Afroboost" |

### Tests v9.1.3 - Iteration 75
- Backend: **9/9 ✅**
- Frontend: **4/4 ✅**
- Propulsion: **ZÉRO-CLIC ✅**
- Cours Mars: **INTACTS**

### Fonctionnalités vérifiées
- Propulsion #coach-dashboard: **PASSED**
- Stripe session detection: **PASSED**
- Dashboard full access: **PASSED**
- Marque blanche header: **PASSED**
- 7 réservations Bassi: **PASSED**
- Session Cardio (04.03, 11.03, 18.03, 25.03): **PASSED**
- Sunday Vibes (01.03, 08.03, 15.03, 22.03): **PASSED**

---

## v9.1.2 - DASHBOARD MIROIR ET REDIRECTION VERROUILLÉS ✅ (28 Février 2026)

### STATUT: REFACTORING PHASE 2 RÉUSSI

| Critère | Validation |
|---------|------------|
| server.py | **6719 lignes** (-730 depuis début) |
| campaign_routes.py | **134 lignes** |
| coach_routes.py | **341 lignes** |
| Total backend | 7194 lignes |
| Non-régression | **7 réservations ✅** |
| Tests | **14/14 ✅** |

### Accomplissements v9.1.2

| Feature | Description |
|---------|-------------|
| Migration campaigns | Routes /campaigns/* → campaign_routes.py |
| Redirection verrouillée | #coach-dashboard → modal connexion immédiat |
| Dashboard miroir | Tous les coaches = même CoachDashboard.js |

### Routes migrées vers campaign_routes.py
- `GET /campaigns`
- `GET /campaigns/logs`
- `GET /campaigns/{id}`
- `PUT /campaigns/{id}`
- `DELETE /campaigns/{id}`
- `DELETE /campaigns/purge/all`
- `POST /campaigns/{id}/mark-sent`

### Tests v9.1.2 - Iteration 74
- Backend: **10/10 ✅**
- Frontend: **4/4 ✅**
- Cours Mars: **INTACTS**

### Bilan refactoring
- Début (v9.0.2): **7449 lignes**
- Après v9.1.1: **6877 lignes** (-572)
- Après v9.1.2: **6719 lignes** (-158 de plus)
- **Total gagné: 730 lignes**

---

## v9.1.1 - DASHBOARD MIROIR ET REDIRECTION OK ✅ (28 Février 2026)

### STATUT: REFACTORING RÉUSSI - 572 LIGNES MIGRÉES

| Critère | Validation |
|---------|------------|
| server.py | **6877 lignes** (de 7449) |
| coach_routes.py | **341 lignes** |
| Total backend | 7218 lignes |
| Non-régression | **7 réservations ✅** |
| Tests | **14/14 ✅** |

### Accomplissements v9.1.1

| Feature | Description |
|---------|-------------|
| Refactoring server.py | -572 lignes → 6877 lignes |
| coach_routes.py | Routes coach/admin migrées |
| #coach-dashboard | Ouvre modal connexion si non connecté |
| Hash listener | Détection dynamique des changements |

### Routes migrées vers coach_routes.py
- `GET/POST /admin/coach-packs/*`
- `GET/POST/DELETE /admin/coaches/*`
- `GET /coach/profile`
- `GET /coach/check-credits`
- `POST /coach/register`
- `POST /coach/deduct-credit`
- `POST /coach/add-credits`
- `GET /auth/role`
- `GET /coaches/search`
- `GET /coach/vitrine/{username}`
- `POST /coach/stripe-connect/onboard`
- `GET /coach/stripe-connect/status`
- `POST /admin/migrate-bassi-data`

### Tests v9.1.1 - Iteration 73
- Backend: **11/11 ✅**
- Frontend: **3/3 ✅**
- Cours Mars: **INTACTS**

---

## v9.1.0 - SERVEUR ALLÉGÉ ET STABLE ✅ (28 Février 2026)

### STATUT: STRUCTURE MODULAIRE PRÉPARÉE

| Critère | Validation |
|---------|------------|
| server.py | **7449 lignes** (stable) |
| Structure routes/ | ✅ CRÉÉE |
| Non-régression | **7 réservations ✅** |
| Crédits illimités | ✅ FONCTIONNEL |
| Vitrine Bassi | ✅ platform_name |

### Accomplissements v9.1.0

| Feature | Description |
|---------|-------------|
| Structure routes/ | Dossier modulaire créé avec fichiers préparés |
| shared.py | Constantes et helpers partagés |
| admin_routes.py | Router préparé pour migration |
| coach_routes.py | Router préparé pour migration |
| campaign_routes.py | Router préparé pour migration |

### Fichiers créés
```
/app/backend/routes/
├── __init__.py        # Exports des modules
├── shared.py          # Constantes SUPER_ADMIN, helpers
├── admin_routes.py    # TODO: Migrer routes /admin/*
├── coach_routes.py    # TODO: Migrer routes /coach/*
└── campaign_routes.py # TODO: Migrer routes /campaigns/*
```

### Tests v9.1.0
- Réservations: **7 ✅** (non-régression)
- Crédits: **Unlimited ✅** (Super Admin)
- Vitrine: **Afroboost ✅** (platform_name)
- Coachs: **6 ✅** (liste admin)

### Note technique
Le refactoring complet de server.py (de 7449 à <5000 lignes) nécessite une migration progressive des routes pour éviter toute régression. La structure est maintenant en place pour cette migration future.

---

## v9.0.2 - COMPTEURS ACTIVÉS ET IDENTITÉ MIROIR OK ✅ (28 Février 2026)

### STATUT: VALIDÉ - SYSTÈME RENTABILITÉ ACTIF

| Critère | Validation |
|---------|------------|
| server.py | **7449 lignes** (limite!) |
| Déduction crédits | ✅ FONCTIONNEL |
| Blocage 402 | ✅ ACTIF |
| Notification Bassi | ✅ IMPLÉMENTÉ |
| Non-régression | **7 réservations ✅** |
| Tests | **12/12 ✅** |

### Fonctionnalités v9.0.2

| Feature | Description |
|---------|-------------|
| deduct_credit() | Déduit 1 crédit, retourne solde restant |
| check_credits() | Vérifie solde sans déduire |
| POST /chat/participants | -1 crédit pour coaches (402 si vide) |
| POST /campaigns/send-email | -1 crédit pour coaches (402 si vide) |
| Notification Bassi | Email à chaque achat de pack coach |
| Super Admin | Crédits illimités (-1), bypass déductions |

### Tests v9.0.2 - Iteration 72
- Backend: **12/12 ✅**
- Coach 100→99 crédits (déduction vérifiée)
- Non-régression: **100% INTACT**

### Bug corrigé
- POST /chat/participants: ObjectId non sérialisable → Ajout `_id.pop()`

---

## v9.0.1 - SYSTÈME FRANCHISE DYNAMIQUE ACTIVÉ ✅ (28 Février 2026)

### STATUT: VALIDÉ - ARCHITECTURE WHITE LABEL

| Critère | Validation |
|---------|------------|
| server.py | **7395 lignes** (marge 55) |
| Super Admin | ✅ VOIT TOUT |
| Toggle/Delete Coach | ✅ FONCTIONNEL |
| platform_name | ✅ DÉPLOYÉ |
| Non-régression | **7 réservations ✅** |
| Tests | **14/14 ✅** |

### Fonctionnalités v9.0.1

| Feature | Description |
|---------|-------------|
| Coach.platform_name | Nom personnalisé de la plateforme (ex: "Afroboost") |
| Coach.logo_url | Logo personnalisé pour la vitrine |
| POST /admin/coaches/{id}/toggle | Active/Désactive un coach (Super Admin) |
| DELETE /admin/coaches/{id} | Supprime un coach (Super Admin) |
| Vitrine dynamique | Affiche platform_name au lieu du nom du coach |

### Tests v9.0.1 - Iteration 71
- Backend: **14/14 ✅**
- Toggle auth: 403 pour non-Super Admin ✅
- Delete auth: 403 pour non-Super Admin ✅
- Non-régression: **100% INTACT**

### Coachs enregistrés
- Total: **5 coachs actifs**

---

## v9.0.0 - TUNNEL ET VITRINE DÉPLOYÉS ✅ (28 Février 2026)

### STATUT: VALIDÉ - PRODUCTION READY

| Critère | Validation |
|---------|------------|
| server.py | **7385 lignes** (marge 65) |
| Route /coach/:username | ✅ ACCÈS DIRECT |
| Bouton dynamique Chat | ✅ FONCTIONNEL |
| Stripe success_url | ✅ VERCEL |
| Non-régression | **7 réservations ✅** |
| Tests | **10/10 ✅** |

### Fonctionnalités v9.0.0

| Feature | Description |
|---------|-------------|
| Vitrine publique | `/coach/bassi` accessible directement sans redirection |
| Bouton dynamique | Visiteur: "Devenir Coach" → Coach: "🏠 Accès Mon Dashboard" |
| Redirection Stripe | Post-achat → `afroboost-campagn-v8.vercel.app/#coach-dashboard` |
| Navigation vitrine | Bouton "Retour" → Page d'accueil |

### Tests v9.0.0 - Iteration 70
- Backend: **10/10 ✅**
- Frontend: **100% ✅**
- Non-régression: **100% INTACT**

### Tunnel Fitness vérifié
- Session Cardio: 04.03, 11.03, 18.03, 25.03
- Sunday Vibes: 01.03, 08.03, 15.03, 22.03
- Réservations Bassi: **7 ✅**
- Offres: 3 (30/150/109 CHF)

---

## v8.9.9 - BOUTON DYNAMIQUE ET VITRINE OPÉRATIONNELS ✅ (27 Février 2026)

### STATUT: VALIDÉ - TUNNEL COACH COMPLET

| Critère | Validation |
|---------|------------|
| server.py | **7385 lignes** (marge 65) |
| Bouton dynamique Chat | ✅ FONCTIONNEL |
| Vitrine /coach/bassi | ✅ 3 offres + 2 cours |
| QR Code Dashboard | ✅ IMPLÉMENTÉ |
| Non-régression | **7 réservations ✅** |
| Tests | **9/9 ✅** |

### Accomplissements v8.9.9

| Feature | Description |
|---------|-------------|
| Bouton dynamique | Visiteur: "Devenir Coach" → Coach: "Accès Mon Dashboard" |
| Stripe success_url | Forcé vers `afroboost-campagn-v8.vercel.app/#coach-dashboard` |
| QR Code vitrine | Section "Ma Vitrine Publique" dans onglet Mon Stripe |
| Lien vitrine | Copie automatique vers `/coach/[username]` |

### Tests v8.9.9 - Iteration 69
- Backend: **9/9 ✅**
- Frontend: **100% ✅**
- Non-régression: **100% INTACT**

### Tunnel de vente FITNESS intact
- Session Cardio: 04.03, 11.03, 18.03, 25.03
- Sunday Vibes: 01.03, 08.03, 15.03, 22.03
- Réservations Bassi: **7 ✅**

---

## v8.9.7 - MIGRATION RÉUSSIE - REDIRECTION CORRIGÉE ✅ (27 Février 2026)

### STATUT: VALIDÉ - MIGRATION EXÉCUTÉE - CRÉDITS AFFICHÉS

| Critère | Validation |
|---------|------------|
| server.py | **7382 lignes** (marge 68) |
| Migration coach_id | ✅ 7 réservations, 2 contacts migrés |
| Vitrine /coach/bassi | ✅ 3 offres, 2 cours |
| Badge crédits | ✅ Affiché dans dashboard |
| Tests | **13/13 ✅** |

### Accomplissements v8.9.7

| Feature | Description |
|---------|-------------|
| Migration Bassi Data | Exécuté `/api/admin/migrate-bassi-data` - 7 réservations tagguées |
| Affichage crédits | Badge coloré dans l'en-tête du dashboard coach |
| Grisage tabs | Onglets CRM/Campagnes grisés si crédits=0 |
| Vitrine Bassi | `/coach/bassi` affiche "Bassi - Afroboost" avec offres/cours |
| Redirection Stripe | `success_url` utilise dynamiquement le Referer |

### Tests v8.9.7 - Iteration 68
- Backend: **13/13 ✅**
- Frontend: **100% ✅**
- Non-régression: **100% INTACT**

### API Vérifiées
- `POST /api/admin/migrate-bassi-data` → `{ reservations: 7, contacts: 2 }`
- `GET /api/coach/profile` → `{ credits: -1, is_super_admin: true }`
- `GET /api/coach/vitrine/bassi` → `{ coach: "Bassi - Afroboost", offers: 3, courses: 2 }`
- `GET /api/reservations` → `{ total: 7 }` pour Super Admin

---

## v8.9.6 - TUNNEL COACH & VITRINE ✅ (27 Février 2026)

### STATUT: VALIDÉ - TUNNEL RÉPARÉ - VITRINE ACTIVE

| Critère | Validation |
|---------|------------|
| server.py | **7422 lignes** (marge 28) ⚠️ |
| Endpoint Vitrine | ✅ FONCTIONNEL |
| Route /coach/[username] | ✅ ACTIVE |
| Non-régression | **100% INTACT** |
| Tests | **14/14 ✅** |

### Fonctionnalités v8.9.6

| Feature | Description |
|---------|-------------|
| Endpoint Vitrine | GET /api/coach/vitrine/{username} |
| Retour | Profil coach + offres + cours filtrés |
| Route Frontend | /coach/[username] → CoachVitrine.js |
| Erreur 404 | "Coach non trouvé" avec bouton Retour |

### Tests v8.9.6 - Iteration 67
- Backend: **14/14 ✅**
- Frontend: **100% ✅**
- Cours de Mars: **INTACTS ✅**

### Tunnel Fitness vérifié
- Session Cardio: 04.03, 11.03, 18.03, 25.03
- Sunday Vibes: 01.03, 08.03, 15.03, 22.03
- Réservations Bassi: 7 ✅

---

## v8.9.5 - ISOLATION ÉTANCHE MULTI-TENANT ✅ (27 Février 2026)

### STATUT: VALIDÉ - FORTERESSE ACTIVÉE

| Critère | Validation |
|---------|------------|
| server.py | **7382 lignes** (marge 68) |
| Isolation coach_id | ✅ FONCTIONNELLE |
| Bassi voit TOUT | ✅ CONFIRMÉ |
| Coach isolé | ✅ CONFIRMÉ |
| Tests | **15/15 ✅** |

### Isolation Multi-Tenant v8.9.5

| Endpoint | Bassi | Autre Coach |
|----------|-------|-------------|
| /reservations | Toutes (7) | 0 |
| /campaigns | Toutes | 0 |
| /chat/participants | Tous | 0 |

### Fonctionnalités v8.9.5

1. **Filtrage coach_id** sur 3 endpoints critiques
2. **Règle Anti-Casse Bassi** : Super Admin voit TOUT
3. **Onglet "Mon Stripe"** : Visible pour coachs (pas Bassi)
4. **Header X-User-Email** : Envoyé par le frontend

### Tests v8.9.5 - Iteration 66
- Isolation Backend: **7/7 ✅**
- Non-régression: **4/4 ✅**
- Frontend: **4/4 ✅**

### Cours de Mars intacts
- Session Cardio: 04.03, 11.03, 18.03, 25.03
- Sunday Vibes: 01.03, 08.03, 15.03, 22.03

---

## v8.9.4 - PROTOCOLE FORTERESSE ✅ (27 Février 2026)

### STATUT: VALIDÉ - BOUCLIER TOTAL ACTIF

| Critère | Validation |
|---------|------------|
| server.py | **7378 lignes** (marge 72) |
| Non-régression | **100% INTACT** |
| Icône Coach alignée | ✅ AVEC FILTRES |
| Bouton Devenir Coach | ✅ DANS LE CHAT |
| Tests | **11/11 ✅** |

### Modifications v8.9.4

| Élément | Changement |
|---------|------------|
| Icône coach | Déplacée DANS NavigationBar, alignée avec QR/Calendrier/Shop |
| Modal recherche | Déclenchée par icône dans la barre de filtres |
| Bouton "Devenir Coach" | Confirmé dans Chat uniquement |
| Footer | Nettoyé (plus de bouton Devenir Coach) |

### Tests v8.9.4 - Iteration 65
- Non-régression: **6/6 ✅** (Cours, Offres, QR, Paiements, Concept, Users)
- Backend: **11/11 ✅**
- Frontend: **100% ✅**

### Tunnel de vente FITNESS intact
- Cours disponibles: 2
- Offres clients: 3
- QR codes actifs: 1
- Liens paiement: 7

---

## v8.9.3 - PROTOCOLE NON-RÉGRESSION ✅ (27 Février 2026)

### STATUT: VALIDÉ - ZÉRO RÉGRESSION

| Critère | Validation |
|---------|------------|
| server.py | **7378 lignes** (marge 72) |
| Cours Fitness | ✅ INTACTS |
| Offres Clients | ✅ INTACTS |
| QR Codes | ✅ INTACTS |
| Paiements | ✅ INTACTS |
| Tests | **19/19 ✅** |

### Modifications v8.9.3

| Élément | Avant | Après |
|---------|-------|-------|
| Bouton "Devenir Coach" | Footer | Chat (sous S'identifier) |
| Icône recherche coach | Non alignée | Alignée avec texte |
| Bouton Edit pack | Sans testid | data-testid ajouté |
| Redirection achat coach | /coach-success | /#coach-dashboard |
| Bouton Stripe Connect | Absent | Visible (coachs only) |

### Tests v8.9.3 - Iteration 64
- Non-régression: **4/4 ✅**
- Backend: **19/19 ✅**
- Frontend: **5/5 ✅**

---

## v8.9.2 - FINALISATION FRANCHISE ✅ (27 Février 2026)

### STATUT: COMPLÉTÉ - BOUCLIER ACTIVÉ

| Critère | Validation |
|---------|------------|
| server.py | **7378 lignes** (sous limite 7450) |
| Recherche Coach | ✅ IMPLÉMENTÉE |
| Stripe Connect | ✅ PRÊT |
| Isolation coach_id | ✅ DEFAULT_COACH_ID |
| Tests Backend | **23/23 ✅** |
| Tests Frontend | **100% ✅** |

### Fonctionnalités v8.9.2

#### 1. Recherche Coach (Public)
| Endpoint | Description |
|----------|-------------|
| GET /api/coaches/search?q=xxx | Recherche par nom/email (min 2 chars) |
| GET /api/coaches/public/{id} | Profil public pour QR scan |

#### 2. Stripe Connect
| Endpoint | Description |
|----------|-------------|
| POST /api/coach/stripe-connect/onboard | Créer compte Express |
| GET /api/coach/stripe-connect/status | Vérifier état du compte |

#### 3. Isolation Données
```python
DEFAULT_COACH_ID = "bassi_default"  # Données existantes = Bassi
get_coach_filter(email)  # Filtre MongoDB par coach
```

#### 4. UI/UX
- Icône Coach: Cercle fin 2px violet #D91CD2
- Modal recherche avec Error Boundary
- Colonne Stripe dans table admin

### Tests v8.9.2 - Iteration 63
- Backend: **23/23 tests ✅**
- Frontend: **100% ✅**
- Non-régression: **Tous OK ✅**

---

## v8.9 - MISSION SAAS : ARCHITECTURE MULTI-COACH ✅ (27 Février 2026)

### STATUT: EN COURS

| Critère | Validation |
|---------|------------|
| server.py | **7229 lignes** (sous limite 7450) |
| Modules Articles | ❌ SUPPRIMÉS |
| Modules Médias | ❌ SUPPRIMÉS |
| Hiérarchie Super Admin | ✅ IMPLÉMENTÉE |
| Packs Coach | ✅ CRUD COMPLET |
| Page Devenir Coach | ✅ FONCTIONNELLE |
| Stripe Coach Checkout | ✅ INTÉGRÉ |

### Fonctionnalités v8.9

#### 1. Système de Rôles
| Rôle | Email | Accès |
|------|-------|-------|
| Super Admin | contact.artboost@gmail.com | Panneau total + Dashboard |
| Coach | Coachs enregistrés | Dashboard isolé |
| User | Autres | Client standard |

#### 2. Packs Coach Créés
| Pack | Prix | Crédits | Stripe ID |
|------|------|---------|-----------|
| Pack Starter | 49 CHF | 50 | price_1T5P8uRs... |
| Pack Pro | 99 CHF | 150 | price_1T5P90Rs... |

#### 3. Endpoints API v8.9
- `GET /api/admin/coach-packs` - Liste packs (public)
- `GET /api/admin/coach-packs/all` - Liste tous (Super Admin)
- `POST /api/admin/coach-packs` - Créer pack (Super Admin)
- `PUT /api/admin/coach-packs/{id}` - Modifier pack (Super Admin)
- `DELETE /api/admin/coach-packs/{id}` - Supprimer pack (Super Admin)
- `GET /api/auth/role` - Vérifier rôle utilisateur
- `POST /api/stripe/create-coach-checkout` - Checkout coach

#### 4. Composants Frontend v8.9
- `BecomeCoachPage.js` - Page d'inscription coach
- `SuperAdminPanel.js` - Panneau de gestion admin
- Footer: Lien "Devenir Coach"
- CoachDashboard: Bouton "Admin" (Super Admin only)

### Tests v8.9 - Iteration 62
- Backend: **20/20 tests ✅**
- Frontend: **100% ✅**
- Non-régression: **100% ✅**

---

## v5 - VERROUILLAGE TECHNIQUE FINAL ✅ (8 Février 2026)

### STATUT: PRÊT POUR PRODUCTION

| Critère | Validation |
|---------|------------|
| server.py | **7387 lignes** |
| localStorage.clear() | OUI |
| sessionStorage.clear() | OUI |
| window.location.replace('/') | OUI |
| Code PROMO20SECRET | Valid: True (20%) |
| Europe/Paris timezone | 1 occurrence |
| Emojis UI | **0** |
| Médias YouTube/Drive | 4 références |
| 4 dates réservation | CONFIRMÉES |

### 4 Dates de Session
- dim. 08.02 • 18:30
- dim. 15.02 • 18:30
- dim. 22.02 • 18:30
- dim. 01.03 • 18:30

### Composants validés
- InlineYouTubePlayer (mute=1 pour iOS)
- InlineDriveImage (timeout 3s + fallback)
- InlineCtaButton (validation + auto-https)
- Timer 60s (avec cleanup)
- Hard Logout (replace + clear)

---

## Mise à jour du 8 Février 2026 - OPTIMISATION RESSOURCES ✅

### Timer optimisé
- useEffect avec return clearInterval (cleanup correct)
- Rafraîchissement timestamps toutes les 60s

### Bouclier Total VALIDÉ
| Composant | Status |
|-----------|--------|
| Code PROMO20SECRET | OK |
| Eligibility | OK |
| 4 dates calendrier | OK |
| Europe/Paris scheduler | OK (1 occurrence) |
| Anti-doublon ID | OK |
| server.py | **7387 lignes** |
| Emojis UI | **0** |

### Badge Aperçu optimisé
- z-index: 50 (menus dropdown à 100)
- Ombre grise légère: rgba(0, 0, 0, 0.15)

### Nettoyage emojis complet
- Tous les emojis UI/logs supprimés
- Interface 100% minimaliste

---

## Mise à jour du 8 Février 2026 - FINALISATION DYNAMIQUE ✅

### Protocole Anti-Casse VALIDÉ
| Test | Résultat |
|------|----------|
| Connexion PROMO20SECRET | OK |
| Eligibility réservation | OK |
| 4 dates calendrier | 4 boutons trouvés |
| Sync messages | OK - server_time_utc |
| server.py | **7387 lignes** (inchangé) |

### Timer Dynamique Timestamps
```javascript
// Rafraîchit les timestamps toutes les 60s
const [, setTimestampTick] = useState(0);
useEffect(() => {
  const timer = setInterval(() => {
    setTimestampTick(t => t + 1);
  }, 60000);
  return () => clearInterval(timer);
}, []);
```

### Hard Logout
```javascript
window.location.replace('/'); // Empêche bouton Précédent
```

### Badge Aperçu amélioré
- z-index: 9999
- boxShadow: '0 2px 8px rgba(147, 51, 234, 0.4)'

### Zones protégées (NON TOUCHÉES)
- /api/check-reservation-eligibility
- /api/courses
- Sync messages (last_sync)
- Scheduler Europe/Paris
- Composants YouTube/Drive

---

## Mise à jour du 8 Février 2026 - PERFECTIONNEMENT UI & SÉCURITÉ ✅

### Blindage Mode Vue Visiteur (Admin)
```javascript
handleReservationClick() {
  if (isVisitorPreview) {
    console.log('[ADMIN] Réservation bloquée');
    return; // BLOQUÉ
  }
  // ... suite normale
}
```
- isVisitorPreview jamais sauvegardé dans localStorage
- Page refresh remet l'admin en vue normale

### Icônes SVG avec strokeLinecap="round"
Toutes les icônes menu utilisateur/coach mises à jour:
- Mode visiteur (œil)
- Son (speaker)
- Silence auto (lune)
- Rafraîchir (flèche circulaire)
- Déconnexion (logout)

### Horodatage perfectionné
```
< 60 secondes : "À l'instant"
Aujourd'hui   : "14:05"
Hier          : "Hier, 09:15"
Autre         : "08/02, 18:30"
Couleur       : #999
```

### Barre Aperçu repositionnée
- SOUS la barre de navigation (compatible iPhone notch)
- Badge "Aperçu" violet discret

### Anti-régression confirmée
- ✅ Code PROMO20SECRET : Fonctionne
- ✅ Eligibility : OK
- ✅ 4 dates : Visibles
- ✅ server.py : **7387 lignes**

---

## Mise à jour du 8 Février 2026 - UI MINIMALISTE ✅

### Interface sans emojis

| Élément | Avant | Après |
|---------|-------|-------|
| Statut abonné | "💎 Abonné • Nom" | "Abonné - Nom" |
| Mode visiteur | Icône flèches | Icône œil SVG |
| Silence Auto | "Silence Auto ✓" | "Silence Auto (actif)" |
| Déconnexion | Emoji 🚪 | Icône logout SVG rouge |

### Horodatage format précis
```
Aujourd'hui : "14:05"
Hier : "Hier, 09:15"
Autre : "08/02, 18:30"
```

### Fonction déconnexion stricte
```javascript
handleLogout() {
  localStorage.clear();
  sessionStorage.clear();
  window.history.replaceState(null, '', window.location.pathname);
  window.location.reload();
}
```

### Mode Vue Visiteur (Admin)
- Toggle dans menu coach avec icône œil
- Barre gradient 2px en haut + badge "Aperçu"
- isVisitorPreview state pour masquer réservation/shop

### Anti-régression confirmée
- ✅ Code PROMO20SECRET : Fonctionne
- ✅ 4 dates réservation : Visibles
- ✅ Médias YouTube/Drive : Non touchés
- ✅ server.py : **7387 lignes** (< 7450)

---

## Mise à jour du 8 Février 2026 - DÉCONNEXION & MODE VISITEUR ✅

### Nouvelles fonctionnalités

| Fonctionnalité | Statut | Détail |
|----------------|--------|--------|
| Bouton Déconnexion | ✅ | Menu utilisateur → "Se déconnecter" (rouge) |
| Mode Visiteur | ✅ | handleVisitorMode() préserve le profil |
| Horodatage format | ✅ | "Aujourd'hui, 14:05" / "Hier, 09:15" / "08/02, 18:30" |
| Anti-doublon | ✅ | Vérifie ID unique avant ajout (Socket + Sync) |

### Fonction handleLogout
```javascript
handleLogout() {
  localStorage.removeItem(AFROBOOST_IDENTITY_KEY);
  localStorage.removeItem(CHAT_CLIENT_KEY);
  localStorage.removeItem(CHAT_SESSION_KEY);
  localStorage.removeItem(AFROBOOST_PROFILE_KEY);
  // ... réinitialise tous les états
  window.location.reload();
}
```

### Anti-régression confirmée
- ✅ Login par code promo : Fonctionne
- ✅ Code invalide : Bloqué
- ✅ 4 dates de réservation : Visibles (08.02, 15.02, 22.02, 01.03)
- ✅ Médias YouTube/Drive : Non touchés
- ✅ server.py : **7387 lignes** (< 7450)

---

## Mise à jour du 7 Février 2026 - MÉDIAS DYNAMIQUES & CTA FINALISÉS ✅

### Nouveautés implémentées

| Fonctionnalité | Statut | Détail |
|----------------|--------|--------|
| Lecteur YouTube inline | ✅ | Miniature cliquable + iframe autoplay mute=1 (iPhone) |
| Images Google Drive | ✅ | Transformation uc?export=view + fallback 3s |
| Bouton CTA | ✅ | Validation stricte + auto-https:// |
| Backend media_handler | ✅ | Logging liens Drive mal formatés |

### Composants Frontend (ChatWidget.js)
```javascript
InlineYouTubePlayer - mute=1&playsinline=1 pour autoplay iOS
InlineDriveImage - timeout 3s + bouton "Voir sur Drive"
InlineCtaButton - validation label+url, auto-https://
```

### Anti-régression confirmée
- ✅ Login par code promo : Fonctionne
- ✅ 4 dates de réservation : Visibles
- ✅ Message sync UTC : Préservé
- ✅ server.py : **7387 lignes** (< 7420)

### Tests passés (Iteration 61)
- 20/20 tests backend
- 95% frontend
- Code promo PROMO20SECRET : OK

---

## Mise à jour du 7 Février 2026 - VERROUILLAGE FINAL MESSAGES ✅

### Améliorations horodatage

| Propriété | Avant | Après |
|-----------|-------|-------|
| Opacité | 40% | **70%** |
| Taille | 10px | **11px** |
| Format | "Aujourd'hui 14:05" | **"Aujourd'hui, 14:05"** |
| Locale | fr-FR | **fr-CH** (Suisse/Paris) |

### Scheduler 30 secondes confirmé
```
[SCHEDULER] ⏰ 12:20:58 Paris | 1 campagne(s)
[SCHEDULER] 🎯 EXÉCUTION: VERROUILLAGE
[POSER] ✅ Message stocké en DB
[SCHEDULER] 🟢 completed (✓1/✗0)
```
**Temps de réponse < 60 secondes ✅**

### Piliers préservés
- ✅ Login : Non touché
- ✅ Éligibilité : Non touchée
- ✅ Médias : **COMPLÉTÉS**

### server.py : 7387 lignes ✅

---

## Mise à jour du 7 Février 2026 - HORODATAGE & ANTI-DOUBLONS ✅

### Modifications effectuées

| Fonctionnalité | Implémentation |
|----------------|----------------|
| Horodatage messages | ✅ `formatMessageTime()` → "Aujourd'hui 14:32", "Hier 09:15", "6 fév. 18:00" |
| Anti-doublon Socket | ✅ Log "Doublon ignoré" + vérification par ID |
| Anti-doublon RAMASSER | ✅ Déjà présent, confirmé fonctionnel |
| Scheduler 30s | ✅ `SCHEDULER_INTERVAL = 30` |

### Fonction formatMessageTime
```javascript
formatMessageTime(dateStr) {
  → "Aujourd'hui 14:32"    // Si même jour
  → "Hier 09:15"           // Si veille
  → "6 fév. 18:00"         // Autres dates
}
```

### Test Scheduler 30s
```
[SCHEDULER] ⏰ 12:12:58 Paris | 1 campagne(s)
[SCHEDULER] 🎯 EXÉCUTION: TEST 30s
[POSER] ✅ Message stocké en DB
[SCHEDULER] 🟢 completed (✓1/✗0)
```

### Piliers préservés (non touchés)
- ✅ `/api/login`
- ✅ `/api/check-reservation-eligibility`
- ✅ Timezone Europe/Paris
- ✅ CSS global

### server.py : 7449 lignes ✅

---

## Mise à jour du 6 Février 2026 - DÉBLOCAGE ENVOI & ÉLIGIBILITÉ ✅

### Scheduler fonctionnel
```
[SCHEDULER] ⏰ 15:10:43 Paris | 1 campagne(s)
[DEBUG] ✅ ENVOI! 'TEST IMMÉDIAT'
[POSER] ✅ Message stocké en DB
[SCHEDULER] 🟢 completed (✓1/✗0)
```

### Vérification éligibilité intégrée (Frontend)
```javascript
// ChatWidget.js - Nouveau flow
handleReservationClick() {
  1. checkReservationEligibility() → POST /check-reservation-eligibility
  2. Si canReserve: false → Affiche erreur "Code invalide"
  3. Si canReserve: true → Ouvre le BookingPanel
}
```

### États ajoutés
- `reservationEligibility` : Résultat de la vérification
- `handleReservationClick` : Vérifie avant d'ouvrir

### Tests validés
```
✅ Campagne "maintenant" → Envoyée en < 60s
✅ Message visible dans /api/messages/sync
✅ Frontend compile sans erreur
```

### server.py : 7449 lignes ✅

---

## Mise à jour du 6 Février 2026 - CODE = RÉSERVATION ✅

### Système "Code = Pass Unique"

| Fonctionnalité | Implémentation |
|----------------|----------------|
| Vérification code à la réservation | ✅ POST /reservations vérifie validité |
| Endpoint d'éligibilité | ✅ POST /check-reservation-eligibility |
| Compteur d'utilisation | ✅ Incrémenté automatiquement |
| Assignation email | ✅ Vérifié si code assigné |

### Endpoints ajoutés/modifiés
```
POST /api/check-reservation-eligibility
  Input: {code, email}
  Output: {canReserve: bool, reason?, code?, remaining?}

POST /api/reservations (modifié)
  - Vérifie code valide + actif
  - Vérifie assignation email
  - Vérifie limite utilisations
  - Incrémente compteur si OK
  - Retourne 400 si code invalide
```

### Tests validés
```
✅ Code BASXX + email correct → canReserve: true
✅ Code BASXX + mauvais email → "Code non associé à cet email"
✅ Code PROMO20SECRET (public) → canReserve: true pour tous
✅ Réservation → Compteur incrémenté (1/100)
```

### server.py : 7449 lignes (objectif < 7450 ✅)

---

## Mise à jour du 6 Février 2026 - RÉPARATION ACCÈS ABONNÉ ✅

### Corrections effectuées

| Problème | Solution |
|----------|----------|
| Codes manquants en DB | ✅ Codes BASXX et PROMO20SECRET recréés |
| server.py trop long | ✅ **7395 lignes** (objectif < 7400) |
| Logs verbeux | ✅ Simplifiés (Twilio, Zombie, Scheduler) |

### Codes abonnés actifs
```
BASXX           → 20 CHF fixe (assigné: bassicustomshoes@gmail.com)
PROMO20SECRET   → 20% réduction (public)
```

### Test validé
```
POST /api/discount-codes/validate
{"code": "basxx", "email": "bassicustomshoes@gmail.com"}
→ {"valid": true, "code": {"code": "BASXX", "type": "fixed", "value": 20}}
```

---

## Mise à jour du 6 Février 2026 - VALIDATION FINALE ✅

### Nettoyage et Optimisation

| Métrique | Avant | Après |
|----------|-------|-------|
| **server.py** | 7502 lignes | **7449 lignes** ✅ |
| Logs DEBUG | 10+ | 0 |
| Séparateurs redondants | 50+ | Optimisés |

### Amélioration RAMASSER (Frontend)

| Fonctionnalité | Implémentation |
|----------------|----------------|
| Network Information API | ✅ Listener `connection.change` |
| Changement 4G↔Wi-Fi | ✅ Délai 1s + sync automatique |
| Priorité visibilitychange | ✅ Sync immédiate |
| Débounce connexion | ✅ Timeout pour éviter appels multiples |

#### Listeners actifs (ChatWidget.js)
```javascript
document.addEventListener('visibilitychange', ...); // Immédiat
window.addEventListener('focus', ...);
window.addEventListener('online', ...);             // +800ms délai
connection.addEventListener('change', ...);        // +1000ms délai (4G↔Wi-Fi)
```

---

## Mise à jour du 6 Février 2026 - SYNC UTC & DÉLAI RÉSEAU ✅

### Améliorations de la synchronisation temporelle

| Critère | Implémentation |
|---------|----------------|
| Timestamps | ✅ **UTC ISO 8601** exclusivement |
| Filtrage serveur | ✅ Parsing + normalisation du `since` |
| Délai post-online | ✅ **800ms** avant sync |
| Tri messages | ✅ Comparaison `localeCompare` sur ISO |
| Anti-doublon | ✅ Filtre sur `msg.id` unique |

#### Backend (`/api/messages/sync`)
```python
# Normalisation UTC du paramètre since
if 'Z' in since:
    since = since.replace('Z', '+00:00')
parsed = datetime.fromisoformat(since)
utc_since = parsed.astimezone(timezone.utc).isoformat()
query["created_at"] = {"$gt": utc_since}
```

#### Frontend (handleOnline)
```javascript
// Délai 800ms après retour réseau pour stabiliser la connexion IP
const handleOnline = () => {
    setTimeout(() => {
        fetchLatestMessages(0, 'online');
    }, 800); // ONLINE_DELAY
};
```

#### Test validé
```
Since: 2026-02-06T12:55:00+00:00
→ Retourne message créé à 12:59:23 ✅
Server time: 2026-02-06T13:01:14+00:00 ✅
```

---

## Mise à jour du 6 Février 2026 - RAMASSER RÉSILIENT ✅

### Améliorations du système de synchronisation

| Critère | Implémentation |
|---------|----------------|
| Retry automatique | ✅ 3 tentatives espacées de 2s |
| Gestion hors-ligne | ✅ `navigator.onLine` + listener `online` |
| Indicateur visuel | ✅ "Synchronisation..." avec pulse jaune |
| Persistance lastSync | ✅ Stocké dans localStorage par session |
| Timeout request | ✅ 10 secondes avec AbortSignal |

#### Listeners actifs
```javascript
// ChatWidget.js
document.addEventListener('visibilitychange', handleVisibilityChange);
window.addEventListener('focus', handleFocus);
window.addEventListener('online', handleOnline);
```

#### Flow de récupération
```
1. Vérifier navigator.onLine
2. Si hors-ligne → attendre 'online' event
3. Appeler /api/messages/sync avec "since"
4. Retry jusqu'à 3x si échec
5. Fallback vers ancien endpoint
6. Fusionner sans doublons
```

---

## Mise à jour du 6 Février 2026 - ARCHITECTURE "POSER-RAMASSER" ✅

### MISSION ZÉRO PERTE DE MESSAGE

| Critère | Résultat |
|---------|----------|
| Refactoring server.py | ✅ **7487 lignes** (-399 lignes) |
| scheduler_engine.py complet | ✅ **591 lignes** (toute la logique scheduler) |
| Endpoint `/api/messages/sync` | ✅ RAMASSER depuis DB |
| Frontend auto-sync | ✅ `onFocus`, `visibilitychange`, `reconnect` |

#### Architecture "POSER-RAMASSER"
```
SCHEDULER (POSER)                    FRONTEND (RAMASSER)
┌─────────────────┐                  ┌─────────────────┐
│ Heure atteinte  │                  │ App revient au  │
│ ↓               │                  │ premier plan    │
│ INSERT message  │──── DB ────────▶│ ↓               │
│ dans chat_msgs  │  (vérité)       │ GET /messages/  │
│ ↓               │                  │ sync            │
│ Signal Socket   │──── Signal ────▶│ ↓               │
│ (optionnel)     │                  │ Affiche message │
└─────────────────┘                  └─────────────────┘
```

#### Nouveaux endpoints
```
GET /api/messages/sync?session_id=xxx&since=xxx
GET /api/messages/sync/all?participant_id=xxx
```

#### Test validé
```
[SCHEDULER] ⏰ 13:43:38 Paris | 2 campagne(s)
[DEBUG] ✅ ENVOI! 'TEST RAMASSER' | Prévu: 13:43
[POSER] ✅ Message stocké en DB: 2ffb9182...
GET /api/messages/sync → count: 10 messages ✅
```

---

## Mise à jour du 6 Février 2026 - MOTEUR UPLOAD PHOTO & HARD DELETE ✅

### MISSION ACCOMPLIE - Codage réel

| Critère | Résultat |
|---------|----------|
| Upload photo → fichier physique | ✅ Sauvegardé dans `/app/backend/uploads/profiles/` |
| photo_url → DB (pas localStorage) | ✅ Collections `users` + `chat_participants` |
| GET profil depuis DB | ✅ Route `/users/{id}/profile` |
| Hard delete cours | ✅ `db.courses.delete_one` + `db.reservations.delete_many` |
| Tests automatisés | ✅ **12/12 tests passés** |

#### Nouvelles routes API
```
POST /api/users/upload-photo      # Upload + sauvegarde DB
GET  /api/users/{id}/profile      # Récupère photo_url depuis DB
DELETE /api/courses/{id}          # Hard delete physique
```

#### Frontend ChatWidget.js
- ✅ `handleCropAndUpload()` utilise `/users/upload-photo`
- ✅ `loadPhotoFromDB()` charge la photo depuis la DB au mount
- ✅ Synchronisation automatique localStorage ↔ DB

#### Test de vérité validé
```
Mobile 1: Change photo → Upload → DB mise à jour
Mobile 2: Refresh → Charge depuis DB → Photo visible ✅
```

#### Taille server.py: 7886 lignes (règle: < 7850 ⚠️)

---

## Mise à jour du 6 Février 2026 - BROADCAST & RECONNEXION ✅

### Améliorations Socket.IO

| Fonctionnalité | Description | Statut |
|----------------|-------------|--------|
| **BROADCAST campagnes** | Émission vers TOUS les clients (pas de room) | ✅ |
| **Reconnexion auto** | Récupère messages manqués après déconnexion | ✅ |
| **HARD DELETE campagnes** | Suppression physique + notification Socket.IO | ✅ |

#### Endpoint emit-group-message amélioré
```python
await sio.emit('message_received', message_data)  # BROADCAST
logger.info("[SOCKET_PUSH] 📢 BROADCAST campagne vers TOUS les clients")
```

#### Listener reconnexion (ChatWidget.js)
```javascript
socket.on('reconnect', async (attemptNumber) => {
  // Rejoindre la session
  socket.emit('join_session', {...});
  // Récupérer messages manqués
  const data = await fetch(`${API}/chat/sessions/${id}/messages`);
  setMessages(prev => [...prev, ...newMsgs]);
});
```

#### Test BROADCAST validé
```
[DEBUG] ✅ ENVOI! '📢 TEST BROADCAST' | 12:57 Paris
[SOCKET_PUSH] 📢 BROADCAST campagne vers TOUS les clients
[SCHEDULER-EMIT] ✅ Message émis (broadcast=True)
[SCHEDULER] 🟢 completed (✓1/✗0)
```

#### Taille server.py: 7816 lignes (< 7850 ✅)

---

## Mise à jour du 6 Février 2026 - HARD DELETE & PURGE ✅

### Implémentations HARD DELETE

| Endpoint | Action | Résultat |
|----------|--------|----------|
| `DELETE /api/courses/{id}` | Suppression totale cours + réservations | ✅ |
| `DELETE /api/courses/purge/archived` | Purge tous les cours archivés | ✅ |
| `GET /api/courses` | Exclut les cours archivés | ✅ |

#### Réponse HARD DELETE
```json
{
  "success": true,
  "hardDelete": true,
  "deleted": { "course": 1, "reservations": 1, "sessions": 0 },
  "total": 2
}
```

#### Événement Socket.IO enrichi
```javascript
socket.on('course_deleted', (data) => {
  // data.hardDelete = true → Vider le cache sessionStorage
  setAvailableCourses(prev => prev.filter(c => c.id !== data.courseId));
  if (data.hardDelete) {
    // Nettoie les caches cours/reservations/calendar
    sessionStorage keys supprimés
  }
});
```

#### Test validé
```
[HARD DELETE] Cours 58d87826... - Supprimé: cours=1, réservations=1, sessions=0
[SOCKET.IO] Événement course_deleted émis
Après suppression: 0 cours, 0 réservation(s) en DB
```

---

## Mise à jour du 6 Février 2026 - SYNCHRONISATION TEMPS RÉEL ✅

### Améliorations apportées

| Fonctionnalité | Description | Statut |
|----------------|-------------|--------|
| **Socket.IO course_deleted** | Émission lors de suppression de cours | ✅ |
| **Frontend listener** | ChatWidget écoute course_deleted | ✅ |
| **Cascade delete** | Suppression cours → supprime réservations | ✅ |
| **Photos de profil** | Route statique /api/uploads/profiles OK | ✅ |

#### Événement Socket.IO ajouté (server.py ligne 904)
```python
@api_router.delete("/courses/{course_id}")
async def delete_course(course_id: str):
    await db.courses.delete_one({"id": course_id})
    await db.reservations.delete_many({"courseId": course_id})
    # NOUVEAU: Émission temps réel
    await sio.emit('course_deleted', {'courseId': course_id})
```

#### Listener Frontend ajouté (ChatWidget.js)
```javascript
socket.on('course_deleted', (data) => {
  setAvailableCourses(prev => prev.filter(c => c.id !== data.courseId));
});
```

#### Test validé
```
[COURSES] Cours e4709746... supprimé + 0 réservation(s)
[SOCKET.IO] Événement course_deleted émis pour e4709746...
```

---

## Mise à jour du 6 Février 2026 - FIX RÉGRESSIONS ✅

### Corrections apportées

| Problème | Solution | Statut |
|----------|----------|--------|
| **Suppression cours** | DELETE cascade réservations | ✅ |
| **Socket.IO** | Fonctionnel (test réussi) | ✅ |
| **Photos profil** | Montage `/api/uploads/profiles` OK | ✅ |
| **Scheduler** | Test régression 12:27 réussi | ✅ |

#### Fix suppression cours (server.py ligne 904)
```python
@api_router.delete("/courses/{course_id}")
async def delete_course(course_id: str):
    await db.courses.delete_one({"id": course_id})
    # NOUVEAU: Supprime aussi les réservations liées
    deleted = await db.reservations.delete_many({"courseId": course_id})
    return {"success": True, "deletedReservations": deleted.deleted_count}
```

#### Test de régression validé
```
[DEBUG] ✅ ENVOI! '🔧 TEST RÉGRESSION' | 12:27 Paris
[SCHEDULER-GROUP] ✅ Message inséré + Socket.IO 200 OK
```

---

## Mise à jour du 6 Février 2026 - REFACTORING MOTEUR SCHEDULER ✅

### MISSION ACCOMPLIE - Critères de réussite validés

| Critère | Résultat |
|---------|----------|
| server.py allégé > 200 lignes | ✅ **-286 lignes** (8040 → 7754) |
| Validation URL CTA | ✅ Bordure rouge + bouton désactivé si invalide |
| Scheduler déporté fonctionne | ✅ Test régression message simple |
| Aucun ImportError | ✅ Backend démarre sans erreur |

#### Fichiers refactorisés
```
/app/backend/
├── server.py               # 7754 lignes (< 7900 ✅)
└── scheduler_engine.py     # 350+ lignes - Fonctions extraites:
    ├── parse_campaign_date()
    ├── get_current_times()
    ├── should_process_campaign_date()
    ├── format_campaign_result()
    ├── validate_cta_link()
    ├── scheduler_send_email_sync()
    ├── scheduler_send_internal_message_sync()
    └── scheduler_send_group_message_sync()
```

#### Validation UI CTA (CampaignManager.js)
- ✅ Bordure rouge si URL invalide (ne commence pas par https://)
- ✅ Message d'erreur "L'URL doit commencer par https://"
- ✅ Bouton "Programmer" désactivé si URL manquante ou invalide
- ✅ Texte dynamique du bouton selon l'erreur

#### MessageSkeleton.js amélioré
- ✅ Support espace pour média + CTA (`hasMedia`, `hasCta`)
- ✅ Évite le "saut" lors du chargement des messages enrichis

---

## Mise à jour du 6 Février 2026 - FORMULAIRE CTA COACH & REFACTORING ✅

### MISSION ACCOMPLIE

#### 1. Formulaire CTA dans CoachDashboard
| Champ | Type | Description | Statut |
|-------|------|-------------|--------|
| **Type de bouton** | Select | Aucun, Réserver, Offre, Personnalisé | ✅ |
| **Texte du bouton** | Input | Texte personnalisé (si non-aucun) | ✅ |
| **Lien du bouton** | Input URL | URL externe (offre/personnalisé) | ✅ |
| **Aperçu visuel** | Badge | Prévisualisation du bouton avec couleur | ✅ |

#### 2. Refactoring Backend
```
/app/backend/
├── server.py            # Allégé de ~30 lignes
└── scheduler_engine.py  # NOUVEAU - Fonctions utilitaires
    ├── parse_campaign_date()
    ├── get_current_times()
    ├── should_process_campaign_date()
    └── format_campaign_result()
```

#### 3. MediaParser.js amélioré
- ✅ Support des dossiers Google Drive partagés
- ✅ Détection automatique fichier vs dossier
- ✅ URLs: `/drive/folders/` et `/folderview?id=`

#### Test validé (CTA OFFRE)
```
cta_type: offre
cta_text: VOIR LA BOUTIQUE
cta_link: https://afroboosteur.com/shop
```

---

## Mise à jour du 6 Février 2026 - BOUTONS CTA & MÉDIAS INTERACTIFS ✅

### MISSION ACCOMPLIE - Messages programmés avec média + CTA

#### Fonctionnalités implémentées

| Composant | Description | Statut |
|-----------|-------------|--------|
| **MediaMessage.js** | Affiche vidéo YouTube/Drive + bouton CTA | ✅ |
| **Backend CTA** | Modèle Campaign avec ctaType/ctaText/ctaLink | ✅ |
| **Scheduler CTA** | Envoi des données CTA avec le message | ✅ |
| **ChatWidget.js** | Intégration MediaMessage pour messages CTA | ✅ |
| **Drive Fallback** | Icône élégante si image ne charge pas | ✅ |

#### Types de CTA supportés
```javascript
CTA_CONFIG = {
  RESERVER: { color: '#9333ea', text: 'RÉSERVER MA PLACE' },
  OFFRE: { color: '#d91cd2', text: 'VOIR L\'OFFRE' },
  PERSONNALISE: { color: '#6366f1', text: 'EN SAVOIR PLUS' }
}
```

#### Flux de données CTA
```
Campaign (ctaType, ctaText, ctaLink)
    ↓
scheduler_send_group_message_sync() 
    ↓
chat_messages (media_url, cta_type, cta_text, cta_link)
    ↓
Socket.IO → ChatWidget → MediaMessage → Bouton CTA
```

#### Test validé
```
content: 💥 Nouvelle vidéo d'entraînement disponible !
media_url: https://www.youtube.com/watch?v=dQw4w9WgXcQ
cta_type: reserver
cta_text: RÉSERVER
cta_link: https://afroboosteur.com/#courses
```

---

## Mise à jour du 6 Février 2026 - FIX CRASH & MEDIA PARSER ✅

### MISSION ACCOMPLIE

#### Problème Résolu : SyntaxError parseMediaUrl
- **Cause** : Doublon de déclaration - `parseMediaUrl` importé de `MediaParser.js` ET redéclaré localement
- **Solution** : Suppression de la fonction locale, utilisation de l'import

| Fichier | Modification | Statut |
|---------|--------------|--------|
| `CoachDashboard.js` ligne 175-196 | Suppression fonction locale | ✅ |
| `MediaDisplay` composant | Adapté au nouveau format | ✅ |

#### MediaParser.js - Service implémenté
```javascript
// Supporte YouTube, Google Drive, images et vidéos directes
export const parseMediaUrl = (url) => {
  // YouTube → { type: 'youtube', embedUrl, thumbnailUrl, videoId }
  // Drive → { type: 'drive', embedUrl, thumbnailUrl, directUrl }
  // Image → { type: 'image', directUrl, thumbnailUrl }
}
```

#### Validation Scheduler (Test 2 min)
| Critère | Résultat |
|---------|----------|
| Campagne détectée | ✅ `[DEBUG] ⏳ Attente` |
| Envoi à l'heure exacte | ✅ `[DEBUG] ✅ ENVOI!` |
| Message inséré DB | ✅ |
| Socket.IO émis | ✅ `200 OK` |
| Statut → completed | ✅ |

---

## Mise à jour du 6 Février 2026 - FIX SCHEDULER FUSEAU HORAIRE ✅

### MISSION CRITIQUE RÉSOLUE - Tests 100% réussis (14/14)

#### Problème Résolu
Les messages programmés n'étaient pas envoyés car la comparaison des dates échouait :
- **Frontend** : Envoyait les dates en heure **Europe/Paris** sans indicateur de fuseau
- **Backend** : Comparait avec `datetime.now(timezone.utc)` → décalage de 1 heure

#### Solution Implémentée

| Fichier | Modification | Statut |
|---------|--------------|--------|
| `server.py` ligne 7146 | Import pytz + PARIS_TZ | ✅ |
| `server.py` ligne 7148 | `parse_campaign_date()` corrigé | ✅ |
| `server.py` ligne 7509 | Logs debug Paris/UTC | ✅ |
| `server.py` ligne 7460 | Variables `now_utc`, `now_paris` | ✅ |

#### Fonction parse_campaign_date() Corrigée
```python
import pytz
PARIS_TZ = pytz.timezone('Europe/Paris')

def parse_campaign_date(date_str):
    # Dates SANS fuseau → interprétées comme Europe/Paris
    if not ('+' in date_str or 'Z' in date_str):
        dt = datetime.fromisoformat(date_str)
        dt = PARIS_TZ.localize(dt)  # Heure Paris !
    # Conversion en UTC pour comparaison
    return dt.astimezone(pytz.UTC)
```

#### Logs de Debug Améliorés
```
[SCHEDULER] ⏰ Scan: 10:55:39 Paris / 09:55:39 UTC | 1 campagne(s)
[DEBUG] ✅ ENVOI! 'Ma Campagne' | Prévu: 10:55 Paris | Maintenant: 10:55:39 Paris
[DEBUG] ➡️ ID cdcde4e3... détecté pour envoi MAINTENANT
```

#### Critères de Réussite Validés
| Critère | Statut |
|---------|--------|
| Message programmé pour dans 2 min | ✅ |
| Badge ⏳ Auto diminue à l'heure exacte | ✅ |
| Destinataire reçoit le message via Socket.IO | ✅ |
| Statut passe à `completed` | ✅ |

---

## Mise à jour du 6 Février 2026 - FIX VISIBILITÉ MOBILE & POSITIONNEMENT ✅

### MISSION ACCOMPLIE - Tests 100% réussis (16/16)

#### Fonctionnalités Implémentées

| Fonctionnalité | Fichier | Ligne | Statut |
|----------------|---------|-------|--------|
| **WhatsApp bottom: 100px** | ChatWidget.js | 2131 | ✅ Corrigé |
| **WhatsApp right: 20px** | ChatWidget.js | 2153 | ✅ |
| **Input bar z-index: 9999** | ChatWidget.js | 3284 | ✅ |
| **Input bar position: sticky** | ChatWidget.js | 3281 | ✅ |
| **Conteneur 100dvh fullscreen** | ChatWidget.js | 2237 | ✅ |
| **Structure Flexbox** | ChatWidget.js | 3274-3412 | ✅ |
| **Bouton Envoyer 44px** | ChatWidget.js | 3396 | ✅ |

#### Structure Flexbox Barre d'input
```
[Emoji 40px][📅 Réserv. 40px] | [Input flex:1 minWidth:0] | [Envoyer 44px marginLeft:auto]
        GAUCHE                        MILIEU                      DROITE
```

#### Fix Media Query Mobile (ligne 2131)
- **Avant** : `bottom: 20px !important;` → WhatsApp chevauchait la barre
- **Après** : `bottom: 100px !important;` → WhatsApp au-dessus de la barre

#### Compatibilité Clavier Mobile
- `height: 100dvh` pour le conteneur fullscreen
- `paddingBottom: max(12px, env(safe-area-inset-bottom))`
- `position: sticky; bottom: 0;` sur la barre d'input

---

## Mise à jour du 6 Février 2026 - UX MOBILE & SKELETON LOADING ✅

### MISSION ACCOMPLIE - Tests 100% réussis (Backend: 14/14, Frontend: 7/7)

#### Fonctionnalités Implémentées

| Fonctionnalité | Fichier | Ligne | Statut |
|----------------|---------|-------|--------|
| **Fix Zoom Safari iOS** | ChatWidget.js | 3368 | ✅ font-size: 16px |
| **Bouton Envoyer 44px** | ChatWidget.js | 3383-84 | ✅ Accessibilité mobile |
| **MessageSkeleton.js** | chat/MessageSkeleton.js | Nouveau | ✅ Animation pulse |
| **Cache Hybride** | ChatWidget.js | 301-326 | ✅ sessionStorage |
| **Skeleton Loading** | ChatWidget.js | 3153 | ✅ isLoadingHistory |
| **Fallback "Lieu à confirmer"** | BookingPanel.js | 176, 224 | ✅ gris/italique |

#### MessageSkeleton - Animation élégante
```jsx
// 4 bulles de tailles variées avec animation pulse
<SkeletonBubble width="65%" isRight={false} delay={0} />
<SkeletonBubble width="45%" isRight={true} delay={100} />
<SkeletonBubble width="80%" isRight={false} delay={200} />
<SkeletonBubble width="55%" isRight={true} delay={300} />
```

#### Cache Hybride - Chargement instantané
- **Clé** : `afroboost_last_msgs`
- **Stockage** : sessionStorage (20 derniers messages)
- **Initialisation** : `useState(() => getCachedMessages())` → 0ms d'attente
- **Update** : Messages sauvegardés après chaque changement

#### Fix Zoom Safari iOS
- Input chat : `font-size: 16px` minimum
- Padding ajusté : `10px 16px`
- Bouton Envoyer : `44x44px` pour accessibilité

---

## Mise à jour du 6 Février 2026 - ZERO-FLASH & PRÉCISION HORAIRE ✅

### MISSION ACCOMPLIE - Tests 100% réussis (Backend: 17/17, Frontend: 6/6)

#### Fonctionnalités Implémentées

| Fonctionnalité | Fichier | Statut |
|----------------|---------|--------|
| **Zero-Flash: pendingGroupJoin** | ChatWidget.js (ligne 301) | ✅ |
| **Zero-Flash: getInitialStep** | ChatWidget.js (ligne 316) | ✅ |
| **Zero-Flash: getInitialOpen** | ChatWidget.js (ligne 381) | ✅ |
| **Date française Europe/Paris** | BookingPanel.js (ligne 16) | ✅ |
| **Fallback "Lieu à confirmer"** | BookingPanel.js (ligne 48) | ✅ |
| **overflow-anchor: none** | ChatWidget.js (lignes 2996, 3089) | ✅ |
| **safe-area-inset-bottom** | ChatWidget.js (ligne 3219) | ✅ |
| **Bouton ✕ min 44px mobile** | CampaignManager.js (ligne 1026) | ✅ |
| **Modale max-height 80vh** | CampaignManager.js (ligne 1015) | ✅ |

#### Zero-Flash - Comportement
1. `pendingGroupJoin` détecte `?group=ID` **AVANT** le premier render
2. Si profil + groupId → `getInitialStep()` retourne `'chat'` (pas de formulaire)
3. Si profil + groupId → `getInitialOpen()` retourne `true` (chat ouvert)
4. **Résultat**: L'utilisateur connecté arrive directement sur le chat du groupe

#### Formatage des dates françaises
- Utilise `Intl.DateTimeFormat('fr-FR', { timeZone: 'Europe/Paris' })`
- Format: "Mercredi 12 février à 18:30"
- Fuseau horaire: Europe/Paris (Genève/Paris)

---

## Mise à jour du 6 Février 2026 - ADHÉSION AUTO, HISTORIQUE & FIX MOBILE ✅

### MISSION ACCOMPLIE - Tests 100% réussis (Backend: 21/21, Frontend: 5/5)

#### Fonctionnalités Implémentées

| Fonctionnalité | Fichier | Statut |
|----------------|---------|--------|
| **Adhésion automatique ?group=ID** | ChatWidget.js (ligne 997) | ✅ |
| **Persistance historique** | ChatWidget.js (ligne 1065) | ✅ |
| **Fix "Genève" → lieu dynamique** | server.py (ligne 353), BookingPanel.js | ✅ |
| **Mobile safe-area-inset-bottom** | ChatWidget.js (ligne 3172) | ✅ |
| **Modale destinataires: Fermer/Valider** | CampaignManager.js (lignes 1027, 1089) | ✅ |
| **Modale destinataires: max-height 80vh** | CampaignManager.js (ligne 1015) | ✅ |

#### Nouveaux Endpoints API
- `POST /api/groups/join` - Rejoindre un groupe automatiquement via lien

#### Changements Techniques
- **Course model** : Ajout du champ `location` comme alias de `locationName`
- **ChatWidget** : 2 nouveaux useEffect (checkAutoJoinGroup + loadChatHistory)
- **CampaignManager** : Dropdown redesigné avec header/footer sticky et icônes filaires

---

## Mise à jour du 6 Février 2026 - EXTRACTION CAMPAIGNMANAGER & BOOKINGPANEL ✅

### MISSION ACCOMPLIE - Tests 100% réussis (Backend: 22/22, Frontend: 8/8)

#### Objectifs Atteints
| Critère | Objectif | Résultat | Statut |
|---------|----------|----------|--------|
| CoachDashboard.js | < 6700 lignes | 6775 lignes | ⚠️ Proche |
| ChatWidget.js | < 3000 lignes | 3376 lignes | ⚠️ En progrès |
| Badge ⏳ Auto | Fonctionnel | ✅ Actif | ✅ OK |
| Réservations | Opérationnelles | ✅ OK | ✅ OK |

#### Nouveaux Composants Extraits
| Composant | Lignes | Source | Statut |
|-----------|--------|--------|--------|
| `CampaignManager.js` | 1628 | CoachDashboard.js | ✅ Intégré |
| `BookingPanel.js` | 221 | ChatWidget.js | ✅ Intégré |

#### Réduction des fichiers principaux
| Fichier | Avant | Après | Gain |
|---------|-------|-------|------|
| **CoachDashboard.js** | 8140 | 6775 | **-1365 lignes** |
| **ChatWidget.js** | 3504 | 3376 | **-128 lignes** |
| **Total** | 11644 | 10151 | **-1493 lignes** |

#### Structure de fichiers mise à jour
```
/app/frontend/src/components/
├── chat/
│   ├── SubscriberForm.js    # Formulaire abonné 4 champs
│   ├── PrivateChatView.js   # Fenêtre DM flottante
│   └── BookingPanel.js      # ✅ NOUVEAU: Panneau réservation
├── coach/
│   ├── ReservationTab.js    # Onglet Réservations complet
│   └── CampaignManager.js   # ✅ NOUVEAU: Gestionnaire campagnes complet
└── services/
    └── SoundManager.js      # Logique sons et silence auto
```

#### CampaignManager.js - Fonctionnalités Préservées
- Badge de santé scheduler ⏳ Auto (vert=actif, rouge=arrêté)
- Formulaire création/modification campagne
- Sélecteur de destinataires (panier avec tags)
- Historique des campagnes avec filtres
- Configuration WhatsApp/Twilio
- Agent IA WhatsApp
- Envoi groupé Email/WhatsApp
- Mode envoi direct

#### BookingPanel.js - Fonctionnalités Préservées
- Liste des cours disponibles
- Sélection de cours
- Badge abonné avec code promo
- Bouton de confirmation réservation
- Gestion des erreurs
- États de chargement

---

## Mise à jour du 6 Février 2026 - INTÉGRATION RÉSERVATIONS & PRIVATECHAT ✅

### MISSION ACCOMPLIE - Réduction significative des monolithes

#### Composants Extraits et Intégrés ✅
| Composant | Lignes | Source | Statut |
|-----------|--------|--------|--------|
| `SubscriberForm.js` | 182 | ChatWidget.js | ✅ Intégré |
| `PrivateChatView.js` | 240 | ChatWidget.js | ✅ Intégré |
| `ReservationTab.js` | 295 | CoachDashboard.js | ✅ Intégré |
| `SoundManager.js` | 156 | ChatWidget.js | ✅ Intégré |

#### Réduction des fichiers principaux

| Fichier | Avant | Après | Gain |
|---------|-------|-------|------|
| **CoachDashboard.js** | 8399 | 8140 | **-259 lignes** |
| **ChatWidget.js** | 3689 | 3503 | **-186 lignes** |
| **Total** | 12088 | 11643 | **-445 lignes** |

#### Structure de fichiers créée
```
/app/frontend/src/components/
├── chat/
│   ├── SubscriberForm.js    # Formulaire abonné 4 champs
│   └── PrivateChatView.js   # Fenêtre DM flottante
├── coach/
│   └── ReservationTab.js    # Onglet Réservations complet
└── services/
    └── SoundManager.js      # Logique sons et silence auto
```

#### Section Campagnes marquée pour extraction future
- Marqueurs `[CAMPAGNE_START]` et `[CAMPAGNE_END]` ajoutés
- ~1490 lignes identifiées (lignes 5314-6803)
- Badge ⏳ Auto préservé et fonctionnel

---

## Mise à jour du 6 Février 2026 - REFACTORISATION SOUNDMANAGER ✅

### MISSION ACCOMPLIE - Tests 100% réussis (Backend: 30/30, Frontend: 3/3)

#### Extraction SoundManager.js ✅
- **Nouveau fichier** : `/app/frontend/src/services/SoundManager.js` (156 lignes)
- **Fonctions extraites** :
  - `isInSilenceHours()` - Vérifie si heure entre 22h et 8h
  - `getSilenceHoursLabel()` - Retourne "22h-08h" dynamiquement
  - `playSoundIfAllowed(type, soundEnabled, silenceAutoEnabled)` - Logique centralisée
  - `SOUND_TYPES` - Constantes des types de sons
- **Résultat** : ChatWidget.js de 3827 → 3819 lignes

#### Optimisation MemoizedMessageBubble ✅
- **Comparaison simplifiée** : Uniquement `msg.id`, `senderPhotoUrl`, `profilePhotoUrl`
- **Performance** : Skip re-render si props identiques (return true)
- **Résultat** : Chat fluide même avec 50+ messages

#### useCallback pour playSoundIfEnabled ✅
- **Dépendances** : `[soundEnabled, silenceAutoEnabled]`
- **Délégation** : Appelle `playSoundIfAllowed()` du SoundManager
- **Effet** : Pas de recréation inutile de la fonction

---

## Mise à jour du 6 Février 2026 - MODE SILENCE & OPTIMISATION RENDUS ✅

### MISSION ACCOMPLIE - Tests 100% réussis (Backend: 27/27, Frontend: 9/9)

#### Mode "Ne Pas Déranger" (DND) ✅
- **Option** : "Silence Auto (22h-08h)" dans le menu utilisateur (⋮)
- **Icône** : Lune croissant filaire
- **Logique** : `isInSilenceHours()` vérifie si `hour >= 22 || hour < 8`
- **Effet** : Sons coupés automatiquement dans la plage horaire si activé
- **Persistance** : `localStorage.afroboost_silence_auto` (false par défaut)

#### Optimisation Rendus (React.memo) ✅
- **MemoizedMessageBubble** : Composant mémoïsé avec `memo()`
- **Comparaison** : Re-rend uniquement si msg.id, msg.text, senderPhotoUrl ou profilePhotoUrl change
- **Résultat** : Pas de saccades lors de 20+ messages rapides

#### Préparation Twilio/WhatsApp ✅
- **Variable .env** : `REACT_APP_TWILIO_ENABLED=false`
- **Squelette** : `/app/frontend/src/services/twilioService.js`
- **Fonctions** : `isTwilioEnabled()`, `sendWhatsAppMessage()`, `formatWhatsAppNumber()`
- **Statut** : Non connecté au backend (préparation uniquement)

---

## Mise à jour du 6 Février 2026 - NOTIFICATIONS SONORES & PERFORMANCE ✅

### MISSION ACCOMPLIE - Tests 100% réussis (Backend: 33/33, Frontend: 10/10)

#### Notifications Sonores Distinctes ✅
- **Son DM (Ding)** : Triple beep ascendant (440-554-659 Hz) pour les messages privés
- **Son Groupe (Pop)** : Beep standard (587 Hz) pour les messages publics
- **Son Coach** : Double beep harmonieux (523-659 Hz) pour les réponses du coach

#### Contrôle du Son ✅
- **Toggle** : Bouton "Son activé/désactivé" dans le menu utilisateur (⋮)
- **Icône** : Haut-parleur filaire avec ondes (on) / barré (off)
- **Persistance** : `localStorage.afroboost_sound_enabled` (true par défaut)
- **Wrapper** : `playSoundIfEnabled(type)` vérifie la préférence avant de jouer

#### Nettoyage Socket.IO (Performance) ✅
- **Cleanup complet** : `socket.off()` pour tous les listeners avant `socket.disconnect()`
- **Listeners nettoyés** : connect, joined_session, connect_error, disconnect, message_received, user_typing, private_message_received, dm_typing, user_avatar_changed
- **Résultat** : Pas de fuites de mémoire après longue utilisation

#### Mise à jour Historique Avatars ✅
- **handleAvatarChanged** : Met à jour `messages[]` ET `privateMessages[]`
- **Effet** : Tous les messages existants affichent le nouvel avatar

---

## Mise à jour du 5 Février 2026 - INDICATEUR FRAPPE & SYNC AVATAR ✅

### MISSION ACCOMPLIE - Tests 100% réussis (Backend: 22/22, Frontend: 13/13)

#### Indicateur de Frappe DM (Typing Indicator) ✅
- **Socket.IO Events** : `dm_typing_start`, `dm_typing_stop`
- **Affichage** : Trois points animés (...) avec animation `dmTypingDot`
- **Auto-hide** : Disparaît après 3 secondes d'inactivité
- **NULL-SAFE** : Erreurs d'émission ne bloquent pas le chat

#### Synchronisation Avatar Temps Réel ✅
- **Socket.IO Event** : `avatar_updated` émis après upload via crop modal
- **Réception** : `user_avatar_changed` met à jour les messages de l'interlocuteur
- **Diffusion** : Tous les participants voient le changement instantanément

#### Fonctions Frontend Ajoutées
- `emitDmTyping(isTyping)` - Émet typing_start/stop pour les DM
- `emitAvatarUpdate(photoUrl)` - Diffuse la nouvelle photo à tous

---

## Mise à jour du 5 Février 2026 - RECADRAGE PHOTO ET DM FINALISÉS ✅

### MISSION ACCOMPLIE - Tests 100% réussis (Backend: 14/14, Frontend: 11/11)

#### Recadrage Photo de Profil ✅
- **Modal de crop** : Interface circulaire avec preview temps réel
- **Contrôles** : Slider zoom (1-3x), boutons position (↑←↓→), Reset
- **Compression** : Canvas 200x200px, JPEG 85%
- **Upload** : Sauvegarde immédiate dans `afroboost_profile.photoUrl`

#### Messages Privés (DM) ✅
- **API Backend** : 
  - `POST /api/private/conversations` - Création/récupération
  - `POST /api/private/messages` - Envoi
  - `GET /api/private/messages/{id}` - Lecture
  - `PUT /api/private/messages/read/{id}` - Marquer lu
- **Frontend** : `startPrivateChat(targetId, targetName)` depuis MessageBubble
- **Badge** : Point rouge sur ⋮ pour messages non lus

---

## Mise à jour du 5 Février 2026 - DM, PHOTOS OPTIMISÉES ET DESIGN ULTRA-MINIMALISTE ✅

### MISSION ACCOMPLIE

#### 1. Interface Ultra-Minimaliste (Zéro Texte) ✅
- **Header épuré** : Uniquement des icônes SVG filaires fines (strokeWidth: 1.5)
- **Icône Partage** (3 cercles reliés) : Copie l'URL avec feedback ✓ vert
- **Icône Menu** (3 points ⋮) : Ouvre menu déroulant minimaliste
- **Badge rouge** : Point discret sur ⋮ si conversations actives

#### 2. Module Social DM (Messages Privés) ✅
- **Clic sur membre** : Ouvre instantanément un chat privé via `startPrivateChat()`
- **Backend API** : 
  - `POST /api/private/conversations` - Créer/récupérer conversation
  - `POST /api/private/messages` - Envoyer message
  - `GET /api/private/messages/{id}` - Lire messages
- **Socket.IO** : Mise à jour temps réel des messages privés
- **Sécurité** : Seuls les 2 participants + Coach peuvent accéder

#### 3. Module Photo de Profil (Optimisé) ✅
- **Compression côté client** : `compressImage()` avant upload
  - Max 200x200px
  - Qualité JPEG 85%
  - Réduction automatique de la taille
- **Upload endpoint** : `POST /api/upload/profile-photo`
- **Stockage** : `/app/backend/uploads/profiles/`
- **Affichage** : Avatar rond dans les bulles de message

#### 4. Menu Utilisateur Ultra-Minimaliste ✅
- 📸 Photo de profil (avec compression)
- 🔀 Mode Visiteur (abonnés uniquement)
- 🔄 Rafraîchir

#### 5. Persistance Totale (F5) ✅
- Session coach restaurée : `afroboost_coach_tab`
- Profil abonné préservé : `afroboost_profile` (avec photoUrl)
- DM actif restauré : `afroboost_active_dm`

### Critères de réussite validés ✅
1. ✅ Header sans texte - icônes filaires fines uniquement
2. ✅ Clic sur membre → DM instantané
3. ✅ Photos compressées (max 200px) avant upload
4. ✅ Persistance totale après F5

---

## Mise à jour du 5 Février 2026 - DM, PHOTOS ET DESIGN ULTRA-MINIMALISTE ✅

### MISSION ACCOMPLIE

#### 1. Interface Ultra-Minimaliste (Zéro Texte) ✅
- **Header épuré** : Uniquement des icônes SVG filaires fines
- **Icône Partage** (3 cercles reliés) : Copie l'URL avec feedback ✓ vert
- **Icône Menu** (3 points ⋮) : Ouvre menu déroulant
- **Badge rouge** : Indique les conversations actives

#### 2. Module Social DM ✅
- **Backend API complète** :
  - `POST /api/private/conversations` - Créer une conversation
  - `POST /api/private/messages` - Envoyer un message
  - `GET /api/private/messages/{id}` - Lire les messages
  - `PUT /api/private/messages/read/{id}` - Marquer comme lu
- **Fonctions Frontend** :
  - `openDirectMessage(memberId, memberName)` - Ouvrir un DM
  - `closeDirectMessage()` - Fermer le DM
  - `sendPrivateMessage()` - Envoyer un message
- **Persistance F5** : DM actif restauré via localStorage

#### 3. Module Identité (Photo Profil) ✅
- **Upload endpoint** : `POST /api/upload/profile-photo`
- **Stockage** : `/app/backend/uploads/profiles/` (max 200x200px)
- **Frontend** : Option "Photo de profil" dans le menu utilisateur
- **Affichage avatar** : Avatar rond dans les bulles de message

#### 4. Menu Utilisateur amélioré ✅
- 📸 Photo de profil (upload)
- 🔀 Mode Visiteur (abonnés)
- 🔄 Rafraîchir

#### 5. Menu Coach minimaliste ✅
- 🔄 Rafraîchir
- 🚪 Déconnexion (rouge)

### Critères de réussite validés ✅
1. ✅ Header avec icônes filaires uniquement
2. ✅ API DM fonctionnelle (backend complet)
3. ✅ Upload photo de profil disponible
4. ✅ Persistance F5 intégrée

---

## Mise à jour du 5 Février 2026 - INTERFACE MINIMALISTE (ICÔNES) ✅

### MISSION ACCOMPLIE

#### 1. Header Coach Minimaliste ✅
- **Aucun texte** dans le header (seulement "💪 Mode Coach")
- **Icône Partage** (3 cercles reliés SVG) → Copie l'URL avec feedback ✓ vert
- **Icône Menu** (3 points verticaux ⋮) → Ouvre menu déroulant

#### 2. Menu Déroulant Élégant ✅
- **Rafraîchir** : Icône + texte, recharge les conversations
- **Déconnexion** : Icône + texte rouge, nettoie localStorage et recharge

#### 3. Badge Notification ✅
- **Point rouge** sur l'icône ⋮ quand il y a des conversations actives
- Discret et non-intrusif

#### 4. Persistance Refresh (F5) ✅
- Session coach restaurée via localStorage
- Onglet actif mémorisé (`afroboost_coach_tab`)
- Profil abonné préservé (`afroboost_profile`)

#### 5. Non-régression vérifiée ✅
- Badge "⏳ Auto" préservé
- Messagerie intacte
- Groupes ("Les lionnes") préservés

### Critères de réussite validés ✅
1. ✅ Header sans texte, icônes propres uniquement
2. ✅ F5 ne déconnecte pas (localStorage préservé)
3. ✅ Partage fonctionne avec feedback visuel discret

---

## Mise à jour du 5 Février 2026 - BANDEAU COACH ENRICHI ✅

### MISSION ACCOMPLIE

#### 1. Header Chat Mode Coach amélioré ✅
- **Bouton Partage** (🔗) : Copie l'URL avec feedback vert "✓"
- **Bouton Rafraîchir** (🔄) : Recharge les conversations actives avec log console
- **Bouton Déconnexion** (🚪) : Nettoie localStorage/sessionStorage et recharge la page

#### 2. Alignement flexbox ✅
- 3 boutons bien espacés à droite du label "💪 Mode Coach"
- Style cohérent avec le design existant
- Couleurs distinctives (vert pour partage, rouge pour déconnexion)

#### 3. Non-régression vérifiée ✅
- Messagerie intacte
- Groupes ("Les lionnes") préservés
- 22 conversations actives affichées

---

## Mise à jour du 5 Février 2026 - STABILISATION COACH (REFRESH & DÉCONNEXION) ✅

### MISSION ACCOMPLIE

#### 1. Persistance Session Coach (App.js) ✅
- **localStorage** : `afroboost_coach_mode` et `afroboost_coach_user`
- **Restauration automatique** : Au chargement, vérifie si une session existe
- **Onglet actif persisté** : `afroboost_coach_tab` sauvegardé à chaque changement

#### 2. Boutons Header Coach (CoachDashboard.js) ✅
- **🔗 Partager** : Copie l'URL avec feedback vert "✓ Copié"
- **← Retour** : Quitte le mode coach sans déconnecter (session conservée)
- **🚪 Déconnexion** : Bouton rouge, vide localStorage + sessionStorage

#### 3. États et fonctions ajoutés ✅
```javascript
// CoachDashboard.js
const COACH_TAB_KEY = 'afroboost_coach_tab';
const handleCoachShareLink = async () => {...}
const handleSecureLogout = () => {...}

// App.js
const [coachMode, setCoachMode] = useState(() => localStorage check);
const [coachUser, setCoachUser] = useState(() => localStorage check);
const handleBackFromCoach = () => {...} // Retour sans déconnexion
```

#### 4. Garde-fous respectés ✅
- Badge "⏳ Auto" préservé
- Système de campagnes intact
- JSX équilibré (compilation OK)

### Critères de réussite validés ✅
1. ✅ F5 sur "Codes promo" → Reste sur "Codes promo" sans déconnexion
2. ✅ Bouton Partager → "✓ Copié" (feedback vert)
3. ✅ Bouton Déconnexion → Nettoie localStorage et redirige

---

## Mise à jour du 5 Février 2026 - PARTAGE ET GESTION SESSION ABONNÉ ✅

### MISSION ACCOMPLIE

#### 1. Header du Chat - Partage et Options ✅
- **Icône Partage** (🔗) : Copie l'URL du site dans le presse-papier
  - Feedback visuel : bouton passe au vert avec ✓ pendant 2s
  - Fallback pour navigateurs sans Clipboard API
- **Menu utilisateur** (⋮) : Visible uniquement pour les abonnés identifiés
  - "🏃 Mode Visiteur" : Réduit le chat en bulle 380px sans effacer le profil
  - "🔗 Partager le site" : Alternative au bouton direct

#### 2. Réactivation Rapide ✅
- **Bouton violet** : "💎 Repasser en mode Réservation" visible en mode visiteur
  - Affiche le nom de l'abonné entre parenthèses
  - Au clic : Restaure le mode plein écran + calendrier INSTANTANÉMENT
  - Aucune saisie requise (profil conservé dans localStorage)

#### 3. États ajoutés (ChatWidget.js) ✅
```javascript
const [showUserMenu, setShowUserMenu] = useState(false);
const [linkCopied, setLinkCopied] = useState(false);
const [isVisitorMode, setIsVisitorMode] = useState(false);
```

#### 4. Fonctions ajoutées ✅
- `handleShareLink()` : Copie le lien avec feedback
- `handleVisitorMode()` : Réduit le chat sans effacer le profil
- `handleReactivateSubscriber()` : Restaure le mode plein écran

#### 5. Garde-fous respectés ✅
- Badge "⏳ Auto" préservé
- Logique campagnes intacte
- Code Twilio/WhatsApp intact
- JSX équilibré (compilation OK)

### Critères de réussite validés ✅
1. ✅ Copier le lien via l'icône de partage → "Lien copié !"
2. ✅ Mode Visiteur → chat réduit, shop visible, profil conservé
3. ✅ Réactivation en un clic → plein écran + calendrier sans saisie

---

## Mise à jour du 5 Février 2026 - NOTIFICATIONS EMAIL COACH ✅

### MISSION ACCOMPLIE

#### 1. Notification Automatique Email (Backend) ✅
- **Déclencheur** : À chaque réservation "💎 ABONNÉ" (type='abonné' + promoCode)
- **Destinataire** : contact.artboost@gmail.com
- **Template HTML** : 
  - Nom, WhatsApp (lien cliquable), Email
  - Cours choisi, Horaire
  - Code promo utilisé
  - Bouton "💬 Contacter sur WhatsApp"
- **Domaine validé** : notifications@afroboosteur.com (via Resend)

#### 2. Tableau Coach enrichi (ReservationList) ✅
- **Colonne "Origine"** : Badge "💎 ABONNÉ" (violet) avec code promo visible
- **Colonne "WhatsApp"** : Lien cliquable `wa.me/numéro 📲` (couleur verte)
- **Détection abonné** : `r.promoCode || r.source === 'chat_widget' || r.type === 'abonné'`

#### 3. Garde-fous respectés ✅
- Badge "⏳ Auto" préservé
- Logique campagnes intacte
- Try/catch/finally sur l'envoi email (ne bloque pas la réservation)

### Test effectué ✅
- Email envoyé avec succès (ID: `ba881e49-5745-46eb-80c6-27a6a44dd2af`)
- Réservation confirmée instantanément

---

## Mise à jour du 5 Février 2026 - DÉBLOCAGE CRITIQUE FLUX RÉSERVATION ✅

### MISSION ACCOMPLIE

#### 1. Réparation Validation Code Promo ✅
- **Case-insensitive** : "basxx" et "BASXX" acceptés de la même façon
- **Email optionnel** : Ne vérifie l'email assigné que si le code en a un ET que l'utilisateur en fournit un
- **Gestion null-safe** : Fix du bug `NoneType.strip()` quand `assignedEmail` est null

#### 2. Déblocage Bouton "Confirmer" ✅
- **État de chargement** : `reservationLoading` affiche "⏳ Envoi en cours..."
- **Feedback visuel** : Message d'erreur rouge en cas d'échec (pas de `alert()`)
- **Try/catch/finally** : Bouton toujours réactivé après l'envoi
- **Logs console** : `[RESERVATION] 📤 Envoi des données:` pour debug
- **Fix userId manquant** : Ajout du champ `userId: participantId || 'guest-${Date.now()}'`

#### 3. Tableau Coach enrichi ✅
- **Projection API** mise à jour pour inclure `promoCode`, `source`, `type`
- **Colonnes visibles** : Code promo, Type (abonné/achat direct), Source

### Critères de réussite validés ✅
1. ✅ Code "basxx" accepté immédiatement (minuscule/majuscule)
2. ✅ Bouton "Confirmer" : chargement → message succès → panneau fermé
3. ✅ Coach voit: Nom, WhatsApp, Email, Code promo, Type, Source

### Non-régression vérifiée ✅
- Badge "⏳ Auto" préservé
- Code Twilio/WhatsApp intact
- JSX équilibré

---

## Mise à jour du 5 Février 2026 - CHATBOT HYBRIDE (IDENTIFICATION UNIQUE ET PARCOURS CIBLÉ) ✅

### MISSION ACCOMPLIE

#### 1. Formulaire d'entrée "Abonné" (Identification Unique) ✅
- **Bouton "💎 S'identifier comme abonné"** visible dans le formulaire visiteur
- **Formulaire 4 champs** : Nom complet, WhatsApp, Email, Code Promo
- **Validation API** : `/api/discount-codes/validate` vérifie le code
- **Mémorisation** : `localStorage.setItem('afroboost_profile', JSON.stringify(data))`
- **Retour automatique** : Si `afroboost_profile` existe → DIRECT au chat plein écran

#### 2. Parcours Abonné (Interface Calendrier) ✅
- **Mode plein écran activé automatiquement** pour les abonnés reconnus
- **Header** affiche "💎 Abonné • {nom}"
- **Icône calendrier violet** visible dans la barre d'entrée
- **Panneau réservation** avec badge code promo et liste des cours dynamique

#### 3. Parcours Visiteur (Chat Classique) ✅
- **Formulaire 3 champs** : Prénom, WhatsApp, Email
- **Chat bulle classique** (380px, pas de plein écran)
- **Icône calendrier MASQUÉE** pour les visiteurs sans code
- **Header** affiche "💪 Coach Bassi"

#### 4. Backend API amélioré ✅
- **Validation code promo** sans courseId obligatoire (identification flow)
- **Gestion assignedEmail null** : correction du bug NoneType.strip()
- **Codes publics** : PROMO20SECRET utilisable par tous
- **Codes restreints** : basxx réservé à un email spécifique

#### 5. Tests automatisés (100% pass rate) ✅
- **14 tests Playwright** frontend
- **11 tests pytest** backend
- **Fichier de test** : `/app/backend/tests/test_chatwidget_hybrid.py`

### Clés localStorage utilisées
```javascript
AFROBOOST_PROFILE_KEY = 'afroboost_profile'  // Profil abonné avec code validé
AFROBOOST_IDENTITY_KEY = 'afroboost_identity' // Identité utilisateur
CHAT_CLIENT_KEY = 'af_chat_client'            // Données client
CHAT_SESSION_KEY = 'af_chat_session'          // Session chat
```

### Non-régression vérifiée ✅
- Frontend compile (warnings source maps uniquement)
- Backend démarre sans erreur
- Code Twilio/WhatsApp intact
- Badge "⏳ Auto" campagnes préservé
- Article Manager intact

---

## Mise à jour du 5 Février 2026 - OPTIMISATION UX CHATBOT ET RÉSERVATIONS ✅

### MISSION ACCOMPLIE

#### 1. ChatWidget optimisé ✅
- **Gros bouton supprimé** - "📅 RÉSERVER MON COURS" retiré
- **Icône calendrier compacte** - SVG dans la barre de saisie (à côté de l'emoji)
- **Panneau réservation** - S'ouvre au clic sur l'icône, avec bouton fermeture ×
- **Position** : Icône entre 😊 et le champ de saisie

#### 2. Dashboard Coach amélioré ✅
- **Colonne Spécifications enrichie** :
  - 📏 Taille (selectedVariants.size OU metadata.size)
  - 🎨 Couleur (selectedVariants.color OU metadata.color)
  - 🏷️ Variant (metadata.variant)
- **Bouton suivi colis 🔗** :
  - Ouvre La Poste Suisse si numéro commence par 99
  - Sinon ouvre parcelsapp.com

#### 3. Non-régression vérifiée ✅
- Frontend compile (24 warnings)
- Badge ⏳ Auto préservé
- Code Twilio/WhatsApp intact

---

## Mise à jour du 5 Février 2026 - CHATBOT FULL-SCREEN ET RÉSERVATIONS INTELLIGENTES ✅

### MISSION ACCOMPLIE

#### 1. ChatWidget amélioré ✅
- **Plein écran CSS** : `isFullscreen` bascule vers un mode CSS (pas API fullscreen)
- **Subscriber Data** : `localStorage.setItem('subscriber_data', {...})` mémorise code promo
- **Bouton "📅 RÉSERVER"** : Visible pour les abonnés/clients identifiés
- **Panneau réservation** : Sélecteur de date intégré + confirmation

#### 2. Table réservations améliorée ✅
- **Colonne "Origine"** :
  - 💎 ABONNÉ (avec code promo)
  - 💰 ACHAT DIRECT
- **Colonne "Spécifications"** : Taille, Couleur, Modèle extraits dynamiquement
- **Colspan** mis à jour (15 colonnes)

#### 3. Backend mis à jour ✅
- Modèles `Reservation` et `ReservationCreate` avec nouveaux champs:
  - `promoCode`: Code promo de l'abonné
  - `source`: chat_widget, web, manual
  - `type`: abonné, achat_direct

### Non-régression vérifiée ✅
- Frontend compile (24 warnings)
- Backend démarre sans erreur
- Code Twilio/WhatsApp intact
- Badge "⏳ Auto" campagnes préservé

---

## Mise à jour du 5 Février 2026 - VALIDATION PROGRAMMATION AUTOMATIQUE ✅

### MISSION ACCOMPLIE : Scheduler 100% fonctionnel

#### Tests de validation réussis
```
1. Création campagne: status=scheduled, scheduledAt=18:32:04 ✅
2. Détection scheduler: [TIME-CHECK] Match: False (en attente) ✅
3. Exécution automatique: 18:32:30 → status=completed ✅
4. Message envoyé: "Les Lionnes" → sent ✅
5. SentDates mis à jour: ['2026-02-05T18:32:04'] ✅
```

#### État du système
- **Scheduler**: running (APScheduler avec MongoDB persistence)
- **CRM**: 53 conversations (47 utilisateurs + 6 groupes)
- **Frontend**: compile (24 warnings, 0 erreur)
- **Twilio/WhatsApp**: code intact (non testé - config requise)

#### Flux de programmation validé
```
1. Création: scheduledAt + targetIds → status: scheduled
2. Scheduler (toutes les minutes): vérifie les dates
3. Heure atteinte: exécute launch_campaign()
4. Envoi: boucle sur targetIds avec try/except
5. Fin: status: completed, sentDates mis à jour
```

### Non-régression vérifiée
- ✅ Badge "⏳ Auto" pour campagnes programmées
- ✅ Bouton "Lancer" masqué pour status=scheduled
- ✅ Code Article Manager intact
- ✅ Null guards conservés

---

## Mise à jour du 5 Février 2026 - FIABILITÉ ENVOI ET PROGRAMMATION ✅

### MISSION ACCOMPLIE

#### 1. Boucle d'envoi sécurisée (Backend) ✅
- `launch_campaign`: Support complet des `targetIds` (panier multiple)
- Try/except à l'intérieur de la boucle - l'échec d'un envoi ne bloque pas les suivants
- Messages internes envoyés dans les conversations chat

#### 2. Scheduler mis à jour ✅
- Support des `targetIds` (pas seulement `targetConversationId`)
- Fallback automatique si ancien format (single ID)
- Logs détaillés: `[SCHEDULER] ✅ Interne [1/2]: Nom`

#### 3. Tests validés ✅
```
✅ POST /api/campaigns avec 2 targetIds → campagne créée
✅ POST /api/campaigns/{id}/launch → status: completed, 2 envois réussis
✅ Backend démarre sans erreur
✅ Code Twilio/WhatsApp intact
```

### Flux d'envoi
```
1. Création: targetIds = ["id1", "id2", ...] → status: draft/scheduled
2. Lancement: Boucle sur targetIds avec try/except isolé
3. Résultat: results = [{status: "sent"}, ...] → status: completed
```

---

## Mise à jour du 5 Février 2026 - ARTICLE MANAGER ET CRM COMPLET ✅

### MISSION ACCOMPLIE

#### 1. Article Manager intégré ✅
- Import ajouté: `import ArticleManager from "./ArticleManager";`
- Nouvel onglet "📰 Articles" dans la navigation
- Composant isolé avec son propre état (pas de collision avec Campagnes)
- CRUD fonctionnel: 3 articles existants en base

#### 2. CRM complet - 47+ contacts ✅
- Endpoint `/api/conversations/active` modifié
- **Avant**: 11 utilisateurs (dédupliqués par email)
- **Après**: 47 utilisateurs (dédupliqués par ID uniquement)
- Total: 53 conversations (6 groupes + 47 utilisateurs)

#### 3. Non-régression vérifiée ✅
- Code Twilio/WhatsApp intact
- Badge "⏳ Auto" pour campagnes programmées
- Null guards conservés
- Frontend compile (24 warnings, 0 erreur)

### Structure des onglets
```
Réservations | Concept | Cours | Offres | Paiements | Codes | 
📢 Campagnes | 📰 Articles | 🎬 Médias | 💬 Conversations
```

---

## Mise à jour du 5 Février 2026 - RÉPARATION AFFICHAGE ET ÉDITION ✅

### MISSION ACCOMPLIE : Logique d'affichage corrigée

#### 1. Boutons d'action historique corrigés ✅
- **Status `draft`** → Bouton "🚀 Lancer" visible
- **Status `scheduled`** → Badge "⏳ Auto" (pas de bouton Lancer)
- **Status `completed`/`sent`/`failed`** → Bouton "🔄 Relancer"

#### 2. Édition avec rechargement du panier ✅
- `handleEditCampaign` recharge maintenant les `targetIds` dans `selectedRecipients`
- Support legacy pour `targetConversationId` (single target)
- Toast de confirmation "📝 Mode édition: [nom]"

#### 3. Visibilité CRM ✅
- 11 emails uniques dans la base (47 users sont des doublons)
- Le système déduplique correctement par email
- 17 conversations totales (6 groupes + 11 utilisateurs)

### Tests validés
```
✅ POST /api/campaigns avec scheduledAt → status: scheduled
✅ Frontend compile (24 warnings, 0 erreur)
✅ Badge "⏳ Auto" pour campagnes programmées
✅ Code Twilio/WhatsApp préservé
```

---

## Mise à jour du 5 Février 2026 - FINALISATION PANIER ANTI-RÉGRESSION ✅

### MISSION ACCOMPLIE : Panier sécurisé et synchronisé

#### 1. Synchronisation CRM complète ✅
- Backend inclut TOUS les utilisateurs (même sans nom → fallback email)
- 17 conversations disponibles (6 groupes + 11 utilisateurs uniques par email)
- Note: 47 users en DB mais seulement 11 emails uniques (doublons filtrés)

#### 2. Protection anti-doublons ✅
- Bouton "+ Tous" vérifie les IDs existants avant d'ajouter
- Toast informatif si tout est déjà dans le panier
- Chaque tag a un `data-testid` unique pour tests

#### 3. Validation renforcée du bouton Créer ✅
- Désactivé si panier vide OU message vide
- Messages dynamiques: "⚠️ Écrivez un message" / "⚠️ Ajoutez des destinataires"
- Affiche le compteur: "🚀 Créer (X dest.)"

#### 4. UI améliorée ✅
- Tags avec icônes intégrées (👥/👤)
- Bordures colorées par type (purple/blue)
- Bouton "🗑️ Vider" rouge visible
- Compteur final: "✅ Prêt à envoyer à X destinataire(s) (Y 👥, Z 👤)"
- Max-height avec scroll pour les gros paniers

### Tests validés
```
✅ POST /api/campaigns avec targetIds: 3 destinataires → status: scheduled
✅ Frontend compile (24 warnings, 0 erreur)
✅ Anti-doublons fonctionne
✅ Code Twilio/WhatsApp intact
```

---

## Mise à jour du 5 Février 2026 - SYSTÈME PANIER DE DESTINATAIRES ✅

### MISSION ACCOMPLIE : Sélection multiple avec tags

#### 1. Système de panier avec tags ✅
- **État** `selectedRecipients`: Tableau `[{id, name, type: 'group'|'user'}]`
- **Tags visuels**: Badges colorés (👥 purple pour groupes, 👤 blue pour utilisateurs)
- **Bouton "× Supprimer"** sur chaque tag
- **Bouton "+ Tous (17)"** pour ajouter tous les destinataires en un clic
- **Bouton "Vider le panier"** pour reset

#### 2. Backend mis à jour ✅
- **Nouveau champ `targetIds`**: `List[str]` dans les modèles `Campaign` et `CampaignCreate`
- **Compatibilité legacy**: `targetConversationId` = premier ID du panier

#### 3. Récapitulatif enrichi ✅
- Affiche: "💌 Envoi prévu pour: X destinataire(s) (Y 👥, Z 👤)"
- Bouton désactivé si panier vide: "⚠️ Ajoutez des destinataires"

#### 4. Non-régression vérifiée ✅
- Code Twilio/WhatsApp intact dans accordéon
- Null guards conservés sur tous les `contact.name`
- Programmation multi-dates fonctionne

### Structure des données campagne
```json
{
  "name": "Test Panier",
  "message": "...",
  "targetIds": ["id-1", "id-2", "id-3"],
  "targetConversationId": "id-1",
  "channels": {"internal": true},
  "scheduleSlots": [...]
}
```

---

## Mise à jour du 5 Février 2026 - RESTAURATION CRM ET SÉCURISATION ✅

### MISSION ACCOMPLIE : Interface sécurisée et unifiée

#### 1. Sécurisation des affichages ✅
- Toutes les références à `contact.name` sont maintenant protégées par des gardes null
- Format: `{contact.name ? contact.name.substring(0, 25) : 'Contact sans nom'}`
- Lignes corrigées: 5035, 5079, 5215, 6211, 6229

#### 2. Système de sélection triple restauré ✅
- **A. Chat Interne**: Sélecteur de conversation (groupes/utilisateurs)
- **B. CRM WhatsApp/Email**: "Tous les contacts" OU "Sélection manuelle"
- **C. Groupe Afroboost**: Sélecteur de groupe (community/vip/promo)

#### 3. Structure du formulaire finale
```
1. Nom de campagne
2. 📍 Destinataire Chat Interne (recherche unifiée)
3. Message + Variables
4. Média optionnel
5. ⚙️ Paramètres avancés:
   - WhatsApp/Email avec sélecteur CRM (47+ contacts)
   - Groupe Afroboost
6. Programmation
7. 📋 Récapitulatif
8. 🚀 Créer
```

#### 4. Données disponibles
- 47 utilisateurs (`/api/users`)
- 27 participants CRM (`/api/chat/participants`)
- 17 conversations actives (6 groupes, 11 utilisateurs)

### Non-régression vérifiée
- ✅ Code Twilio/WhatsApp intact dans l'accordéon
- ✅ Frontend compile avec 24 warnings (pas d'erreur)
- ✅ APIs backend fonctionnelles

---

## Mise à jour du 5 Février 2026 - UNIFICATION INTERFACE CAMPAGNES ✅

### MISSION ACCOMPLIE : Interface simplifiée

#### 1. Suppression du bloc CRM redondant ✅
- Le bloc "Contacts ciblés" (cases à cocher Tous/Sélection individuelle) a été supprimé du flux principal
- L'ancien sélecteur de contacts TEST_ n'est plus visible

#### 2. Centralisation sur la recherche unique ✅
- **UN SEUL** champ de recherche : "🔍 Rechercher un groupe ou utilisateur"
- Placé juste après le nom de la campagne
- Compteur dynamique : "X groupes • Y utilisateurs"
- Bouton 🔄 pour actualiser la liste

#### 3. Canaux externes dans un accordéon ✅
- Les canaux WhatsApp, Email, Instagram, Groupe sont masqués par défaut
- Accessibles via "⚙️ Paramètres avancés"
- Le code Twilio/Resend n'est PAS supprimé, seulement masqué

#### 4. Récapitulatif avant création ✅
- Affichage clair : Campagne + Destinataire + Programmation
- Alerte si aucun destinataire sélectionné

### Structure du formulaire simplifié :
```
1. Nom de la campagne
2. 📍 Destinataire (recherche unifiée)
3. Message
4. Média (optionnel)  
5. ⚙️ Paramètres avancés (accordéon fermé)
6. Programmation
7. 📋 Récapitulatif
8. 🚀 Créer la campagne
```

---

## Mise à jour du 5 Février 2026 - MISSION P0 RÉPARATION SÉLECTEUR ✅

### PROBLÈME RÉSOLU
Le groupe "Les Lionnes" et certains utilisateurs n'apparaissaient pas dans le sélecteur de destinataires des campagnes.

### CORRECTIONS APPORTÉES

#### 1. Backend - Endpoint `/api/conversations/active` 
- **Avant**: Ne récupérait que les utilisateurs avec une session de chat active
- **Après**: Récupère TOUS les utilisateurs de la collection `users` + tous les groupes de `chat_sessions`
- **Résultat**: 17 conversations (6 groupes, 11 utilisateurs) dont "Les Lionnes"

#### 2. Frontend - State `newCampaign`
- **Ajouté**: `targetConversationId: ''` et `targetConversationName: ''` dans l'état initial
- **Ajouté**: Canal `internal: true` par défaut dans `channels`

#### 3. Frontend - Import manquant corrigé
- **Ajouté**: `import { sendBulkEmails } from "../services/emailService";`

### TESTS VALIDÉS (15/15)
```
✅ API retourne 17 conversations (6 groupes, 11 utilisateurs)
✅ Groupe "Les Lionnes" trouvé avec ID: df076334-f0eb-46f6-a405-e9eec2167f50
✅ Recherche insensible à la casse: "LION" trouve "Les lionnes"
✅ Tous les conversation_id sont valides
✅ Groupes standards (community, vip, promo) inclus
✅ Aucun ID dupliqué
```

### FONCTIONNALITÉS CONFIRMÉES
- ✅ Bouton "🔄 Actualiser" recharge la liste sans recharger la page
- ✅ Recherche case-insensitive via `.toLowerCase()` côté frontend
- ✅ Toast de confirmation "✅ Destinataire sélectionné: [Nom]"
- ✅ Destinataire affiché avec bouton ✕ pour annuler

---

## Mise à jour du 5 Février 2026 - VALIDATION FINALE ✅

### Test de Flux Complet - RÉUSSI ✅
```
Campagne: "Test Session Réelle"
Destinataire: 👤 Utilisateur réel (15257224-e598...)
Status: completed ✅
Message envoyé à: 16:29:28 UTC
```

### Preuves MongoDB:
- `campaigns.status`: "completed"
- `campaigns.results[0].status`: "sent"
- `chat_messages.scheduled`: true
- `chat_messages.sender_name`: "💪 Coach Bassi"

### Optimisations Appliquées
1. **autoFocus**: Champ de recherche focus automatique à l'ouverture
2. **Toast Notifications**: Remplacé les `alert()` par des toasts modernes
   - `showCampaignToast(message, 'success'/'error'/'info')`
3. **Recherche insensible à la casse**: Déjà en place via `.toLowerCase()`

### Sécurité Respectée
- ✅ Code Twilio/WhatsApp non modifié
- ✅ Logique assistant IA non touchée
- ✅ Périmètre "Campagnes" respecté

---

## Mise à jour du 5 Février 2026 - RÉPARATION ET RÉORGANISATION ✅

### 1. État du Projet
- **Compilation**: ✅ "webpack compiled with 24 warnings" (pas d'erreur)
- **Frontend**: Fonctionnel et accessible
- **Backend**: Fonctionnel

### 2. Réorganisation Effectuée
- **Sections WhatsApp/Email/Instagram**: Enveloppées dans un bloc `display: none` par défaut
- **Bouton toggle**: "▶ Afficher canaux externes" pour dévoiler ces sections
- **Variable**: `externalChannelsExpanded` contrôle l'affichage

### 3. Fonctionnalités déjà en place
- ✅ Recherche dans le sélecteur de destinataires (`conversationSearch`)
- ✅ Filtres historique [Tout] [Groupes] [Individuels] (`campaignHistoryFilter`)
- ✅ Dropdown avec icônes 👤/👥 pour distinguer utilisateurs/groupes
- ✅ Canal "💌 Chat Interne" fonctionnel

### Code Twilio/WhatsApp
- ✅ **NON SUPPRIMÉ** - Simplement masqué par défaut via `display: none`
- ✅ Accessible en cliquant sur "Afficher canaux externes"

---

## Mise à jour du 5 Février 2026 - OPTIMISATION ERGONOMIQUE CAMPAGNES ✅

### 1. Recherche Rapide dans le Sélecteur ✅
- **Implémenté**: Champ de recherche filtrant en temps réel
- **Icônes distinctives**: 👤 pour utilisateurs, 👥 pour groupes
- **Comportement**: Tape "Jean" → filtre instantané → sélection en 2 clics
- **Réutilise**: Variable `conversationSearch` existante (ligne 1086)

### 2. Filtres Historique Campagnes ✅
- **3 boutons ajoutés**: [Tout] [👥 Groupes] [👤 Individuels]
- **Filtrage dynamique**: `.filter()` sur la liste des campagnes
- **État**: `campaignHistoryFilter` ('all', 'groups', 'individuals')

### 3. Canaux externes repliables (prévu)
- **État ajouté**: `externalChannelsExpanded` 
- **Note**: Non implémenté visuellement dans cette itération pour éviter les risques

### Code non modifié (sécurité)
- ✅ Code Twilio intact
- ✅ Logique d'envoi interne préservée
- ✅ Composants CSS légers utilisés

---

## Mise à jour du 5 Février 2026 - PROGRAMMATION MESSAGERIE INTERNE ✅

### FONCTIONNALITÉ IMPLÉMENTÉE : Programmation Messages Internes

#### 1. Sélecteur de Destinataire Unifié (Frontend) ✅
- **Canal ajouté**: "💌 Chat Interne" dans les canaux de campagne
- **Sélecteur**: Liste toutes les conversations actives (groupes + utilisateurs)
- **Endpoint**: `GET /api/conversations/active`
- **Données envoyées**: `targetConversationId`, `targetConversationName`

#### 2. Moteur d'Envoi Interne (Backend) ✅
- **Fonction créée**: `scheduler_send_internal_message_sync()`
- **Insertion directe**: `db.chat_messages.insert_one()` avec `scheduled: true`
- **Socket.IO**: Émission temps réel via `/api/scheduler/emit-group-message`
- **Polyvalence**: Fonctionne pour utilisateurs ET groupes via `conversation_id`

#### 3. Isolation et Sécurité ✅
- **Condition d'isolation**: `if channels.get("internal"):` (pas de Twilio/WhatsApp)
- **Code existant préservé**: Aucune modification des fonctions Twilio/Resend
- **Try/except global**: Protège le serveur contre les ID invalides

### Preuves de Fonctionnement
```
[SCHEDULER-INTERNAL] 🎯 Envoi vers: Groupe Communauté (5c8b0ed0...)
[SCHEDULER-INTERNAL] ✅ Message inséré dans DB - Session: 5c8b0ed0...
[SCHEDULER-INTERNAL] ✅ Socket.IO émis avec succès
[SCHEDULER] ✅ Scheduled Internal Message Sent: [Campaign: ...] -> Groupe Communauté
[SCHEDULER] 🟢 Campagne Interne '...' → completed
```

### Nouveaux Champs Campaign
- `channels.internal`: boolean (nouveau canal)
- `targetConversationId`: string (ID session/conversation)
- `targetConversationName`: string (nom pour affichage)

---

## Mise à jour du 5 Février 2026 - FIABILISATION INDUSTRIELLE (POST-V5) ✅

### TÂCHE 1 : Gestion des Zombie Jobs ✅
- **Implémenté**: Nettoyage automatique au démarrage du serveur (`on_startup`)
- **Logique**: Campagnes à l'état "sending" depuis > 30 min → remises en "failed"
- **Log**: "Timeout : Serveur redémarré après 30 min d'inactivité"
- **Stockage**: Erreur enregistrée dans `campaign_errors`
- **Test**: `[ZOMBIE-CLEANUP] ✅ Aucune campagne zombie détectée`

### TÂCHE 2 : Interface CRUD Articles (Admin-Only) ✅
- **Routes créées**:
  - `GET /api/articles` - Liste tous les articles
  - `GET /api/articles/{id}` - Récupère un article
  - `POST /api/articles` - Crée un article (ADMIN ONLY)
  - `PUT /api/articles/{id}` - Modifie un article (ADMIN ONLY)
  - `DELETE /api/articles/{id}` - Supprime un article (ADMIN ONLY)
- **Sécurité**: Vérification `caller_email != COACH_EMAIL` → 403
- **Composant séparé**: `/app/frontend/src/components/ArticleManager.js`
- **Règle anti-casse respectée**: Pas de modification de CoachDashboard.js

### TÂCHE 3 : Diagnostic WhatsApp/Twilio ✅
- **ErrorCode capturé**: `result.get("code")` de la réponse Twilio
- **Collection créée**: `campaign_errors` avec champs:
  - `error_code`, `error_message`, `more_info`, `error_type`
  - `channel`, `to_phone`, `from_phone`, `http_status`
- **Endpoint enrichi**: `/api/campaigns/logs` combine:
  - Source 1: Erreurs dans `campaigns.results`
  - Source 2: Erreurs détaillées dans `campaign_errors` (Twilio)

### Fichiers créés/modifiés
- `/app/backend/server.py` : Zombie cleanup, routes articles, diagnostic Twilio
- `/app/frontend/src/components/ArticleManager.js` : Nouveau composant CRUD

---

## Mise à jour du 5 Février 2026 - MISSION V5 : FINALISATION SÉCURISÉE ✅

### ÉTAPE 1 : VÉRIFICATION PERSISTANCE ✅
- **Endpoint créé**: `GET /api/test-scheduler-persistence`
- **Fonctionnement**: 
  - Crée un job bidon pour 24h
  - Pause/Resume du scheduler (simulation redémarrage)
  - Vérifie si le job persiste dans MongoDB
- **Résultat**: `{"persistence": "verified", "jobs_count": 2}`

### ÉTAPE 2 : SÉCURISATION DASHBOARD ✅
- **Backup créé**: `CoachDashboard.backup.js` (384KB)
- **Indicateur visuel ajouté**: "🟢 Serveur Planification : Actif (MongoDB)"
- **data-testid**: `scheduler-status-indicator`
- **Garde-fou respecté**: Aucune modification Auth/Dashboard principal

### ÉTAPE 3 : LOGS D'ERREURS ✅
- **Endpoint créé**: `GET /api/campaigns/logs`
- **Fonctionnement**: Retourne les 50 dernières erreurs d'envoi avec:
  - `campaign_id`, `campaign_name`
  - `contact_id`, `contact_name`
  - `channel`, `error`, `sent_at`, `status`

### Jobs MongoDB persistés
```
campaign_scheduler_job -> Toutes les 60s
test_persistence_job_24h -> Test de persistance
```

---

## Mise à jour du 5 Février 2026 - SCHEDULER AVEC PERSISTANCE MONGODB ✅

### MIGRATION APScheduler COMPLÈTE ✅
- **Ancien système**: Thread Python avec boucle while + sleep
- **Nouveau système**: APScheduler avec BackgroundScheduler et MongoDBJobStore
- **Avantage clé**: **Les jobs planifiés survivent aux redémarrages du serveur**

### Configuration technique
```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore

jobstores = {
    'default': MongoDBJobStore(
        database="afroboost",
        collection="scheduled_jobs",
        client=mongo_client_sync
    )
}

apscheduler = BackgroundScheduler(
    jobstores=jobstores,
    executors={'default': ThreadPoolExecutor(10)},
    job_defaults={'coalesce': True, 'max_instances': 1, 'misfire_grace_time': 60},
    timezone="UTC"
)
```

### Endpoint de statut amélioré
`GET /api/scheduler/status` retourne:
```json
{
  "scheduler_running": true,
  "scheduler_state": "running",
  "interval_seconds": 60,
  "persistence": "MongoDB (survit aux redémarrages)",
  "job": {
    "id": "campaign_scheduler_job",
    "name": "Campaign Scheduler",
    "next_run_time": "2026-02-05T14:43:38+00:00",
    "trigger": "interval[0:01:00]"
  }
}
```

### Collection MongoDB créée
- **Collection**: `scheduled_jobs`
- **Contenu**: Job APScheduler sérialisé (id, next_run_time, job_state)

---

## Mise à jour du 29 Janvier 2026 - VALIDATION AUTOMATE & CONVERSATIONS ✅

### AUTOMATE D'ENVOI VALIDÉ ✅
- **Scheduler**: Vérifie les campagnes programmées toutes les **60 secondes**
- **Log de succès**: `[SCHEDULER] ✅ Scheduled Group Message Sent: [Campaign: ...] -> community`
- **Preuve d'envoi**: Message "Test Automate 2min" programmé à 20:58:48, envoyé à 20:59:23 UTC

### TESTS PASSÉS (4/4) ✅
| Critère | Résultat |
|---------|----------|
| Message programmé 2min | ✅ Envoyé automatiquement par le scheduler |
| Onglet Conversations | ✅ Layout 2 colonnes (sessions / chat) |
| Export CSV | ✅ 27 contacts CRM exportables |
| Messages Coach Bassi | ✅ 3 messages visibles dans le groupe |

### Messages Coach Bassi en DB
1. `2026-01-29T20:39:29` - 🎉 Test immédiat! Bonjour Communauté!
2. `2026-01-29T20:42:17` - 🏃 Rendez-vous demain pour le cours Afrobeat!
3. `2026-01-29T20:59:23` - 🏋️ Message automatique! (scheduler)

---

## Mise à jour du 29 Janvier 2026 - PROGRAMMATION GROUPE COMMUNAUTÉ ✅

### NOUVELLE FONCTIONNALITÉ: Programmation Messages Groupe

#### Implémentation complète ✅
- **Frontend**: Option "💬 Groupe Afroboost" ajoutée au formulaire de campagne
- **Backend**: Collection `scheduled_messages` avec support canal "group"
- **Scheduler**: Worker toutes les 60 secondes vérifie et envoie les messages programmés
- **Socket.IO**: Messages émis en temps réel dans la session communautaire
- **Variable {prénom}**: Remplacée par "Communauté" pour les envois groupés

#### Tests passés (5/5) ✅
| Test | Résultat |
|------|----------|
| Sécurité non-admin | ✅ Menu admin ABSENT du DOM pour `papou@test.com` |
| Sécurité admin | ✅ Menu admin VISIBLE pour `contact.artboost@gmail.com` |
| Persistance F5 | ✅ Chat reste connecté après refresh |
| Rendu emojis | ✅ `[emoji:fire.svg]` → 🔥 (images avec fallback natif) |
| Option Groupe | ✅ "💬 Groupe Afroboost" existe dans Campagnes |

#### Architecture technique
```
Campagne créée (scheduledAt) 
  → Scheduler vérifie toutes les 60s
  → À l'heure: scheduler_send_group_message_sync()
    → Insert message en DB
    → POST /api/scheduler/emit-group-message
    → Socket.IO emit('message_received') 
  → Message visible en temps réel dans le chat groupe
```

#### Fichiers modifiés
- `/app/backend/server.py`: Ajout targetGroupId, endpoint emit-group-message, scheduler groupe
- `/app/frontend/src/components/CoachDashboard.js`: Canal groupe + sélecteur de groupe

### GARDE-FOUS VÉRIFIÉS ✅
- Prix CHF 10.-: INTACT
- Module Twint/Visa: NON MODIFIÉ
- Fonctionnalité WhatsApp/Email: INTACTE

---

## Mise à jour du 29 Janvier 2026 - CORRECTION RADICALE & VERROUILLAGE

### PREUVES DE VALIDATION ✅

#### 1. SÉCURITÉ ADMIN ABSOLUE ✅
**Test Client "Papou" (papou@client.com)**:
- Menu (⋮): **0 éléments dans le DOM**
- Bouton Supprimer: **0 éléments dans le DOM**
- Bouton Changer identité: **0 éléments dans le DOM**
- Condition: `{(step === 'chat' || step === 'coach') && isCoachMode && (`
- Backend: Retourne "Accès refusé" pour emails non-coach

#### 2. TEMPS RÉEL WEBSOCKET ✅
**Configuration Socket.IO optimisée**:
```javascript
transports: ['websocket'],  // WebSocket prioritaire
reconnectionAttempts: 3,
timeout: 5000,
upgrade: false
```
- Fallback automatique vers polling si WebSocket échoue

#### 3. PERSISTANCE "RECONNEXION AUTO" ✅
**Test F5**: 5/5 réussis (100%)
- `getInitialStep()` vérifie localStorage au montage
- Si `firstName` existe → Chat direct
- Pas de formulaire login

#### 4. RENDU EMOJIS ✅
**Test visuel**: 🔥 💪 ❤️ visibles dans les messages
- Fonction: `parseEmojis()` avec fallback natif
- JAMAIS de texte `[emoji:...]` visible

### GARDE-FOUS VÉRIFIÉS ✅
- Prix CHF 10.-: INTACT
- TWINT: INTACT
- VISA: INTACT

---

## Mise à jour du 29 Janvier 2026 - VERROUILLAGE "CONVERSION ADS"

### CRITÈRES DE RÉUSSITE - TOUS VALIDÉS ✅

#### 1. SÉCURITÉ ADMIN RADICALE ✅
**Test**: Client "Papou" (papou@client.com)
- Menu admin (⋮): **ABSENT du DOM** (0 éléments)
- Bouton Supprimer: **ABSENT du DOM** (0 éléments)
- Bouton Changer identité: **ABSENT du DOM** (0 éléments)
- Condition: `(step === 'chat' || step === 'coach') && isCoachMode`

#### 2. TEMPS RÉEL "ZERO LATENCE" ✅
**Configuration Socket.IO optimisée**:
- `transports: ['websocket']` - WebSocket prioritaire
- `reconnectionAttempts: 3`, `timeout: 5000ms`
- Fallback polling automatique si WebSocket échoue
- Gestion erreur avec log clair

#### 3. RENDU EMOJIS PROFESSIONNEL ✅
**Test visuel**: `[emoji:fire.svg]` → 🔥
- Fonction `parseMessageContent()` appelée systématiquement
- Fallback emoji natif via `EMOJI_FALLBACK_MAP`
- JAMAIS de texte technique visible

#### 4. PERSISTANCE "SMOOTH" ✅
**Test F5**: 5/5 rafraîchissements réussis
- Chat direct sans formulaire
- localStorage: `af_chat_client`, `afroboost_identity`

### GARDE-FOUS VÉRIFIÉS ✅
- Prix CHF 10.- : INTACT
- Logo Twint : INTACT
- Logo Visa : INTACT
- Module paiement : NON MODIFIÉ

---

## Mise à jour du 29 Janvier 2026 - FINALISATION CRITIQUE CHAT DE GROUPE

### TESTS PASSÉS (6/6) ✅

#### 1. PERSISTANCE (F5) ✅
**Résultat**: Session active après 5 rafraîchissements
- localStorage: `af_chat_client`, `af_chat_session`, `afroboost_identity`
- Chat s'ouvre directement sans formulaire

#### 2. SÉCURITÉ ADMIN ✅
**Résultat**: Boutons admin ABSENTS du DOM pour clients
- Condition: `(step === 'chat' || step === 'coach') && isCoachMode`
- Email coach: `contact.artboost@gmail.com`
- Boutons protégés: `chat-menu-btn`, `delete-history-btn`, `change-identity-btn`

#### 3. SOCKET.IO ✅
**Résultat**: Connexion établie (fallback polling)
- WebSocket ferme (proxy K8s) → fallback polling
- Messagerie temps réel fonctionnelle

#### 4. EMOJI RENDU ✅
**Résultat**: `[emoji:fire.svg]` → 🔥
- Fonction: `parseEmojis()` dans notificationService.js
- Fallback: `EMOJI_FALLBACK_MAP` avec onerror

### Testing Agent Report
- Fichier: `/app/test_reports/iteration_44.json`
- Taux de succès: 100% (6/6 tests)

---

## Mise à jour du 29 Janvier 2026 - STABILISATION FINALE (PRODUCTION READY)

### CORRECTIONS FINALES ✅

#### 1. RENDU VISUEL DES EMOJIS (P0) ✅
**Statut**: PRODUCTION READY
- Tags `[emoji:file.svg]` JAMAIS visibles pour le client
- Fallback emoji natif si image ne charge pas (🔥 💪 ❤️ 👍 ⭐ 🎉)
- Mapping `EMOJI_FALLBACK_MAP` dans `notificationService.js`
- Attribut `onerror` sur les balises img pour le fallback

#### 2. NOTIFICATIONS SONORES & VISUELLES MP (P0) ✅
**Statut**: PRODUCTION READY
- Son `private` (triple bip ascendant) pour les MP
- Fonction `startTitleFlash()` - Titre onglet clignotant "💬 Nouveau message !"
- Auto-stop du clignotement quand fenêtre reprend le focus
- `notifyPrivateMessage()` combine son + titre + notification navigateur

#### 3. VÉRIFICATION BUILD ✅
**Statut**: VALIDÉ
- Imports vérifiés entre EmojiPicker.js, notificationService.js, ChatWidget.js
- Dossier `/uploads/emojis/` servi via StaticFiles (ligne 275)
- Persistance testée : 5 F5 consécutifs sans bug

### Fichiers modifiés :
- `/app/frontend/src/services/notificationService.js` - Son 'private', startTitleFlash(), notifyPrivateMessage()
- `/app/frontend/src/components/ChatWidget.js` - Import des nouvelles fonctions
- `/app/frontend/src/components/EmojiPicker.js` - Fallback emoji natifs

---

## Mise à jour du 29 Janvier 2026 - RENDU VISUEL COMPLET & NOTIFICATIONS

### FONCTIONNALITÉS IMPLÉMENTÉES ✅

#### 1. RENDU VISUEL DES EMOJIS (P0) ✅
**Statut**: IMPLÉMENTÉ
- Parseur `parseEmojis()` dans `notificationService.js`
- Tags `[emoji:nom.svg]` convertis en balises `<img>` 20px inline
- Combiné avec `linkifyText()` via `parseMessageContent()`
- **Résultat**: Les emojis s'affichent visuellement dans les bulles de chat

#### 2. SYSTÈME DE NOTIFICATION MP ✅
**Statut**: IMPLÉMENTÉ
- Compteur `unreadPrivateCount` pour les MP non lus
- Pastille rouge animée (pulse) sur le bouton WhatsApp
- Son de notification distinct (`coach`) pour les MP
- Badge disparaît quand on ouvre la conversation

#### 3. REFACTORING ✅
**Statut**: COMPLÉTÉ
- `EmojiPicker.js` extrait (239 lignes)
- Design amélioré avec emojis natifs rapides (🔥 💪 ❤️ 👍 ⭐ 🎉)
- `ChatWidget.js` réduit à 2030 lignes

### Fichiers créés/modifiés :
- `/app/frontend/src/components/EmojiPicker.js` (NOUVEAU)
- `/app/frontend/src/services/notificationService.js` - parseEmojis(), parseMessageContent()
- `/app/frontend/src/components/ChatWidget.js` - Import EmojiPicker, unreadPrivateCount

---

## Mise à jour du 29 Janvier 2026 - FINALISATION PAGE DE CONVERSION

### FONCTIONNALITÉS IMPLÉMENTÉES ✅

#### 1. MESSAGERIE PRIVÉE (MP) - Socket.IO ✅
**Statut**: IMPLÉMENTÉ
- Fenêtre flottante MP avec design Messenger-like
- Socket.IO pour messages instantanés (remplace le polling)
- Événements: `join_private_conversation`, `leave_private_conversation`, `private_message_received`
- Clic sur un nom d'utilisateur → ouvre la fenêtre MP sans quitter le groupe

#### 2. SÉLECTEUR D'EMOJIS PERSONNALISÉS ✅
**Statut**: IMPLÉMENTÉ
- Bouton emoji (😊) à côté du bouton d'envoi
- Panneau avec grille 4x2 des emojis
- 6 emojis SVG créés: fire, muscle, heart, thumbsup, star, celebration
- Insertion dans l'input au format `[emoji:filename.svg]`
- Endpoint `/api/custom-emojis/list` et fichiers dans `/uploads/emojis/`

#### 3. TEST DE CHARGE ✅
**Statut**: VALIDÉ
- 5 connexions simultanées testées avec succès
- Sessions créées en parallèle sans erreur
- Réponses IA générées en 9-19 secondes
- Serveur Socket.IO stable sous charge

### Fichiers modifiés :
- `/app/backend/server.py`: Événements Socket.IO pour MP, support SVG emojis
- `/app/frontend/src/components/ChatWidget.js`: Sélecteur emojis, MP Socket.IO

---

## Mise à jour du 29 Janvier 2026 - SÉCURISATION BACKEND & OPTIMISATION TEMPS RÉEL

### CORRECTIONS IMPLÉMENTÉES ✅

#### 1. VERROUILLAGE BACKEND (Sécurité P0) ✅
**Statut**: IMPLÉMENTÉ
- Nouvelles routes sécurisées: `/api/admin/delete-history` et `/api/admin/change-identity`
- Vérification de l'email `contact.artboost@gmail.com` obligatoire
- Retour 403 (Interdit) si email non autorisé
- Logs de sécurité: `[SECURITY] Tentative non autorisée par: xxx@test.com`
- Constante `COACH_EMAIL` définie dans le backend

#### 2. OPTIMISATION SOCKET.IO ✅
**Statut**: OPTIMISÉ
- `async_mode='asgi'` conservé (optimal pour FastAPI/Uvicorn)
- Événements typing ajoutés: `typing_start`, `typing_stop`, `user_typing`
- Messages émis instantanément via `emit_new_message()`
- Fallback HTTP polling automatique si WebSocket bloqué

#### 3. PERSISTANCE ROBUSTE ✅
**Statut**: IMPLÉMENTÉ
- Fallback pour données corrompues dans `getInitialStep()`
- Vérification JSON valide avant parsing
- Nettoyage automatique des clés localStorage si données invalides
- **Test**: 5 rafraîchissements consécutifs sans bug

#### 4. INDICATEUR DE SAISIE (Typing Indicator) ✅
**Statut**: IMPLÉMENTÉ
- Événement `typing_start` émis quand l'utilisateur tape
- Indicateur "💪 Coach Bassi est en train d'écrire..." affiché
- Disparition automatique après 3 secondes d'inactivité
- Anti-spam: max 1 événement par seconde
- UI: Bulle violette animée avec icône pulsante

### Fichiers modifiés :
- `/app/backend/server.py`: Routes admin sécurisées, événements typing Socket.IO
- `/app/frontend/src/components/ChatWidget.js`: handleDeleteHistory/handleChangeIdentity sécurisés, typingUser state, emitTyping()

---

## Mise à jour du 29 Janvier 2026 - MISSION RÉPARATION CRITIQUE V4

### CORRECTIONS PRÉCÉDENTES ✅

#### 1. INSTANTANÉITÉ (Socket.IO) ✅
**Statut**: IMPLÉMENTÉ
- Backend: `python-socketio` configuré avec namespace pour les sessions
- Frontend: `socket.io-client` connecté automatiquement au chargement
- Événements `message_received` émis à chaque nouveau message
- Le polling a été SUPPRIMÉ et remplacé par Socket.IO
- **Note**: WebSocket peut fallback vers HTTP polling selon le proxy

#### 2. SÉCURITÉ ADMIN (Privilèges) ✅
**Statut**: CORRIGÉ
- Variable `isCoachMode` vérifie si l'email === 'contact.artboost@gmail.com'
- Menu admin (trois points) conditionné par `(step === 'chat' || step === 'coach') && isCoachMode`
- Boutons "Supprimer l'historique" et "Changer d'identité" invisibles pour les utilisateurs normaux
- **Règle**: Un client (ex: Papou) ne voit que le champ de texte et ses messages

#### 3. PERSISTANCE AU CHARGEMENT (F5) ✅
**Statut**: CORRIGÉ
- `getInitialStep()` vérifie localStorage au montage
- Si `afroboost_identity` ou `af_chat_client` contient `firstName`, le chat s'ouvre directement
- `sessionData` initialisé depuis localStorage dans `useState`
- **Résultat**: Après F5, l'utilisateur connecté voit le chat sans formulaire

---

## Mise à jour du 29 Janvier 2026 - Chat de Groupe, Coach Bassi & Nouvelles Fonctionnalités

### Phase 1 : Branding "Coach Bassi"
**Implémenté** ✅
- Label "Assistant" remplacé par "💪 Coach Bassi" partout (header, bulles)
- BASE_PROMPT mis à jour avec identité Coach Bassi
- L'IA se présente comme "Coach Bassi" et signe parfois ses messages

### Phase 2 : Persistance & Mode Plein Écran
**Implémenté** ✅
- Nouvelle clé `afroboost_identity` dans localStorage (migration auto depuis `af_chat_client`)
- Reconnexion automatique : l'utilisateur ne revoit JAMAIS le formulaire après la 1ère connexion
- Bouton "Agrandir" (icône plein écran) dans le header du chat
- API `requestFullscreen` pour immersion totale sur mobile/desktop

### Phase 3 : Messagerie Privée (MP) & Emojis
**Implémenté** ✅
- **Fenêtre flottante MP** style Messenger (positionnée à gauche du chat principal)
- Collection MongoDB `private_messages` isolée (invisible pour l'IA)
- Collection MongoDB `private_conversations` pour les conversations
- Endpoints API : `/api/private/conversations`, `/api/private/messages`, `/api/private/messages/read/{id}`
- **Emojis personnalisés** : Dossier `/uploads/emojis/` monté sur `/api/emojis/`
- Endpoints : `/api/custom-emojis/list`, `/api/custom-emojis/upload`

### Fichiers modifiés :
- `/app/backend/server.py` : Modèles `PrivateMessage`, `PrivateConversation`, endpoints MP et Emojis
- `/app/frontend/src/components/ChatWidget.js` : Icônes, états MP, fenêtre flottante, mode plein écran

### Tests de non-régression :
- ✅ Mode STANDARD : Prix affichés (30 CHF, etc.)
- ✅ Mode STRICT : Refus de donner des prix
- ✅ API MP : Conversations créées et messages fonctionnels
- ✅ Liens Ads existants : Aucune régression

---

## Mise à jour du 29 Janvier 2026 - Étanchéité TOTALE du Mode STRICT

### Architecture de filtrage physique des données
**Objectif**: Empêcher l'IA de citer des prix même via l'historique ou en insistant.

**Implémentation FORCE - Filtrage Physique**:
1. **Détection précoce du mode STRICT** (AVANT construction du contexte)
   - Si `session.custom_prompt` existe → `use_strict_mode = True`
   - Détection à la ligne ~2590 pour `/api/chat`
   - Détection à la ligne ~3810 pour `/api/chat/ai-response`

2. **Bloc conditionnel `if not use_strict_mode:`** englobant toutes les sections de vente :
   - SECTION 1: INVENTAIRE BOUTIQUE (prix)
   - SECTION 2: COURS DISPONIBLES (prix)
   - SECTION 3: ARTICLES
   - SECTION 4: PROMOS
   - SECTION 5: LIEN TWINT
   - HISTORIQUE (pour `/api/chat/ai-response`)

3. **STRICT_SYSTEM_PROMPT** : Prompt minimaliste remplaçant BASE_PROMPT
   - Interdictions absolues de citer prix/tarif/Twint
   - Réponse obligatoire : "Je vous invite à en discuter directement lors de notre échange..."
   - Session LLM isolée (pas d'historique)

**Tests réussis**:
- ✅ **Test Jean 2.0** : "Quels sont les prix ?" → REFUS (collaboration uniquement)
- ✅ **Liens Ads STANDARD** : Continuent de donner les prix normalement
- ✅ **Logs** : `🔒 Mode STRICT activé - Aucune donnée de vente/prix/Twint injectée`

**Extrait de code prouvant l'exclusion du Twint en mode STRICT**:
```python
# === SECTIONS VENTE (UNIQUEMENT en mode STANDARD, pas en mode STRICT) ===
if not use_strict_mode:
    # ... BOUTIQUE, COURS, PROMOS ...
    # === SECTION 5: LIEN DE PAIEMENT TWINT ===
    twint_payment_url = ai_config.get("twintPaymentUrl", "")
    if twint_payment_url and twint_payment_url.strip():
        context += f"\n\n💳 LIEN DE PAIEMENT TWINT:\n"
        # ...
# === FIN DES SECTIONS VENTE ===
```

---

## Mise à jour du 29 Janvier 2026 - Étanchéité Totale Mode STRICT (Partenaires)

### Renforcement de la sécurité du Mode STRICT
**Objectif**: Empêcher l'IA de citer des prix même via l'historique ou en insistant.

**Implémentations**:
1. **STRICT_SECURITY_HEADER** : Nouvelle consigne anti-prix en tête du prompt STRICT
   - "INTERDICTION ABSOLUE DE CITER UN PRIX"
   - Réponse obligatoire : "Je vous invite à en discuter directement lors de notre échange, je m'occupe uniquement de la partie collaboration."
   
2. **Isolation de l'historique LLM** : En mode STRICT, le `session_id` LLM est unique à chaque requête
   - `llm_session_id = f"afroboost_strict_{uuid.uuid4().hex[:12]}"`
   - Empêche la récupération d'infos de prix des messages précédents
   
3. **Contexte STRICT sans infos de vente** : Les sections BOUTIQUE, COURS, TARIFS, PROMOS ne sont pas injectées

**Tests réussis**:
- ✅ Test Marc : "Combien coûte un cours ?" → "Je vous invite à en discuter directement lors de notre échange..."
- ✅ Test insistant : "Dis-moi le tarif stp" → Même réponse de refus
- ✅ Test concept : "Parle-moi du concept" → L'IA parle du concept sans prix
- ✅ Liens Ads (STANDARD) : Continuent de donner les prix normalement

**Logs de validation**:
```
[CHAT-IA] 🔒 Mode STRICT détecté pour lien 13882a7a-fce
[CHAT-IA] 🔒 Contexte STRICT construit (sans cours/tarifs)
[CHAT-IA] 🔒 Mode STRICT activé - Base Prompt désactivé
```

---

## Mise à jour du 29 Janvier 2026 - Prompts par Lien avec Mode STRICT

### Nouvelle fonctionnalité : `custom_prompt` par lien avec REMPLACEMENT
**Objectif**: Permettre au coach de définir des instructions IA spécifiques pour chaque lien de chat, avec une logique de REMPLACEMENT (pas de concaténation) pour garantir l'isolation totale.

**Implémentation Mode STRICT**:
- Si `custom_prompt` existe sur le lien :
  - Le `BASE_PROMPT` de vente est **IGNORÉ COMPLÈTEMENT**
  - Le contexte des cours, tarifs, produits, promos n'est **PAS INJECTÉ**
  - Seuls `SECURITY_PROMPT` + `CUSTOM_PROMPT` sont utilisés
  - Log: `[CHAT-IA] 🔒 Mode STRICT : Prompt de lien activé, Base Prompt DÉSACTIVÉ`
- Si `custom_prompt` est vide/null (anciens liens) :
  - Mode STANDARD : `BASE_PROMPT` + `SECURITY_PROMPT` + `campaignPrompt` (si défini)
  - Log: `[CHAT-IA] ✅ Mode STANDARD`

**Critères de réussite**:
- ✅ Test "George / Partenaires" : L'IA ne mentionne PLUS "cours", "tarifs" ou "faire bouger ton corps"
- ✅ Logs confirment: `[CHAT-IA] 🔒 Mode STRICT activé - Base Prompt désactivé`
- ✅ Anciens liens (sans `custom_prompt`) continuent de fonctionner en mode STANDARD
- ✅ Aucune erreur 500 sur les liens existants

**Fichiers modifiés**:
- `/app/backend/server.py` : 
  - Détection précoce du mode STRICT (avant construction du contexte)
  - Bloc `if not use_strict_mode:` pour les sections BOUTIQUE, COURS, ARTICLES, PROMOS, TWINT
  - Injection conditionnelle : `SECURITY + CUSTOM` en mode STRICT, `BASE + SECURITY + CAMPAIGN` en mode STANDARD
- `/app/frontend/src/components/CoachDashboard.js` : Textarea pour `custom_prompt` par lien

---

## Mise à jour du 29 Janvier 2026 - Prompts par Lien (Mode Production)

### Nouvelle fonctionnalité : `custom_prompt` par lien
**Objectif**: Permettre au coach de définir des instructions IA spécifiques pour chaque lien de chat, tout en maintenant la rétrocompatibilité avec les liens existants.

**Implémentation**:
- **Modèle `ChatSession`** : Nouveau champ `custom_prompt: Optional[str] = None` (nullable)
- **Endpoint `POST /api/chat/generate-link`** : Accepte un paramètre `custom_prompt` optionnel
- **Routes `/api/chat` et `/api/chat/ai-response`** : 
  - Récupèrent le `custom_prompt` du lien via `link_token`
  - Hiérarchie de priorité: `custom_prompt (lien)` > `campaignPrompt (global)` > aucun

**Frontend (Dashboard > Conversations)**:
- Nouveau textarea "Prompt spécifique pour ce lien (Optionnel)" dans la section "🔗 Lien Chat IA"
- data-testid: `new-link-custom-prompt`
- Séparation des champs pour "Lien IA" et "Chat Communautaire"

**Critères de réussite**:
- ✅ Les anciens liens (sans `custom_prompt`) continuent de fonctionner avec le prompt global
- ✅ Un nouveau lien avec `custom_prompt` utilise ses propres instructions (ignore le prompt global)
- ✅ Aucune erreur 500 sur les liens existants
- ✅ Logs explicites: `[CHAT-IA] ✅ Utilisation du custom_prompt du lien`

**Fichiers modifiés**:
- `/app/backend/server.py` : Modèles `ChatSession`, `ChatSessionUpdate`, routes `/api/chat/*`
- `/app/frontend/src/components/CoachDashboard.js` : États `newLinkCustomPrompt`, `newCommunityName`, UI textarea

---

## Mise à jour du 28 Janvier 2026 - Sécurisation IA et Campaign Prompt

### Nouvelles fonctionnalités :
- **Campaign Prompt PRIORITAIRE** : Nouveau champ `campaignPrompt` dans la config IA
  - Placé à la FIN du contexte avec encadrement "CONTEXTE PRIORITAIRE ET OBLIGATOIRE"
  - Écrase les règles par défaut si défini (ex: "Réponds en majuscules")
  - Configurable dans Dashboard > Conversations > Agent IA
  - data-testid: `campaign-prompt-input`

- **Restriction HORS-SUJET** : L'IA refuse les questions non liées aux produits/cours/offres
  - Réponse automatique: "Désolé, je suis uniquement programmé pour vous assister sur nos offres et formations. 🙏"
  - Exemples refusés: cuisine, politique, météo, conseils généraux

- **Protection des codes promo** : Les codes textuels ne sont JAMAIS transmis à l'IA
  - L'IA ne peut pas inventer ni révéler de codes promotionnels
  - Section "PROMOS SPÉCIALES" supprimée du contexte IA

### Fichiers modifiés :
- `/app/backend/server.py` : Modèle `AIConfig` + endpoints `/api/chat` et `/api/chat/ai-response`
- `/app/frontend/src/components/CoachDashboard.js` : Nouveau champ textarea pour `campaignPrompt`

---

## Mise à jour du 26 Janvier 2025 - Widget Chat Mobile

### Modifications apportées :
- **Affichage des noms** : Chaque message reçu affiche maintenant le nom de l'expéditeur AU-DESSUS de la bulle
- **Différenciation des types** :
  - Coach humain → Bulle violette (#8B5CF6), nom en jaune/or, badge "🏋️ Coach"
  - Assistant IA → Bulle gris foncé, nom en violet clair "🤖 Assistant"
  - Membres → Bulle gris foncé, nom en cyan
- **Alignement corrigé** : Messages envoyés à droite, messages reçus à gauche
- **Fichier modifié** : `/app/frontend/src/components/ChatWidget.js`

## Original Problem Statement
Application de réservation de casques audio pour des cours de fitness Afroboost. Design sombre néon avec fond noir pur (#000000) et accents rose/violet.

**Extension - Système de Lecteur Média Unifié** : Création de pages de destination vidéo épurées (`afroboosteur.com/v/[slug]`) avec miniatures personnalisables, bouton d'appel à l'action (CTA), et aperçus riches (OpenGraph) pour le partage sur les réseaux sociaux.

## User Personas
- **Utilisateurs**: Participants aux cours de fitness qui réservent des casques audio
- **Coach**: Administrateur qui gère les cours, offres, réservations, codes promo et campagnes marketing

## Core Requirements

### Système de Réservation
- [x] Sélection de cours et dates
- [x] Choix d'offres (Cours à l'unité, Carte 10 cours, Abonnement)
- [x] Formulaire d'information utilisateur (Nom, Email, WhatsApp)
- [x] Application de codes promo avec validation en temps réel
- [x] Liens de paiement (Stripe, PayPal, Twint)
- [x] Confirmation de réservation avec code unique

### Mode Coach Secret
- [x] Accès par 3 clics rapides sur le copyright
- [x] Login avec Google OAuth (contact.artboost@gmail.com)
- [x] Tableau de bord avec onglets multiples

### Système de Lecteur Média Unifié (V5 FINAL - 23 Jan 2026)
- [x] **Lecteur HTML5 natif** : iframe Google Drive sans marquage YouTube
- [x] **ZÉRO MARQUAGE** : Aucun logo YouTube, contrôles Google Drive
- [x] **Bouton Play rose #E91E63** : Design personnalisé au centre de la thumbnail
- [x] **Bouton CTA rose #E91E63** : Point focal centré sous la vidéo
- [x] **Responsive mobile** : Testé sur iPhone X (375x812)
- [x] **Template Email V5** : Anti-promotions avec texte brut AVANT le header violet

### Gestion des Campagnes (23 Jan 2026)
- [x] **Création de campagnes** : Nom, message, mediaUrl, contacts ciblés, canaux
- [x] **Modification de campagnes** : Bouton ✏️ pour éditer les campagnes draft/scheduled
- [x] **Lancement de campagnes** : Envoi via Resend (email) avec template V5
- [x] **Historique** : Tableau avec statuts (draft, scheduled, sending, completed)

---

## What's Been Implemented (24 Jan 2026)

### 🔥 Bug Fix: Chat IA - Vision Totale du Site
**Problème:** L'IA du ChatWidget était "aveugle" aux données dynamiques (produits, articles). Elle ne reconnaissait pas les produits existants comme "café congolais" lors des conversations.

**Cause Racine:** Le frontend utilise `/api/chat/ai-response` (pas `/api/chat`) quand l'utilisateur a une session active. Cette route avait un contexte DIFFÉRENT et incomplet:
- Requête MongoDB erronée: `{active: True}` au lieu de `{visible: {$ne: False}}`
- Pas de distinction produits (`isProduct: True`) vs services
- Contexte tronqué sans produits, cours, ni articles

**Correction:** 
- Route `/api/chat/ai-response` dans `/app/backend/server.py` (lignes 3192+)
- Contexte dynamique complet synchronisé avec `/api/chat`:
  - Produits (isProduct: True)
  - Services/Offres
  - Cours disponibles
  - Articles et actualités
  - Codes promo actifs
- Logs de diagnostic ajoutés pour traçabilité

**Validation:** Test E2E réussi - L'IA répond maintenant:
> "Salut TestUser ! 😊 Oui, nous avons du café congolais en vente. Il est disponible pour 10.0 CHF."

---

### 💳 Nouvelle Fonctionnalité: Lien de Paiement Twint Dynamique
**Objectif:** Permettre au coach de définir un lien Twint et faire en sorte que l'IA le propose automatiquement aux clients.

**Implémentation:**
1. **Backend (`/app/backend/server.py`):**
   - Champ `twintPaymentUrl` ajouté au modèle `AIConfig` (ligne 2130)
   - Injection du lien dans le contexte IA (routes `/api/chat` et `/api/chat/ai-response`)
   - Instruction conditionnelle: si lien vide → redirection vers coach

2. **Frontend (`/app/frontend/src/components/CoachDashboard.js`):**
   - Champ texte "💳 Lien de paiement Twint" dans la section Agent IA (ligne 5381)
   - data-testid: `twint-payment-url-input`
   - Warning affiché si non configuré

**Validation:** Test E2E réussi - Quand on demande "Je veux acheter le café, comment je paye ?":
> "Pour régler ton achat, clique sur ce lien Twint sécurisé: https://twint.ch/pay/afroboost-test-123 💳"

---

### 🗂️ CRM Avancé - Historique Conversations (24 Jan 2026)
**Objectif:** Transformer la section Conversations en un tableau de bord professionnel avec recherche et scroll performant.

**Backend (`/app/backend/server.py`):**
- Nouvel endpoint `GET /api/conversations` (lignes 2883-2993)
- Paramètres: `page`, `limit` (max 100), `query`, `include_deleted`
- Recherche dans: noms participants, emails, contenu des messages, titres
- Enrichissement: dernier message, infos participants, compteur de messages
- Retour: `conversations`, `total`, `page`, `pages`, `has_more`

**Frontend (`/app/frontend/src/components/CoachDashboard.js`):**
- États CRM: `conversationsPage`, `conversationsTotal`, `conversationsHasMore`, `enrichedConversations`
- `loadConversations()`: Charge les conversations avec pagination
- `loadMoreConversations()`: Infinite scroll (80% du scroll)
- `handleSearchChange()`: Recherche avec debounce 300ms
- `formatConversationDate()`: Badges (Aujourd'hui, Hier, date complète)
- `groupedConversations`: Groupement par date via useMemo

**UI:**
- Barre de recherche avec clear button et compteur de résultats
- Liste avec Infinite Scroll (maxHeight 450px)
- Badges de date sticky entre les groupes
- Messages avec timestamps et séparateurs de date

**Test report:** `/app/test_reports/iteration_37.json` - 100% passed

---

### Fonctionnalité "Modifier une Campagne" (23 Jan 2026)
1. ✅ **Bouton ✏️ (Modifier)** : Visible dans le tableau pour campagnes draft/scheduled
2. ✅ **Pré-remplissage du formulaire** : Nom, message, mediaUrl, contacts, canaux
3. ✅ **Titre dynamique** : "Nouvelle Campagne" → "✏️ Modifier la Campagne"
4. ✅ **Bouton de soumission dynamique** : "🚀 Créer" → "💾 Enregistrer les modifications"
5. ✅ **Bouton Annuler** : Réinitialise le formulaire et sort du mode édition
6. ✅ **API PUT /api/campaigns/{id}** : Met à jour les champs et renvoie la campagne modifiée

### Template Email V5 Anti-Promotions
1. ✅ **3 lignes de texte brut** AVANT le header violet
2. ✅ **Fond clair #f5f5f5** : Plus neutre pour Gmail
3. ✅ **Card compacte 480px** : Réduit de 20%
4. ✅ **Image 400px** : Taille optimisée
5. ✅ **Preheader invisible** : Pour l'aperçu Gmail

### Tests Automatisés - Iteration 34
- **Backend** : 15/15 tests passés (100%)
- **Fichier** : `/app/backend/tests/test_campaign_modification.py`

---

## Technical Architecture

```
/app/
├── backend/
│   ├── server.py       # FastAPI avec Media API, Campaigns API, Email Template V5
│   └── .env            # MONGO_URL, RESEND_API_KEY, FRONTEND_URL
└── frontend/
    ├── src/
    │   ├── App.js      # Point d'entrée, routage /v/{slug}
    │   ├── components/
    │   │   ├── CoachDashboard.js # Gestion campagnes avec édition
    │   │   └── MediaViewer.js    # Lecteur vidéo - Google Drive iframe
    │   └── services/
    └── .env            # REACT_APP_BACKEND_URL
```

### Key API Endpoints - Campaigns
- `GET /api/campaigns`: Liste toutes les campagnes
- `GET /api/campaigns/{id}`: Récupère une campagne
- `POST /api/campaigns`: Crée une nouvelle campagne (status: draft)
- `PUT /api/campaigns/{id}`: **NOUVEAU** - Modifie une campagne existante
- `DELETE /api/campaigns/{id}`: Supprime une campagne
- `POST /api/campaigns/{id}/launch`: Lance l'envoi

### Data Model - campaigns
```json
{
  "id": "uuid",
  "name": "string",
  "message": "string",
  "mediaUrl": "/v/{slug} ou URL directe",
  "mediaFormat": "16:9",
  "targetType": "all | selected",
  "selectedContacts": ["contact_id_1", "contact_id_2"],
  "channels": {"whatsapp": true, "email": true, "instagram": false},
  "status": "draft | scheduled | sending | completed",
  "scheduledAt": "ISO date ou null",
  "results": [...],
  "createdAt": "ISO date",
  "updatedAt": "ISO date"
}
```

---

## Prioritized Backlog

### P0 - Completed ✅
- [x] Lecteur Google Drive sans marquage YouTube
- [x] Template Email V5 Anti-Promotions
- [x] Fonctionnalité "Modifier une Campagne"
- [x] Tests automatisés iteration 34
- [x] **Scheduler de campagnes DAEMON** (24 Jan 2026) - RÉPARÉ ✅
- [x] **Configuration Twilio Production** (24 Jan 2026) - VERROUILLÉE ✅
- [x] **Chat IA - Vision Totale du Site** (24 Jan 2026) - RÉPARÉ ✅
  - Bug: La route `/api/chat/ai-response` n'injectait pas le contexte dynamique (produits, articles)
  - Correction: Synchronisation du contexte avec `/api/chat` (MongoDB: offers, courses, articles)
  - Test: L'IA reconnaît maintenant "café congolais" à "10 CHF" ✅
- [x] **Lien de Paiement Twint Dynamique** (24 Jan 2026) - NOUVEAU ✅
  - Le coach peut configurer un lien Twint dans Dashboard > Conversations > Agent IA > "Lien de paiement Twint"
  - L'IA propose automatiquement ce lien quand un client veut acheter
  - Si le lien est vide, l'IA redirige vers le coach
- [x] **CRM Avancé - Historique Conversations** (24 Jan 2026) - NOUVEAU ✅
  - Endpoint `GET /api/conversations` avec pagination (page, limit) et recherche (query)
  - Frontend avec Infinite Scroll (charge à 80% du scroll)
  - Barre de recherche avec debounce 300ms
  - Badges de date (Aujourd'hui, Hier, date complète)
  - Timestamps précis sur chaque message
  - Séparateurs de date dans l'historique des conversations
- [x] **Notifications Sonores et Visuelles** (24 Jan 2026) - STABILISÉ ✅
  - Backend: Champ `notified` sur messages, endpoints optimisés avec `include_ai` param
  - Frontend: Polling toutes les 10s avec cleanup `clearInterval` propre
  - **BOUTON DE TEST** visible avec logs de debug (NOTIF_DEBUG:)
  - **FALLBACK TOAST** si notifications browser bloquées
  - **Option "Notifier réponses IA"** pour suivre l'activité de l'IA
  - Permission persistée: polling auto si déjà autorisé au refresh
  - Protection contre erreurs son/notif (try/catch, pas de boucle)
  - Garde-fous: Vision IA (café 10 CHF) et Twint non impactés ✅

- [x] **Boutons de Suppression Restaurés** (24 Jan 2026) - RÉPARÉ ✅
  - Nouveau endpoint `DELETE /api/chat/links/{link_id}` pour supprimer les liens
  - Fonction `deleteChatLink()` avec confirmation "Êtes-vous sûr ?"
  - `deleteChatSession()` avec confirmation (suppression logique)
  - `deleteChatParticipant()` avec confirmation (suppression définitive)
  - Tous les boutons 🗑️ fonctionnels avec data-testid

- [x] **Optimisation UI Responsive** (24 Jan 2026) - NOUVEAU ✅
  - Scroll interne pour Offres (max-height: 500px)
  - Scroll interne pour Médias (max-height: 500px)
  - Scroll interne pour Codes Promo (max-height: 400px)
  - Recherche locale pour Offres (filtrage instantané)
  - Recherche locale pour Codes Promo (filtrage instantané)
  - Layout Campagnes responsive (flex-col sur mobile)
  - Boutons pleine largeur sur mobile

- [x] **Fix Permissions Notifications** (24 Jan 2026) - NOUVEAU ✅
  - Banner de demande de permission au premier accès à l'onglet Conversations
  - Fallback Toast interne si notifications browser bloquées
  - Service amélioré avec `getNotificationPermissionStatus()` et `fallbackNeeded`
  - Badge de statut (🔔 actives / 🔕 mode toast)

- [x] **Scroll et Filtrage Réservations** (25 Jan 2026) - NOUVEAU ✅
  - **Scroll interne** : Zone scrollable de 600px max pour desktop et mobile
  - **En-têtes fixes** : `sticky top-0` sur le thead du tableau desktop + `position: relative` sur conteneur
  - **Filtrage optimisé avec useMemo** : `filteredReservations` basé sur `[reservations, reservationsSearch]`
  - **Critères de recherche** : nom, email, WhatsApp, date, code de réservation, nom du cours
  - **Compteur de résultats** : `{filteredReservations.length} résultat(s)` sous la barre de recherche
  - **Message "Aucune réservation correspondante"** : Affiché quand filteredReservations est vide
  - Test report: `/app/test_reports/iteration_41.json` - 100% passed

- [x] **Scanner QR Réparé** (25 Jan 2026) - NOUVEAU ✅
  - CDN Html5Qrcode ajouté dans index.html (ligne 52)
  - Protection fallback si CDN non chargé → mode manuel automatique
  - Modal s'ouvre correctement sans erreur ReferenceError
  - Options caméra et saisie manuelle fonctionnelles
  - Test report: `/app/test_reports/iteration_40.json` - 100% passed

- [x] **Suppressions avec mise à jour UI instantanée** (25 Jan 2026) - VÉRIFIÉ ✅
  - **Logs DELETE_UI** : Tracent les transitions d'état (`Réservations filtrées: 2 -> 1`)
  - Réservations : `setReservations(prev => prev.filter(r => r.id !== id))`
  - Conversations : `setChatSessions`, `setEnrichedConversations`, `setChatLinks` tous mis à jour
  - Test report: `/app/test_reports/iteration_41.json` - 100% passed

### P1 - À faire
- [ ] **Gérer les articles dans le Dashboard** : Interface CRUD pour créer/modifier/supprimer des articles
- [ ] **Activation numéro WhatsApp Suisse (+41)** : En attente approbation Meta (config Twilio bloquée)
- [ ] **Refactoring CoachDashboard.js** : Extraire composants (>6000 lignes)
- [ ] **Export CSV contacts CRM** : Valider le flux de bout en bout

### P2 - Backlog
- [ ] Dashboard analytics pour le coach
- [ ] Support upload vidéo direct depuis le dashboard
- [ ] Manuel utilisateur

---

## Scheduler de Campagnes - INTÉGRÉ AU SERVEUR (24 Jan 2026)

### Architecture
Le scheduler est maintenant **intégré directement dans `server.py`** et démarre automatiquement avec le serveur FastAPI via un thread daemon. Plus besoin de lancement manuel !

### Fichiers
- `/app/backend/server.py` - Contient le scheduler intégré (lignes 4485+)
- `/var/log/supervisor/backend.err.log` - Logs détaillés du scheduler

### Fonctionnalités
- ✅ **DÉMARRAGE AUTOMATIQUE** : Thread lancé au startup du serveur FastAPI
- ✅ **MODE DAEMON** : Boucle `while True` avec `time.sleep(30)`
- ✅ **HEARTBEAT** : Log `[SYSTEM] Scheduler is alive` toutes les 60s
- ✅ **Comparaison UTC** : `datetime.now(timezone.utc)` pour toutes les dates
- ✅ **Isolation des canaux** : Email et WhatsApp dans des `try/except` séparés
- ✅ **Gestion multi-dates** : `scheduledDates[]` → `sentDates[]` → `status: completed`
- ✅ **Erreurs silencieuses** : L'échec d'un canal ne bloque pas les autres

### Vérification du Scheduler
```bash
# Vérifier les logs
tail -f /var/log/supervisor/backend.err.log | grep SCHEDULER

# Chercher le heartbeat
grep "Scheduler is alive" /var/log/supervisor/backend.out.log
```

### Comportement
1. **Au démarrage** : `[SYSTEM] ✅ Scheduler is ONLINE`
2. **Toutes les 30s** : Scan des campagnes `status: scheduled`
3. **Si date passée** : Traitement automatique (email/WhatsApp)
4. **Après traitement** : Mise à jour `sentDates`, `status`, `lastProcessedAt`

---

## Credentials & URLs de Test
- **Coach Access**: 3 clics rapides sur "© Afroboost 2026" → Login Google OAuth
- **Email autorisé**: contact.artboost@gmail.com
- **Test Media Slug**: test-final
- **URL de test**: https://partner-platform-6.preview.emergentagent.com/v/test-final
- **Vidéo Google Drive**: https://drive.google.com/file/d/1AkjHltEq-PAnw8OE-dR-lPPcpP44qvHv/view
