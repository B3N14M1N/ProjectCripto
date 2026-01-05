// src/components/Message/FileIcons.js
// Iconițe SVG pentru diferite tipuri de fișiere
// Responsabilitate: furnizare iconițe consistente

import React from 'react';

const FileIcons = {
  pdf: (
    <svg viewBox="0 0 24 24" fill="currentColor" className="file-icon pdf">
      <path d="M20 2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-8.5 7.5c0 .83-.67 1.5-1.5 1.5H9v2H7.5V7H10c.83 0 1.5.67 1.5 1.5v1zm5 2c0 .83-.67 1.5-1.5 1.5h-2.5V7H15c.83 0 1.5.67 1.5 1.5v3zm4-3H19v1h1.5V11H19v2h-1.5V7h3v1.5zM9 9.5h1v-1H9v1zM4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm10 5.5h1v-3h-1v3z"/>
    </svg>
  ),
  word: (
    <svg viewBox="0 0 24 24" fill="currentColor" className="file-icon word">
      <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 14h-3v3h-2v-3H8v-2h3v-3h2v3h3v2zm-3-7V3.5L18.5 9H13z"/>
    </svg>
  ),
  powerpoint: (
    <svg viewBox="0 0 24 24" fill="currentColor" className="file-icon powerpoint">
      <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14H8V7h4c2.21 0 4 1.79 4 4s-1.79 4-4 4zm0-2c1.1 0 2-.9 2-2s-.9-2-2-2h-2v4h2z"/>
    </svg>
  ),
  excel: (
    <svg viewBox="0 0 24 24" fill="currentColor" className="file-icon excel">
      <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-3 14h-2l-2-3-2 3H8l3-4.5L8 8h2l2 3 2-3h2l-3 4.5 3 4.5z"/>
    </svg>
  ),
  text: (
    <svg viewBox="0 0 24 24" fill="currentColor" className="file-icon text">
      <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
    </svg>
  ),
  image: (
    <svg viewBox="0 0 24 24" fill="currentColor" className="file-icon image">
      <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
    </svg>
  ),
  video: (
    <svg viewBox="0 0 24 24" fill="currentColor" className="file-icon video">
      <path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z"/>
    </svg>
  ),
  audio: (
    <svg viewBox="0 0 24 24" fill="currentColor" className="file-icon audio">
      <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
    </svg>
  ),
  file: (
    <svg viewBox="0 0 24 24" fill="currentColor" className="file-icon default">
      <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11z"/>
    </svg>
  ),
  download: (
    <svg viewBox="0 0 24 24" fill="currentColor" className="download-icon">
      <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
    </svg>
  )
};

/**
 * Obține iconița pentru un anumit tip
 */
export function getIcon(iconType) {
  return FileIcons[iconType] || FileIcons.file;
}

export default FileIcons;
