// src/pages/RegisterPage.js
// Pagina de inregistrare
// Creeaza cont nou si genereaza chei RSA

import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../App';
import './AuthPages.css';

/**
 * Componenta pentru pagina de inregistrare
 * 
 * La inregistrare:
 * 1. Se creeaza contul cu username, email, parola
 * 2. Se genereaza automat o pereche de chei RSA
 * 3. Utilizatorul poate descarca cheia privata intr-un fisier
 * 4. Cheia privata este salvata si local in browser
 */
function RegisterPage() {
  const { register } = useContext(AuthContext);
  const navigate = useNavigate();
  
  // State pentru formular
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  // State pentru ecranul de succes cu cheia privata
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [privateKeyData, setPrivateKeyData] = useState(null);
  const [registeredUsername, setRegisteredUsername] = useState('');
  
  // Functie pentru descarcarea cheii private
  const downloadPrivateKey = () => {
    if (!privateKeyData) return;
    
    const blob = new Blob([privateKeyData], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${registeredUsername}_private_key.pem`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  
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
      if (result.success) {
        // Afisam modalul cu cheia privata
        setPrivateKeyData(result.private_key);
        setRegisteredUsername(username);
        setShowKeyModal(true);
      } else {
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
            <li><strong>Cheia privata</strong> - necesara pentru decriptarea mesajelor primite</li>
          </ul>
          <p className="text-sm text-muted" style={{marginTop: '8px'}}>
            Vei avea optiunea sa descarci cheia privata intr-un fisier pentru backup.
          </p>
        </div>
      </div>
      
      {/* Modal pentru salvarea cheii private */}
      {showKeyModal && (
        <div className="modal-overlay">
          <div className="modal modal-lg">
            <div className="modal-header">
              <h3>
                <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24" style={{color: '#22c55e', marginRight: '8px'}}>
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>
                Cont creat cu succes!
              </h3>
            </div>
            <div className="modal-body">
              <div className="success-box" style={{marginBottom: '20px'}}>
                <p style={{color: '#22c55e', fontWeight: '600', marginBottom: '8px'}}>
                  ✓ Perechea de chei RSA a fost generata
                </p>
                <p style={{color: '#6b7280', fontSize: '14px'}}>
                  Cheia privata este salvata automat in browser, dar recomandam sa o descarci 
                  si intr-un fisier pentru backup, in caz ca schimbi dispozitivul.
                </p>
              </div>
              
              <div className="key-preview-box" style={{
                background: '#1f2937',
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '16px'
              }}>
                <label style={{color: '#9ca3af', fontSize: '12px', display: 'block', marginBottom: '8px'}}>
                  Cheia ta privata RSA-2048:
                </label>
                <pre style={{
                  color: '#e5e7eb',
                  fontSize: '11px',
                  fontFamily: 'monospace',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-all',
                  maxHeight: '150px',
                  overflow: 'auto',
                  margin: 0
                }}>
                  {privateKeyData}
                </pre>
              </div>
              
              <div className="warning-box" style={{
                background: '#fef3c7',
                border: '1px solid #fbbf24',
                borderRadius: '8px',
                padding: '12px',
                marginBottom: '16px'
              }}>
                <p style={{color: '#92400e', fontSize: '13px', margin: 0}}>
                  <strong>⚠️ Important:</strong> Aceasta cheie este necesara pentru a decripta mesajele. 
                  Daca o pierzi, nu vei mai putea citi mesajele primite!
                </p>
              </div>
            </div>
            <div className="modal-footer" style={{display: 'flex', gap: '12px', justifyContent: 'flex-end'}}>
              <button 
                className="btn btn-secondary"
                onClick={downloadPrivateKey}
                style={{display: 'flex', alignItems: 'center', gap: '8px'}}
              >
                <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
                  <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
                </svg>
                Descarca cheia (.pem)
              </button>
              <button 
                className="btn btn-primary"
                onClick={() => navigate('/chat')}
              >
                Continua catre chat
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default RegisterPage;
