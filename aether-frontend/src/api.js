const envUrl = (import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || "").trim();

export const API_BASE = envUrl || "https://api.aethercompass.com";

const normalizeUrl = (path) => {
  // Ensure the path starts with a slash
  const cleanedPath = path.startsWith("/") ? path : `/${path}`;
  
  // If no base URL is defined, return just the path (relative to current domain)
  if (!API_BASE) return cleanedPath;
  
  // Combine base + path, stripping trailing slash from base
  return `${API_BASE.replace(/\/+$/, "")}${cleanedPath}`;
};

export const apiFetch = (path, options = {}) => {
  const url = normalizeUrl(path);
  console.log(`[apiFetch] Calling: ${url}`); // Debugging help
  
  if (path.includes('/admin/')) {
    options.headers = {
      ...options.headers,
      'X-Admin-Key': import.meta.env.VITE_ADMIN_API_KEY || ''
    };
  }
  
  return fetch(url, options);
};
