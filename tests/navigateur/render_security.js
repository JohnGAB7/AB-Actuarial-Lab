const { chromium } = require('playwright');

const BASE = process.env.SITE_URL || 'http://localhost:8765/';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));

  await page.route('**/a1/s01/index.html', async (route) => {
    const response = await route.fetch();
    let body = await response.text();
    body = body.replace(
      'À un taux annuel',
      "<img src=x onerror='window.__xss=1'>À un taux annuel",
    );
    body = body.replace(
      'Quatre questions avant le cours.',
      "<svg onload='window.__xss=2'></svg>Quatre questions avant le cours.",
    );
    body = body.replace(
      "Le taux d'escompte $d$ est",
      "<img src=x onerror='window.__xss=3'>Le taux d'escompte $d$ est",
    );
    body = body.replace(
      'https://www.soa.org/education/exam-req/edu-exam-fm-detail/',
      'javascript:window.__xss=4',
    );
    await route.fulfill({ response, body });
  });

  await page.goto(BASE + 'a1/s01/index.html#etape-1');
  await page.waitForSelector('#stage h3');

  const introAndQuestion = await page.evaluate(() => ({
    intro: document.querySelector('#stage .step-head .lead')?.textContent || '',
    question: document.querySelector('#stage h3')?.textContent || '',
    activeElements: document.querySelectorAll('#stage img, #stage svg, #stage script').length,
    xss: window.__xss,
  }));

  await page.locator('#stage .opt').first().click();
  await page.waitForFunction(() => {
    const why = document.querySelector('#stage .why');
    return why && !why.hidden && why.textContent.includes("Le taux d'escompte");
  });
  const explanation = await page.evaluate(() => ({
    text: document.querySelector('#stage .why')?.textContent || '',
    activeElements: document.querySelectorAll('#stage .why img, #stage .why svg, #stage .why script').length,
    xss: window.__xss,
  }));

  await page.evaluate(() => { location.hash = '#etape-3'; });
  await page.waitForSelector('#stage .sources li');
  const sources = await page.evaluate(() => ({
    javascriptLinks: document.querySelectorAll('#stage a[href^="javascript:"]').length,
    links: document.querySelectorAll('#stage .sources a').length,
    plainSourceLabels: document.querySelectorAll('#stage .sources .src-t').length,
    bold: document.querySelectorAll('#stage .flow b').length,
    italic: document.querySelectorAll('#stage .flow i').length,
    xss: window.__xss,
  }));

  const englishPage = await browser.newPage();
  englishPage.on('pageerror', (error) => errors.push(error.message));
  await englishPage.route('**/en/a1/s01/index.html', async (route) => {
    const response = await route.fetch();
    let body = await response.text();
    body = body.replace(
      'The rate of discount $d$ is',
      "<img src=x onerror='window.__xss=5'>The rate of discount $d$ is",
    );
    await route.fulfill({ response, body });
  });
  await englishPage.goto(BASE + 'en/a1/s01/index.html#etape-1');
  await englishPage.waitForSelector('#stage h3');
  await englishPage.locator('#stage .opt').first().click();
  await englishPage.waitForFunction(() => {
    const why = document.querySelector('#stage .why');
    return why && !why.hidden && why.textContent.includes('The rate of discount');
  });
  const english = await englishPage.evaluate(() => ({
    lang: document.documentElement.lang,
    text: document.querySelector('#stage .why')?.textContent || '',
    activeElements: document.querySelectorAll('#stage .why img, #stage .why svg, #stage .why script').length,
    xss: window.__xss,
  }));

  const failures = [];
  if (!introAndQuestion.intro.includes('Quatre questions')) failures.push('intro text lost');
  if (!introAndQuestion.question.includes('À un taux annuel')) failures.push('question text lost');
  if (introAndQuestion.activeElements !== 0) failures.push('active elements inserted from intro/question');
  if (introAndQuestion.xss !== undefined) failures.push('intro/question payload executed');
  if (!explanation.text.includes("Le taux d'escompte")) failures.push('explanation text lost');
  if (explanation.activeElements !== 0) failures.push('active elements inserted from explanation');
  if (explanation.xss !== undefined) failures.push('explanation payload executed');
  if (sources.javascriptLinks !== 0 || sources.links !== 0) failures.push('unsafe source URL became a link');
  if (sources.plainSourceLabels !== 2) failures.push('unsafe source labels not retained as plain text');
  if (sources.bold === 0 || sources.italic === 0) failures.push('allowed bold/italic formatting was lost');
  if (sources.xss !== undefined) failures.push('source URL payload executed');
  if (english.lang !== 'en') failures.push('English page did not retain its language');
  if (!english.text.includes('The rate of discount')) failures.push('English explanation text lost');
  if (english.activeElements !== 0) failures.push('active elements inserted from English content');
  if (english.xss !== undefined) failures.push('English content payload executed');
  if (errors.length) failures.push('page errors: ' + errors.join('; '));

  console.log(JSON.stringify({ introAndQuestion, explanation, sources, english, errors }, null, 2));
  await browser.close();
  if (failures.length) {
    console.error('FAILED:', failures.join('; '));
    process.exitCode = 1;
  } else {
    console.log('OK: rich content is allowlisted and unsafe URLs are inert.');
  }
})();
