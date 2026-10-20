// Shared helpers for the browser QA scripts: the loopback test server, installed Chrome,
// and a PASS/FAIL recorder. Uses playwright-core from qa/tooling (no browser download).
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const { spawn } = require("child_process");

const PROJECT = path.dirname(__dirname);
const DIST = path.join(PROJECT, "courses/ode/browser", "dist");
const CHROME = process.env.CHROME_PATH || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
// Python for serve_local.py: repo-local .venv, else a sibling ../ManimGL/.venv, else python on PATH.
const PY = [path.join(PROJECT, ".venv", "Scripts", "python.exe"),
            path.join(path.dirname(PROJECT), "ManimGL", ".venv", "Scripts", "python.exe")].find(p => fs.existsSync(p))
           || "python";
const { chromium } = require(path.join(__dirname, "tooling", "node_modules", "playwright-core"));

function recorder() {
  const results = [];
  function check(name, ok, detail) {
    results.push({ check: name, ok: !!ok, detail: detail === undefined ? "" : String(detail) });
    console.log((ok ? "PASS " : "FAIL ") + name + (detail !== undefined && detail !== "" ? "  [" + detail + "]" : ""));
    return !!ok;
  }
  return { results, check };
}

// Start courses/ode/browser/serve_local.py on a free loopback port and confirm its identity via the nonce.
function startServer(startPort) {
  const portFile = path.join(os.tmpdir(), "sode-qa-port-" + process.pid + "-" + Date.now() + ".txt");
  const nonce = "qa-" + process.pid + "-" + Date.now();
  const proc = spawn(PY, ["-I", path.join(PROJECT, "courses/ode/browser", "serve_local.py"), "--port", String(startPort || 8790),
                          "--port-file", portFile, "--nonce", nonce], { stdio: ["ignore", "pipe", "pipe"] });
  proc.stderr.on("data", () => {});
  proc.stdout.on("data", () => {});
  return new Promise((resolve, reject) => {
    const t0 = Date.now();
    (function poll() {
      if (fs.existsSync(portFile)) {
        const port = fs.readFileSync(portFile, "utf8").trim();
        fetch(`http://127.0.0.1:${port}/__guide_health`).then(r => r.json()).then(j => {
          if (j.app === "SecondOrderODE" && j.nonce === nonce) {
            const stop = () => {
              try { process.kill(j.pid); } catch (e) { /* gone */ }
              try { proc.kill(); } catch (e) { /* gone */ }
              try { fs.unlinkSync(portFile); } catch (e) { /* gone */ }
            };
            resolve({ base: `http://127.0.0.1:${port}/`, stop, serverPid: j.pid });
          } else reject(new Error("health mismatch " + JSON.stringify(j)));
        }).catch(() => setTimeout(poll, 150));
      } else if (Date.now() - t0 > 15000) reject(new Error("server did not start"));
      else setTimeout(poll, 150);
    })();
  });
}

function launch() {
  return chromium.launch({ executablePath: CHROME, headless: true, args: ["--autoplay-policy=no-user-gesture-required"] });
}

// Relative luminance contrast (WCAG 2) between two "rgb(a)" strings.
function contrast(fg, bg) {
  const parse = s => (s.match(/[\d.]+/g) || [0, 0, 0]).slice(0, 3).map(Number);
  const lum = c => {
    const [r, g, b] = parse(c).map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };
  const a = lum(fg), b = lum(bg);
  return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
}

module.exports = { PROJECT, DIST, CHROME, PY, recorder, startServer, launch, contrast };
