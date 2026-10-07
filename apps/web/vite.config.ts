import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig({
  plugins: [react()],
  server: { strictPort: true, proxy: { "/api": "http://127.0.0.1:8093" } },
  build: {
    outDir: "dist",
    rollupOptions: {
      output: {
        manualChunks: {
          charts: ["recharts"],
          ui: ["react", "react-dom", "radix-ui"],
        },
      },
    },
  },
});
