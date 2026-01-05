// src/pages/RegisterPage.js
// Pagina de inregistrare
// Creeaza cont nou si genereaza chei RSA

import React, { useState, useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../App';
import './AuthPages.css';

/**
 * Componenta pentru pagina de inregistrare
 * 
 * La inregistrare:
 * 1. Se creeaza contul cu username, email, parola
 * 2. Se genereaza automat o pereche de chei RSA
 * 3. Cheia privata este salvata local (important pentru decriptare!)
 */
function RegisterPage() {
  const { register } = useContext(AuthContext);
  
  // State pentru formular
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Handler pentru submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // Validari client-side
    if (password !== confirmPassword) {
      setError('Parolele nu se potrivesc');
      return;
    }
    
    if (password.length < 6) {
      setError('Parola trebuie sa aiba minim 6 caractere');
      return;
    }
    
    if (username.length < 3) {
      setError('Username-ul trebuie sa aiba minim 3 caractere');
      return;
    }
    
    setLoading(true);
    
    try {
      const result = await register(username, email, password);
      if (!result.success) {
        setError(result.error || 'Eroare la inregistrare');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Eroare de conexiune');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="auth-page">
      <div className="auth-container">
        {/* Header cu logo si titlu */}
        <div className="auth-header">
          <div className="auth-logo">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 6c1.4 0 2.8 1.1 2.8 2.5V11c.6.3 1.2 1 1.2 1.8V16c0 1.1-.9 2-2 2h-4c-1.1 0-2-.9-2-2v-3.2c0-.8.5-1.5 1.2-1.8V9.5C9.2 8.1 10.6 7 12 7zm0 1.2c-.8 0-1.5.7-1.5 1.3v1.5h3V9.5c0-.6-.7-1.3-1.5-1.3z"/>
            </svg>
          </div>
          <h1>Creeaza cont</h1>
          <p className="auth-subtitle">Inregistreaza-te pentru a incepe sa comunici securizat</p>
        </div>
        
        {/* Formular de inregistrare */}
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="input-group">
            <label className="input-label">Nume utilizator</label>
            <input
              type="text"
              className="input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Alege un username"
              required
              autoComplete="username"
            />
          </div>
          
          <div className="input-group">
            <label className="input-label">Email</label>
            <input
              type="email"
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="email@exemplu.com"
              required
              autoComplete="email"
            />
          </div>
          
          <div className="input-group">
            <label className="input-label">Parola</label>
            <input
              type="password"
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Minim 6 caractere"
              required
              autoComplete="new-password"
            />
          </div>
          
          <div className="input-group">
            <label className="input-label">Confirma parola</label>
            <input
              type="password"
              className="input"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Repeta parola"
              required
              autoComplete="new-password"
            />
          </div>
          
          {error && <div className="error-message">{error}</div>}
          
          <button 
            type="submit" 
            className="btn btn-primary w-full"
            disabled={loading}
          >
            {loading ? 'Se creeaza contul...' : 'Creeaza cont'}
          </button>
        </form>
        
        {/* Link catre login */}
        <div className="auth-footer">
          <p>Ai deja cont? <Link to="/login">Conecteaza-te</Link></p>
        </div>
        
        {/* Informatii despre chei RSA */}
        <div className="crypto-info-box warning">
          <h4>
            <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
              <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
            </svg>
            Important despre cheile de criptare
          </h4>
          <p>
            La inregistrare se genereaza automat o pereche de chei <strong>RSA</strong>:
          </p>
          <ul>
            <li><strong>Cheia publica</strong> - vizibila pentru toti, folosita pentru a-ti trimite mesaje criptate</li>
            <li><strong>Cheia privata</strong> - salvata local, necesara pentru decriptarea mesajelor primite</li>
          </ul>
          <p className="text-sm text-muted" style={{marginTop: '8px'}}>
            Cheia privata este salvata automat in browser. Daca o pierzi, nu vei putea citi mesajele criptate!
          </p>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;
