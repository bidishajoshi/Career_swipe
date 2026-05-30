import os
import re

from utils.ats import calculate_ats_score
from utils.tfidf import extract_skills, match_resume_to_job, parse_resume


STATUS_LABELS = {
    "pending": "Pending",
    "shortlisted": "Shortlisted",
    "interview": "Interview",
    "accepted": "Hired",
    "hired": "Hired",
    "rejected": "Rejected",
}

STATUS_CLASSES = {
    "pending": "pending",
    "shortlisted": "shortlisted",
    "interview": "interview",
    "accepted": "hired",
    "hired": "hired",
    "rejected": "rejected",
}


def normalize_static_path(path):
    """Return a path suitable for url_for('static', filename=...)."""
    if not path:
        return ""
    return path.replace("\\", "/").replace("static/", "").lstrip("/")


def existing_static_path(path):
    """Return a static-relative path only when the asset exists on disk."""
    normalized = normalize_static_path(path)
    if not normalized:
        return ""
    static_root = os.path.abspath("static")
    asset_path = os.path.abspath(os.path.join(static_root, normalized))
    if asset_path.startswith(static_root) and os.path.exists(asset_path):
        return normalized
    return ""


def _score_value(value):
    try:
        return max(0, min(100, int(round(float(value or 0)))))
    except (TypeError, ValueError):
        return 0


def _seeker_text(seeker, resume_text):
    return " ".join([
        resume_text or "",
        getattr(seeker, "first_name", "") or "",
        getattr(seeker, "last_name", "") or "",
        getattr(seeker, "email", "") or "",
        getattr(seeker, "phone", "") or "",
        getattr(seeker, "education", "") or "",
        getattr(seeker, "experience", "") or "",
        getattr(seeker, "skills", "") or "",
        getattr(seeker, "certifications", "") or "",
        getattr(seeker, "career_field", "") or "",
        getattr(seeker, "desired_roles", "") or "",
    ])


def _resume_text(seeker):
    active_resume = None
    try:
        active_resume = max(
            [resume for resume in getattr(seeker, "resumes", []) if resume.is_active],
            key=lambda resume: resume.created_at,
            default=None,
        )
    except Exception:
        active_resume = None

    if active_resume and active_resume.extracted_text:
        return active_resume.extracted_text

    resume_path = getattr(seeker, "resume_path", "") or ""
    if resume_path and os.path.exists(resume_path):
        return parse_resume(resume_path)

    return ""


def _job_text(job):
    return " ".join([
        getattr(job, "title", "") or "",
        getattr(job, "description", "") or "",
        getattr(job, "required_skills", "") or "",
        getattr(job, "tags", "") or "",
        getattr(job, "experience_level", "") or "",
        getattr(job, "experience_required", "") or "",
    ])


def split_skills(raw_skills, fallback_text=""):
    """Split profile skills into display badges, including old un-delimited data."""
    combined = " ".join([raw_skills or "", fallback_text or ""]).strip()
    if not combined:
        return []

    if re.search(r"[,;|\n/]", raw_skills or ""):
        candidates = re.split(r"[,;|\n/]+", raw_skills or "")
    else:
        candidates = extract_skills(combined, raw_skills or "")

    seen = set()
    skills = []
    for skill in candidates:
        cleaned = re.sub(r"\s+", " ", str(skill or "")).strip(" -.")
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        skills.append(cleaned.title() if cleaned.islower() else cleaned)
    return skills


def build_applicant_cards(swipes):
    applicants = []

    for swipe in swipes:
        seeker = getattr(swipe, "seeker", None)
        job = getattr(swipe, "job_listing", None)
        if not seeker or not job:
            continue

        resume_text = _resume_text(seeker)
        profile_text = _seeker_text(seeker, resume_text)
        job_text = _job_text(job)

        match_score = _score_value(getattr(swipe, "match_score", 0))
        ats_score = _score_value(getattr(swipe, "ats_score", 0))

        if match_score == 0 and profile_text.strip() and job_text.strip():
            match_score = _score_value(match_resume_to_job(profile_text, job_text))
        if ats_score == 0 and profile_text.strip() and job_text.strip():
            ats_score = _score_value(calculate_ats_score(profile_text, job_text).get("score", 0))

        first_name = (getattr(seeker, "first_name", "") or "Unknown").strip()
        last_name = (getattr(seeker, "last_name", "") or "").strip()
        status_key = (getattr(swipe, "status", "") or "pending").lower()
        skills = split_skills(getattr(seeker, "skills", "") or "", profile_text)

        applicants.append({
            "seeker_id": seeker.id,
            "first_name": first_name,
            "last_name": last_name,
            "full_name": f"{first_name} {last_name}".strip(),
            "initials": f"{first_name[:1]}{last_name[:1]}".upper() or "CS",
            "email": getattr(seeker, "email", "") or "No email provided",
            "skills": skills,
            "skill_count": len(skills),
            "resume_path": normalize_static_path(getattr(seeker, "resume_path", "") or ""),
            "job_id": job.id,
            "job_title": getattr(job, "title", "") or "Untitled position",
            "applied_at": getattr(swipe, "created_at", None) or getattr(swipe, "applied_at", None),
            "status": status_key,
            "status_label": STATUS_LABELS.get(status_key, status_key.replace("_", " ").title()),
            "status_class": STATUS_CLASSES.get(status_key, "pending"),
            "swipe_id": swipe.id,
            "match_score": match_score,
            "ats_score": ats_score,
        })

    return applicants
