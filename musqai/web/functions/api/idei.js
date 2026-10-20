import { handler, methodNotAllowed, readBody, field, oneOf, checkSafe, runJson, s, list, RULES_RO } from "../../lib/ai.js";
import { characters, niches } from "../../content.mjs";

const FORMATS = ["Reel 8–15 s", "Carusel", "Story", "Reclamă 9:16"];
const IDEA = {
  type: "object",
  properties: {
    titlu: { type: "string" },
    hook: { type: "string" },
    cadre: { type: "array", items: { type: "string" } },
    text_pe_ecran: { type: "string" },
    caption: { type: "string" },
    ora: { type: "string" },
    de_ce: { type: "string" }
  },
  required: ["titlu", "hook", "cadre", "caption", "ora", "de_ce"]
};
const SCHEMA = { type: "object", properties: { idei: { type: "array", items: IDEA } }, required: ["idei"] };

export const onRequestPost = handler(async ({ request, env }) => {
  const b = await readBody(request, 16 * 1024);
  const brief = field(b.brief, { min: 10, max: 800, name: "Ce vinzi și cui" });
  checkSafe(brief);
  const ch = characters.find((c) => c.id === b.caracter);
  const niche = niches.find((n) => n.id === b.nisa) || niches[0];
  const format = oneOf(b.format, FORMATS, FORMATS[0]);
  const n = Number(b.n) === 3 ? 3 : 5;
  const who = ch
    ? `Caracter: ${ch.name}, ${ch.age} de ani, ${ch.role}. Personalitate: ${ch.personality.join(", ")}. Vocea: ${ch.voice} Piloni de conținut: ${ch.pillars.map((p) => p[0]).join(", ")}.`
    : "Fără caracter: ideile sunt pentru contul brandului.";
  const data = await runJson(env, {
    system:
      "Ești strategul de conținut al MUSQAI, un studio românesc de ambasadori AI pentru branduri. " + RULES_RO +
      " Hook-ul are cel mult 12 cuvinte și prinde atenția în primele 2 secunde. Fiecare idee are exact 3 cadre scurte. " +
      "Caption: cel mult 300 de caractere și un singur îndemn. Ora: o oră de postare potrivită pentru publicul din România, în formatul HH:MM. " +
      "de_ce: o propoziție despre de ce ar funcționa.",
    user: `${who}\nNișa: ${niche.name}. Clienți tipici: ${niche.who}\nFormat: ${format}\nBrief: ${brief}\nScrie ${n} idei diferite între ele.`,
    schema: SCHEMA,
    maxTokens: 1800,
    temperature: 0.8
  });
  const idei = (Array.isArray(data.idei) ? data.idei : []).slice(0, n).map((o) => ({
    titlu: s(o.titlu, 120),
    hook: s(o.hook, 160),
    cadre: list(o.cadre, 3, 200),
    text_pe_ecran: s(o.text_pe_ecran, 120),
    caption: s(o.caption, 400),
    ora: s(o.ora, 10),
    de_ce: s(o.de_ce, 240)
  })).filter((o) => o.hook);
  if (!idei.length) throw new Error("fără idei");
  return { idei };
});

export const onRequest = methodNotAllowed;
