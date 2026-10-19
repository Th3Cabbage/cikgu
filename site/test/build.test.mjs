// Build/registry invariants for the unified site.  Run: node --test site/test/
import { test } from "node:test";
import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { build, loadCatalog, inspectPackage, injectIndex, listOutput, REPO, SITE } from "../build.mjs";

const tmpBase = fs.realpathSync(os.tmpdir());
const tmp = fs.realpathSync(fs.mkdtempSync(path.join(tmpBase, "cikgu-site-test-")));
assert.equal(path.dirname(tmp), tmpBase, "test cleanup must stay inside the temporary directory");
assert.ok(path.basename(tmp).startsWith("cikgu-site-test-"), "test cleanup must target its owned directory");
const hash = (f) => crypto.createHash("sha256").update(fs.readFileSync(f)).digest("hex");
const first = build({ out: path.join(tmp, "a"), quiet: true });
const second = build({ out: path.join(tmp, "b"), quiet: true });
process.on("exit", () => fs.rmSync(tmp, { recursive: true, force: true }));

function packages(cat) {
  const out = [];
  for (const c of cat.courses) {
    if (c.kind === "single") out.push({ src: c.sourceAbs, dest: c.path });
    else for (const l of c.lectures) out.push({ src: l.sourceAbs, dest: c.path + "/" + l.slug });
  }
  return out;
}

test("rebuild is deterministic", () => {
  assert.deepEqual(first.files, second.files);
  for (const f of first.files) assert.equal(hash(path.join(first.out, f)), hash(path.join(second.out, f)), f);
});

test("package files are copied byte-for-byte; only index.html is integrated", () => {
  for (const p of packages(first.catalog)) {
    const files = listOutput(p.src);
    for (const f of files) {
      const out = path.join(first.out, p.dest, f);
      assert.ok(fs.existsSync(out), "missing " + p.dest + "/" + f);
      if (f !== "index.html") assert.equal(hash(out), hash(path.join(p.src, f)), p.dest + "/" + f);
    }
    // Removing the injected markup gives back the original page exactly.
    const built = fs.readFileSync(path.join(first.out, p.dest, "index.html"), "utf8");
    const restored = built
      .replace(/\n<script>\(function\(l\)\{[^\n]*<\/script>/, "")
      .replace(' class="cikgu-site"', "")
      .replace(/<link rel="stylesheet" href="[./]*site-assets\/coursebar\.css">\n/, "")
      .replace(/\n<nav class="cikgu-cb"[^\n]*<\/nav>/, "")
      .replace(/<script src="[./]*site-assets\/coursebar\.js"><\/script>\n/, "");
    assert.equal(restored, fs.readFileSync(path.join(p.src, "index.html"), "utf8"), p.dest);
  }
});

test("output holds only public web assets", () => {
  const allowed = /\.(html|css|js|json|mp4|jpg|png|svg|ttf|woff2?|txt)$|\/LICENSE$|\/api\/status$/;
  for (const f of first.files) {
    assert.match(f, allowed, f);
    assert.ok(!f.split("/").some((s) => s.startsWith(".")), f);
  }
  assert.ok(!first.files.some((f) => /\.(pdf|py|ps1|log|env|pem|key|md)$/i.test(f)));
  const statuses = first.files.filter((f) => f.endsWith("/api/status"));
  assert.equal(statuses.length, 3);
  for (const f of statuses) {
    const s = JSON.parse(fs.readFileSync(path.join(first.out, f), "utf8"));
    assert.equal(s.tutor.configured, false);
    assert.equal(s.book.available, false);
  }
});

test("every generated link and asset reference resolves inside the site", () => {
  const pages = first.files.filter((f) => f.endsWith(".html"));
  let checked = 0;
  for (const page of pages) {
    const html = fs.readFileSync(path.join(first.out, page), "utf8");
    for (const m of html.matchAll(/\s(?:href|src)="([^"]+)"/g)) {
      const ref = m[1];
      if (/^(https?:|mailto:|#|data:)/.test(ref)) continue;
      const target = path.join(path.dirname(path.join(first.out, page)), ref.split("#")[0]);
      const ok = ref.split("#")[0].endsWith("/") ? fs.existsSync(path.join(target, "index.html")) : fs.existsSync(target);
      assert.ok(ok, `${page}: ${ref}`);
      assert.ok(path.resolve(target).startsWith(path.resolve(first.out)), `${page}: ${ref} leaves the site`);
      checked++;
    }
  }
  assert.ok(checked > 50);
});

test("lecture order, counts and prev/next links follow the catalog", () => {
  const series = first.catalog.courses.find((c) => c.kind === "series");
  const course = fs.readFileSync(path.join(first.out, series.path, "index.html"), "utf8");
  const order = [...course.matchAll(/data-lecture="([^"]+)"/g)].map((m) => m[1]);
  assert.deepEqual(order, series.lectures.map((l) => l.slug));
  series.lectures.forEach((l, i) => {
    const p = first.info[series.id + "/" + l.slug];
    assert.ok(course.includes(`${p.sequences} animations, ${p.steps} steps`), l.slug + " counts");
    const html = fs.readFileSync(path.join(first.out, series.path, l.slug, "index.html"), "utf8");
    assert.equal((html.match(/aria-current="page"/g) || []).length, 1);
    assert.ok(html.includes(`href="../${l.slug}/" aria-current="page"`));
    const prev = series.lectures[i - 1], next = series.lectures[i + 1];
    assert.equal(html.includes('rel="prev"'), !!prev);
    assert.equal(html.includes('rel="next"'), !!next);
    if (next) assert.ok(html.includes(`href="../${next.slug}/" rel="next"`));
  });
});

test("registry is validated against the packages", () => {
  const cat = JSON.parse(fs.readFileSync(path.join(SITE, "catalog.json"), "utf8"));
  const tryCat = (mutate) => {
    const c = structuredClone(cat);
    mutate(c);
    const f = path.join(tmp, "catalog-" + crypto.randomUUID() + ".json");
    fs.writeFileSync(f, JSON.stringify(c));
    return () => loadCatalog(f, REPO);
  };
  const series = (c) => c.courses.find((x) => x.kind === "series");
  assert.throws(tryCat((c) => { series(c).lectures[1].storeKey = series(c).lectures[0].storeKey; }), /used twice/);
  assert.throws(tryCat((c) => { series(c).lectures[0].source = "../outside/dist"; }), /repository-relative/);
  assert.throws(tryCat((c) => { series(c).lectures[0].source = "sources"; }), /has no index.html/);
  assert.throws(tryCat((c) => { series(c).lectures[0].slug = "Bad Slug"; }), /slug/);
  assert.throws(tryCat((c) => { series(c).path = "site-assets"; }), /reserved/);
  const lec = series(first.catalog).lectures[0];
  assert.throws(() => inspectPackage(lec.sourceAbs, { ...lec, storeKey: "renamed-v2" }), /storage key/);
  assert.throws(() => inspectPackage(lec.sourceAbs, { ...lec, statusApp: "SomethingElse" }), /app identity/);
});

test("output directory safety and injection anchors", () => {
  assert.throws(() => build({ out: first.out, quiet: true }), /Refusing to write into existing/);
  assert.throws(() => build({ out: path.join(REPO, "not-site-dist"), quiet: true }), /outside the repository/);
  assert.ok(!fs.existsSync(path.join(REPO, "not-site-dist")));
  assert.throws(() => injectIndex("<html><head></head><body></body></html>", { bar: "", assets: "" }), /skip link/);
});
