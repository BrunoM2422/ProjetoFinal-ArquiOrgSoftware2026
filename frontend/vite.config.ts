import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// O proxy encaminha as chamadas /api do front para o backend FastAPI em
// desenvolvimento, evitando configuração de CORS durante o desenvolvimento.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
