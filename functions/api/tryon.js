// Cloudflare Pages Function: POST /api/tryon
// Primește selfie-ul și alegerile clientului și îi cere modelului Gemini de editare
// a imaginii („Nano Banana”) să schimbe doar tunsoarea și, la cerere, barba.
// Cheia nu ajunge niciodată în browser.
//
// Variabile de mediu (Cloudflare Pages → Settings → Variables and Secrets):
//   GEMINI_API_KEY      cheia din Google AI Studio. Fără ea, site-ul rulează în mod demo.
//   GEMINI_IMAGE_MODEL  opțional; implicit gemini-2.5-flash-image
//
// Id-urile de mai jos trebuie să se potrivească cu public/js/catalog.js.

const STYLES = {
  'skin-fade': 'a modern skin fade: the sides and back faded smoothly down to bare skin, with a short textured top',
  'french-crop': 'a French crop: a short textured top pushed forward into a short blunt fringe across the forehead, with faded sides',
  buzz: 'a clean buzz cut: hair clipped evenly short all over (about 3-6 mm) with a crisp natural hairline',
  quiff: 'a textured quiff: the front styled up and slightly back with natural matte texture, with short tapered sides',
  pompadour: 'a classic pompadour: a voluminous top swept up and back with a polished finish, with short faded sides',
  'slick-back': 'a slick back: the top combed straight back with a sleek, slightly glossy finish, with short tapered sides',
  mullet: 'a modern mullet: a short textured top and sides, with longer hair left at the back reaching the nape of the neck',
  curly: 'a curly top: defined natural curls on top, with the sides tapered short',
};
const BEARDS = {
  keep: 'Keep the facial hair exactly as it is in the photo.',
  none: 'Also make the face clean-shaven.',
  stubble: 'Also give a neat, even light stubble (2-3 mm).',
  short: 'Also give a short, neatly boxed beard with sharp cheek and neck lines.',
  full: 'Also give a full, well-groomed beard with clean lines.',
};
const MAX_BASE64 = 4_000_000;

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
  });

function buildPrompt(body) {
  const custom = String(body.custom || '').replace(/[\u0000-\u001f]/g, ' ').slice(0, 140).trim();
  const style = custom
    ? `this hairstyle, as described by the client (the description may be in Romanian): "${custom}"`
    : STYLES[body.style] || STYLES['skin-fade'];
  return [
    `Edit this photo the way a top barber would: change the haircut to ${style}.`,
    BEARDS[body.beard] || BEARDS.keep,
    'Keep the natural hair color.',
    "Keep the person's face, identity, skin, expression, eyes, ears, head shape, clothing, background, lighting, framing and camera angle exactly the same.",
    'Photorealistic result with a natural hairline and realistic hair texture, as if photographed right after a fresh cut. No text, no watermark.',
  ].join(' ');
}

export async function onRequestPost({ request, env }) {
  if (!env.GEMINI_API_KEY) return json({ demo: true, error: 'AI-ul nu este configurat încă.' }, 501);

  // Acceptăm cereri doar de pe propriul site
  const origin = request.headers.get('Origin');
  if (origin && new URL(origin).host !== new URL(request.url).host) return json({ error: 'Origine nepermisă.' }, 403);

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: 'Cerere invalidă.' }, 400);
  }
  const m = /^data:(image\/(?:jpeg|png|webp));base64,([A-Za-z0-9+/=]+)$/.exec(body.image || '');
  if (!m) return json({ error: 'Poza lipsește sau are un format greșit.' }, 400);
  if (m[2].length > MAX_BASE64) return json({ error: 'Poza este prea mare.' }, 413);

  const model = env.GEMINI_IMAGE_MODEL || 'gemini-2.5-flash-image';
  const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'x-goog-api-key': env.GEMINI_API_KEY },
    body: JSON.stringify({
      contents: [{ role: 'user', parts: [{ inline_data: { mime_type: m[1], data: m[2] } }, { text: buildPrompt(body) }] }],
      generationConfig: { responseModalities: ['IMAGE'] },
    }),
  });

  if (!res.ok) {
    console.log('gemini error', res.status, (await res.text()).slice(0, 500));
    return json({
      error: res.status === 429
        ? 'Sunt multe cereri acum. Încearcă din nou într-un minut.'
        : 'Generarea nu a mers. Mai încearcă o dată.',
    }, 502);
  }

  const data = await res.json();
  const parts = (data.candidates && data.candidates[0] && data.candidates[0].content && data.candidates[0].content.parts) || [];
  const part = parts.find((p) => p.inlineData || p.inline_data);
  if (!part) {
    return json({ error: 'AI-ul nu a returnat o imagine. Încearcă o poză din față, cu fața bine vizibilă.' }, 422);
  }
  const img = part.inlineData || part.inline_data;
  return json({ image: `data:${img.mimeType || img.mime_type || 'image/png'};base64,${img.data}` });
}
