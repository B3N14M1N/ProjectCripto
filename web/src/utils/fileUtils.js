// src/utils/fileUtils.js
// Utilități pentru gestiunea tipurilor de fișiere
// SINGLE SOURCE OF TRUTH pentru extensii și tipuri de fișiere

/**
 * Mapare extensii -> tip fișier
 * Tipuri posibile: image, video, audio, document, other
 */
const EXTENSION_TO_TYPE = {
  // Imagini
  'jpg': 'image',
  'jpeg': 'image',
  'png': 'image',
  'gif': 'image',
  'webp': 'image',
  'svg': 'image',
  'bmp': 'image',
  'ico': 'image',
  
  // Video
  'mp4': 'video',
  'webm': 'video',
  'avi': 'video',
  'mov': 'video',
  'mkv': 'video',
  'wmv': 'video',
  'flv': 'video',
  
  // Audio
  'mp3': 'audio',
  'wav': 'audio',
  'ogg': 'audio',
  'flac': 'audio',
  'm4a': 'audio',
  'aac': 'audio',
  'wma': 'audio',
  
  // Documente
  'pdf': 'document',
  'doc': 'document',
  'docx': 'document',
  'xls': 'document',
  'xlsx': 'document',
  'ppt': 'document',
  'pptx': 'document',
  'txt': 'document',
  'rtf': 'document',
  'odt': 'document',
  'ods': 'document',
  'odp': 'document',
  'csv': 'document',
};

/**
 * Mapare extensii -> iconiță specifică
 */
const EXTENSION_TO_ICON = {
  // PDF
  'pdf': 'pdf',
  
  // Word
  'doc': 'word',
  'docx': 'word',
  'odt': 'word',
  'rtf': 'word',
  
  // Excel
  'xls': 'excel',
  'xlsx': 'excel',
  'ods': 'excel',
  'csv': 'excel',
  
  // PowerPoint
  'ppt': 'powerpoint',
  'pptx': 'powerpoint',
  'odp': 'powerpoint',
  
  // Text
  'txt': 'text',
  
  // Imagini
  'jpg': 'image',
  'jpeg': 'image',
  'png': 'image',
  'gif': 'image',
  'webp': 'image',
  'svg': 'image',
  'bmp': 'image',
  
  // Video
  'mp4': 'video',
  'webm': 'video',
  'avi': 'video',
  'mov': 'video',
  'mkv': 'video',
  
  // Audio
  'mp3': 'audio',
  'wav': 'audio',
  'ogg': 'audio',
  'flac': 'audio',
  'm4a': 'audio',
};

/**
 * Extrage extensia dintr-un nume de fișier
 */
export function getExtension(fileName) {
  if (!fileName) return '';
  const parts = fileName.split('.');
  return parts.length > 1 ? parts.pop().toLowerCase() : '';
}

/**
 * Determină tipul fișierului bazat pe extensie
 * @returns 'image' | 'video' | 'audio' | 'document' | 'other'
 */
export function getFileType(fileName) {
  const ext = getExtension(fileName);
  return EXTENSION_TO_TYPE[ext] || 'other';
}

/**
 * Determină iconița potrivită pentru fișier
 * @returns 'pdf' | 'word' | 'excel' | 'powerpoint' | 'text' | 'image' | 'video' | 'audio' | 'file'
 */
export function getFileIcon(fileName) {
  const ext = getExtension(fileName);
  return EXTENSION_TO_ICON[ext] || 'file';
}

/**
 * Verifică dacă fișierul este o imagine
 */
export function isImage(fileName) {
  return getFileType(fileName) === 'image';
}

/**
 * Verifică dacă fișierul este un video
 */
export function isVideo(fileName) {
  return getFileType(fileName) === 'video';
}

/**
 * Verifică dacă fișierul este audio
 */
export function isAudio(fileName) {
  return getFileType(fileName) === 'audio';
}

/**
 * Verifică dacă fișierul este un document
 */
export function isDocument(fileName) {
  return getFileType(fileName) === 'document';
}

/**
 * Formatează dimensiunea fișierului în format human-readable
 */
export function formatFileSize(bytes) {
  if (!bytes || bytes === 0) return '0 B';
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
}

/**
 * Obține culoarea asociată unui tip de fișier
 */
export function getFileColor(fileName) {
  const icon = getFileIcon(fileName);
  const colors = {
    pdf: '#ef4444',
    word: '#3b82f6',
    excel: '#22c55e',
    powerpoint: '#f97316',
    text: '#6b7280',
    image: '#8b5cf6',
    video: '#ec4899',
    audio: '#06b6d4',
    file: '#9ca3af',
  };
  return colors[icon] || colors.file;
}

export default {
  getExtension,
  getFileType,
  getFileIcon,
  isImage,
  isVideo,
  isAudio,
  isDocument,
  formatFileSize,
  getFileColor,
};
