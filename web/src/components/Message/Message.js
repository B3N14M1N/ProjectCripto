// src/components/Message/Message.js
// Componenta pentru afișarea unui singur mesaj

import React, { useState, useEffect } from 'react';
import { fileAPI } from '../../services/api';
import { cryptoClient } from '../../services/crypto';
import { isImage } from '../../utils/fileUtils';
import FileAttachmentItem from './FileAttachmentItem';
import ImageAttachmentItem from './ImageAttachmentItem';
import ImageViewer from './ImageViewer';
import './Message.css';

// Formatează timestamp-ul
const formatTime = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  return date.toLocaleTimeString('ro-RO', { hour: '2-digit', minute: '2-digit' });
};

/**
 * Componenta pentru un singur mesaj
 */
const Message = ({ message, isOwn, privateKey, onDecrypt, decryptedContent, onShowKeyModal }) => {
  const [isDecrypting, setIsDecrypting] = useState(false);
  const [localDecrypted, setLocalDecrypted] = useState(null);
  const [downloadingFile, setDownloadingFile] = useState(null);
  const [loadedImages, setLoadedImages] = useState({});
  const [viewingImage, setViewingImage] = useState(null);
  const [showInfo, setShowInfo] = useState(false);

  const content = localDecrypted || decryptedContent || null;
  const hasText = content && content.trim().length > 0;
  const hasAttachments = message.attachments && message.attachments.length > 0;

  // Separăm imaginile de alte fișiere
  const images = hasAttachments 
    ? message.attachments.filter(a => isImage(a.file_name))
    : [];
  const files = hasAttachments 
    ? message.attachments.filter(a => !isImage(a.file_name))
    : [];

  // Decriptare automată când primim cheia
  useEffect(() => {
    if (privateKey && !content && !isDecrypting && message.encrypted_content) {
      decryptMessage();
    }
  }, [privateKey, message.id]);

  const decryptMessage = async () => {
    if (!onDecrypt) return;
    setIsDecrypting(true);
    try {
      const decrypted = await onDecrypt(message.id, privateKey);
      setLocalDecrypted(decrypted);
    } catch (err) {
      console.error('Decrypt error:', err);
      setLocalDecrypted('[Eroare la decriptare]');
    } finally {
      setIsDecrypting(false);
    }
  };

  // Handler pentru butonul de decriptare manuală
  const handleManualDecrypt = () => {
    if (onShowKeyModal) {
      onShowKeyModal();
    }
  };

  // Handler download fișier - CLIENT-SIDE DECRYPTION (E2E)
  const handleDownload = async (attachment) => {
    if (!privateKey) {
      alert('Nu ai cheia privată pentru a decripta fișierul');
      return;
    }

    setDownloadingFile(attachment.id);
    try {
      // 1. Obtinem metadatele (cheia AES criptata, IV)
      const metaResponse = await fileAPI.getAttachmentMeta(attachment.id);
      const { encrypted_aes_key, iv, file_name, file_mime_type } = metaResponse.data;
      
      // 2. Descarcam fisierul criptat
      const encryptedResponse = await fileAPI.downloadEncrypted(attachment.id);
      const encryptedData = encryptedResponse.data; // ArrayBuffer
      
      // 3. Decriptam pe client
      const decryptedData = await cryptoClient.decryptFile(
        encryptedData,
        encrypted_aes_key,
        iv,
        privateKey
      );
      
      // 4. Cream blob si downloadam
      const blob = new Blob([decryptedData], { type: file_mime_type || 'application/octet-stream' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = file_name || attachment.file_name || 'file';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download error:', err);
      alert('Eroare la descărcarea fișierului: ' + (err.message || 'Verifică cheia privată'));
    } finally {
      setDownloadingFile(null);
    }
  };

  // Handler pentru încărcarea imaginilor - CLIENT-SIDE DECRYPTION (E2E)
  const handleLoadImage = async (attachmentId) => {
    if (!privateKey) {
      throw new Error('Nu ai cheia privată');
    }
    
    try {
      // 1. Obtinem metadatele (cheia AES criptata, IV)
      const metaResponse = await fileAPI.getAttachmentMeta(attachmentId);
      const { encrypted_aes_key, iv, file_mime_type } = metaResponse.data;
      
      // 2. Descarcam imaginea criptata
      const encryptedResponse = await fileAPI.downloadEncrypted(attachmentId);
      const encryptedData = encryptedResponse.data; // ArrayBuffer
      
      // 3. Decriptam pe client
      const decryptedData = await cryptoClient.decryptFile(
        encryptedData,
        encrypted_aes_key,
        iv,
        privateKey
      );
      
      // 4. Cream blob URL pentru afisare
      const blob = new Blob([decryptedData], { type: file_mime_type || 'image/jpeg' });
      const dataUrl = URL.createObjectURL(blob);
      setLoadedImages(prev => ({ ...prev, [attachmentId]: dataUrl }));
      return dataUrl;
    } catch (err) {
      console.error('Error loading image:', err);
      throw err;
    }
  };

  // Handler pentru click pe imagine
  const handleImageClick = (attachment) => {
    const imageUrl = loadedImages[attachment.id];
    if (imageUrl) {
      setViewingImage({
        url: imageUrl,
        name: attachment.file_name
      });
    }
  };

  // Verificăm dacă mesajul este criptat și nu avem cheia
  const isEncryptedWithoutKey = !privateKey && message.encrypted_content && !content;

  return (
    <div className={`message-wrapper ${isOwn ? 'own' : 'other'}`}>
      {/* Conținutul mesajului */}
      <div className="message-content">
        {/* Bubble pentru text */}
        {(hasText || isDecrypting || isEncryptedWithoutKey || (!hasAttachments && !content)) && (
          <div className={`message-bubble ${isOwn ? 'own' : 'other'}`}>
            {isDecrypting ? (
              <div className="decrypting-indicator">
                <div className="decrypt-spinner"></div>
                <span>Se decriptează...</span>
              </div>
            ) : isEncryptedWithoutKey ? (
              <div className="encrypted-message">
                <div className="encrypted-icon">
                  <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                    <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
                  </svg>
                </div>
                <span className="encrypted-text">Mesaj criptat</span>
                <button className="decrypt-btn" onClick={handleManualDecrypt}>
                  Decriptează
                </button>
              </div>
            ) : content ? (
              <p className="message-text">{content}</p>
            ) : (
              <p className="message-text-muted">Mesaj criptat</p>
            )}
          </div>
        )}

        {/* Atașamente - doar dacă avem cheia privată sau mesajul e decriptat */}
        {!isEncryptedWithoutKey && (
          <>
            {/* Atașamente - imagini */}
            {images.map(img => (
              <ImageAttachmentItem
                key={img.id}
                attachment={img}
                privateKey={privateKey}
                onLoadImage={handleLoadImage}
                onDownload={handleDownload}
                onImageClick={handleImageClick}
                isOwn={isOwn}
                preloadedData={loadedImages[img.id]}
              />
            ))}

            {/* Atașamente - fișiere */}
            {files.map(file => (
              <FileAttachmentItem
                key={file.id}
                attachment={file}
                onDownload={handleDownload}
                downloading={downloadingFile === file.id}
                isOwn={isOwn}
              />
            ))}
          </>
        )}
      </div>

      {/* Footer: timp + info */}
      <div className={`message-footer ${isOwn ? 'own' : 'other'}`}>
        <span className="message-time">{formatTime(message.created_at)}</span>
        
        <div 
          className="info-trigger"
          onMouseEnter={() => setShowInfo(true)}
          onMouseLeave={() => setShowInfo(false)}
        >
          <span className="crypto-badge">AES-256</span>
          
          {showInfo && (
            <div className={`info-popup ${isOwn ? 'right' : 'left'}`}>
              <div className="info-title">Despre acest mesaj</div>
              <div className="info-row">
                <span>Algoritm:</span>
                <span>AES-256-CBC</span>
              </div>
              <div className="info-row">
                <span>Schimb chei:</span>
                <span>RSA-2048</span>
              </div>
              {message.iv && (
                <div className="info-row">
                  <span>IV:</span>
                  <span className="mono">{message.iv.substring(0, 12)}...</span>
                </div>
              )}
              {hasAttachments && (
                <div className="info-row">
                  <span>Atașamente:</span>
                  <span>{message.attachments.length} fișier{message.attachments.length > 1 ? 'e' : ''}</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Image Viewer Overlay */}
      {viewingImage && (
        <ImageViewer
          imageUrl={viewingImage.url}
          imageName={viewingImage.name}
          onClose={() => setViewingImage(null)}
        />
      )}
    </div>
  );
};

export default Message;
