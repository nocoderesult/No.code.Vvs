import { handler, methodNotAllowed, readBody, field, oneOf, checkSafe, runJson, makeImage, s, HttpError } from "../../lib/ai.js";
import { characters } from "../../content.mjs";

const STYLES = {
  telefon: "candid smartphone photo, natural light, slightly imperfect framing, realistic skin texture, light film grain",
  studio: "professional studio photo, softbox lighting, seamless backdrop, crisp detail, realistic skin texture",
  editorial: "high-fashion editorial photograph, dramatic directional light, magazine quality, rich color",
  produs: "commercial product photograph, clean composition, the product in sharp focus, soft natural shadows"
};
const SCHEMA = {
  type: "object",
  properties: { ok: { type: "boolean" }, motiv: { type: "string" }, prompt: { type: "string" } },
  required: ["ok", "motiv", "prompt"]
};
export const GATE =
  "You write prompts for a photorealistic text-to-image model. The user describes an idea, usually in Romanian. First decide if it is allowed. " +
  "Refuse (ok=false) if it asks for: nudity or sexual content; minors or anyone who could look under 21; violence, gore or weapons aimed at people; " +
  "hate or extremist symbols; a real, named person (celebrity, politician, influencer, public figure) or a look-alike of one; real brand logos or trademarks; " +
  "fake documents, fake reviews or deceptive news. Every person in the image is a fictional adult. " +
  "If allowed, write one English prompt of 50 to 90 words describing subject, action, clothing, setting, light, camera and lens, mood, and the requested style. " +
  "Never add text, captions or watermarks to the image. motiv is a short Romanian explanation when you refuse, otherwise an empty string.";

export const onRequestPost = handler(async ({ request, env }) => {
  const b = await readBody(request, 16 * 1024);
  const idee = field(b.idee, { min: 6, max: 600, name: "Ce vrei să vezi" });
  checkSafe(idee, { minors: true });
  const style = oneOf(b.stil, Object.keys(STYLES), "telefon");
  const ch = characters.find((c) => c.id === b.caracter);
  const plan = await runJson(env, {
    system: GATE,
    user: `Idea: ${idee}\nStyle: ${STYLES[style]}` + (ch ? `\nThe main person must have exactly this appearance: ${ch.imageStyle}.` : ""),
    schema: SCHEMA,
    maxTokens: 400,
    temperature: 0.5
  });
  if (!plan.ok) throw new HttpError(422, s(plan.motiv, 300) || "Nu putem genera imaginea asta. Reformulează ideea.");
  const prompt = s(plan.prompt, 1500);
  if (prompt.length < 20) throw new HttpError(502, "N-am reușit să scriem promptul. Încearcă din nou.");
  checkSafe(prompt, { minors: true });
  const { image, seed } = await makeImage(env, prompt);
  return { image, prompt, seed };
});

export const onRequest = methodNotAllowed;
