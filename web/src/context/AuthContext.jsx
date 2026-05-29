import React, { createContext, useState, useEffect, useContext } from 'react';
import * as authService from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check stored credentials on mount
  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = authService.getStoredToken();
      const storedUser = authService.getStoredUser();

      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(storedUser);
        
        // Optionally sync profile status in background
        try {
          const profileData = await authService.getMe();
          if (profileData && profileData.user) {
            setUser(profileData.user);
          }
        } catch (error) {
          console.error("Failed to sync profile status on start:", error);
          // If profile check fails due to 401, axios interceptor handles it
        }
      }
      setLoading(false);
    };

    initializeAuth();

    // Listen to global event for session expiration
    const handleAuthExpired = () => {
      setUser(null);
      setToken(null);
    };

    window.addEventListener('auth-expired', handleAuthExpired);
    return () => {
      window.removeEventListener('auth-expired', handleAuthExpired);
    };
  }, []);

  const login = async (username, password) => {
    setLoading(true);
    try {
      const data = await authService.login(username, password);
      setToken(data.access_token);
      setUser(data.user);
      return data;
    } finally {
      setLoading(false);
    }
  };

  const signup = async (username, password) => {
    setLoading(true);
    try {
      const data = await authService.signup(username, password);
      setToken(data.access_token);
      setUser(data.user);
      return data;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      await authService.logout();
    } finally {
      setUser(null);
      setToken(null);
      setLoading(false);
    }
  };

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!token,
    login,
    signup,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
