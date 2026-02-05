import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE || "http://localhost:8000";

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
