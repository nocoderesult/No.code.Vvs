// Contact sheet of every SVG in a folder (grey tiles), for eyeballing logos.
// usage: node svgsheet.js <dir> <out.png>
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const [dir, out] = process.argv.slice(2);
  const files = fs.readdirSync(dir).filter((f) => f.endsWith('.svg'));
  const cells = files.map((f) => {
    const b64 = fs.readFileSync(path.join(dir, f)).toString('base64');
    return `<div style="display:inline-block;margin:10px;text-align:center;font:14px sans-serif">
      <div style="width:180px;height:180px;background:#bbb;display:flex;align-items:center;justify-content:center">
      <img src="data:image/svg+xml;base64,${b64}" style="max-width:160px;max-height:160px"></div>${f}</div>`;
  }).join('');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1000, height: 700 } });
  await page.setContent(`<body style="background:#fff">${cells}</body>`);
  await page.screenshot({ path: out, fullPage: true });
  await browser.close();
})();
