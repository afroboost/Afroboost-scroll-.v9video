// Composants UI réutilisables - Afroboost
// Style: Dark Neon Theme

import React from 'react';

// Bouton principal avec effet néon
export const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  fullWidth = false,
  disabled = false,
  onClick,
  type = 'button',
  className = '',
  ...props 
}) => {
  const baseStyles = 'rounded-lg font-bold transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'btn-primary hover:scale-105',
    secondary: 'glass text-white hover:bg-white/10',
    danger: 'bg-red-600 hover:bg-red-500 text-white',
    ghost: 'bg-transparent text-purple-400 hover:text-purple-300 underline'
  };
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg'
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${fullWidth ? 'w-full' : ''} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

// Input avec style néon
export const Input = ({
  type = 'text',
  placeholder,
  value,
  onChange,
  required = false,
  disabled = false,
  className = '',
  label,
  error,
  ...props
}) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block mb-2 text-white text-sm">{label}</label>
      )}
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        required={required}
        disabled={disabled}
        className={`w-full px-4 py-3 rounded-lg neon-input disabled:opacity-50 ${error ? 'border-red-500' : ''} ${className}`}
        {...props}
      />
      {error && (
        <p className="mt-1 text-xs text-red-400">{error}</p>
      )}
    </div>
  );
};

// Carte avec style glass
export const Card = ({
  children,
  className = '',
  neonBorder = false,
  onClick,
  selected = false,
  ...props
}) => {
  return (
    <div
      onClick={onClick}
      className={`
        glass rounded-xl p-6 
        ${neonBorder ? 'neon-border' : ''} 
        ${selected ? 'border-2 border-pink-500 shadow-lg shadow-pink-500/30' : ''}
        ${onClick ? 'cursor-pointer hover:scale-[1.02] transition-transform' : ''}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
};

// Modal
export const Modal = ({
  isOpen,
  onClose,
  children,
  title,
  maxWidth = 'max-w-md'
}) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div 
        className={`modal-content glass rounded-xl p-8 ${maxWidth} w-full neon-border`}
        onClick={e => e.stopPropagation()}
      >
        {title && (
          <h2 className="font-bold mb-6 text-center text-white text-2xl">{title}</h2>
        )}
        {children}
      </div>
    </div>
  );
};

// Badge de statut
export const StatusBadge = ({ status, children }) => {
  const styles = {
    success: 'bg-green-600 text-white',
    pending: 'bg-yellow-600 text-white',
    error: 'bg-red-600 text-white',
    info: 'bg-purple-600 text-white'
  };

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-bold ${styles[status] || styles.info}`}>
      {children}
    </span>
  );
};

// Loader
export const Loader = ({ size = 'md', className = '' }) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  return (
    <div className={`${sizes[size]} border-2 border-purple-500 border-t-transparent rounded-full animate-spin ${className}`} />
  );
};

// Switch Toggle
export const Switch = ({ checked, onChange, label }) => {
  return (
    <div className="flex items-center gap-3">
      {label && <span className="text-white text-sm">{label}</span>}
      <div
        onClick={() => onChange(!checked)}
        className={`switch ${checked ? 'active' : ''} cursor-pointer`}
      />
    </div>
  );
};

// Icône Info (i)
export const InfoIcon = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10"/>
    <path d="M12 16v-4M12 8h.01"/>
  </svg>
);

// Icône Loupe
export const SearchIcon = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="11" cy="11" r="8"/>
    <path d="M21 21l-4.35-4.35"/>
  </svg>
);

// Icône Close
export const CloseIcon = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M18 6L6 18M6 6l12 12"/>
  </svg>
);

export default {
  Button,
  Input,
  Card,
  Modal,
  StatusBadge,
  Loader,
  Switch,
  InfoIcon,
  SearchIcon,
  CloseIcon
};
