import { handler, methodNotAllowed, readBody, field, oneOf, checkSafe, runJson, makeImage, s, list, HttpError, RULES_RO } from "../../lib/ai.js";
import { characters, niches } from "../../content.mjs";

const SCHEMA = {
  type: "object",
  properties: {
    ok: { type: "boolean" },
    motiv: { type: "string" },
    nume: { type: "string" },
    rol: { type: "string" },
    arhetip: { type: "string" },
    aspect: { type: "string" },
    stil: { type: "string" },
    personalitate: { type: "array", items: { type: "string" } },
    voce: { type: "string" },
    piloni: { type: "array", items: { type: "object", properties: { nume: { type: "string" }, procent: { type: "number" } }, required: ["nume", "procent"] } },
    hookuri: { type: "array", items: { type: "string" } },
    prompt_portret: { type: "string" }
  },
  required: ["ok", "motiv", "nume", "rol", "arhetip", "aspect", "stil", "personalitate", "voce", "piloni", "hookuri", "prompt_portret"]
};

export const onRequestPost = handler(async ({ request, env }) => {
  const b = await readBody(request, 16 * 1024);
  const gen = oneOf(b.gen, ["femeie", "bărbat"], "femeie");
  const age = Math.min(60, Math.max(21, Math.round(Number(b.varsta) || 28)));
  const niche = niches.find((n) => n.id === b.nisa) || niches[0];
  const stil = field(b.stil, { max: 160, name: "Stilul" });
  const vibe = field(b.vibe, { max: 160, name: "Cum vrei să pară" });
  checkSafe(`${stil} ${vibe}`, { minors: true });
  const taken = characters.map((c) => c.name).join(", ");

  const sheet = await runJson(env, {
    system:
      "Creezi un ambasador AI fictiv pentru un brand din România. " + RULES_RO +
      " Caracterul este adult (vârsta dată), fictiv și nu seamănă intenționat cu nicio persoană reală: nu folosi nume de vedete și nu descrie sosii. " +
      `Numele: un prenume ușor de pronunțat în română, diferit de ${taken}. ` +
      "aspect: 2–3 propoziții despre păr, ochi, ten și semne distinctive. stil: 1–2 propoziții. personalitate: 4 adjective. voce: o propoziție. " +
      "piloni: 4 piloni de conținut, procentele adunate dau 100. hookuri: 3 hook-uri de maximum 12 cuvinte. " +
      "prompt_portret: în engleză, 50–80 de cuvinte, portret realist bust (head and shoulders), fundal de studio simplu, lumină moale, fără text. " +
      "Refuză (ok=false, motiv în română) dacă cererea cere ceva sexual, minori sau o persoană reală.",
    user: `Gen: ${gen}. Vârsta: ${age} de ani. Nișa brandului: ${niche.name}. Stilul dorit: ${stil || "la alegerea ta"}. Cum vrea să pară: ${vibe || "la alegerea ta"}.`,
    schema: SCHEMA,
    maxTokens: 1100,
    temperature: 0.85
  });
  if (!sheet.ok) throw new HttpError(422, s(sheet.motiv, 300) || "Nu putem crea caracterul ăsta. Reformulează.");

  const fisa = {
    nume: s(sheet.nume, 40),
    varsta: age,
    rol: s(sheet.rol, 120),
    arhetip: s(sheet.arhetip, 120),
    aspect: s(sheet.aspect, 600),
    stil: s(sheet.stil, 400),
    personalitate: list(sheet.personalitate, 5, 40),
    voce: s(sheet.voce, 300),
    piloni: (Array.isArray(sheet.piloni) ? sheet.piloni : []).slice(0, 5).map((p) => ({ nume: s(p && p.nume, 80), procent: Math.max(0, Math.min(100, Math.round(Number(p && p.procent) || 0))) })).filter((p) => p.nume),
    hookuri: list(sheet.hookuri, 3, 160)
  };
  const portrait = s(sheet.prompt_portret, 1200);
  let image = null, imageError = "";
  try {
    checkSafe(portrait, { minors: true });
    image = (await makeImage(env, `${portrait}, photorealistic, natural skin texture, ${gen === "bărbat" ? "adult man" : "adult woman"} aged ${age}`)).image;
  } catch (err) {
    if (err instanceof HttpError && err.status === 422) throw err;
    const msg = String((err && err.message) || err);
    imageError = /neuron|allocation|daily|3036|quota|exceeded/i.test(msg) ? "Portretul n-a putut fi generat azi: s-a atins limita zilnică." : "Portretul n-a ieșit de data asta. Fișa e gata; încearcă din nou pentru portret.";
  }
  return { fisa, image, imageError };
});

export const onRequest = methodNotAllowed;
