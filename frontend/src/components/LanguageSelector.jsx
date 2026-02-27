// Sélecteur de langue - Afroboost
import React from 'react';
import APP_CONFIG from '../../config';

const LanguageSelector = ({ lang, setLang }) => {
  const languages = [
    { code: 'fr', flag: '🇫🇷', name: 'Français' },
    { code: 'en', flag: '🇬🇧', name: 'English' },
    { code: 'de', flag: '🇩🇪', name: 'Deutsch' }
  ];

  return (
    <div className="flex gap-2">
      {languages.map(({ code, flag, name }) => (
        <button
          key={code}
          onClick={() => setLang(code)}
          className={`px-3 py-2 rounded-lg transition-all ${
            lang === code 
              ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/30' 
              : 'glass text-white/70 hover:text-white hover:bg-white/10'
          }`}
          title={name}
        >
          {flag}
        </button>
      ))}
    </div>
  );
};

export default LanguageSelector;
