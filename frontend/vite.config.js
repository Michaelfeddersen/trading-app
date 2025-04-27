import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  base: './', // ⬅️ HIER hinzufügen, super wichtig!
  plugins: [react()],
  server: {
    port: 5173, // oder 5174, 5175 wenn 5173 belegt ist
    open: true,
  }
})
