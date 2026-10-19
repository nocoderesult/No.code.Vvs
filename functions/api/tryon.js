// POST /api/tryon — apelată din worker/index.js (Cloudflare Workers); merge și ca Pages Function.
// Primește selfie-ul și alegerile clientului și îi cere modelului GPT Image (OpenAI) să schimbe
// doar tunsoarea și, la cerere, barba. Cheia stă pe server și nu ajunge niciodată în browser.
//
// Variabile (Cloudflare → proiectul → Settings → Variables and Secrets):
//   OPENAI_API_KEY        cheia OpenAI, ca secret. Fără ea, proba virtuală rulează în mod demo.
//   OPENAI_IMAGE_MODEL    opțional; implicit gpt-image-2.5-flare (rapid).
//                         Pentru precizie maximă, dar mai lent: gpt-image-2.5-sunburst
//   OPENAI_IMAGE_QUALITY  opțional; low | medium | high (implicit medium)
//
// Id-urile tunsorilor trebuie să se potrivească cu public/js/catalog.js.

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
const MAX_BYTES = 4 * 1024 * 1024;
// Limită aproximativă de încercări pe IP. E ținută în memoria instanței, deci nu e exactă,
// dar oprește apăsările repetate; limita sigură de cost se pune din contul OpenAI.
const LIMIT = { max: 6, windowMs: 10 * 60 * 1000 };
const attempts = new Map();

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
  });

function tooManyAttempts(ip) {
  const now = Date.now();
  const recent = (attempts.get(ip) || []).filter((t) => now - t < LIMIT.windowMs);
  recent.push(now);
  if (attempts.size > 5000) attempts.clear();
  attempts.set(ip, recent);
  return recent.length > LIMIT.max;
}

function buildPrompt(style, custom, beard) {
  const description = String(custom || '').replace(/[\u0000-\u001f]/g, ' ').slice(0, 140).trim();
  const haircut = description
    ? `this hairstyle, as described by the client (the description may be in Romanian): "${description}"`
    : STYLES[style] || STYLES['skin-fade'];
  return [
    `Edit this photo the way a top barber would: change the haircut to ${haircut}.`,
    BEARDS[beard] || BEARDS.keep,
    'Keep the natural hair color.',
    "Keep the person's face, identity, skin, expression, eyes, ears, head shape, clothing, background, lighting, framing and camera angle exactly the same.",
    'Photorealistic result with a natural hairline and realistic hair texture, as if photographed right after a fresh cut. No text, no watermark.',
  ].join(' ');
}

function friendlyError(status, detail) {
  if (status === 429) return 'Sunt multe cereri acum. Încearcă din nou într-un minut.';
  if (/safety|moderation|content_policy/i.test(detail)) {
    return 'Poza nu a putut fi procesată. Încearcă o poză din față, doar cu tine în cadru.';
  }
  return 'Generarea nu a mers. Mai încearcă o dată.';
}

export async function onRequestPost({ request, env }) {
  if (!env.OPENAI_API_KEY) return json({ demo: true, error: 'AI-ul nu este configurat încă.' }, 501);

  // Acceptăm cereri doar de pe propriul site
  const origin = request.headers.get('Origin');
  if (origin && new URL(origin).host !== new URL(request.url).host) return json({ error: 'Origine nepermisă.' }, 403);

  if (tooManyAttempts(request.headers.get('CF-Connecting-IP') || 'necunoscut')) {
    return json({ error: 'Ai făcut multe încercări. Mai încearcă peste câteva minute.' }, 429);
  }

  let form;
  try {
    form = await request.formData();
  } catch {
    return json({ error: 'Cerere invalidă.' }, 400);
  }
  const photo = form.get('image');
  if (!photo || typeof photo === 'string' || !/^image\/(jpeg|png|webp)$/.test(photo.type)) {
    return json({ error: 'Poza lipsește sau are un format greșit.' }, 400);
  }
  if (photo.size > MAX_BYTES) return json({ error: 'Poza este prea mare.' }, 413);

  const model = env.OPENAI_IMAGE_MODEL || 'gpt-image-2.5-flare';
  const body = new FormData();
  body.append('model', model);
  body.append('image', photo, 'selfie.jpg');
  body.append('prompt', buildPrompt(form.get('style'), form.get('custom'), form.get('beard')));
  body.append('size', 'auto');
  body.append('quality', env.OPENAI_IMAGE_QUALITY || 'medium');
  body.append('output_format', 'jpeg');
  body.append('output_compression', '85');
  // GPT Image 1 și 1.5 păstrează fața mai bine cu input_fidelity=high; de la gpt-image-2 e automat
  if (/^gpt-image-1(\.5)?$/.test(model)) body.append('input_fidelity', 'high');

  const res = await fetch('https://api.openai.com/v1/images/edits', {
    method: 'POST',
    headers: { Authorization: `Bearer ${env.OPENAI_API_KEY}` },
    body,
  });

  if (!res.ok) {
    const detail = (await res.text()).slice(0, 600);
    console.log('openai error', res.status, detail);
    return json({ error: friendlyError(res.status, detail) }, res.status === 429 ? 429 : 502);
  }

  // Răspunsul OpenAI (imaginea în base64, în data[0].b64_json) trece direct spre browser
  return new Response(res.body, {
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
  });
}
