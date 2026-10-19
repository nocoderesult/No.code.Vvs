// Intrarea: video-ul salonului, derulat de scroll pe un canvas, cu monograma RA desenată peste.
// Cadrele vin din public/assets/seq/ (scripts/make-sequence.sh). Fazele, din progresul scroll-ului (0–1):
//   0.06–0.29  R și A urcă pe rând din linia de bază; apoi apare „BARBERSHOP”
//   0.50–0.72  literele devin ferestre: în jur se întunecă, video-ul se vede doar prin RA
//   0.78–0.94  RA urcă și se micșorează; apar mesajul și butonul de programare

const { gsap, ScrollTrigger } = window;

const LABEL = 'BARBERSHOP';
const CENTER_Y = 0.45; // poziția verticală a monogramei, din înălțimea ecranului
const PARALLEL_LOADS = 6;

const clamp01 = (v) => Math.min(1, Math.max(0, v));
const easeOut = (t) => 1 - Math.pow(1 - t, 3);
const smooth = (t) => t * t * (3 - 2 * t);
const lerp = (a, b, t) => a + (b - a) * t;
const span = (p, a, b) => clamp01((p - a) / (b - a));

export function initIntro({ reduceMotion }) {
  const section = document.querySelector('[data-intro]');
  const stage = section.querySelector('[data-intro-stage]');
  const canvas = section.querySelector('[data-intro-canvas]');
  const ctx = canvas.getContext('2d');
  const mask = document.createElement('canvas');
  const mctx = mask.getContext('2d');
  const hint = section.querySelector('[data-intro-hint]');
  const end = section.querySelector('[data-intro-end]');
  const dim = section.querySelector('[data-intro-dim]');

  const state = { p: 0 };
  let seq = null; // { count, frames }
  let m = null; // dimensiunile monogramei, calculate la resize
  let dpr = 1;
  let W = 0;
  let H = 0;
  let cssW = 0;
  let cssH = 0;

  // ---------- Dimensiuni ----------
  function measure() {
    ctx.font = '500 100px "Bodoni Moda"';
    const size = ((W * 0.78) / ctx.measureText('RA').width) * 100;
    ctx.font = `500 ${size}px "Bodoni Moda"`;
    const r = ctx.measureText('R');
    const a = ctx.measureText('A');
    const total = ctx.measureText('RA').width;
    const cap = r.actualBoundingBoxAscent || size * 0.68;
    const labelSize = Math.max(11 * dpr, W * 0.03);
    ctx.font = `500 ${labelSize}px Inter`;
    const labelWidths = [...LABEL].map((ch) => ctx.measureText(ch).width);
    const labelGap = labelSize * 0.55;
    const gradient = ctx.createLinearGradient(0, -cap / 2, 0, cap / 2);
    gradient.addColorStop(0, '#f7eedd');
    gradient.addColorStop(0.55, '#e3cda4');
    gradient.addColorStop(1, '#b8915a');
    m = {
      size, cap, total, gradient, labelSize, labelWidths, labelGap,
      wR: r.width,
      kern: total - r.width - a.width,
      labelTotal: labelWidths.reduce((s, w) => s + w, 0) + labelGap * (LABEL.length - 1),
    };
  }

  function resize() {
    cssW = stage.clientWidth;
    cssH = stage.clientHeight;
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = canvas.width = mask.width = Math.round(cssW * dpr);
    H = canvas.height = mask.height = Math.round(cssH * dpr);
    measure();
    render();
  }

  // ---------- Desen ----------
  function cover(img, alpha) {
    const ir = img.naturalWidth / img.naturalHeight;
    let w = W;
    let h = H;
    if (ir > W / H) w = H * ir;
    else h = W / ir;
    ctx.globalAlpha = alpha;
    ctx.drawImage(img, (W - w) / 2, (H - h) / 2, w, h);
    ctx.globalAlpha = 1;
  }

  function nearestLoaded(i) {
    const f = seq.frames;
    if (f[i]) return f[i];
    for (let d = 1; d < seq.count; d++) {
      if (f[i - d]) return f[i - d];
      if (f[i + d]) return f[i + d];
    }
    return null;
  }

  // Cadrul curent, amestecat cu următorul, ca scroll-ul să curgă fără sacadări
  function drawVideo(p) {
    const pos = p * (seq.count - 1);
    const i = Math.floor(pos);
    const t = pos - i;
    const base = nearestLoaded(i);
    if (base) cover(base, 1);
    const next = t > 0.02 && seq.frames[i + 1];
    if (next) cover(next, t);
  }

  // Desenează R și A în jurul centrului; literele urcă din linia de bază (clip pe linia de bază)
  function letters(target, g, mode, style) {
    target.save();
    target.translate(W / 2, H * CENTER_Y - g.shift);
    target.scale(g.scale, g.scale);
    target.font = `500 ${m.size}px "Bodoni Moda"`;
    target.textBaseline = 'alphabetic';
    const x0 = -m.total / 2;
    const base = m.cap / 2;
    target.beginPath();
    target.rect(-W, -H, W * 2, H + base + m.size * 0.03);
    target.clip();
    const parts = [['R', x0, g.aR, g.riseR], ['A', x0 + m.wR + m.kern, g.aA, g.riseA]];
    for (const [ch, x, alpha, rise] of parts) {
      if (alpha <= 0.001) continue;
      target.globalAlpha = alpha * g.alpha;
      if (mode === 'stroke') {
        target.strokeStyle = style;
        target.lineWidth = (0.9 * dpr) / g.scale;
        target.strokeText(ch, x, base + rise);
      } else {
        target.fillStyle = style;
        target.fillText(ch, x, base + rise);
      }
    }
    target.restore();
  }

  function label(g, alpha) {
    if (alpha <= 0.001) return;
    ctx.save();
    ctx.translate(W / 2, H * CENTER_Y - g.shift);
    ctx.scale(g.scale, g.scale);
    ctx.globalAlpha = alpha;
    const lineY = m.cap / 2 + m.size * 0.15;
    const lineW = W * 0.1 * alpha;
    ctx.fillStyle = 'rgba(230, 210, 173, 0.85)';
    ctx.fillRect(-lineW / 2, lineY, lineW, Math.max(1, dpr));
    ctx.font = `500 ${m.labelSize}px Inter`;
    ctx.textBaseline = 'alphabetic';
    ctx.fillStyle = 'rgba(241, 235, 225, 0.92)';
    let x = -m.labelTotal / 2;
    const y = lineY + m.labelSize * 2.3;
    [...LABEL].forEach((ch, i) => {
      ctx.fillText(ch, x, y);
      x += m.labelWidths[i] + m.labelGap;
    });
    ctx.restore();
  }

  function render() {
    if (!W || !m) return;
    const p = state.p;
    const still = reduceMotion;
    const aR = still ? 1 : easeOut(span(p, 0.06, 0.24));
    const aA = still ? 1 : easeOut(span(p, 0.11, 0.29));
    const aL = still ? 1 : easeOut(span(p, 0.22, 0.34));
    const w = still ? 0 : smooth(span(p, 0.5, 0.72));
    const q = still ? 0 : smooth(span(p, 0.78, 0.94));
    const shown = Math.max(aR, aA);
    const g = {
      aR, aA, alpha: 1,
      riseR: (1 - aR) * m.cap * 1.05,
      riseA: (1 - aA) * m.cap * 1.05,
      scale: lerp(1.04, 1, shown) * lerp(1, 0.84, q),
      shift: H * 0.085 * q,
    };

    ctx.globalCompositeOperation = 'source-over';
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, W, H);
    if (seq) drawVideo(p);

    // Strat întunecat cu „gaură” în forma literelor: din ce în ce mai opac în jur, transparent în litere
    const darkness = lerp(0.2 + 0.3 * shown, 0.93, w);
    mctx.globalCompositeOperation = 'source-over';
    mctx.clearRect(0, 0, W, H);
    mctx.fillStyle = `rgba(5, 4, 3, ${darkness})`;
    mctx.fillRect(0, 0, W, H);
    if (w > 0.001) {
      mctx.globalCompositeOperation = 'destination-out';
      letters(mctx, { ...g, alpha: w }, 'fill', '#000');
      mctx.globalCompositeOperation = 'source-over';
    }
    ctx.drawImage(mask, 0, 0);

    // Umbre discrete sus și jos, pentru meniu și textele de jos
    const top = ctx.createLinearGradient(0, 0, 0, H * 0.16);
    top.addColorStop(0, 'rgba(0, 0, 0, 0.35)');
    top.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = top;
    ctx.fillRect(0, 0, W, H * 0.16);
    const bottom = ctx.createLinearGradient(0, H * 0.62, 0, H);
    bottom.addColorStop(0, 'rgba(0, 0, 0, 0)');
    bottom.addColorStop(1, 'rgba(0, 0, 0, 0.55)');
    ctx.fillStyle = bottom;
    ctx.fillRect(0, H * 0.62, W, H * 0.38);

    // Literele pline se sting pe măsură ce devin ferestre; video-ul din ele primește o lumină
    // aurie discretă, iar conturul fin le păstrează forma
    if (w < 0.999) letters(ctx, { ...g, alpha: 1 - w }, 'fill', m.gradient);
    if (w > 0.001) {
      ctx.globalCompositeOperation = 'soft-light';
      letters(ctx, { ...g, alpha: 0.75 * w }, 'fill', m.gradient);
      ctx.globalCompositeOperation = 'source-over';
      letters(ctx, { ...g, alpha: 0.6 * w }, 'stroke', 'rgb(230, 210, 173)');
    }
    label(g, aL);
  }

  // ---------- Încărcare ----------
  async function loadManifest() {
    try {
      const res = await fetch('assets/seq/manifest.json', { cache: 'no-cache' });
      return res.ok ? await res.json() : null;
    } catch {
      return null;
    }
  }

  // Ordine grosier → fin: întâi fiecare al 16-lea cadru, ca scroll-ul să meargă imediat
  function loadOrder(count) {
    const seen = new Uint8Array(count);
    const order = [];
    for (const step of [16, 8, 4, 2, 1]) {
      for (let i = 0; i < count; i += step) {
        if (!seen[i]) { seen[i] = 1; order.push(i); }
      }
    }
    return order;
  }

  async function preload(onProgress) {
    await Promise.all([
      document.fonts.load('500 100px "Bodoni Moda"'),
      document.fonts.load('500 16px Inter'),
    ]).catch(() => {});
    resize();
    const manifest = await loadManifest();
    const variant = manifest && (manifest.mobile || manifest.desktop);
    if (!variant) {
      onProgress(1);
      return;
    }
    seq = { count: variant.count, frames: new Array(variant.count) };
    const order = loadOrder(variant.count);
    const gate = Math.max(1, Math.ceil(order.length * 0.35));
    const url = (i) => `${variant.path}${String(i + 1).padStart(variant.pad || 4, '0')}.${variant.ext || 'webp'}`;
    let done = 0;
    let next = 0;
    await new Promise((resolve) => {
      const pump = () => {
        if (next >= order.length) return;
        const i = order[next++];
        const img = new Image();
        img.decoding = 'async';
        img.onload = img.onerror = () => {
          if (img.naturalWidth) seq.frames[i] = img;
          done++;
          if (done <= gate) onProgress(done / gate);
          if (done === gate) resolve();
          if (i === 0) render();
          pump();
        };
        img.src = url(i);
      };
      for (let k = 0; k < PARALLEL_LOADS; k++) pump();
    });
    render();
  }

  // ---------- Scroll ----------
  function buildScroll() {
    const tl = gsap.timeline({ defaults: { ease: 'none' } });
    tl.to(state, { p: 1, duration: 1, onUpdate: render }, 0);
    tl.to(hint, { autoAlpha: 0, duration: 0.05 }, 0.02);
    tl.fromTo(end, { autoAlpha: 0, y: 24 }, { autoAlpha: 1, y: 0, duration: 0.12 }, 0.84);

    ScrollTrigger.create({
      trigger: section,
      start: 'top top',
      // video-ul se termină înainte ca secțiunea următoare să urce peste el
      end: () => '+=' + Math.max(1, section.offsetHeight - 2 * stage.offsetHeight),
      scrub: 1,
      animation: tl,
      invalidateOnRefresh: true,
    });

    gsap.timeline({ scrollTrigger: { trigger: '.curtain', start: 'top bottom', end: 'top top', scrub: true } })
      .to(stage, { scale: 0.92, ease: 'none' }, 0)
      .to(dim, { opacity: 0.7, ease: 'none' }, 0);
  }

  function start() {
    if (reduceMotion) {
      gsap.set(hint, { autoAlpha: 0 });
      gsap.set(end, { autoAlpha: 1 });
      render();
      return;
    }
    gsap.from(canvas, { scale: 1.08, duration: 2.4, ease: 'power3.out' });
    gsap.from(hint, { autoAlpha: 0, y: 10, duration: 1, delay: 0.9, ease: 'power2.out' });
    buildScroll();
  }

  window.addEventListener('resize', () => {
    // bara de adresă a telefonului schimbă puțin înălțimea; redesenăm doar la schimbări reale
    if (Math.abs(stage.clientWidth - cssW) > 1 || Math.abs(stage.clientHeight - cssH) > 120) resize();
  });

  return { preload, start };
}
