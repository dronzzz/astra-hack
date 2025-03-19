import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 4000,
    proxy: {
      '/api': {
        target: 'http://localhost:5050',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path,
      },
      '/shorts': {
        target: 'http://localhost:5050',
        changeOrigin: true,
      },
      '/video': {
        target: 'http://localhost:5050',
        changeOrigin: true,
      },
      '/thumbnail': {
        target: 'http://localhost:5050',
        changeOrigin: true,
      },
      '/shorts_output': {
        target: 'http://localhost:5050',
        changeOrigin: true,
      },
      '/status': {
        target: 'http://localhost:5050',
        changeOrigin: true,
      }
    }
  },
  plugins: [
    react(),
    mode === 'development' &&
    componentTagger(),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
