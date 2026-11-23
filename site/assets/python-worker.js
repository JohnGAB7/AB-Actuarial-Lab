// Runs learner Python in a dedicated Worker. This improves responsiveness and removes direct DOM access,
// but a same-origin Worker is not a complete security boundary.
/* global loadPyodide */
const MAX_CODE_CHARS = 50000;
const MAX_TESTS = 30;
const MAX_TEST_CHARS = 2000;
const MAX_TOTAL_TEST_CHARS = 20000;
const MAX_ERROR_CHARS = 500;
let py = null;
let busy = false;
const sendToPage = self.postMessage.bind(self);

async function ready() {
  if (!py) {
    importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js");
    py = await loadPyodide();
    restrictRuntimeCapabilities();
  }
  return py;
}

// Defense in depth: exercises do not need network or browser storage.
// This is not a substitute for an isolated origin or a server-side sandbox.
function restrictRuntimeCapabilities() {
  const blocked = [
    "fetch", "XMLHttpRequest", "WebSocket", "EventSource", "BroadcastChannel",
    "indexedDB", "caches", "importScripts", "Worker", "SharedWorker", "WebTransport", "postMessage",
  ];
  for (const name of blocked) {
    try {
      Object.defineProperty(self, name, {
        configurable: false,
        enumerable: false,
        get: () => undefined,
      });
    } catch {
      try { self[name] = undefined; } catch {}
    }
  }
}

const messageOf = (err) => String((err && err.message) || err)
  .trim().split("\n").pop().slice(0, MAX_ERROR_CHARS);

function validateRequest(data) {
  if (!data || typeof data !== "object" || !Number.isSafeInteger(data.id) || data.id < 1) {
    throw new Error("Requête Python invalide.");
  }
  if (typeof data.code !== "string" || data.code.length > MAX_CODE_CHARS) {
    throw new Error("Code trop long (maximum " + MAX_CODE_CHARS + " caractères).");
  }
  if (!Array.isArray(data.tests) || data.tests.length < 1 || data.tests.length > MAX_TESTS) {
    throw new Error("Nombre de tests invalide (maximum " + MAX_TESTS + ").");
  }
  let total = 0;
  for (const expr of data.tests) {
    if (typeof expr !== "string" || expr.length > MAX_TEST_CHARS) {
      throw new Error("Expression de test invalide ou trop longue.");
    }
    total += expr.length;
  }
  if (total > MAX_TOTAL_TEST_CHARS) throw new Error("Ensemble des tests trop volumineux.");
}

self.onmessage = async (ev) => {
  const data = ev.data;
  const id = data && Number.isSafeInteger(data.id) ? data.id : null;
  if (busy) {
    sendToPage({ id, phase: "error", msg: "Une exécution est déjà en cours." });
    return;
  }
  try {
    validateRequest(data);
  } catch (err) {
    sendToPage({ id, phase: "error", msg: messageOf(err) });
    return;
  }

  busy = true;
  try {
    const p = await ready();
    sendToPage({ id, phase: "running" });
    const ns = p.globals.get("dict")();
    let setupErr = null;
    try { p.runPython(data.code, { globals: ns }); } catch (err) { setupErr = messageOf(err); }
    const results = data.tests.map((expr) => {
      if (setupErr) return { status: "fail", msg: setupErr };
      try {
        const value = p.runPython(expr, { globals: ns });
        const ok = value === true || (typeof value === "number" && value !== 0);
        if (value && typeof value.destroy === "function") value.destroy();
        return { status: ok ? "pass" : "fail", msg: ok ? "" : "unexpected" };
      } catch (err) {
        const msg = messageOf(err);
        return /NotImplementedError/.test(msg)
          ? { status: "todo", msg: "" }
          : { status: "fail", msg };
      }
    });
    if (ns.destroy) ns.destroy();
    sendToPage({ id, phase: "done", results });
  } catch (err) {
    sendToPage({ id, phase: "error", msg: messageOf(err) });
  } finally {
    busy = false;
  }
};
