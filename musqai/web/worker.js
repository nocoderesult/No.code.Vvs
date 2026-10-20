/* MUSQAI pe Cloudflare Workers: paginile din public/ le servește Cloudflare direct,
   iar adresele /api/<zonă> ajung aici, la zonele de generare. */
import * as idei from "./functions/api/idei.js";
import * as text from "./functions/api/text.js";
import * as imagine from "./functions/api/imagine.js";
import * as prompt from "./functions/api/prompt.js";
import * as caracter from "./functions/api/caracter.js";

const ZONES = { idei, text, imagine, prompt, caracter };

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const m = url.pathname.match(/^\/api\/([a-z]+)\/?$/);
    if (m && ZONES[m[1]]) {
      const zone = ZONES[m[1]];
      const context = { request, env, waitUntil: (p) => ctx.waitUntil(p) };
      return request.method === "POST" ? zone.onRequestPost(context) : zone.onRequest(context);
    }
    return env.ASSETS.fetch(request);
  }
};
