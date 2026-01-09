// src/pages/ChatPage.js
// Pagina principala de chat
// Contine sidebar cu conversatii si zona de mesaje

import React, { useState, useEffect, useContext, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AuthContext } from '../App';
import { chatAPI, authAPI, fileAPI } from '../services/api';
import { cryptoClient } from '../services/crypto';
import Sidebar from '../components/Sidebar';
import MessageArea from '../components/MessageArea';
import CryptoInfoPanel from '../components/CryptoInfoPanel';
import './ChatPage.css';

/**
 * Componenta principala pentru pagina de chat
 * 
 * Layout:
 * - Sidebar (stanga): lista conversatii, cautare, profil
 * - MessageArea (centru): mesajele conversatiei selectate
 * - CryptoInfoPanel (dreapta, optional): informatii despre criptare
 */
function ChatPage() {
  const { user, privateKey, logout, setPrivateKey } = useContext(AuthContext);
  const { conversationId } = useParams();
  const navigate = useNavigate();
  
  // State pentru conversatii si mesaje
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loadingConversations, setLoadingConversations] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  
  // State pentru UI
  const [showCryptoPanel, setShowCryptoPanel] = useState(false);
  const [showPrivateKeyModal, setShowPrivateKeyModal] = useState(false);
  const [tempPrivateKey, setTempPrivateKey] = useState('');
  const [isEditingKey, setIsEditingKey] = useState(false);
  
  // Referinta pentru polling
  const pollingRef = useRef(null);
  
  // Incarcam conversatiile la montare
  useEffect(() => {
    loadConversations();
    
    // Polling pentru conversatii noi (la fiecare 5 secunde)
    pollingRef.current = setInterval(() => {
      loadConversations(true);
    }, 5000);
    
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, []);
  
  // Incarcam mesajele cand se schimba conversatia
  useEffect(() => {
    if (conversationId) {
      loadConversation(conversationId);
      loadMessages(conversationId);
      
      // Polling pentru mesaje noi
      const messagePolling = setInterval(() => {
        loadMessages(conversationId, true);
      }, 3000);
      
      return () => clearInterval(messagePolling);
    } else {
      setCurrentConversation(null);
      setMessages([]);
    }
  }, [conversationId]);
  
  // Verificam daca avem cheia privata
  useEffect(() => {
    if (user && !privateKey) {
      setShowPrivateKeyModal(true);
    }
  }, [user, privateKey]);
  
  // Functie pentru incarcarea conversatiilor
  const loadConversations = async (silent = false) => {
    if (!silent) setLoadingConversations(true);
    try {
      const response = await chatAPI.getConversations();
      setConversations(response.data.conversations);
    } catch (error) {
      console.error('Eroare la incarcarea conversatiilor:', error);
    } finally {
      if (!silent) setLoadingConversations(false);
    }
  };
  
  // Functie pentru incarcarea unei conversatii specifice
  const loadConversation = async (convId) => {
    try {
      const response = await chatAPI.getConversation(convId);
      setCurrentConversation(response.data.conversation);
      // Marcam ca citita
      await chatAPI.markAsRead(convId);
      loadConversations(true); // Actualizam lista pentru badge
    } catch (error) {
      console.error('Eroare la incarcarea conversatiei:', error);
    }
  };
  
  // Functie pentru incarcarea mesajelor
  const loadMessages = async (convId, silent = false) => {
    if (!silent) setLoadingMessages(true);
    try {
      const response = await chatAPI.getMessages(convId);
      setMessages(response.data.messages);
    } catch (error) {
      console.error('Eroare la incarcarea mesajelor:', error);
    } finally {
      if (!silent) setLoadingMessages(false);
    }
  };
  
  // Functie pentru trimiterea unui mesaj - CRIPTARE CLIENT-SIDE (E2E)
  const sendMessage = async (content, messageType = 'text') => {
    if (!conversationId || !content.trim()) return;
    
    try {
      // 1. Obtinem cheile publice ale participantilor
      const keysResponse = await chatAPI.getConversationPublicKeys(conversationId);
      const publicKeys = keysResponse.data.public_keys;
      
      // 2. Criptam mesajul pe client
      const encryptedData = await cryptoClient.encryptMessage(content.trim(), publicKeys);
      
      // 3. Trimitem mesajul criptat la server
      const response = await chatAPI.sendEncryptedMessage(conversationId, {
        encrypted_content: encryptedData.encrypted_content,
        iv: encryptedData.iv,
        encrypted_aes_keys: encryptedData.encrypted_aes_keys,
        message_type: messageType
      });
      
      if (response.data.success) {
        // Adaugam mesajul nou la lista
        setMessages(prev => [...prev, response.data.message]);
        // Actualizam conversatiile
        loadConversations(true);
      }
    } catch (error) {
      console.error('Eroare la trimiterea mesajului:', error);
      throw error;
    }
  };
  
  // Functie pentru trimitere mesaj cu fisiere multiple
  const sendWithFiles = async (content, uploadedFiles) => {
    if (!conversationId || !uploadedFiles.length) return;
    
    try {
      // Mapam toate campurile necesare pentru backend
      const fileData = uploadedFiles.map(f => ({
        temp_id: f.temp_id,
        name: f.name,
        size: f.size,
        mime_type: f.mime_type,
        file_type: f.file_type,
        file_icon: f.file_icon,
        encrypted_path: f.encrypted_path,
        encrypted_aes_keys: f.encrypted_aes_keys,
        iv: f.iv
      }));
      
      const response = await fileAPI.sendWithFiles(conversationId, content, fileData);
      if (response.data.success) {
        setMessages(prev => [...prev, response.data.message]);
        loadConversations(true);
      }
      return response.data;
    } catch (error) {
      console.error('Eroare la trimitere cu fisiere:', error);
      throw error;
    }
  };
  
  // Functie pentru crearea unei conversatii noi
  const createConversation = async (participantIds) => {
    try {
      const response = await chatAPI.createConversation(participantIds);
      if (response.data.success) {
        loadConversations();
        navigate(`/chat/${response.data.conversation.id}`);
      }
      return response.data;
    } catch (error) {
      console.error('Eroare la crearea conversatiei:', error);
      throw error;
    }
  };
  
  // Functie pentru cautarea utilizatorilor
  const searchUsers = async (query) => {
    try {
      const response = await authAPI.searchUsers(query);
      return response.data.users;
    } catch (error) {
      console.error('Eroare la cautare:', error);
      return [];
    }
  };
  
  // Functie pentru stergerea unei conversatii
  const deleteConversation = async (convId) => {
    try {
      const response = await chatAPI.deleteConversation(convId);
      if (response.data.success) {
        // Actualizam lista de conversatii
        loadConversations();
        // Daca stergem conversatia curenta, navigam la pagina de chat fara ID
        if (conversationId && parseInt(conversationId) === convId) {
          navigate('/chat');
        }
      }
    } catch (error) {
      console.error('Eroare la stergerea conversatiei:', error);
    }
  };
  
  // Functie pentru decriptarea unui mesaj - CLIENT-SIDE (End-to-End)
  // userPrivateKey este pasat de componenta Message pentru compatibilitate,
  // dar folosim privateKey din context pentru consistenta
  const decryptMessage = async (messageId, userPrivateKey) => {
    const keyToUse = userPrivateKey || privateKey;
    
    if (!keyToUse) {
      setShowPrivateKeyModal(true);
      return null;
    }
    
    try {
      // Gasim mesajul in lista de mesaje
      const message = messages.find(m => m.id === messageId);
      if (!message) {
        throw new Error('Mesajul nu a fost gasit');
      }
      
      // Decriptam pe client folosind Web Crypto API
      const decryptedContent = await cryptoClient.decryptMessage(
        message.encrypted_content,
        message.encrypted_aes_key,
        message.iv,
        keyToUse
      );
      
      return decryptedContent;
    } catch (error) {
      console.error('Eroare la decriptare client-side:', error);
      throw error;
    }
  };
  
  // Handler pentru salvarea cheii private
  const handleSavePrivateKey = () => {
    if (tempPrivateKey.trim()) {
      setPrivateKey(tempPrivateKey.trim());
      setShowPrivateKeyModal(false);
      setTempPrivateKey('');
      setIsEditingKey(false);
    }
  };
  
  // Handler pentru activarea modului de editare
  const handleStartEditKey = () => {
    setTempPrivateKey(privateKey || '');
    setIsEditingKey(true);
  };
  
  // Handler pentru anularea editarii
  const handleCancelEditKey = () => {
    setTempPrivateKey('');
    setIsEditingKey(false);
  };
  
  // Handler pentru inchiderea modalului
  const handleCloseKeyModal = () => {
    setShowPrivateKeyModal(false);
    setTempPrivateKey('');
    setIsEditingKey(false);
  };
  
  return (
    <div className="chat-page">
      {/* Sidebar cu conversatii */}
      <Sidebar
        user={user}
        conversations={conversations}
        currentConversationId={conversationId ? parseInt(conversationId) : null}
        onSelectConversation={(id) => navigate(`/chat/${id}`)}
        onNewConversation={createConversation}
        onSearchUsers={searchUsers}
        onLogout={logout}
        onShowCryptoInfo={() => setShowCryptoPanel(!showCryptoPanel)}
        onShowPrivateKeyModal={() => setShowPrivateKeyModal(true)}
        onDeleteConversation={deleteConversation}
        loading={loadingConversations}
      />
      
      {/* Zona de mesaje */}
      <MessageArea
        conversation={currentConversation}
        messages={messages}
        currentUserId={user?.id}
        privateKey={privateKey}
        onSendMessage={sendMessage}
        onSendWithFiles={sendWithFiles}
        onDecryptMessage={decryptMessage}
        onShowKeyModal={() => setShowPrivateKeyModal(true)}
        loading={loadingMessages}
      />
      
      {/* Panel informativ despre criptare */}
      {showCryptoPanel && (
        <CryptoInfoPanel
          conversation={currentConversation}
          onClose={() => setShowCryptoPanel(false)}
        />
      )}
      
      {/* Modal pentru cheia privata */}
      {showPrivateKeyModal && (
        <div className="modal-overlay" onClick={handleCloseKeyModal}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Cheia Privata RSA</h3>
              <button 
                className="btn-icon" 
                onClick={handleCloseKeyModal}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <p className="text-sm text-muted" style={{marginBottom: '16px'}}>
                Cheia privata este necesara pentru a decripta mesajele primite.
                Aceasta este pastrata doar in browser-ul tau.
              </p>
              
              {privateKey && !isEditingKey ? (
                <div>
                  <p className="success-message" style={{marginBottom: '16px'}}>
                    ✓ Cheia privata este configurata
                  </p>
                  <div className="input-group">
                    <label className="input-label">Cheia ta privata:</label>
                    <textarea
                      className="input private-key-textarea"
                      value={privateKey}
                      readOnly
                      rows={12}
                      style={{
                        fontFamily: 'monospace', 
                        fontSize: '11px',
                        resize: 'vertical',
                        minHeight: '200px',
                        maxHeight: '400px'
                      }}
                    />
                  </div>
                </div>
              ) : (
                <div className="input-group">
                  <label className="input-label">
                    {isEditingKey ? 'Editeaza cheia privata RSA:' : 'Introdu cheia privata RSA:'}
                  </label>
                  <textarea
                    className="input private-key-textarea"
                    value={tempPrivateKey}
                    onChange={(e) => setTempPrivateKey(e.target.value)}
                    placeholder="-----BEGIN PRIVATE KEY-----&#10;...&#10;-----END PRIVATE KEY-----"
                    rows={12}
                    style={{
                      fontFamily: 'monospace', 
                      fontSize: '11px',
                      resize: 'vertical',
                      minHeight: '200px',
                      maxHeight: '400px'
                    }}
                  />
                  <p className="text-sm text-muted" style={{marginTop: '8px'}}>
                    {isEditingKey 
                      ? 'Atentie: Modificarea cheii poate afecta decriptarea mesajelor vechi.' 
                      : 'Ai primit cheia privata la inregistrare. Daca ai pierdut-o, nu vei putea decripta mesajele vechi.'}
                  </p>
                </div>
              )}
            </div>
            <div className="modal-footer">
              {privateKey && !isEditingKey ? (
                <button 
                  className="btn btn-secondary"
                  onClick={handleStartEditKey}
                >
                  Modifica cheia
                </button>
              ) : (
                <>
                  <button 
                    className="btn btn-primary"
                    onClick={handleSavePrivateKey}
                    disabled={!tempPrivateKey.trim()}
                  >
                    Salveaza cheia
                  </button>
                  {isEditingKey && (
                    <button 
                      className="btn btn-secondary"
                      onClick={handleCancelEditKey}
                    >
                      Anuleaza
                    </button>
                  )}
                </>
              )}
              <button 
                className="btn btn-secondary"
                onClick={handleCloseKeyModal}
              >
                Inchide
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatPage;
