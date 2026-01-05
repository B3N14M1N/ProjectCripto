// src/components/Message/ImageAttachmentItem.js
// Componenta pentru afișarea unei imagini atașate
// Responsabilitate: decriptare și randare imagini cu preview

import React, { useState, useEffect } from 'react';
import { getIcon } from './FileIcons';
import './ImageAttachmentItem.css';

/**
 * Componenta pentru afișarea unei imagini atașate
 */
const ImageAttachmentItem = ({ 
  attachment, 
  privateKey,
  onLoadImage,
  onDownload,
  onImageClick,
  isOwn = false,
  preloadedData = null
}) => {
  const [imageData, setImageData] = useState(preloadedData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showOverlay, setShowOverlay] = useState(false);
  
  const DownloadIcon = getIcon('download');
  const ImageIcon = getIcon('image');
  
  // Încărcăm imaginea automat când avem cheia
  useEffect(() => {
    if (privateKey && !imageData && !loading && !error) {
      loadImage();
    }
  }, [privateKey, attachment.id]);
  
  // Actualizăm dacă primim date preîncărcate
  useEffect(() => {
    if (preloadedData) {
      setImageData(preloadedData);
    }
  }, [preloadedData]);
  
  const loadImage = async () => {
    if (!onLoadImage) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await onLoadImage(attachment.id);
      setImageData(data);
    } catch (err) {
      setError('Eroare la încărcarea imaginii');
      console.error('Error loading image:', err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleImageClick = () => {
    // Folosim callback-ul pentru a deschide viewer-ul în Message
    if (onImageClick && imageData) {
      onImageClick(attachment);
    }
  };
  
  const handleDownloadClick = (e) => {
    e.stopPropagation();
    if (onDownload) {
      onDownload(attachment);
    }
  };
  
  return (
    <div 
      className={`image-attachment-item ${isOwn ? 'own' : 'other'}`}
      onMouseEnter={() => setShowOverlay(true)}
      onMouseLeave={() => setShowOverlay(false)}
    >
      {loading ? (
        <div className="image-loading">
          <div className="spinner"></div>
          <span>Se decriptează imaginea...</span>
        </div>
      ) : error ? (
        <div className="image-error" onClick={loadImage}>
          <span>{error}</span>
          <button className="retry-btn">Reîncearcă</button>
        </div>
      ) : imageData ? (
        <>
          <img 
            src={imageData} 
            alt={attachment.file_name}
            className="decrypted-image"
            onClick={handleImageClick}
          />
          {showOverlay && (
            <div className="image-overlay">
              <button 
                className="download-image-btn"
                onClick={handleDownloadClick}
                title="Descarcă imaginea"
              >
                {DownloadIcon}
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="image-placeholder" onClick={loadImage}>
          {ImageIcon}
          <span>{attachment.file_name}</span>
          <button className="load-btn">Decriptează imaginea</button>
        </div>
      )}
    </div>
  );
};

export default ImageAttachmentItem;
