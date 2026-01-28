import axios from "axios";

// Define global typings for Vite environment variables so TypeScript
// knows that `import.meta.env` exists and what it contains.
declare global {
  interface ImportMetaEnv {
    readonly VITE_API_BASE_URL?: string;
  }

  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }
}

const baseURL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

// Create axios instance with base URL
const api = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Optional: Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log("Making request to:", config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// Optional: Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  },
);

export default api;
