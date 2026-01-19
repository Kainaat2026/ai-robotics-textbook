/**
 * Authentication Context
 * Manages user authentication state across the application
 */
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authApi } from '../api/client';

// Auth context
const AuthContext = createContext(null);

// Token storage key
const TOKEN_KEY = 'auth_token';

/**
 * Auth Provider component
 */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load user on mount
  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem(TOKEN_KEY);
      if (token) {
        try {
          const userData = await authApi.getMe();
          setUser(userData);
        } catch (err) {
          // Token invalid, clear it
          localStorage.removeItem(TOKEN_KEY);
          console.error('Failed to load user:', err);
        }
      }
      setLoading(false);
    };

    loadUser();
  }, []);

  // Signup
  const signup = useCallback(async ({ email, password }) => {
    setError(null);
    try {
      const { access_token } = await authApi.signup({ email, password });
      localStorage.setItem(TOKEN_KEY, access_token);

      // Load user data
      const userData = await authApi.getMe();
      setUser(userData);

      return { success: true };
    } catch (err) {
      const message = err.response?.data?.detail || 'Signup failed';
      setError(message);
      return { success: false, error: message };
    }
  }, []);

  // Login
  const login = useCallback(async ({ email, password }) => {
    setError(null);
    try {
      const { access_token } = await authApi.login({ email, password });
      localStorage.setItem(TOKEN_KEY, access_token);

      // Load user data
      const userData = await authApi.getMe();
      setUser(userData);

      return { success: true };
    } catch (err) {
      const message = err.response?.data?.detail || 'Login failed';
      setError(message);
      return { success: false, error: message };
    }
  }, []);

  // Logout
  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setUser(null);
    setError(null);
  }, []);

  // Submit questionnaire (background questions)
  const submitQuestionnaire = useCallback(async (questionnaireData) => {
    setError(null);
    try {
      const profile = await authApi.submitQuestionnaire(questionnaireData);
      // Update user with new profile
      setUser(prev => prev ? { ...prev, profile } : null);
      return { success: true };
    } catch (err) {
      const message = err.response?.data?.detail || 'Failed to save questionnaire';
      setError(message);
      return { success: false, error: message };
    }
  }, []);

  // Refresh user data
  const refreshUser = useCallback(async () => {
    try {
      const userData = await authApi.getMe();
      setUser(userData);
      return userData;
    } catch (err) {
      console.error('Failed to refresh user:', err);
      return null;
    }
  }, []);

  // Check if user is authenticated
  const isAuthenticated = !!user;

  // Get user's skill level for personalization
  const getUserSkillLevel = useCallback(() => {
    if (!user?.profile) return 'intermediate';

    const levels = {
      beginner: 1,
      intermediate: 2,
      advanced: 3
    };

    const avgLevel = (
      levels[user.profile.python_level] +
      levels[user.profile.ai_experience] +
      levels[user.profile.robotics_experience]
    ) / 3;

    if (avgLevel < 1.5) return 'beginner';
    if (avgLevel < 2.5) return 'intermediate';
    return 'advanced';
  }, [user]);

  const value = {
    user,
    loading,
    error,
    isAuthenticated,
    signup,
    login,
    logout,
    submitQuestionnaire,
    refreshUser,
    getUserSkillLevel,
    clearError: () => setError(null),
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook to use auth context
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
