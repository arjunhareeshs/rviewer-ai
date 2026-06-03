export const API_BASE_URL = typeof window !== 'undefined' ? '' : 'http://localhost:8000';

export const APP_ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/upload',
  ANALYSIS: '/analysis',
  ATS: '/analysis/ats',
  SECTIONS: '/analysis/sections',
  ROLES: '/analysis/roles',
  PROJECTS: '/analysis/projects',
  LINKS: '/analysis/links',
  ROADMAP: '/analysis/roadmap',
  CHAT: '/analysis/chat',
  BUILDER: '/builder',
  INTERVIEW: '/interview',
  ADMIN: '/admin',
};

export const LOCAL_STORAGE_KEYS = {
  TOKEN: 'auth_token',
  USER: 'auth_user',
};
