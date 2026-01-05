// src/components/Message/ImageViewer.js
// Componenta pentru vizualizarea imaginilor în overlay fullscreen
// Responsabilitate: afișare imagine mărită cu opțiuni de închidere și download

import React, { useEffect } from 'react';
import './ImageViewer.css';

/**
 * Overlay pentru vizualizarea imaginilor mărite
 */
const ImageViewer = ({ imageUrl, imageName, onClose, onDownload }) => {
  // Închide la ESC
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    
    document.addEventListener('keydown', handleEsc);
    // Prevenim scroll pe body
    document.body.style.overflow = 'hidden';
    
    return () => {
      document.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = '';
    };
  }, [onClose]);

  // Click pe backdrop închide viewer-ul
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="image-viewer-overlay" onClick={handleBackdropClick}>
      <div className="image-viewer-header">
        <span className="image-viewer-name">{imageName}</span>
        <div className="image-viewer-actions">
          {onDownload && (
            <button className="viewer-btn" onClick={onDownload} title="Descarcă">
              <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
              </svg>
            </button>
          )}
          <button className="viewer-btn close-btn" onClick={onClose} title="Închide (ESC)">
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>
      </div>
      
      <div className="image-viewer-content">
        <img 
          src={imageUrl} 
          alt={imageName}
          className="viewer-image"
        />
      </div>
    </div>
  );
};

export default ImageViewer;
