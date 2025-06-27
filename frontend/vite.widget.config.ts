import { defineConfig } from 'vite'
import path from 'path'

// Dedicated config for the web component
export default defineConfig({
  build: {
    lib: {
      entry: path.resolve(__dirname, 'src/Liz.ts'),
      name: 'Liz',
      fileName: 'liz',
      formats: ['es']
    },
    outDir: 'dist',
    rollupOptions: {
      output: {
        entryFileNames: 'liz.js',
        assetFileNames: 'liz.[ext]'
      }
    },
    minify: false, // Keep readable for development
    sourcemap: true,
    watch: {}
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  define: {
    'process.env.NODE_ENV': '"development"',
    'process.env': '{}'
  }
}) 