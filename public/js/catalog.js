// Catalogul probei virtuale. Mostrele sunt schițe fine-line (ca desenele de tatuaj din reel);
// când avem poze cu lucrările salonului, le putem pune în locul lor.
// Id-urile trebuie să se potrivească cu cele din functions/api/tryon.js.

function rng(seed) {
  let s = seed;
  return () => (s = (s * 16807) % 2147483647) / 2147483647;
}

// Puncte pentru fade: mai dese sus, tot mai rare spre piele
function fadeDots(seed, n = 34, top = 45, bottom = 57) {
  const r = rng(seed);
  let d = '';
  for (const [x0, x1] of [[44.7, 47.4], [72.6, 75.3]]) {
    for (let i = 0; i < n; i++) {
      const y = top + Math.pow(r(), 1.8) * (bottom - top);
      const x = x0 + r() * (x1 - x0);
      d += `M${x.toFixed(1)} ${y.toFixed(1)}h.01`;
    }
  }
  return `<path d="${d}" stroke-width="1.15"/>`;
}

// Puncte uniforme pe tot scalpul (buzz cut)
function scalpDots(seed, n = 150) {
  const r = rng(seed);
  let d = '';
  let placed = 0;
  while (placed < n) {
    const x = 45 + r() * 30;
    const y = 33 + r() * 15;
    const dome = ((x - 60) / 15.2) ** 2 + ((y - 48) / 14.6) ** 2 < 1;
    const aboveHairline = y < 47.2 - 2.4 * (1 - ((x - 60) / 14) ** 2);
    if (dome && aboveHairline) {
      d += `M${x.toFixed(1)} ${y.toFixed(1)}h.01`;
      placed++;
    }
  }
  return `<path d="${d}" stroke-width="1.05"/>`;
}

// Bucle mici (trei sferturi de cerc) pentru curly top
function curls(seed) {
  const r = rng(seed);
  const rows = [
    [30.5, [54.5, 60, 65.5]],
    [34.6, [49.3, 54.8, 60.3, 65.8, 71]],
    [39, [46.8, 52.3, 57.8, 63.3, 68.8, 73.6]],
    [43.4, [47.6, 53.1, 58.6, 64.1, 69.6, 73.2]],
  ];
  let d = '';
  for (const [y, xs] of rows) {
    for (const x of xs) {
      const rad = 2.3 + r() * 0.6;
      const a = r() * Math.PI * 2;
      const b = a + Math.PI * 1.5;
      const sx = x + rad * Math.cos(a);
      const sy = y + rad * Math.sin(a);
      const ex = x + rad * Math.cos(b);
      const ey = y + rad * Math.sin(b);
      d += `M${sx.toFixed(1)} ${sy.toFixed(1)}A${rad.toFixed(1)} ${rad.toFixed(1)} 0 1 1 ${ex.toFixed(1)} ${ey.toFixed(1)}`;
    }
  }
  return `<path d="${d}"/>`;
}

const BUST = `
  <path d="M44.5 50C44.5 70 50.5 87 60 87S75.5 70 75.5 50"/>
  <path d="M44.6 58C40.6 56.8 39.8 66.5 44.9 68.6M75.4 58C79.4 56.8 80.2 66.5 75.1 68.6"/>
  <path d="M53.5 84.5 52.8 97M66.5 84.5 67.2 97"/>
  <path d="M52.8 97C41 99 28 103.5 21 119M67.2 97C79 99 92 103.5 99 119"/>
  <path d="M51.5 60.2C53.5 59 56 59 58 60M62 60C64 59 66.5 59 68.5 60.2M60.3 62.5C59.4 66.5 58.6 69.6 60.6 70.6M56.8 77.6C58.9 78.5 61.1 78.5 63.2 77.6" stroke-width=".85"/>`;

// Încadrare strânsă pe cap și umeri, ca schițele să umple cardul
const svg = (hair) => `<svg viewBox="12 17 96 96" aria-hidden="true">${hair}${BUST}</svg>`;

export const STYLES = [
  {
    id: 'skin-fade',
    name: 'Skin fade',
    svg: svg(`
      <path d="M44.5 50 45.2 45M75.5 50 74.8 45"/>
      <path d="M45.2 45C44 36 50 30 60 30S76 36 74.8 45"/>
      <path d="M47 46C52 44.4 68 44.4 73 46"/>
      <path d="M49 46c1-3 3-5 6-6M54 45.5c1-3.2 3-5 6.2-6M59.5 45.3c1-3.2 3-5 6.2-6M65 45.5c1-3 3-4.8 6-5.6" stroke-width=".9"/>
      ${fadeDots(11)}`),
  },
  {
    id: 'french-crop',
    name: 'French crop',
    svg: svg(`
      <path d="M44.5 50 45 47M75.5 50 75 47"/>
      <path d="M45 47C44.5 37 50.5 31.5 60 31.5S75.5 37 75 47"/>
      <path d="M45 47 46.8 48.6H73.2L75 47"/>
      <path d="M49 48.6l.6-6M52.5 48.6l.4-7M56 48.6l.2-7.5M59.5 48.6v-7.6M63 48.6l-.2-7.5M66.5 48.6l-.4-7M70 48.6l-.6-6" stroke-width=".9"/>
      ${fadeDots(23, 30, 48.5, 58)}`),
  },
  {
    id: 'buzz',
    name: 'Buzz cut',
    svg: svg(`
      <path d="M44.5 50C44 39 50.5 33 60 33S76 39 75.5 50"/>
      <path d="M46.2 47.6C51 45.6 69 45.6 73.8 47.6" stroke-width=".9"/>
      ${scalpDots(7)}`),
  },
  {
    id: 'quiff',
    name: 'Quiff texturat',
    svg: svg(`
      <path d="M44.5 50 45.2 46M75.5 50 74.8 46"/>
      <path d="M45.2 46C43.6 35 48.5 25.5 58.5 23.5C67 22 74.5 26.5 75.6 34C76.2 38.5 75.6 42.5 74.8 46"/>
      <path d="M47.2 46.3C52 44.6 68 44.6 72.8 46.3"/>
      <path d="M49.5 45.5C49.8 37 53.5 30 60.5 26.5M54.5 45C55.2 37.5 58.8 31.5 65.5 28.5M59.8 44.8C61 38.5 64.5 33.5 70.5 31.5M65 45C66.5 40.5 69.5 37 73.8 35.5" stroke-width=".9"/>
      ${fadeDots(31, 22, 46.5, 55)}`),
  },
  {
    id: 'pompadour',
    name: 'Pompadour',
    svg: svg(`
      <path d="M44.5 50 45.4 47M75.5 50 75 47"/>
      <path d="M45.4 47C42.5 32 49 20.5 61 19.5C72.5 18.8 79 26.5 77 37C76.3 41 75.6 44 75 47"/>
      <path d="M47.2 46.6C52 45 68 45 72.8 46.6"/>
      <path d="M48.6 46C47.6 34.5 52.5 25.5 61.5 23M52.8 45.5C52.6 35.5 57 28 66 25.8M57.2 45.2C58 37 62 31 70.5 29.6M62 45.2C63.5 38.5 67.5 34 74.5 33.4" stroke-width=".9"/>
      ${fadeDots(47, 22, 47, 55)}`),
  },
  {
    id: 'slick-back',
    name: 'Slick back',
    svg: svg(`
      <path d="M44.5 50 45 49M75.5 50 75 49"/>
      <path d="M45 49C44 38 50 31 60 30.6S76 38 75 49"/>
      <path d="M46.6 47.5C51.5 45.6 68.5 45.6 73.4 47.5"/>
      <path d="M50 46.5C50.5 40 53.5 35 58 32.5M54.5 46C55 40 57 35.5 60 32.2M60 45.8C60 40 60.4 35.5 61.6 32.2M65.5 46C65 40.5 63.8 36 62.6 32.5M70 46.5C69.2 40.5 66.5 35.5 63.6 33" stroke-width=".9"/>
      <path d="M45.6 52C45.8 48.5 47 45.6 49 43.6M74.4 52C74.2 48.5 73 45.6 71 43.6" stroke-width=".8"/>`),
  },
  {
    id: 'mullet',
    name: 'Mullet modern',
    svg: svg(`
      <path d="M44.5 50 45 47M75.5 50 75 47"/>
      <path d="M45 47C44.4 37 50.5 31 60 31S75.6 37 75 47"/>
      <path d="M46.6 47.6C51.5 46 68.5 46 73.4 47.6"/>
      <path d="M48.5 47c.8-3 2.6-5 5.5-6M54 46.5c.8-3.2 2.6-5 5.8-6M59.5 46.3c.8-3.2 2.6-5 5.8-6M65 46.5c.8-3 2.6-4.8 5.5-5.6" stroke-width=".9"/>
      <path d="M44.8 52C42.5 62 41.5 74 43.5 86C44.5 91 46.5 94 49 95.5M75.2 52C77.5 62 78.5 74 76.5 86C75.5 91 73.5 94 71 95.5"/>
      <path d="M43.6 60C42.2 70 42.5 80 45.1 88.5M76.4 60C77.8 70 77.5 80 74.9 88.5" stroke-width=".8"/>`),
  },
  {
    id: 'curly',
    name: 'Curly top',
    svg: svg(`
      <path d="M44.5 50 45.4 46.5M75.5 50 74.6 46.5"/>
      ${curls(5)}
      ${fadeDots(59, 26, 46.5, 56)}`),
  },
];

export const BEARDS = [
  { id: 'keep', name: 'Păstrează' },
  { id: 'none', name: 'Fără' },
  { id: 'stubble', name: 'Stubble' },
  { id: 'short', name: 'Scurtă' },
  { id: 'full', name: 'Completă' },
];

export const COLORS = [
  { id: 'natural', name: 'Naturală', css: 'conic-gradient(from 200deg, #2a1c13, #6b4a32, #b08a5a, #3b2a1d, #2a1c13)' },
  { id: 'black', name: 'Negru', css: '#16110e' },
  { id: 'brown', name: 'Șaten', css: '#5b3d28' },
  { id: 'blonde', name: 'Blond', css: '#c39b5e' },
  { id: 'platinum', name: 'Platinat', css: '#e4ded1' },
];

export const FADES = { low: 'low fade', mid: 'mid fade', high: 'high fade' };
