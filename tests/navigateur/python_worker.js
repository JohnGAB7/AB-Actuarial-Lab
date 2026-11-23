const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
// Browser test of the Python Web Worker. Run: node tests/navigateur/python_worker.js (site served on :8765).
// PYODIDE_LOCAL=<dir> serves Pyodide from a local npm package instead of the CDN (offline machines).
const PKG = process.env.PYODIDE_LOCAL ? process.env.PYODIDE_LOCAL.replace(/\/?$/, '/') : null;
const BASE = process.env.SITE_URL || 'http://localhost:8765/';
const types = { '.js': 'text/javascript', '.wasm': 'application/wasm', '.json': 'application/json', '.zip': 'application/zip' };
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1000, height: 900 } });
  if (PKG) await ctx.route('https://cdn.jsdelivr.net/pyodide/v0.27.7/full/**', (r) => {
    const f = PKG + path.basename(new URL(r.request().url()).pathname);
    if (!fs.existsSync(f)) return r.fulfill({ status: 404, body: '' });
    r.fulfill({ body: fs.readFileSync(f), contentType: types[path.extname(f)] || 'application/octet-stream', headers: { 'Access-Control-Allow-Origin': '*' } });
  });
  const p = await ctx.newPage();
  const out = {};
  const errs = []; p.on('pageerror', (e) => errs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
  const setCode = async (code) => p.evaluate((c) => { document.querySelector('.CodeMirror').CodeMirror.setValue(c); }, code);
  await p.goto(BASE + 'a1/s01/index.html#etape-6'); await p.waitForTimeout(800);
  const clickRun = () => p.locator('.row .btn').first().click();
  const summary = () => p.locator('.res-sum').textContent();
  // 1. skeleton: todo
  await clickRun(); await p.waitForFunction(() => !document.querySelector('.row .btn').disabled, null, { timeout: 60000 });
  out.skeleton = await summary(); console.log('skeleton:', out.skeleton, await p.$$eval('.results li', (l) => l.map((x) => x.className).join(',')));
  // 2. correct solution
  await setCode(fs.readFileSync(path.join(__dirname, '..', 'a1', 'reference.py'), 'utf8'));
  await clickRun(); await p.waitForFunction(() => !document.querySelector('.row .btn').disabled, null, { timeout: 30000 });
  out.solution = await summary(); console.log('solution:', out.solution);
  // 3. infinite loop: timeout
  await setCode('while True:\n    pass\n');
  const t0 = Date.now(); await clickRun();
  await p.waitForFunction(() => !document.querySelector('.row .btn').disabled, null, { timeout: 30000 });
  out.loop = await summary(); console.log('loop:', out.loop, Math.round((Date.now() - t0) / 1000) + 's');
  // 4. page stays responsive during a loop, Stop button works
  await clickRun(); await p.waitForTimeout(1500);
  const responsive = await p.evaluate(() => 1 + 1);
  await p.locator('.row .btn', { hasText: 'Arrêter' }).click(); await p.waitForTimeout(300);
  out.responsive = responsive; out.stop = await summary(); console.log('stop:', responsive, out.stop);
  // 5. no access to localStorage or the DOM from Python
  await setCode("import js\nleaks = [n for n in ('localStorage', 'document') if hasattr(js, n)]\nraise RuntimeError('LEAKS=' + ','.join(leaks))\n");
  await clickRun(); await p.waitForFunction(() => !document.querySelector('.row .btn').disabled, null, { timeout: 60000 });
  out.sandbox = await p.locator('.results li .tm').first().textContent(); console.log('sandbox:', out.sandbox);
  // Network and browser storage APIs are unavailable after Pyodide initialization.
  await setCode("import js\nblocked = ['fetch', 'XMLHttpRequest', 'WebSocket', 'EventSource', 'BroadcastChannel', 'indexedDB', 'caches', 'importScripts', 'postMessage']\\navailable = [name for name in blocked if hasattr(js, name) and getattr(js, name) is not None]\\nraise RuntimeError('AVAILABLE=' + ','.join(available))\\n");
  await clickRun(); await p.waitForFunction(() => !document.querySelector('.row .btn').disabled, null, { timeout: 30000 });
  out.capabilities = await p.locator('.results li .tm').first().textContent(); console.log('capabilities:', out.capabilities);
  // Oversized code is rejected before Pyodide is loaded.
  await setCode('x'.repeat(50001));
  await clickRun(); await p.waitForFunction(() => !document.querySelector('.row .btn').disabled, null, { timeout: 5000 });
  out.inputLimit = await summary(); console.log('input limit:', out.inputLimit);
  console.log('errors', errs);
  const fails = [];
  if (!/^0 test/.test(out.skeleton)) fails.push('skeleton');
  if (!/6 tests passent/.test(out.solution)) fails.push('solution');
  if (!/Arrêt après 10 secondes/.test(out.loop)) fails.push('loop timeout');
  if (out.responsive !== 2 || !/arrêtée/.test(out.stop)) fails.push('stop');
  if (out.sandbox !== 'RuntimeError: LEAKS=') fails.push('sandbox: ' + out.sandbox);
  if (out.capabilities !== 'RuntimeError: AVAILABLE=') fails.push('runtime capabilities: ' + out.capabilities);
  if (!/Code trop long/.test(out.inputLimit)) fails.push('input limit');
  if (errs.length) fails.push('page errors');
  if (fails.length) { console.error('FAILED:', fails.join('; ')); process.exitCode = 1; } else console.log('OK');
  await b.close();
})();
