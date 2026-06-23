import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';

// The guide is published to GitHub Pages at
// blog.bytesofpurpose.com/getting-started-with-claude-agents/ (a project page under a
// subpath, no CNAME). Relative base ('./') makes the emitted asset URLs work regardless of
// the exact mount point, so we never hardcode the repo name.
//
// Source lives under web/ (web/index.html is the Vite entry). Build output goes to dist-site/.
// The deploy step copies the built index.html + assets/ to the repo root, where GitHub Pages
// serves from (main/root, legacy build). Source-under-web/ keeps the React app cleanly
// separated from the repo's example/ + tooling and avoids colliding with the generated
// index.html at root during the transition.
export default defineConfig({
  base: './',
  root: 'web',
  plugins: [react()],
  build: {
    outDir: '../dist-site',
    emptyOutDir: true,
    assetsDir: 'assets',
  },
});
