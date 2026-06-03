import axios from 'axios';
import { API_BASE_URL, LOCAL_STORAGE_KEYS } from './constants';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Automatically inject JWT tokens into all outbound requests
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem(LOCAL_STORAGE_KEYS.TOKEN);
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Global response error handler
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An unexpected error occurred';
    
    // Auto-logout user on unauthorized / token expiration errors
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem(LOCAL_STORAGE_KEYS.TOKEN);
        localStorage.removeItem(LOCAL_STORAGE_KEYS.USER);
        // Force redirect to login page if we are in dashboard
        if (!window.location.pathname.startsWith('/login') && !window.location.pathname.startsWith('/register') && window.location.pathname !== '/') {
          window.location.href = '/login';
        }
      }
    }
    
    return Promise.reject(new Error(message));
  }
);

export default api;
