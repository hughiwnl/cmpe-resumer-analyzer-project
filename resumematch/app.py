"""ResumeMatch -- Resume-to-Job Description Analyzer.

A Streamlit prototype that compares an uploaded resume against a pasted
job description and produces a transparent, rule-based alignment score.
"""

import streamlit as st

from analyzer import (
    calculate_score,
    detect_sections,
    extract_required_skills,
    generate_recommendations,
    match_skills,
)
from resume_parser import extract_text

st.set_page_config(page_title="ResumeMatch", page_icon="📄", layout="centered")

st.title("📄 ResumeMatch")
st.caption("Resume-to-Job Description Alignment Analyzer (Prototype)")

st.info(
    "🔒 **Privacy note:** Your resume is processed in memory only for this session. "
    "It is never permanently saved, written to disk, or logged.",
    icon="🔒",
)

# --- Step 1: Resume upload ---
st.header("1. Upload your resume")
uploaded_file = st.file_uploader("Upload a PDF or DOCX resume", type=["pdf", "docx"])

resume_text = ""
parse_error = None

if uploaded_file is not None:
    resume_text, parse_error = extract_text(uploaded_file)
    if parse_error:
        st.error(f"❌ {parse_error}")
    else:
        word_count = len(resume_text.split())
        st.success(f"✅ Extracted text from **{uploaded_file.name}** ({word_count} words detected).")

# --- Step 2: Job description input ---
st.header("2. Paste the job description")
job_description = st.text_area(
    "Job description",
    height=250,
    placeholder="Paste the full job description here...",
    label_visibility="collapsed",
)

# --- Step 3: Analyze ---
st.header("3. Analyze")
resume_ready = bool(resume_text) and not parse_error
jd_ready = bool(job_description.strip())

if not resume_ready:
    st.warning("Upload a resume to continue.")
if not jd_ready:
    st.warning("Paste a job description to continue.")

analyze_clicked = st.button("Analyze Resume", type="primary", disabled=not (resume_ready and jd_ready))

if analyze_clicked:
    required_skills = extract_required_skills(job_description)
    matched_skills, missing_skills = match_skills(resume_text, required_skills)
    detected_sections, missing_sections = detect_sections(resume_text)
    score = calculate_score(matched_skills, required_skills, detected_sections)
    recommendations = generate_recommendations(
        matched_skills, missing_skills, detected_sections, missing_sections
    )

    st.divider()
    st.header("Results")

    # --- Overall score ---
    st.subheader("Job Description Alignment Score")
    st.markdown(f"<h1 style='text-align:center; font-size:64px;'>{score} / 100</h1>", unsafe_allow_html=True)

    with st.expander("How is this score calculated?"):
        st.markdown(
            f"""
This is a **heuristic alignment score**, not a prediction of whether you'll be hired
and not an employer's actual ATS score. It measures textual overlap between your
resume and this specific job description:

- **75% Skill/Keyword Alignment** — the fraction of skills mentioned in the job
  description that were also found in your resume
  ({len(matched_skills)} of {len(required_skills)} matched).
- **25% Resume Completeness** — how many of 4 common resume sections
  (Education, Experience, Skills, Projects) were detected
  ({len(detected_sections)} of 4 detected).
"""
        )

    # --- Summary metrics ---
    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Matched Skills", len(matched_skills))
    col2.metric("Missing Skills", len(missing_skills))
    col3.metric("Sections Detected", f"{len(detected_sections)}/4")

    # --- Matched / missing skills ---
    st.subheader("Skill Alignment")
    skill_col1, skill_col2 = st.columns(2)
    with skill_col1:
        st.markdown("**✅ Matched Skills**")
        if matched_skills:
            for skill in matched_skills:
                st.markdown(f"- {skill}")
        else:
            st.markdown("_No matches found._")
    with skill_col2:
        st.markdown("**⚠️ Missing Skills**")
        if missing_skills:
            for skill in missing_skills:
                st.markdown(f"- {skill}")
        else:
            st.markdown("_None -- all identified skills were found._")

    # --- Resume sections ---
    st.subheader("Resume Sections")
    section_col1, section_col2 = st.columns(2)
    with section_col1:
        st.markdown("**✅ Detected**")
        if detected_sections:
            for section in detected_sections:
                st.markdown(f"- {section}")
        else:
            st.markdown("_None detected._")
    with section_col2:
        st.markdown("**⚠️ Not Detected**")
        if missing_sections:
            for section in missing_sections:
                st.markdown(f"- {section}")
        else:
            st.markdown("_None -- all common sections detected._")

    # --- Recommendations ---
    st.subheader("Recommendations")
    for rec in recommendations:
        st.markdown(f"- {rec}")

    st.divider()
    st.caption(
        "This analysis measures textual alignment with the supplied job description. "
        "It does not predict hiring decisions."
    )
