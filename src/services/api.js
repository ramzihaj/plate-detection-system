import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Authentification
export const authService = {
  signup: (data) => api.post('/signup', data),
  login: (data) => api.post('/login', data),
};

// Détection de plaques
export const plateService = {
  detectPlate: (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return api.post('/detect-plate-text', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
  },
  getHistory: () => api.get('/plates'),
};

// Contact
export const contactService = {
  sendMessage: (data) => api.post('/contact', data),
  getMessages: () => api.get('/contacts'),
};

export default api;
