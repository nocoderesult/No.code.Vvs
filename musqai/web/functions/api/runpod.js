/* Generatorul Krea 2 (/generator/) vorbește cu Runpod prin această adresă, pentru că politica
   site-ului permite cereri doar către același domeniu (connect-src 'self').
   Cheia vine de la cel care generează, în antetul Authorization, și pleacă neschimbată la Runpod;
   Worker-ul nu o păstrează. Se ajunge doar la endpoint-ul studioului, cu trei acțiuni:
   POST /api/runpod/run, GET /api/runpod/status/<id>, POST /api/runpod/cancel/<id>. */

const ENDPOINT_ID = "zi26pfbwi74co9"; // musqai-matrix-pro6000 (RTX PRO 6000)
const MAX_BODY = 10 * 1024 * 1024; // limita Runpod pentru /run

function json(data, status, extra = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", ...extra }
  });
}

export async function handleRunpod(request, env, path) {
  let method;
  if (path === "run") method = "POST";
  else if (/^status\/[A-Za-z0-9-]{1,100}$/.test(path)) method = "GET";
  else if (/^cancel\/[A-Za-z0-9-]{1,100}$/.test(path)) method = "POST";
  else return json({ error: "Adresă necunoscută." }, 404);
  if (request.method !== method) return json({ error: "Metodă nepermisă." }, 405, { Allow: method });

  const auth = request.headers.get("Authorization") || "";
  if (!/^Bearer [A-Za-z0-9_\-.]{10,300}$/.test(auth)) return json({ error: "Lipsește cheia de acces." }, 401);

  const init = { method, headers: { Authorization: auth } };
  if (path === "run") {
    const body = await request.arrayBuffer();
    if (body.byteLength > MAX_BODY) return json({ error: "Cererea e prea mare." }, 413);
    init.headers["Content-Type"] = "application/json";
    init.body = body;
  }

  const endpoint = (env && env.RUNPOD_ENDPOINT_ID) || ENDPOINT_ID;
  let upstream;
  try {
    upstream = await fetch(`https://api.runpod.ai/v2/${endpoint}/${path}`, init);
  } catch (e) {
    return json({ error: "Runpod nu răspunde acum." }, 502);
  }
  return new Response(upstream.body, {
    status: upstream.status,
    headers: {
      "Content-Type": upstream.headers.get("Content-Type") || "application/json",
      "Cache-Control": "no-store"
    }
  });
}
