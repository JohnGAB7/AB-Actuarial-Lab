// Pages de navigation (accueil, domaines, modules) : progression lue dans ce navigateur et bouton « Reprendre ».
// Le plan (ordre conseillé, nombre d'étapes par séance) est intégré à la page par tools/construire.py.
(function () {
  "use strict";
  var EN = document.documentElement.lang === "en";
  var tr = function (fr, en) { return EN ? en : fr; };
  var plan = [];
  try { plan = JSON.parse(document.getElementById("plan").textContent); } catch (e) { return; }
  var faites = function (sid) {
    try {
      var v = JSON.parse(localStorage.getItem("parcours:" + sid + ":etapes") || "{}");
      return Object.keys(v).filter(function (k) { return v[k] === true; }).length;
    } catch (e) { return 0; }
  };

  function afficher() {
    var etat = plan.map(function (p) { return { p: p, f: Math.min(faites(p.s), p.n) }; });
    var somme = function (filtre) {
      var f = 0, n = 0;
      etat.forEach(function (x) { if (filtre(x.p)) { f += x.f; n += x.p.n; } });
      return n ? f / n : 0;
    };
    var barre = function (el, r) {
      var i = el.querySelector(".barre i"); if (i) i.style.width = Math.round(r * 100) + "%";
      el.classList.toggle("commence", r > 0); el.classList.toggle("fini", r >= 1);
    };
    document.querySelectorAll("[data-domaine]").forEach(function (el) { barre(el, somme(function (p) { return p.d === el.dataset.domaine; })); });
    document.querySelectorAll("[data-module]").forEach(function (el) { barre(el, somme(function (p) { return p.m === el.dataset.module; })); });
    document.querySelectorAll("[data-seance]").forEach(function (el) {
      var r = somme(function (p) { return p.s === el.dataset.seance; });
      barre(el, r);
      var t = el.querySelector("[data-etat]");
      if (t) t.textContent = r >= 1 ? tr("Terminée ✓", "Finished ✓") : r > 0 ? tr("Continuer →", "Continue →") : tr("Commencer →", "Start →");
    });
    var cta = document.querySelector("[data-reprendre]");
    if (cta && etat.length) {
      var commence = etat.some(function (x) { return x.f > 0; });
      var suite = etat.filter(function (x) { return x.f < x.p.n; })[0];
      var base = BASE + (EN ? "en/" : "");
      if (suite) {
        cta.href = base + suite.p.s + "/index.html";
        cta.textContent = (commence ? tr("Reprendre la séance", "Resume session") : tr("Commencer la première séance", "Start first session")) + " →";
      } else {
        cta.textContent = tr("Tout est terminé. Revoir le parcours →", "All done. Review the path →");
      }
    }
  }
  var BASE = (document.currentScript && document.currentScript.dataset.base) || "";
  afficher();
  // Progression arrivée du compte (compte.js) : on met à jour les barres.
  document.addEventListener("parcours:remote", afficher);
  addEventListener("pageshow", afficher);

  // Menu mobile : se ferme avec Échap ou un clic à l'extérieur.
  var menu = document.querySelector(".nav-menu");
  if (menu) {
    var summary = menu.querySelector("summary");
    var synchroniserEtat = function () { summary.setAttribute("aria-expanded", menu.open ? "true" : "false"); };
    synchroniserEtat();
    menu.addEventListener("toggle", synchroniserEtat);
    document.addEventListener("click", function (ev) {
      if (menu.open && !menu.contains(ev.target)) menu.open = false;
    });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && menu.open) {
        menu.open = false;
        summary.focus();
      }
    });
  }
})();
