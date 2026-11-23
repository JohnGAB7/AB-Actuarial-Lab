// Affiche une séance une étape à la fois. Le contenu vient du JSON intégré à la page (généré depuis contenus/*.yaml).
// Formules : KaTeX. Éditeur : CodeMirror 5. Python : Pyodide, chargé au premier lancement des tests.
const S = JSON.parse(document.getElementById("seance").textContent);
const SCRIPT_URL = document.currentScript ? document.currentScript.src : location.href;
const $ = (s, r = document) => r.querySelector(s);
const el = (tag, attrs = {}, ...kids) => {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "html") e.innerHTML = v; else if (k === "class") e.className = v; else e.setAttribute(k, v);
  }
  e.append(...kids.filter((k) => k !== null && k !== undefined && k !== ""));
  return e;
};
const KEY = "parcours:" + S.id;
const store = {
  get(k, d) { try { const v = localStorage.getItem(KEY + k); return v === null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem(KEY + k, JSON.stringify(v)); } catch {} },
};
let progress = store.get(":etapes", {});
const N = S.etapes.length;
const fr = (v, d) => v.toLocaleString("fr-BE", { minimumFractionDigits: d, maximumFractionDigits: d });

function math(node) {
  if (window.renderMathInElement) {
    renderMathInElement(node, {
      delimiters: [{ left: "$$", right: "$$", display: true }, { left: "$", right: "$", display: false }],
      throwOnError: false,
    });
  }
}
function tex(src, display = true) {
  const d = el("div", { class: display ? "formula" : "" });
  if (window.katex) katex.render(src, d, { displayMode: display, throwOnError: false });
  else d.textContent = src;
  return d;
}
// Signale un changement local : compte.js le synchronise avec le compte, si l'apprenant est connecté.
let changeTimer = null;
function changed() { clearTimeout(changeTimer); changeTimer = setTimeout(() => document.dispatchEvent(new CustomEvent("parcours:change", { detail: S.id })), 1500); }
function markDone(i) {
  const neuf = !progress[i];
  progress[i] = true; store.set(":etapes", progress); segs(current());
  if (neuf) changed();
}
function saveCode(v) { store.set(":code", v); store.set(":code-at", new Date().toISOString()); changed(); }
function current() {
  const m = location.hash.match(/^#etape-(\d+)$/);
  const i = m ? parseInt(m[1], 10) - 1 : 0;
  return Math.min(Math.max(i, 0), N - 1);
}
function segs(i) {
  $("#segs").replaceChildren(...S.etapes.map((e, j) => {
    const a = el("a", { href: "#etape-" + (j + 1), class: (progress[j] ? "ok " : "") + (j === i ? "on" : ""), "aria-label": `Étape ${j + 1} : ${e.titre}` });
    if (j === i) a.setAttribute("aria-current", "step");
    return a;
  }));
}

/* ---------- Table de Makeham ---------- */
const T = S.table;
const lx = (x) => T.k * Math.pow(T.s, x) * Math.pow(T.g, Math.pow(T.c, x));
const mu = (x) => -Math.log(T.s) - Math.log(T.g) * Math.log(T.c) * Math.pow(T.c, x);
const ex = (x) => { let s = 0; for (let k = 1; k <= T.omega - x; k++) s += lx(x + k); return s / lx(x); };

function interactif() {
  let age = 65;
  const cv = el("canvas", { role: "img", "aria-label": "Force de mortalité de la table MK selon l'âge, échelle logarithmique" });
  const slider = el("input", { type: "range", min: "20", max: "100", step: "1", value: String(age), id: "age", "aria-label": "Âge" });
  const out = {
    age: el("output", { class: "big" }),
    mu: el("output"), q: el("output"), e: el("output"), ec: el("output"),
  };
  const stat = (label, o) => el("div", { class: "stat" }, el("span", { class: "lbl", html: label }), o);
  const panel = el("div", { class: "lab-stats" },
    el("div", { class: "stat age" }, el("span", { class: "lbl" }, "Âge"), out.age),
    stat("$\\mu_x$", out.mu), stat("$q_x$", out.q), stat("$e_x$", out.e), stat("$\\mathring{e}_x$", out.ec));
  const box = el("figure", { class: "lab" },
    el("div", { class: "lab-head" }, el("span", { class: "eyebrow" }, "Manipule"), el("span", { class: "hint" }, "Fais glisser l'âge : la table MK de ton simulateur répond.")),
    cv, el("div", { class: "lab-slider" }, el("span", { class: "mono" }, "20"), slider, el("span", { class: "mono" }, "100")), panel);

  const draw = () => {
    const r = cv.getBoundingClientRect(); if (!r.width) return;
    const d = window.devicePixelRatio || 1; cv.width = r.width * d; cv.height = r.height * d;
    const c = cv.getContext("2d"); c.setTransform(d, 0, 0, d, 0, 0);
    const cs = getComputedStyle(document.documentElement);
    const col = (n) => cs.getPropertyValue(n).trim();
    const W = r.width, H = r.height, L = 50, R = 16, Tp = 16, B = 28, x0 = 20, x1 = 100;
    const y0 = Math.log10(0.0005), y1 = Math.log10(1);
    const px = (x) => L + (x - x0) / (x1 - x0) * (W - L - R);
    const py = (v) => Tp + (y1 - Math.log10(v)) / (y1 - y0) * (H - Tp - B);
    c.font = "11px 'JetBrains Mono', ui-monospace, monospace"; c.lineWidth = 1;
    [0.001, 0.01, 0.1, 1].forEach((v) => {
      c.strokeStyle = col("--line"); c.beginPath(); c.moveTo(L, py(v)); c.lineTo(W - R, py(v)); c.stroke();
      c.fillStyle = col("--muted"); c.textAlign = "right"; c.fillText(String(v).replace(".", ","), L - 8, py(v) + 4);
    });
    [20, 40, 60, 80, 100].forEach((x) => { c.fillStyle = col("--muted"); c.textAlign = "center"; c.fillText(String(x), px(x), H - 8); });
    // aire sous la courbe
    const g = c.createLinearGradient(0, Tp, 0, H - B);
    g.addColorStop(0, col("--data-soft")); g.addColorStop(1, col("--surface"));
    c.beginPath(); c.moveTo(px(x0), H - B);
    for (let x = x0; x <= x1; x += 0.5) c.lineTo(px(x), py(mu(x)));
    c.lineTo(px(x1), H - B); c.closePath(); c.fillStyle = g; c.fill();
    c.strokeStyle = col("--data"); c.lineWidth = 2.5; c.beginPath();
    for (let x = x0; x <= x1; x += 0.5) { const y = py(mu(x)); x === x0 ? c.moveTo(px(x), y) : c.lineTo(px(x), y); }
    c.stroke();
    // repère de l'âge choisi
    c.setLineDash([3, 4]); c.strokeStyle = col("--progress"); c.lineWidth = 1;
    c.beginPath(); c.moveTo(px(age), Tp); c.lineTo(px(age), H - B); c.stroke(); c.setLineDash([]);
    c.fillStyle = col("--paper"); c.strokeStyle = col("--progress"); c.lineWidth = 2.5;
    c.beginPath(); c.arc(px(age), py(mu(age)), 5.5, 0, 7); c.fill(); c.stroke();
  };
  const update = () => {
    age = parseInt(slider.value, 10);
    const e = ex(age);
    out.age.textContent = age + " ans";
    out.mu.textContent = fr(mu(age), 5);
    out.q.textContent = fr(1 - lx(age + 1) / lx(age), 5);
    out.e.textContent = fr(e, 2) + " ans";
    out.ec.textContent = "≈ " + fr(e + 0.5, 2) + " ans";
    draw();
  };
  slider.addEventListener("input", update);
  addEventListener("resize", draw);
  matchMedia("(prefers-color-scheme: dark)").addEventListener?.("change", draw);
  requestAnimationFrame(update);
  return box;
}

/* ---------- Étapes ---------- */
const R = {
  video(e) {
    const ab = S.actu_basics || {};
    return [el("div", { class: "video" },
      el("div", { class: "video-in" },
        el("span", { class: "eyebrow light" }, "Actu-Basics · " + (ab.episode || "")),
        el("p", { class: "video-q" }, "« " + (ab.accroche_fr || "") + " »"),
        el("span", { class: "pill" }, "Vidéo en préparation"))),
      el("p", {}, e.texte)];
  },
  rappel(e) {
    return e.blocs.map((b) => {
      if (b.p) return el("p", { html: b.p });
      if (b.formule) return tex(b.formule);
      if (b.note) return el("aside", { class: "note" }, el("span", { class: "eyebrow" }, "Dans ton métier"), el("p", { html: b.note }));
      if (b.interactif) return interactif();
      if (b.sources) return el("section", { class: "sources" }, el("span", { class: "eyebrow" }, "Pour aller plus loin"),
        el("ol", {}, ...b.sources.map((s) => el("li", {},
          s.url ? el("a", { href: s.url, target: "_blank", rel: "noopener" }, s.titre) : el("span", { class: "src-t" }, s.titre),
          el("span", { class: "src-d" }, s.detail)))));
      return "";
    });
  },
  quiz(e, i) {
    const explication = (p) => {
      if (typeof p === "string") return `<p>${p}</p>`;
      const ligne = (k, lib) => p[k] ? `<p class="why-l"><span class="why-k">${lib}</span>${p[k]}</p>` : "";
      return ligne("rappel", "Rappel") + (p.formule ? `<div class="why-f">$$${p.formule}$$</div>` : "")
        + ligne("exemple", "Exemple") + ligne("piege", "Piège");
    };
    const ok = new Set();
    const score = el("p", { class: "score" });
    const upd = () => { score.textContent = `${ok.size} sur ${e.questions.length}`; };
    const qs = e.questions.map((it, qi) => {
      const why = el("div", { class: "why", html: "" }); why.hidden = true;
      const opts = el("div", { class: "opts", role: "group" }, ...it.options.map((t, j) => {
        const b = el("button", { class: "opt", type: "button", html: `<span class="k">${String.fromCharCode(65 + j)}</span><span>${t}</span>` });
        b.addEventListener("click", () => {
          opts.querySelectorAll(".opt").forEach((x) => x.classList.remove("right", "wrong"));
          const good = j === it.reponse;
          b.classList.add(good ? "right" : "wrong");
          why.hidden = false;
          why.innerHTML = `<p class="why-v ${good ? "ok" : "ko"}">${good ? "Juste." : "Pas tout à fait."}</p>` + explication(it.pourquoi);
          math(why);
          if (good) ok.add(qi); else ok.delete(qi);
          upd(); if (ok.size === e.questions.length) markDone(i);
        });
        return b;
      }));
      return el("div", { class: "q" }, el("span", { class: "qn mono" }, String(qi + 1).padStart(2, "0")), el("div", { class: "q-body" }, el("h3", { html: it.q }), opts, why));
    });
    upd();
    return [el("div", { class: "qs" }, ...qs), el("div", { class: "score-row" }, el("span", { class: "eyebrow" }, "Score"), score)];
  },
  calcul(e, i) {
    const t = el("div", { class: "tbl" }, el("table", {},
      el("thead", {}, el("tr", {}, ...e.donnees.entetes.map((h) => el("th", { html: h })))),
      el("tbody", {}, ...e.donnees.lignes.map((r) => el("tr", {}, ...r.map((c) => el("td", { html: c })))))));
    const fields = el("div", { class: "fields" }, ...e.champs.map((c) => el("div", { class: "field" },
      el("label", { for: "c_" + c.cle, html: c.libelle }),
      el("span", { class: "eq" }, "="),
      el("input", { id: "c_" + c.cle, inputmode: "decimal", placeholder: "0,0000", autocomplete: "off" }),
      el("span", { class: "st", id: "st_" + c.cle, "aria-live": "polite" }))));
    const check = el("button", { class: "btn", type: "button" }, "Vérifier");
    check.addEventListener("click", () => {
      let all = true;
      for (const c of e.champs) {
        const raw = $("#c_" + c.cle).value.trim().replace(/\s/g, "").replace(",", ".");
        const good = raw !== "" && Math.abs(parseFloat(raw) - c.valeur) <= c.tolerance;
        const st = $("#st_" + c.cle);
        st.className = "st " + (raw === "" ? "" : good ? "good" : "bad");
        st.textContent = raw === "" ? "à remplir" : good ? "juste" : "à revoir";
        all = all && good;
      }
      if (all) markDone(i);
    });
    const sol = el("details", { class: "solution" }, el("summary", {}, "Voir la solution"), el("div", { html: e.solution.replace(/\n/g, "<br>") }));
    return [t, fields, el("div", { class: "row" }, check), sol];
  },
  code(e, i) {
    const ta = el("textarea", { id: "code", spellcheck: "false", "aria-label": "Ton code Python" });
    ta.value = store.get(":code", null) || e.depart;
    const res = el("ol", { class: "results", "aria-live": "polite" },
      ...e.tests.map((t) => el("li", { class: "idle" }, el("span", { class: "dot" }), el("span", { class: "tn", html: t.nom }), el("span", { class: "tm" }))));
    const summary = el("p", { class: "res-sum" }, "Lance les tests quand ta fonction est prête.");
    const run = el("button", { class: "btn", type: "button" }, el("span", {}, "Lancer les tests"), el("kbd", {}, "Ctrl ↵"));
    const reset = el("button", { class: "btn ghost", type: "button" }, "Code de départ");
    const shell = el("div", { class: "editor" }, el("div", { class: "editor-bar" }, el("span", { class: "dots" }, el("i"), el("i"), el("i")), el("span", { class: "mono fname" }, e.fichier.split("/").pop())), ta);
    let cm = null;
    const value = () => (cm ? cm.getValue() : ta.value);
    requestAnimationFrame(() => {
      if (!window.CodeMirror) return;
      cm = CodeMirror.fromTextArea(ta, {
        mode: "python", lineNumbers: true, indentUnit: 4, tabSize: 4, matchBrackets: true, autoCloseBrackets: true,
        viewportMargin: Infinity,
        extraKeys: { Tab: (c) => c.replaceSelection("    "), "Ctrl-Enter": () => run.click(), "Cmd-Enter": () => run.click() },
      });
      cm.on("change", (c, ch) => { if (ch.origin !== "setValue") saveCode(cm.getValue()); });
    });
    ta.addEventListener("input", () => saveCode(ta.value));
    reset.addEventListener("click", () => { if (cm) cm.setValue(e.depart); else ta.value = e.depart; saveCode(e.depart); });
    const stop = el("button", { class: "btn ghost", type: "button", hidden: "" }, "Arrêter");
    stop.addEventListener("click", () => { stopPython(); });
    run.addEventListener("click", async () => {
      run.disabled = true; stop.hidden = false;
      summary.className = "res-sum";
      summary.textContent = "Chargement de Python… (quelques secondes la première fois)";
      [...res.children].forEach((li) => { li.className = "run"; li.querySelector(".tm").textContent = ""; });
      try {
        const results = await runPython(value(), e.tests.map((t) => t.expr), () => { summary.textContent = "Exécution…"; });
        let n = 0;
        results.forEach((r, k) => {
          const li = res.children[k], msg = li.querySelector(".tm");
          li.className = r.status;
          if (r.status === "pass") n++;
          msg.textContent = r.status === "todo" ? "fonction pas encore écrite" : r.msg === "unexpected" ? "valeur inattendue" : r.msg;
        });
        summary.textContent = n === e.tests.length ? `Les ${n} tests passent. Bravo.` : `${n} test${n > 1 ? "s" : ""} sur ${e.tests.length} passe${n > 1 ? "nt" : ""}.`;
        summary.className = "res-sum " + (n === e.tests.length ? "good" : "");
        if (n === e.tests.length) markDone(i);
      } catch (err) {
        [...res.children].forEach((li) => { li.className = "idle"; });
        summary.textContent = String(err.message || err);
      }
      run.disabled = false; stop.hidden = true;
    });
    const where = el("p", { class: "hint" }, "Même exercice dans le dépôt : ", el("code", {}, e.fichier), ". Les tests y tournent aussi sur GitHub Actions.");
    return [shell, el("div", { class: "row" }, run, stop, reset), el("div", { class: "results-box" }, summary, res), where];
  },
  vocabulaire(e, i) {
    const seen = new Set();
    return [el("div", { class: "cards" }, ...e.cartes.map(([f, en, exm], j) => {
      const b = el("button", { class: "card", type: "button", "aria-expanded": "false" },
        el("span", { class: "fr" }, f), el("span", { class: "tap" }, "Voir l'anglais →"),
        el("span", { class: "back" }, el("b", {}, en), el("i", {}, exm)));
      b.addEventListener("click", () => {
        const on = b.classList.toggle("flip"); b.setAttribute("aria-expanded", String(on));
        seen.add(j); if (seen.size === e.cartes.length) markDone(i);
      });
      return b;
    }))];
  },
};
const lastLine = (err) => String(err.message || err).trim().split("\n").pop();

/* ---------- Python dans un Web Worker ---------- */
// Le code de l'apprenant tourne hors de la page : pas d'accès au DOM ni à la session du compte.
// Limite de temps après le chargement ; « Arrêter » ou le dépassement termine le worker.
const PY_LIMITE_MS = 10000;
let worker = null, pending = null, seq = 0;
function stopPython(raison) {
  if (worker) { worker.terminate(); worker = null; }
  if (pending) { const p = pending; pending = null; clearTimeout(p.timer); p.reject(new Error(raison || "Exécution arrêtée. Python se rechargera au prochain lancement.")); }
}
function runPython(code, tests, onRunning) {
  stopPython();
  if (!worker) {
    worker = new Worker(new URL("python-worker.js", SCRIPT_URL));
    worker.onmessage = (ev) => {
      const m = ev.data; if (!pending || m.id !== pending.id) return;
      if (m.phase === "running") {
        onRunning && onRunning();
        pending.timer = setTimeout(() => stopPython(`Arrêt après ${PY_LIMITE_MS / 1000} secondes : boucle infinie ou calcul trop long ?`), PY_LIMITE_MS);
        return;
      }
      const p = pending; pending = null; clearTimeout(p.timer);
      if (m.phase === "done") p.resolve(m.results);
      else p.reject(new Error(m.msg));
    };
    worker.onerror = () => stopPython("Python n'a pas pu se charger. Vérifie ta connexion, ou lance les tests du dépôt avec pytest.");
  }
  return new Promise((resolve, reject) => {
    pending = { id: ++seq, resolve, reject, timer: null };
    worker.postMessage({ id: seq, code, tests });
  });
}

function render() {
  const i = current(), e = S.etapes[i];
  segs(i);
  const stage = $("#stage");
  stage.replaceChildren(
    el("div", { class: "step-head" },
      el("span", { class: "eyebrow" }, `Étape ${i + 1} sur ${N} · ${e.minutes} min`),
      el("h1", {}, e.titre),
      e.intro ? el("p", { class: "lead", html: e.intro }) : null),
    el("div", { class: "flow" }, ...R[e.type](e, i)));
  math(stage);
  stage.classList.remove("enter"); void stage.offsetWidth; stage.classList.add("enter");
  if (e.type === "rappel" || e.type === "video") markDone(i);
  $("#prev").disabled = i === 0;
  $("#next").textContent = i === N - 1 ? "Terminer" : "Suivante →";
  const w = $("#where"); w.replaceChildren(el("a", { href: S.module_url }, S.module_titre), ` · ${S.titre}`);
  document.title = `${e.titre} · ${S.titre}`;
  window.scrollTo({ top: 0 });
}
$("#prev").addEventListener("click", () => { const i = current(); if (i > 0) location.hash = "etape-" + i; });
$("#next").addEventListener("click", () => {
  const i = current();
  if (i === N - 1) location.href = S.module_url; else location.hash = "etape-" + (i + 2);
});
addEventListener("keydown", (ev) => {
  const t = ev.target;
  if (t.closest && t.closest("input, textarea, .CodeMirror")) return;
  if (ev.key === "ArrowRight") $("#next").click();
  if (ev.key === "ArrowLeft") $("#prev").click();
});
addEventListener("hashchange", render);
// Progression arrivée d'un autre appareil : on recharge l'état local et on réaffiche l'étape.
document.addEventListener("parcours:remote", (ev) => {
  if (!(ev.detail || []).includes(S.id)) return;
  progress = store.get(":etapes", {});
  const enEdition = document.activeElement && document.activeElement.closest && document.activeElement.closest(".CodeMirror, textarea");
  if (enEdition) segs(current()); else render();
});
render();
