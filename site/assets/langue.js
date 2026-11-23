// FR | EN switch: keeps the current step when changing language and remembers the choice.
// On the home page only, a visitor who chose a language (or whose browser has no French) lands on that language.
(function () {
  "use strict";
  var CLE = "parcours:langue";
  var ici = document.documentElement.lang === "en" ? "en" : "fr";
  var lire = function () { try { return localStorage.getItem(CLE); } catch (e) { return null; } };
  var ecrire = function (v) { try { localStorage.setItem(CLE, v); } catch (e) { /* private mode */ } };
  var lien = document.querySelector(".langs a[data-langue]");
  if (!lien) return;
  lien.addEventListener("click", function () {
    ecrire(lien.dataset.langue);
    if (location.hash) lien.href = lien.href.split("#")[0] + location.hash;
  });
  if (!document.body.classList.contains("accueil")) return;
  var depuisLeSite = document.referrer && document.referrer.indexOf(location.origin) === 0;
  if (depuisLeSite) return;
  var voulu = lire();
  if (!voulu) {
    var langues = navigator.languages || [navigator.language || ""];
    voulu = langues.some(function (l) { return /^fr\b/i.test(l); }) ? "fr" : "en";
  }
  if (voulu !== ici) location.replace(lien.href);
})();
