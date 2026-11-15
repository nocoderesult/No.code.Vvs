/* MUSQAI pe Cloudflare Workers: paginile din public/ le servește Cloudflare direct,
   iar adresele /api/<zonă> ajung aici, la zonele de generare.
   /api/runpod/* duce generatorul Krea 2 (/generator/) la endpoint-ul Runpod.
   /st/video/* servește teaserul S&T pe bucăți, ca să meargă și pe iPhone. */
import * as idei from "./functions/api/idei.js";
import * as text from "./functions/api/text.js";
import * as imagine from "./functions/api/imagine.js";
import * as prompt from "./functions/api/prompt.js";
import * as caracter from "./functions/api/caracter.js";
import { handleRunpod } from "./functions/api/runpod.js";
import { serveVideo } from "./functions/video.js";

const ZONES = { idei, text, imagine, prompt, caracter };

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const rp = url.pathname.match(/^\/api\/runpod\/(.+)$/);
    if (rp) return handleRunpod(request, env, rp[1]);
    const sv = url.pathname.match(/^\/st\/video\/((?:hls\/)?[a-z0-9_-]+\.(?:mp4|m3u8|ts))$/);
    if (sv) return serveVideo(request, env, sv[1]);
    const m = url.pathname.match(/^\/api\/([a-z]+)\/?$/);
    if (m && ZONES[m[1]]) {
      const zone = ZONES[m[1]];
      const context = { request, env, waitUntil: (p) => ctx.waitUntil(p) };
      return request.method === "POST" ? zone.onRequestPost(context) : zone.onRequest(context);
    }
    return env.ASSETS.fetch(request);
  }
};
