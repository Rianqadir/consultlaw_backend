import axios from 'axios';

const publicAPI = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'https://consultlaw-backend.onrender.com/api/auth/',
});

export default publicAPI;
