// src/services/api.js
// Serviciu pentru comunicarea cu backend-ul Flask
// Gestioneaza toate cererile HTTP catre API

import axios from 'axios';

// Configuram axios cu URL-ul de baza
const api = axios.create({
  baseURL: '/api',
  withCredentials: true, // Trimitem cookies pentru sesiuni
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor pentru erori globale
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Daca primim 401, utilizatorul nu e autentificat
    if (error.response?.status === 401) {
      // Redirectionam la login daca nu suntem deja acolo
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// ==================== AUTENTIFICARE ====================

export const authAPI = {
  // Verifica daca utilizatorul e autentificat
  checkAuth: () => api.get('/auth/check'),
  
  // Inregistrare cont nou
  register: (username, email, password) =>
    api.post('/auth/register', { username, email, password }),
  
  // Autentificare
  login: (username, password) =>
    api.post('/auth/login', { username, password }),
  
  // Deconectare
  logout: () => api.post('/auth/logout'),
  
  // Obtine utilizatorul curent
  getCurrentUser: () => api.get('/auth/me'),
  
  // Cauta utilizatori
  searchUsers: (query) => api.get(`/auth/users/search?q=${encodeURIComponent(query)}`),
  
  // Obtine cheia publica a unui utilizator
  getUserPublicKey: (userId) => api.get(`/auth/users/${userId}/public-key`),
  
  // Actualizeaza profilul
  updateProfile: (data) => api.put('/auth/profile', data),
  
  // Obtine informatii despre criptare
  getCryptoInfo: () => api.get('/auth/crypto-info'),
};

// ==================== CONVERSATII ====================

export const chatAPI = {
  // Obtine lista conversatiilor
  getConversations: () => api.get('/conversations'),
  
  // Creeaza o conversatie noua
  createConversation: (participantIds, name = null) =>
    api.post('/conversations', { participant_ids: participantIds, name }),
  
  // Obtine detaliile unei conversatii
  getConversation: (conversationId) => api.get(`/conversations/${conversationId}`),
  
  // Sterge o conversatie
  deleteConversation: (conversationId) => api.delete(`/conversations/${conversationId}`),
  
  // Obtine mesajele dintr-o conversatie
  getMessages: (conversationId, limit = 50, beforeId = null) => {
    let url = `/conversations/${conversationId}/messages?limit=${limit}`;
    if (beforeId) url += `&before=${beforeId}`;
    return api.get(url);
  },
  
  // Trimite un mesaj
  sendMessage: (conversationId, content, messageType = 'text') =>
    api.post(`/conversations/${conversationId}/messages`, { content, message_type: messageType }),
  
  // Marcheaza conversatia ca citita
  markAsRead: (conversationId) => api.put(`/conversations/${conversationId}/read`),
  
  // Obtine numarul de mesaje necitite
  getUnreadCount: () => api.get('/unread-count'),
  
  // Obtine informatii despre criptarea conversatiei
  getConversationCryptoInfo: (conversationId) => api.get(`/conversations/${conversationId}/crypto-info`),
  
  // Decripteaza un mesaj (pe server - pentru demo)
  decryptMessage: (messageId, privateKey) =>
    api.post(`/messages/${messageId}/decrypt`, { private_key: privateKey }),
};

// ==================== FISIERE ====================

export const fileAPI = {
  // Uploadeaza fisiere (fara a trimite mesaj)
  uploadFiles: (conversationId, files) => {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    
    return api.post(`/files/upload/${conversationId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  // Trimite mesaj cu fisiere atasate
  sendWithFiles: (conversationId, content, attachments) =>
    api.post(`/files/send/${conversationId}`, { content, attachments }),
  
  // Descarca un atasament
  downloadAttachment: async (attachmentId, privateKey) => {
    const response = await api.post(`/files/download/${attachmentId}`, 
      { private_key: privateKey },
      { responseType: 'blob' }
    );
    return response;
  },
  
  // Descarca fisier din mesaj vechi (legacy)
  downloadLegacy: async (messageId, privateKey) => {
    const response = await api.post(`/files/download-legacy/${messageId}`, 
      { private_key: privateKey },
      { responseType: 'blob' }
    );
    return response;
  },
  
  // Obtine imagine decriptata ca base64
  getImage: (attachmentId, privateKey) =>
    api.post(`/files/image/${attachmentId}`, { private_key: privateKey }),
  
  // Sterge fisier temporar
  deleteTempFile: (tempId) => api.delete(`/files/delete-temp/${tempId}`),
  
  // Obtine informatii despre un fisier (legacy)
  getFileInfo: (messageId) => api.get(`/files/info/${messageId}`),
};

// ==================== HEALTH CHECK ====================

export const healthAPI = {
  check: () => api.get('/health'),
};

export default api;
