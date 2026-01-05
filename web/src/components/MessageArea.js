// src/components/MessageArea.js
// Componenta principală pentru zona de mesaje
// Responsabilitate: orchestrare mesaje, input, și preview fișiere

import React, { useState, useEffect, useRef } from 'react';
import { Message, FilesPreviewBar } from './Message';
import { fileAPI } from '../services/api';
import './MessageArea.css';

/**
 * Componenta pentru zona de mesaje din chat
 */
const MessageArea = ({
  conversation,
  messages = [],
  currentUserId,
  privateKey,
  onDecryptMessage,
  onSendMessage,
  onSendWithFiles,
  decryptedMessages = {},
  loading = false,
  onShowKeyModal
}) => {
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const [inputText, setInputText] = useState('');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isSending, setIsSending] = useState(false);
  const lastMessageCountRef = useRef(0);
  const lastConversationIdRef = useRef(null);

  // Scroll la jos doar la: 1) prima încărcare, 2) schimbare conversație, 3) mesaj propriu nou
  useEffect(() => {
    const isNewConversation = lastConversationIdRef.current !== conversation?.id;
    const isNewMessage = messages.length > lastMessageCountRef.current;
    const lastMessage = messages[messages.length - 1];
    const isOwnNewMessage = isNewMessage && lastMessage?.sender_id === currentUserId;

    if (isNewConversation || isOwnNewMessage) {
      messagesEndRef.current?.scrollIntoView({ behavior: isNewConversation ? 'auto' : 'smooth' });
    }

    lastConversationIdRef.current = conversation?.id;
    lastMessageCountRef.current = messages.length;
  }, [messages, conversation?.id, currentUserId]);

  // Handler pentru selectarea fișierelor
  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    setSelectedFiles(prev => [...prev, ...files]);
    e.target.value = '';
  };

  const handleRemoveFile = (fileToRemove) => {
    setSelectedFiles(prev => prev.filter(f => f !== fileToRemove));
  };

  const handleClearFiles = () => {
    setSelectedFiles([]);
  };

  // Trimitere mesaj
  const handleSend = async () => {
    const hasText = inputText.trim().length > 0;
    const hasFiles = selectedFiles.length > 0;

    if (!hasText && !hasFiles) return;
    if (!conversation) return;

    setIsSending(true);
    try {
      if (hasFiles) {
        // 1. Uploadăm toate fișierele
        const uploadResponse = await fileAPI.uploadFiles(conversation.id, selectedFiles);
        
        if (uploadResponse.data.success && uploadResponse.data.uploaded_files) {
          // 2. Trimitem mesajul cu fișierele uploadate
          await onSendWithFiles(inputText.trim(), uploadResponse.data.uploaded_files);
        } else {
          throw new Error('Upload failed');
        }
      } else {
        // Doar text
        await onSendMessage(inputText.trim());
      }
      
      setInputText('');
      setSelectedFiles([]);
    } catch (err) {
      console.error('Send error:', err);
      alert('Eroare la trimiterea mesajului: ' + (err.message || 'Eroare necunoscută'));
    } finally {
      setIsSending(false);
    }
  };

  // Enter pentru trimitere
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Empty state când nu e selectată o conversație
  if (!conversation) {
    return (
      <div className="message-area empty-state">
        <div className="empty-conversation">
          <svg viewBox="0 0 24 24" fill="currentColor" width="64" height="64">
            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
          </svg>
          <h3>Selectează o conversație</h3>
          <p>Alege o conversație din sidebar sau începe una nouă</p>
        </div>
      </div>
    );
  }

  return (
    <div className="message-area">
      {/* Header conversație - simplu */}
      <div className="chat-header">
        <span className="chat-partner-name">
          {conversation.name || conversation.other_participant?.username || 'Conversație'}
        </span>
        <span className="encryption-status">
          <svg viewBox="0 0 24 24" fill="currentColor" width="12" height="12">
            <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
          </svg>
          End-to-end encrypted
        </span>
      </div>

      {/* Lista mesaje */}
      <div className="messages-container">
        {loading ? (
          <div className="loading-messages">
            <div className="loading-spinner"></div>
            <span>Se încarcă mesajele...</span>
          </div>
        ) : messages.length === 0 ? (
          <div className="empty-messages">
            <span>Nu există mesaje încă.</span>
            <span className="empty-hint">Trimite primul mesaj!</span>
          </div>
        ) : (
          messages.map(msg => (
            <Message
              key={msg.id}
              message={msg}
              isOwn={msg.sender_id === currentUserId}
              privateKey={privateKey}
              onDecrypt={onDecryptMessage}
              decryptedContent={decryptedMessages[msg.id]}
              onShowKeyModal={onShowKeyModal}
            />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Preview fișiere selectate */}
      <FilesPreviewBar
        files={selectedFiles}
        onRemoveFile={handleRemoveFile}
        onClearAll={handleClearFiles}
      />

      {/* Input zona */}
      <div className="message-input-area">
        <button
          className="attach-btn"
          onClick={() => fileInputRef.current?.click()}
          title="Atașează fișiere"
        >
          <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
            <path d="M16.5 6v11.5c0 2.21-1.79 4-4 4s-4-1.79-4-4V5c0-1.38 1.12-2.5 2.5-2.5s2.5 1.12 2.5 2.5v10.5c0 .55-.45 1-1 1s-1-.45-1-1V6H10v9.5c0 1.38 1.12 2.5 2.5 2.5s2.5-1.12 2.5-2.5V5c0-2.21-1.79-4-4-4S7 2.79 7 5v12.5c0 3.04 2.46 5.5 5.5 5.5s5.5-2.46 5.5-5.5V6h-1.5z"/>
          </svg>
        </button>
        
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          multiple
          style={{ display: 'none' }}
        />
        
        <textarea
          className="message-input"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Scrie un mesaj..."
          rows={1}
        />
        
        <button
          className="send-btn"
          onClick={handleSend}
          disabled={isSending || (!inputText.trim() && selectedFiles.length === 0)}
        >
          {isSending ? (
            <div className="sending-spinner"></div>
          ) : (
            <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          )}
        </button>
      </div>
    </div>
  );
};

export default MessageArea;
