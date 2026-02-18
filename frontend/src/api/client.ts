import axios from "axios";

// Use relative /api path so Nginx proxy routes to the backend container.
// This works both locally (via Vite proxy) and in production (via Nginx proxy).
const baseURL = "/api";

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
