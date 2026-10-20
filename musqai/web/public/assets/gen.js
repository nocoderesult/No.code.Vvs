/* MUSQAI: zonele de generare. Trimite formularul la /api/<zonă> și afișează rezultatul. */
(() => {
  "use strict";
  const form = document.getElementById("zone-form");
  if (!form) return;
  const zone = form.dataset.zone;
  const out = document.getElementById("output");
  const status = document.getElementById("status");
  const go = document.getElementById("go");
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  const val = (name) => {
    const el = form.elements[name];
    return el ? String(el.value ?? "").trim() : "";
  };
  let seq = 0;
  const uid = () => "r" + ++seq;
  const copyBtn = (id, label = "Copiază") => `<button class="btn btn-ghost btn-sm" type="button" data-copy="${id}">${label}</button>`;

  /* Valori din adresă (ex. /genereaza/imagine/?caracter=iness&idee=...) */
  const params = new URLSearchParams(location.search);
  for (const key of ["caracter", "idee", "nisa"]) {
    const v = params.get(key);
    const el = form.elements[key];
    if (v && el) {
      if (el.tagName === "SELECT") { if ([...el.options].some((o) => o.value === v)) el.value = v; }
      else el.value = v.slice(0, 600);
    }
  }

  /* Starea butonului și a mesajului */
  let busy = false, timer = 0;
  function working(label) {
    busy = true;
    go.disabled = true;
    const t0 = Date.now();
    const tick = () => {
      status.className = "status";
      status.innerHTML = `<span class="spin" aria-hidden="true"></span>${esc(label)} ${Math.round((Date.now() - t0) / 1000)} s`;
    };
    tick();
    clearInterval(timer);
    timer = setInterval(tick, 1000);
  }
  function idle(msg, isErr) {
    busy = false;
    go.disabled = false;
    clearInterval(timer);
    status.className = isErr ? "status err" : "status";
    status.textContent = msg || "";
  }
  function ask(fieldName, msg) {
    idle(msg, true);
    const el = form.elements[fieldName];
    if (el && el.focus) el.focus();
  }

  async function api(body) {
    let res;
    try {
      res = await fetch(`/api/${zone}`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
    } catch (_) {
      throw new Error("Nu am putut ajunge la server. Verifică internetul și încearcă din nou.");
    }
    let data = null;
    try { data = await res.json(); } catch (_) { data = null; }
    if (!res.ok) {
      if ((res.status === 404 || res.status === 405) && !data) throw new Error("Zonele de generare nu sunt încă pornite pe server.");
      throw new Error((data && data.eroare) || `Ceva n-a mers (cod ${res.status}). Încearcă din nou.`);
    }
    if (!data || typeof data !== "object") throw new Error("Răspunsul n-a venit în formatul așteptat. Încearcă din nou.");
    return data;
  }

  /* Imaginea pentru Image → Prompt: o micșorăm la maximum 672 px, JPEG (modelul citește oricum la rezoluție mică) */
  let imageB64 = "";
  const drop = document.getElementById("drop");
  const fileInput = form.elements.file;
  const preview = document.getElementById("preview");
  async function loadBitmap(file) {
    if (window.createImageBitmap) {
      try { return await createImageBitmap(file); } catch (_) { /* încercăm mai jos */ }
    }
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = () => reject(new Error("Imaginea nu poate fi citită."));
      img.src = URL.createObjectURL(file);
    });
  }
  async function takeFile(file) {
    if (!file) return;
    if (!/^image\/(jpeg|png|webp)$/.test(file.type)) { idle("Alege o imagine JPG, PNG sau WebP.", true); return; }
    if (file.size > 15 * 1024 * 1024) { idle("Imaginea e prea mare (maximum 15 MB).", true); return; }
    try {
      const bmp = await loadBitmap(file);
      const w0 = bmp.width || bmp.naturalWidth, h0 = bmp.height || bmp.naturalHeight;
      const k = Math.min(1, 672 / Math.max(w0, h0));
      const cv = document.createElement("canvas");
      cv.width = Math.round(w0 * k);
      cv.height = Math.round(h0 * k);
      cv.getContext("2d").drawImage(bmp, 0, 0, cv.width, cv.height);
      const url = cv.toDataURL("image/jpeg", 0.86);
      imageB64 = url.split(",")[1];
      preview.src = url;
      preview.hidden = false;
      idle("Imaginea e gata. Apasă „Scrie promptul”.");
    } catch (_) {
      idle("Imaginea nu poate fi citită. Încearcă alt fișier.", true);
    }
  }
  if (drop && fileInput) {
    fileInput.addEventListener("change", () => takeFile(fileInput.files && fileInput.files[0]));
    drop.addEventListener("dragover", (e) => { e.preventDefault(); drop.classList.add("over"); });
    drop.addEventListener("dragleave", () => drop.classList.remove("over"));
    drop.addEventListener("drop", (e) => { e.preventDefault(); drop.classList.remove("over"); takeFile(e.dataTransfer.files && e.dataTransfer.files[0]); });
    document.addEventListener("paste", (e) => {
      const f = [...((e.clipboardData && e.clipboardData.files) || [])].find((x) => /^image\//.test(x.type));
      if (f) takeFile(f);
    });
  }

  /* Ce face fiecare zonă */
  const ZONES = {
    async idei() {
      const brief = val("brief");
      if (brief.length < 10) return ask("brief", "Scrie în câteva cuvinte ce vinzi și cui.");
      working("Se gândește la idei…");
      const d = await api({ caracter: val("caracter"), nisa: val("nisa"), format: val("format"), brief, n: Number(val("n") || 5) });
      const ideas = Array.isArray(d.idei) ? d.idei : [];
      out.innerHTML = `<div class="results">${ideas.map((o) => {
        const id = uid();
        return `<article class="result">
          <div class="actions" style="justify-content:space-between"><span class="chip hot">${esc(o.ora ? "postare la " + o.ora : "idee")}</span></div>
          <span class="muted tiny" style="text-transform:uppercase;letter-spacing:.08em;font-weight:700">${esc(o.titlu)}</span>
          <p class="hook">„${esc(o.hook)}”</p>
          ${o.cadre && o.cadre.length ? `<ol>${o.cadre.map((c) => `<li>${esc(c)}</li>`).join("")}</ol>` : ""}
          ${o.text_pe_ecran ? `<p class="small"><b>Text pe ecran:</b> ${esc(o.text_pe_ecran)}</p>` : ""}
          <p class="cap" id="${id}">${esc(o.caption)}</p>
          ${o.de_ce ? `<p class="why">De ce: ${esc(o.de_ce)}</p>` : ""}
          <div class="actions">${copyBtn(id, "Copiază textul")}</div>
        </article>`;
      }).join("")}</div>`;
      idle(`${ideas.length} idei gata.`);
    },

    async imagine() {
      const idee = val("idee");
      if (idee.length < 6) return ask("idee", "Scrie în câteva cuvinte ce vrei să vezi.");
      working("Se generează imaginea…");
      const d = await api({ idee, stil: val("stil"), caracter: val("caracter") });
      if (!d.image || !/^data:image\/(jpeg|png);base64,/.test(d.image)) throw new Error("Nu a venit nicio imagine. Încearcă din nou.");
      const id = uid();
      out.innerHTML = `<figure class="img-out" style="margin:0"><img src="${d.image}" width="1024" height="1024" alt="Imagine generată cu AI: ${esc(idee)}"><span class="ai-tag">Generat cu AI</span></figure>
        <div class="result"><span class="h4">Promptul folosit</span><pre class="code" id="${id}">${esc(d.prompt)}</pre>
        <div class="actions"><a class="btn btn-sm" href="${d.image}" download="musqai-imagine.jpg">Descarcă</a>${copyBtn(id, "Copiază promptul")}<button class="btn btn-ghost btn-sm" type="submit" form="zone-form">Încă o variantă</button></div>
        ${val("caracter") ? '<p class="muted small">Imaginea folosește doar descrierea caracterului. Fața exactă o facem în studio, cu modelul lui.</p>' : ""}</div>`;
      idle("Imaginea e gata. Are marcaj AI în fișier.");
    },

    async prompt() {
      if (!imageB64) { idle("Alege întâi o imagine.", true); if (fileInput) fileInput.click(); return; }
      working("Se uită la imagine…");
      const d = await api({ image: imageB64, tinta: val("tinta") });
      const a = uid(), b = uid();
      out.innerHTML = `<div class="result"><div class="actions" style="justify-content:space-between"><span class="h4">Promptul</span><span class="chip hot">${esc(d.tinta || "")}</span></div>
          <pre class="code" id="${a}">${esc(d.prompt)}</pre><div class="actions">${copyBtn(a, "Copiază promptul")}</div></div>
        ${d.negative ? `<div class="result"><span class="h4">Ce să eviți (negative)</span><pre class="code" id="${b}">${esc(d.negative)}</pre><div class="actions">${copyBtn(b)}</div></div>` : ""}
        ${d.setari ? `<div class="result"><span class="h4">Setări</span><p style="color:var(--text-2)">${esc(d.setari)}</p>${d.nota ? `<p class="why">${esc(d.nota)}</p>` : ""}</div>` : ""}
        ${d.descriere ? `<details class="result"><summary class="h4" style="cursor:pointer">Ce a văzut în imagine</summary><p class="muted small">${esc(d.descriere)}</p></details>` : ""}`;
      idle("Promptul e gata.");
    },

    async text() {
      const despre = val("despre");
      if (despre.length < 10) return ask("despre", "Scrie în câteva cuvinte despre ce e postarea.");
      working("Se scriu textele…");
      const d = await api({ platforma: val("platforma"), ton: val("ton"), despre, cta: val("cta"), caracter: val("caracter") });
      const vs = Array.isArray(d.variante) ? d.variante : [];
      out.innerHTML = vs.map((v, i) => {
        const id = uid();
        const tags = (v.hashtaguri || []).join(" ");
        return `<article class="result"><span class="chip">Varianta ${i + 1}</span><p class="cap" id="${id}">${esc(v.caption)}${tags ? "\n\n" + esc(tags) : ""}</p><div class="actions">${copyBtn(id, "Copiază")}</div></article>`;
      }).join("");
      idle(`${vs.length} variante gata.`);
    },

    async caracter() {
      working("Se creează caracterul…");
      const d = await api({ gen: val("gen"), varsta: Number(val("varsta")), nisa: val("nisa"), stil: val("stil"), vibe: val("vibe") });
      const f = d.fisa || {};
      const piloni = (f.piloni || []).map((p) => `<div class="pillar"><span class="h4">${esc(p.nume)}</span><span class="h4">${Number(p.procent) || 0}%</span><span class="bar"><i style="width:${Math.max(0, Math.min(100, Number(p.procent) || 0))}%"></i></span></div>`).join("");
      out.innerHTML = `<div class="sheet">
          <div class="portrait">${d.image ? `<img src="${d.image}" width="1024" height="1024" alt="Portretul caracterului ${esc(f.nume)}, generat cu AI"><span class="ai-tag">Generat cu AI</span>` : `<div class="empty" style="min-height:300px">${esc(d.imageError || "Portretul nu e disponibil.")}</div>`}</div>
          <div class="stack" style="gap:12px">
            <span class="chip hot" style="justify-self:start">${esc(f.arhetip || "Caracter nou")}</span>
            <h2 class="h2">${esc(f.nume)}<span class="muted" style="font-size:.5em"> · ${esc(f.varsta)}</span></h2>
            <p class="h4">${esc(f.rol)}</p>
            <p style="color:var(--text-2)">${esc(f.aspect)}</p>
            <p class="muted">${esc(f.stil)}</p>
            <div class="actions">${(f.personalitate || []).map((p) => `<span class="chip">${esc(p)}</span>`).join("")}</div>
          </div>
        </div>
        <div class="grid-2">
          <div class="result"><span class="h4">Vocea</span><p style="color:var(--text-2)">${esc(f.voce)}</p><span class="h4" style="margin-top:6px">Hook-uri</span><ul class="ticks">${(f.hookuri || []).map((h) => `<li>„${esc(h)}”</li>`).join("")}</ul></div>
          <div class="result"><span class="h4">Piloni de conținut</span>${piloni}</div>
        </div>
        <div class="result"><span class="h4">Îl facem real?</span><p class="muted">În studio îi creăm modelul feței, vocea și conturile, ca să arate la fel în fiecare postare.</p><div class="actions"><a class="btn btn-sm" href="/contact/">Cere o ofertă</a><button class="btn btn-ghost btn-sm" type="submit" form="zone-form">Alt caracter</button></div></div>`;
      idle(d.image ? "Caracterul e gata." : "Fișa e gata.");
    }
  };

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (busy) return;
    try {
      await ZONES[zone]();
    } catch (err) {
      idle((err && err.message) || "Ceva n-a mers. Încearcă din nou.", true);
    }
  });
  out.addEventListener("click", (e) => {
    const b = e.target.closest("[data-copy]");
    if (!b) return;
    const el = document.getElementById(b.getAttribute("data-copy"));
    if (el && window.MQcopy) window.MQcopy(el.textContent);
  });
})();
