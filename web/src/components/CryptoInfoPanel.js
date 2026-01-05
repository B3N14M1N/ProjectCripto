// src/components/CryptoInfoPanel.js
// Panel educational despre criptare
// Afiseaza explicatii despre AES, RSA si schema hibrida

import React, { useState, useEffect } from 'react';
import { authAPI, chatAPI } from '../services/api';
import { encryptionInfo } from '../services/crypto';
import './CryptoInfoPanel.css';

/**
 * Componenta CryptoInfoPanel
 * 
 * Panel informativ care explica:
 * 1. Ce este AES si cum functioneaza
 * 2. Ce este RSA si rolul cheilor publice/private
 * 3. Schema hibrida - de ce combinam AES cu RSA
 * 4. Cum sunt stocate mesajele in baza de date
 */
function CryptoInfoPanel({ conversation, onClose }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [cryptoInfo, setCryptoInfo] = useState(null);
  const [convCryptoInfo, setConvCryptoInfo] = useState(null);
  
  // Incarcam informatiile despre criptare
  useEffect(() => {
    loadCryptoInfo();
    if (conversation) {
      loadConversationCryptoInfo();
    }
  }, [conversation]);
  
  const loadCryptoInfo = async () => {
    try {
      const response = await authAPI.getCryptoInfo();
      setCryptoInfo(response.data);
    } catch (error) {
      console.error('Eroare:', error);
    }
  };
  
  const loadConversationCryptoInfo = async () => {
    if (!conversation) return;
    try {
      const response = await chatAPI.getConversationCryptoInfo(conversation.id);
      setConvCryptoInfo(response.data);
    } catch (error) {
      console.error('Eroare:', error);
    }
  };
  
  return (
    <div className="crypto-panel">
      {/* Header */}
      <div className="panel-header">
        <h3>
          <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
          </svg>
          Informatii Criptare
        </h3>
        <button className="btn-icon" onClick={onClose}>✕</button>
      </div>
      
      {/* Tabs */}
      <div className="panel-tabs">
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Prezentare
        </button>
        <button 
          className={`tab ${activeTab === 'aes' ? 'active' : ''}`}
          onClick={() => setActiveTab('aes')}
        >
          AES
        </button>
        <button 
          className={`tab ${activeTab === 'rsa' ? 'active' : ''}`}
          onClick={() => setActiveTab('rsa')}
        >
          RSA
        </button>
        <button 
          className={`tab ${activeTab === 'flow' ? 'active' : ''}`}
          onClick={() => setActiveTab('flow')}
        >
          Flux
        </button>
        <button 
          className={`tab ${activeTab === 'db' ? 'active' : ''}`}
          onClick={() => setActiveTab('db')}
        >
          Stocare
        </button>
      </div>
      
      {/* Content */}
      <div className="panel-content">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="tab-content">
            <h4>Schema de Criptare Hibrida</h4>
            <p>
              Aceasta aplicatie foloseste o <strong>schema hibrida</strong> care combina 
              doua tipuri de criptare pentru a obtine atat securitate cat si performanta.
            </p>
            
            <div className="info-cards">
              <div className="info-card aes">
                <div className="card-header">
                  <span className="encryption-indicator aes">AES-256</span>
                  <span className="card-type">Criptare Simetrica</span>
                </div>
                <p>Folosita pentru continutul mesajelor. Rapida si eficienta pentru date mari.</p>
              </div>
              
              <div className="info-card rsa">
                <div className="card-header">
                  <span className="encryption-indicator rsa">RSA-2048</span>
                  <span className="card-type">Criptare Asimetrica</span>
                </div>
                <p>Folosita pentru schimbul cheilor AES. Permite comunicare securizata fara canal pre-partajat.</p>
              </div>
            </div>
            
            <div className="why-hybrid">
              <h5>De ce schema hibrida?</h5>
              <ul>
                <li><strong>AES singur:</strong> Necesita un canal securizat pentru schimbul cheii</li>
                <li><strong>RSA singur:</strong> Prea lent pentru date mari, limitat la ~190 bytes</li>
                <li><strong>Combinat:</strong> Obtinem viteza AES + securitatea schimbului RSA</li>
              </ul>
            </div>
          </div>
        )}
        
        {/* AES Tab */}
        {activeTab === 'aes' && (
          <div className="tab-content">
            <h4>AES - Advanced Encryption Standard</h4>
            
            <div className="specs-table">
              <div className="spec-row">
                <span className="spec-label">Algoritm</span>
                <span className="spec-value">AES-256-CBC</span>
              </div>
              <div className="spec-row">
                <span className="spec-label">Dimensiune cheie</span>
                <span className="spec-value">256 biti (32 bytes)</span>
              </div>
              <div className="spec-row">
                <span className="spec-label">Dimensiune bloc</span>
                <span className="spec-value">128 biti (16 bytes)</span>
              </div>
              <div className="spec-row">
                <span className="spec-label">Mod operare</span>
                <span className="spec-value">CBC (Cipher Block Chaining)</span>
              </div>
              <div className="spec-row">
                <span className="spec-label">Padding</span>
                <span className="spec-value">PKCS7</span>
              </div>
            </div>
            
            <div className="explanation">
              <h5>Cum functioneaza AES?</h5>
              <p>
                AES este un algoritm de <strong>criptare simetrica</strong> - foloseste 
                aceeasi cheie pentru criptare si decriptare.
              </p>
              
              <h5>Modul CBC</h5>
              <p>
                In modul CBC (Cipher Block Chaining), fiecare bloc de 16 bytes este 
                XOR-at cu blocul criptat anterior inainte de criptare. Primul bloc 
                este XOR-at cu un <strong>IV (Initialization Vector)</strong>.
              </p>
              
              <div className="code-example">
                <code>
                  Bloc[i] = AES_Encrypt(Plaintext[i] XOR Ciphertext[i-1])
                </code>
              </div>
              
              <h5>De ce AES-256?</h5>
              <ul>
                <li>Standard industrial, folosit de guverne si banci</li>
                <li>Rezistent la toate atacurile cunoscute</li>
                <li>Foarte rapid - optimizat hardware pe procesoare moderne</li>
              </ul>
            </div>
          </div>
        )}
        
        {/* RSA Tab */}
        {activeTab === 'rsa' && (
          <div className="tab-content">
            <h4>RSA - Rivest-Shamir-Adleman</h4>
            
            <div className="specs-table">
              <div className="spec-row">
                <span className="spec-label">Algoritm</span>
                <span className="spec-value">RSA-2048</span>
              </div>
              <div className="spec-row">
                <span className="spec-label">Dimensiune cheie</span>
                <span className="spec-value">2048 biti</span>
              </div>
              <div className="spec-row">
                <span className="spec-label">Padding</span>
                <span className="spec-value">OAEP (SHA-256)</span>
              </div>
              <div className="spec-row">
                <span className="spec-label">Max. date criptate</span>
                <span className="spec-value">~190 bytes</span>
              </div>
            </div>
            
            <div className="explanation">
              <h5>Cele doua chei</h5>
              
              <div className="key-info">
                <div className="key-card public">
                  <h6>🔓 Cheia Publica</h6>
                  <ul>
                    <li>Distribuita tuturor</li>
                    <li>Folosita pentru CRIPTARE</li>
                    <li>Stocata in baza de date</li>
                    <li>Vizibila pentru oricine</li>
                  </ul>
                </div>
                
                <div className="key-card private">
                  <h6>🔐 Cheia Privata</h6>
                  <ul>
                    <li>Pastrata secreta</li>
                    <li>Folosita pentru DECRIPTARE</li>
                    <li>Stocata local in browser</li>
                    <li>Nu trebuie partajata niciodata!</li>
                  </ul>
                </div>
              </div>
              
              <h5>Cum functioneaza?</h5>
              <p>
                RSA se bazeaza pe dificultatea factorizarii numerelor mari.
                Cheia publica si privata sunt legate matematic, dar este 
                practic imposibil sa calculezi cheia privata din cea publica.
              </p>
              
              <div className="code-example">
                <code>
                  Ciphertext = Message^e mod n (criptare cu cheie publica)<br/>
                  Message = Ciphertext^d mod n (decriptare cu cheie privata)
                </code>
              </div>
            </div>
          </div>
        )}
        
        {/* Flow Tab */}
        {activeTab === 'flow' && (
          <div className="tab-content">
            <h4>Fluxul de Criptare/Decriptare</h4>
            
            <div className="flow-section">
              <h5>📤 Trimitere Mesaj</h5>
              <ol className="flow-steps">
                <li>
                  <span className="step-icon">🔑</span>
                  <div>
                    <strong>Generare cheie AES</strong>
                    <p>Se genereaza o cheie AES de 256 biti aleatorie pentru acest mesaj</p>
                  </div>
                </li>
                <li>
                  <span className="step-icon">🔒</span>
                  <div>
                    <strong>Criptare continut cu AES</strong>
                    <p>Mesajul este criptat cu AES-256-CBC folosind cheia generata</p>
                  </div>
                </li>
                <li>
                  <span className="step-icon">📦</span>
                  <div>
                    <strong>Criptare cheie AES cu RSA</strong>
                    <p>Cheia AES este criptata cu cheia publica RSA a FIECARUI destinatar</p>
                  </div>
                </li>
                <li>
                  <span className="step-icon">💾</span>
                  <div>
                    <strong>Stocare in baza de date</strong>
                    <p>Se salveaza: mesaj_criptat + cheie_AES_criptata + IV</p>
                  </div>
                </li>
              </ol>
            </div>
            
            <div className="flow-section">
              <h5>📥 Primire Mesaj</h5>
              <ol className="flow-steps">
                <li>
                  <span className="step-icon">📨</span>
                  <div>
                    <strong>Primire date criptate</strong>
                    <p>Se primeste mesajul criptat, cheia AES criptata si IV</p>
                  </div>
                </li>
                <li>
                  <span className="step-icon">🔓</span>
                  <div>
                    <strong>Decriptare cheie AES cu RSA</strong>
                    <p>Cheia AES este decriptata cu cheia PRIVATA RSA proprie</p>
                  </div>
                </li>
                <li>
                  <span className="step-icon">📖</span>
                  <div>
                    <strong>Decriptare continut cu AES</strong>
                    <p>Mesajul este decriptat cu cheia AES obtinuta</p>
                  </div>
                </li>
              </ol>
            </div>
          </div>
        )}
        
        {/* DB Tab */}
        {activeTab === 'db' && (
          <div className="tab-content">
            <h4>Stocare in Baza de Date</h4>
            
            <p>
              Mesajele sunt stocate <strong>criptat</strong> in baza de date SQLite. 
              Chiar daca cineva acceseaza baza de date, nu poate citi mesajele fara 
              cheile private ale utilizatorilor.
            </p>
            
            <div className="db-schema">
              <h5>Schema tabelului `messages`</h5>
              <table className="schema-table">
                <thead>
                  <tr>
                    <th>Coloana</th>
                    <th>Tip</th>
                    <th>Descriere</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><code>id</code></td>
                    <td>INTEGER</td>
                    <td>ID unic mesaj</td>
                  </tr>
                  <tr>
                    <td><code>conversation_id</code></td>
                    <td>INTEGER</td>
                    <td>Referinta conversatie</td>
                  </tr>
                  <tr>
                    <td><code>sender_id</code></td>
                    <td>INTEGER</td>
                    <td>ID expeditor</td>
                  </tr>
                  <tr className="highlight">
                    <td><code>encrypted_content</code></td>
                    <td>TEXT</td>
                    <td>Continut criptat AES (base64)</td>
                  </tr>
                  <tr className="highlight">
                    <td><code>encrypted_aes_keys</code></td>
                    <td>TEXT</td>
                    <td>Chei AES criptate RSA (JSON)</td>
                  </tr>
                  <tr className="highlight">
                    <td><code>iv</code></td>
                    <td>VARCHAR(32)</td>
                    <td>Vector initializare (base64)</td>
                  </tr>
                  <tr>
                    <td><code>message_type</code></td>
                    <td>VARCHAR(20)</td>
                    <td>text/image/file</td>
                  </tr>
                  <tr>
                    <td><code>created_at</code></td>
                    <td>DATETIME</td>
                    <td>Data trimitere</td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div className="storage-note">
              <h5>⚠️ Important</h5>
              <p>
                Campul <code>encrypted_aes_keys</code> contine cheia AES criptata 
                pentru FIECARE participant:
              </p>
              <div className="code-example">
                <code>
                  {`{
  "user_1": "cheie_AES_criptata_RSA_user1_base64",
  "user_2": "cheie_AES_criptata_RSA_user2_base64"
}`}
                </code>
              </div>
              <p>
                Fiecare utilizator poate decripta doar cu cheia sa privata.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default CryptoInfoPanel;
