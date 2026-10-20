/* Unelte comune pentru zonele de generare (Cloudflare Pages Functions + Workers AI). */

export const TEXT_MODEL = "@cf/meta/llama-3.3-70b-instruct-fp8-fast";
export const IMAGE_MODEL = "@cf/black-forest-labs/flux-1-schnell";
export const VISION_MODEL = "@cf/llava-hf/llava-1.5-7b-hf";

export class HttpError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

export const json = (data, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", "x-content-type-options": "nosniff" }
  });

export const methodNotAllowed = () => json({ eroare: "Folosește POST." }, 405);

/* Învelește fiecare zonă: verifică legătura AI și transformă orice eroare într-un mesaj clar, în română. */
export function handler(fn) {
  return async (context) => {
    try {
      if (!context.env || !context.env.AI) {
        throw new HttpError(503, "Generarea nu e pornită încă: în Cloudflare lipsește legătura Workers AI cu numele AI.");
      }
      return json(await fn(context));
    } catch (err) {
      if (err instanceof HttpError) return json({ eroare: err.message }, err.status);
      const msg = String((err && err.message) || err);
      if (/neuron|allocation|daily|3036|quota|exceeded|too many requests|rate limit/i.test(msg)) {
        return json({ eroare: "Limita zilnică de generare a fost atinsă. Revino mâine sau scrie-ne pentru acces." }, 429);
      }
      console.error("musqai-api", msg);
      return json({ eroare: "Generarea n-a mers de data asta. Încearcă din nou peste câteva secunde.", detaliu: msg.slice(0, 300) }, 502);
    }
  };
}

export async function readBody(request, maxBytes) {
  const type = request.headers.get("content-type") || "";
  if (!type.includes("application/json")) throw new HttpError(415, "Trimite datele ca JSON.");
  const declared = Number(request.headers.get("content-length") || 0);
  if (declared > maxBytes) throw new HttpError(413, "Cererea e prea mare.");
  const raw = await request.text();
  if (raw.length > maxBytes) throw new HttpError(413, "Cererea e prea mare.");
  let value;
  try {
    value = JSON.parse(raw);
  } catch (_) {
    throw new HttpError(400, "Cererea nu e un JSON valid.");
  }
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new HttpError(400, "Cererea nu e un JSON valid.");
  return value;
}

export function field(v, { max, min = 0, name }) {
  const s = String(v ?? "").replace(/\s+/g, " ").trim();
  if (s.length < min) throw new HttpError(400, `Completează câmpul „${name}”.`);
  if (s.length > max) throw new HttpError(400, `Câmpul „${name}” e prea lung (maximum ${max} de caractere).`);
  return s;
}
export const oneOf = (v, list, fallback) => (list.includes(v) ? v : fallback);

/* Filtre de siguranță înainte de model. Modelul are și el regulile lui, scrise în instrucțiuni. */
const word = (alts) => new RegExp(`(?<![\\p{L}\\p{N}])(?:${alts})(?![\\p{L}\\p{N}])`, "iu");
const EXPLICIT = word("naked|topless|porn\\p{L}*|xxx|nsfw|hentai|onlyfans|sex|sexual\\p{L}*|erotic\\p{L}*|fetish\\p{L}*|dezbrăcat\\p{L}*|dezbracat\\p{L}*|undress\\p{L}*|deepfake\\p{L}*|face ?swap");
const MINORS = word("copil|copii|copiii|copilul|copiilor|copilă|fetiț\\p{L}*|fetit\\p{L}*|băieței|băiețel\\p{L}*|baietel\\p{L}*|bebeluș\\p{L}*|bebelus\\p{L}*|școlăriț\\p{L}*|scolarit\\p{L}*|adolescent\\p{L}*|child\\p{L}*|kids|teen\\p{L}*|underage|toddler\\p{L}*|schoolgirl\\p{L}*|loli\\p{L}*");
export function checkSafe(text, { minors = false } = {}) {
  if (EXPLICIT.test(text) || (minors && MINORS.test(text))) {
    throw new HttpError(422, "Cererea conține ceva ce nu generăm: nuditate, conținut sexual, minori sau persoane reale. Reformulează și încearcă din nou.");
  }
}

/* Textul: Llama 3.3 cu răspuns JSON după o schemă. Dacă modul JSON nu reușește, mai încercăm o dată și citim JSON-ul din text. */
export async function runJson(env, { system, user, schema, maxTokens = 1200, temperature = 0.6 }) {
  const messages = [{ role: "system", content: system }, { role: "user", content: user }];
  let out;
  try {
    out = await env.AI.run(TEXT_MODEL, { messages, max_tokens: maxTokens, temperature, response_format: { type: "json_schema", json_schema: schema } });
  } catch (err) {
    if (!/json mode/i.test(String(err && err.message))) throw err;
    out = await env.AI.run(TEXT_MODEL, {
      messages: [...messages, { role: "user", content: "Răspunde doar cu un singur obiect JSON valid, fără alt text." }],
      max_tokens: maxTokens,
      temperature
    });
  }
  const r = out && out.response;
  if (r && typeof r === "object") return r;
  return parseLoose(String(r || ""));
}

export function parseLoose(s) {
  const t = s.replace(/```(?:json)?/gi, "").trim();
  try {
    return JSON.parse(t);
  } catch (_) { /* încercăm mai jos */ }
  const a = t.indexOf("{"), b = t.lastIndexOf("}");
  if (a >= 0 && b > a) {
    try {
      return JSON.parse(t.slice(a, b + 1));
    } catch (_) { /* cade mai jos */ }
  }
  throw new HttpError(502, "Răspunsul n-a venit în formatul așteptat. Încearcă din nou.");
}

/* Curăță valorile primite de la model, ca pagina să primească mereu forma așteptată. */
export const s = (v, max = 600) => String(v ?? "").trim().slice(0, max);
export const list = (v, n, max = 300) => (Array.isArray(v) ? v : []).map((x) => s(x, max)).filter(Boolean).slice(0, n);

/* Imaginea: FLUX.1 [schnell], apoi marcajul AI în fișier. */
export async function makeImage(env, prompt) {
  const seed = 1 + Math.floor(Math.random() * 2147483646);
  const out = await env.AI.run(IMAGE_MODEL, { prompt: prompt.slice(0, 2000), steps: 6, seed });
  let bytes;
  if (out && typeof out.image === "string") bytes = b64ToBytes(out.image);
  else if (out instanceof ReadableStream) bytes = new Uint8Array(await new Response(out).arrayBuffer());
  else if (out instanceof ArrayBuffer) bytes = new Uint8Array(out);
  if (!bytes || bytes.length < 100) throw new HttpError(502, "Nu a venit nicio imagine. Încearcă din nou.");
  const isJpeg = bytes[0] === 0xff && bytes[1] === 0xd8;
  const isPng = bytes[0] === 0x89 && bytes[1] === 0x50;
  const marked = isJpeg ? addXmp(bytes) : bytes;
  const mime = isJpeg ? "image/jpeg" : isPng ? "image/png" : "image/jpeg";
  return { image: `data:${mime};base64,${bytesToB64(marked)}`, seed };
}

export function b64ToBytes(b64) {
  const bin = atob(String(b64).replace(/\s+/g, ""));
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}
export function bytesToB64(bytes) {
  let str = "";
  for (let i = 0; i < bytes.length; i += 0x8000) str += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  return btoa(str);
}

/* AI Act, art. 50: marcaj citibil de calculator. Punem în JPEG un bloc XMP cu tipul IPTC „trainedAlgorithmicMedia”. */
export function addXmp(jpeg) {
  const xmp =
    '<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>' +
    '<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">' +
    '<rdf:Description rdf:about="" xmlns:Iptc4xmpExt="http://iptc.org/std/Iptc4xmpExt/2008-02-29/" xmlns:xmp="http://ns.adobe.com/xap/1.0/" xmlns:dc="http://purl.org/dc/elements/1.1/"' +
    ' Iptc4xmpExt:DigitalSourceType="http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia"' +
    ' xmp:CreatorTool="MUSQAI · FLUX.1 [schnell] prin Cloudflare Workers AI">' +
    '<dc:description><rdf:Alt><rdf:li xml:lang="x-default">Imagine generată cu AI pe musqai.com</rdf:li></rdf:Alt></dc:description>' +
    "</rdf:Description></rdf:RDF></x:xmpmeta>" +
    '<?xpacket end="w"?>';
  const enc = new TextEncoder();
  const head = enc.encode("http://ns.adobe.com/xap/1.0/\0");
  const body = enc.encode(xmp);
  const len = 2 + head.length + body.length;
  if (len > 0xffff) return jpeg;
  const seg = new Uint8Array(2 + len);
  seg[0] = 0xff;
  seg[1] = 0xe1;
  seg[2] = (len >> 8) & 0xff;
  seg[3] = len & 0xff;
  seg.set(head, 4);
  seg.set(body, 4 + head.length);
  // după segmentul APP0 (JFIF), dacă există
  let at = 2;
  if (jpeg[2] === 0xff && jpeg[3] === 0xe0) at = 4 + ((jpeg[4] << 8) | jpeg[5]);
  const out = new Uint8Array(jpeg.length + seg.length);
  out.set(jpeg.subarray(0, at), 0);
  out.set(seg, at);
  out.set(jpeg.subarray(at), at + seg.length);
  return out;
}

/* Reguli comune pentru textele în română. */
export const RULES_RO =
  "Reguli obligatorii: ambasadorul este un caracter AI declarat; nu spune că a cumpărat sau a folosit produsul ca o persoană reală; " +
  "fără mărturii sau recenzii false; fără promisiuni medicale, financiare sau de rezultat corporal; fără nuditate sau conținut sexual; " +
  "fără minori; colaborările plătite au #ad. Scrie natural, în română corectă cu diacritice, fără clișee de marketing.";
