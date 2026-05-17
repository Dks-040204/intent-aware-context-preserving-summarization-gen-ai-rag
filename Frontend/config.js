/* ─────────────────────────────────────────────────────────────────────
   Contexto — API Configuration
   ─────────────────────────────────────────────────────────────────────
   LOCAL DEVELOPMENT:
     Set API_BASE_URL to 'http://localhost:8000'

   PRODUCTION (after deploying backend to Railway / Render / HF Spaces):
     Set API_BASE_URL to your deployed backend URL, e.g.:
       'https://contexto-backend.railway.app'
       'https://contexto-api.onrender.com'
   ───────────────────────────────────────────────────────────────────── */

window.CONTEXTO_CONFIG = {
  API_BASE_URL: 'http://localhost:8000'   // ← change this for production
};
