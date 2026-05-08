import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [tailwindcss(), sveltekit()],
	server: {
		fs: {
			allow: ['.']
		},
		watch: {
			ignored: ['**/static/audio/**', '**/data/tts.db**']
		},
		hmr: {
			overlay: false
		}
	},
	optimizeDeps: {
		exclude: ['bun:sqlite']
	},
	build: {
		rollupOptions: {
			external: ['bun:sqlite']
		}
	}
});
