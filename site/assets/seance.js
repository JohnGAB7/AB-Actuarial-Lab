// Affiche une séance une étape à la fois. Le contenu vient du JSON intégré à la page (généré depuis contenus/*.yaml).
const S = JSON.parse(document.getElementById("seance").textContent);
const $ = (s, r = document) => r.querySelector(s);
const el = (tag, attrs = {}, ...kids) => {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "html") e.innerHTML = v; else if (k === "class") e.className = v; else e.setAttribute(k, v);
  }
  e.append(...kids);
  return e;
};
const KEY = "parcours:" + S.id;
const load = () => { try { return JSON.parse(localStorage.getItem(KEY) || "{}"); } catch { return {}; } };
const save = (v) => { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch {} };
let progress = load();
const N = S.etapes.length;

function markDone(i) { progress[i] = true; save(progress); segs(current()); }
function current() {
  const m = location.hash.match(/^#etape-(\d+)$/);
  const i = m ? parseInt(m[1], 10) - 1 : 0;
  return Math.min(Math.max(i, 0), N - 1);
}
function segs(i) {
  const box = $("#segs");
  box.replaceChildren(...S.etapes.map((_, j) => el("span", { class: (progress[j] ? "ok " : "") + (j === i ? "on" : ""), title: S.etapes[j].titre })));
}

const R = {
  video(e, i) {
    return [el("div", { class: "video" }, el("div", {}, el("b", {}, "Vidéo à venir"), S.actu_basics ? S.actu_basics.episode : "")),
      el("p", {}, e.texte)];
  },
  rappel(e) {
    return e.blocs.map((b) => {
      if (b.p) return el("p", { html: b.p });
      if (b.formule) return el("div", { class: "formula" }, b.formule);
      if (b.note) return el("p", { class: "note", html: b.note });
      if (b.graphique) return chart(b.graphique);
      return "";
    });
  },
  quiz(e, i) {
    const ok = new Set();
    const qs = e.questions.map((it, qi) => {
      const why = el("p", { class: "why" }); why.hidden = true;
      const opts = el("div", { class: "opts" }, ...it.options.map((t, j) => {
        const b = el("button", { class: "opt", type: "button" }, t);
        b.addEventListener("click", () => {
          opts.querySelectorAll(".opt").forEach((x) => x.classList.remove("right", "wrong"));
          const good = j === it.reponse;
          b.classList.add(good ? "right" : "wrong");
          why.hidden = false;
          why.textContent = (good ? "Juste. " : "Pas tout à fait. ") + it.pourquoi;
          if (good) { ok.add(qi); if (ok.size === e.questions.length) markDone(i); }
        });
        return b;
      }));
      return el("div", { class: "q" }, el("h3", {}, `${qi + 1}. ${it.q}`), opts, why);
    });
    return [el("div", { class: "qs" }, ...qs)];
  },
  calcul(e, i) {
    const t = el("div", { class: "tbl" }, el("table", {},
      el("thead", {}, el("tr", {}, ...e.donnees.entetes.map((h) => el("th", {}, h)))),
      el("tbody", {}, ...e.donnees.lignes.map((r) => el("tr", {}, ...r.map((c) => el("td", {}, c)))))));
    const fields = el("div", { class: "fields" }, ...e.champs.map((c) => el("div", { class: "field" },
      el("label", { for: "c_" + c.cle }, c.libelle + " ="),
      el("input", { id: "c_" + c.cle, inputmode: "decimal", placeholder: "0,0000", autocomplete: "off" }),
      el("span", { class: "st", id: "st_" + c.cle }))));
    const check = el("button", { class: "btn", type: "button" }, "Vérifier");
    check.addEventListener("click", () => {
      let all = true;
      for (const c of e.champs) {
        const raw = $("#c_" + c.cle).value.trim().replace(/\s/g, "").replace(",", ".");
        const good = raw !== "" && Math.abs(parseFloat(raw) - c.valeur) <= c.tolerance;
        const st = $("#st_" + c.cle);
        st.className = "st " + (good ? "good" : "bad");
        st.textContent = raw === "" ? "à remplir" : good ? "juste" : "à revoir";
        all = all && good;
      }
      if (all) markDone(i);
    });
    const sol = el("details", {}, el("summary", {}, "Voir la solution"), el("p", {}, e.solution));
    return [t, fields, el("div", { class: "row" }, check), sol];
  },
  code(e, i) {
    const ed = el("textarea", { class: "editor", id: "code", spellcheck: "false", "aria-label": "Ton code Python" });
    let saved = null; try { saved = localStorage.getItem(KEY + ":code"); } catch {}
    ed.value = saved || e.depart;
    ed.addEventListener("input", () => { try { localStorage.setItem(KEY + ":code", ed.value); } catch {} });
    ed.addEventListener("keydown", (ev) => {
      if (ev.key === "Tab") { ev.preventDefault(); ed.setRangeText("    ", ed.selectionStart, ed.selectionEnd, "end"); }
    });
    const out = el("div", { class: "out", "aria-live": "polite" }, "Les résultats des tests s'afficheront ici.");
    const run = el("button", { class: "btn", type: "button" }, "Lancer les tests");
    const reset = el("button", { class: "btn ghost", type: "button" }, "Code de départ");
    const hint = el("span", { class: "hint" }, "Python se charge au premier lancement (quelques secondes).");
    reset.addEventListener("click", () => { ed.value = e.depart; ed.dispatchEvent(new Event("input")); });
    run.addEventListener("click", async () => {
      run.disabled = true; hint.textContent = "Exécution…";
      try {
        const py = await pyodide();
        const lines = [];
        py.runPython("_ns = {}");
        const ns = py.globals.get("dict")();
        py.runPython(ed.value, { globals: ns });
        for (const t of e.tests) {
          try { lines.push((py.runPython(t.expr, { globals: ns }) ? "✓  " : "✗  ") + t.nom); }
          catch (err) { lines.push("✗  " + t.nom + " : " + String(err.message || err).trim().split("\n").pop()); }
        }
        const all = lines.every((l) => l.startsWith("✓"));
        out.textContent = lines.join("\n") + (all ? "\n\nTous les tests passent." : "\n\nAu moins un test échoue. Relis la formule et les bornes de la somme.");
        if (all) markDone(i);
      } catch (err) {
        out.textContent = String(err.message || err).trim().split("\n").slice(-3).join("\n");
      }
      run.disabled = false; hint.textContent = "";
    });
    const where = el("p", { class: "hint" }, "Même exercice dans le dépôt : ", el("span", { class: "mono" }, e.fichier), ". Les tests y tournent sur GitHub Actions.");
    return [ed, el("div", { class: "row" }, run, reset, hint), out, where];
  },
  vocabulaire(e, i) {
    const seen = new Set();
    return [el("div", { class: "cards" }, ...e.cartes.map(([fr, en, ex], j) => {
      const b = el("button", { class: "card", type: "button" }, el("span", { class: "fr" }, fr), el("span", { class: "tap" }, "Voir l'anglais"),
        el("span", { class: "back", html: `<b>${en}</b><br><i>${ex}</i>` }));
      b.addEventListener("click", () => { b.classList.toggle("flip"); seen.add(j); if (seen.size === e.cartes.length) markDone(i); });
      return b;
    }))];
  },
};

let pyPromise = null;
function pyodide() {
  if (pyPromise) return pyPromise;
  pyPromise = new Promise((resolve, reject) => {
    const s = document.createElement("script");
    s.src = "https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js";
    s.onload = () => window.loadPyodide().then(resolve, reject);
    s.onerror = () => reject(new Error("Python n'a pas pu se charger. Vérifie ta connexion, ou lance les tests du dépôt avec pytest."));
    document.head.append(s);
  }).catch((e) => { pyPromise = null; throw e; });
  return pyPromise;
}

function chart(kind) {
  const t = S.table;
  const mu = (x) => -Math.log(t.s) - Math.log(t.g) * Math.log(t.c) * Math.pow(t.c, x);
  const cv = el("canvas", { role: "img", "aria-label": "Force de mortalité de la table MK, de 20 à 100 ans, échelle logarithmique" });
  const box = el("figure", { class: "chart", style: "margin:0" }, cv, el("figcaption", { class: "caption" }, "Force de mortalité μₓ, table MK, échelle logarithmique. Points : 40 et 65 ans."));
  const draw = () => {
    const r = cv.getBoundingClientRect(); if (!r.width) return;
    const d = window.devicePixelRatio || 1; cv.width = r.width * d; cv.height = r.height * d;
    const c = cv.getContext("2d"); c.scale(d, d);
    const cs = getComputedStyle(document.documentElement);
    const muted = cs.getPropertyValue("--muted").trim(), line = cs.getPropertyValue("--line").trim(), data = cs.getPropertyValue("--data").trim();
    const W = r.width, H = r.height, L = 54, Rr = 30, T = 14, B = 30, x0 = 20, x1 = 100, y0 = Math.log10(0.0005), y1 = Math.log10(1);
    const px = (x) => L + (x - x0) / (x1 - x0) * (W - L - Rr), py = (v) => T + (y1 - Math.log10(v)) / (y1 - y0) * (H - T - B);
    c.font = "11px 'JetBrains Mono', monospace"; c.lineWidth = 1;
    [0.001, 0.01, 0.1].forEach((v) => { c.strokeStyle = line; c.beginPath(); c.moveTo(L, py(v)); c.lineTo(W - Rr, py(v)); c.stroke(); c.fillStyle = muted; c.textAlign = "right"; c.fillText(String(v).replace(".", ","), L - 8, py(v) + 4); });
    [20, 40, 60, 80, 100].forEach((x) => { c.fillStyle = muted; c.textAlign = "center"; c.fillText(x + " ans", px(x), H - 8); });
    c.strokeStyle = data; c.lineWidth = 2.5; c.beginPath();
    for (let x = x0; x <= x1; x += 0.5) { const y = py(mu(x)); x === x0 ? c.moveTo(px(x), y) : c.lineTo(px(x), y); }
    c.stroke();
    c.fillStyle = data; [40, 65].forEach((x) => { c.beginPath(); c.arc(px(x), py(mu(x)), 4, 0, 7); c.fill(); });
  };
  requestAnimationFrame(draw);
  addEventListener("resize", draw);
  matchMedia("(prefers-color-scheme: dark)").addEventListener?.("change", draw);
  return box;
}

function render() {
  const i = current(), e = S.etapes[i];
  segs(i);
  const stage = $("#stage");
  stage.replaceChildren(
    el("span", { class: "eyebrow" }, `Étape ${i + 1} sur ${N} · ${e.minutes} min`),
    el("h1", {}, e.titre),
    ...(e.intro ? [el("p", { class: "lead" }, e.intro)] : []),
    el("div", { class: "flow" }, ...R[e.type](e, i)));
  if (e.type === "rappel" || e.type === "video") markDone(i);
  $("#prev").disabled = i === 0;
  $("#next").textContent = i === N - 1 ? "Retour au parcours" : "Étape suivante →";
  $("#where").textContent = `${S.module_titre} · ${S.titre}`;
  window.scrollTo({ top: 0 });
}
$("#prev").addEventListener("click", () => { const i = current(); if (i > 0) location.hash = "etape-" + i; });
$("#next").addEventListener("click", () => {
  const i = current();
  if (i === N - 1) location.href = S.accueil; else location.hash = "etape-" + (i + 2);
});
addEventListener("hashchange", render);
render();
