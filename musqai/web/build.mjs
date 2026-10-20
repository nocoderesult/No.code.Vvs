/* Construiește site-ul MUSQAI în musqai/web/public/: o pagină HTML separată pentru fiecare adresă.
   Rulare: node musqai/web/build.mjs */
import { cpSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import * as C from "./content.mjs";

const ROOT = dirname(fileURLToPath(import.meta.url));
const OUT = join(ROOT, "public");
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const byId = (id) => C.characters.find((c) => c.id === id);
/* „în stilul …”: forma corectă de genitiv pentru fiecare nume */
const GENITIVE = { iness: "lui Iness", matei: "lui Matei", ilinca: "Ilincăi", ioana: "Ioanei", mira: "Mirei" };

/* ---------- Iconițe ---------- */
const ICONS = {
  spark: '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 15l.7 2.1 2.3.9-2.3.8L19 21l-.7-2.2-2.3-.8 2.3-.9z"/>',
  image: '<rect x="3" y="4" width="18" height="16" rx="3"/><circle cx="9" cy="10" r="2"/><path d="M21 16l-5-5-8 8"/>',
  swap: '<path d="M4 8h14l-3.5-3.5"/><path d="M20 16H6l3.5 3.5"/>',
  text: '<path d="M4 6h16"/><path d="M4 12h11"/><path d="M4 18h14"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/>',
  arrow: '<path d="M5 12h14"/><path d="M13 6l6 6-6 6"/>',
  menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
  upload: '<path d="M12 20V8"/><path d="M7 13l5-5 5 5"/><path d="M5 4h14"/>',
  shield: '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
  star: '<path d="M12 4l2.4 5 5.6.8-4 3.9.9 5.5-4.9-2.6-4.9 2.6.9-5.5-4-3.9 5.6-.8z"/>'
};
const icon = (name) =>
  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name]}</svg>`;
const gradIcon = (name) =>
  `<span class="icon-tile"><svg viewBox="0 0 24 24" fill="none" stroke="url(#g)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name]}</svg></span>`;

/* ---------- Bucăți refolosite ---------- */
const ticks = (items, no) => `<ul class="ticks${no ? " no" : ""}">${items.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>`;
const specs = (rows) => `<table class="specs"><tbody>${rows.map(([k, v]) => `<tr><th scope="row">${esc(k)}</th><td>${esc(v)}</td></tr>`).join("")}</tbody></table>`;
const statusChip = (c) => `<span class="chip ${c.status === "live" ? "hot" : c.status === "casting" ? "casting" : ""}">${esc(c.statusLabel)}</span>`;
const secHead = (eyebrow, title, lead, center) =>
  `<div class="sec-head${center ? " center" : ""}"><span class="eyebrow">${esc(eyebrow)}</span><h2 class="h2">${title}</h2>${lead ? `<p class="lead">${lead}</p>` : ""}</div>`;
const em = (t) => `<span class="serif grad-text">${t}</span>`;

function picture(c, loading = "lazy", sizes = "(max-width: 920px) 92vw, 42vw") {
  return `<picture><source type="image/webp" srcset="/assets/img/iness-600.webp 600w, /assets/img/iness-960.webp 960w" sizes="${sizes}"><img src="/assets/img/iness-960.jpg" width="960" height="1440" alt="${esc(c.name)}, ambasadoare AI MUSQAI. Imagine generată cu AI." loading="${loading}" decoding="async"${loading === "eager" ? ' fetchpriority="high"' : ""}></picture>`;
}
function art(c) {
  const [a, b, d] = c.palette;
  return `<div class="art" style="background: radial-gradient(120% 90% at 85% 10%, ${d}55, transparent 55%), radial-gradient(90% 80% at 10% 100%, ${b}cc, transparent 60%), linear-gradient(160deg, ${b}, ${a})"><b>${esc(c.name[0])}</b></div>`;
}
function castCard(c) {
  const media = c.photo ? picture(c, "lazy", "(max-width: 920px) 92vw, 40vw") : art(c);
  return `<a class="cast" href="/caractere/${c.id}/">${media}<span class="meta"><span class="nm">${esc(c.name)}</span><span class="rl">${esc(c.role)}</span>${statusChip(c)}</span></a>`;
}

/* ---------- Pagina de bază ---------- */
const NAV = [["/caractere/", "Caractere", "caractere"], ["/genereaza/", "Generează", "genereaza"], ["/servicii/", "Servicii", "servicii"], ["/nise/", "Nișe", "nise"], ["/cum-lucram/", "Cum lucrăm", "cum-lucram"]];

function layout({ path, title, desc, active = "", body, scripts = [] }) {
  const full = title ? `${title} · MUSQAI` : "MUSQAI · Ambasadori AI pentru branduri";
  return `<!doctype html>
<html lang="ro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>${esc(full)}</title>
<meta name="description" content="${esc(desc)}">
<link rel="canonical" href="${C.brand.url}${path}">
<meta name="theme-color" content="#0a090c">
<meta property="og:type" content="website">
<meta property="og:site_name" content="MUSQAI">
<meta property="og:locale" content="ro_RO">
<meta property="og:title" content="${esc(full)}">
<meta property="og:description" content="${esc(desc)}">
<meta property="og:url" content="${C.brand.url}${path}">
<meta property="og:image" content="${C.brand.url}/assets/img/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/fonts/BricolageGrotesque-normal-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/Manrope-normal-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/fonts/fonts.css">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<a class="skip" href="#main">Sari la conținut</a>
<svg width="0" height="0" class="sr-only" aria-hidden="true" focusable="false"><defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="#ff8a3d"/><stop offset=".5" stop-color="#ff2d78"/><stop offset="1" stop-color="#9d5cff"/></linearGradient></defs></svg>
<header class="hdr"><div class="wrap">
  <a class="logo" href="/" aria-label="MUSQAI, prima pagină"><i></i>MUSQAI</a>
  <button class="menu-btn" id="menu-btn" type="button" aria-expanded="false" aria-controls="nav">${icon("menu")}Meniu</button>
  <nav class="nav" id="nav" aria-label="Principal">
    ${NAV.map(([h, t, k]) => `<a href="${h}"${k === active ? ' class="on" aria-current="page"' : ""}>${t}</a>`).join("\n    ")}
    <a class="btn btn-sm" href="/contact/">Cere o mostră</a>
  </nav>
</div></header>
<main id="main">
${body}
</main>
<footer class="ftr"><div class="wrap">
  <div class="ftr-grid">
    <div class="stack"><div class="word">MUSQAI</div><p class="muted small">${esc(C.brand.full)}</p><p class="small" style="max-width:34ch;color:var(--text-2)">Ambasadori AI pentru branduri. Conținut nou în fiecare săptămână, etichetat corect.</p></div>
    <div><h4>Studio</h4><a href="/caractere/">Caractere</a><a href="/servicii/">Servicii și prețuri</a><a href="/nise/">Nișe</a><a href="/cum-lucram/">Cum lucrăm</a></div>
    <div><h4>Generează</h4>${C.zones.map((z) => `<a href="/genereaza/${z.id}/">${esc(z.name)}</a>`).join("")}</div>
    <div><h4>Încredere</h4><a href="/transparenta/">Transparență AI</a><a href="/platforma/">Platforma</a><a href="/contact/">Contact</a></div>
  </div>
  <div class="ftr-base"><span>© 2026 MUSQAI</span><span>Tot conținutul cu ambasadorii MUSQAI e generat cu AI și etichetat ca atare.</span></div>
</div></footer>
<div class="toast" id="toast" role="status" aria-live="polite" hidden></div>
<script src="/assets/site.js" defer></script>
${scripts.map((s) => `<script src="${s}" defer></script>`).join("\n")}
</body>
</html>
`;
}

const pageHead = (crumbs, eyebrow, title, lead) => `
<section class="page-head"><div class="wrap">
  ${crumbs ? `<nav class="crumbs" aria-label="Unde ești">${crumbs}</nav>` : ""}
  <span class="eyebrow">${esc(eyebrow)}</span>
  <h1 class="h1">${title}</h1>
  ${lead ? `<p class="lead">${lead}</p>` : ""}
</div></section>`;

const ctaBand = (title, lead, primary = ["/contact/", "Cere o mostră"], ghost = ["/genereaza/", "Încearcă generarea"]) => `
<section class="section-tight"><div class="wrap"><div class="band-grad stack" style="gap:20px">
  <h2 class="h2" style="max-width:18ch">${title}</h2>
  <p class="lead">${lead}</p>
  <div class="btn-row"><a class="btn" href="${primary[0]}">${primary[1]} ${icon("arrow")}</a><a class="btn btn-ghost" href="${ghost[0]}">${ghost[1]}</a></div>
</div></div></section>`;

const offerPair = () => {
  const o = C.offers;
  return `<div class="offer-pair">
    <div class="card offer"><div class="plan-top"><span class="h3">${esc(o.small.name)}</span><span class="chip">${esc(o.small.note)}</span></div><div class="price">${esc(o.small.price)}</div>${ticks(o.small.items)}<a class="btn btn-ghost btn-sm" href="/contact/" style="justify-self:start;margin-top:8px">Vreau testul</a></div>
    <div class="card offer featured"><div class="plan-top"><span class="h3">${esc(o.full.name)}</span><span class="chip hot">${esc(o.full.note)}</span></div><div class="price">${esc(o.full.price)}</div>${ticks(o.full.items)}<a class="btn btn-sm" href="/contact/" style="justify-self:start;margin-top:8px">Pornim campania ${icon("arrow")}</a></div>
  </div>`;
};

const zoneCards = (withCta) => `<div class="grid-3">
  ${C.zones.map((z) => `<a class="card zone-card" href="/genereaza/${z.id}/">${gradIcon(z.icon)}<span class="h3">${esc(z.name)}</span><span class="muted">${esc(z.short)}</span><span class="go">Deschide ${icon("arrow")}</span></a>`).join("")}
  ${withCta ? `<a class="card zone-card" href="/contact/">${gradIcon("star")}<span class="h3">Cu caracterul tău</span><span class="muted">Pentru clienți generăm cu modelul exact al ambasadorului, în studio.</span><span class="go">Cere acces ${icon("arrow")}</span></a>` : ""}
</div>`;

/* ---------- Paginile ---------- */
function home() {
  const i = byId("iness");
  const idee = "Iness pe un rooftop în București, la ora de aur, în rochie de satin champagne";
  return layout({
    path: "/", title: "", active: "",
    desc: "Ambasadori AI pentru branduri: poze și reels noi în fiecare săptămână, cu o față care rămâne mereu aceeași. Etichetate AI, în română.",
    body: `
<section class="hero"><div class="wrap hero-grid">
  <div>
    <span class="eyebrow">Studio de ambasadori AI · România</span>
    <h1 class="h1">Ambasadori AI care îți ${em("vând")} produsele.</h1>
    <p class="lead">Poze și reels noi în fiecare săptămână, cu o față care rămâne mereu aceeași. Fără ședințe foto. Fiecare postare e etichetată AI.</p>
    <div class="btn-row"><a class="btn" href="/genereaza/">Încearcă generarea ${icon("arrow")}</a><a class="btn btn-ghost" href="/caractere/iness/">Cunoaște-o pe Iness</a></div>
    <div class="facts"><div><b>5</b>caractere în univers</div><div><b>5</b>zone de generare</div><div><b>100%</b>etichetat AI</div></div>
  </div>
  <div class="photo-frame">
    <a class="photo" href="/caractere/iness/">${picture(i, "eager")}<span class="ai-tag">AI · declarat</span><span class="cap"><span><span class="nm">Iness</span><span class="rl">${esc(i.role)}</span></span></span></a>
    <div class="float-card"><span class="lbl">Prompt</span><span class="q">„${esc(idee)}”</span><a class="btn btn-sm" href="/genereaza/imagine/?idee=${encodeURIComponent(idee)}&amp;caracter=iness">Generează ${icon("spark")}</a></div>
  </div>
</div></section>

<div class="marquee" aria-hidden="true"><div class="marquee-track">${[...C.marquee, ...C.marquee].map((t) => `<span>${esc(t)}</span>`).join("")}</div></div>

<section class="section"><div class="wrap">
  ${secHead("Zone de generare", `Generează conținut ${em("direct pe site")}.`, "Idei, imagini, prompturi, texte și caractere noi. Scrii în română, primești rezultatul în câteva secunde.")}
  ${zoneCards(true)}
</div></section>

<section class="section"><div class="wrap split">
  <div class="stack" style="gap:22px">
    <span class="eyebrow">Prima ambasadoare</span>
    <h2 class="h2">Iness. ${em("Aceeași față")} în fiecare postare.</h2>
    <p class="lead">${esc(i.summary)}</p>
    ${specs(i.comp.slice(1, 5))}
    <div class="btn-row"><a class="btn" href="/caractere/iness/">Vezi fișa completă ${icon("arrow")}</a></div>
  </div>
  <div class="digitals" style="margin:0">
    <figure><img src="/assets/img/iness-fata.webp" width="640" height="640" alt="Iness, prim-plan. Imagine generată cu AI." loading="lazy" decoding="async"><figcaption>Prim-plan</figcaption></figure>
    <figure><img src="/assets/img/iness-600.webp" width="600" height="900" alt="Iness, portret. Imagine generată cu AI." loading="lazy" decoding="async" style="aspect-ratio:1;object-position:50% 20%"><figcaption>Portret</figcaption></figure>
  </div>
</div></section>

<section class="section"><div class="wrap">
  ${secHead("Universul MUSQAI", `Cinci caractere. ${em("Fiecare")} cu fața, vocea și regulile lui.`, "Le construim pe rând, cu același proces: fișă, set de antrenare, modelul feței, voce, conturi etichetate.")}
  <div class="cast-grid">${C.characters.map(castCard).join("")}</div>
</div></section>

<section class="section"><div class="wrap">
  ${secHead("Cum funcționează", `De la brief la postare, ${em("în fiecare săptămână")}.`)}
  <ol class="steps">
    <li><span class="h3">Brief de 15 minute</span><span class="muted">Ne spui ce vinzi, cui și ce nu vrei să vezi.</span></li>
    <li><span class="h3">Mostra pe produsul tău</span><span class="muted">Vezi ambasadorul cu produsul tău înainte de abonament.</span></li>
    <li><span class="h3">Producție săptămânală</span><span class="muted">Poze, reels, texte și variante pentru reclame.</span></li>
    <li><span class="h3">Postare și raport</span><span class="muted">Programăm la orele bune și îți arătăm ce a mers.</span></li>
  </ol>
</div></section>

<section class="section"><div class="wrap">
  ${secHead("Pentru început", `Testează cu 5 creative. ${em("Sau pornește campania.")}`)}
  ${offerPair()}
  <p style="margin-top:24px"><a class="btn btn-ghost" href="/servicii/">Toate pachetele ${icon("arrow")}</a></p>
</div></section>

<section class="section"><div class="wrap"><div class="panel-soft">
  ${secHead("Transparență", `Spunem mereu că e AI. ${em("Asta e regula.")}`, "Din 2 august 2026, în UE, conținutul generat cu AI care pare real trebuie etichetat. Noi o facem la fiecare postare, din prima zi.")}
  <div class="grid-3">
    <div class="stack" style="gap:10px">${gradIcon("shield")}<span class="h4">Etichetă AI</span><span class="muted small">„AI creator” în bio și eticheta AI la fiecare postare.</span></div>
    <div class="stack" style="gap:10px">${gradIcon("user")}<span class="h4">Fețe reale, doar cu acord</span><span class="muted small">Acord scris și verificare, înainte de orice.</span></div>
    <div class="stack" style="gap:10px">${gradIcon("text")}<span class="h4">Fără recenzii false</span><span class="muted small">Ambasadorul prezintă produsul. Nu pretinde că l-a cumpărat.</span></div>
  </div>
  <p style="margin-top:28px"><a class="btn btn-ghost btn-sm" href="/transparenta/">Cum lucrăm cu AI ${icon("arrow")}</a></p>
</div></div></section>

${ctaBand(`Vrei să vezi ambasadorul ${em("cu produsul tău")}?`, "Trimite-ne linkul către produs. Îți arătăm cum ar arăta o reclamă nouă, fără ședință foto.")}`
  });
}

function roster() {
  return layout({
    path: "/caractere/", title: "Caractere", active: "caractere",
    desc: "Universul MUSQAI: cinci ambasadori AI fictivi, fiecare cu fața, vocea, stilul și regulile lui.",
    body: `
${pageHead("", "Universul MUSQAI", `Caracterele ${em("casei")}.`, "Fiecare caracter e fictiv, adult și are o fișă fixă: aspect, stil, voce, nișe și reguli. Așa arată la fel în fiecare imagine.")}
<section class="section-tight"><div class="wrap"><div class="cast-grid">${C.characters.map(castCard).join("")}</div></div></section>
<section class="section"><div class="wrap split" style="align-items:start">
  <div class="stack" style="gap:22px">
    <span class="eyebrow">Caracterul tău</span>
    <h2 class="h2">Un ambasador ${em("doar al tău")}.</h2>
    <p class="lead">Pornim de la brandul tău și construim un caracter pe care îl folosești doar tu. Durează 2–3 săptămâni.</p>
    <div class="btn-row"><a class="btn" href="/genereaza/caracter/">Schițează-l acum ${icon("spark")}</a><a class="btn btn-ghost" href="/contact/">Cere o ofertă</a></div>
  </div>
  <ol class="steps" style="grid-template-columns:minmax(0,1fr)">
    <li><span class="h3">Fișa</span><span class="muted">Aspect, stil, personalitate, voce, nișe, ce nu face niciodată.</span></li>
    <li><span class="h3">40 de fețe, alegi una</span><span class="muted">Generăm variante până găsim fața potrivită.</span></li>
    <li><span class="h3">Modelul feței</span><span class="muted">34 de imagini de antrenare, apoi fața rămâne aceeași în orice scenă.</span></li>
    <li><span class="h3">Vocea și conturile</span><span class="muted">Voce proprie, conturi etichetate AI, primele 9 postări.</span></li>
  </ol>
</div></section>
<section class="section-tight"><div class="wrap grid-2">
  <div class="card"><span class="h3">Reguli pentru orice caracter</span>${ticks(["Adult clar, peste 21 de ani", "Fictiv: nu seamănă intenționat cu nicio persoană reală", "Fișă scrisă, aceeași în fiecare prompt", "Voce proprie, salvată", "Conturi etichetate AI"])}</div>
  <div class="card"><span class="h3">Fețe reale</span><p class="muted">Lucrăm cu fața unei persoane reale doar cu acordul ei scris și după verificare. Acordul se păstrează și poate fi retras oricând.</p></div>
</div></section>`
  });
}

function character(c) {
  const idx = C.characters.indexOf(c);
  const prev = C.characters[(idx + C.characters.length - 1) % C.characters.length];
  const next = C.characters[(idx + 1) % C.characters.length];
  const done = c.pipeline.filter((p) => p[1] === "done").length;
  const media = c.photo
    ? `<div class="photo-frame"><div class="photo">${picture(c, "eager")}<span class="ai-tag">AI · declarat</span></div></div>
       <div class="digitals"><figure><img src="${c.photo.face}" width="640" height="640" alt="${esc(c.name)}, prim-plan. Imagine generată cu AI." loading="lazy" decoding="async"><figcaption>Prim-plan</figcaption></figure><figure><img src="${c.photo.card}" width="600" height="900" alt="${esc(c.name)}, portret. Imagine generată cu AI." loading="lazy" decoding="async" style="aspect-ratio:1;object-position:50% 18%"><figcaption>Portret</figcaption></figure></div>`
    : `<div class="cast" style="min-height:560px;cursor:default">${art(c)}<span class="meta"><span class="chip casting" style="margin:0">Portretul vine după casting</span></span></div>`;
  return layout({
    path: `/caractere/${c.id}/`, title: `${c.name}, ${c.role.toLowerCase()}`, active: "caractere",
    desc: `${c.name}: ${c.summary}`,
    body: `
<section class="page-head"><div class="wrap">
  <nav class="crumbs" aria-label="Unde ești"><a href="/caractere/">Caractere</a><span>/</span><span>${esc(c.name)}</span></nav>
  <div class="char-hero">
    <div>${media}</div>
    <div class="stack" style="gap:22px">
      <div class="btn-row" style="gap:8px">${statusChip(c)}<span class="chip">${esc(c.handle)}</span></div>
      <h1 class="h1">${esc(c.name)}</h1>
      <p class="h3" style="font-weight:600">${esc(c.role)} <span class="muted">· ${esc(c.archetype)}</span></p>
      <p class="lead">${esc(c.summary)}</p>
      ${specs(c.comp)}
      <div class="btn-row"><a class="btn" href="/genereaza/imagine/?caracter=${c.id}">Generează în stilul ${esc(GENITIVE[c.id] || "lui " + c.name)} ${icon("spark")}</a><a class="btn btn-ghost" href="/genereaza/idei/?caracter=${c.id}">Idei pentru ${esc(c.name)}</a></div>
    </div>
  </div>
</div></section>

<section class="section-tight"><div class="wrap grid-2">
  <div class="card"><span class="h3">Aspectul</span><p style="color:var(--text-2)">${esc(c.look)}</p><span class="h3" style="margin-top:8px">Stilul</span><p class="muted">${esc(c.style)}</p><div class="btn-row" style="gap:8px">${c.personality.map((p) => `<span class="chip hot">${esc(p)}</span>`).join("")}</div></div>
  <div class="card"><span class="h3">Vocea</span><p style="color:var(--text-2)">${esc(c.voice)}</p><span class="h3" style="margin-top:8px">Nișe</span><div class="btn-row" style="gap:8px">${c.niches.map((n) => `<span class="chip">${esc(n)}</span>`).join("")}</div><span class="h3" style="margin-top:8px">Program</span><p class="muted">${esc(c.schedule)} · ${c.platforms.map(esc).join(", ")}</p></div>
</div></section>

<section class="section"><div class="wrap split" style="align-items:start">
  <div class="stack" style="gap:18px">
    <span class="eyebrow">Piloni de conținut</span>
    <h2 class="h2">Despre ce ${em("postează")}.</h2>
    <div>${c.pillars.map(([n, p, ex]) => `<div class="pillar"><span class="h4">${esc(n)}</span><span class="h4">${p}%</span><span class="bar"><i style="width:${p}%"></i></span><span class="ex">Ex.: ${esc(ex)}</span></div>`).join("")}</div>
  </div>
  <div class="stack" style="gap:20px">
    <div class="card"><span class="h3">Hook-uri de test</span>${ticks(c.hooks.map((h) => `„${h}”`))}</div>
    <div class="card"><span class="h3">Ce face</span>${ticks(c.rules.do)}<span class="h3" style="margin-top:6px">Ce nu face niciodată</span>${ticks(c.rules.dont, true)}</div>
  </div>
</div></section>

<section class="section-tight"><div class="wrap grid-2">
  <div class="card"><div class="plan-top"><span class="h3">Producția</span><span class="chip">${done} din ${c.pipeline.length}</span></div>
    <ul class="pipe">${c.pipeline.map(([n, st]) => `<li><span class="dot ${st}"></span><span>${esc(n)}</span><span class="chip${st === "doing" ? " casting" : ""}">${st === "done" ? "gata" : st === "doing" ? "în lucru" : "urmează"}</span></li>`).join("")}</ul>
  </div>
  <div class="card" style="align-content:space-between"><div class="stack" style="gap:12px"><span class="h3">Vrei ${esc(c.name)} pentru brandul tău?</span><p class="muted">Primești poze și reels cu produsul tău, etichetate AI, în fiecare săptămână.</p></div><div class="btn-row"><a class="btn" href="/contact/">Cere o mostră ${icon("arrow")}</a></div></div>
</div></section>

<section class="section-tight"><div class="wrap btn-row" style="justify-content:space-between">
  <a class="btn btn-ghost" href="/caractere/${prev.id}/">← ${esc(prev.name)}</a><a class="btn btn-ghost" href="/caractere/${next.id}/">${esc(next.name)} →</a>
</div></section>`
  });
}

function zonesHub() {
  return layout({
    path: "/genereaza/", title: "Zone de generare", active: "genereaza",
    desc: "Generează idei de conținut, imagini, prompturi, texte pentru postări și caractere AI, direct pe site.",
    body: `
${pageHead("", "Zone de generare", `Generează. ${em("Direct aici.")}`, "Cinci unelte pe care le folosim și noi în studio. Scrii în română, primești rezultatul în câteva secunde.")}
<section class="section-tight"><div class="wrap">${zoneCards(true)}</div></section>
<section class="section-tight"><div class="wrap grid-3">
  <div class="card"><span class="h4">Etichetat din fișier</span><p class="muted small">Imaginile primesc un marcaj în fișier care spune că sunt generate cu AI, cum cere AI Act.</p></div>
  <div class="card"><span class="h4">Nu păstrăm ce trimiți</span><p class="muted small">Textele și pozele trimise sunt folosite doar ca să generăm răspunsul. Nu le salvăm.</p></div>
  <div class="card"><span class="h4">Limită zilnică</span><p class="muted small">Generarea are o limită pe zi pentru tot site-ul. Dacă se atinge, revii mâine sau ne scrii pentru acces.</p></div>
</div></section>`
  });
}

/* Formularele zonelor */
const charOptions = (withNone = true) =>
  `${withNone ? '<option value="">Fără caracter</option>' : ""}${C.characters.map((c) => `<option value="${c.id}">${esc(c.name)} · ${esc(c.role)}</option>`).join("")}`;
const nicheOptions = () => C.niches.map((n) => `<option value="${n.id}">${esc(n.name)}</option>`).join("");
const radios = (name, items, checked) =>
  `<div class="opts" role="radiogroup">${items.map(([v, t]) => `<label><input type="radio" name="${name}" value="${esc(v)}"${v === checked ? " checked" : ""}><span>${esc(t)}</span></label>`).join("")}</div>`;

const ZONE_FORMS = {
  idei: () => `
    <div class="field"><label for="f-caracter">Caracter</label><select class="select" id="f-caracter" name="caracter">${charOptions()}</select></div>
    <div class="field"><label for="f-nisa">Nișă</label><select class="select" id="f-nisa" name="nisa">${nicheOptions()}</select></div>
    <div class="field"><span class="lbl">Format</span>${radios("format", [["Reel 8–15 s", "Reel"], ["Carusel", "Carusel"], ["Story", "Story"], ["Reclamă 9:16", "Reclamă"]], "Reel 8–15 s")}</div>
    <div class="field"><label for="f-brief">Ce vinzi și cui</label><textarea class="textarea" id="f-brief" name="brief" maxlength="800" placeholder="Ex.: rochie midi din satin, brand românesc, 349 lei, pentru femei de 24–35 de ani din orașele mari." required></textarea></div>
    <div class="field"><span class="lbl">Câte idei</span>${radios("n", [["3", "3"], ["5", "5"]], "5")}</div>`,
  imagine: () => `
    <div class="field"><label for="f-idee">Ce vrei să vezi</label><textarea class="textarea" id="f-idee" name="idee" maxlength="600" placeholder="Ex.: o femeie la o cafenea dimineața, cu un latte, lumină de la fereastră." required></textarea><span class="hint">Scrie în română. Noi transformăm ideea într-un prompt detaliat.</span></div>
    <div class="field"><span class="lbl">Stil</span>${radios("stil", [["telefon", "Poză de telefon"], ["studio", "Studio"], ["editorial", "Editorial"], ["produs", "Produs"]], "telefon")}</div>
    <div class="field"><label for="f-caracter">Aspectul unui caracter</label><select class="select" id="f-caracter" name="caracter">${charOptions()}</select><span class="hint">Aici folosim doar descrierea caracterului. Fața exactă o facem în studio, cu modelul lui.</span></div>`,
  prompt: () => `
    <div class="field"><span class="lbl">Imaginea</span>
      <label class="drop" id="drop" for="f-file">${icon("upload")}<span class="h4">Trage aici o imagine</span><span class="muted small">sau apasă ca s-o alegi · JPG, PNG, WebP</span><img id="preview" alt="Imaginea aleasă" hidden></label>
      <input id="f-file" name="file" type="file" accept="image/jpeg,image/png,image/webp" class="sr-only">
    </div>
    <div class="field"><label for="f-tinta">Pentru ce generator</label><select class="select" id="f-tinta" name="tinta"><option>FLUX / Krea (ComfyUI)</option><option>Nano Banana</option><option>Midjourney</option><option>Seedance / Kling (video)</option></select></div>`,
  text: () => `
    <div class="field"><span class="lbl">Platformă</span>${radios("platforma", [["Instagram", "Instagram"], ["TikTok", "TikTok"], ["Facebook", "Facebook"], ["LinkedIn", "LinkedIn"]], "Instagram")}</div>
    <div class="field"><span class="lbl">Ton</span>${radios("ton", [["cald", "Cald"], ["premium", "Premium"], ["amuzant", "Amuzant"], ["direct", "Direct"]], "cald")}</div>
    <div class="field"><label for="f-despre">Despre ce e postarea</label><textarea class="textarea" id="f-despre" name="despre" maxlength="800" placeholder="Ex.: lansăm colecția de toamnă, 12 rochii din satin, livrare în 24 de ore." required></textarea></div>
    <div class="field"><label for="f-cta">Ce vrei să facă oamenii</label><input class="input" id="f-cta" name="cta" maxlength="120" placeholder="Ex.: să intre pe site prin linkul din bio"></div>
    <div class="field"><label for="f-caracter">Vocea unui caracter</label><select class="select" id="f-caracter" name="caracter">${charOptions()}</select></div>`,
  caracter: () => `
    <div class="field"><span class="lbl">Gen</span>${radios("gen", [["femeie", "Femeie"], ["bărbat", "Bărbat"]], "femeie")}</div>
    <div class="field"><label for="f-varsta">Vârsta</label><select class="select" id="f-varsta" name="varsta">${[22, 25, 28, 30, 33, 35, 40, 45].map((v) => `<option${v === 28 ? " selected" : ""}>${v}</option>`).join("")}</select></div>
    <div class="field"><label for="f-nisa">Nișa brandului</label><select class="select" id="f-nisa" name="nisa">${nicheOptions()}</select></div>
    <div class="field"><label for="f-stil">Stilul</label><input class="input" id="f-stil" name="stil" maxlength="160" placeholder="Ex.: sport-elegant, culori neutre, accesorii aurii"></div>
    <div class="field"><label for="f-vibe">Cum vrei să pară</label><input class="input" id="f-vibe" name="vibe" maxlength="160" placeholder="Ex.: caldă, sigură pe ea, cu umor"></div>`
};

const ZONE_INFO = {
  idei: { title: "Idei de conținut", lead: "Alegi caracterul, nișa și formatul. Primești idei cu hook, cadre, text pe ecran și descriere.", empty: "Ideile apar aici, una câte una.", btn: "Generează ideile" },
  imagine: { title: "Imagine din text", lead: "Scrii ideea în română. Primești o imagine pătrată, 1024 × 1024, cu marcaj AI în fișier.", empty: "Imaginea apare aici în câteva secunde.", btn: "Generează imaginea" },
  prompt: { title: "Image → Prompt", lead: "Urci o poză care îți place. Primești promptul, ce să eviți și setările, pentru generatorul tău.", empty: "Promptul apare aici după ce urci o imagine.", btn: "Scrie promptul" },
  text: { title: "Texte pentru postări", lead: "Spui despre ce e postarea. Primești trei variante de descriere, cu hook, îndemn și hashtag-uri.", empty: "Cele trei variante apar aici.", btn: "Scrie textele" },
  caracter: { title: "Creează-ți caracterul", lead: "Descrii ambasadorul pe care îl vrei. Primești fișa lui și primul portret.", empty: "Fișa și portretul apar aici.", btn: "Creează caracterul" }
};

function zonePage(z) {
  const info = ZONE_INFO[z.id];
  return layout({
    path: `/genereaza/${z.id}/`, title: info.title, active: "genereaza",
    desc: `${info.title}: ${z.short}`,
    scripts: ["/assets/gen.js"],
    body: `
${pageHead(`<a href="/genereaza/">Generează</a><span>/</span><span>${esc(info.title)}</span>`, "Zonă de generare", esc(info.title), esc(info.lead))}
<section class="section-tight" style="padding-top:0"><div class="wrap zone-grid">
  <form class="glass zone-form" id="zone-form" data-zone="${z.id}" novalidate>
    ${ZONE_FORMS[z.id]()}
    <button class="btn" type="submit" id="go">${icon("spark")}${esc(info.btn)}</button>
    <p class="status" id="status" role="status" aria-live="polite"></p>
  </form>
  <div class="output" id="output" aria-live="polite">
    <div class="empty">${gradIcon(z.icon)}<span>${esc(info.empty)}</span></div>
  </div>
</div></section>
<section class="section-tight"><div class="wrap grid-3">
  <div class="note-box"><b>Ce nu generăm</b>Nuditate, conținut sexual, minori, violență, persoane reale sau sosii ale lor, logo-uri de branduri reale.</div>
  <div class="note-box"><b>Ce se întâmplă cu datele</b>Ce trimiți e procesat de Cloudflare Workers AI doar ca să primești răspunsul. Noi nu salvăm nimic.</div>
  <div class="note-box"><b>Modelele</b>FLUX.1 [schnell] pentru imagini, LLaVA pentru citirea pozelor și Llama 3.3 pentru texte (Built with Llama), prin Cloudflare Workers AI.</div>
</div></section>`
  });
}

function services() {
  return layout({
    path: "/servicii/", title: "Servicii și prețuri", active: "servicii",
    desc: "Testul cu 5 creative AI la 99 €, lansarea completă la 490 € și abonamente lunare de la 350 €.",
    body: `
${pageHead("", "Servicii și prețuri", `Începi mic. ${em("Crești când vezi rezultate.")}`, "Prețuri de lansare pentru primii clienți.")}
<section class="section-tight"><div class="wrap stack" style="gap:20px">
  ${offerPair()}
  <div class="card" style="grid-template-columns:auto minmax(0,1fr);align-items:center;gap:18px">${gradIcon("shield")}<div class="stack" style="gap:4px"><span class="h4">Garanția</span><span class="muted">${esc(C.offers.guarantee)}</span></div></div>
</div></section>
<section class="section"><div class="wrap">
  ${secHead("Abonamente", `Conținut nou, ${em("în fiecare lună")}.`, `Facturare la 4 săptămâni. ${esc(C.offers.prepay)}`)}
  <div class="price-grid">${C.packages.map((p) => `<div class="card price-card${p.featured ? " featured" : ""}"><div class="plan-top"><span class="h3">${esc(p.name)}</span>${p.featured ? '<span class="chip hot">Cel mai ales</span>' : ""}</div><div class="price">${esc(p.price)} <small>/ lună</small></div><p class="muted small">${esc(p.note)}</p>${ticks(p.items)}<a class="btn${p.featured ? "" : " btn-ghost"} btn-sm" href="/contact/" style="justify-self:start;margin-top:8px">Alege ${esc(p.name)}</a></div>`).join("")}</div>
</div></section>
<section class="section-tight"><div class="wrap split" style="align-items:start">
  <div class="stack" style="gap:18px"><span class="eyebrow">Extra</span><h2 class="h2">Adaugi doar ${em("ce-ți trebuie")}.</h2></div>
  <div class="grid-2">${C.extras.map(([a, b]) => `<div class="card"><span class="h4">${esc(a)}</span><span class="muted small">${esc(b)}</span></div>`).join("")}</div>
</div></section>
<section class="section"><div class="wrap split" style="align-items:start">
  <div class="stack" style="gap:18px"><span class="eyebrow">Întrebări</span><h2 class="h2">Ce ne întreabă ${em("toată lumea")}.</h2></div>
  <div class="faq">${C.faq.map(([q, a]) => `<details><summary>${esc(q)}</summary><p>${esc(a)}</p></details>`).join("")}</div>
</div></section>
${ctaBand(`Pornim cu ${em("5 creative")}?`, "Ne trimiți linkul către produs, primești mostra în 3–5 zile lucrătoare.")}`
  });
}

function nichesPage() {
  return layout({
    path: "/nise/", title: "Nișe", active: "nise",
    desc: "Unde aduce un ambasador AI cel mai mult: magazine online, imobiliare, turism și HoReCa, evenimente, wellness.",
    body: `
${pageHead("", "Nișe", `Unde aduce un ambasador AI ${em("cel mai mult")}.`, "Pornim cu o nișă, o facem bine, apoi trecem la următoarea. Fiecare are regulile ei, scrise înainte de primul livrabil.")}
<section class="section-tight"><div class="wrap">
  ${C.niches.map((x) => {
    const ch = byId(x.character);
    return `<article class="niche"><div class="code grad-text">${esc(x.code)}</div><div>
      <div class="btn-row" style="justify-content:space-between"><h2 class="h2" style="font-size:clamp(28px,3.6vw,44px)">${esc(x.name)}</h2><span class="chip${x.avail === "Disponibil acum" ? " hot" : ""}">${esc(x.avail)}</span></div>
      <p class="lead" style="margin-top:12px">${esc(x.who)} ${esc(x.pain)}</p>
      <div class="niche-cols"><div><h4>Ce livrăm</h4>${ticks(x.deliver)}</div><div><h4>Reguli</h4>${ticks(x.rules)}</div><div><h4>Ce măsurăm</h4><p style="color:var(--text-2)">${esc(x.metric)}</p><h4 style="margin-top:18px">Ambasador</h4><p><a href="/caractere/${ch.id}/" style="text-decoration:underline;text-underline-offset:4px">${esc(ch.name)}</a> <span class="muted">· ${esc(ch.role)}</span></p></div></div>
    </div></article>`;
  }).join("")}
</div></section>
${ctaBand(`Nișa ta ${em("nu e aici")}?`, "Scrie-ne ce vinzi. Îți spunem sincer dacă un ambasador AI te ajută.", ["/contact/", "Scrie-ne"], ["/servicii/", "Vezi prețurile"])}`
  });
}

function how() {
  return layout({
    path: "/cum-lucram/", title: "Cum lucrăm", active: "cum-lucram",
    desc: "Linia de producție MUSQAI: brief, idei, imagini, video, voce, editare, verificare, livrare și raport.",
    body: `
${pageHead("", "Cum lucrăm", `Linia de producție, ${em("pas cu pas")}.`, "Fiecare livrabil trece prin aceiași nouă pași. Nimic nu pleacă la client fără verificare.")}
<section class="section-tight"><div class="wrap"><ol class="steps">${C.steps.map(([a, b]) => `<li><span class="h3">${esc(a)}</span><span class="muted">${esc(b)}</span></li>`).join("")}</ol></div></section>
<section class="section"><div class="wrap split" style="align-items:start">
  <div class="stack" style="gap:18px"><span class="eyebrow">Primele 30 de zile</span><h2 class="h2">Ce se întâmplă ${em("după ce semnăm")}.</h2><p class="lead">Ai materialele în prima săptămână și cifrele în a doua.</p></div>
  <ul class="timeline">${C.timeline.map(([d, t]) => `<li><b class="grad-text">${esc(d)}</b><span style="color:var(--text-2)">${esc(t)}</span></li>`).join("")}</ul>
</div></section>
<section class="section-tight"><div class="wrap grid-2">
  <div class="card"><span class="h3">Ce ne dai tu</span>${ticks(C.clientGives)}</div>
  <div class="card"><span class="h3">Ce primești de la noi</span>${ticks(["Două runde de revizii la fiecare livrabil", "Fișierele în folderul tău, denumite clar", "Postările programate la orele bune", "Raportul lunar, cu recomandări"])}</div>
</div></section>
<section class="section"><div class="wrap">
  ${secHead("Procesele", `Cum arată munca ${em("din interior")}.`)}
  <div class="stack" style="gap:12px">${C.processes.map((p, i) => `<details class="card"${i === 0 ? " open" : ""}><summary style="list-style:none;cursor:pointer;display:flex;justify-content:space-between;gap:12px;align-items:center"><span class="h3">${esc(p.name)}</span><span class="chip">${esc(p.time)}</span></summary><ul class="pipe" style="margin-top:12px">${p.steps.map(([s, d], k) => `<li><span class="dot done"></span><span>${esc(s)}</span><span class="muted small">${esc(d)}</span></li>`).join("")}</ul></details>`).join("")}</div>
</div></section>
${ctaBand(`Vrei să vezi ${em("primul livrabil")}?`, "Facem o mostră pe produsul tău. Vezi exact ce primești înainte să semnezi.")}`
  });
}

function platform() {
  return layout({
    path: "/platforma/", title: "Platforma", active: "",
    desc: "MUSQAI Studio: caractere, idei, generare, editare, publicare, rezultate și conformitate, într-un singur loc.",
    body: `
${pageHead("", "Platforma", `Tot procesul, ${em("într-un singur loc")}.`, "Acum o folosim noi pentru clienți. Pas cu pas, o deschidem și pentru tine.")}
<section class="section-tight"><div class="wrap grid-4">${C.modules.map(([n, d], k) => `<div class="card"><span class="grad-text" style="font-family:var(--f-display);font-weight:800;font-size:28px">${String(k + 1).padStart(2, "0")}</span><span class="h4">${esc(n)}</span><span class="muted small">${esc(d)}</span></div>`).join("")}</div></section>
<section class="section"><div class="wrap">
  ${secHead("Etapele", `Construim ${em("ce s-a vândut deja")}.`)}
  <div class="grid-4">${C.phases.map(([a, b], k) => `<div class="card${k === 0 ? " featured price-card" : ""}"><span class="h3">${esc(a)}</span><span class="muted small">${esc(b)}</span></div>`).join("")}</div>
</div></section>
${ctaBand(`Încearcă ${em("ce merge deja")}.`, "Cinci zone de generare sunt live pe site.", ["/genereaza/", "Deschide zonele"], ["/contact/", "Cere acces"])}`
  });
}

function transparency() {
  const cards = [
    ["Etichetăm tot", "Fiecare cont are „AI creator” în bio. Fiecare postare are eticheta AI a platformei. Imaginile din zonele de generare primesc și un marcaj în fișier."],
    ["AI Act, articolul 50", "Din 2 august 2026, în UE, imaginile, clipurile și sunetele generate cu AI care par reale trebuie marcate ca atare, iar generatoarele trebuie să pună un marcaj citibil de calculator."],
    ["Fețe reale, doar cu acord", "Folosim fața sau vocea unei persoane reale doar cu acordul ei scris și după verificare. Acordul poate fi retras oricând."],
    ["Fără recenzii false", "Ambasadorul prezintă produsul. Nu spune că l-a cumpărat, nu dă note și nu se prezintă drept client mulțumit."],
    ["Zonele de generare", "Ce scrii sau urci e trimis la Cloudflare Workers AI doar ca să primești răspunsul. Nu salvăm textele, pozele sau rezultatele."],
    ["Modele cu licență", "Folosim modele care permit utilizarea comercială și verificăm licența fiecăruia înainte să-l folosim pentru clienți."]
  ];
  return layout({
    path: "/transparenta/", title: "Transparență AI", active: "",
    desc: "Cum lucrează MUSQAI cu AI: etichete, marcaj în fișier, acord pentru fețe reale, fără recenzii false.",
    body: `
${pageHead("", "Transparență AI", `Cum lucrăm cu AI, ${em("pe față")}.`, "Ambasadorii MUSQAI sunt generați cu AI. Asta nu e un secret, e regula de la care pornim.")}
<section class="section-tight"><div class="wrap grid-3">${cards.map(([a, b]) => `<div class="card">${gradIcon("shield")}<span class="h4">${esc(a)}</span><span class="muted small">${esc(b)}</span></div>`).join("")}</div></section>
<section class="section"><div class="wrap split" style="align-items:start">
  <div class="stack" style="gap:18px"><span class="eyebrow">Ce nu facem niciodată</span><h2 class="h2">Liniile ${em("pe care nu le trecem")}.</h2></div>
  ${ticks(["Conținut sexual sau nuditate", "Fețe reale fără acord scris", "Persoane care par minore", "Mărturii sau recenzii false", "Promisiuni medicale sau de rezultat corporal", "Conținut politic"], true)}
</div></section>`
  });
}

function contact() {
  return layout({
    path: "/contact/", title: "Contact", active: "",
    desc: "Cere o mostră pe produsul tău: ambasadorul AI MUSQAI cu produsul tău, în 3–5 zile lucrătoare.",
    scripts: ["/assets/contact.js"],
    body: `
${pageHead("", "Contact", `Cere o mostră ${em("pe produsul tău")}.`, "Îți răspundem în 24 de ore, în zilele lucrătoare.")}
<section class="section-tight" style="padding-top:0"><div class="wrap split" style="align-items:start">
  <div class="stack" style="gap:20px">
    <ul class="pipe">
      <li><span class="dot done"></span><span>Ne trimiți linkul către produs</span><span></span></li>
      <li><span class="dot done"></span><span>Facem un apel de 15 minute</span><span></span></li>
      <li><span class="dot done"></span><span>Primești mostra în 3–5 zile lucrătoare</span><span></span></li>
    </ul>
    <div class="card"><span class="muted small">Direct</span><span class="h3">${esc(C.brand.email)}</span><button class="btn btn-ghost btn-sm" type="button" data-copy-text="${esc(C.brand.email)}" style="justify-self:start">Copiază adresa</button></div>
  </div>
  <div class="glass" id="contact-box">
    <form class="stack" id="contact-form" novalidate style="gap:16px">
      <div class="grid-2" style="gap:14px">
        <div class="field"><label for="c-name">Numele tău</label><input class="input" id="c-name" name="name" autocomplete="name" placeholder="Numele și prenumele" required></div>
        <div class="field"><label for="c-company">Firma</label><input class="input" id="c-company" name="company" autocomplete="organization" placeholder="Numele firmei"></div>
      </div>
      <div class="field"><label for="c-link">Site sau Instagram</label><input class="input" id="c-link" name="link" placeholder="site.ro sau instagram.com/brand"></div>
      <div class="grid-2" style="gap:14px">
        <div class="field"><label for="c-niche">Nișa</label><select class="select" id="c-niche" name="niche">${C.niches.map((n) => `<option>${esc(n.name)}</option>`).join("")}<option>Altceva</option></select></div>
        <div class="field"><label for="c-want">Ce te interesează</label><select class="select" id="c-want" name="want"><option>5 creative AI (99 €)</option><option>Lansarea completă (490 €)</option><option>Abonament lunar</option><option>Caracter exclusiv</option><option>Acces la zonele de generare</option></select></div>
      </div>
      <div class="field"><label for="c-msg">Ce vrei să vinzi?</label><textarea class="textarea" id="c-msg" name="msg" placeholder="Produsul, linkul către el și ce vrei să obții."></textarea></div>
      <button class="btn" type="submit" style="justify-self:start">Trimite cererea ${icon("arrow")}</button>
      <p class="muted tiny">Butonul deschide aplicația ta de email, cu cererea completată și adresată către ${esc(C.brand.email)}.</p>
    </form>
  </div>
</div></section>`
  });
}

function notFound() {
  return layout({
    path: "/404", title: "Pagina nu există", active: "",
    desc: "Pagina căutată nu există.",
    body: `${pageHead("", "Eroare 404", `Pagina asta ${em("nu există")}.`, "Poate a fost mutată. Pornește de la prima pagină sau încearcă zonele de generare.")}
<section class="section-tight" style="padding-top:0"><div class="wrap btn-row"><a class="btn" href="/">Prima pagină ${icon("arrow")}</a><a class="btn btn-ghost" href="/genereaza/">Zonele de generare</a></div></section>`
  });
}

/* ---------- Scrierea fișierelor ---------- */
const pages = [
  ["index.html", home()],
  ["caractere/index.html", roster()],
  ...C.characters.map((c) => [`caractere/${c.id}/index.html`, character(c)]),
  ["genereaza/index.html", zonesHub()],
  ...C.zones.map((z) => [`genereaza/${z.id}/index.html`, zonePage(z)]),
  ["servicii/index.html", services()],
  ["nise/index.html", nichesPage()],
  ["cum-lucram/index.html", how()],
  ["platforma/index.html", platform()],
  ["transparenta/index.html", transparency()],
  ["contact/index.html", contact()],
  ["404.html", notFound()]
];

rmSync(OUT, { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });
cpSync(join(ROOT, "static"), OUT, { recursive: true });
for (const [file, html] of pages) {
  const target = join(OUT, file);
  mkdirSync(dirname(target), { recursive: true });
  writeFileSync(target, html);
}
const urls = pages.filter(([f]) => f !== "404.html").map(([f]) => "/" + f.replace(/index\.html$/, ""));
writeFileSync(join(OUT, "sitemap.xml"), `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.map((u) => `  <url><loc>${C.brand.url}${u}</loc></url>`).join("\n")}\n</urlset>\n`);
console.log(`Gata: ${pages.length} pagini în ${OUT}`);
