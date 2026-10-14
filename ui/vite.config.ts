import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  // In development the backend runs separately on port 8000; in production
  // FastAPI serves this build itself, so /api is the same origin.
  server: { proxy: { "/api": "http://localhost:8000" } },
});
