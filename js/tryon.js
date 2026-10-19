// „Vezi-o pe tine”: proba virtuală. Selfie-ul și alegerile merg la /api/tryon, unde un model AI
// de editare a imaginii schimbă doar tunsoarea (și barba). Dacă AI-ul nu e încă conectat
// (sau site-ul rulează local), secțiunea merge în mod demo, ca să se vadă fluxul.
import { site } from './config.js';
import { bookingLink } from './booking.js';
import { STYLES, BEARDS } from './catalog.js';

const { gsap } = window;
const SCAN_STEPS = ['Analizăm forma feței…', 'Măsurăm linia părului…', 'Aplicăm tunsoarea…', 'Finisăm detaliile…'];
const MAX_SIDE = 1024;
const TIMEOUT_MS = 150000;

const wait = (ms) => new Promise((r) => setTimeout(r, ms));

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
}

// Micșorăm poza în browser: e trimisă mai repede și fără date inutile.
// Întoarce poza ca imagine de afișat (url) și ca fișier JPEG de trimis (blob).
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
  const blob = await new Promise((resolve) => c.toBlob(resolve, 'image/jpeg', 0.9));
  if (!blob) throw new Error('Poza nu a putut fi pregătită.');
  return { url: c.toDataURL('image/jpeg', 0.9), blob };
}

// Rezultat simulat pentru modul demo: doar o corecție de culoare, ca să se vadă fluxul
async function demoResult(photo) {
  const img = await loadImage(photo);
  const c = document.createElement('canvas');
  c.width = img.naturalWidth;
  c.height = img.naturalHeight;
  const ctx = c.getContext('2d');
  ctx.filter = 'contrast(1.12) saturate(.8) sepia(.2) brightness(1.04)';
  ctx.drawImage(img, 0, 0);
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
    beard: $('[data-beard]'),
    consent: $('[data-consent]'),
    generate: $('[data-generate]'),
    status: $('[data-status]'),
    book: $('[data-book]'),
    bookStyle: $('[data-book-style]'),
    reset: $('[data-reset]'),
    scanText: $('[data-scan-text]'),
    demo: $('[data-demo-badge]'),
  };

  // photo = { url, blob } după ce clientul alege o poză
  const state = { photo: null, style: STYLES[0].id, custom: '', beard: 'keep', result: null, busy: false };

  const styleName = () => (state.style === 'custom' ? 'tunsoarea descrisă' : STYLES.find((s) => s.id === state.style).name);

  // Ce scrie în mesajul de programare, ex. „Skin fade, barbă scurtă”
  function describeChoice() {
    const parts = [state.style === 'custom' ? `tunsoarea descrisă: „${state.custom}”` : styleName()];
    if (state.beard !== 'keep') parts.push(`barbă: ${BEARDS.find((b) => b.id === state.beard).name.toLowerCase()}`);
    return parts.join(', ');
  }

  // ---------- Opțiuni ----------
  function radio(className, value, onPick) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = className;
    b.setAttribute('role', 'radio');
    b.dataset.value = value;
    b.addEventListener('click', onPick);
    return b;
  }

  const customCard = radio('style-card', 'custom', () => select('style', 'custom'));
  customCard.hidden = true;
  customCard.innerHTML = '<span class="style-card__text" data-custom-text></span>';
  customCard.setAttribute('aria-label', 'Tunsoarea descrisă de tine');
  el.styles.append(customCard);

  for (const s of STYLES) {
    const b = radio('style-card', s.id, () => {
      el.custom.value = '';
      state.custom = '';
      customCard.hidden = true;
      select('style', s.id);
    });
    b.setAttribute('aria-label', s.name);
    b.innerHTML = s.svg;
    el.styles.append(b);
  }

  for (const beard of BEARDS) {
    const b = radio('chip', beard.id, () => select('beard', beard.id));
    b.textContent = beard.name;
    el.beard.append(b);
  }

  function select(key, value) {
    if (state[key] === value) return;
    state[key] = value;
    sync();
    if (key === 'style') {
      gsap.fromTo(el.styleName, { y: 10, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.5, ease: 'power3.out' });
    }
  }

  function sync() {
    for (const [container, value] of [[el.styles, state.style], [el.beard, state.beard]]) {
      container.querySelectorAll('[role="radio"]').forEach((b) => b.setAttribute('aria-checked', String(b.dataset.value === value)));
    }
    const name = state.style === 'custom' ? 'Tunsoarea descrisă' : styleName();
    el.styleName.textContent = name;
    el.bookStyle.textContent = name;
    el.generate.disabled = !state.photo || !el.consent.checked || state.busy;
  }

  el.custom.addEventListener('input', () => {
    state.custom = el.custom.value.trim();
    customCard.hidden = !state.custom;
    customCard.querySelector('[data-custom-text]').textContent = state.custom;
    if (state.custom) select('style', 'custom');
    else if (state.style === 'custom') select('style', STYLES[0].id);
  });
  el.consent.addEventListener('change', sync);

  // ---------- Poza ----------
  function setStatus(text, isError = false) {
    el.status.textContent = text;
    el.status.classList.toggle('is-error', isError);
  }

  function setPos(v) {
    el.compare.style.setProperty('--pos', `${v}%`);
    el.range.value = v;
  }

  function showPhoto(on) {
    el.empty.hidden = on;
    el.compare.hidden = !on;
    el.reset.hidden = !on;
    el.compare.classList.remove('has-result');
    el.demo.hidden = true;
    el.book.classList.remove('is-ready');
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
    el.before.src = state.photo.url;
    el.after.removeAttribute('src');
    showPhoto(true);
    gsap.fromTo(el.before, { scale: 1.06, autoAlpha: 0 }, { scale: 1, autoAlpha: 1, duration: 0.9, ease: 'power3.out' });
    setStatus(el.consent.checked ? 'Poza e gata. Apasă „Generează previzualizarea”.' : 'Poza e gata. Bifează acordul de mai jos, apoi generează.');
    sync();
  }

  root.querySelectorAll('[data-file], [data-camera]').forEach((input) => input.addEventListener('change', onFile));

  el.reset.addEventListener('click', () => {
    state.photo = null;
    state.result = null;
    showPhoto(false);
    setStatus('');
    sync();
  });

  el.range.addEventListener('input', () => setPos(Number(el.range.value)));

  // ---------- Generarea ----------
  function cycleScanText() {
    let i = 0;
    el.scanText.textContent = SCAN_STEPS[0];
    const id = setInterval(() => {
      i = (i + 1) % SCAN_STEPS.length;
      el.scanText.textContent = SCAN_STEPS[i];
      gsap.fromTo(el.scanText, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5 });
    }, 2200);
    return () => clearInterval(id);
  }

  function showResult(src, demo) {
    state.result = src;
    el.after.src = src;
    el.demo.hidden = !demo;
    el.compare.classList.add('has-result');
    const o = { v: 100 };
    gsap.timeline()
      .to(o, { v: 0, duration: 1.2, ease: 'power3.inOut', onUpdate: () => setPos(o.v) })
      .to(o, { v: 50, duration: 1, ease: 'power3.out', onUpdate: () => setPos(o.v) }, '+=0.4');
    el.book.classList.add('is-ready');
    setStatus(demo
      ? 'Mod demo: imaginea e doar simulată. Rezultatul real apare după ce conectăm AI-ul.'
      : 'Gata! Trage de bară ca să compari înainte și după.');
  }

  async function generate() {
    if (!state.photo || !el.consent.checked || state.busy) return;
    state.busy = true;
    sync();
    el.frame.classList.add('is-scanning');
    el.demo.hidden = true;
    setStatus('Pregătim previzualizarea. Durează cam 30 de secunde.');
    const stopScan = cycleScanText();
    let image = null;
    let demo = false;
    let error = null;
    const form = new FormData();
    form.append('image', state.photo.blob, 'selfie.jpg');
    form.append('style', state.style);
    form.append('custom', state.style === 'custom' ? state.custom : '');
    form.append('beard', state.beard);
    const abort = new AbortController();
    const timer = setTimeout(() => abort.abort(), TIMEOUT_MS);
    try {
      const res = await fetch(site.tryOnEndpoint, { method: 'POST', body: form, signal: abort.signal });
      const data = await res.json().catch(() => ({}));
      const b64 = data.data && data.data[0] && data.data[0].b64_json;
      if (res.ok && b64) image = `data:image/jpeg;base64,${b64}`;
      else if (data.demo || [404, 405, 501].includes(res.status)) demo = true;
      else error = data.error || 'Generarea nu a mers. Mai încearcă o dată.';
    } catch (err) {
      if (err.name === 'AbortError') error = 'A durat prea mult. Mai încearcă o dată.';
      else demo = true; // fără server (ex. previzualizare locală)
    } finally {
      clearTimeout(timer);
    }
    if (demo) {
      await wait(2400);
      image = await demoResult(state.photo.url);
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
