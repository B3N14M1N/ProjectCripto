// src/pages/LoginPage.js
// Pagina de autentificare
// Design simplu cu informatii despre criptare

import React, { useState, useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../App';
import './AuthPages.css';

/**
 * Componenta pentru pagina de login
 * 
 * Permite autentificarea cu username/email si parola.
 * Include informatii educationale despre securitate.
 */
function LoginPage() {
  const { login } = useContext(AuthContext);
  
  // State pentru formular
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Handler pentru submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const result = await login(username, password);
      if (!result.success) {
        setError(result.error || 'Eroare la autentificare');
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
          <h1>SecureChat</h1>
          <p className="auth-subtitle">Chat criptat end-to-end cu AES si RSA</p>
        </div>
        
        {/* Formular de login */}
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="input-group">
            <label className="input-label">Utilizator sau Email</label>
            <input
              type="text"
              className="input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Introdu username sau email"
              required
              autoComplete="username"
            />
          </div>
          
          <div className="input-group">
            <label className="input-label">Parola</label>
            <input
              type="password"
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Introdu parola"
              required
              autoComplete="current-password"
            />
          </div>
          
          {error && <div className="error-message">{error}</div>}
          
          <button 
            type="submit" 
            className="btn btn-primary w-full"
            disabled={loading}
          >
            {loading ? 'Se conecteaza...' : 'Conectare'}
          </button>
        </form>
        
        {/* Link catre inregistrare */}
        <div className="auth-footer">
          <p>Nu ai cont? <Link to="/register">Creeaza unul acum</Link></p>
        </div>
        
        {/* Informatii despre criptare */}
        <div className="crypto-info-box">
          <h4>
            <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
            </svg>
            Despre securitate
          </h4>
          <p>
            Mesajele tale sunt protejate cu <strong>AES-256</strong> pentru criptarea continutului 
            si <strong>RSA-2048</strong> pentru schimbul securizat de chei. 
            Doar tu si destinatarii puteti citi mesajele.
          </p>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
