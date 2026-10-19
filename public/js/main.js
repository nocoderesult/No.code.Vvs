import { site } from './config.js';
import { bookingLink, whatsappLink } from './booking.js';
import { initIntro } from './intro.js';
import { initTryOn } from './tryon.js';

const { gsap, ScrollTrigger, SplitText, Lenis } = window;
gsap.registerPlugin(ScrollTrigger, SplitText);
ScrollTrigger.config({ ignoreMobileResize: true });
gsap.defaults({ ease: 'power3.out' });

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const touch = window.matchMedia('(hover: none), (pointer: coarse)').matches;
const html = document.documentElement;

// ---------- Scroll fluid pe calculator (pe telefon rămâne scroll-ul nativ) ----------
let lenis = null;
if (!reduceMotion && !touch) {
  lenis = new Lenis({ lerp: 0.085, smoothWheel: true });
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add((time) => lenis.raf(time * 1000));
  gsap.ticker.lagSmoothing(0);
  lenis.stop();
}

function scrollToTarget(selector) {
  const target = document.querySelector(selector);
  if (!target) return;
  if (lenis) lenis.scrollTo(target, { duration: 1.4, easing: (t) => 1 - Math.pow(1 - t, 4) });
  else target.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth' });
}

// ---------- Preloader ----------
async function runLoader(intro) {
  const loader = document.querySelector('[data-loader]');
  const mark = loader.querySelector('[data-loader-mark]');
  const label = loader.querySelector('[data-loader-label]');
  const bar = loader.querySelector('[data-loader-bar]');
  const shown = { v: 0 };
  const draw = () => { bar.style.transform = `scaleX(${shown.v})`; };
  const progress = (p) => gsap.to(shown, { v: p, duration: 0.5, ease: 'power2.out', overwrite: true, onUpdate: draw });

  if (!reduceMotion) {
    gsap.from(mark, { yPercent: 30, autoAlpha: 0, duration: 1.4, ease: 'power3.out' });
    gsap.from(label, { autoAlpha: 0, y: 8, duration: 1.2, delay: 0.3 });
  }
  await Promise.all([intro.preload(progress), new Promise((r) => setTimeout(r, reduceMotion ? 0 : 1400))]);
  await gsap.to(shown, { v: 1, duration: 0.4, overwrite: true, onUpdate: draw });

  gsap.timeline()
    .to([mark, label, bar.parentElement], { autoAlpha: 0, y: -12, duration: 0.6, ease: 'power2.in', stagger: 0.05 })
    .to(loader, { autoAlpha: 0, duration: reduceMotion ? 0.01 : 0.9, ease: 'power2.inOut' }, '-=0.15')
    .add(() => {
      document.body.classList.remove('is-loading');
      lenis && lenis.start();
      intro.start();
      ScrollTrigger.refresh();
    }, '-=0.6')
    .set(loader, { display: 'none' });
}

// ---------- Header, meniu, butonul plutitor ----------
function initChrome() {
  const header = document.querySelector('[data-header]');
  const dock = document.querySelector('[data-dock]');
  ScrollTrigger.create({
    trigger: '.curtain',
    start: 'top 12%',
    onToggle: (self) => header.classList.toggle('is-solid', self.isActive),
    end: 'max',
  });

  // Butonul plutitor apare după intro și se retrage în proba virtuală și la Programări
  gsap.set(dock, { yPercent: 160, autoAlpha: 1 });
  let inRange = false;
  let inTryOn = false;
  let visible = false;
  const update = () => {
    const on = inRange && !inTryOn;
    if (on === visible) return;
    visible = on;
    gsap.to(dock, { yPercent: on ? 0 : 160, duration: 0.6, ease: on ? 'power3.out' : 'power2.in', overwrite: true });
  };
  ScrollTrigger.create({
    trigger: '.curtain',
    start: 'top 35%',
    endTrigger: '#programare',
    end: 'top 80%',
    onToggle: (self) => { inRange = self.isActive; update(); },
  });
  ScrollTrigger.create({
    trigger: '#proba',
    start: 'top 60%',
    end: 'bottom 40%',
    onToggle: (self) => { inTryOn = self.isActive; update(); },
  });
}

function initMenu() {
  const btn = document.querySelector('[data-menu-toggle]');
  const menu = document.querySelector('[data-menu]');
  const items = menu.querySelectorAll('.menu__nav a, .menu__cta');
  let open = false;
  const tl = gsap.timeline({ paused: true })
    .to(menu, { autoAlpha: 1, duration: 0.45, ease: 'power2.out' })
    .from(items, { y: 24, autoAlpha: 0, duration: 0.6, stagger: 0.05 }, 0.1);

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
      tl.timeScale(1.6).reverse();
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
  const external = (a, href) => { a.href = href; a.target = '_blank'; a.rel = 'noopener'; };
  document.querySelectorAll('[data-book-online]').forEach((a) => {
    external(a, bookingLink());
    a.addEventListener('click', () => { if (html.classList.contains('menu-open')) toggleMenu(false); });
  });
  document.querySelectorAll('[data-whatsapp]').forEach((a) => external(a, whatsappLink()));
  document.querySelectorAll('[data-instagram]').forEach((a) => external(a, site.instagram));
  document.querySelectorAll('[data-maps]').forEach((a) => external(a, `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(site.address)}`));
  document.querySelectorAll('[data-address]').forEach((el) => (el.textContent = site.address));
  document.querySelectorAll('[data-phone]').forEach((a) => {
    a.href = `tel:${site.phoneLink}`;
    a.textContent = site.phone;
  });
  document.querySelectorAll('[data-year]').forEach((s) => (s.textContent = new Date().getFullYear()));
}

// ---------- Dezvăluiri la scroll (doar transform și opacitate, ca să curgă lin) ----------
function initReveals() {
  if (reduceMotion) return;
  document.querySelectorAll('[data-reveal="lines"]').forEach((el) => {
    SplitText.create(el, {
      type: 'lines',
      mask: 'lines',
      autoSplit: true,
      onSplit: (self) => gsap.from(self.lines, {
        yPercent: 100,
        duration: 1.1,
        stagger: 0.08,
        scrollTrigger: { trigger: el, start: 'top 88%', once: true },
      }),
    });
  });

  document.querySelectorAll('[data-reveal="fade"]').forEach((el) => {
    gsap.from(el, { y: 24, autoAlpha: 0, duration: 1, scrollTrigger: { trigger: el, start: 'top 92%', once: true } });
  });

  document.querySelectorAll('[data-reveal="photo"]').forEach((el) => {
    const img = el.querySelector('img');
    gsap.timeline({ scrollTrigger: { trigger: el, start: 'top 88%', once: true } })
      .from(el, { autoAlpha: 0, y: 40, duration: 1.2 })
      .from(img, { scale: 1.18, duration: 1.8, ease: 'power2.out' }, 0);
    gsap.fromTo(img, { yPercent: -4 }, {
      yPercent: 4,
      ease: 'none',
      scrollTrigger: { trigger: el, start: 'top bottom', end: 'bottom top', scrub: true },
    });
  });
}

// ---------- Servicii: rândurile apar pe rând; atingerea deschide programarea ----------
function initServices() {
  const rows = [...document.querySelectorAll('[data-service]')];
  const open = (row) => window.open(bookingLink(row.dataset.service), '_blank', 'noopener');
  rows.forEach((row) => {
    row.addEventListener('click', () => open(row));
    row.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        open(row);
      }
    });
  });
  if (reduceMotion) return;
  rows.forEach((row) => {
    gsap.timeline({ scrollTrigger: { trigger: row, start: 'top 94%', once: true } })
      .from(row, { '--line-scale': 0, duration: 1.2, ease: 'power2.inOut' })
      .from(row.children, { y: 18, autoAlpha: 0, duration: 0.9, stagger: 0.08 }, 0.1);
  });
}

// ---------- Galerie: bara de progres urmărește glisarea ----------
function initGallery() {
  const track = document.querySelector('[data-gallery]');
  const bar = document.querySelector('[data-gallery-bar]');
  const update = () => {
    const max = track.scrollWidth - track.clientWidth;
    const p = max > 0 ? track.scrollLeft / max : 0;
    const visible = track.clientWidth / track.scrollWidth;
    bar.style.transform = `scaleX(${visible + (1 - visible) * p})`;
  };
  track.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update);
  update();
}

// ---------- Footer: monograma urcă literă cu literă ----------
function initFooter() {
  if (reduceMotion) return;
  const mark = document.querySelector('[data-footer-mark]');
  const split = SplitText.create(mark, { type: 'chars', charsClass: 'char' });
  gsap.from(split.chars, {
    yPercent: 60,
    autoAlpha: 0,
    duration: 1.4,
    stagger: 0.12,
    scrollTrigger: { trigger: mark, start: 'top 95%', once: true },
  });
}

// ---------- Pornire ----------
const intro = initIntro({ reduceMotion });
const toggleMenu = initMenu();
initLinks(toggleMenu);
initChrome();
initReveals();
initServices();
initTryOn();
initGallery();
initFooter();
runLoader(intro);
window.addEventListener('load', () => ScrollTrigger.refresh());
