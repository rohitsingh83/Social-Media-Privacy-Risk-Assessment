# Local Execution — Step by Step

The frontend is served by the Flask app, so you do **not** need a second server or a Node build step.

## Step 1 — Open the project

If you downloaded or cloned the repository:

```bash
cd Social-Media-Privacy-Risk-Assessment
```

The project folders and files are already created. Confirm with `ls` (macOS/Linux) or `dir` (Windows).

## Step 2 — Create a virtual environment

```bash
python -m venv .venv
```

## Step 3 — Activate and install dependencies

macOS/Linux:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Step 4 — Generate the synthetic dataset

```bash
python data/generate_dataset.py --count 1200 --seed 20251006
```

The script writes `data/social_media_privacy_assessments.csv` with fictional IDs and no personal content.

## Step 5 — Start the backend

```bash
python -m backend.app
```

Keep this terminal open. Flask serves both `/api/...` and the frontend from the same origin at port 8000. To use another port, set `PORT` before starting. To change the database path, set `DATABASE_PATH`. `.env.example` is a reference file; it is not loaded automatically.

## Step 6 — Start / open the frontend

There is no separate frontend process. Open this URL in the browser:

```text
http://127.0.0.1:8000
```

The CSS, JavaScript, SVG charts, and API are served locally. No CDN or external font is needed.

## Step 7 — Start the assessment

Select **Start my assessment** or **Run a scan**. The questionnaire contains ten sections and 56 questions. Answers default to **Not sure** until changed; review each answer. The safe fictional shortcut is **Load fictional demo profile**.

## Step 8 — Complete the questionnaire

For each setting/habit choose the closest fixed response. Do not type or paste actual phone numbers, emails, birthdays, passwords, home addresses, exact locations, account names, photos, links, or private messages. Use “Not sure” if you cannot confirm a setting, then review that setting in the platform directly.

## Step 9 — Generate the score

On the final section, choose **Generate my readout**. The API validates the fixed-choice payload, scores it in memory, saves derived results only, and displays the overall score and risk level.

## Step 10 — Review category analysis

Scroll through the category radar and bars, findings, and recommendations. A high score means higher assessed exposure in this educational model; it is not a compromise prediction.

## Step 11 — Run the improvement simulation

Select one or more suggested changes in the **What-if simulator** and choose **Simulate selected changes**. The app computes a temporary scenario only. It does not change social-platform settings and does not save simulated answers.

## Step 12 — Generate a report and checklist

Choose **Open report**; the new tab has **Print / Save as PDF**. The Privacy by Design section has a text download for the printable checklist. When finished, choose **Delete saved result** to remove the derived assessment and related database rows.

## Step 13 — Run automated tests

In a second terminal, from the project root:

```bash
python -m pytest -q
```

Expected latest result at build time: `57 passed`. Re-run after changes; the test matrix records the currently observed results.
