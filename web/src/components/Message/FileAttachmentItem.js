// src/components/Message/FileAttachmentItem.js
// Componenta pentru afișarea unui fișier atașat (non-imagine)
// Responsabilitate: randarea fișierelor cu iconiță și opțiune download

import React, { useState } from 'react';
import { getFileIcon, formatFileSize } from '../../utils/fileUtils';
import { getIcon } from './FileIcons';
import './FileAttachmentItem.css';

/**
 * Componenta pentru afișarea unui fișier atașat
 */
const FileAttachmentItem = ({ 
  attachment, 
  onDownload, 
  downloading = false,
  isOwn = false 
}) => {
  const [isHovered, setIsHovered] = useState(false);
  
  // Determinăm iconița bazat pe extensia fișierului
  const iconType = getFileIcon(attachment.file_name);
  const Icon = getIcon(iconType);
  const DownloadIcon = getIcon('download');
  
  const handleClick = () => {
    if (!downloading && onDownload) {
      onDownload(attachment);
    }
  };
  
  return (
    <div 
      className={`file-attachment-item ${isOwn ? 'own' : 'other'} ${isHovered ? 'hovered' : ''}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleClick}
    >
      <div className={`file-icon-wrapper ${iconType}`}>
        {Icon}
      </div>
      
      <div className="file-info">
        <span className="file-name" title={attachment.file_name}>
          {attachment.file_name}
        </span>
        <span className="file-size">
          {formatFileSize(attachment.file_size)}
        </span>
      </div>
      
      <div className={`download-button ${downloading ? 'downloading' : ''}`}>
        {downloading ? (
          <div className="spinner-small"></div>
        ) : (
          DownloadIcon
        )}
      </div>
    </div>
  );
};

export default FileAttachmentItem;
