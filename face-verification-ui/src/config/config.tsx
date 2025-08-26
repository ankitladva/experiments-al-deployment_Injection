// If backend is on a different port
// export const BACKEND_URL = window.location.protocol + "//" + window.location.hostname + ":8000"
// export const BACKEND_URL =  "https://10.128.0.29:8000"
// export const BACKEND_URL =  "https://192.168.167.189:8000"
// export const BACKEND_URL =  "https://192.168.1.100:8000"
// export const BACKEND_URL =  "https://192.168.1.5:8000"
// export const BACKEND_URL =  "https://172.16.14.83:8000"
// export const BACKEND_URL =  "https://localhost:8000"
// export const BACKEND_URL =  "https://192.168.167.189:8000"
// export const BACKEND_URL =  "https://0.0.0.0:8000"
export const BACKEND_URL = (import.meta.env.VITE_BACKEND_URL as string) || window.location.origin;
console.log("BACKEND_URL::",BACKEND_URL)

// API Key for backend authentication
export const API_KEY = import.meta.env.VITE_API_KEY as string;
if (!API_KEY) {
    console.error("❌ VITE_API_KEY environment variable is not set! Backend connection will fail.");
}
console.log("API_KEY configured:", API_KEY ? "Yes" : "No");

