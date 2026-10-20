# Cikgu study site (all courses in one website)

One static website that gathers the study packages:

| URL path | Content | Copied from |
|---|---|---|
| `/` | Library home: two courses | generated |
| `/ode/` | Second-Order Linear Differential Equations | `courses/ode/browser/dist` |
| `/controls/` | Control Bootcamp course page: lectures in order, counts, saved progress | generated |
| `/controls/overview/` | Lecture 1, Overview | `courses/controls/overview/dist` |
| `/controls/linear-systems/` | Lecture 2, Linear Systems | `courses/controls/linear-systems/dist` |
| `/controls/stability-eigenvalues/` | Lecture 3, Stability and Eigenvalues | `courses/controls/stability-eigenvalues/dist` |
| `/controls/linearization/` | Lecture 4, Linearizing Around a Fixed Point | `courses/controls/linearization/dist` |
| `/controls/controllability/` | Lecture 5, Controllability | `courses/controls/controllability/dist` |

Each lecture keeps its own player, notes, worked examples, explorer, quiz, source links and routes
(`#s1`, `#explorer`, `#quiz`, `#sources`; the ODE guide uses `#watch`, `#lesson-N`, ...).
A course bar above each lecture links to the library, the course page, every lecture in order and the
previous/next lecture, in the same tab. Its links are plain HTML and work without JavaScript.

## Run it locally

```powershell
.\launch_study.ps1                # builds site\dist, serves http://127.0.0.1:8800/, opens the browser
.\launch_study.ps1 -Port 9200     # another starting port (the next free one is used)
.\launch_study.ps1 -NoBrowser     # serve and print the URL only
.\launch_study.ps1 -SkipBuild     # serve the existing site\dist
```

The launcher needs Node.js 18+ for the build (no `npm install`) and Python 3 (standard library) for
`site/server.py`. It confirms the server through `/__site_health` and a per-launch nonce; Ctrl+C or
closing the window stops it. Manual equivalent: `node site/build.mjs` then
`python -I site/server.py --port 8800`. Do not open `site/dist/index.html` from disk.

## Publish on Netlify

`netlify.toml` at the repository root holds the settings. In the Netlify UI:

1. **Add new site → Import an existing project → GitHub**, choose `Th3Cabbage/cikgu`, branch `main`.
2. Build settings (Netlify reads these from `netlify.toml`; if the form asks, enter exactly):
   - **Base directory:** `site`
   - **Build command:** `node build.mjs`
   - **Publish directory:** `dist`, relative to the base directory (Netlify may display it as `site/dist`)
   - Functions directory: leave empty. No environment variables are needed.
3. Deploy. Pushes to `main` redeploy automatically.

The build only copies the committed viewing assets (about 46.5 MB, 839 output files), so it needs no Python, ManimGL,
LaTeX or package install; `base = "site"` also stops Netlify from installing the repository's
Python requirements. There is no catch-all rewrite: every page is a real directory, and course
routes are `#hashes`. A small script in each lecture page adds the trailing slash if someone opens
`/controls/overview` without it, so relative files still load.

## What the static site does not do

- **No Ask GPT chat.** The lectures' optional GPT tutor needs the single-lecture Python server holding an
  `OPENAI_API_KEY`. The site publishes a static `api/status` for each lecture saying chat is not
  configured; the panel explains that chat is not available on this site and never sends requests.
  Use `launch_control.ps1`, `launch_linear_systems.ps1` or `launch_stability_eigenvalues.ps1` with a
  key for live chat; `launch_linearization.ps1` does the same for lecture 4.
  Do not add a key or a hosted chat proxy to this site without a separate design.
- **No local PDF links.** Book references open the online copy. The source PDF, lecture downloads and
  research caches are never copied (the build fails on any file that is not a public web asset).
- **Progress is per website.** Each lecture keeps its original browser storage key
  (`ctl-overview-v1`, `linear-systems-v1`, `stability-eigenvalues-v1`, `linearization-v1`; ODE saves only its theme in
  `sode-theme`), so progress carries across lectures, the course page and reloads on the same site.
  Browsers keep storage per origin: `127.0.0.1:8800`, the standalone launcher ports and the Netlify
  domain each have separate progress. Nothing is migrated automatically.

## How the build works

`build.mjs` (Node built-ins only) reads [`catalog.json`](catalog.json), checks it, and writes
`site/dist`, which is ignored by Git and deleted only after its resolved path is confirmed:

- Copies every package `dist/` file byte-for-byte. Only `index.html` is changed: it gets the course
  bar markup, `site-assets/coursebar.css|js`, a `cikgu-site` class and the trailing-slash guard.
  The original package folders are not modified, so the standalone launchers keep working.
- Checks each package: the registry's storage key and server identity appear in its code, and every
  clip/still named in its manifest exists. Hidden files, symlinks and non-web files stop the build.
- Generates the home and course pages. Counts come from each `course.json` and animation manifest.
- Source files: `src/site.css` and `src/library.js` (library pages; the course page reads saved
  lecture progress read-only), `src/coursebar.css` and `src/coursebar.js` (lecture integration),
  `src/favicon.svg`.

`coursebar.js` keeps the lecture's sticky side menu and tutor panel clear of the non-sticky bar by
setting `--cikgu-cb-vis` to the visible bar height.

## Add the next lecture

1. Build the package with the normal workflow (`/build-study-package`) and commit its `dist/`.
2. Append it to the Control Bootcamp `lectures` list in `catalog.json`:
   `slug` (URL folder), `source` (`courses/controls/<package>/dist`), `title`, a one-sentence student-facing
   `description`, its `storeKey` (the `STORE_KEY` in its `app.js`) and `statusApp` (the `app` name its
   server reports). The order of the list is the lecture order.
3. Run `node site/build.mjs`, `node --test site/test/build.test.mjs` and `node qa/site_browser_qa.js`.
   The tests use the catalog, so the next lecture is included; update hard-coded expectations such as
   the number of static `api/status` files.

A new course is a new `courses` entry (`kind: "single"` for one package, `"series"` for lectures).

## Checks

```powershell
node --test site/test/build.test.mjs   # build/registry invariants (7 tests, ~10 s)
node site/build.mjs
node qa/site_browser_qa.js             # HTTP + Chrome checks; screenshots in qa/screenshots/site/
```

The browser check needs `npm --prefix qa/tooling ci` once and installed Chrome (`CHROME_PATH` to override).
See [REVIEW.md](REVIEW.md) for the delivery checks and limitations.
