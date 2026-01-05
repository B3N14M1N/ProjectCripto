// src/components/Sidebar.js
// Componenta pentru sidebar-ul din stanga
// Contine: profil, cautare, lista conversatii

import React, { useState } from 'react';
import './Sidebar.css';

/**
 * Componenta Sidebar
 * 
 * Structura:
 * 1. Header: profil utilizator, setari
 * 2. Cautare: gasire utilizatori pentru conversatii noi
 * 3. Lista conversatii: ordonate dupa activitate
 */
function Sidebar({
  user,
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  onSearchUsers,
  onLogout,
  onShowCryptoInfo,
  onShowPrivateKeyModal,
  onDeleteConversation,
  loading
}) {
  // State pentru cautare
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showSearch, setShowSearch] = useState(false);
  // State pentru meniul contextual de stergere
  const [showDeleteMenu, setShowDeleteMenu] = useState(null);
  
  // Handler pentru cautare
  const handleSearch = async (query) => {
    setSearchQuery(query);
    
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }
    
    setIsSearching(true);
    try {
      const results = await onSearchUsers(query);
      setSearchResults(results);
    } catch (error) {
      console.error('Eroare la cautare:', error);
    } finally {
      setIsSearching(false);
    }
  };
  
  // Handler pentru selectarea unui utilizator din cautare
  const handleSelectUser = async (selectedUser) => {
    try {
      await onNewConversation([selectedUser.id]);
      setSearchQuery('');
      setSearchResults([]);
      setShowSearch(false);
    } catch (error) {
      console.error('Eroare:', error);
    }
  };
  
  // Formateaza timpul ultimului mesaj
  const formatTime = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    // Azi - afisam ora
    if (diff < 24 * 60 * 60 * 1000 && date.getDate() === now.getDate()) {
      return date.toLocaleTimeString('ro-RO', { hour: '2-digit', minute: '2-digit' });
    }
    
    // Ieri
    if (diff < 48 * 60 * 60 * 1000) {
      return 'Ieri';
    }
    
    // Mai vechi - afisam data
    return date.toLocaleDateString('ro-RO', { day: '2-digit', month: '2-digit' });
  };
  
  return (
    <div className="sidebar">
      {/* Header cu profil */}
      <div className="sidebar-header">
        <div className="profile-section">
          <div 
            className="avatar"
            style={{ backgroundColor: user?.avatar_color || '#3b82f6' }}
          >
            {user?.username?.charAt(0).toUpperCase()}
          </div>
          <div className="profile-info">
            <span className="profile-name">{user?.username}</span>
            <span className="profile-status">
              <span className="status-dot"></span>
              Online
            </span>
          </div>
        </div>
        
        <div className="header-actions">
          {/* Buton pentru info criptare */}
          <button 
            className="btn-icon" 
            onClick={onShowCryptoInfo}
            title="Informatii despre criptare"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
            </svg>
          </button>
          
          {/* Buton logout */}
          <button 
            className="btn-icon" 
            onClick={onLogout}
            title="Deconectare"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
            </svg>
          </button>
        </div>
      </div>
      
      {/* Sectiunea de cautare */}
      <div className="search-section">
        <div className="search-input-wrapper">
          <svg className="search-icon" viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
            <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
          </svg>
          <input
            type="text"
            className="search-input"
            placeholder="Cauta utilizatori..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            onFocus={() => setShowSearch(true)}
          />
          {searchQuery && (
            <button 
              className="search-clear" 
              onClick={() => {
                setSearchQuery('');
                setSearchResults([]);
              }}
            >
              ✕
            </button>
          )}
        </div>
        
        {/* Rezultate cautare */}
        {showSearch && searchQuery.length >= 2 && (
          <div className="search-results">
            {isSearching ? (
              <div className="search-loading">Se cauta...</div>
            ) : searchResults.length > 0 ? (
              searchResults.map(result => (
                <div
                  key={result.id}
                  className="search-result-item"
                  onClick={() => handleSelectUser(result)}
                >
                  <div 
                    className="avatar avatar-sm"
                    style={{ backgroundColor: result.avatar_color || '#3b82f6' }}
                  >
                    {result.username.charAt(0).toUpperCase()}
                  </div>
                  <div className="result-info">
                    <span className="result-name">{result.username}</span>
                    <span className="result-email">{result.email}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="search-empty">Niciun utilizator gasit</div>
            )}
          </div>
        )}
      </div>
      
      {/* Lista conversatii */}
      <div className="conversations-section">
        <h3 className="section-title">Conversatii</h3>
        
        {loading ? (
          <div className="conversations-loading">
            <div className="spinner"></div>
          </div>
        ) : conversations.length === 0 ? (
          <div className="conversations-empty">
            <p>Nicio conversatie</p>
            <p className="text-sm">Cauta un utilizator pentru a incepe</p>
          </div>
        ) : (
          <div className="conversations-list">
            {conversations.map(conv => (
              <div
                key={conv.id}
                className={`conversation-item ${conv.id === currentConversationId ? 'active' : ''}`}
                onClick={() => onSelectConversation(conv.id)}
                onContextMenu={(e) => {
                  e.preventDefault();
                  setShowDeleteMenu(conv.id);
                }}
              >
                <div 
                  className="avatar"
                  style={{ backgroundColor: conv.other_user?.avatar_color || '#3b82f6' }}
                >
                  {conv.name?.charAt(0).toUpperCase() || '?'}
                </div>
                
                <div className="conversation-info">
                  <div className="conversation-header">
                    <span className="conversation-name">{conv.name}</span>
                    <span className="conversation-time">
                      {conv.last_message && formatTime(conv.last_message.created_at)}
                    </span>
                  </div>
                  <div className="conversation-preview">
                    <span className="preview-text">
                      {conv.last_message ? (
                        <>
                          <svg viewBox="0 0 24 24" fill="currentColor" width="12" height="12" style={{marginRight: '4px', opacity: 0.6}}>
                            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
                          </svg>
                          Mesaj criptat
                        </>
                      ) : 'Conversatie noua'}
                    </span>
                    {conv.unread_count > 0 && (
                      <span className="badge">{conv.unread_count}</span>
                    )}
                  </div>
                </div>
                
                {/* Buton stergere - pozitionat absolut */}
                <button
                  className="btn-delete-conv"
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowDeleteMenu(showDeleteMenu === conv.id ? null : conv.id);
                  }}
                  title="Sterge conversatia"
                >
                  <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                    <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                  </svg>
                </button>
                
                {/* Meniu confirmare stergere */}
                {showDeleteMenu === conv.id && (
                  <div className="delete-menu" onClick={(e) => e.stopPropagation()}>
                    <p>Stergi conversatia?</p>
                    <div className="delete-menu-actions">
                      <button 
                        className="btn-confirm-delete"
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteConversation(conv.id);
                          setShowDeleteMenu(null);
                        }}
                      >
                        Da, sterge
                      </button>
                      <button 
                        className="btn-cancel-delete"
                        onClick={(e) => {
                          e.stopPropagation();
                          setShowDeleteMenu(null);
                        }}
                      >
                        Anuleaza
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* Footer cu info */}
      <div className="sidebar-footer">
        <button 
          className="encryption-badge-btn"
          onClick={onShowPrivateKeyModal}
          title="Configureaza cheia privata"
        >
          <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
          </svg>
          <span>Criptare end-to-end</span>
        </button>
      </div>
    </div>
  );
}

export default Sidebar;
