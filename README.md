# CMPE Resume Analyzer Project

This repo contains **ResumeMatch**, a resume-to-job-description alignment analyzer. The app itself lives in [`resumematch/`](resumematch/).

## Quick Start

```bash
cd resumematch
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints (default `http://localhost:8501`).

## Technology Stack

| Piece | Used for | Why |
|---|---|---|
| Python 3.10+ | Everything | Team's shared language; no build step needed |
| [Streamlit](https://streamlit.io/) | Web UI (`app.py`) | Turns a plain Python script into an interactive web app — no separate frontend/backend or HTML/JS needed |
| [PyMuPDF](https://pymupdf.readthedocs.io/) (`fitz`) | PDF text extraction | Reads text directly out of PDF bytes in memory, no temp files |
| [python-docx](https://python-docx.readthedocs.io/) | DOCX text extraction | Reads paragraphs/tables out of `.docx` XML in memory |
| `re` (standard library) | Skill & section matching | Whole-word regex matching — no external dependency, no ML |

There is **no database, no authentication, no cloud services, and no paid/external APIs**. The whole app runs as a single local process.

## Project File Structure

```
resumematch/
├── app.py                          # Streamlit UI — layout, input validation, wiring results into the dashboard
├── resume_parser.py                # Turns an uploaded PDF/DOCX into plain text (in memory, never saved to disk)
├── analyzer.py                     # All matching/scoring/recommendation logic — the "brain" of the app
├── skills.py                       # Flat list of known skill/keyword strings (the skill dictionary)
├── requirements.txt                # Python dependencies
├── README.md                       # Full project README (features, privacy, limitations)
└── sample_data/
    ├── sample_job_description.txt  # Paste-in sample job posting
    ├── sample_resume_strong.pdf/.docx  # Resume with strong overlap with the sample JD (high score)
    ├── sample_resume_weak.pdf/.docx    # Resume with little overlap (low score)
    └── README.md                   # How to use the sample files
```

**Why it's split this way:** `app.py` only handles what shows up on screen — it never computes a score itself, it just calls into `analyzer.py` and displays what comes back. `analyzer.py` has no Streamlit code in it at all, so it can be read, tested, or reused independently of the UI. `skills.py` is deliberately just a list, so adding a new skill to detect is a one-line change with no logic to touch.

## How It Works

**Does it use AI?** No. There is no machine learning model and no LLM anywhere in this app. Everything is deterministic, rule-based Python — the same resume + job description will always produce the exact same result. This was a deliberate design choice: it keeps the score fully explainable, which matters more for a resume-feedback tool than raw sophistication (see `resumematch/analyzer.py` — it's short enough to read top to bottom).

The pipeline, step by step:

1. **Extract text** (`resume_parser.py`) — the uploaded PDF/DOCX is read directly from bytes in memory (`fitz`/`python-docx`) and converted to plain text. Nothing is written to disk.

2. **Find required skills** (`analyzer.py: extract_required_skills`) — every skill string in `skills.py` (~60 entries: languages, tools, cloud platforms, methodologies) is checked against the job description text with a **whole-word regex**:
   ```python
   pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
   ```
   The lookaround assertions require the match not be preceded/followed by a word character — that's what stops `"Go"` from matching inside `"Google"`, or `"Java"` from matching inside `"JavaScript"`. Matching is case-insensitive, so `"python"` and `"PYTHON"` are treated the same.

3. **Match against the resume** (`match_skills`) — the same whole-word check runs against the resume text. Skills found in both → **matched**; skills only in the job description → **missing**.

4. **Detect resume sections** (`detect_sections`) — the resume is split into lines, and each short line (≤40 characters, to avoid false hits on prose that merely mentions "experience" mid-sentence) is checked against header patterns for Education, Experience, Skills, and Projects.

5. **Calculate the score** (`calculate_score`) — a plain weighted formula, not a model:
   ```
   score = (matched_skills / required_skills) × 75%  +  (sections_detected / 4) × 25%
   ```
   rounded to an integer 0–100. If the job description doesn't mention any skill from the dictionary, the skill portion defaults to 100% so the resume isn't penalized for something the posting never asked for.

6. **Generate recommendations** (`generate_recommendations`) — plain string templates filled in from the numbers computed in steps 2–5 (e.g. *"The job description mentions X, which was not detected in your resume"*). Nothing is invented — recommendations only ever report what was or wasn't found in the resume text, and missing skills are phrased as "highlight it **if you have it**," never "add this skill," so the tool can't be used to fabricate qualifications.

The **Job Description Alignment Score** is a transparent, explainable heuristic — **not** a prediction of hiring outcome and **not** an actual employer ATS score. The same methodology summary (steps 5–6, condensed) is also shown in-app under "How is this score calculated?" on the results dashboard.

See [`resumematch/README.md`](resumematch/README.md) for full details: features, privacy notes, and known limitations.
