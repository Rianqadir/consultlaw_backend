import axios from 'axios';

const authAPI = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'https://consultlaw-backend.onrender.com/api',
});

authAPI.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Token ${token}`;
  return config;
});

import axios from 'axios';

const publicAPI = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'https://consultlaw-backend.onrender.com/api',
});

export { publicAPI, authAPI };
