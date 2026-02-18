import axios from "axios";

const baseURL = "http://3.88.55.152:8000";

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
