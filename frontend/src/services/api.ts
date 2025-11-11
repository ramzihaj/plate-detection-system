import axios from 'axios';
import type { 
  LoginCredentials, 
  RegisterData, 
  AuthResponse, 
  User,
  Detection,
  DetectionHistory,
  UserStats 
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/api/auth/login', credentials);
    return response.data;
  },

  register: async (data: RegisterData): Promise<User> => {
    const response = await api.post<User>('/api/auth/register', data);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/api/auth/me');
    return response.data;
  },
};

// Plate Detection APIs
export const plateAPI = {
  detectPlate: async (file: File): Promise<Detection> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<Detection>('/api/plates/detect', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getHistory: async (page = 1, pageSize = 10): Promise<DetectionHistory> => {
    const response = await api.get<DetectionHistory>('/api/plates/history', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  getDetection: async (id: string): Promise<Detection> => {
    const response = await api.get<Detection>(`/api/plates/${id}`);
    return response.data;
  },

  deleteDetection: async (id: string): Promise<void> => {
    await api.delete(`/api/plates/${id}`);
  },
};

// User APIs
export const userAPI = {
  getProfile: async (): Promise<User> => {
    const response = await api.get<User>('/api/users/profile');
    return response.data;
  },

  updateProfile: async (data: { full_name?: string; username?: string }): Promise<User> => {
    const response = await api.put<User>('/api/users/profile', data);
    return response.data;
  },

  getStats: async (): Promise<UserStats> => {
    const response = await api.get<UserStats>('/api/users/stats');
    return response.data;
  },
};

export default api;
