// Environment configuration for the frontend
// Copy this file to .env.local and update the values

export const ENV_CONFIG = {
  // Backend API Key for authentication (REQUIRED)
  VITE_API_KEY: "",
  
  // Backend URL (optional - will fallback to current origin)
  VITE_BACKEND_URL: "https://kyc-backend-7f7c.onrender.com"
};

// Instructions:
// 1. Create a .env.local file in this directory
// 2. Add: VITE_API_KEY=your-actual-api-key-here
// 3. Optionally add: VITE_BACKEND_URL=your-backend-url
// 4. Restart your development server
