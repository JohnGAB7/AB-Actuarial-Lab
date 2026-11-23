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
      title: document.querySelector(".home-intro h2").textContent
    }));
    console.log("mobile EN:", englishMobile);
    if (englishMobile.lang !== "en") failures.push("English homepage language");
    if (englishMobile.scrollWidth > englishMobile.width + 1) failures.push("English mobile horizontal overflow");
    if (!/Understand the idea/.test(englishMobile.title)) failures.push("English editorial content");

    await page.setViewportSize({ width: 1440, height: 900 });
    const desktop = await page.evaluate(() => ({
      width: window.innerWidth,
      scrollWidth: document.documentElement.scrollWidth,
      heroColumns: getComputedStyle(document.querySelector(".hero-in")).gridTemplateColumns
    }));
    console.log("desktop EN:", desktop);
    if (desktop.scrollWidth > desktop.width + 1) failures.push("desktop horizontal overflow");
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
