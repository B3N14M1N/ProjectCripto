// src/App.js
// Componenta principala a aplicatiei
// Gestioneaza rutarea si starea de autentificare

import React, { useState, useEffect, createContext } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { authAPI } from './services/api';

// Pagini
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ChatPage from './pages/ChatPage';

// Context pentru autentificare
export const AuthContext = createContext(null);

/**
 * Componenta principala App
 * 
 * Responsabilitati:
 * - Verifica starea de autentificare la incarcare
 * - Gestioneaza rutarea bazata pe autentificare
 * - Furnizeaza context pentru starea utilizatorului
 */
function App() {
  // Starea utilizatorului curent
  const [user, setUser] = useState(null);
  const [privateKey, setPrivateKey] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const navigate = useNavigate();
  
  // Verificam autentificarea la incarcarea aplicatiei
  useEffect(() => {
    checkAuth();
  }, []);
  
  // Functie pentru verificarea autentificarii
  const checkAuth = async () => {
    try {
      const response = await authAPI.checkAuth();
      if (response.data.authenticated) {
        setUser(response.data.user);
        // Incercam sa recuperam cheia privata din localStorage
        const storedKey = localStorage.getItem(`privateKey_${response.data.user.id}`);
        if (storedKey) {
          setPrivateKey(storedKey);
        }
      }
    } catch (error) {
      console.log('Nu e autentificat');
    } finally {
      setLoading(false);
    }
  };
  
  // Functie pentru login
  const login = async (username, password) => {
    const response = await authAPI.login(username, password);
    if (response.data.success) {
      setUser(response.data.user);
      // Verificam daca avem cheia privata salvata
      const storedKey = localStorage.getItem(`privateKey_${response.data.user.id}`);
      if (storedKey) {
        setPrivateKey(storedKey);
      }
      navigate('/chat');
    }
    return response.data;
  };
  
  // Functie pentru inregistrare
  const register = async (username, email, password) => {
    const response = await authAPI.register(username, email, password);
    if (response.data.success) {
      setUser(response.data.user);
      // Salvam cheia privata in localStorage
      if (response.data.private_key) {
        localStorage.setItem(`privateKey_${response.data.user.id}`, response.data.private_key);
        setPrivateKey(response.data.private_key);
      }
      navigate('/chat');
    }
    return response.data;
  };
  
  // Functie pentru logout
  const logout = async () => {
    await authAPI.logout();
    setUser(null);
    setPrivateKey(null);
    navigate('/login');
  };
  
  // Functie pentru setarea cheii private manual
  const setUserPrivateKey = (key) => {
    if (user) {
      localStorage.setItem(`privateKey_${user.id}`, key);
      setPrivateKey(key);
    }
  };
  
  // Afisam loading in timpul verificarii autentificarii
  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="spinner" style={{ margin: '0 auto 16px' }}></div>
          <p className="text-muted">Se incarca...</p>
        </div>
      </div>
    );
  }
  
  // Valoarea contextului de autentificare
  const authContextValue = {
    user,
    privateKey,
    login,
    register,
    logout,
    setPrivateKey: setUserPrivateKey,
    isAuthenticated: !!user,
  };
  
  return (
    <AuthContext.Provider value={authContextValue}>
      <Routes>
        {/* Ruta pentru login */}
        <Route 
          path="/login" 
          element={user ? <Navigate to="/chat" /> : <LoginPage />} 
        />
        
        {/* Ruta pentru inregistrare */}
        <Route 
          path="/register" 
          element={user ? <Navigate to="/chat" /> : <RegisterPage />} 
        />
        
        {/* Ruta pentru chat - necesita autentificare */}
        <Route 
          path="/chat" 
          element={user ? <ChatPage /> : <Navigate to="/login" />} 
        />
        <Route 
          path="/chat/:conversationId" 
          element={user ? <ChatPage /> : <Navigate to="/login" />} 
        />
        
        {/* Redirectionare default */}
        <Route 
          path="*" 
          element={<Navigate to={user ? "/chat" : "/login"} />} 
        />
      </Routes>
    </AuthContext.Provider>
  );
}

export default App;
