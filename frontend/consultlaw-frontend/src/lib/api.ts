// src/lib/api.ts

import axios from 'axios';

const API = axios.create({
  baseURL: 'https://consultlaw-backend.onrender.com/api/auth/',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default API;
