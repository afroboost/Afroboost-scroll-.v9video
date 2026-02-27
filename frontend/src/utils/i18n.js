// Traductions i18n - Afroboost
// Structure modulaire pour Vercel

export const translations = {
  fr: {
    // App
    loading: "Chargement...",
    error: "Erreur",
    success: "Succès",
    cancel: "Annuler",
    save: "Sauvegarder",
    add: "Ajouter",
    edit: "Modifier",
    delete: "Supprimer",
    confirm: "Confirmer",
    
    // Navigation
    home: "Accueil",
    shop: "Boutique",
    profile: "Profil",
    contact: "Contact",
    
    // Booking
    selectCourse: "Choisissez votre cours",
    selectDate: "Choisissez votre date",
    selectOffer: "Choisissez votre offre",
    yourInfo: "Vos informations",
    fullName: "Nom complet",
    emailRequired: "Email (obligatoire)",
    whatsappRequired: "WhatsApp (obligatoire)",
    promoCode: "Code promo",
    applyCode: "Appliquer",
    acceptTerms: "J'accepte les conditions générales",
    bookNow: "Réserver maintenant",
    
    // Coach
    coachLogin: "Connexion Coach",
    email: "Email",
    password: "Mot de passe",
    login: "Se connecter",
    logout: "Déconnexion",
    forgotPassword: "Mot de passe oublié ?",
    wrongCredentials: "Identifiants incorrects",
    
    // Offers
    offers: "Offres",
    offerName: "Nom de l'offre",
    price: "Prix (CHF)",
    thumbnail: "Image",
    visible: "Visible",
    addOffer: "Ajouter une offre",
    
    // Reservations
    reservations: "Réservations",
    noReservations: "Aucune réservation",
    downloadCSV: "📥 Télécharger CSV",
    scanTicket: "📷 Scanner un ticket",
    
    // Status
    validated: "Validé",
    pending: "En attente",
    
    // Products
    physicalProduct: "Produit physique",
    shippingAddress: "Adresse de livraison",
    shippingCost: "Frais de port",
    tva: "TVA",
    
    // Messages
    swipeToSeeMore: "← Faites défiler pour voir plus d'offres →",
    noPaymentConfigured: "Paiement requis – réservation impossible.",
    reservationSuccess: "Réservation confirmée !",
    
    // Admin
    adminEmail: "contact.artboost@gmail.com"
  },
  
  en: {
    loading: "Loading...",
    error: "Error",
    success: "Success",
    cancel: "Cancel",
    save: "Save",
    add: "Add",
    edit: "Edit",
    delete: "Delete",
    confirm: "Confirm",
    
    home: "Home",
    shop: "Shop",
    profile: "Profile",
    contact: "Contact",
    
    selectCourse: "Select your course",
    selectDate: "Select your date",
    selectOffer: "Select your offer",
    yourInfo: "Your information",
    fullName: "Full name",
    emailRequired: "Email (required)",
    whatsappRequired: "WhatsApp (required)",
    promoCode: "Promo code",
    applyCode: "Apply",
    acceptTerms: "I accept the terms and conditions",
    bookNow: "Book now",
    
    coachLogin: "Coach Login",
    email: "Email",
    password: "Password",
    login: "Login",
    logout: "Logout",
    forgotPassword: "Forgot password?",
    wrongCredentials: "Invalid credentials",
    
    offers: "Offers",
    offerName: "Offer name",
    price: "Price (CHF)",
    thumbnail: "Image",
    visible: "Visible",
    addOffer: "Add offer",
    
    reservations: "Reservations",
    noReservations: "No reservations",
    downloadCSV: "📥 Download CSV",
    scanTicket: "📷 Scan ticket",
    
    validated: "Validated",
    pending: "Pending",
    
    physicalProduct: "Physical product",
    shippingAddress: "Shipping address",
    shippingCost: "Shipping cost",
    tva: "VAT",
    
    swipeToSeeMore: "← Swipe to see more offers →",
    noPaymentConfigured: "Payment required – booking impossible.",
    reservationSuccess: "Booking confirmed!",
    
    adminEmail: "contact.artboost@gmail.com"
  },
  
  de: {
    loading: "Laden...",
    error: "Fehler",
    success: "Erfolg",
    cancel: "Abbrechen",
    save: "Speichern",
    add: "Hinzufügen",
    edit: "Bearbeiten",
    delete: "Löschen",
    confirm: "Bestätigen",
    
    home: "Startseite",
    shop: "Shop",
    profile: "Profil",
    contact: "Kontakt",
    
    selectCourse: "Wählen Sie Ihren Kurs",
    selectDate: "Wählen Sie Ihr Datum",
    selectOffer: "Wählen Sie Ihr Angebot",
    yourInfo: "Ihre Informationen",
    fullName: "Vollständiger Name",
    emailRequired: "E-Mail (erforderlich)",
    whatsappRequired: "WhatsApp (erforderlich)",
    promoCode: "Promo-Code",
    applyCode: "Anwenden",
    acceptTerms: "Ich akzeptiere die AGB",
    bookNow: "Jetzt buchen",
    
    coachLogin: "Coach-Login",
    email: "E-Mail",
    password: "Passwort",
    login: "Anmelden",
    logout: "Abmelden",
    forgotPassword: "Passwort vergessen?",
    wrongCredentials: "Ungültige Anmeldedaten",
    
    offers: "Angebote",
    offerName: "Angebotsname",
    price: "Preis (CHF)",
    thumbnail: "Bild",
    visible: "Sichtbar",
    addOffer: "Angebot hinzufügen",
    
    reservations: "Reservierungen",
    noReservations: "Keine Reservierungen",
    downloadCSV: "📥 CSV herunterladen",
    scanTicket: "📷 Ticket scannen",
    
    validated: "Bestätigt",
    pending: "Ausstehend",
    
    physicalProduct: "Physisches Produkt",
    shippingAddress: "Lieferadresse",
    shippingCost: "Versandkosten",
    tva: "MwSt",
    
    swipeToSeeMore: "← Wischen für mehr Angebote →",
    noPaymentConfigured: "Zahlung erforderlich – Buchung nicht möglich.",
    reservationSuccess: "Buchung bestätigt!",
    
    adminEmail: "contact.artboost@gmail.com"
  }
};

// Hook de traduction
export const useTranslation = (lang = 'fr') => {
  const t = (key) => translations[lang]?.[key] || translations.fr[key] || key;
  return { t, translations: translations[lang] || translations.fr };
};

export default translations;
