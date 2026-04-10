const envUrl = import.meta.env.VITE_API_URL?.trim();
const isLocalhost = envUrl?.includes('127.0.0.1') || envUrl?.includes('localhost');

export const API_BASE = (envUrl && !isLocalhost) 
  ? envUrl 
  : "https://api.aethercompass.com";

const normalizeUrl = (path) => {
  const cleanedPath = path.startsWith("/") ? path : `/${path}`;
  if (!API_BASE) return cleanedPath;
  return `${API_BASE.replace(/\/+$/, "")}${cleanedPath}`;
};

export const apiFetch = (path, options) => fetch(normalizeUrl(path), options);
