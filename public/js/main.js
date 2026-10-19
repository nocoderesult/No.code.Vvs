import { site } from './config.js';
import { bookingLink, whatsappLink } from './booking.js';
import { initIntro } from './intro.js';
import { initTryOn } from './tryon.js';

const { gsap, ScrollTrigger, SplitText, Lenis } = window;
gsap.registerPlugin(ScrollTrigger, SplitText);
ScrollTrigger.config({ ignoreMobileResize: true });

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
const html = document.documentElement;

// ---------- Scroll fluid ----------
let lenis = null;
if (!reduceMotion) {
  lenis = new Lenis({ lerp: 0.09, smoothWheel: true });
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add((time) => lenis.raf(time * 1000));
  gsap.ticker.lagSmoothing(0);
  lenis.stop();
}

function scrollToTarget(selector) {
  const target = document.querySelector(selector);
  if (!target) return;
  if (lenis) lenis.scrollTo(target, { duration: 1.6, easing: (t) => 1 - Math.pow(1 - t, 4) });
  else target.scrollIntoView();
}

// ---------- Preloader ----------
async function runLoader(intro) {
  const loader = document.querySelector('[data-loader]');
  const brand = loader.querySelector('[data-loader-brand]');
  const bar = loader.querySelector('[data-loader-bar]');
  const count = loader.querySelector('[data-loader-count]');
  const shown = { v: 0 };
  const draw = () => {
    count.textContent = String(Math.round(shown.v)).padStart(3, '0');
    bar.style.transform = `scaleX(${shown.v / 100})`;
  };
  const progress = (p) => gsap.to(shown, { v: p * 100, duration: 0.6, ease: 'power2.out', overwrite: true, onUpdate: draw });

  await document.fonts.ready;
  const split = SplitText.create(brand, { type: 'words,chars', mask: 'chars' });
  if (!reduceMotion) gsap.from(split.chars, { yPercent: 110, duration: 1.2, ease: 'expo.out', stagger: 0.035 });

  await Promise.all([intro.preload(progress), new Promise((r) => setTimeout(r, reduceMotion ? 0 : 1600))]);
  await gsap.to(shown, { v: 100, duration: 0.5, ease: 'power2.out', overwrite: true, onUpdate: draw });

  const out = gsap.timeline();
  if (!reduceMotion) out.to(split.chars, { yPercent: -110, duration: 0.6, ease: 'power3.in', stagger: 0.02 });
  out.to(loader, { clipPath: 'inset(0% 0% 100% 0%)', duration: reduceMotion ? 0.01 : 1.2, ease: 'expo.inOut' }, '-=0.15')
    .add(() => {
      document.body.classList.remove('is-loading');
      lenis && lenis.start();
      intro.start();
      ScrollTrigger.refresh();
    }, reduceMotion ? 0 : '-=0.75')
    .set(loader, { display: 'none' });
}

// ---------- Header, meniu, progres ----------
function initHeader() {
  const header = document.querySelector('[data-header]');
  const intro = document.querySelector('[data-intro]');
  ScrollTrigger.create({
    start: 0,
    end: 'max',
    onUpdate(self) {
      const y = self.scroll();
      header.classList.toggle('is-solid', y > intro.offsetHeight - window.innerHeight * 1.2);
      header.classList.toggle('is-hidden', self.direction === 1 && y > 160 && !html.classList.contains('menu-open'));
    },
  });
  gsap.to('[data-scroll-progress]', { scaleX: 1, ease: 'none', scrollTrigger: { start: 0, end: 'max', scrub: 0.3 } });
}

function initMenu() {
  const btn = document.querySelector('[data-menu-toggle]');
  const menu = document.querySelector('[data-menu]');
  const links = menu.querySelectorAll('.menu__nav a');
  let open = false;
  const tl = gsap.timeline({ paused: true })
    .set(menu, { visibility: 'visible' })
    .to(menu, { clipPath: 'circle(150% at calc(100% - 44px) 44px)', duration: 0.9, ease: 'expo.inOut' })
    .from(links, { yPercent: 100, autoAlpha: 0, stagger: 0.06, duration: 0.7, ease: 'expo.out' }, '-=0.45');

  function toggle(force) {
    open = typeof force === 'boolean' ? force : !open;
    html.classList.toggle('menu-open', open);
    btn.setAttribute('aria-expanded', String(open));
    btn.setAttribute('aria-label', open ? 'Închide meniul' : 'Deschide meniul');
    menu.setAttribute('aria-hidden', String(!open));
    if (open) {
      tl.timeScale(1).play();
      lenis && lenis.stop();
    } else {
      tl.timeScale(1.8).reverse();
      lenis && lenis.start();
    }
  }
  btn.addEventListener('click', () => toggle());
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && open) toggle(false); });
  return toggle;
}

function initLinks(toggleMenu) {
  document.querySelectorAll('[data-scroll-to]').forEach((a) => {
    a.addEventListener('click', (e) => {
      const href = a.getAttribute('href');
      if (!href || !href.startsWith('#')) return;
      e.preventDefault();
      if (html.classList.contains('menu-open')) toggleMenu(false);
      scrollToTarget(href);
    });
  });

  document.querySelectorAll('[data-book-online]').forEach((a) => {
    a.href = bookingLink();
    a.target = '_blank';
    a.rel = 'noopener';
  });
  document.querySelectorAll('[data-whatsapp]').forEach((a) => {
    a.href = whatsappLink();
    a.target = '_blank';
    a.rel = 'noopener';
  });
  document.querySelectorAll('[data-phone]').forEach((a) => {
    a.href = `tel:${site.phone.replace(/\s/g, '')}`;
    a.textContent = site.phone;
  });
  document.querySelectorAll('[data-instagram]').forEach((a) => (a.href = site.instagram));
  document.querySelectorAll('[data-year]').forEach((s) => (s.textContent = new Date().getFullYear()));
}

// ---------- Cursor și butoane magnetice ----------
function initCursor() {
  if (!finePointer || reduceMotion) return;
  html.classList.add('has-cursor');
  const el = document.querySelector('[data-cursor-el]');
  const ring = el.querySelector('.cursor__ring');
  const dot = el.querySelector('.cursor__dot');
  const label = el.querySelector('[data-cursor-label]');
  const rx = gsap.quickTo(ring, 'x', { duration: 0.55, ease: 'power3' });
  const ry = gsap.quickTo(ring, 'y', { duration: 0.55, ease: 'power3' });
  const dx = gsap.quickTo(dot, 'x', { duration: 0.12, ease: 'power3' });
  const dy = gsap.quickTo(dot, 'y', { duration: 0.12, ease: 'power3' });

  window.addEventListener('pointermove', (e) => {
    rx(e.clientX); ry(e.clientY); dx(e.clientX); dy(e.clientY);
  }, { passive: true });
  document.addEventListener('pointerover', (e) => {
    const t = e.target.closest('[data-cursor], a, button, label, input[type="range"]');
    const text = t ? t.dataset.cursor || '' : '';
    el.classList.toggle('is-label', !!text);
    el.classList.toggle('is-link', !!t && !text);
    label.textContent = text;
  });
  document.documentElement.addEventListener('pointerleave', () => gsap.to(el, { autoAlpha: 0, duration: 0.3 }));
  document.documentElement.addEventListener('pointerenter', () => gsap.to(el, { autoAlpha: 1, duration: 0.3 }));
}

function initMagnetic() {
  if (!finePointer || reduceMotion) return;
  document.querySelectorAll('[data-magnetic]').forEach((btn) => {
    const xTo = gsap.quickTo(btn, 'x', { duration: 0.7, ease: 'power3' });
    const yTo = gsap.quickTo(btn, 'y', { duration: 0.7, ease: 'power3' });
    btn.addEventListener('pointermove', (e) => {
      const r = btn.getBoundingClientRect();
      xTo((e.clientX - r.left - r.width / 2) * 0.3);
      yTo((e.clientY - r.top - r.height / 2) * 0.4);
    });
    btn.addEventListener('pointerleave', () => { xTo(0); yTo(0); });
  });
}

// ---------- Dezvăluiri la scroll ----------
function initReveals() {
  if (reduceMotion) return;
  document.querySelectorAll('[data-reveal="lines"]').forEach((el) => {
    SplitText.create(el, {
      type: 'lines',
      mask: 'lines',
      autoSplit: true,
      onSplit: (self) => gsap.from(self.lines, {
        yPercent: 105,
        duration: 1.3,
        ease: 'expo.out',
        stagger: 0.09,
        scrollTrigger: { trigger: el, start: 'top 86%', once: true },
      }),
    });
  });

  document.querySelectorAll('[data-reveal="fade"]').forEach((el) => {
    gsap.from(el, {
      y: 40,
      autoAlpha: 0,
      duration: 1.2,
      ease: 'power3.out',
      scrollTrigger: { trigger: el, start: 'top 90%', once: true },
    });
  });

  document.querySelectorAll('[data-reveal="clip"]').forEach((el) => {
    gsap.timeline({ scrollTrigger: { trigger: el, start: 'top 85%', once: true } })
      .fromTo(el,
        { clipPath: 'inset(100% 0% 0% 0% round 18px)' },
        { clipPath: 'inset(0% 0% 0% 0% round 18px)', duration: 1.6, ease: 'expo.inOut' })
      .from(el.firstElementChild, { scale: 1.35, duration: 2, ease: 'expo.out' }, 0.1);
  });

  document.querySelectorAll('[data-parallax]').forEach((el) => {
    gsap.fromTo(el.firstElementChild, { yPercent: -7 }, {
      yPercent: 7,
      ease: 'none',
      scrollTrigger: { trigger: el, start: 'top bottom', end: 'bottom top', scrub: true },
    });
  });
}

// Manifestul se „aprinde” cuvânt cu cuvânt pe măsură ce derulezi
function initManifesto() {
  const el = document.querySelector('[data-manifesto]');
  if (!el || reduceMotion) return;
  const split = SplitText.create(el, { type: 'words', wordsClass: 'word' });
  gsap.fromTo(split.words, { opacity: 0.14 }, {
    opacity: 1,
    ease: 'none',
    stagger: 0.1,
    scrollTrigger: { trigger: el, start: 'top 78%', end: 'bottom 40%', scrub: true },
  });
}

function initCounters() {
  document.querySelectorAll('[data-count]').forEach((el) => {
    const end = parseFloat(el.dataset.count);
    const decimals = Number(el.dataset.decimals || 0);
    const suffix = el.dataset.suffix || '';
    const fmt = (v) => (decimals ? v.toFixed(decimals).replace('.', ',') : Math.round(v).toLocaleString('ro-RO')) + suffix;
    if (reduceMotion) {
      el.textContent = fmt(end);
      return;
    }
    const o = { v: 0 };
    gsap.to(o, {
      v: end,
      duration: 2.4,
      ease: 'power3.out',
      scrollTrigger: { trigger: el, start: 'top 92%', once: true },
      onUpdate: () => (el.textContent = fmt(o.v)),
    });
  });
}

// ---------- Servicii: linii care se desenează + poza care urmărește cursorul ----------
function initServices() {
  const rows = [...document.querySelectorAll('[data-service]')];
  rows.forEach((row) => row.addEventListener('click', () => {
    window.open(bookingLink(row.querySelector('.service__name').textContent), '_blank', 'noopener');
  }));
  if (reduceMotion) return;

  rows.forEach((row) => {
    gsap.timeline({ scrollTrigger: { trigger: row, start: 'top 92%', once: true } })
      .from(row, { '--line-scale': 0, duration: 1.4, ease: 'expo.inOut' })
      .from(row.querySelectorAll('.service__num, .service__body, .service__time, .service__price'),
        { y: 30, autoAlpha: 0, duration: 1, ease: 'power3.out', stagger: 0.06 }, 0.2);
  });

  if (!finePointer) return;
  const preview = document.querySelector('[data-hover-preview]');
  const img = preview.querySelector('[data-hover-preview-img]');
  gsap.set(preview, { xPercent: -50, yPercent: -50, scale: 0.6 });
  const xTo = gsap.quickTo(preview, 'x', { duration: 0.8, ease: 'power3' });
  const yTo = gsap.quickTo(preview, 'y', { duration: 0.8, ease: 'power3' });
  const list = document.querySelector('.service-list');
  list.addEventListener('pointermove', (e) => { xTo(e.clientX); yTo(e.clientY); });
  rows.forEach((row, i) => row.addEventListener('pointerenter', () => {
    const src = row.dataset.preview;
    img.className = `hover-preview__img ${src ? '' : `ph ${i % 2 ? 'ph--warm' : ''}`}`;
    img.style.backgroundImage = src ? `url("${src}")` : '';
    img.style.backgroundSize = 'cover';
    img.dataset.ph = row.dataset.previewLabel || '';
    gsap.to(preview, { autoAlpha: 1, scale: 1, rotation: gsap.utils.random(-6, 6), duration: 0.6, ease: 'power3.out' });
    gsap.fromTo(img, { scale: 1.35 }, { scale: 1, duration: 0.9, ease: 'expo.out' });
  }));
  list.addEventListener('pointerleave', () => gsap.to(preview, { autoAlpha: 0, scale: 0.6, duration: 0.45, ease: 'power3.in' }));
}

// ---------- Bandă infinită care accelerează cu scroll-ul ----------
function initMarquee() {
  if (reduceMotion) return;
  document.querySelectorAll('[data-marquee]').forEach((row) => {
    const track = row.querySelector('.marquee__track');
    const original = track.innerHTML;
    while (track.scrollWidth < window.innerWidth * 1.3) track.innerHTML += original;
    track.innerHTML += track.innerHTML;
    let half = track.scrollWidth / 2;
    let x = 0;
    const dir = Number(row.dataset.marquee) || 1;
    const setX = gsap.quickSetter(track, 'x', 'px');
    const setSkew = gsap.quickSetter(track, 'skewX', 'deg');
    window.addEventListener('resize', () => (half = track.scrollWidth / 2));
    gsap.ticker.add((time, delta) => {
      const v = lenis ? lenis.velocity : 0;
      const speed = (0.55 + Math.min(Math.abs(v) * 0.12, 7)) * (delta / 16.67);
      x = gsap.utils.wrap(-half, 0, x - speed * dir);
      setX(x);
      setSkew(gsap.utils.clamp(-9, 9, -v * 0.22));
    });
  });
}

// ---------- Galerie orizontală (desktop) ----------
function initGallery() {
  const mm = gsap.matchMedia();
  mm.add('(min-width: 901px) and (prefers-reduced-motion: no-preference)', () => {
    const pin = document.querySelector('[data-gallery-pin]');
    const track = document.querySelector('[data-gallery-track]');
    const dist = () => Math.max(0, track.scrollWidth - window.innerWidth);
    const tween = gsap.to(track, {
      x: () => -dist(),
      ease: 'none',
      scrollTrigger: {
        trigger: pin,
        start: 'top top',
        end: () => `+=${dist()}`,
        pin: true,
        scrub: 0.8,
        invalidateOnRefresh: true,
        anticipatePin: 1,
      },
    });
    track.querySelectorAll('.shot').forEach((shot) => {
      gsap.fromTo(shot.querySelector('.shot__img > *'), { xPercent: -9 }, {
        xPercent: 9,
        ease: 'none',
        scrollTrigger: { trigger: shot, containerAnimation: tween, start: 'left right', end: 'right left', scrub: true },
      });
      gsap.from(shot, {
        yPercent: 14,
        rotation: 3,
        ease: 'none',
        scrollTrigger: { trigger: shot, containerAnimation: tween, start: 'left right', end: 'left 55%', scrub: true },
      });
    });
  });
}

// ---------- Echipa: carduri care se înclină după mouse ----------
function initTilt() {
  if (!finePointer || reduceMotion) return;
  document.querySelectorAll('[data-tilt]').forEach((card) => {
    const rx = gsap.quickTo(card, 'rotationX', { duration: 0.9, ease: 'power3' });
    const ry = gsap.quickTo(card, 'rotationY', { duration: 0.9, ease: 'power3' });
    card.addEventListener('pointermove', (e) => {
      const r = card.getBoundingClientRect();
      ry(((e.clientX - r.left) / r.width - 0.5) * 12);
      rx(-((e.clientY - r.top) / r.height - 0.5) * 12);
    });
    card.addEventListener('pointerleave', () => { rx(0); ry(0); });
  });
}

// ---------- Recenzii care se schimbă singure ----------
function initReviews() {
  const stage = document.querySelector('[data-reviews]');
  const dotsEl = document.querySelector('[data-review-dots]');
  const items = [...stage.querySelectorAll('.review')];
  const splits = items.map((it) => SplitText.create(it.querySelector('p'), { type: 'lines', mask: 'lines', autoSplit: true }));
  let index = 0;
  let timer = null;

  function show(i, instant = false) {
    const prev = items[index];
    const next = items[i];
    index = i;
    dots.forEach((d, k) => d.setAttribute('aria-current', String(k === i)));
    if (instant || reduceMotion) {
      items.forEach((it) => gsap.set(it, { autoAlpha: it === next ? 1 : 0 }));
      return;
    }
    if (prev !== next) gsap.to(prev, { autoAlpha: 0, duration: 0.5, ease: 'power2.out' });
    gsap.set(next, { autoAlpha: 1 });
    gsap.fromTo(splits[i].lines, { yPercent: 105 }, { yPercent: 0, duration: 1.2, ease: 'expo.out', stagger: 0.08, delay: 0.25 });
    gsap.fromTo(next.querySelector('cite'), { autoAlpha: 0, y: 12 }, { autoAlpha: 1, y: 0, duration: 0.8, delay: 0.6 });
  }

  const restart = () => {
    clearInterval(timer);
    if (!reduceMotion) timer = setInterval(() => show((index + 1) % items.length), 6500);
  };
  const dots = items.map((_, i) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.setAttribute('aria-label', `Recenzia ${i + 1}`);
    b.addEventListener('click', () => { show(i); restart(); });
    dotsEl.append(b);
    return b;
  });
  show(0, true);
  restart();
}

// ---------- Footer: numele uriaș urcă literă cu literă ----------
function initFooter() {
  if (reduceMotion) return;
  const big = document.querySelector('[data-footer-big]');
  const split = SplitText.create(big, { type: 'chars', charsClass: 'char' });
  gsap.from(split.chars, {
    yPercent: 100,
    autoAlpha: 0,
    duration: 1.5,
    ease: 'expo.out',
    stagger: 0.07,
    scrollTrigger: { trigger: big, start: 'top 98%', once: true },
  });
}

// ---------- Pornire ----------
const intro = initIntro({ reduceMotion });
const toggleMenu = initMenu();
initLinks(toggleMenu);
initHeader();
initCursor();
initMagnetic();
initReveals();
initManifesto();
initCounters();
initServices();
initMarquee();
initTryOn();
initGallery();
initTilt();
initReviews();
initFooter();
runLoader(intro);
window.addEventListener('load', () => ScrollTrigger.refresh());
