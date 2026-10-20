/* MUSQAI: routerul paginilor, desenele caracterelor și uneltele live din Studio. */
(() => {
  "use strict";
  const D = window.MQ;
  const main = document.getElementById("view");
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  const cap = (name) =>
    window.claude && typeof window.claude.use === "function"
      ? window.claude.use(name).catch(() => null)
      : Promise.resolve(null);
  const byId = (id) => D.characters.find((c) => c.id === id);
  const STATUS = { live: "acc", casting: "gold", planned: "" };
  const DAYS = ["Luni", "Marți", "Miercuri", "Joi", "Vineri", "Sâmbătă", "Duminică"];
  /* Versiunea publică (Cloudflare) ascunde prompturile, declanșatorii LoRA și rutina internă de pe pod. */
  const PUBLIC = !!window.MQ_PUBLIC;

  const chip = (text, kind = "") => `<span class="chip ${kind}">${esc(text)}</span>`;
  const stateChip = (state, text) => {
    const map = { ok: ["ok", "●"], warn: ["warn", "▲"], bad: ["bad", "✕"], done: ["ok", "●"], doing: ["warn", "◐"], todo: ["", "○"] };
    const [kind, glyph] = map[state] || ["", "○"];
    return `<span class="chip ${kind}">${glyph} ${esc(text)}</span>`;
  };

  let toastTimer = 0;
  function toast(msg) {
    const t = $("#toast");
    t.textContent = msg;
    t.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => (t.hidden = true), 2400);
  }

  /* ---------- Portretele: un platou de studio desenat pentru fiecare caracter ---------- */
  function seeded(str) {
    let h = 2166136261;
    for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); }
    return () => {
      h += 0x6d2b79f5;
      let t = h;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function rgba(hex, a) {
    const n = parseInt(hex.slice(1), 16);
    return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
  }
  let grainTile = null;
  function grain() {
    if (grainTile) return grainTile;
    const c = document.createElement("canvas");
    c.width = c.height = 120;
    const g = c.getContext("2d");
    const img = g.createImageData(120, 120);
    const rnd = seeded("grain");
    for (let i = 0; i < img.data.length; i += 4) {
      const v = rnd() * 255;
      img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
      img.data[i + 3] = 20;
    }
    g.putImageData(img, 0, 0);
    grainTile = c;
    return c;
  }
  function drawPortrait(cv) {
    const ch = byId(cv.dataset.portrait);
    if (!ch) return;
    const variant = Number(cv.dataset.variant || 0);
    const rect = cv.getBoundingClientRect();
    const w = Math.max(40, rect.width), hh = Math.max(40, rect.height);
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    cv.width = Math.round(w * dpr);
    cv.height = Math.round(hh * dpr);
    const g = cv.getContext("2d");
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    const [deep, mid, light, glow] = ch.palette;
    const rnd = seeded(ch.id + ":" + variant);
    let rg;

    g.fillStyle = deep;
    g.fillRect(0, 0, w, hh);
    // lumina principală (softbox)
    const kx = w * (0.25 + 0.5 * rnd()), ky = hh * (0.12 + 0.18 * rnd());
    rg = g.createRadialGradient(kx, ky, 0, kx, ky, Math.max(w, hh) * 0.95);
    rg.addColorStop(0, rgba(mid, 1));
    rg.addColorStop(0.55, rgba(mid, 0.42));
    rg.addColorStop(1, rgba(mid, 0));
    g.fillStyle = rg;
    g.fillRect(0, 0, w, hh);
    // lumina de contur
    const rx = w * (rnd() < 0.5 ? 0.92 : 0.08), ry = hh * (0.3 + 0.15 * rnd());
    rg = g.createRadialGradient(rx, ry, 0, rx, ry, w * 0.75);
    rg.addColorStop(0, rgba(glow, 0.5));
    rg.addColorStop(1, rgba(glow, 0));
    g.fillStyle = rg;
    g.fillRect(0, 0, w, hh);
    // podeaua platoului
    const fy = hh * 0.72;
    const fl = g.createLinearGradient(0, fy - hh * 0.06, 0, hh);
    fl.addColorStop(0, rgba(deep, 0));
    fl.addColorStop(0.3, rgba(deep, 0.32));
    fl.addColorStop(1, rgba(deep, 0.72));
    g.fillStyle = fl;
    g.fillRect(0, fy - hh * 0.06, w, hh);

    if (variant !== 3) {
      // silueta, ca în spatele unui geam mat
      const cx = w * (variant === 2 ? 0.56 : 0.5);
      const scale = variant === 3 ? 0.7 : variant === 1 ? 1.25 : 1;
      const headY = hh * (variant === 1 ? 0.42 : 0.37), headR = Math.min(w, hh) * 0.12 * scale;
      rg = g.createRadialGradient(cx, headY, headR * 0.15, cx, headY, headR * 1.7);
      rg.addColorStop(0, rgba(deep, 0.78));
      rg.addColorStop(0.58, rgba(deep, 0.5));
      rg.addColorStop(1, rgba(deep, 0));
      g.fillStyle = rg;
      g.fillRect(0, 0, w, hh);
      g.save();
      g.translate(cx, hh * (variant === 1 ? 1.0 : 0.88));
      g.scale(1, 0.78);
      const sr = w * 0.4 * scale;
      rg = g.createRadialGradient(0, 0, sr * 0.1, 0, 0, sr);
      rg.addColorStop(0, rgba(deep, 0.85));
      rg.addColorStop(0.68, rgba(deep, 0.5));
      rg.addColorStop(1, rgba(deep, 0));
      g.fillStyle = rg;
      g.beginPath();
      g.arc(0, 0, sr, 0, Math.PI * 2);
      g.fill();
      g.restore();
    }
    // monograma
    const size = hh * (variant ? 0.46 : 0.62);
    g.font = `italic 500 ${Math.round(size)}px "Bodoni Moda", Didot, "Times New Roman", serif`;
    g.textAlign = "center";
    g.textBaseline = "alphabetic";
    g.fillStyle = rgba(light, variant ? 0.14 : 0.17);
    g.fillText(ch.name[0], w * 0.5, hh * (variant ? 0.66 : 0.78));
    // granulația filmului
    g.fillStyle = g.createPattern(grain(), "repeat");
    g.fillRect(0, 0, w, hh);
    // vignetare
    rg = g.createRadialGradient(w / 2, hh / 2, Math.min(w, hh) * 0.28, w / 2, hh / 2, Math.max(w, hh) * 0.78);
    rg.addColorStop(0, "rgba(0,0,0,0)");
    rg.addColorStop(1, "rgba(0,0,0,0.4)");
    g.fillStyle = rg;
    g.fillRect(0, 0, w, hh);
  }
  const drawAll = () => $$("canvas[data-portrait]").forEach(drawPortrait);

  /* ---------- Bucăți refolosite ---------- */
  function photo(c, i, tagText, aiText = "AI", variant = 0) {
    return `<div class="photo"><canvas data-portrait="${c.id}" data-variant="${variant}" aria-hidden="true"></canvas>${
      tagText ? `<span class="tag">${esc(tagText)}</span>` : ""
    }${aiText ? `<span class="ai">${esc(aiText)}</span>` : ""}</div>`;
  }
  function compCard(c) {
    const i = D.characters.indexOf(c);
    return `<a class="comp" href="#${c.id}">
      ${photo(c, i, "MUSQAI · 0" + (i + 1))}
      <div class="comp-body">
        <div class="comp-name">${esc(c.name)}</div>
        <div class="comp-role">${esc(c.role)}</div>
        <div class="comp-status">${chip(c.statusLabel, STATUS[c.status])}</div>
      </div>
    </a>`;
  }
  const specs = (rows) =>
    `<table class="specs"><tbody>${rows.map(([k, v]) => `<tr><th scope="row">${esc(k)}</th><td>${esc(v)}</td></tr>`).join("")}</tbody></table>`;
  const ticks = (items, no) => `<ul class="ticks${no ? " no" : ""}">${items.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>`;
  const secHead = (eyebrow, title, lead) =>
    `<div class="sec-head"><p class="eyebrow">${esc(eyebrow)}</p><h2 class="h2">${title}</h2>${lead ? `<p class="lead">${lead}</p>` : ""}</div>`;
  let copySeq = 0;
  function copyBlock(text, label = "Copiază") {
    const id = "copy-" + ++copySeq;
    return `<div class="stack" style="gap:8px"><pre class="code" id="${id}">${esc(text)}</pre><div><button class="btn btn-ghost btn-sm" type="button" data-copy="${id}">${label}</button></div></div>`;
  }

  /* ---------- Acasă ---------- */
  function viewHome() {
    const d = byId("daria");
    const n = D.niches;
    return `
    <section class="hero"><div class="wrap split">
      <div>
        <p class="eyebrow">Marketing Universe Studio · Quantum AI</p>
        <h1 class="display">Ambasadori AI pentru branduri care vor <em>să vândă</em>.</h1>
        <p class="lead">Poze și reels noi în fiecare săptămână, cu un ambasador care arată mereu la fel. Fără ședințe foto. Fiecare postare e etichetată ca AI.</p>
        <div class="row"><a class="btn" href="#contact">Cere o mostră pe produsul tău</a><a class="btn btn-ghost" href="#caractere">Vezi caracterele</a></div>
        <div class="hero-note">
          <span><b>✓</b> Etichetă AI la fiecare postare</span>
          <span><b>✓</b> Produsul arătat exact ca în realitate</span>
          <span><b>✓</b> În română, pentru piața de aici</span>
        </div>
      </div>
      <a class="comp hero-card" href="#daria">
        ${photo(d, 0, "MUSQAI · 01", "AI · declarat")}
        <div class="comp-body">
          <p class="eyebrow">Fișa de casting</p>
          <div class="comp-name">${esc(d.name)}</div>
          <div class="comp-role">${esc(d.role)}</div>
          ${specs(d.comp.slice(1, 6))}
          <div class="comp-status">${chip(d.statusLabel, "acc")}</div>
        </div>
      </a>
    </div></section>

    <section class="band band-alt"><div class="wrap">
      ${secHead("Universul MUSQAI", "Cinci caractere. Fiecare cu <em>fața, vocea și regulile</em> lui.", "Le construim pe rând, cu același proces: fișă, set de antrenare, LoRA, voce, conturi etichetate. Daria e prima.")}
      <div class="roster">${D.characters.map(compCard).join("")}</div>
    </div></section>

    <section class="band"><div class="wrap">
      ${secHead("Cum funcționează", "De la brief la postare, <em>în fiecare săptămână</em>.")}
      <ol class="steps">
        <li><span class="h3">Brief de 15 minute</span><span class="muted">Ne spui ce vinzi, cui și ce nu vrei să vezi.</span></li>
        <li><span class="h3">Mostra pe produsul tău</span><span class="muted">Vezi ambasadorul cu produsul tău înainte să plătești abonamentul.</span></li>
        <li><span class="h3">Producție săptămânală</span><span class="muted">Poze, reels, texte și variante pentru reclame.</span></li>
        <li><span class="h3">Postare și raport</span><span class="muted">Programăm la orele bune și îți arătăm ce a mers.</span></li>
      </ol>
    </div></section>

    <section class="band band-ink"><div class="wrap split">
      <div class="stack">
        <p class="eyebrow">Ce primești</p>
        <h2 class="h2">Tot ce îi trebuie unui cont care vinde, <em>gata de postat</em>.</h2>
        <p class="muted">Un singur studio în loc de fotograf, model, editor și copywriter.</p>
      </div>
      <ul class="ticks">
        <li>Poze lifestyle cu produsul tău pe ambasador</li>
        <li>Reels de 8–15 secunde, pentru organic și reclame</li>
        <li>Variante de hook pentru teste A/B</li>
        <li>Texte în română, pe vocea ambasadorului</li>
        <li>Calendarul de postare, la orele care merg pentru contul tău</li>
        <li>Raport lunar: ce a mers și ce schimbăm</li>
      </ul>
    </div></section>

    <section class="band"><div class="wrap">
      ${secHead("Nișe", "Începem cu <em>magazinele online</em>.", "Apoi imobiliare, turism și HoReCa, evenimente, wellness. Fiecare nișă are regulile ei.")}
      <div class="grid-3">
        ${n.slice(0, 3).map((x) => `<a class="panel" href="#nise" style="text-decoration:none;display:grid;gap:8px">
          <span class="eyebrow">${esc(x.code)} · ${esc(x.order)}</span><span class="h3">${esc(x.name)}</span><span class="muted small">${esc(x.pain)}</span></a>`).join("")}
      </div>
    </div></section>

    <section class="band band-alt"><div class="wrap">
      ${secHead("Pentru început", "Testează cu <em>5 creative</em>. Sau pornește direct campania.")}
      ${offerPair()}
      <p style="margin-top:22px"><a class="btn btn-ghost" href="#servicii">Toate pachetele</a></p>
    </div></section>

    <section class="band"><div class="wrap split">
      <div class="stack">
        <p class="eyebrow">Platforma</p>
        <h2 class="h2">MUSQAI Studio: <em>tot procesul</em> într-un singur loc.</h2>
        <p class="lead">Caractere, idei, generare, editare, programare și rezultate. Acum îl folosim noi pentru clienți. Mai târziu îl deschidem și pentru tine.</p>
        <div class="row"><a class="btn" href="#studio">Deschide Studio (demo)</a><a class="btn btn-ghost" href="#platforma">Modulele</a></div>
      </div>
      ${miniStudio()}
    </div></section>

    <section class="band band-ink"><div class="wrap">
      ${secHead("Transparență", "Spunem mereu că e AI. <em>Asta e regula.</em>", "Din 2 august 2026, în UE, conținutul generat cu AI care pare real trebuie etichetat. Noi o facem la fiecare postare, din prima zi.")}
      <div class="grid-3">
        <div class="stack" style="gap:6px"><span class="h3">Etichetă AI</span><span class="muted">„AI creator” în bio și eticheta AI la fiecare postare.</span></div>
        <div class="stack" style="gap:6px"><span class="h3">Fețe reale, doar cu acord</span><span class="muted">Acord scris și verificare, înainte de orice.</span></div>
        <div class="stack" style="gap:6px"><span class="h3">Fără recenzii false</span><span class="muted">Ambasadorul prezintă produsul. Nu pretinde că l-a cumpărat.</span></div>
      </div>
      <p style="margin-top:26px"><a class="btn btn-ghost" href="#transparenta">Cum lucrăm cu AI</a></p>
    </div></section>

    <section class="band"><div class="wrap split">
      <div class="stack">
        <h2 class="h2">Vrei să vezi ambasadorul <em>cu produsul tău</em>?</h2>
        <p class="lead">Trimite-ne linkul către produs. Îți arătăm cum ar arăta o reclamă nouă, fără ședință foto.</p>
      </div>
      <div class="row" style="justify-content:flex-end"><a class="btn" href="#contact">Cere o mostră</a></div>
    </div></section>`;
  }

  function offerPair() {
    const o = D.offers.entry;
    return `<div class="offer-pair">
      <div class="panel">
        <div class="plan-name"><span class="h3">${esc(o.small.name)}</span>${chip("Test", "")}</div>
        <div class="price">${esc(o.small.price)}</div>
        ${ticks(o.small.items)}
      </div>
      <div class="panel feat">
        <div class="plan-name"><span class="h3">${esc(o.full.name)}</span>${chip("Recomandat", "acc")}</div>
        <div class="price">${esc(o.full.price)}</div>
        ${ticks(o.full.items)}
      </div>
    </div>`;
  }

  function miniStudio() {
    const k = D.demo.kpis;
    return `<a class="panel" href="#studio" style="text-decoration:none;display:grid;gap:14px;box-shadow:var(--shadow)">
      <div class="row" style="justify-content:space-between"><span class="eyebrow">MUSQAI Studio · panou</span>${chip("Demo", "")}</div>
      <div class="grid-2">${k.slice(0, 4).map(([a, b, c]) => `<div class="kpi"><span>${esc(a)}</span><b>${esc(b)}</b><span>${esc(c)}</span></div>`).join("")}</div>
      <ul class="list">${D.demo.today.slice(0, 3).map(([t, x, a, s]) => `<li><span class="mono tnum">${esc(t)}</span><span>${esc(x)}</span>${stateChip(s === "doing" ? "doing" : "todo", a)}</li>`).join("")}</ul>
    </a>`;
  }

  /* ---------- Caractere ---------- */
  function viewRoster() {
    return `
    <section class="band" style="padding-top:48px"><div class="wrap">
      ${secHead("Caracterele casei", "Universul <em>MUSQAI</em>.", "Fiecare caracter e fictiv, adult și are o fișă fixă: aspect, stil, voce, nișe și reguli. Așa arată la fel în fiecare imagine.")}
      <div class="roster-lg">${D.characters.map(compCard).join("")}</div>
    </div></section>
    <section class="band band-alt"><div class="wrap split" style="align-items:start">
      <div class="stack">
        <p class="eyebrow">Caracterul tău</p>
        <h2 class="h2">Un ambasador <em>doar al tău</em>.</h2>
        <p class="lead">Pornim de la brandul tău și construim un caracter pe care îl folosești doar tu. Durează 2–3 săptămâni.</p>
        <p><a class="btn" href="#contact">Vreau un caracter exclusiv</a></p>
      </div>
      <ol class="steps" style="grid-template-columns:minmax(0,1fr)">
        <li><span class="h3">Fișa</span><span class="muted">Aspect, stil, personalitate, voce, nișe, ce nu face niciodată.</span></li>
        <li><span class="h3">40 de fețe, alegi una</span><span class="muted">Generăm variante până găsim fața potrivită.</span></li>
        <li><span class="h3">Setul de antrenare</span><span class="muted">34 de imagini: față, studio și poze de telefon.</span></li>
        <li><span class="h3">Modelul caracterului (LoRA)</span><span class="muted">Fața rămâne aceeași în orice scenă.</span></li>
        <li><span class="h3">Vocea și conturile</span><span class="muted">Voce proprie, conturi etichetate AI, primele 9 postări.</span></li>
      </ol>
    </div></section>
    <section class="band"><div class="wrap grid-2">
      <div class="panel"><h3 class="h3">Reguli pentru orice caracter</h3>${ticks(["Adult clar, 25+ de ani", "Fictiv: nu seamănă intenționat cu nicio persoană reală", "Fișă scrisă, aceeași în fiecare prompt", "Voce proprie, salvată", "Conturi etichetate AI"])}</div>
      <div class="panel"><h3 class="h3">Fețe reale</h3><p class="muted">Lucrăm cu fața unei persoane reale doar cu acordul ei scris și după verificare. Acordul se păstrează în registrul de acorduri și poate fi retras oricând.</p></div>
    </div></section>`;
  }

  function viewCharacter(c) {
    const i = D.characters.indexOf(c);
    const prev = D.characters[(i + D.characters.length - 1) % D.characters.length];
    const next = D.characters[(i + 1) % D.characters.length];
    const done = c.pipeline.filter((p) => p[1] === "done").length;
    const gen = PUBLIC
      ? ""
      : `<div class="sec-head" style="margin-bottom:0"><p class="eyebrow">Pentru generare</p><h2 class="h2">Descrierea fixă <em>din fiecare prompt</em>.</h2><p class="lead">Declanșatorul LoRA e <b class="mono" style="font-size:15px">${esc(c.prompt.split(",")[0])}</b>. Textul de mai jos se copiază identic la fiecare imagine.</p></div>
      ${copyBlock(c.prompt, "Copiază promptul")}
      <div class="stack" style="gap:6px"><p class="eyebrow">Negative prompt</p>${copyBlock(c.negative, "Copiază")}</div>`;
    return `
    <section class="band" style="padding-top:36px"><div class="wrap">
      <p class="eyebrow" style="margin-bottom:22px"><a href="#caractere">Caractere</a> / ${esc(c.name)}</p>
      <div class="char-hero">
        <div>
          ${photo(c, i, "MUSQAI · 0" + (i + 1), "AI · declarat")}
          <div class="digitals">
            ${["Față", "Profil", "Corp întreg"].map((t, k) => `<figure>${photo(c, i, "", "", k + 1)}<figcaption>${t}</figcaption></figure>`).join("")}
          </div>
        </div>
        <div class="stack" style="gap:20px">
          <div class="row">${chip(c.statusLabel, STATUS[c.status])}${chip(c.handle)}</div>
          <h1 class="display" style="font-size:clamp(60px,9vw,120px)">${esc(c.name)}</h1>
          <p class="h3" style="font-weight:600">${esc(c.role)} · <span class="muted">${esc(c.archetype)}</span></p>
          <p class="lead">${esc(c.summary)}</p>
          ${specs(PUBLIC ? c.comp.filter(([k]) => k !== "Declanșator") : c.comp)}
        </div>
      </div>
    </div></section>

    <section class="band band-alt"><div class="wrap grid-2">
      <div class="panel stack">
        <h3 class="h3">Aspectul fix</h3>
        <p>${esc(c.look)}</p>
        <h3 class="h3" style="margin-top:8px">Stilul</h3>
        <p class="muted">${esc(c.style)}</p>
        <div class="row">${c.personality.map((p) => chip(p, "acc")).join("")}</div>
      </div>
      <div class="panel stack">
        <h3 class="h3">Vocea</h3>
        <p>${esc(c.voice.desc)}</p>
        ${PUBLIC ? "" : `<p class="eyebrow">Descrierea pentru ElevenLabs Voice Design</p>${copyBlock(c.voice.design)}`}
      </div>
    </div></section>

    <section class="band"><div class="wrap split" style="align-items:start">
      <div class="stack">
        <p class="eyebrow">Piloni de conținut</p>
        <h2 class="h2">Despre ce <em>postează</em>.</h2>
        <div>${c.pillars.map(([name, pct, ex]) => `<div class="pillar"><span class="h3" style="font-size:16px">${esc(name)}</span><span class="mono tnum" style="text-align:right">${pct}%</span><span class="bar"><i style="width:${pct}%"></i></span><span class="ex">Ex.: ${esc(ex)}</span></div>`).join("")}</div>
      </div>
      <div class="stack" style="gap:22px">
        <div class="panel"><h3 class="h3">Hook-uri de test</h3><ul class="ticks">${c.hooks.map((x) => `<li>„${esc(x)}”</li>`).join("")}</ul></div>
        <div class="panel"><h3 class="h3">Nișe</h3><div class="row" style="margin-top:8px">${c.niches.map((x) => chip(x)).join("")}</div>
          <h3 class="h3" style="margin-top:16px">Program</h3><p class="muted">${esc(c.schedule)}</p>
          <h3 class="h3" style="margin-top:16px">Platforme</h3><p class="muted">${c.platforms.map(esc).join(" · ")}</p></div>
      </div>
    </div></section>

    <section class="band band-alt"><div class="wrap grid-2">
      <div class="panel stack">
        <h3 class="h3">Ce face</h3>${ticks(c.rules.do)}
        <h3 class="h3" style="margin-top:6px">Ce nu face niciodată</h3>${ticks(c.rules.dont, true)}
      </div>
      <div class="panel">
        <div class="row" style="justify-content:space-between;margin-bottom:8px"><h3 class="h3">Producția</h3><span class="mono tnum">${done} / ${c.pipeline.length}</span></div>
        <ul class="pipe">${c.pipeline.map(([name, st]) => `<li><span class="dot ${st}">${st === "done" ? "✓" : ""}</span><span>${esc(name)}</span>${stateChip(st, st === "done" ? "gata" : st === "doing" ? "în lucru" : "urmează")}</li>`).join("")}</ul>
      </div>
    </div></section>

    <section class="band"><div class="wrap stack" style="gap:22px">
      ${gen}
      <div class="char-nav"><a class="btn btn-ghost" href="#${prev.id}">← ${esc(prev.name)}</a><a class="btn btn-ghost" href="#${next.id}">${esc(next.name)} →</a></div>
    </div></section>`;
  }

  /* ---------- Servicii ---------- */
  function viewServices() {
    return `
    <section class="band" style="padding-top:48px"><div class="wrap">
      ${secHead("Servicii și prețuri", "Începi mic. <em>Crești când vezi rezultate.</em>", "Prețurile de mai jos sunt de test pentru primii clienți. Le confirmăm după primele 10 discuții.")}
      ${offerPair()}
      <div class="panel" style="margin-top:20px;display:grid;gap:8px">
        <span class="eyebrow">Garanția</span>
        <p class="h3" style="font-weight:600">${esc(D.offers.guarantee)}</p>
      </div>
    </div></section>
    <section class="band band-alt"><div class="wrap">
      ${secHead("Abonamente", "Conținut nou, <em>în fiecare lună</em>.", "Facturare la 4 săptămâni. " + esc(D.offers.prepay))}
      <div class="grid-3">${D.packages.map((p) => `<div class="panel${p.featured ? " feat" : ""}">
        <div class="plan-name"><span class="h3">${esc(p.name)}</span>${p.featured ? chip("Cel mai ales", "acc") : ""}</div>
        <div class="price">${esc(p.price)} <small>${esc(p.per)}</small></div>
        <p class="muted small">${esc(p.note)}</p>
        ${ticks(p.items)}
      </div>`).join("")}</div>
    </div></section>
    <section class="band"><div class="wrap split" style="align-items:start">
      <div class="stack"><p class="eyebrow">Extra</p><h2 class="h2">Adaugi doar <em>ce-ți trebuie</em>.</h2></div>
      <div class="extras">${D.extras.map(([a, b]) => `<div><span class="h3" style="font-size:16px">${esc(a)}</span><span class="muted small">${esc(b)}</span></div>`).join("")}</div>
    </div></section>
    <section class="band band-alt"><div class="wrap split" style="align-items:start">
      <div class="stack"><p class="eyebrow">Întrebări</p><h2 class="h2">Ce ne întreabă <em>toată lumea</em>.</h2></div>
      <div class="faq">${D.faq.map(([q, a]) => `<details><summary>${esc(q)}</summary><p>${esc(a)}</p></details>`).join("")}</div>
    </div></section>`;
  }

  /* ---------- Nișe ---------- */
  function viewNiches() {
    const avail = ["Disponibil acum", "Din decembrie", "Din ianuarie", "În curând", "În curând"];
    return `
    <section class="band" style="padding-top:48px"><div class="wrap">
      ${secHead("Nișe", "Unde aduce un ambasador AI <em>cel mai mult</em>.", "Pornim cu o nișă, o facem bine, apoi trecem la următoarea. Fiecare are regulile ei, scrise înainte de primul livrabil.")}
      ${D.niches.map((x, k) => {
        const ch = byId(x.character);
        return `<article class="niche">
          <div class="code">${esc(x.code)}</div>
          <div>
            <div class="row" style="justify-content:space-between"><h2 class="h2" style="font-size:clamp(26px,3.4vw,38px)">${esc(x.name)}</h2>${chip(avail[k], k === 0 ? "acc" : "")}</div>
            <p class="lead" style="margin-top:8px">${esc(x.who)} ${esc(x.pain)}</p>
            <div class="niche-cols">
              <div><h4>Ce livrăm</h4>${ticks(x.deliver)}</div>
              <div><h4>Reguli</h4>${ticks(x.rules)}</div>
              <div><h4>Ce măsurăm</h4><p>${esc(x.metric)}</p><h4 style="margin-top:16px">Ambasador</h4><p><a href="#${ch.id}">${esc(ch.name)}</a>, ${esc(ch.role.toLowerCase())}</p></div>
            </div>
          </div>
        </article>`;
      }).join("")}
    </div></section>`;
  }

  /* ---------- Cum lucrăm ---------- */
  function viewHow() {
    return `
    <section class="band" style="padding-top:48px"><div class="wrap">
      ${secHead("Cum lucrăm", "Linia de producție, <em>pas cu pas</em>.", "Fiecare livrabil trece prin aceiași nouă pași. Nimic nu pleacă la client fără verificare.")}
      <ol class="steps">${D.steps.map(([a, b, t]) => `<li><span class="h3">${esc(a)}</span><span class="muted">${esc(b)}</span><span class="tool">${esc(t)}</span></li>`).join("")}</ol>
    </div></section>
    <section class="band band-alt"><div class="wrap split" style="align-items:start">
      <div class="stack"><p class="eyebrow">Primele 30 de zile</p><h2 class="h2">Ce se întâmplă <em>după ce semnăm</em>.</h2><p class="lead">Ai materialele în prima săptămână și cifrele în a doua.</p></div>
      <ul class="pipe">${D.timeline.map(([d, t]) => `<li><span class="dot done">✓</span><span><b>${esc(d)}</b> · ${esc(t)}</span><span></span></li>`).join("")}</ul>
    </div></section>
    <section class="band"><div class="wrap grid-2">
      <div class="panel"><h3 class="h3">Ce ne dai tu</h3>${ticks(D.clientGives)}</div>
      <div class="panel"><h3 class="h3">Ce primești de la noi</h3>${ticks(["Două runde de revizii la fiecare livrabil", "Fișierele în folderul tău, denumite clar", "Postările programate la orele bune", "Raportul lunar, cu recomandări"])}</div>
    </div></section>
    <section class="band band-ink"><div class="wrap split">
      <div class="stack"><h2 class="h2">Vrei să vezi procesul <em>din interior</em>?</h2><p class="muted">În Studio găsești toate cele zece procese, cu pași, unelte și durate.</p></div>
      <div class="row" style="justify-content:flex-end"><a class="btn" href="#studio-procese">Vezi procesele</a></div>
    </div></section>`;
  }

  /* ---------- Platforma ---------- */
  function viewPlatform() {
    const svc = [
      ["Claude", "texte, idei, image-to-prompt, skill-uri"],
      ["GPU la cerere", "workflow-urile ComfyUI (RunPod)"],
      ["Video din cloud", "Seedance, Kling, când merită"],
      ["Randare automată", "reels montate din șabloane"],
      ["Publicare", "Instagram și TikTok, prin API"],
      ["Plăți și credite", "Stripe"]
    ];
    return `
    <section class="band" style="padding-top:48px"><div class="wrap">
      ${secHead("Platforma", "Opt module. <em>Un singur flux.</em>", "Le construim în ordinea în care ne ajută la clienți: întâi pentru noi, apoi pentru tine.")}
      <div class="modules">${D.modules.map((m, k) => `<div class="panel module">
        <span class="num">${String(k + 1).padStart(2, "0")}</span>
        <span class="h3">${esc(m.name)}</span>
        <p class="muted small">${esc(m.job)}</p>
        <dl><dt>F1 · INTERN</dt><dd>${esc(m.f1)}</dd><dt>F2 · CLIENȚI</dt><dd>${esc(m.f2)}</dd><dt>F3 · SCALARE</dt><dd>${esc(m.f3)}</dd></dl>
      </div>`).join("")}</div>
    </div></section>
    <section class="band band-alt"><div class="wrap">
      ${secHead("Fazele", "Construim <em>ce s-a vândut deja</em>.")}
      <div class="phases">${D.phases.map(([a, b, c]) => `<div><b>${esc(a)}</b><span class="eyebrow">${esc(b)}</span><span class="muted small">${esc(c)}</span></div>`).join("")}</div>
    </div></section>
    <section class="band"><div class="wrap">
      ${secHead("Arhitectura", "Cum se leagă <em>piesele</em>.")}
      <div class="diagram">
        <div style="display:grid;gap:12px;min-width:560px">
          <div class="row" style="justify-content:center"><span class="chip">Clientul · web și telefon</span></div>
          <div style="text-align:center" class="muted mono">↓</div>
          <div class="panel" style="text-align:center;border-color:var(--accent)"><span class="h3">Aplicația MUSQAI</span><p class="muted small">Next.js · conturi, bază de date și fișiere (Supabase) · statistici de utilizare</p></div>
          <div style="text-align:center" class="muted mono">↓ ↓ ↓</div>
          <div class="grid-3" style="gap:10px">${svc.map(([a, b]) => `<div class="panel" style="padding:14px"><span class="h3" style="font-size:15px">${esc(a)}</span><p class="muted small">${esc(b)}</p></div>`).join("")}</div>
          <div style="text-align:center" class="muted mono">↓</div>
          <div class="grid-2" style="gap:10px">
            <div class="panel" style="padding:14px"><span class="h3" style="font-size:15px">Rezultate → învățare</span><p class="muted small">fiecare postare etichetată și măsurată</p></div>
            <div class="panel" style="padding:14px"><span class="h3" style="font-size:15px">Conformitate</span><p class="muted small">etichete AI, C2PA, acorduri, filtre de conținut</p></div>
          </div>
        </div>
      </div>
      <p style="margin-top:24px"><a class="btn" href="#studio">Deschide Studio (demo)</a></p>
    </div></section>`;
  }

  /* ---------- Transparență ---------- */
  function viewTransparency() {
    return `
    <section class="band" style="padding-top:48px"><div class="wrap">
      ${secHead("Transparență AI", "Cum lucrăm cu AI, <em>pe față</em>.", "Ambasadorii MUSQAI sunt generați cu AI. Asta nu e un secret, e regula de la care pornim.")}
      <div class="grid-2">
        <div class="panel"><h3 class="h3">Etichetăm tot</h3><p class="muted">Fiecare cont are „AI creator” în bio. Fiecare postare are eticheta AI a platformei. În platformă adăugăm și marcajul în fișier (C2PA), ca să poată fi recunoscut automat.</p></div>
        <div class="panel"><h3 class="h3">AI Act, articolul 50</h3><p class="muted">Din 2 august 2026, în UE, imaginile, clipurile și sunetele generate cu AI care par reale trebuie marcate ca atare. Cine oferă un generator trebuie să pună un marcaj citibil de mașină.</p></div>
        <div class="panel"><h3 class="h3">Fețe reale, doar cu acord</h3><p class="muted">Folosim fața sau vocea unei persoane reale doar cu acordul ei scris și după verificare. Acordul poate fi retras oricând.</p></div>
        <div class="panel"><h3 class="h3">Fără recenzii false</h3><p class="muted">Ambasadorul prezintă produsul. Nu spune că l-a cumpărat, nu dă note și nu se prezintă drept client mulțumit.</p></div>
        <div class="panel"><h3 class="h3">Date personale</h3><p class="muted">Cerem doar datele de care avem nevoie, cu acord explicit. Pentru învățare folosim doar date anonimizate. Semnăm contracte de prelucrare a datelor cu furnizorii care lucrează cu datele clienților.</p></div>
        <div class="panel"><h3 class="h3">Modele cu licență</h3><p class="muted">Folosim modele care permit utilizarea comercială și verificăm licența fiecăruia înainte să-l folosim pentru clienți.</p></div>
      </div>
    </div></section>
    <section class="band band-alt"><div class="wrap split" style="align-items:start">
      <div class="stack"><p class="eyebrow">Ce nu facem niciodată</p><h2 class="h2">Liniile <em>pe care nu le trecem</em>.</h2></div>
      ${ticks(["Conținut NSFW", "Fețe reale fără acord scris", "Persoane care par minore", "Mărturii sau recenzii false", "Promisiuni medicale sau de rezultat corporal", "Conținut politic"], true)}
    </div></section>`;
  }

  /* ---------- Contact ---------- */
  function viewContact() {
    const v = (val, ph) => (PUBLIC ? `placeholder="${esc(ph)}"` : `value="${esc(val)}"`);
    return `
    <section class="band" style="padding-top:48px"><div class="wrap split" style="align-items:start">
      <div class="stack" style="gap:20px">
        ${secHead("Contact", "Cere o mostră <em>pe produsul tău</em>.", "Îți răspundem în 24 de ore, în zilele lucrătoare.")}
        <ul class="pipe">
          <li><span class="dot done">1</span><span>Ne trimiți linkul către produs</span><span></span></li>
          <li><span class="dot done">2</span><span>Facem un apel de 15 minute</span><span></span></li>
          <li><span class="dot done">3</span><span>Primești mostra în 3–5 zile lucrătoare</span><span></span></li>
        </ul>
        <div class="panel"><p class="eyebrow">Direct</p><p class="h3" style="margin-top:6px">${esc(D.brand.email)}</p><p class="muted">Instagram ${esc(D.brand.instagram)}</p></div>
      </div>
      <div class="panel" id="contact-box">
        <form class="form" id="contact-form" novalidate>
          <div class="grid-2" style="gap:12px">
            <div class="field"><label for="cf-name">Numele tău</label><input id="cf-name" name="name" autocomplete="name" ${v("Ana Popescu", "Numele și prenumele")} required></div>
            <div class="field"><label for="cf-company">Firma</label><input id="cf-company" name="company" autocomplete="organization" ${v("Atelier Satin", "Numele firmei")}></div>
          </div>
          <div class="field"><label for="cf-link">Site sau Instagram</label><input id="cf-link" name="link" ${v("instagram.com/ateliersatin", "site.ro sau instagram.com/brand")}></div>
          <div class="grid-2" style="gap:12px">
            <div class="field"><label for="cf-niche">Nișa</label><select id="cf-niche" name="niche">${D.niches.map((n) => `<option>${esc(n.name)}</option>`).join("")}</select></div>
            <div class="field"><label for="cf-want">Ce te interesează</label><select id="cf-want" name="want"><option>5 creative AI (99 €)</option><option>Lansarea completă (490 €)</option><option>Abonament lunar</option><option>Caracter exclusiv</option></select></div>
          </div>
          <div class="field"><label for="cf-msg">Ce vrei să vinzi?</label><textarea id="cf-msg" name="msg"${PUBLIC ? ' placeholder="Produsul, linkul către el și ce vrei să obții."' : ""}>${PUBLIC ? "" : "Rochia de satin champagne, colecția de toamnă. Reclamele noastre sunt doar poze pe fundal alb."}</textarea></div>
          <div><button class="btn" type="submit">Trimite cererea</button></div>
          <p class="muted small">${PUBLIC ? "Butonul deschide aplicația ta de email, cu cererea completată." : "Formular demo: în varianta live, cererea ajunge direct în tabelul de vânzări."}</p>
        </form>
      </div>
    </div></section>`;
  }

  /* ---------- Studio (demo) ---------- */
  const RAIL = [
    ["studio", "Panou", "◧"],
    ["studio-caractere", "Caractere", "◎"],
    ["studio-idei", "Content Brain", "✦"],
    ["studio-prompt", "Image → Prompt", "⇄"],
    ["studio-calendar", "Calendar și ore", "▦"],
    ["studio-procese", "Procese", "≡"],
    ["studio-rezultate", "Rezultate", "↗"],
    ["studio-conformitate", "Conformitate", "✓"]
  ];
  function studio(id, title, note, body) {
    return `<div class="studio">
      <nav class="rail" aria-label="Studio"><span class="eyebrow">MUSQAI Studio</span>${RAIL.map(([k, n, ico]) => `<a href="#${k}" class="${k === id ? "on" : ""}"><span class="ico">${ico}</span>${n}</a>`).join("")}</nav>
      <div class="app">
        <div class="app-head"><div class="stack" style="gap:4px"><span class="eyebrow">Studio · demo</span><h1>${title}</h1></div><span class="demo-note">${note}</span></div>
        ${body}
      </div>
    </div>`;
  }

  function viewStudioHome() {
    const k = D.demo;
    return studio("studio", "Panou", "Exemplu: datele sunt demonstrative", `
      <div class="kpis">${k.kpis.map(([a, b, c]) => `<div class="panel kpi"><span>${esc(a)}</span><b>${esc(b)}</b><span>${esc(c)}</span></div>`).join("")}</div>
      <div class="grid-2" style="align-items:start">
        <div class="panel"><div class="row" style="justify-content:space-between"><h3 class="h3">Azi</h3><a class="small" href="#studio-calendar">Calendarul</a></div>
          <ul class="list">${k.today.map(([t, x, a, s]) => `<li><span class="mono tnum">${esc(t)}</span><span>${esc(x)} <span class="muted small">· ${esc(a)}</span></span>${stateChip(s === "doing" ? "doing" : "todo", s === "doing" ? "în lucru" : "urmează")}</li>`).join("")}</ul>
        </div>
        <div class="panel"><h3 class="h3">Atenție</h3>
          <ul class="alerts" style="margin-top:12px">${k.alerts.map(([t, s]) => `<li>${stateChip(s, s === "ok" ? "OK" : "verifică")}<span>${esc(t)}</span></li>`).join("")}</ul>
          <h3 class="h3" style="margin-top:18px">Caractere</h3>
          <ul class="list">${D.characters.map((c) => { const d = c.pipeline.filter((p) => p[1] === "done").length; return `<li><span class="mono tnum">${d}/${c.pipeline.length}</span><a href="#${c.id}">${esc(c.name)}</a>${chip(c.status === "live" ? "în lucru" : c.status === "casting" ? "casting" : "planificat", STATUS[c.status])}</li>`; }).join("")}</ul>
        </div>
      </div>
      <div class="stack"><h3 class="h3">Livrabile</h3>
        <div class="board">${k.board.map(([col, cards]) => `<div class="col"><h4><span>${esc(col)}</span><span class="mono">${cards.length}</span></h4>${cards.map(([t, c]) => `<div class="card"><span>${esc(t)}</span><small>${esc(c.toUpperCase())}</small></div>`).join("")}</div>`).join("")}</div>
      </div>`);
  }

  function viewStudioChars() {
    return studio("studio-caractere", "Caractere", "Starea reală a producției", `
      <div class="tbl-wrap"><table class="tbl"><thead><tr><th>Caracter</th><th>Rol</th>${PUBLIC ? "" : "<th>Declanșator</th>"}<th>Producție</th><th>Stare</th></tr></thead><tbody>
      ${D.characters.map((c) => { const d = c.pipeline.filter((p) => p[1] === "done").length; const pct = Math.round((d / c.pipeline.length) * 100);
        return `<tr><td><a href="#${c.id}"><b>${esc(c.name)}</b></a>, ${c.age}</td><td>${esc(c.role)}</td>${PUBLIC ? "" : `<td class="mono">${esc(c.prompt.split(",")[0])}</td>`}
        <td style="min-width:150px"><div class="pillar" style="border:0;padding:0"><span class="small">${d} din ${c.pipeline.length} pași</span><span class="mono tnum" style="text-align:right">${pct}%</span><span class="bar"><i style="width:${pct}%"></i></span></div></td>
        <td>${chip(c.statusLabel, STATUS[c.status])}</td></tr>`; }).join("")}
      </tbody></table></div>
      <div class="roster">${D.characters.map(compCard).join("")}</div>`);
  }

  function ideaCard(o, idx, example, saved) {
    const shots = Array.isArray(o.cadre) ? o.cadre : [];
    return `<article class="panel idea">
      <div class="row" style="justify-content:space-between">${chip(o.ora ? "postare la " + o.ora : "idee", "acc")}${example ? chip("Exemplu") : ""}</div>
      <span class="eyebrow">${esc(o.titlu || "")}</span>
      <p class="hook">„${esc(o.hook || "")}”</p>
      ${shots.length ? `<ol>${shots.map((s) => `<li>${esc(s)}</li>`).join("")}</ol>` : ""}
      ${o.text_pe_ecran ? `<p class="small"><b>Text pe ecran:</b> ${esc(o.text_pe_ecran)}</p>` : ""}
      ${o.caption ? `<p class="cap">${esc(o.caption)}</p>` : ""}
      ${o.de_ce ? `<p class="why">De ce: ${esc(o.de_ce)}</p>` : ""}
      ${saved ? `<div><button class="btn btn-ghost btn-sm" type="button" data-del="${esc(saved)}">Șterge din bancă</button></div>`
        : example ? "" : `<div><button class="btn btn-ghost btn-sm" type="button" data-save="${idx}" hidden>Salvează în banca de idei</button></div>`}
    </article>`;
  }

  function viewStudioIdeas() {
    return studio("studio-idei", "Content Brain", "Generare live cu Claude", `
      <form class="panel form" id="cb-form">
        <div class="form-row">
          <div class="field"><label for="cb-char">Caracter</label><select id="cb-char" name="char">${D.characters.map((c) => `<option value="${c.id}">${esc(c.name)} · ${esc(c.role)}</option>`).join("")}</select></div>
          <div class="field"><label for="cb-niche">Nișă</label><select id="cb-niche" name="niche">${D.niches.map((n) => `<option value="${n.id}">${esc(n.name)}</option>`).join("")}</select></div>
          <div class="field"><label for="cb-format">Format</label><select id="cb-format" name="format"><option>Reel 8–15 s</option><option>Carusel</option><option>Story</option><option>Reclamă 9:16</option></select></div>
        </div>
        <div class="field"><label for="cb-brief">Brief: produsul, publicul, ce vrei să obții</label>
          <textarea id="cb-brief" name="brief">Rochie midi din satin champagne, brand românesc, 349 lei. Public: femei 24–35 din orașele mari. Vrem vânzări din reclame, nu doar like-uri.</textarea></div>
        <div class="row">
          <div class="field" style="min-width:140px"><label for="cb-count">Câte idei</label><select id="cb-count" name="count"><option>3</option><option selected>5</option><option>8</option></select></div>
          <div class="row" style="align-self:end"><button class="btn" id="cb-go" type="submit">Generează idei</button><button class="btn btn-ghost" id="cb-stop" type="button" hidden>Oprește</button></div>
        </div>
        <p class="status-line" id="cb-status" role="status" aria-live="polite"></p>
      </form>
      <div class="ideas" id="cb-out">${D.demo.ideas.map((o, i) => ideaCard(o, i, true)).join("")}</div>
      <section class="stack" id="bank" hidden>
        <div class="row" style="justify-content:space-between"><h3 class="h3">Banca de idei</h3><span class="muted small" id="bank-count"></span></div>
        <div class="ideas" id="bank-list"></div>
      </section>`);
  }

  function viewStudioPrompt() {
    const ex = D.demo.examplePrompt;
    return studio("studio-prompt", "Image → Prompt", "Urci o imagine, primești promptul", `
      <div class="grid-2" style="align-items:start">
        <div class="stack">
          <label class="drop" id="i2p-drop" for="i2p-file">
            <span class="h3">Trage aici o imagine</span>
            <span class="muted small">sau apasă ca s-o alegi · JPG, PNG, WebP</span>
            <img id="i2p-preview" alt="Imaginea aleasă" hidden>
          </label>
          <input id="i2p-file" type="file" accept="image/jpeg,image/png,image/webp,image/gif" hidden>
          <div class="panel form">
            <div class="field"><label for="i2p-target">Pentru ce generator</label><select id="i2p-target"><option>Krea 2 + LoRA (ComfyUI)</option><option>Nano Banana</option><option>Seedance / Kling (video)</option><option>Midjourney</option></select></div>
            <div class="field"><label for="i2p-char">Pune caracterul în locul persoanei</label><select id="i2p-char"><option value="">Nu, descrie imaginea așa cum e</option>${D.characters.map((c) => `<option value="${c.id}">${esc(c.name)}${PUBLIC ? "" : ` (${esc(c.prompt.split(",")[0])})`}</option>`).join("")}</select></div>
            <div class="row"><button class="btn" id="i2p-go" type="button">Scrie promptul</button><button class="btn btn-ghost" id="i2p-stop" type="button" hidden>Oprește</button></div>
            <p class="status-line" id="i2p-status" role="status" aria-live="polite"></p>
          </div>
        </div>
        <div class="panel out" id="i2p-out">${promptOut(ex, true)}</div>
      </div>`);
  }
  function promptOut(o, example) {
    return `<div class="copy-row"><h3 class="h3">Promptul</h3>${example ? chip("Exemplu") : chip("Gata", "ok")}</div>
      ${copyBlock(o.prompt || "", "Copiază promptul")}
      ${o.negative ? `<p class="eyebrow">Negative</p>${copyBlock(o.negative, "Copiază")}` : ""}
      ${o.setari ? `<p class="small"><b>Setări:</b> ${esc(o.setari)}</p>` : ""}
      ${o.note ? `<p class="muted small">${esc(o.note)}</p>` : ""}`;
  }

  function bucket(v) { return v >= 85 ? 5 : v >= 70 ? 4 : v >= 55 ? 3 : v >= 40 ? 2 : v >= 25 ? 1 : 0; }
  function viewStudioCalendar() {
    const k = D.demo;
    const flat = k.heat.flat().slice().sort((a, b) => b - a);
    const top3 = flat[2];
    return studio("studio-calendar", "Calendar și ore", "Exemplu: săptămâna Dariei", `
      <div class="week">${DAYS.map((d, i) => `<div class="day"><h4>${d}</h4>
        ${k.calendar.filter((p) => p.day === i).map((p) => `<div class="post ${p.status === "draft" ? "draft" : p.status === "idee" ? "idee" : ""}"><b>${esc(p.time)} · ${esc(p.type)}</b><span>${esc(p.title)}</span><span class="small muted">${esc(p.status)}</span></div>`).join("")}
        <div class="story">Stories · 1–3</div></div>`).join("")}</div>
      <div class="panel stack">
        <div class="row" style="justify-content:space-between;align-items:end">
          <div class="stack" style="gap:2px"><h3 class="h3">Când reacționează urmăritorii Dariei</h3><span class="muted small">Indice de interacțiune pe zi și oră, din 0 la 100. Punctul marchează cele mai bune 3 ferestre.</span></div>
          <div class="legend"><span>scăzut</span><span class="ramp">${[0, 1, 2, 3, 4, 5].map((b) => `<i style="background:var(--h${b})"></i>`).join("")}</span><span>ridicat</span></div>
        </div>
        <div class="heat-wrap" id="heat-wrap">
          <div class="heat" role="grid" aria-label="Interacțiune pe zi și oră">
            <span></span>${k.heatHours.map((h) => `<span class="hh">${h}:00</span>`).join("")}
            ${k.heat.map((row, r) => `<span class="hl">${DAYS[r].slice(0, 2)}</span>${row.map((v, c) => { const b = bucket(v); return `<button type="button" class="cell${v >= top3 ? " best" : ""}" style="background:var(--h${b})" data-tip="${DAYS[r]}, ${k.heatHours[c]}:00 · indice ${v}" aria-label="${DAYS[r]}, ora ${k.heatHours[c]}, indice ${v}"></button>`; }).join("")}`).join("")}
          </div>
          <div class="tip" id="heat-tip" hidden></div>
        </div>
        <details><summary class="small" style="cursor:pointer">Vezi ca tabel</summary>
          <div class="tbl-wrap" style="margin-top:10px"><table class="tbl"><thead><tr><th>Zi</th>${k.heatHours.map((h) => `<th class="n">${h}:00</th>`).join("")}</tr></thead><tbody>
          ${k.heat.map((row, r) => `<tr><td>${DAYS[r]}</td>${row.map((v) => `<td class="n">${v}</td>`).join("")}</tr>`).join("")}</tbody></table></div>
        </details>
        <p class="small"><b>Ce facem cu asta:</b> postările importante merg joi și marți la 20:00. Caruselele, la 12:00. Ferestrele se recalculează în fiecare lună, din datele contului.</p>
      </div>`);
  }

  function viewStudioProcesses() {
    return studio("studio-procese", "Procese", "Cele 10 procese ale studioului", `
      <div class="proc-list">${D.processes.filter((p) => !(PUBLIC && p.id === "pod")).map((p, i) => `<details class="panel proc"${i === 0 ? " open" : ""}>
        <summary><span class="stack" style="gap:2px"><span class="h3">${esc(p.name)}</span><span class="muted small">${p.steps.length} pași</span></span><span class="meta">${chip(p.area, "acc")}${chip(p.time)}</span></summary>
        <ol>${p.steps.map(([s, who, tool, dur]) => `<li><span>${esc(s)}</span><span class="who">${chip(who, who === "Client" ? "gold" : who.includes("Claude") || who.includes("Agent") ? "acc" : "")}</span><span class="tool">${esc(tool)}</span><span class="dur">${esc(dur)}</span></li>`).join("")}</ol>
      </details>`).join("")}</div>`);
  }

  function viewStudioResults() {
    const p = D.demo.posts;
    const reach = p.reduce((s, x) => s + x[3], 0), saves = p.reduce((s, x) => s + x[5], 0), shares = p.reduce((s, x) => s + x[6], 0);
    const fmt = (n) => n.toLocaleString("ro-RO");
    return studio("studio-rezultate", "Rezultate", "Exemplu: datele sunt demonstrative", `
      <div class="kpis">
        <div class="panel kpi"><span>Reach total</span><b>${fmt(reach)}</b><span>${p.length} postări</span></div>
        <div class="panel kpi"><span>Salvări</span><b>${fmt(saves)}</b><span>caruselele conduc</span></div>
        <div class="panel kpi"><span>Distribuiri</span><b>${fmt(shares)}</b><span>reels cu contrast</span></div>
        <div class="panel kpi"><span>Cea mai bună oră</span><b>20:00</b><span>joi</span></div>
      </div>
      <div class="panel"><h3 class="h3">Fiecare postare, etichetată și măsurată</h3>
        <div class="tbl-wrap" style="margin-top:10px"><table class="tbl"><thead><tr><th>Format</th><th>Tip de hook</th><th>Când</th><th class="n">Reach</th><th class="n">Vizionare medie</th><th class="n">Salvări</th><th class="n">Distribuiri</th></tr></thead>
        <tbody>${p.map((x) => `<tr><td>${esc(x[0])}</td><td>${esc(x[1])}</td><td class="mono">${esc(x[2])}</td><td class="n">${fmt(x[3])}</td><td class="n">${x[4] ? x[4] + "%" : "—"}</td><td class="n">${fmt(x[5])}</td><td class="n">${fmt(x[6])}</td></tr>`).join("")}</tbody></table></div>
      </div>
      <div class="panel"><h3 class="h3">Ce am învățat</h3>${ticks(D.demo.insights)}</div>`);
  }

  function viewStudioCompliance() {
    const proc = D.processes.find((x) => x.id === "conformitate");
    return studio("studio-conformitate", "Conformitate", "Verificarea de dinaintea fiecărei livrări", `
      <div class="grid-2" style="align-items:start">
        <div class="panel"><h3 class="h3">Lista de verificare</h3>
          <ul class="pipe" style="margin-top:8px">${[
            "Fața = caracterul (comparată cu referința)", "Mâini, degete, ochi, dinți corecți", "Produsul identic: culoare, logo, formă, text",
            "Fără text străin, logo-uri sau watermark", "Nimic care să sugereze minori, nuditate sau promisiuni medicale", "Eticheta AI pregătită și #ad la colaborări plătite",
            "Format corect (9:16 / 4:5), subtitrări corecte în română", "Muzică licențiată", "Fișierul denumit corect, în folderul clientului"
          ].map((t, i) => `<li><span class="dot ${i < 6 ? "done" : ""}">${i < 6 ? "✓" : ""}</span><span>${esc(t)}</span><span></span></li>`).join("")}</ul>
        </div>
        <div class="stack">
          <div class="panel"><h3 class="h3">Registrul de acorduri</h3>
            <div class="tbl-wrap" style="margin-top:8px"><table class="tbl" style="min-width:420px"><thead><tr><th>Cine</th><th>Tip</th><th>Stare</th></tr></thead>
            <tbody>${D.demo.consents.map(([a, b, c, s]) => `<tr><td>${esc(a)}</td><td>${esc(b)}</td><td>${stateChip(s, c)}</td></tr>`).join("")}</tbody></table></div>
          </div>
          <div class="panel"><h3 class="h3">La fiecare livrabil</h3><ul class="list">${proc.steps.map(([s, w, t, d]) => `<li><span class="mono">${esc(d)}</span><span>${esc(s)}</span>${chip(w)}</li>`).join("")}</ul></div>
        </div>
      </div>`);
  }

  /* ---------- Router ---------- */
  const VIEWS = {
    acasa: viewHome,
    caractere: viewRoster,
    servicii: viewServices,
    nise: viewNiches,
    "cum-lucram": viewHow,
    platforma: viewPlatform,
    transparenta: viewTransparency,
    contact: viewContact,
    studio: viewStudioHome,
    "studio-caractere": viewStudioChars,
    "studio-idei": viewStudioIdeas,
    "studio-prompt": viewStudioPrompt,
    "studio-calendar": viewStudioCalendar,
    "studio-procese": viewStudioProcesses,
    "studio-rezultate": viewStudioResults,
    "studio-conformitate": viewStudioCompliance
  };
  D.characters.forEach((c) => (VIEWS[c.id] = () => viewCharacter(c)));

  function route() {
    const id = decodeURIComponent((location.hash || "#acasa").slice(1)) || "acasa";
    const key = VIEWS[id] ? id : "acasa";
    main.innerHTML = VIEWS[key]();
    const navKey = byId(key) ? "caractere" : key.startsWith("studio") ? "studio" : key;
    $$("[data-nav]").forEach((a) => a.classList.toggle("on", a.dataset.nav === navKey));
    $("#site-nav").classList.remove("open");
    $("#menu-btn").setAttribute("aria-expanded", "false");
    window.scrollTo(0, 0);
    main.focus({ preventScroll: true });
    drawAll();
    if (key === "studio-idei") bindIdeas();
    if (key === "studio-prompt") bindPrompt();
    if (key === "studio-calendar") bindHeat();
    if (key === "contact") bindContact();
  }

  /* ---------- Content Brain (live) ---------- */
  const ERR = {
    not_granted: "Generarea cu Claude nu e permisă aici.",
    sampling_disabled: "Claude nu e disponibil pentru acest cont.",
    capability_disabled: "Generarea live nu merge în această vizualizare.",
    not_declared: "Generarea live nu e activă pe această pagină.",
    rate_limited: "Prea multe cereri acum. Încearcă din nou peste un minut.",
    refused: "Claude n-a acceptat cererea. Schimbă brief-ul și încearcă din nou.",
    image_rejected: "Imaginea nu poate fi folosită. Încearcă alt fișier (JPG, PNG sau WebP, sub 20 MB).",
    images_unavailable: "Imaginile nu pot fi trimise în această vizualizare.",
    invalid_json: "Răspunsul n-a venit în formatul așteptat. Încearcă din nou.",
    empty_completion: "N-a venit niciun răspuns. Scurtează brief-ul și încearcă din nou.",
    session_expired: "Sesiunea a expirat. Autentifică-te din nou în Claude.",
    cancelled: "Oprit."
  };
  const HIDE = ["not_granted", "sampling_disabled", "capability_disabled", "capability_removed", "not_declared"];
  const errText = (e) => ERR[e && e.code] || "Nu a mers acum. Încearcă din nou.";

  let dbPromise = null;
  const getDb = () => (dbPromise ||= cap("db"));
  let bankDocs = null;
  let bankSub = null;

  function ideasPrompt(ch, niche, format, n, brief) {
    return [
      "Ești strategul de conținut al MUSQAI, un studio de ambasadori AI pentru branduri din România.",
      `Scrie ${n} idei de ${format} pentru Instagram și TikTok, în limba română, pentru caracterul ${ch.name} (${ch.role}).`,
      `Personalitate: ${ch.personality.join(", ")}. Vocea: ${ch.voice.desc} Piloni: ${ch.pillars.map((p) => p[0]).join(", ")}.`,
      `Nișa: ${niche.name}. Clientul tipic: ${niche.who}`,
      `Brief: ${brief || "fără brief, propune idei generale pentru nișă"}`,
      "Reguli obligatorii: caracterul este un ambasador AI declarat; nu spune că a cumpărat sau a folosit produsul ca o persoană reală; fără mărturii sau recenzii false; fără promisiuni medicale sau de rezultat; fără nuditate; colaborările plătite au #ad.",
      `Răspunde cu exact ${n} rânduri. Fiecare rând este un singur obiect JSON, pe o singură linie, fără alt text și fără blocuri de cod:`,
      '{"titlu": string, "hook": string (primele 2 secunde, maximum 12 cuvinte), "cadre": [3 cadre scurte], "text_pe_ecran": string, "caption": string (maximum 300 de caractere, cu un singur CTA), "ora": string (ora propusă, ex. "19:00"), "de_ce": string (o propoziție)}'
    ].join("\n");
  }

  async function bindIdeas() {
    const form = $("#cb-form"), out = $("#cb-out"), status = $("#cb-status"), go = $("#cb-go"), stop = $("#cb-stop");
    let items = [];
    const sample = await cap("sample");
    if (!document.body.contains(form)) return;
    if (!sample) {
      go.disabled = true;
      if (PUBLIC) status.innerHTML = 'Generarea live e disponibilă clienților MUSQAI. <a href="#contact">Cere acces</a>. Mai jos vezi trei idei de exemplu.';
      else status.textContent = "Generarea live merge când deschizi pagina în Claude. Mai jos vezi trei idei de exemplu.";
    }
    startBank();
    let ctl = null;
    stop.onclick = () => ctl && ctl.abort();
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!sample) return;
      const ch = byId(form.elements.char.value);
      const niche = D.niches.find((x) => x.id === form.elements.niche.value);
      const n = Number(form.elements.count.value);
      const prompt = ideasPrompt(ch, niche, form.elements.format.value, n, form.elements.brief.value.trim());
      ctl = new AbortController();
      items = [];
      out.innerHTML = "";
      go.disabled = true;
      stop.hidden = false;
      status.textContent = "Se gândește…";
      let blocked = false;
      let pending = "";
      const addLine = (line) => {
        const t = line.trim().replace(/^```(?:json)?/, "").replace(/```$/, "").trim();
        if (!t.startsWith("{")) return;
        try {
          const o = JSON.parse(t);
          items.push({ ...o, _char: ch.id, _niche: niche.id, _format: form.elements.format.value });
          out.insertAdjacentHTML("beforeend", ideaCard(o, items.length - 1, false));
          status.textContent = `${items.length} din ${n}…`;
          refreshSaveButtons();
        } catch (_) { /* rând incomplet */ }
      };
      try {
        await sample(prompt, {
          signal: ctl.signal,
          cache: false,
          onText: ({ delta }) => {
            const lines = (pending + delta).split("\n");
            pending = lines.pop();
            lines.forEach(addLine);
          }
        });
        if (pending.trim()) addLine(pending);
        status.textContent = items.length ? `${items.length} idei gata. Salvează ce îți place în banca de idei.` : "N-au venit idei în formatul cerut. Încearcă din nou.";
      } catch (err) {
        status.textContent = errText(err);
        blocked = HIDE.includes(err && err.code);
      } finally {
        go.disabled = blocked;
        stop.hidden = true;
      }
    });
    out.addEventListener("click", async (e) => {
      const b = e.target.closest("[data-save]");
      if (!b) return;
      const db = await getDb();
      const o = items[Number(b.dataset.save)];
      if (!db || !o) return;
      b.disabled = true;
      try {
        const clean = { titlu: o.titlu || "", hook: o.hook || "", cadre: Array.isArray(o.cadre) ? o.cadre.slice(0, 5).map(String) : [], text_pe_ecran: o.text_pe_ecran || "", caption: o.caption || "", ora: o.ora || "", de_ce: o.de_ce || "", caracter: o._char, nisa: o._niche, format: o._format, creat: Date.now() };
        await db.collection("ideas").add(clean);
        b.textContent = "Salvată";
        toast("Ideea e în bancă.");
      } catch (err) {
        b.disabled = false;
        toast(err && err.code === "quota_exceeded" ? "Banca e plină. Șterge câteva idei vechi." : "Nu s-a salvat. Încearcă din nou.");
      }
    });
    async function refreshSaveButtons() {
      const db = await getDb();
      if (db) $$("[data-save]", out).forEach((b) => (b.hidden = false));
    }
  }

  async function startBank() {
    const db = await getDb();
    const section = $("#bank");
    if (!db || !section) return;
    section.hidden = false;
    renderBank();
    if (bankSub) return;
    bankSub = db.collection("ideas").orderBy("creat", "desc").limit(60).onSnapshot(
      (snap) => { bankDocs = snap.docs.map((d) => ({ id: d.id, ...d.data() })); renderBank(); },
      () => { bankSub = null; }
    );
  }
  function renderBank() {
    const list = $("#bank-list"), count = $("#bank-count");
    if (!list) return;
    if (!bankDocs) { list.innerHTML = `<p class="muted small">Se încarcă banca de idei…</p>`; return; }
    count.textContent = bankDocs.length ? `${bankDocs.length} idei salvate` : "";
    list.innerHTML = bankDocs.length
      ? bankDocs.map((o) => ideaCard(o, 0, false, o.id)).join("")
      : `<p class="muted small">Banca e goală. Generează idei mai sus și apasă „Salvează în banca de idei” la cele bune.</p>`;
  }
  document.addEventListener("click", async (e) => {
    const b = e.target.closest("[data-del]");
    if (!b) return;
    if (b.dataset.armed !== "1") {
      b.dataset.armed = "1";
      b.textContent = "Sigur? Apasă din nou";
      setTimeout(() => { if (b.isConnected) { b.dataset.armed = ""; b.textContent = "Șterge din bancă"; } }, 3000);
      return;
    }
    const db = await getDb();
    if (!db) return;
    b.disabled = true;
    try { await db.doc("ideas/" + b.dataset.del).delete(); toast("Ideea a fost ștearsă."); }
    catch (_) { b.disabled = false; toast("Nu s-a șters. Încearcă din nou."); }
  });

  /* ---------- Image → Prompt (live) ---------- */
  function i2pPrompt(target, ch) {
    const video = /video/i.test(target);
    return [
      `Ești expert în prompturi pentru generatoare de ${video ? "video" : "imagini"}. Privește imaginea atașată și scrie un prompt în engleză pentru ${target}.`,
      ch
        ? `Înlocuiește persoana din imagine cu caracterul ${ch.name}. Începe promptul cu „${ch.prompt.split(",")[0]}, ” și nu descrie fața, părul sau corpul persoanei din imagine: le dă LoRA-ul caracterului.`
        : "Descrie persoana din imagine fără să o identifici și fără nume de persoane reale.",
      `Descrie: subiectul, poza, hainele, locul, lumina, unghiul camerei, obiectivul, stilul fotografiei${video ? ", mișcarea și mișcarea camerei, pe 5 secunde" : ""}.`,
      "Fără nume de branduri, de artiști sau de persoane reale. Fără nuditate.",
      'Răspunde doar cu JSON: {"prompt": string, "negative": string, "setari": string (format, raport de aspect, sugestii scurte), "note": string (în română, o propoziție despre ce să verifici)}'
    ].join("\n");
  }

  async function bindPrompt() {
    const drop = $("#i2p-drop"), input = $("#i2p-file"), prev = $("#i2p-preview"), go = $("#i2p-go"), stop = $("#i2p-stop"), status = $("#i2p-status"), out = $("#i2p-out");
    let file = null;
    let objUrl = "";
    const setFile = (f) => {
      if (!f || !/^image\//.test(f.type)) { status.textContent = "Alege o imagine (JPG, PNG sau WebP)."; return; }
      file = f;
      if (objUrl) URL.revokeObjectURL(objUrl);
      objUrl = URL.createObjectURL(f);
      prev.src = objUrl;
      prev.hidden = false;
      status.textContent = f.name + " e gata.";
    };
    input.addEventListener("change", () => setFile(input.files && input.files[0]));
    drop.addEventListener("dragover", (e) => { e.preventDefault(); drop.classList.add("over"); });
    drop.addEventListener("dragleave", () => drop.classList.remove("over"));
    drop.addEventListener("drop", (e) => { e.preventDefault(); drop.classList.remove("over"); setFile(e.dataTransfer.files && e.dataTransfer.files[0]); });
    document.addEventListener("paste", (e) => {
      if (!document.body.contains(drop)) return;
      const f = Array.from(e.clipboardData ? e.clipboardData.files : []).find((x) => /^image\//.test(x.type));
      if (f) setFile(f);
    });
    const sample = await cap("sample");
    const limits = sample ? await sample.limits().catch(() => null) : null;
    if (!document.body.contains(go)) return;
    if (!sample || !limits || !limits.images) {
      go.disabled = true;
      if (PUBLIC) status.innerHTML = 'Image → Prompt e disponibil clienților MUSQAI. <a href="#contact">Cere acces</a>. În dreapta vezi un exemplu.';
      else status.textContent = "Generarea live merge când deschizi pagina în Claude. În dreapta vezi un exemplu.";
      return;
    }
    input.accept = limits.images.mediaTypes.join(",");
    let ctl = null;
    stop.onclick = () => ctl && ctl.abort();
    go.addEventListener("click", async () => {
      if (!file) { status.textContent = "Alege întâi o imagine."; return; }
      if (file.size > limits.images.maxInputBytes) { status.textContent = "Imaginea e prea mare. Alege una mai mică."; return; }
      const ch = byId($("#i2p-char").value);
      ctl = new AbortController();
      go.disabled = true;
      stop.hidden = false;
      status.textContent = "Se uită la imagine…";
      try {
        const o = await sample.json(i2pPrompt($("#i2p-target").value, ch), { images: [file], signal: ctl.signal });
        if (!o || typeof o.prompt !== "string") throw { code: "invalid_json" };
        out.innerHTML = promptOut(o, false);
        status.textContent = "Promptul e gata.";
      } catch (err) {
        status.textContent = errText(err);
        if (HIDE.includes(err && err.code)) { stop.hidden = true; return; }
      } finally {
        go.disabled = false;
        stop.hidden = true;
      }
    });
  }

  /* ---------- Heatmap: tooltip ---------- */
  function bindHeat() {
    const wrap = $("#heat-wrap"), tip = $("#heat-tip");
    if (!wrap) return;
    const show = (cell) => {
      const r = cell.getBoundingClientRect(), w = wrap.getBoundingClientRect();
      tip.textContent = cell.dataset.tip;
      tip.style.left = r.left - w.left + wrap.scrollLeft + r.width / 2 + "px";
      tip.style.top = r.top - w.top + "px";
      tip.hidden = false;
    };
    wrap.addEventListener("pointerover", (e) => { const c = e.target.closest(".cell"); if (c) show(c); });
    wrap.addEventListener("pointerleave", () => (tip.hidden = true));
    wrap.addEventListener("focusin", (e) => { const c = e.target.closest(".cell"); if (c) show(c); });
    wrap.addEventListener("focusout", () => (tip.hidden = true));
  }

  /* ---------- Contact (demo) ---------- */
  function bindContact() {
    const form = $("#contact-form");
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const f = form.elements;
      const name = f.name.value.trim();
      if (!name) { f.name.focus(); toast("Scrie-ți numele, ca să știm cui răspundem."); return; }
      if (PUBLIC) {
        const company = f.company.value.trim();
        const body = [`Nume: ${name}`, `Firma: ${company}`, `Site sau Instagram: ${f.link.value.trim()}`, `Nișa: ${f.niche.value}`, `Mă interesează: ${f.want.value}`, "", f.msg.value.trim()].join("\n");
        window.location.href = `mailto:${D.brand.email}?subject=${encodeURIComponent("Cerere mostră" + (company ? ": " + company : ""))}&body=${encodeURIComponent(body)}`;
        $("#contact-box").innerHTML = `<div class="stack"><span class="chip ok">● Emailul e pregătit</span><h2 class="h2" style="font-size:34px">Mulțumim, ${esc(name.split(" ")[0])}.</h2><p class="lead">Ți-am deschis aplicația de email cu cererea completată. Apasă „Trimite” acolo. Dacă nu s-a deschis, scrie-ne direct la <b>${esc(D.brand.email)}</b>.</p><p><a class="btn btn-ghost" href="#acasa">Înapoi acasă</a></p></div>`;
        return;
      }
      $("#contact-box").innerHTML = `<div class="stack"><span class="chip ok">● Cerere primită</span><h2 class="h2" style="font-size:34px">Mulțumim, ${esc(name.split(" ")[0])}.</h2><p class="lead">În varianta live, cererea ta ajunge în tabelul de vânzări și primești un răspuns în 24 de ore. Acum e un formular demo, deci nu s-a trimis nimic.</p><p><a class="btn btn-ghost" href="#acasa">Înapoi acasă</a></p></div>`;
    });
  }

  /* ---------- Copiere, meniu, redesenare ---------- */
  document.addEventListener("click", (e) => {
    const b = e.target.closest("[data-copy]");
    if (!b) return;
    const el = document.getElementById(b.dataset.copy);
    if (!el) return;
    const text = el.textContent;
    const fallback = () => {
      const sel = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(el);
      sel.removeAllRanges();
      sel.addRange(range);
      toast("Textul e selectat. Copiază-l cu Ctrl+C.");
    };
    try {
      navigator.clipboard.writeText(text).then(() => toast("Copiat."), fallback);
    } catch (_) { fallback(); }
  });
  $("#menu-btn").addEventListener("click", () => {
    const nav = $("#site-nav");
    const open = !nav.classList.contains("open");
    nav.classList.toggle("open", open);
    $("#menu-btn").setAttribute("aria-expanded", String(open));
  });
  let resizeTimer = 0;
  window.addEventListener("resize", () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(drawAll, 150); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(drawAll);
  window.addEventListener("hashchange", route);
  route();
})();
