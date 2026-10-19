// Intrarea cinematică: cadrele video-ului salonului sunt desenate pe un canvas
// și derulate de scroll, ca pe site-urile Apple. Cadrele se generează cu
// scripts/make-sequence.sh în public/assets/seq/ (împreună cu manifest.json).
// Fără manifest rulează o animație provizorie: un culoar de uși spre o lumină caldă.

const { gsap, ScrollTrigger } = window;

// Ferestrele (din progresul total 0–1) în care apare fiecare cuvânt după nume
const WORD_WINDOWS = [[0.3, 0.5], [0.56, 0.76]];
const PARALLEL_LOADS = 6;

export function initIntro({ reduceMotion }) {
  const section = document.querySelector('[data-intro]');
  const stage = section.querySelector('[data-intro-stage]');
  const canvas = section.querySelector('[data-intro-canvas]');
  const ctx = canvas.getContext('2d');
  const words = [...section.querySelectorAll('[data-word]')];
  const final = section.querySelector('[data-intro-final]');
  const hint = section.querySelector('[data-intro-hint]');
  const bar = section.querySelector('[data-intro-progress]');
  const dim = section.querySelector('[data-intro-dim]');

  const state = { p: 0 };
  let seq = null; // { count, frames }
  let dpr = 1;
  let lastWidth = 0;
  let lastHeight = 0;

  function resize() {
    const w = stage.clientWidth;
    const h = stage.clientHeight;
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    lastWidth = w;
    lastHeight = h;
    render();
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

  function drawCover(img) {
    const cw = canvas.width;
    const ch = canvas.height;
    const ir = img.naturalWidth / img.naturalHeight;
    let w = cw;
    let h = ch;
    if (ir > cw / ch) w = ch * ir;
    else h = cw / ir;
    ctx.drawImage(img, (cw - w) / 2, (ch - h) / 2, w, h);
  }

  function drawPlaceholder(p) {
    const w = canvas.width;
    const h = canvas.height;
    const cx = w / 2;
    const cy = h * 0.5;
    ctx.fillStyle = '#070605';
    ctx.fillRect(0, 0, w, h);

    const glow = ctx.createRadialGradient(cx, cy, 0, cx, cy, Math.max(w, h) * (0.3 + p * 0.55));
    glow.addColorStop(0, `rgba(231, 211, 174, ${0.24 + p * 0.34})`);
    glow.addColorStop(0.4, 'rgba(200, 163, 107, 0.09)');
    glow.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, w, h);

    ctx.lineWidth = dpr;
    ctx.strokeStyle = 'rgba(236, 228, 214, 0.05)';
    for (let k = -5; k <= 5; k++) {
      ctx.beginPath();
      ctx.moveTo(cx + k * w * 0.16, h);
      ctx.lineTo(cx, cy);
      ctx.stroke();
    }

    const travel = p * 7.2;
    const baseW = Math.min(w, h * 1.1) * 0.5;
    const baseH = h * 0.84;
    for (let i = 10; i >= 1; i--) {
      const z = i - travel;
      if (z <= 0.12) continue;
      const s = 1 / z;
      const a = Math.max(0, Math.min(1, 1.5 - z / 4)) * Math.min(1, z * 1.6);
      ctx.strokeStyle = `rgba(236, 228, 214, ${0.6 * a})`;
      ctx.lineWidth = Math.max(dpr, 3 * s * dpr);
      ctx.strokeRect(cx - (baseW * s) / 2, cy - (baseH * s) / 2, baseW * s, baseH * s);
    }
  }

  function render() {
    if (!canvas.width) return;
    if (seq) {
      const img = nearestLoaded(Math.round(state.p * (seq.count - 1)));
      if (img) drawCover(img);
    } else {
      drawPlaceholder(state.p);
    }
  }

  async function loadManifest() {
    try {
      const res = await fetch('assets/seq/manifest.json', { cache: 'no-cache' });
      return res.ok ? await res.json() : null;
    } catch {
      return null;
    }
  }

  // Ordine grosier → fin: întâi fiecare al 16-lea cadru, ca scroll-ul să meargă devreme
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

  // Rezolvă când s-au încărcat destule cadre pentru un scroll fluid; restul vin în fundal.
  async function preload(onProgress) {
    resize();
    const manifest = await loadManifest();
    const portrait = window.innerHeight > window.innerWidth;
    const variant = manifest && ((portrait && manifest.mobile) || manifest.desktop || manifest.mobile);
    if (!variant) {
      onProgress(1);
      return;
    }
    seq = { count: variant.count, frames: new Array(variant.count) };
    const order = loadOrder(variant.count);
    const gate = Math.min(order.length, Math.max(1, Math.ceil(order.length * 0.3)));
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
          if (i === 0 || done <= gate) render();
          pump();
        };
        img.src = url(i);
      };
      for (let k = 0; k < PARALLEL_LOADS; k++) pump();
    });
  }

  function buildScroll() {
    const tl = gsap.timeline({ defaults: { ease: 'none' } });
    tl.to(state, { p: 1, duration: 1, onUpdate: render }, 0);
    tl.to(bar, { scaleX: 1, duration: 1 }, 0);
    tl.to(hint, { autoAlpha: 0, duration: 0.03 }, 0.01);
    tl.to(words[0], { autoAlpha: 0, y: -24, filter: 'blur(10px)', duration: 0.08 }, 0.12);
    words.slice(1).forEach((el, k) => {
      const [a, b] = WORD_WINDOWS[k] || [0.3 + k * 0.2, 0.45 + k * 0.2];
      tl.fromTo(el,
        { autoAlpha: 0, y: 26, filter: 'blur(12px)', letterSpacing: '0.7em' },
        { autoAlpha: 1, y: 0, filter: 'blur(0px)', letterSpacing: '0.42em', duration: 0.08 }, a);
      tl.to(el, { autoAlpha: 0, y: -26, filter: 'blur(12px)', duration: 0.08 }, b - 0.08);
    });
    tl.fromTo(final, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.04 }, 0.84);
    tl.from(final.querySelectorAll('.intro__kicker, .intro__title > *, .btn'),
      { yPercent: 70, autoAlpha: 0, stagger: 0.015, duration: 0.1 }, 0.84);

    ScrollTrigger.create({
      trigger: section,
      start: 'top top',
      // video-ul se termină înainte ca secțiunea următoare să urce peste el
      end: () => '+=' + Math.max(1, section.offsetHeight - 2 * stage.offsetHeight),
      scrub: 0.6,
      animation: tl,
      invalidateOnRefresh: true,
    });

    // Cortina: secțiunea următoare urcă, iar scena se micșorează și se întunecă
    gsap.timeline({
      scrollTrigger: { trigger: '.curtain', start: 'top bottom', end: 'top top', scrub: true },
    })
      .to(stage, { scale: 0.9, ease: 'none' }, 0)
      .to(dim, { opacity: 0.75, ease: 'none' }, 0);
  }

  function start() {
    if (reduceMotion) {
      gsap.set([words[0], final], { autoAlpha: 1 });
      return;
    }
    gsap.fromTo(words[0],
      { autoAlpha: 0, y: 24, filter: 'blur(14px)', letterSpacing: '0.62em' },
      { autoAlpha: 1, y: 0, filter: 'blur(0px)', letterSpacing: '0.34em', duration: 1.8, ease: 'expo.out', delay: 0.15 });
    gsap.from(canvas, { scale: 1.14, duration: 2.4, ease: 'expo.out' });
    gsap.from(hint, { autoAlpha: 0, y: 14, duration: 1, delay: 1 });
    buildScroll();
  }

  window.addEventListener('resize', () => {
    // pe telefon bara de adresă declanșează resize-uri mici de înălțime; le ignorăm
    if (Math.abs(stage.clientWidth - lastWidth) > 2 || Math.abs(stage.clientHeight - lastHeight) > 120) resize();
  });

  return { preload, start };
}
