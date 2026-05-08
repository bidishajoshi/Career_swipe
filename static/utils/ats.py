import re
from .tfidf import clean_text

def calculate_ats_score(resume_text: str, job_text: str) -> dict:
    """
    Evaluates a resume for ATS compatibility.
    Returns a dict with score and findings.
    """
    if not resume_text:
        return {"score": 0, "findings": ["Resume text could not be extracted."], "breakdown": {}}

    score = 0
    findings = []
    breakdown = {}

    # 1. Check for Contact Info (Weight: 15)
    contact_patterns = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "phone": r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
        "linkedin": r"linkedin\.com/in/[a-zA-Z0-9_-]+"
    }
    
    contact_score = 0
    if re.search(contact_patterns["email"], resume_text): contact_score += 5
    else: findings.append("Missing email address")
    
    if re.search(contact_patterns["phone"], resume_text): contact_score += 5
    else: findings.append("Missing phone number")
    
    if re.search(contact_patterns["linkedin"], resume_text, re.I): contact_score += 5
    else: findings.append("LinkedIn profile not detected")
    
    score += contact_score
    breakdown["contact_info"] = contact_score

    # 2. Section Headings (Weight: 20)
    sections = ["Experience", "Education", "Skills", "Projects", "Summary"]
    section_score = 0
    for s in sections:
        if re.search(rf"\b{s}\b", resume_text, re.I):
            section_score += 4
    
    if section_score < 12:
        findings.append("Resume lacks standard section headings (Experience, Education, etc.)")
    
    score += section_score
    breakdown["structure"] = section_score

    # 3. Keyword & Skill Gap Matching (Weight: 50)
    from .tfidf import clean_text
    resume_tokens = set(clean_text(resume_text))
    job_tokens = set(clean_text(job_text))
    
    matched_skills = resume_tokens.intersection(job_tokens)
    missing_skills = job_tokens.difference(resume_tokens)
    
    keyword_match_ratio = len(matched_skills) / len(job_tokens) if job_tokens else 0
    keyword_score = round(keyword_match_ratio * 50)
    
    if len(missing_skills) > 5:
        findings.append(f"Highly relevant keywords missing: {', '.join(list(missing_skills)[:5])}")
    
    score += keyword_score
    breakdown["keywords"] = keyword_score
    breakdown["matched_skills"] = list(matched_skills)[:10]
    breakdown["missing_skills"] = list(missing_skills)[:10]

    # 4. Formatting & Length (Weight: 15)
    # ... (rest of formatting logic)
    words = resume_text.split()
    length_score = 0
    if 200 <= len(words) <= 1500: length_score = 15
    else: length_score = 5; findings.append("Resume length is suboptimal for ATS.")
        
    score += length_score
    breakdown["formatting"] = length_score

    return {
        "score": min(100, score),
        "findings": findings if findings else ["Excellent ATS compatibility!"],
        "breakdown": breakdown,
        "missing_skills": list(missing_skills)[:8]
    }
