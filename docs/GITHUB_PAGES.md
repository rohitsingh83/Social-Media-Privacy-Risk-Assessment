# GitHub Pages Deployment — Static, Backend-Free Site

The GitHub Pages version is in this `docs/` directory. It is an independent static website: GitHub Pages serves the HTML, CSS, JavaScript, and small JSON data files. The scoring engine, questionnaire, findings, recommendations, report generation, checklist download, and improvement simulator run entirely in the visitor's browser. It does not call Flask, SQLite, localhost, a remote API, a CDN, or an external font service.

The static build stores **nothing**. Assessment answers and results remain in the current browser tab's memory; refreshing or closing the tab clears them. The cohort dashboard reads a checked-in JSON aggregate generated from the fictional CSV. Do not put private or real profile data into the static data directory.

## 1. Prepare the repository

Create a GitHub repository named `Social-Media-Privacy-Risk-Assessment` (or use your own repo name). From the project root:

```bash
git init
git add .
git commit -m "Build privacy assessment and GitHub Pages site"
git branch -M main
git remote add origin https://github.com/<YOUR-USERNAME>/Social-Media-Privacy-Risk-Assessment.git
git push -u origin main
```

If the repository already exists locally, keep its history and use its existing `origin` instead of running `git init` again.

## 2. Enable GitHub Pages

1. Open the repository on GitHub.
2. Select **Settings → Pages**.
3. Under **Build and deployment**, choose **Deploy from a branch**.
4. Select branch **main** and folder **/docs**.
5. Save. GitHub Actions will publish the static site; wait for the Pages deployment to complete.

For a normal project repository, the address will be similar to:

```text
https://<YOUR-USERNAME>.github.io/Social-Media-Privacy-Risk-Assessment/
```

For a repository named exactly `<YOUR-USERNAME>.github.io`, GitHub uses the account's root site URL instead. Use the URL GitHub displays under Settings → Pages.

## 3. Local test before publishing

`file://` may block browser JSON loading. Run a local static web server from the repository root:

```bash
python -m http.server 8001 --bind 0.0.0.0 --directory docs
```

Open `http://127.0.0.1:8001/`. This is the same backend-free Pages build. Try the fictional demo, generate the score, choose simulator changes, open the report, and download the checklist.

## 4. Regenerate the static bundle after changing content

The Pages data is generated from the Python questionnaire, safe improvement allow-list, reporting checklist, and synthetic CSV. After changing those sources, run:

```bash
python scripts/build_pages.py
python -m pytest -q
git add docs
git commit -m "Update static GitHub Pages build"
git push
```

The checked-in `docs/index.html`, `docs/assets/`, and `docs/data/` are already generated, so GitHub Pages does **not** need Python, Flask, Node, a database, or a build workflow to serve them. `.nojekyll` is included; all asset and JSON URLs are relative so the site works beneath the repository-name path.

## 5. Pages versus Flask mode

| Capability | GitHub Pages (`docs/`) | Local Flask (`python -m backend.app`) |
|---|---|---|
| Hosting | Static GitHub Pages | Local Python server |
| Scoring | In browser | Flask/Python API |
| Assessment persistence | None; current tab only | Derived-only SQLite results |
| Demo analytics | Checked-in synthetic JSON | Synthetic CSV aggregates |
| Report | Browser-generated HTML blob | Printable HTML route |
| Internet/platform access | None | None |
| Setup | Push repo and enable Pages | Install Python requirements |

Both modes use the same questionnaire and scoring rules. The Pages version is the simplest choice for a public portfolio demo because it requires no backend service and does not retain visitor assessments. Do not add a third-party tracker, profile scanner, or real-user dataset when publishing.
