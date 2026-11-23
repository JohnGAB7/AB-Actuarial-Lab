// Responsive and bilingual smoke test for the learner-first homepage.
const { chromium } = require("playwright");
const BASE = process.env.SITE_URL || "http://localhost:8765/";

(async () => {
  let browser;
  const failures = [];
  try {
    browser = await chromium.launch();
    const page = await browser.newPage({ viewport: { width: 390, height: 844 }, locale: "fr-FR" });
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));

    await page.goto(new URL("index.html", BASE).toString(), { waitUntil: "domcontentloaded" });
    await page.locator(".hero-visual").waitFor();
    const shortLabels = await page.locator(".dom-t").allInnerTexts();
    if (!shortLabels.length || shortLabels.some((label) => label.trim().length > 18)) failures.push("homepage domain labels should stay concise");
    await page.waitForFunction(() => Array.from(document.querySelectorAll(".brand-logo")).some((img) => img.complete && img.naturalWidth > 0), null, { timeout: 15000 });
    const brand = await page.evaluate(() => ({
      title: document.title,
      label: document.querySelector(".brand-copy")?.textContent || "",
      logoLoaded: Array.from(document.querySelectorAll(".brand-logo")).some((img) => img.complete && img.naturalWidth > 0)
    }));
    console.log("brand FR:", brand);
    if (!brand.title.startsWith("Laboratoire d’apprentissage actuariel par ACTU-BASICS")) failures.push("French site title");
    if (!brand.label.includes("LABORATOIRE ACTUARIEL") || !brand.label.includes("PAR ACTU-BASICS")) failures.push("French sub-brand lockup");
    if (!brand.logoLoaded) failures.push("custom Actuarial Learning Lab mark did not load");
    const mobile = await page.evaluate(() => ({
      lang: document.documentElement.lang,
      width: window.innerWidth,
      scrollWidth: document.documentElement.scrollWidth,
      domains: document.querySelectorAll(".doms .dom").length,
      sessions: JSON.parse(document.getElementById("plan").textContent).length,
      stat: document.querySelector(".home-stat strong").textContent,
      resume: Boolean(document.querySelector("[data-reprendre]"))
    }));
    console.log("mobile FR:", mobile);
    if (mobile.lang !== "fr") failures.push("French homepage language");
    if (mobile.scrollWidth > mobile.width + 1) failures.push("mobile horizontal overflow");
    if (mobile.domains !== 7) failures.push("domain cards");
    if (Number(mobile.stat) !== mobile.sessions) failures.push("session count is not data-driven");
    if (!mobile.resume) failures.push("resume action missing");

    // Verify local progress changes the primary action without requiring an account.
    await page.evaluate(() => {
      const plan = JSON.parse(document.getElementById("plan").textContent);
      localStorage.setItem("parcours:" + plan[0].s + ":etapes", JSON.stringify({ "0": true }));
    });
    await page.reload({ waitUntil: "domcontentloaded" });
    const resumeText = await page.locator("[data-reprendre]").textContent();
    console.log("resume after local progress:", resumeText);
    if (!/Reprendre/.test(resumeText)) failures.push("local resume state");

    // Language switching must preserve the responsive homepage structure.
    await page.locator('a[data-langue="en"]').click();
    await page.waitForFunction(() => document.documentElement.lang === "en");
    const englishMobile = await page.evaluate(() => ({
      lang: document.documentElement.lang,
      scrollWidth: document.documentElement.scrollWidth,
      width: window.innerWidth,
      title: document.querySelector(".home-intro h2").textContent,
      siteTitle: document.title,
      brand: document.querySelector(".brand-copy")?.textContent || ""
    }));
    console.log("mobile EN:", englishMobile);
    const shortLabelsEN = await page.locator(".dom-t").allInnerTexts();
    if (!shortLabelsEN.length || shortLabelsEN.some((label) => label.trim().length > 18)) failures.push("English homepage domain labels should stay concise");
    if (englishMobile.lang !== "en") failures.push("English homepage language");
    if (englishMobile.scrollWidth > englishMobile.width + 1) failures.push("English mobile horizontal overflow");
    if (!/Understand the idea/.test(englishMobile.title)) failures.push("English editorial content");
    if (!englishMobile.siteTitle.startsWith("Actuarial Learning Lab by ACTU-BASICS")) failures.push("English site title");
    if (!englishMobile.brand.includes("ACTUARIAL LEARNING LAB") || !englishMobile.brand.includes("BY ACTU-BASICS")) failures.push("English sub-brand lockup");

    await page.setViewportSize({ width: 1440, height: 900 });
    const desktop = await page.evaluate(() => ({
      width: window.innerWidth,
      scrollWidth: document.documentElement.scrollWidth,
      heroColumns: getComputedStyle(document.querySelector(".hero-in")).gridTemplateColumns,
      offenders: Array.from(document.querySelectorAll("body *")).map((el) => {
        const r = el.getBoundingClientRect();
        return { tag: el.tagName, className: typeof el.className === "string" ? el.className : "", text: (el.textContent || "").trim().slice(0, 35), left: Math.round(r.left), right: Math.round(r.right), width: Math.round(r.width), display: getComputedStyle(el).display };
      }).filter((x) => x.display !== "none" && (x.right > window.innerWidth + 1 || x.left < -1)).sort((a, b) => b.right - a.right).slice(0, 12)
    }));
    console.log("desktop EN:", desktop);
    if (desktop.scrollWidth > desktop.width + 1) failures.push("desktop horizontal overflow");
    // The shared quiz renderer must separate each option letter from its text in both locales.
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(new URL("a1/s01/index.html", BASE).toString(), { waitUntil: "domcontentloaded" });
    await page.locator(".opt").first().waitFor();
    const frenchOptions = await page.locator(".opt").allInnerTexts();
    console.log("quiz options FR:", frenchOptions);
    if (!frenchOptions.length || !frenchOptions.every((value) => /^[A-Z]\s+(?!-)/.test(value.trim()))) failures.push("French quiz options should use letter enumeration without a dash");
    if (await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1)) failures.push("session mobile horizontal overflow");

    await page.goto(new URL("en/a1/s01/index.html", BASE).toString(), { waitUntil: "domcontentloaded" });
    await page.locator(".opt").first().waitFor();
    const englishOptions = await page.locator(".opt").allInnerTexts();
    console.log("quiz options EN:", englishOptions);
    if (!englishOptions.length || !englishOptions.every((value) => /^[A-Z]\s+(?!-)/.test(value.trim()))) failures.push("English quiz options should use letter enumeration without a dash");


    // Wide lesson workspace: the progress rail stays visible and the canvas uses the available desktop width.
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(new URL("a1/s01/index.html", BASE).toString(), { waitUntil: "domcontentloaded" });
    await page.locator(".lesson-shell").waitFor();
    const lessonDesktop = await page.evaluate(() => ({
      columns: getComputedStyle(document.querySelector(".lesson-shell")).gridTemplateColumns,
      rail: document.querySelector(".lesson-rail")?.getBoundingClientRect().width || 0,
      canvas: document.querySelector(".stage")?.getBoundingClientRect().width || 0,
      labels: document.querySelectorAll(".rail-step-name").length,
      overflow: document.documentElement.scrollWidth > window.innerWidth
    }));
    console.log("lesson desktop:", lessonDesktop);
    if (lessonDesktop.rail < 180 || lessonDesktop.canvas < 800) failures.push("desktop lesson workspace does not use available width");
    if (!lessonDesktop.labels) failures.push("desktop lesson step labels missing");
    if (lessonDesktop.overflow) failures.push("desktop lesson horizontal overflow");

    await page.setViewportSize({ width: 390, height: 844 });
    const lessonMobile = await page.evaluate(() => ({
      overflow: document.documentElement.scrollWidth > window.innerWidth,
      rail: getComputedStyle(document.querySelector(".lesson-rail")).position,
      namesHidden: Array.from(document.querySelectorAll(".rail-step-name")).every((el) => getComputedStyle(el).display === "none")
    }));
    console.log("lesson mobile:", lessonMobile);
    if (lessonMobile.overflow) failures.push("lesson mobile horizontal overflow");

    // A formula is presented as a deliberate dark mathematical studio board, not a generic white card.
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(new URL("a1/s01/index.html#etape-3", BASE).toString(), { waitUntil: "domcontentloaded" });
    await page.locator(".formula").first().waitFor();
    const board = await page.locator(".formula").first().evaluate((el) => ({
      background: getComputedStyle(el).backgroundImage,
      color: getComputedStyle(el).color,
      accent: getComputedStyle(el, "::before").backgroundImage
    }));
    console.log("mathematical board:", board);
    if (!board.background.includes("radial-gradient") || !board.background.includes("linear-gradient")) failures.push("formula should use the mathematical studio board treatment");
    if (board.color !== "rgb(237, 244, 251)") failures.push("formula foreground contrast color missing");
    if (!board.accent.includes("linear-gradient")) failures.push("formula accent line missing");


    // Mobile header, dropdown placement and account-page width at common phone sizes.
    for (const width of [320, 360, 375, 390, 414, 430, 768, 1024]) {
      await page.setViewportSize({ width, height: 844 });
      await page.goto(new URL("compte/index.html", BASE).toString(), { waitUntil: "domcontentloaded" });
      await page.locator(".nav-in").waitFor();
      const header = await page.evaluate(() => {
        const box = (selector) => {
          const el = document.querySelector(selector);
          if (!el) return null;
          const r = el.getBoundingClientRect();
          return { left: r.left, right: r.right, width: r.width };
        };
        return {
          width: window.innerWidth,
          scrollWidth: document.documentElement.scrollWidth,
          header: box(".nav-in"),
          brand: box(".brand"),
          menu: box(".nav-menu"),
          language: box(".langs"),
          account: box(".nav .acct"),
          content: box(".compte")
        };
      });
      console.log("account header viewport:", header);
      if (header.scrollWidth > width + 1) failures.push("account page horizontal overflow at " + width + "px");
      for (const key of ["header", "brand", "menu", "language", "account", "content"]) {
        const item = header[key];
        if (item && (item.left < -1 || item.right > width + 1)) failures.push(key + " escapes viewport at " + width + "px");
      }
      await page.locator(".nav-menu summary").click();
      const dropdown = await page.locator(".nav-sheet").evaluate((el) => {
        const r = el.getBoundingClientRect();
        return { left: r.left, right: r.right, top: r.top, bottom: r.bottom, width: r.width, height: r.height, expanded: el.closest("details").open, ariaExpanded: el.closest("details").querySelector("summary").getAttribute("aria-expanded") };
      });
      console.log("mobile menu viewport:", width, dropdown);
      if (dropdown.left < -1 || dropdown.right > width + 1) failures.push("mobile menu is clipped at " + width + "px");
      if (!dropdown.expanded || dropdown.ariaExpanded !== "true") failures.push("mobile menu expanded state is not announced at " + width + "px");
      await page.keyboard.press("Escape");
      if (await page.locator(".nav-menu").evaluate((el) => el.open)) failures.push("Escape does not close mobile menu at " + width + "px");
      if (await page.locator(".nav-menu summary").evaluate((el) => document.activeElement !== el)) failures.push("Escape does not restore menu focus at " + width + "px");
    }
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(new URL("compte/index.html", BASE).toString(), { waitUntil: "domcontentloaded" });
    if (await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1)) failures.push("account page mobile horizontal overflow");

    if (errors.length) failures.push("page errors: " + errors.join("; "));
    if (failures.length) {
      console.error("FAILED:", failures.join("; "));
      process.exitCode = 1;
    } else {
      console.log("OK: responsive bilingual homepage");
    }
  } catch (error) {
    console.error("HOMEPAGE TEST ERROR:", error && error.stack || error);
    process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
  }
})();
