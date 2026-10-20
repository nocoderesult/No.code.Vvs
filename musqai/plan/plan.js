/* Planul MUSQAI: calculează orele fiecărei zile, ține bifele și notițele. */
(() => {
  "use strict";
  const P = window.PLAN;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  const cap = (name) =>
    window.claude && typeof window.claude.use === "function" ? window.claude.use(name).catch(() => null) : Promise.resolve(null);
  const WD = ["Luni", "Marți", "Miercuri", "Joi", "Vineri", "Sâmbătă", "Duminică"];
  const MON = ["ianuarie", "februarie", "martie", "aprilie", "mai", "iunie", "iulie", "august", "septembrie", "octombrie", "noiembrie", "decembrie"];
  const NW = P.weeks.length;
  const view = $("#view");

  /* ---------- Date și ore ---------- */
  const pad = (n) => String(n).padStart(2, "0");
  const parseISO = (s) => {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s || "");
    return m ? new Date(+m[1], +m[2] - 1, +m[3]) : null;
  };
  const iso = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const addDays = (d, n) => new Date(d.getFullYear(), d.getMonth(), d.getDate() + n);
  const between = (a, b) => Math.round((Date.UTC(b.getFullYear(), b.getMonth(), b.getDate()) - Date.UTC(a.getFullYear(), a.getMonth(), a.getDate())) / 86400000);
  const mondayOf = (d) => addDays(d, -((d.getDay() + 6) % 7));
  const fmtDay = (d) => `${d.getDate()} ${MON[d.getMonth()]}`;
  const fmtLong = (d) => `${WD[(d.getDay() + 6) % 7]}, ${d.getDate()} ${MON[d.getMonth()]}`;
  const hhmm = (m) => { const x = ((m % 1440) + 1440) % 1440; return `${pad(Math.floor(x / 60))}:${pad(x % 60)}`; };
  const toMin = (s) => { const [h, m] = String(s).split(":").map(Number); return h * 60 + (m || 0); };

  /* ---------- Starea ---------- */
  const S = {
    settings: { mode: 4, start: "09:00", startDate: P.startDefault },
    days: {},
    week0: { done: {} },
    eu: { done: {} },
    open: {},
    readOnly: false,
    backend: "local",
    selWeek: 0
  };
  const startDate = () => parseISO(S.settings.startDate) || parseISO(P.startDefault);
  const dayDate = (wi, di) => addDays(startDate(), wi * 7 + di);
  const dayId = (wi, di) => `w${pad(wi + 1)}-d${di + 1}`;
  const todayIndex = () => between(startDate(), new Date());

  function sanitizeSettings(v) {
    const out = {};
    if (v && [2, 4, 8].includes(Number(v.mode))) out.mode = Number(v.mode);
    if (v && /^\d{2}:\d{2}$/.test(v.start || "")) out.start = v.start;
    if (v && parseISO(v.startDate)) out.startDate = v.startDate;
    return out;
  }

  /* ---------- Rutina pe care o adaugă pagina ---------- */
  const R = {
    start: { key: "start", p: 1, min: 5, cat: "admin", title: "Planul zilei", how: ["Deschizi pagina la „Azi”.", "Citești acțiunea principală și blocurile zilei.", "Telefonul pe silențios până la prima pauză."], done: "Știi exact ce faci azi." },
    close: { key: "close", p: 1, min: 10, cat: "admin", title: "Închiderea zilei", how: ["Bifezi ce ai terminat.", "Scrii în notițele zilei cifrele și ce a rămas.", "Scrii primul pas de mâine, apoi te oprești."], done: "Ziua e închisă." },
    post: (w, di) => ({
      key: "post", p: 1, min: 20, cat: "cont", fixed: true,
      title: (w.postTitles && w.postTitles[di + 1]) || "Postarea zilei și 15 minute de răspunsuri",
      how: ["Verifici că postarea programată a ieșit, cu eticheta AI.", "1–3 stories: din culise, un sondaj sau o întrebare.", "15 minute: răspunzi la toate comentariile și mesajele, apoi lași 5 comentarii utile în nișă."],
      done: "Toate comentariile au primit răspuns."
    }),
    story: { key: "story", p: 1, min: 10, cat: "cont", fixed: true, title: "Stories și răspunsuri", how: ["1–2 stories.", "Răspunzi la mesaje și la comentarii."], done: "Toate mesajele au primit răspuns." },
    review: (w, wi) => ({
      key: "review", p: 1, min: 30, cat: "admin", title: `Recenzia săptămânii ${wi + 1}`,
      how: ["Cifrele: " + w.kpi.join(" · ") + ".", "Ce a mers, ce nu și o singură schimbare pentru săptămâna următoare.", "Notezi în plan/JURNAL.md sau îmi trimiți notițele."],
      done: "Recenzia e scrisă."
    }),
    next: (wi) =>
      wi + 1 < NW
        ? { key: "next", p: 1, min: 15, cat: "admin", title: `Pregătești săptămâna ${wi + 2}: ${P.weeks[wi + 1].title}`, how: ["Muți blocurile nebifate unde ai loc.", "Citești obiectivul săptămânii următoare."], done: "Știi cu ce începi luni." }
        : { key: "next", p: 1, min: 15, cat: "admin", title: "Odihnă: ai terminat cele 12 săptămâni", how: ["Planul pe lunile 4–6 îl facem împreună."], done: "Gata." }
  };

  function blocksFor(wi, di) {
    const w = P.weeks[wi], d = w.days[di];
    const date = dayDate(wi, di);
    const hol = P.holidays[iso(date)] || "";
    const mode = S.settings.mode;
    let maxP = mode === 2 ? 1 : mode === 4 ? 2 : 3;
    if (di === 5) maxP = Math.min(maxP, 2);
    if (di === 6 || hol) maxP = 1;
    const authored = (d.blocks || [])
      .map((b, i) => ({ key: "a" + i, p: b[0], min: b[1], cat: b[2], title: b[3], how: b[4] || [], done: b[5] || "" }))
      .filter((b) => b.p <= maxP);
    const workday = di < 6 && !hol;
    const seq = [];
    if (workday) seq.push(R.start);
    seq.push(...authored);
    if (di === 6) seq.push(R.review(w, wi), R.next(wi));
    if (workday) seq.push(R.close);

    const fixed = [];
    if ((w.post || []).includes(di + 1)) fixed.push(R.post(w, di));
    else if (w.live && !hol) fixed.push(R.story);
    const ft = toMin(P.postTime);
    const slots = fixed.map((b) => ({ ...b, s: ft, e: ft + b.min }));
    const clear = (s, len) => {
      let moved = true;
      while (moved) {
        moved = false;
        for (const f of slots) if (s < f.e && s + len > f.s) { s = f.e; moved = true; }
      }
      return s;
    };
    const out = [];
    let t = toMin(S.settings.start), since = 0, worked = 0, lunch = false;
    for (const b of seq) {
      if (mode === 8 && !lunch && worked >= 200 && b.min >= 15) {
        const s = clear(t, 45);
        out.push({ brk: true, title: "Prânz", min: 45, s, e: s + 45 });
        t = s + 45; since = 0; lunch = true;
      } else if (mode !== 2 && since >= 85 && b.min >= 15) {
        const s = clear(t, 10);
        out.push({ brk: true, title: "Pauză", min: 10, s, e: s + 10 });
        t = s + 10; since = 0;
      }
      const s = clear(t, b.min);
      out.push({ ...b, s, e: s + b.min });
      t = s + b.min; since += b.min; worked += b.min;
    }
    out.push(...slots);
    out.sort((a, b) => a.s - b.s);
    return { list: out, hol, date, theme: d.theme };
  }

  const isDone = (wi, di, key) => { const doc = S.days[dayId(wi, di)]; return !!(doc && doc.done && doc.done[key]); };
  function dayStats(wi, di) {
    const items = blocksFor(wi, di).list.filter((b) => !b.brk);
    return { done: items.filter((b) => isDone(wi, di, b.key)).length, total: items.length };
  }
  function weekStats(wi) {
    let done = 0, total = 0;
    for (let di = 0; di < 7; di++) { const s = dayStats(wi, di); done += s.done; total += s.total; }
    return { done, total };
  }
  function overallStats() {
    let done = 0, total = 0;
    for (let wi = 0; wi < NW; wi++) { const s = weekStats(wi); done += s.done; total += s.total; }
    return { done, total };
  }
  const pct = (s) => (s.total ? Math.round((s.done / s.total) * 100) : 0);

  /* ---------- Salvarea ---------- */
  let db = null;
  const LS = "musqai-plan-v1";
  function saveLocal() {
    try { localStorage.setItem(LS, JSON.stringify({ settings: S.settings, days: S.days, week0: S.week0, eu: S.eu })); } catch (_) { /* fără stocare locală */ }
  }
  function loadLocal() {
    try {
      const o = JSON.parse(localStorage.getItem(LS) || "null");
      if (!o) return;
      Object.assign(S.settings, sanitizeSettings(o.settings));
      S.days = o.days || {};
      S.week0 = o.week0 || { done: {} };
      S.eu = o.eu || { done: {} };
    } catch (_) { /* fără stocare locală */ }
  }
  const setSync = (t) => { const el = $("#sync"); if (el) el.textContent = t; };
  const queues = {};
  function persist(path, data) {
    if (!db) { saveLocal(); return; }
    const q = (queues[path] ||= { busy: false, next: null });
    q.next = data;
    if (!q.busy) drain(path);
  }
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  async function drain(path) {
    const q = queues[path];
    q.busy = true;
    setSync("Se salvează…");
    let failed = false;
    while (q.next) {
      const data = q.next;
      q.next = null;
      try {
        await db.doc(path).set(data);
      } catch (e) {
        const code = e && e.code;
        if (code === "invalid_argument" || code === "not_granted" || code === "revoked") {
          S.readOnly = true; q.next = null; failed = true;
          setSync("Doar citire: bifele nu se pot salva în această vizualizare.");
          render();
          break;
        }
        if (code === "unavailable") {
          await sleep(700 + Math.random() * 900);
          try { await db.doc(path).set(data); continue; } catch (_) { /* cade mai jos */ }
        }
        failed = true;
        setSync("Nu s-a salvat. Verifică conexiunea și bifează din nou.");
      }
    }
    q.busy = false;
    if (!failed) setSync("Salvat.");
  }

  function toggleDay(id, key) {
    if (S.readOnly) return;
    const cur = S.days[id] || { done: {}, note: "" };
    const done = { ...(cur.done || {}) };
    if (done[key]) delete done[key]; else done[key] = true;
    const next = { done, note: cur.note || "" };
    S.days[id] = next;
    persist("days/" + id, next);
    render();
  }
  function toggleMeta(which, key) {
    if (S.readOnly) return;
    const cur = S[which] || { done: {} };
    const done = { ...(cur.done || {}) };
    if (done[key]) delete done[key]; else done[key] = true;
    S[which] = { done };
    persist("meta/" + which, S[which]);
    render();
  }
  function saveSettings() { persist("meta/settings", { ...S.settings }); }

  /* ---------- Bucăți de interfață ---------- */
  const catChip = (c) => `<span class="chip cat-${c}">${esc(P.cats[c] || c)}</span>`;
  const check = (attrs, on, label) =>
    `<button type="button" class="check" role="checkbox" aria-checked="${on}" aria-label="${esc(label)}" ${attrs}${S.readOnly ? " disabled" : ""}></button>`;

  function slot(b, wi, di) {
    if (b.brk) {
      return `<li class="slot brk"><span class="time">${hhmm(b.s)}<small>${hhmm(b.e)}</small></span><div class="blk">${esc(b.title)} · ${b.min} min</div></li>`;
    }
    const id = dayId(wi, di);
    const on = isDone(wi, di, b.key);
    const openKey = id + "|" + b.key;
    const open = !!S.open[openKey];
    const has = (b.how && b.how.length) || b.done;
    return `<li class="slot${b.fixed ? " fixed" : ""}">
      <span class="time">${hhmm(b.s)}<small>${hhmm(b.e)}</small></span>
      <div class="blk${on ? " done" : ""}">
        ${check(`data-day="${id}" data-key="${b.key}"`, on, "Bifează: " + b.title)}
        <div><div class="t">${esc(b.title)}</div>
          <div class="meta">${catChip(b.cat)}<span class="mono">${b.min} min</span><span class="prio p${b.p}" title="${b.p === 1 ? "Drumul critic" : b.p === 2 ? "Important" : "Accelerează"}">P${b.p}</span>${b.fixed ? `<span class="chip acc">fix la ${esc(P.postTime)}</span>` : ""}</div>
        </div>
        ${has ? `<button type="button" class="more" data-open="${esc(openKey)}" aria-expanded="${open}">${open ? "Ascunde" : "Cum"}</button>` : "<span></span>"}
        ${open ? `<div class="det">${b.how.length ? `<ol>${b.how.map((x) => `<li>${esc(x)}</li>`).join("")}</ol>` : ""}${b.done ? `<p class="gata"><b>Gata când:</b> ${esc(b.done)}</p>` : ""}</div>` : ""}
      </div>
    </li>`;
  }

  function sidePanels(wi) {
    const w = P.weeks[wi];
    const modeText = {
      2: "Doar drumul critic (P1). Ce e P2 se mută sâmbăta sau în săptămâna următoare.",
      4: "Drumul critic și ce e important (P1 + P2). Ritmul standard al planului.",
      8: "Tot, inclusiv ce accelerează (P3). Sâmbăta e jumătate de zi, duminica e liberă."
    }[S.settings.mode];
    return `
      <div class="panel stack">
        <span class="eyebrow">Săptămâna ${wi + 1} · obiectivul</span>
        <p><b>${esc(w.title)}.</b> ${esc(w.goal)}</p>
        <ul class="kpi-list">${w.kpi.map((k) => `<li>${esc(k)}</li>`).join("")}</ul>
        ${w.gate ? `<p class="gate">Poarta de decizie: ${esc(w.gate)}</p>` : ""}
      </div>
      <div class="panel">
        <span class="eyebrow">Ce pregătește Claude săptămâna asta</span>
        <ul class="side-list" style="margin-top:8px">${w.eu.map((t, i) => { const k = `w${pad(wi + 1)}-${i}`; const on = !!(S.eu.done && S.eu.done[k]); return `<li>${check(`data-meta="eu" data-key="${k}"`, on, "Bifează: " + t)}<span>${esc(t)}</span></li>`; }).join("")}</ul>
        <p class="muted small" style="margin-top:10px">Le ceri în sesiunea de luni: „Citește plan/PLAN_COMPLET.md și plan/JURNAL.md, suntem la săptămâna ${wi + 1}.”</p>
      </div>
      <div class="panel stack" style="gap:6px">
        <span class="eyebrow">Modul de ${S.settings.mode} ore</span>
        <p class="small">${esc(modeText)}</p>
      </div>`;
  }

  /* ---------- Vederile ---------- */
  function renderDay(wi, di) {
    const { list, hol, date, theme } = blocksFor(wi, di);
    const st = dayStats(wi, di);
    const idx = wi * 7 + di;
    const isToday = idx === todayIndex();
    const id = dayId(wi, di);
    const main = list.find((b) => !b.brk && b.key[0] === "a" && b.p === 1);
    const w = P.weeks[wi];
    return `<div class="grid-side">
      <section>
        <div class="day-head">
          <div class="row">${isToday ? '<span class="chip acc">Azi</span>' : ""}<span class="chip">Săptămâna ${wi + 1} · ziua ${di + 1}</span><span class="chip">${esc(theme)}</span>${hol ? `<span class="chip hol">▲ Sărbătoare: ${esc(hol)}</span>` : ""}</div>
          <h2>${esc(fmtLong(date))}</h2>
          <div class="row" style="justify-content:space-between">
            <div class="ring"><b>${st.done}/${st.total}</b><span class="muted small">blocuri bifate</span></div>
            <div class="day-nav">
              <button type="button" class="btn" data-go="${idx - 1}"${idx <= 0 ? " disabled" : ""}>← Ziua dinainte</button>
              <button type="button" class="btn" data-go="today">Azi</button>
              <button type="button" class="btn" data-go="${idx + 1}"${idx >= NW * 7 - 1 ? " disabled" : ""}>Ziua următoare →</button>
            </div>
          </div>
        </div>
        ${main ? `<div class="focus"><span class="eyebrow">Acțiunea principală a zilei · ${hhmm(main.s)}</span><b>${esc(main.title)}</b></div>` : hol ? `<div class="focus"><span class="eyebrow">Sărbătoare</span><b>Zi liberă. Doar ce e programat.</b></div>` : ""}
        ${list.length ? `<ol class="timeline">${list.map((b) => slot(b, wi, di)).join("")}</ol>` : `<p class="empty">Zi liberă. Odihnește-te.</p>`}
        <div class="stack" style="margin-top:22px;gap:8px">
          <label for="day-note" class="eyebrow">Notițele zilei</label>
          <textarea id="day-note" class="note" data-day="${id}" placeholder="Cifrele zilei, ce a rămas, ce ai observat."${S.readOnly ? " readonly" : ""}></textarea>
        </div>
      </section>
      <aside class="stack">${sidePanels(wi)}</aside>
    </div>`;
  }

  function renderWeek(wi) {
    const w = P.weeks[wi];
    const ws = weekStats(wi);
    const first = dayDate(wi, 0), last = dayDate(wi, 6);
    const ti = todayIndex();
    return `
      <div class="week-head">
        <div class="stack" style="gap:6px">
          <span class="eyebrow">Săptămâna ${wi + 1} din ${NW} · ${fmtDay(first)} – ${fmtDay(last)}</span>
          <h2>${esc(w.title)}</h2>
          <p class="muted">${esc(w.goal)}</p>
        </div>
        <div class="row">
          <button type="button" class="btn" data-week="${wi - 1}"${wi <= 0 ? " disabled" : ""}>← Săptămâna ${wi}</button>
          <button type="button" class="btn" data-week="${wi + 1}"${wi >= NW - 1 ? " disabled" : ""}>Săptămâna ${wi + 2} →</button>
        </div>
      </div>
      <div class="panel row" style="justify-content:space-between;margin-bottom:14px">
        <div class="stack" style="gap:6px;min-width:200px;flex:1"><span class="eyebrow">Progresul săptămânii · ${ws.done} din ${ws.total} blocuri</span><div class="bar"><i style="width:${pct(ws)}%"></i></div></div>
        <button type="button" class="btn" id="export" data-export="${wi}" hidden>Exportă pentru Google Calendar</button>
      </div>
      ${w.gate ? `<p class="gate" style="margin-bottom:14px">Poarta de decizie: ${esc(w.gate)}</p>` : ""}
      <div class="days7">${[0, 1, 2, 3, 4, 5, 6].map((di) => {
        const { list, hol, date, theme } = blocksFor(wi, di);
        const st = dayStats(wi, di);
        const items = list.filter((b) => !b.brk);
        const today = wi * 7 + di === ti;
        return `<div class="dcard${today ? " today" : ""}">
          <h3><a href="#s${wi + 1}-d${di + 1}">${WD[di].slice(0, 2)} ${date.getDate()} ${MON[date.getMonth()].slice(0, 3)}.</a><span class="mono tnum">${st.done}/${st.total}</span></h3>
          <span class="th">${esc(theme)}</span>
          ${hol ? `<span class="chip hol">▲ ${esc(hol)}</span>` : ""}
          ${items.length ? `<ul class="mini">${items.map((b) => { const on = isDone(wi, di, b.key); return `<li class="${on ? "done" : ""}">${check(`data-day="${dayId(wi, di)}" data-key="${b.key}"`, on, "Bifează: " + b.title)}<span><span class="tm">${hhmm(b.s)} · P${b.p}</span>${esc(b.title)}</span></li>`; }).join("")}</ul>` : `<span class="muted small">Zi liberă.</span>`}
        </div>`;
      }).join("")}</div>
      <div class="grid-side" style="margin-top:20px"><div class="panel stack">
        <span class="eyebrow">Cum folosești săptămâna</span>
        <p class="small">Apasă pe o zi ca să vezi orele și pașii fiecărui bloc. Bifele de aici sunt aceleași cu cele din ziua respectivă.</p>
        <p class="small muted">Exportul pune blocurile săptămânii, cu orele modului ales, într-un fișier pe care îl imporți în Google Calendar (Setări → Import).</p>
      </div><aside class="stack">${sidePanels(wi)}</aside></div>`;
  }

  function renderRoadmap() {
    const ti = todayIndex();
    const nowW = ti >= 0 && ti < NW * 7 ? Math.floor(ti / 7) : -1;
    const w0done = P.week0.filter((_, i) => S.week0.done && S.week0.done["p" + i]).length;
    return `<div class="grid-side">
      <section>
        <div class="stack" style="gap:6px;margin-bottom:12px"><span class="eyebrow">${fmtDay(startDate())} ${startDate().getFullYear()} – ${fmtDay(dayDate(NW - 1, 6))} ${dayDate(NW - 1, 6).getFullYear()}</span><h2 style="font-family:var(--f-display);font-size:clamp(28px,4vw,42px);font-weight:600">Toate cele 12 săptămâni</h2></div>
        <ol class="ledger">${P.weeks.map((w, wi) => {
          const s = weekStats(wi);
          return `<li class="${wi === nowW ? "now" : ""}">
            <a class="wn" href="#s${wi + 1}">${wi + 1}</a>
            <span class="mono">${fmtDay(dayDate(wi, 0))} – ${fmtDay(dayDate(wi, 6))}</span>
            <a href="#s${wi + 1}" class="stack" style="gap:2px"><span class="wt">${esc(w.title)}</span><span class="wg">${esc(w.goal)}</span>${w.gate ? `<span class="chip hol" style="justify-self:start;margin-top:4px">▲ Decizie</span>` : ""}</a>
            <span class="stack" style="gap:4px"><span class="mono tnum">${pct(s)}% · ${s.done}/${s.total}</span><span class="bar"><i style="width:${pct(s)}%"></i></span></span>
          </li>`;
        }).join("")}</ol>
      </section>
      <aside class="stack">
        <div class="panel">
          <span class="eyebrow">Săptămâna 0 · înainte de start · ${w0done}/${P.week0.length}</span>
          <ul class="w0" style="margin-top:8px">${P.week0.map(([t, d], i) => { const on = !!(S.week0.done && S.week0.done["p" + i]); return `<li>${check(`data-meta="week0" data-key="p${i}"`, on, "Bifează: " + t)}<span><b style="font-weight:650">${esc(t)}</b><br><span class="muted small">${esc(d)}</span></span></li>`; }).join("")}</ul>
        </div>
      </aside>
    </div>`;
  }

  function renderRoutines() {
    const steps = (arr) => `<ol style="padding-left:18px;display:grid;gap:4px" class="small">${arr.map((x) => `<li>${esc(x)}</li>`).join("")}</ol>`;
    return `<div class="stack" style="gap:22px">
      <div class="cols-2">
        <div class="panel"><span class="eyebrow">Cum lucrează cei mai buni</span>
          <ul class="princ" style="margin-top:6px">${P.principles.map(([a, src, b]) => `<li><b>${esc(a)}</b><span class="src">${esc(src)}</span><span class="small">${esc(b)}</span></li>`).join("")}</ul>
        </div>
        <div class="stack">
          <div class="panel"><span class="eyebrow">Zilele săptămânii</span>
            <div class="tbl-wrap" style="margin-top:8px"><table class="tbl"><thead><tr><th>Zi</th><th>Tema</th><th>Ce faci</th></tr></thead><tbody>${P.themes.map(([d, t, x]) => `<tr><td><b>${esc(d)}</b></td><td>${esc(t)}</td><td class="muted">${esc(x)}</td></tr>`).join("")}</tbody></table></div>
          </div>
          <div class="panel stack"><span class="eyebrow">Prioritățile</span>
            <p class="small"><b>P1, drumul critic.</b> Se face în fiecare mod, chiar și în cel de 2 ore.</p>
            <p class="small"><b>P2, important.</b> Intră în modul de 4 ore, ritmul standard.</p>
            <p class="small"><b>P3, accelerează.</b> Intră doar în modul de 8 ore.</p>
            <div class="legend">${Object.keys(P.cats).map(catChip).join("")}</div>
          </div>
        </div>
      </div>
      <div class="cols-2">
        <div class="panel stack"><span class="eyebrow">Rutina zilnică</span>
          <p><b>Planul zilei · 5 min</b></p>${steps(R.start.how)}
          <p><b>Închiderea zilei · 10 min</b></p>${steps(R.close.how)}
          <p><b>Postarea de la ${esc(P.postTime)} · 20 min</b></p>${steps(R.post(P.weeks[1], 0).how)}
        </div>
        <div class="panel stack"><span class="eyebrow">Rutina pe pod (GPU)</span>
          ${steps(["Pornești podul L40S pe RunPod.", "Rulezi /workspace/porneste.sh și pui noul Bridge URL în Agent Panel.", "Primul mesaj: „Read /workspace/persist/DARIA_CONTEXT.md, the pod restarted, continue.”", "Lucrezi în loturi: tot ce ai de generat azi, deodată.", "Mesajul de final: „Before we stop: update /workspace/persist/DARIA_CONTEXT.md with what we did today, the file paths, and the next step.”", "Oprești podul imediat."])}
          <p><b>Recenzia de duminică · 30 min</b></p>${steps(["Cifrele săptămânii, din tabel.", "Ce a mers, ce nu.", "O singură schimbare pentru săptămâna următoare.", "Notezi în jurnal."])}
        </div>
      </div>
    </div>`;
  }

  function renderBefore() {
    const n = -todayIndex();
    return `<div class="grid-side">
      <section>
        <div class="day-head"><span class="chip acc" style="justify-self:start">Înainte de start</span>
          <h2>Începem ${esc(fmtLong(startDate()).toLowerCase())}${n === 1 ? ", mâine" : `, peste ${n} zile`}.</h2>
          <p class="muted">Până atunci, săptămâna 0: pașii de pregătire. Prima zi o vezi mai jos.</p>
        </div>
        <div class="panel"><span class="eyebrow">Săptămâna 0 · pregătire</span>
          <ul class="w0" style="margin-top:8px">${P.week0.map(([t, d], i) => { const on = !!(S.week0.done && S.week0.done["p" + i]); return `<li>${check(`data-meta="week0" data-key="p${i}"`, on, "Bifează: " + t)}<span><b style="font-weight:650">${esc(t)}</b><br><span class="muted small">${esc(d)}</span></span></li>`; }).join("")}</ul>
        </div>
        <p style="margin-top:18px"><a class="btn primary" href="#s1-d1">Vezi prima zi</a> <a class="btn" href="#s1">Vezi săptămâna 1</a></p>
      </section>
      <aside class="stack">${sidePanels(0)}</aside>
    </div>`;
  }

  function renderAfter() {
    const s = overallStats();
    return `<div class="panel stack"><span class="eyebrow">Plan încheiat</span><h2 style="font-family:var(--f-display);font-size:40px">Ai terminat cele 12 săptămâni.</h2><p>Ai bifat ${s.done} din ${s.total} blocuri (${pct(s)}%). Planul pe lunile 4–6 îl facem împreună, pornind de la recenzii.</p><p><a class="btn" href="#roadmap">Vezi toate săptămânile</a></p></div>`;
  }

  /* ---------- Router ---------- */
  let current = { name: "azi" };
  function parseHash() {
    const h = decodeURIComponent((location.hash || "#azi").slice(1));
    let m;
    if ((m = /^s(\d{1,2})-d([1-7])$/.exec(h))) {
      const wi = Math.min(NW, Math.max(1, +m[1])) - 1;
      return { name: "day", wi, di: +m[2] - 1 };
    }
    if ((m = /^s(\d{1,2})$/.exec(h))) return { name: "week", wi: Math.min(NW, Math.max(1, +m[1])) - 1 };
    if (h === "saptamana") return { name: "week", wi: null };
    if (h === "roadmap" || h === "rutine") return { name: h };
    return { name: "azi" };
  }
  function render() {
    const keepNote = document.activeElement && document.activeElement.id === "day-note";
    if (keepNote) { pendingRender = true; return; }
    const r = current;
    const ti = todayIndex();
    let html = "", tab = r.name;
    if (r.name === "azi") {
      if (ti < 0) html = renderBefore();
      else if (ti >= NW * 7) html = renderAfter();
      else { S.selWeek = Math.floor(ti / 7); html = renderDay(Math.floor(ti / 7), ti % 7); }
    } else if (r.name === "day") {
      S.selWeek = r.wi;
      html = renderDay(r.wi, r.di);
      tab = r.wi * 7 + r.di === ti ? "azi" : "saptamana";
    } else if (r.name === "week") {
      const wi = r.wi ?? (ti >= 0 && ti < NW * 7 ? Math.floor(ti / 7) : S.selWeek);
      S.selWeek = wi;
      html = renderWeek(wi);
      tab = "saptamana";
    } else if (r.name === "roadmap") html = renderRoadmap();
    else html = renderRoutines();
    view.innerHTML = html;
    $$("[data-tab]").forEach((a) => a.classList.toggle("on", a.dataset.tab === tab));
    const tabWeek = $('[data-tab="saptamana"]');
    if (tabWeek) tabWeek.setAttribute("href", "#s" + (S.selWeek + 1));
    const note = $("#day-note");
    if (note) { const doc = S.days[note.dataset.day]; note.value = (doc && doc.note) || ""; }
    const s = overallStats();
    $("#overall-pct").textContent = pct(s) + "%";
    $("#overall-bar").style.width = pct(s) + "%";
    $("#range").textContent = `${fmtDay(startDate())} ${startDate().getFullYear()} – ${fmtDay(dayDate(NW - 1, 6))} ${dayDate(NW - 1, 6).getFullYear()} · ${NW * 7} de zile`;
    showExport();
  }
  let pendingRender = false;
  let raf = 0;
  const scheduleRender = () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(render); };
  function route() {
    current = parseHash();
    pendingRender = false;
    if (document.activeElement && document.activeElement.id === "day-note") document.activeElement.blur();
    render();
    window.scrollTo(0, 0);
  }

  /* ---------- Export pentru Google Calendar ---------- */
  let downloadsCap = null;
  async function showExport() {
    const b = $("#export");
    if (!b) return;
    if (downloadsCap === null) downloadsCap = (await cap("downloads")) || false;
    if (b.isConnected) b.hidden = !downloadsCap;
  }
  const csvCell = (v) => { const s = String(v ?? ""); return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
  const mdy = (d) => `${pad(d.getMonth() + 1)}/${pad(d.getDate())}/${d.getFullYear()}`;
  const ampm = (m) => { const x = ((m % 1440) + 1440) % 1440; const h = Math.floor(x / 60); return `${pad(h % 12 || 12)}:${pad(x % 60)} ${h < 12 ? "AM" : "PM"}`; };
  async function exportWeek(wi) {
    if (!downloadsCap) return;
    const rows = [["Subject", "Start Date", "Start Time", "End Date", "End Time", "Description", "Private"]];
    for (let di = 0; di < 7; di++) {
      const { list, date } = blocksFor(wi, di);
      for (const b of list) {
        if (b.brk) continue;
        const sd = addDays(date, Math.floor(b.s / 1440)), ed = addDays(date, Math.floor(b.e / 1440));
        const desc = [...(b.how || []), b.done ? "Gata când: " + b.done : ""].filter(Boolean).join("\n");
        rows.push([`[MUSQAI] ${b.title}`, mdy(sd), ampm(b.s), mdy(ed), ampm(b.e), desc, "True"]);
      }
    }
    const csv = rows.map((r) => r.map(csvCell).join(",")).join("\r\n");
    try {
      await downloadsCap.save({ filename: `musqai-saptamana-${wi + 1}-${S.settings.mode}h.csv`, data: csv });
      toast("Salvat. În Google Calendar: Setări → Import.");
    } catch (e) {
      if (e && e.code !== "declined") toast("Exportul n-a mers. Încearcă din nou.");
    }
  }

  /* ---------- Evenimente ---------- */
  let toastTimer = 0;
  function toast(msg) {
    const t = $("#toast");
    t.textContent = msg; t.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => (t.hidden = true), 2800);
  }
  document.addEventListener("click", (e) => {
    const c = e.target.closest(".check");
    if (c && !c.disabled) {
      if (c.dataset.day) toggleDay(c.dataset.day, c.dataset.key);
      else if (c.dataset.meta) toggleMeta(c.dataset.meta, c.dataset.key);
      return;
    }
    const o = e.target.closest("[data-open]");
    if (o) { S.open[o.dataset.open] = !S.open[o.dataset.open]; render(); return; }
    const g = e.target.closest("[data-go]");
    if (g && !g.disabled) {
      const v = g.dataset.go;
      if (v === "today") { location.hash = "#azi"; return; }
      const idx = Number(v);
      location.hash = `#s${Math.floor(idx / 7) + 1}-d${(idx % 7) + 1}`;
      return;
    }
    const wk = e.target.closest("[data-week]");
    if (wk && !wk.disabled) { location.hash = "#s" + (Number(wk.dataset.week) + 1); return; }
    const ex = e.target.closest("[data-export]");
    if (ex) exportWeek(Number(ex.dataset.export));
  });
  let noteTimer = 0;
  document.addEventListener("input", (e) => {
    if (e.target.id !== "day-note" || S.readOnly) return;
    const id = e.target.dataset.day, value = e.target.value;
    clearTimeout(noteTimer);
    noteTimer = setTimeout(() => {
      const cur = S.days[id] || { done: {}, note: "" };
      const next = { done: { ...(cur.done || {}) }, note: value.slice(0, 8000) };
      S.days[id] = next;
      persist("days/" + id, next);
    }, 700);
  });
  document.addEventListener("focusout", (e) => {
    if (e.target.id === "day-note" && pendingRender) { pendingRender = false; setTimeout(render, 0); }
  });

  function applyControls() {
    $$("#mode button").forEach((b) => b.setAttribute("aria-pressed", String(Number(b.dataset.mode) === S.settings.mode)));
    const st = $("#start-time");
    if (!st.options.length) {
      for (let m = 5 * 60; m <= 20 * 60; m += 30) st.insertAdjacentHTML("beforeend", `<option value="${hhmm(m)}">${hhmm(m)}</option>`);
    }
    st.value = S.settings.start;
    $("#start-date").value = S.settings.startDate;
  }
  $("#mode").addEventListener("click", (e) => {
    const b = e.target.closest("button[data-mode]");
    if (!b) return;
    S.settings.mode = Number(b.dataset.mode);
    applyControls(); saveSettings(); render();
  });
  $("#start-time").addEventListener("change", (e) => { S.settings.start = e.target.value; saveSettings(); render(); });
  $("#start-date").addEventListener("change", (e) => {
    const d = parseISO(e.target.value);
    if (!d) { e.target.value = S.settings.startDate; return; }
    const m = mondayOf(d);
    S.settings.startDate = iso(m);
    if (iso(m) !== iso(d)) toast(`Planul începe lunea: ${fmtDay(m)}.`);
    applyControls(); saveSettings(); render();
  });
  window.addEventListener("hashchange", route);

  /* ---------- Pornire ---------- */
  loadLocal();
  applyControls();
  route();
  (async () => {
    db = await cap("db");
    if (!db) { setSync("Bifele se salvează doar în acest browser."); return; }
    S.backend = "db";
    setSync("Bifele se salvează automat.");
    const user = await cap("user");
    if (user) {
      const can = await user.can("data.write");
      if (can === false) { S.readOnly = true; setSync("Doar citire."); render(); }
    }
    const onErr = () => setSync("Legătura cu salvarea s-a întrerupt. Reîncarcă pagina.");
    db.collection("days").onSnapshot((snap) => {
      const m = {};
      snap.docs.forEach((d) => (m[d.id] = d.data()));
      S.days = m;
      scheduleRender();
    }, onErr);
    db.collection("meta").onSnapshot((snap) => {
      snap.docs.forEach((d) => {
        const v = d.data() || {};
        if (d.id === "settings") Object.assign(S.settings, sanitizeSettings(v));
        if (d.id === "week0") S.week0 = { done: { ...(v.done || {}) } };
        if (d.id === "eu") S.eu = { done: { ...(v.done || {}) } };
      });
      applyControls();
      scheduleRender();
    }, onErr);
  })();
})();
