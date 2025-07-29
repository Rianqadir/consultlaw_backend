// src/utils/authAPI.js

import axios from 'axios';

// Use localStorage token
const authAPI = axios.create({
 baseURL: 'https://consultlaw-backend.onrender.com/api', // ✅ your backend on Render
 withCredentials: false,
});

authAPI.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default authAPI;
