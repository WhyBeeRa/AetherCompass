const envUrl = import.meta.env.VITE_API_URL?.trim();

export const API_BASE = envUrl || "https://api.aethercompass.com";

const normalizeUrl = (path) => {
  const cleanedPath = path.startsWith("/") ? path : `/${path}`;
  if (!API_BASE) return cleanedPath;
  return `${API_BASE.replace(/\/+$/, "")}${cleanedPath}`;
};

export const apiFetch = (path, options) => fetch(normalizeUrl(path), options);
