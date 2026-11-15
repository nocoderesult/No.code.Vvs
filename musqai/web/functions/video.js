/* Videoclipurile S&T, servite pe bucăți (HTTP Range).
   Fișierele statice de pe Cloudflare vin mereu întregi, iar Safari pe iPhone nu pornește
   un video fără răspunsuri 206. Pagina cere /st/video/<nume>.mp4; aici citim fișierul din
   /st/media/_v/ și trimitem doar intervalul cerut. */

const VIDEOS = new Set(["teaser-720.mp4", "teaser-540.mp4"]);

export async function serveVideo(request, env, name) {
  if (!VIDEOS.has(name)) return env.ASSETS.fetch(request);
  if (request.method !== "GET" && request.method !== "HEAD") {
    return new Response(null, { status: 405, headers: { Allow: "GET, HEAD" } });
  }
  const src = new URL(request.url);
  src.pathname = "/st/media/_v/" + name;
  src.search = "";
  const full = await env.ASSETS.fetch(new Request(src.toString(), { method: "GET" }));
  if (!full.ok) return full;

  const size = Number(full.headers.get("Content-Length"));
  const base = { "Content-Type": "video/mp4", "Accept-Ranges": "bytes", "Cache-Control": "public, max-age=86400" };
  const head = request.method === "HEAD";
  const m = /^bytes=(\d*)-(\d*)$/.exec((request.headers.get("Range") || "").trim());

  if (!m || !size || (m[1] === "" && m[2] === "")) {
    if (head && full.body) full.body.cancel();
    return new Response(head ? null : full.body, { status: 200, headers: { ...base, ...(size ? { "Content-Length": String(size) } : {}) } });
  }

  let start, end;
  if (m[1] === "") {
    start = Math.max(0, size - Number(m[2]));
    end = size - 1;
  } else {
    start = Number(m[1]);
    end = m[2] === "" ? size - 1 : Math.min(Number(m[2]), size - 1);
  }
  if (start > end || start >= size) {
    if (full.body) full.body.cancel();
    return new Response(null, { status: 416, headers: { ...base, "Content-Range": `bytes */${size}` } });
  }
  if (head && full.body) full.body.cancel();
  return new Response(head ? null : slice(full.body, start, end), {
    status: 206,
    headers: { ...base, "Content-Range": `bytes ${start}-${end}/${size}`, "Content-Length": String(end - start + 1) }
  });
}

/* Trece prin flux doar octeții start..end (inclusiv), fără să țină tot fișierul în memorie. */
function slice(stream, start, end) {
  const reader = stream.getReader();
  let pos = 0;
  return new ReadableStream({
    async pull(controller) {
      for (;;) {
        const { done, value } = await reader.read();
        if (done) { controller.close(); return; }
        const from = pos;
        pos += value.byteLength;
        if (pos <= start) continue;
        const a = Math.max(0, start - from);
        const b = Math.min(value.byteLength, end + 1 - from);
        if (b > a) controller.enqueue(value.subarray(a, b));
        if (pos > end) { controller.close(); reader.cancel(); }
        return;
      }
    },
    cancel() { reader.cancel(); }
  });
}
