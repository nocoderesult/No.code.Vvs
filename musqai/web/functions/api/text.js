import { handler, methodNotAllowed, readBody, field, oneOf, checkSafe, runJson, s, list, RULES_RO } from "../../lib/ai.js";
import { characters } from "../../content.mjs";

const PLATFORMS = { Instagram: "până la 400 de caractere, cu rânduri scurte", TikTok: "până la 150 de caractere, foarte direct", Facebook: "până la 500 de caractere, conversațional", LinkedIn: "până la 600 de caractere, profesional, fără emoji multe" };
const TONES = { cald: "cald și prietenos", premium: "elegant și premium", amuzant: "amuzant, cu umor fin", direct: "direct și la obiect" };
const SCHEMA = {
  type: "object",
  properties: {
    variante: {
      type: "array",
      items: { type: "object", properties: { caption: { type: "string" }, hashtaguri: { type: "array", items: { type: "string" } } }, required: ["caption", "hashtaguri"] }
    }
  },
  required: ["variante"]
};

export const onRequestPost = handler(async ({ request, env }) => {
  const b = await readBody(request, 16 * 1024);
  const despre = field(b.despre, { min: 10, max: 800, name: "Despre ce e postarea" });
  const cta = field(b.cta, { max: 120, name: "Ce vrei să facă oamenii" });
  checkSafe(`${despre} ${cta}`);
  const platform = oneOf(b.platforma, Object.keys(PLATFORMS), "Instagram");
  const tone = oneOf(b.ton, Object.keys(TONES), "cald");
  const ch = characters.find((c) => c.id === b.caracter);
  const data = await runJson(env, {
    system:
      "Ești copywriterul MUSQAI. Scrii descrieri pentru postări pe rețelele sociale, în română. " + RULES_RO +
      " Fiecare variantă începe cu un hook puternic în primul rând, are un singur îndemn la final și 4–8 hashtag-uri relevante (cu #, fără spații).",
    user:
      `Platformă: ${platform} (${PLATFORMS[platform]}). Ton: ${TONES[tone]}.\n` +
      (ch ? `Scrie cu vocea caracterului ${ch.name}: ${ch.voice} Personalitate: ${ch.personality.join(", ")}.\n` : "Scrie pentru contul brandului.\n") +
      `Despre postare: ${despre}\n` +
      (cta ? `Îndemnul dorit: ${cta}\n` : "") +
      "Scrie 3 variante diferite între ele.",
    schema: SCHEMA,
    maxTokens: 1200,
    temperature: 0.8
  });
  const variante = (Array.isArray(data.variante) ? data.variante : []).slice(0, 3).map((v) => ({
    caption: s(v.caption, 900),
    hashtaguri: list(v.hashtaguri, 8, 40).map((h) => "#" + h.replace(/^#+/, "").replace(/\s+/g, ""))
  })).filter((v) => v.caption);
  if (!variante.length) throw new Error("fără variante");
  return { variante };
});

export const onRequest = methodNotAllowed;
