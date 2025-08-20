import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import fs from "fs";
import path from "path";

// Check if SSL certificates exist (for dev server)
const keyPath = "../key.pem";
const certPath = "../cert.pem";
const hasSSL = fs.existsSync(keyPath) && fs.existsSync(certPath);

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    ...(hasSSL && {
      https: {
        key: fs.readFileSync(keyPath), // Private key
        cert: fs.readFileSync(certPath), // Certificate
      },
    }),
    host: "0.0.0.0",
    port: 5173,
  },
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
});
