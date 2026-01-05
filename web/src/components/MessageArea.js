// src/components/MessageArea.js
// Componenta pentru zona de mesaje din centru
// Afiseaza mesajele si permite trimiterea de mesaje noi

import React, { useState, useRef, useEffect } from 'react';
import './MessageArea.css';

/**
 * Componenta MessageArea
 * 
 * Structura:
 * 1. Header: informatii conversatie
 * 2. Lista mesaje: scrollabila, mesaje noi jos
 * 3. Input: trimitere mesaj, atasare fisiere
 */
function MessageArea({
  conversation,
  messages,
  currentUserId,
  privateKey,
  onSendMessage,
  onUploadFile,
  onDecryptMessage,
  onShowKeyModal,
  loading
}) {
  // State pentru input
  const [messageInput, setMessageInput] = useState('');
  const [sending, setSending] = useState(false);
  const [decryptedMessages, setDecryptedMessages] = useState({});
  const [decrypting, setDecrypting] = useState({});
  
  // Referinte
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  
  // Scroll la ultimul mesaj cand se adauga mesaje noi
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  // Handler pentru trimitere mesaj
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!messageInput.trim() || sending) return;
    
    setSending(true);
    try {
      await onSendMessage(messageInput.trim());
      setMessageInput('');
    } catch (error) {
      console.error('Eroare:', error);
    } finally {
      setSending(false);
    }
  };
  
  // Handler pentru decriptare mesaj
  const handleDecrypt = async (messageId) => {
    if (!privateKey) {
      onShowKeyModal();
      return;
    }
    
    if (decryptedMessages[messageId]) return; // Deja decriptat
    
    setDecrypting(prev => ({ ...prev, [messageId]: true }));
    try {
      const content = await onDecryptMessage(messageId);
      setDecryptedMessages(prev => ({ ...prev, [messageId]: content }));
    } catch (error) {
      console.error('Eroare la decriptare:', error);
      setDecryptedMessages(prev => ({ ...prev, [messageId]: 'Eroare la decriptare' }));
    } finally {
      setDecrypting(prev => ({ ...prev, [messageId]: false }));
    }
  };
  
  // Handler pentru upload fisier
  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setSending(true);
    try {
      await onUploadFile(file);
    } catch (error) {
      console.error('Eroare upload:', error);
    } finally {
      setSending(false);
      fileInputRef.current.value = '';
    }
  };
  
  // Formateaza ora mesajului
  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('ro-RO', { hour: '2-digit', minute: '2-digit' });
  };
  
  // Afisare cand nu e selectata o conversatie
  if (!conversation) {
    return (
      <div className="message-area empty-state">
        <div className="empty-content">
          <div className="empty-icon">
            <svg viewBox="0 0 24 24" fill="currentColor" width="64" height="64">
              <path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/>
            </svg>
          </div>
          <h2>Bine ai venit la SecureChat</h2>
          <p>Selecteaza o conversatie sau cauta un utilizator pentru a incepe</p>
          
          <div className="crypto-info-card">
            <h4>Cum functioneaza criptarea?</h4>
            <div className="info-steps">
              <div className="info-step">
                <span className="step-number">1</span>
                <span className="step-text">Mesajul tau este criptat cu <strong>AES-256</strong></span>
              </div>
              <div className="info-step">
                <span className="step-number">2</span>
                <span className="step-text">Cheia AES este criptata cu <strong>RSA</strong> pentru destinatar</span>
              </div>
              <div className="info-step">
                <span className="step-number">3</span>
                <span className="step-text">Doar destinatarul poate decripta cu cheia sa privata</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="message-area">
      {/* Header conversatie */}
      <div className="message-header">
        <div className="header-info">
          <div 
            className="avatar"
            style={{ backgroundColor: conversation.other_user?.avatar_color || '#3b82f6' }}
          >
            {conversation.name?.charAt(0).toUpperCase()}
          </div>
          <div className="header-text">
            <span className="header-name">{conversation.name}</span>
            <span className="header-status">
              <svg viewBox="0 0 24 24" fill="currentColor" width="12" height="12">
                <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
              </svg>
              Mesaje criptate end-to-end
            </span>
          </div>
        </div>
      </div>
      
      {/* Lista mesaje */}
      <div className="messages-container">
        {loading ? (
          <div className="messages-loading">
            <div className="spinner"></div>
          </div>
        ) : messages.length === 0 ? (
          <div className="messages-empty">
            <p>Niciun mesaj inca</p>
            <p className="text-sm">Trimite primul mesaj pentru a incepe conversatia</p>
          </div>
        ) : (
          <div className="messages-list">
            {messages.map((message, index) => {
              const isOwn = message.sender_id === currentUserId;
              const showAvatar = !isOwn && (index === 0 || messages[index - 1]?.sender_id !== message.sender_id);
              const isDecrypted = decryptedMessages[message.id];
              const isDecrypting = decrypting[message.id];
              
              return (
                <div 
                  key={message.id} 
                  className={`message ${isOwn ? 'own' : 'other'}`}
                >
                  {!isOwn && showAvatar && (
                    <div 
                      className="avatar avatar-sm"
                      style={{ backgroundColor: message.sender_avatar_color || '#3b82f6' }}
                    >
                      {message.sender_username?.charAt(0).toUpperCase()}
                    </div>
                  )}
                  {!isOwn && !showAvatar && <div className="avatar-placeholder"></div>}
                  
                  <div className="message-content">
                    {!isOwn && showAvatar && (
                      <span className="message-sender">{message.sender_username}</span>
                    )}
                    
                    <div className="message-bubble">
                      {isDecrypted ? (
                        <p className="message-text">{isDecrypted}</p>
                      ) : (
                        <div className="encrypted-content">
                          <div className="encrypted-preview">
                            <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
                              <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
                            </svg>
                            <span>Mesaj criptat</span>
                          </div>
                          <button 
                            className="decrypt-btn"
                            onClick={() => handleDecrypt(message.id)}
                            disabled={isDecrypting}
                          >
                            {isDecrypting ? 'Se decripteaza...' : 'Decripteaza'}
                          </button>
                        </div>
                      )}
                      
                      <div className="message-meta">
                        <span className="message-time">{formatTime(message.created_at)}</span>
                        {isOwn && (
                          <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14" className="sent-icon">
                            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                          </svg>
                        )}
                      </div>
                    </div>
                    
                    {/* Indicator criptare (tooltip) */}
                    <div className="crypto-tooltip">
                      <span className="encryption-indicator aes">AES-256</span>
                      <div className="tooltip-content">
                        <h4>Despre acest mesaj</h4>
                        <p>Continut criptat cu: <strong>AES-256-CBC</strong></p>
                        <p>Cheie schimbata cu: <strong>RSA-2048</strong></p>
                        <p>IV: {message.iv?.substring(0, 16)}...</p>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      
      {/* Input mesaj */}
      <div className="message-input-container">
        <form onSubmit={handleSendMessage} className="message-form">
          {/* Buton atasare fisier */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            style={{ display: 'none' }}
            accept="image/*,.pdf,.doc,.docx,.txt"
          />
          <button 
            type="button" 
            className="btn-icon attach-btn"
            onClick={() => fileInputRef.current?.click()}
            disabled={sending}
            title="Ataseaza fisier"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" width="22" height="22">
              <path d="M16.5 6v11.5c0 2.21-1.79 4-4 4s-4-1.79-4-4V5c0-1.38 1.12-2.5 2.5-2.5s2.5 1.12 2.5 2.5v10.5c0 .55-.45 1-1 1s-1-.45-1-1V6H10v9.5c0 1.38 1.12 2.5 2.5 2.5s2.5-1.12 2.5-2.5V5c0-2.21-1.79-4-4-4S7 2.79 7 5v12.5c0 3.04 2.46 5.5 5.5 5.5s5.5-2.46 5.5-5.5V6h-1.5z"/>
            </svg>
          </button>
          
          {/* Input text */}
          <input
            type="text"
            className="message-input"
            value={messageInput}
            onChange={(e) => setMessageInput(e.target.value)}
            placeholder="Scrie un mesaj securizat..."
            disabled={sending}
          />
          
          {/* Buton trimitere */}
          <button 
            type="submit" 
            className="btn btn-primary send-btn"
            disabled={!messageInput.trim() || sending}
          >
            {sending ? (
              <div className="spinner" style={{width: '18px', height: '18px'}}></div>
            ) : (
              <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
              </svg>
            )}
          </button>
        </form>
        
        {/* Info despre criptare */}
        <div className="input-info">
          <svg viewBox="0 0 24 24" fill="currentColor" width="12" height="12">
            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
          </svg>
          <span>Mesajele sunt criptate automat cu AES-256 si RSA-2048</span>
        </div>
      </div>
    </div>
  );
}

export default MessageArea;
