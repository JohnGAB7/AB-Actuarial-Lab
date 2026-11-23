/* Optional learner account (Supabase, magic link).
 *
 * Local-first: the site works without an account and keeps progress in this browser (localStorage).
 * Once signed in, each session's progress (finished steps and Python code) is merged with the account:
 * finished steps are the union of both sides, the most recently edited code wins.
 * Only the public project URL and the publishable key reach the browser (assets/config.js, written at build time).
 * Row Level Security limits every row to its owner (supabase/migrations/001_progression.sql).
 * supabase-js is vendored and loaded only on the account page, or on other pages when a session already exists.
 */
(function () {
  "use strict";
  var CFG = window.PA_CONFIG || {};
  var BASE = (document.currentScript && document.currentScript.dataset.base) || "";
  var LIB = BASE + "assets/vendor/supabase/supabase.js";
  var PREFIX = "parcours:";
  var ID = /^[a-z0-9+-]{2,20}\/s[0-9]{2}$/;
  var actif = !!(CFG.url && CFG.key);
  var ref = actif ? (/^https:\/\/([a-z0-9]+)\.supabase\.co/.exec(CFG.url) || [])[1] : null;
  var SESSION_KEY = ref ? "sb-" + ref + "-auth-token" : null;

  function store() { try { return window.localStorage; } catch (e) { return null; } }
  function lire(k, d) { var s = store(); if (!s) return d; try { var v = s.getItem(k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } }
  function ecrire(k, v) { var s = store(); if (!s) return; try { s.setItem(k, JSON.stringify(v)); } catch (e) {} }

  /* Local progress, one record per session: {seance_id, etapes, code, code_at}. */
  function local() {
    var out = {}, s = store(); if (!s) return out;
    for (var i = 0; i < s.length; i++) {
      var m = /^parcours:(.+):(etapes|code)$/.exec(s.key(i) || "");
      if (!m || !ID.test(m[1])) continue;
      out[m[1]] = out[m[1]] || { seance_id: m[1], etapes: {}, code: null, code_at: null };
    }
    Object.keys(out).forEach(function (id) {
      var r = out[id], e = lire(PREFIX + id + ":etapes", {});
      if (e && typeof e === "object" && !Array.isArray(e)) Object.keys(e).forEach(function (k) { if (e[k] === true && /^\d{1,2}$/.test(k)) r.etapes[k] = true; });
      var c = lire(PREFIX + id + ":code", null);
      if (typeof c === "string" && c.length <= 20000) { r.code = c; r.code_at = lire(PREFIX + id + ":code-at", null) || new Date(0).toISOString(); }
    });
    return out;
  }

  function fusion(a, b) {
    var etapes = {};
    [a, b].forEach(function (r) { if (r && r.etapes) Object.keys(r.etapes).forEach(function (k) { if (r.etapes[k] === true) etapes[k] = true; }); });
    var ta = a && a.code_at ? Date.parse(a.code_at) : -1, tb = b && b.code_at ? Date.parse(b.code_at) : -1;
    var code = tb > ta ? b : a;
    return { seance_id: (a || b).seance_id, etapes: etapes, code: code ? code.code : null, code_at: code ? code.code_at : null };
  }
  var pareil = function (x, y) {
    return !!x && !!y && JSON.stringify(Object.keys(x.etapes).sort()) === JSON.stringify(Object.keys(y.etapes || {}).sort())
      && x.code === y.code && (x.code_at ? Date.parse(x.code_at) : -1) === (y.code_at ? Date.parse(y.code_at) : -1);
  };

  /* Pull the account, merge with this browser, push what changed, write back locally. */
  function sync(sb, user) {
    return sb.from("progression").select("seance_id,etapes,code,code_at").eq("user_id", user.id).limit(1000).then(function (res) {
      if (res.error) throw res.error;
      var distant = {}; (res.data || []).forEach(function (r) { if (ID.test(r.seance_id)) distant[r.seance_id] = r; });
      var loc = local(), ids = {}, envoi = [], recus = [];
      Object.keys(loc).concat(Object.keys(distant)).forEach(function (id) { ids[id] = true; });
      Object.keys(ids).forEach(function (id) {
        var m = fusion(loc[id], distant[id]);
        if (!pareil(m, distant[id])) envoi.push({ user_id: user.id, seance_id: id, etapes: m.etapes, code: m.code, code_at: m.code_at, updated_at: new Date().toISOString() });
        if (!pareil(m, loc[id])) {
          ecrire(PREFIX + id + ":etapes", m.etapes);
          if (m.code !== null) { ecrire(PREFIX + id + ":code", m.code); ecrire(PREFIX + id + ":code-at", m.code_at); }
          recus.push(id);
        }
      });
      var up = envoi.length ? sb.from("progression").upsert(envoi, { onConflict: "user_id,seance_id" }) : Promise.resolve({ error: null });
      return up.then(function (r) {
        if (r.error) throw r.error;
        if (recus.length) document.dispatchEvent(new CustomEvent("parcours:remote", { detail: recus }));
        return { total: Object.keys(ids).length, envoyes: envoi.length, recus: recus.length };
      });
    });
  }

  var clientPromise = null;
  function client() {
    if (!clientPromise) clientPromise = new Promise(function (ok, ko) {
      if (window.supabase && window.supabase.createClient) return ok(window.supabase);
      var sc = document.createElement("script"); sc.src = LIB; sc.async = true;
      sc.onload = function () { ok(window.supabase); }; sc.onerror = function () { ko(new Error("lib")); };
      document.head.appendChild(sc);
    }).then(function (lib) {
      return lib.createClient(CFG.url, CFG.key, { auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true, flowType: "implicit" } });
    });
    return clientPromise;
  }

  /* ---------- account page ---------- */
  var root = document.querySelector("[data-compte]");
  if (root) {
    var $ = function (sel) { return root.querySelector(sel); };
    var statut = $("[data-statut]"), form = $("[data-form]"), connecte = $("[data-connecte]");
    var dire = function (txt, etat) { statut.textContent = txt; statut.dataset.etat = etat || ""; };
    if (!actif) { form.hidden = true; connecte.hidden = true; dire("Les comptes ne sont pas encore activés sur ce site. Ta progression reste dans ce navigateur."); return; }
    var montrer = function (user) { form.hidden = !!user; connecte.hidden = !user; if (user) $("[data-email]").textContent = user.email || ""; };
    dire("Vérification de ton compte…");
    client().then(function (sb) {
      var enCours = false;
      var lancer = function (user) {
        if (enCours) return; enCours = true;
        dire("Synchronisation de ta progression…");
        sync(sb, user).then(function (r) {
          dire("Progression enregistrée sur ton compte : " + r.total + " séance(s). " + r.recus + " mise(s) à jour sur cet appareil.", "ok");
        }).catch(function () {
          dire("La synchronisation a échoué. Ta progression reste dans ce navigateur ; réessaie plus tard.", "erreur");
        }).then(function () { enCours = false; });
      };
      sb.auth.getSession().then(function (r) {
        var user = r.data && r.data.session && r.data.session.user;
        montrer(user);
        if (user) lancer(user); else dire("Tu n'es pas connecté. Ta progression est enregistrée dans ce navigateur seulement.");
      });
      sb.auth.onAuthStateChange(function (ev, session) {
        if (ev === "SIGNED_IN" && session) { montrer(session.user); lancer(session.user); }
        if (ev === "SIGNED_OUT") { montrer(null); dire("Déconnecté. Ta progression reste dans ce navigateur."); }
      });
      form.addEventListener("submit", function (ev) {
        ev.preventDefault();
        var email = (form.querySelector("input[type=email]").value || "").trim(); if (!email) return;
        var btn = form.querySelector("button"); btn.disabled = true;
        sb.auth.signInWithOtp({ email: email, options: { emailRedirectTo: location.origin + location.pathname, shouldCreateUser: true } }).then(function (r) {
          btn.disabled = false;
          if (r.error) dire("Impossible d'envoyer le lien. Vérifie l'adresse ou réessaie dans quelques minutes.", "erreur");
          else dire("Regarde ta boîte mail : un lien de connexion t'a été envoyé. Ouvre-le sur cet appareil.", "ok");
        });
      });
      $("[data-sync]").addEventListener("click", function () { sb.auth.getUser().then(function (r) { if (r.data && r.data.user) lancer(r.data.user); }); });
      $("[data-deconnexion]").addEventListener("click", function () { sb.auth.signOut(); });
      var supp = $("[data-supprimer]"), conf = $("[data-confirmer]");
      supp.addEventListener("click", function () { conf.hidden = false; supp.hidden = true; });
      $("[data-annuler]").addEventListener("click", function () { conf.hidden = true; supp.hidden = false; });
      $("[data-oui]").addEventListener("click", function () {
        sb.rpc("supprimer_mon_compte").then(function (r) {
          if (r.error) { dire("La suppression a échoué. Réessaie plus tard.", "erreur"); return; }
          conf.hidden = true; supp.hidden = false;
          sb.auth.signOut().then(function () { dire("Ton compte et ta progression en ligne sont supprimés. Ce navigateur garde sa copie locale.", "ok"); });
        });
      });
    }).catch(function () {
      form.hidden = true; connecte.hidden = true;
      dire("Les comptes sont indisponibles pour le moment. Ta progression reste dans ce navigateur.", "erreur");
    });
    return;
  }

  /* ---------- other pages: quiet background sync, only if already signed in ---------- */
  var s = store();
  if (!actif || !s || !s.getItem(SESSION_KEY)) return;
  var envoyer = function () {
    client().then(function (sb) {
      return sb.auth.getSession().then(function (r) { var u = r.data && r.data.session && r.data.session.user; if (u) return sync(sb, u); });
    }).catch(function () {});
  };
  document.addEventListener("parcours:change", envoyer);
  document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") envoyer(); });
  envoyer();
})();
