// „Vezi-o pe tine”: proba virtuală. Selfie-ul și tunsoarea aleasă merg la /api/tryon,
// unde un model AI de editare a imaginii schimbă doar părul. Dacă AI-ul nu e încă
// conectat (sau site-ul rulează local), secțiunea merge în mod demo.
import { site } from './config.js';
import { bookingLink } from './booking.js';
import { STYLES, BEARDS, COLORS, FADES } from './catalog.js';

const { gsap } = window;
const SCAN_STEPS = ['Analizăm forma feței…', 'Măsurăm linia părului…', 'Aplicăm tunsoarea…', 'Finisăm detaliile…'];
const MAX_SIDE = 1024;

const wait = (ms) => new Promise((r) => setTimeout(r, ms));

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
}

// Micșorează poza în browser (mai rapid, mai ieftin, fără date inutile trimise)
async function downscale(file) {
  let src;
  try {
    src = await createImageBitmap(file, { imageOrientation: 'from-image' });
  } catch {
    src = await loadImage(URL.createObjectURL(file));
  }
  const w = src.width || src.naturalWidth;
  const h = src.height || src.naturalHeight;
  const k = Math.min(1, MAX_SIDE / Math.max(w, h));
  const c = document.createElement('canvas');
  c.width = Math.round(w * k);
  c.height = Math.round(h * k);
  c.getContext('2d').drawImage(src, 0, 0, c.width, c.height);
  return c.toDataURL('image/jpeg', 0.9);
}

// Rezultat simulat pentru modul demo: doar o corecție de culoare, ca să se vadă fluxul
async function demoResult(photo) {
  const img = await loadImage(photo);
  const c = document.createElement('canvas');
  c.width = img.naturalWidth;
  c.height = img.naturalHeight;
  const ctx = c.getContext('2d');
  ctx.filter = 'contrast(1.12) saturate(.82) sepia(.22) brightness(1.04)';
  ctx.drawImage(img, 0, 0);
  ctx.filter = 'none';
  const g = ctx.createRadialGradient(c.width / 2, c.height / 2, c.width * 0.25, c.width / 2, c.height / 2, c.width * 0.8);
  g.addColorStop(0, 'rgba(0,0,0,0)');
  g.addColorStop(1, 'rgba(0,0,0,.45)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, c.width, c.height);
  return c.toDataURL('image/jpeg', 0.9);
}

export function initTryOn() {
  const root = document.querySelector('[data-tryon]');
  if (!root) return;
  const $ = (s) => root.querySelector(s);
  const el = {
    frame: $('[data-frame]'),
    empty: $('[data-empty]'),
    compare: $('[data-compare]'),
    before: $('[data-before]'),
    after: $('[data-after]'),
    range: $('[data-compare-range]'),
    styles: $('[data-styles]'),
    styleName: $('[data-style-name]'),
    custom: $('[data-custom]'),
    length: $('[data-length]'),
    fade: $('[data-fade]'),
    beard: $('[data-beard]'),
    color: $('[data-color]'),
    consent: $('[data-consent]'),
    generate: $('[data-generate]'),
    status: $('[data-status]'),
    book: $('[data-book]'),
    bookStyle: $('[data-book-style]'),
    placed: $('[data-placed]'),
    reset: $('[data-reset]'),
    scanText: $('[data-scan-text]'),
    demo: $('[data-demo-badge]'),
    tabs: [...root.querySelectorAll('[data-view]')],
  };

  const state = {
    photo: null,
    style: STYLES[0].id,
    custom: '',
    length: 40,
    fade: 'mid',
    beard: 'keep',
    color: 'natural',
    result: null,
    busy: false,
  };

  const styleName = () => (state.style === 'custom' ? 'Look-ul tău' : STYLES.find((s) => s.id === state.style).name);

  // Ce scrie în mesajul de programare, ex. „Skin fade (mid fade), barbă scurtă”
  function describeChoice() {
    const parts = [state.style === 'custom' ? `tunsoarea descrisă: „${state.custom}”` : styleName()];
    if (state.style !== 'buzz' && state.style !== 'custom') parts[0] += ` (${FADES[state.fade]})`;
    if (state.beard !== 'keep') parts.push(`barbă: ${BEARDS.find((b) => b.id === state.beard).name.toLowerCase()}`);
    if (state.color !== 'natural') parts.push(`culoare: ${COLORS.find((c) => c.id === state.color).name.toLowerCase()}`);
    return parts.join(', ');
  }

  // ---------- Construim opțiunile ----------
  const customCard = document.createElement('button');
  customCard.type = 'button';
  customCard.className = 'style-card';
  customCard.setAttribute('role', 'radio');
  customCard.dataset.value = 'custom';
  customCard.hidden = true;
  customCard.innerHTML = '<span class="style-card__text" data-custom-text></span>';
  customCard.addEventListener('click', () => select('style', 'custom'));
  el.styles.append(customCard);

  for (const s of STYLES) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'style-card';
    b.setAttribute('role', 'radio');
    b.setAttribute('aria-label', s.name);
    b.dataset.value = s.id;
    b.innerHTML = s.svg;
    b.addEventListener('click', () => {
      el.custom.value = '';
      state.custom = '';
      select('style', s.id);
    });
    el.styles.append(b);
  }

  for (const beard of BEARDS) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'chip';
    b.setAttribute('role', 'radio');
    b.dataset.value = beard.id;
    b.textContent = beard.name;
    b.addEventListener('click', () => select('beard', beard.id));
    el.beard.append(b);
  }

  for (const color of COLORS) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'swatch';
    b.setAttribute('role', 'radio');
    b.setAttribute('aria-label', color.name);
    b.dataset.value = color.id;
    b.style.background = color.css;
    b.addEventListener('click', () => select('color', color.id));
    el.color.append(b);
  }
  const colorName = document.createElement('span');
  colorName.className = 'swatches__name';
  el.color.append(colorName);

  el.fade.querySelectorAll('button').forEach((b) => b.addEventListener('click', () => select('fade', b.dataset.value)));

  function select(key, value) {
    state[key] = value;
    sync();
    if (key === 'style') {
      gsap.fromTo(el.styleName, { yPercent: 40, autoAlpha: 0 }, { yPercent: 0, autoAlpha: 1, duration: 0.6, ease: 'expo.out' });
    }
  }

  function markChecked(container, value) {
    container.querySelectorAll('[role="radio"]').forEach((b) => b.setAttribute('aria-checked', String(b.dataset.value === value)));
  }

  function sync() {
    markChecked(el.styles, state.style);
    markChecked(el.fade, state.fade);
    markChecked(el.beard, state.beard);
    markChecked(el.color, state.color);
    colorName.textContent = COLORS.find((c) => c.id === state.color).name;
    el.styleName.textContent = styleName();
    el.bookStyle.textContent = styleName();
    el.length.style.setProperty('--fill', `${state.length}%`);
    el.generate.disabled = !state.photo || !el.consent.checked || state.busy;
    if (!state.result) el.placed.textContent = state.photo ? `Ales · ${styleName()}` : 'Alege o tunsoare';
  }

  el.custom.addEventListener('input', () => {
    state.custom = el.custom.value.trim();
    customCard.hidden = !state.custom;
    customCard.querySelector('[data-custom-text]').textContent = state.custom;
    if (state.custom) select('style', 'custom');
    else if (state.style === 'custom') select('style', STYLES[0].id);
  });
  el.length.addEventListener('input', () => {
    state.length = Number(el.length.value);
    sync();
  });
  el.consent.addEventListener('change', sync);

  // ---------- Poza ----------
  function setStatus(text, isError = false) {
    el.status.textContent = text;
    el.status.classList.toggle('is-error', isError);
  }

  function setView(view) {
    el.compare.dataset.view = view;
    el.tabs.forEach((t) => t.setAttribute('aria-selected', String(t.dataset.view === view)));
  }

  function setPos(v) {
    el.compare.style.setProperty('--pos', `${v}%`);
    el.range.value = v;
  }

  function enableTabs(on) {
    el.tabs.forEach((t) => { if (t.dataset.view !== 'before') t.disabled = !on; });
  }

  async function onFile(e) {
    const file = e.target.files && e.target.files[0];
    e.target.value = '';
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      setStatus('Alege o imagine (JPG sau PNG).', true);
      return;
    }
    try {
      state.photo = await downscale(file);
    } catch {
      setStatus('Nu am putut citi poza. Încearcă altă imagine.', true);
      return;
    }
    state.result = null;
    el.before.src = state.photo;
    el.after.removeAttribute('src');
    el.empty.hidden = true;
    el.compare.hidden = false;
    el.reset.hidden = false;
    el.demo.hidden = true;
    el.book.classList.remove('is-ready');
    enableTabs(false);
    setView('before');
    gsap.fromTo(el.before, { scale: 1.08, autoAlpha: 0 }, { scale: 1, autoAlpha: 1, duration: 1.1, ease: 'expo.out' });
    setStatus(el.consent.checked ? 'Poza e gata. Apasă „Generează look-ul”.' : 'Poza e gata. Bifează acordul și apasă „Generează look-ul”.');
    sync();
  }

  root.querySelectorAll('[data-file], [data-camera]').forEach((input) => input.addEventListener('change', onFile));

  el.reset.addEventListener('click', () => {
    state.photo = null;
    state.result = null;
    el.compare.hidden = true;
    el.empty.hidden = false;
    el.reset.hidden = true;
    el.demo.hidden = true;
    el.book.classList.remove('is-ready');
    enableTabs(false);
    setView('before');
    setStatus('');
    sync();
  });

  el.tabs.forEach((t) => t.addEventListener('click', () => {
    if (t.disabled) return;
    setView(t.dataset.view);
    if (t.dataset.view === 'compare') setPos(50);
  }));
  el.range.addEventListener('input', () => setPos(Number(el.range.value)));

  // ---------- Generarea ----------
  function cycleScanText() {
    let i = 0;
    el.scanText.textContent = SCAN_STEPS[0];
    const id = setInterval(() => {
      i = (i + 1) % SCAN_STEPS.length;
      gsap.fromTo(el.scanText, { autoAlpha: 0, y: 6 }, { autoAlpha: 1, y: 0, duration: 0.5 });
      el.scanText.textContent = SCAN_STEPS[i];
    }, 2200);
    return () => clearInterval(id);
  }

  function showResult(src, demo) {
    state.result = src;
    el.after.src = src;
    el.demo.hidden = !demo;
    enableTabs(true);
    setView('compare');
    const o = { v: 100 };
    gsap.timeline()
      .to(o, { v: 0, duration: 1.3, ease: 'expo.inOut', onUpdate: () => setPos(o.v) })
      .to(o, { v: 50, duration: 1.1, ease: 'expo.out', onUpdate: () => setPos(o.v) }, '+=0.5');
    el.placed.textContent = `Aplicat · ${styleName()}`;
    el.book.classList.add('is-ready');
    gsap.fromTo(el.book, { scale: 0.96 }, { scale: 1, duration: 0.9, ease: 'elastic.out(1, 0.5)' });
    setStatus(demo
      ? 'Mod demo: imaginea e doar simulată. Rezultatul real apare după ce conectăm AI-ul.'
      : 'Gata! Trage de bară ca să compari. Îți place? Programează-te.');
  }

  async function generate() {
    if (!state.photo || !el.consent.checked || state.busy) return;
    state.busy = true;
    sync();
    el.frame.classList.add('is-scanning');
    el.demo.hidden = true;
    setStatus('Îți schițăm noul look. Durează cam 15 secunde.');
    const stopScan = cycleScanText();
    let image = null;
    let demo = false;
    let error = null;
    try {
      const res = await fetch(site.tryOnEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image: state.photo,
          style: state.style,
          custom: state.style === 'custom' ? state.custom : '',
          length: state.length,
          fade: state.fade,
          beard: state.beard,
          color: state.color,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok && data.image) image = data.image;
      else if (data.demo || [404, 405, 501].includes(res.status)) demo = true;
      else error = data.error || 'Generarea nu a mers. Mai încearcă o dată.';
    } catch {
      demo = true; // fără server (ex. previzualizare locală)
    }
    if (demo) {
      await wait(2600);
      image = await demoResult(state.photo);
    }
    stopScan();
    el.frame.classList.remove('is-scanning');
    state.busy = false;
    if (error) setStatus(error, true);
    else showResult(image, demo);
    sync();
  }

  el.generate.addEventListener('click', generate);

  el.book.addEventListener('click', (e) => {
    e.preventDefault();
    window.open(bookingLink(describeChoice()), '_blank', 'noopener');
  });

  sync();
}
