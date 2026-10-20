import { handler, methodNotAllowed, readBody, oneOf, checkSafe, runJson, s, b64ToBytes, HttpError, VISION_MODEL } from "../../lib/ai.js";

const TARGETS = ["FLUX / Krea (ComfyUI)", "Nano Banana", "Midjourney", "Seedance / Kling (video)"];
const SCHEMA = {
  type: "object",
  properties: {
    ok: { type: "boolean" },
    motiv: { type: "string" },
    prompt: { type: "string" },
    negative: { type: "string" },
    setari: { type: "string" },
    nota: { type: "string" }
  },
  required: ["ok", "motiv", "prompt", "negative", "setari", "nota"]
};

export const onRequestPost = handler(async ({ request, env }) => {
  const b = await readBody(request, 3 * 1024 * 1024);
  const b64 = String(b.image || "").replace(/^data:image\/[a-z+]+;base64,/i, "");
  if (!b64 || !/^[A-Za-z0-9+/=\s]+$/.test(b64)) throw new HttpError(400, "Alege o imagine JPG, PNG sau WebP.");
  const bytes = b64ToBytes(b64);
  if (bytes.length < 200) throw new HttpError(400, "Imaginea nu s-a încărcat. Încearcă din nou.");
  if (bytes.length > 2 * 1024 * 1024) throw new HttpError(413, "Imaginea e prea mare. Alege una mai mică.");
  const target = oneOf(b.tinta, TARGETS, TARGETS[0]);
  const video = target.includes("video");

  const vis = await env.AI.run(VISION_MODEL, {
    image: Array.from(bytes),
    prompt:
      "Describe this photo in detail so it can be recreated with an image generator: the main subject, pose, clothing, setting, " +
      "lighting, camera angle, lens feel, colors and mood. Do not guess anyone's identity or name. Answer in English, in one paragraph.",
    max_tokens: 450
  });
  const desc = s((vis && (vis.description || vis.response)) || "", 3000);
  if (desc.length < 20) throw new HttpError(502, "N-am putut citi imaginea. Încearcă cu alta.");

  const data = await runJson(env, {
    system:
      `You turn an image description into a ready-to-use prompt for ${target}. ` +
      "Refuse (ok=false) if the description shows nudity, sexual content or minors. Never name real people or brands. " +
      (video
        ? "Write the prompt for a 5-second video: describe the scene, the subject's motion and the camera movement. "
        : "Write one detailed English prompt of 50 to 100 words: subject, pose, clothing, setting, light, camera, lens, mood, style. ") +
      "negative: an English comma-separated list of things to avoid. setari: short Romanian suggestions (format, aspect ratio, settings for the target). " +
      "nota: one Romanian sentence about what to check in the result. motiv: a short Romanian explanation if you refuse, otherwise an empty string.",
    user: `Image description: ${desc}`,
    schema: SCHEMA,
    maxTokens: 700,
    temperature: 0.4
  });
  if (!data.ok) throw new HttpError(422, s(data.motiv, 300) || "Nu putem scrie un prompt pentru imaginea asta.");
  const out = { prompt: s(data.prompt, 1500), negative: s(data.negative, 500), setari: s(data.setari, 300), nota: s(data.nota, 300), descriere: desc, tinta: target };
  checkSafe(out.prompt, { minors: true });
  return out;
});

export const onRequest = methodNotAllowed;
