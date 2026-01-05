// src/components/Message/FilePreview.js
// Componenta pentru preview fișiere înainte de trimitere
// Responsabilitate: afișare preview pentru fișierele selectate

import React, { useState, useEffect } from 'react';
import { getFileIcon, formatFileSize, isImage } from '../../utils/fileUtils';
import { getIcon } from './FileIcons';
import './FilePreview.css';

/**
 * Preview pentru un singur fișier selectat
 */
export const FilePreviewItem = ({ file, onRemove }) => {
  const [preview, setPreview] = useState(null);
  const isImageFile = isImage(file.name);
  
  useEffect(() => {
    // Generăm preview pentru imagini
    if (isImageFile) {
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result);
      reader.readAsDataURL(file);
    }
    
    return () => setPreview(null);
  }, [file, isImageFile]);
  
  const iconType = getFileIcon(file.name);
  const Icon = getIcon(iconType);
  
  return (
    <div className="file-preview-item">
      {isImageFile && preview ? (
        <img src={preview} alt={file.name} className="preview-thumbnail" />
      ) : (
        <div className={`preview-icon ${iconType}`}>
          {Icon}
        </div>
      )}
      
      <div className="preview-info">
        <span className="preview-name" title={file.name}>
          {file.name.length > 20 ? file.name.substring(0, 17) + '...' : file.name}
        </span>
        <span className="preview-size">{formatFileSize(file.size)}</span>
      </div>
      
      <button 
        className="remove-btn"
        onClick={() => onRemove(file)}
        title="Elimină fișierul"
      >
        <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
          <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
        </svg>
      </button>
    </div>
  );
};

/**
 * Container pentru preview-ul fișierelor selectate
 */
export const FilesPreviewBar = ({ files, onRemoveFile, onClearAll }) => {
  if (!files || files.length === 0) return null;
  
  return (
    <div className="files-preview-bar">
      <div className="preview-header">
        <span className="preview-count">
          {files.length} fișier{files.length > 1 ? 'e' : ''} selectat{files.length > 1 ? 'e' : ''}
        </span>
        <button className="clear-all-btn" onClick={onClearAll}>
          Șterge tot
        </button>
      </div>
      <div className="preview-list">
        {files.map((file, index) => (
          <FilePreviewItem 
            key={`${file.name}-${index}`}
            file={file}
            onRemove={onRemoveFile}
          />
        ))}
      </div>
    </div>
  );
};

export default FilesPreviewBar;
