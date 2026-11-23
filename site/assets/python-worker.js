// Runs the learner's Python (Pyodide) in a Web Worker: no DOM, no localStorage, so no access to the account session.
// The page can stop it at any time (worker.terminate()), which also ends infinite loops.
/* global loadPyodide */
let py = null;

async function ready() {
  if (!py) {
    importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js");
    py = await loadPyodide();
  }
  return py;
}

const lastLine = (err) => String((err && err.message) || err).trim().split("\n").pop();

self.onmessage = async (ev) => {
  const { id, code, tests } = ev.data;
  try {
    const p = await ready();
    self.postMessage({ id, phase: "running" });
    const ns = p.globals.get("dict")();
    let setupErr = null;
    try { p.runPython(code, { globals: ns }); } catch (err) { setupErr = lastLine(err); }
    const results = tests.map((expr) => {
      if (setupErr) return { status: "fail", msg: setupErr };
      try {
        const v = p.runPython(expr, { globals: ns });
        const ok = v === true || (typeof v === "number" && v !== 0);
        if (v && typeof v.destroy === "function") v.destroy();
        return { status: ok ? "pass" : "fail", msg: ok ? "" : "unexpected" };
      } catch (err) {
        const m = lastLine(err);
        return /NotImplementedError/.test(m) ? { status: "todo", msg: "" } : { status: "fail", msg: m };
      }
    });
    if (ns.destroy) ns.destroy();
    self.postMessage({ id, phase: "done", results });
  } catch (err) {
    self.postMessage({ id, phase: "error", msg: lastLine(err) });
  }
};
