// Shared helpers for the Control Bootcamp browser checks: start control/server.py on a free
// loopback port (identity confirmed by nonce), launch installed Chrome via playwright-core from
// qa/tooling, and record PASS/FAIL lines.
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const { spawn } = require("child_process");

const PROJECT = path.dirname(__dirname);
const DIST = path.join(PROJECT, "control", "dist");
const CHROME = process.env.CHROME_PATH || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const PY = [path.join(PROJECT, ".venv", "Scripts", "python.exe")].find(p => fs.existsSync(p)) || "python";
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

// env: extra environment for the server (e.g. a mock OPENAI_BASE_URL). The parent's
// OPENAI_* variables are removed unless given explicitly, so checks never use a real key.
function startServer(startPort, env) {
  const portFile = path.join(os.tmpdir(), "ctl-qa-port-" + process.pid + "-" + Date.now() + ".txt");
  const nonce = "qa-" + process.pid + "-" + Date.now();
  const childEnv = Object.assign({}, process.env);
  Object.keys(childEnv).forEach(k => { if (/^OPENAI_/.test(k)) delete childEnv[k]; });
  Object.assign(childEnv, env || {});
  const proc = spawn(PY, ["-I", path.join(PROJECT, "control", "server.py"), "--port", String(startPort || 8790),
                          "--port-file", portFile, "--nonce", nonce], { stdio: ["ignore", "pipe", "pipe"], env: childEnv });
  let log = "";
  proc.stderr.on("data", d => { log += d; });
  proc.stdout.on("data", d => { log += d; });
  return new Promise((resolve, reject) => {
    const t0 = Date.now();
    (function poll() {
      if (fs.existsSync(portFile)) {
        const port = fs.readFileSync(portFile, "utf8").trim();
        fetch(`http://127.0.0.1:${port}/__control_health`).then(r => r.json()).then(j => {
          if (j.app === "ControlBootcamp" && j.nonce === nonce) {
            const stop = () => {
              try { process.kill(j.pid); } catch (e) { /* gone */ }
              try { proc.kill(); } catch (e) { /* gone */ }
              try { fs.unlinkSync(portFile); } catch (e) { /* gone */ }
            };
            resolve({ base: `http://127.0.0.1:${port}/`, port: +port, stop, serverPid: j.pid, log: () => log });
          } else reject(new Error("health mismatch " + JSON.stringify(j)));
        }).catch(() => setTimeout(poll, 150));
      } else if (Date.now() - t0 > 15000) reject(new Error("server did not start\n" + log));
      else setTimeout(poll, 150);
    })();
  });
}

function launch() {
  return chromium.launch({ executablePath: CHROME, headless: true, args: ["--autoplay-policy=no-user-gesture-required"] });
}

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
