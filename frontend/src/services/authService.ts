/**
 * Authentication API service
 *
 * Handles:
 * - User signup and login
 * - JWT token management
 * - Current user information
 * - Questionnaire submission
 */

import axios, { AxiosError } from 'axios';

const API_BASE_URL = (typeof process !== 'undefined' && process.env?.REACT_APP_API_URL) || 'http://localhost:8000/api';

// TypeScript interfaces

export interface SignupRequest {
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export enum SkillLevel {
  BEGINNER = 'beginner',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced',
}

export interface UserProfile {
  python_level: SkillLevel;
  ai_experience: SkillLevel;
  robotics_experience: SkillLevel;
  has_rtx_gpu: boolean;
  preferred_language: string;
}

export interface QuestionnaireRequest {
  python_level: SkillLevel;
  ai_experience: SkillLevel;
  robotics_experience: SkillLevel;
  has_rtx_gpu: boolean;
  preferred_language: string;
}

export interface UserMeResponse {
  id: string;
  email: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  profile?: UserProfile;
}

/**
 * Authentication service class
 */
class AuthService {
  private axiosInstance;
  private readonly TOKEN_KEY = 'auth_token';

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.axiosInstance.interceptors.request.use(
      (config) => {
        const token = this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
  }

  /**
   * Store JWT token in localStorage
   */
  private setToken(token: string): void {
    localStorage.setItem(this.TOKEN_KEY, token);
  }

  /**
   * Get JWT token from localStorage
   */
  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Remove JWT token from localStorage
   */
  private removeToken(): void {
    localStorage.removeItem(this.TOKEN_KEY);
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return this.getToken() !== null;
  }

  /**
   * Sign up a new user
   */
  async signup(email: string, password: string): Promise<AuthToken> {
    try {
      const response = await this.axiosInstance.post<AuthToken>('/auth/signup', {
        email,
        password,
      });

      // Store token
      this.setToken(response.data.access_token);

      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Login with email and password
   */
  async login(email: string, password: string): Promise<AuthToken> {
    try {
      const response = await this.axiosInstance.post<AuthToken>('/auth/login', {
        email,
        password,
      });

      // Store token
      this.setToken(response.data.access_token);

      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Logout (clear token)
   */
  logout(): void {
    this.removeToken();
  }

  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<UserMeResponse> {
    try {
      const response = await this.axiosInstance.get<UserMeResponse>('/auth/me');
      return response.data;
    } catch (error) {
      // If unauthorized, clear token
      if (axios.isAxiosError(error) && error.response?.status === 401) {
        this.removeToken();
      }
      throw this.handleError(error);
    }
  }

  /**
   * Submit questionnaire (skill assessment)
   */
  async submitQuestionnaire(data: QuestionnaireRequest): Promise<UserProfile> {
    try {
      const response = await this.axiosInstance.post<UserProfile>(
        '/auth/questionnaire',
        data
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Change password
   */
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    try {
      await this.axiosInstance.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Handle and format errors
   */
  private handleError(error: unknown): Error {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;

      if (axiosError.response) {
        const detail = (axiosError.response.data as any)?.detail;
        return new Error(detail || 'An error occurred');
      }

      if (axiosError.code === 'ECONNABORTED') {
        return new Error('Request timeout');
      }

      if (axiosError.code === 'ERR_NETWORK') {
        return new Error('Network error. Please check your connection.');
      }
    }

    return new Error('An unexpected error occurred');
  }
}

// Export singleton instance
export const authService = new AuthService();
