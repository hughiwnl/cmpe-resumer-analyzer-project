"""Rule-based resume-to-job-description analysis.

Everything here is a plain, explainable function -- no ML, no external
services. The goal is transparency: a user should be able to read this
file and understand exactly why they got the score they did.
"""

import re

from skills import SKILLS

# Common resume section headers, mapped to a canonical display name.
# Matching is done line-by-line against these patterns (case-insensitive).
SECTION_PATTERNS = {
    "Education": r"\beducation\b",
    "Experience": r"\b(experience|work history|employment)\b",
    "Skills": r"\b(skills|technical skills|core competencies)\b",
    "Projects": r"\bprojects?\b",
}

# Scoring weights: 75% skill/keyword alignment, 25% resume completeness
# (section coverage). This mirrors the idea that matching the job's
# requested skills matters most, but a well-structured resume also helps
# a human reader (and often an ATS) find that information.
SKILL_WEIGHT = 0.75
SECTION_WEIGHT = 0.25


def _find_whole_word(term: str, text: str) -> bool:
    """Check whether `term` appears in `text` as a whole word/phrase.

    Uses word-boundary regex so short terms like "R" or "Go" don't match
    inside unrelated words (e.g. "R" should not match "Barbara", "Go"
    should not match "Google"). Matching is case-insensitive.
    """
    pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def extract_required_skills(job_description: str) -> list[str]:
    """Return the subset of the known SKILLS dictionary mentioned in the job description."""
    return [skill for skill in SKILLS if _find_whole_word(skill, job_description)]


def match_skills(resume_text: str, required_skills: list[str]) -> tuple[list[str], list[str]]:
    """Split required_skills into (matched, missing) based on resume_text."""
    matched = [s for s in required_skills if _find_whole_word(s, resume_text)]
    missing = [s for s in required_skills if s not in matched]
    return matched, missing


def detect_sections(resume_text: str) -> tuple[list[str], list[str]]:
    """Detect which common resume sections appear to be present.

    Checks each line of the resume against known section header patterns
    (this avoids false positives from the word appearing mid-sentence
    elsewhere in the document).
    """
    lines = resume_text.splitlines()
    detected = set()

    for line in lines:
        stripped = line.strip()
        # Section headers are typically short lines, not full sentences.
        if not stripped or len(stripped) > 40:
            continue
        for section_name, pattern in SECTION_PATTERNS.items():
            if re.search(pattern, stripped, flags=re.IGNORECASE):
                detected.add(section_name)

    all_sections = list(SECTION_PATTERNS.keys())
    detected_list = [s for s in all_sections if s in detected]
    missing_list = [s for s in all_sections if s not in detected]
    return detected_list, missing_list


def calculate_score(matched_skills: list[str], required_skills: list[str], detected_sections: list[str]) -> int:
    """Compute the 0-100 Job Description Alignment Score.

    Formula: 75% skill/keyword alignment + 25% resume completeness
    (section coverage out of the 4 tracked sections).
    """
    if required_skills:
        skill_ratio = len(matched_skills) / len(required_skills)
    else:
        # No recognized skills in the job description -- don't penalize
        # the resume for something the job description didn't specify.
        skill_ratio = 1.0

    section_ratio = len(detected_sections) / len(SECTION_PATTERNS)

    raw_score = (skill_ratio * SKILL_WEIGHT) + (section_ratio * SECTION_WEIGHT)
    return round(raw_score * 100)


def generate_recommendations(
    matched_skills: list[str],
    missing_skills: list[str],
    detected_sections: list[str],
    missing_sections: list[str],
) -> list[str]:
    """Generate rule-based, evidence-grounded recommendations.

    Recommendations only ever describe what was detected or not detected --
    they never suggest fabricating experience or skills.
    """
    recommendations = []

    total_required = len(matched_skills) + len(missing_skills)
    if total_required > 0:
        recommendations.append(
            f"Your resume contains {len(matched_skills)} of the {total_required} "
            f"skills/keywords identified in this job description."
        )

    if missing_skills:
        shown = missing_skills[:5]
        skill_list = ", ".join(shown)
        more = f" and {len(missing_skills) - 5} more" if len(missing_skills) > 5 else ""
        recommendations.append(
            f"The job description mentions {skill_list}{more}, which were not detected in your resume. "
            f"If you have experience with these, consider highlighting it explicitly."
        )

    for section in missing_sections:
        article = "An" if section[0] in "AEIOU" else "A"
        recommendations.append(
            f"{article} '{section}' section was not clearly detected. If you have relevant {section.lower()} "
            f"to include, adding a clearly labeled section may help both readers and ATS systems find it."
        )

    if matched_skills:
        highlight = matched_skills[0]
        recommendations.append(
            f"Consider making your experience with {highlight} more prominent (e.g. in a summary "
            f"or near the top of your Experience section), since it's a direct match with this job."
        )

    if not missing_skills and not missing_sections:
        recommendations.append(
            "Your resume covers all identified skills and common sections for this job description. "
            "Review formatting and clarity as a final pass."
        )

    return recommendations[:5]
