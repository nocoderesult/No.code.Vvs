// Fișierele din public/ sunt servite direct de Cloudflare; aici ajung doar cererile
// care nu sunt fișiere: proba virtuală (/api/tryon) și adresele inexistente.
import { onRequestPost as tryOn } from '../functions/api/tryon.js';

export default {
  async fetch(request, env) {
    const { pathname } = new URL(request.url);
    if (pathname === '/api/tryon') {
      if (request.method === 'POST') return tryOn({ request, env });
      return new Response('Method Not Allowed', { status: 405, headers: { Allow: 'POST' } });
    }
    return env.ASSETS.fetch(request);
  },
};
