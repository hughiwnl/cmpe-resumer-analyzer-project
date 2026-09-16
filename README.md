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

See [`resumematch/README.md`](resumematch/README.md) for full details: features, how the alignment score works, privacy notes, and known limitations.
