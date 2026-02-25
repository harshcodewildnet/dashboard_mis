import axios from "axios";

// Use VITE_API_BASE env var if set, otherwise empty string (routes through Vite proxy)
const baseURL = import.meta.env.VITE_API_BASE || "";

export const api = axios.create({
  baseURL,
  timeout: 15000
});

// Add a request interceptor to attach the token
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
