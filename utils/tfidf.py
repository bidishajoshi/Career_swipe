"""
Resume parsing and job recommendation helpers backed by scikit-learn TF-IDF.
"""
import os
import re
import string
from collections import Counter

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    from docx import Document as DocxDocument
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False


STOP_WORDS = set(ENGLISH_STOP_WORDS)

SKILL_TERMS = {
    "accounting", "adobe", "agile", "analytics", "angular", "aws", "azure",
    "banking", "budgeting", "business analysis", "c", "c++", "c#", "cad",
    "caregiving", "case management", "communication", "content marketing",
    "copywriting", "crm", "css", "customer service", "data analysis",
    "data science", "devops", "django", "docker", "education", "excel",
    "figma", "finance", "flask", "git", "go", "google analytics", "gcp",
    "healthcare", "html", "java", "javascript", "kotlin", "kubernetes",
    "leadership", "linux", "logistics", "machine learning", "marketing",
    "mongodb", "mysql", "negotiation", "node", "nursing", "operations",
    "patient care", "php", "postgresql", "power bi", "project management",
    "python", "quality assurance", "react", "recruiting", "research",
    "risk management", "ruby", "rust", "sales", "scrum", "seo", "sql",
    "statistics", "staad pro", "swift", "tableau", "teaching", "testing",
    "typescript", "ui", "ux", "vue", "writing"
}

QUALIFICATION_TERMS = {
    "bachelor", "master", "phd", "doctorate", "diploma", "certificate",
    "certification", "degree", "mba", "bsc", "ba", "msc", "ma", "high school"
}

EXPERIENCE_TERMS = {
    "internship", "junior", "associate", "mid level", "senior", "lead",
    "manager", "director", "years", "experience", "supervisor", "entry level"
}


def parse_resume(filepath: str) -> str:
    """Extract raw text from PDF, DOCX, or DOC resumes."""
    if not filepath or not os.path.exists(filepath):
        return ""

    ext = filepath.rsplit(".", 1)[-1].lower()
    text = ""

    if ext == "pdf" and PDF_SUPPORT:
        try:
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception:
            text = ""
    elif ext == "docx" and DOCX_SUPPORT:
        try:
            doc = DocxDocument(filepath)
            text = "\n".join(p.text for p in doc.paragraphs)
            for table in doc.tables:
                for row in table.rows:
                    text += "\n" + " ".join(cell.text for cell in row.cells)
        except Exception:
            text = ""
    elif ext == "doc":
        try:
            with open(filepath, "r", errors="ignore") as f:
                text = f.read()
        except Exception:
            text = ""

    return text


def clean_text(text: str) -> list[str]:
    """Lowercase, remove punctuation, tokenize, and remove stop words."""
    if not text:
        return []
    punctuation = string.punctuation.replace("+", "").replace("#", "")
    text = text.lower().translate(str.maketrans(punctuation, " " * len(punctuation)))
    tokens = re.findall(r"[a-z0-9][a-z0-9+#.-]*", text)
    return [token for token in tokens if token not in STOP_WORDS and len(token) > 1]


def preprocess_text(text: str) -> str:
    """Return a normalized string suitable for TF-IDF vectorization."""
    return " ".join(clean_text(text))


def _phrase_in_text(phrase: str, text: str) -> bool:
    return re.search(rf"\b{re.escape(phrase)}\b", text, flags=re.IGNORECASE) is not None


def extract_skills(text: str, extra_terms: str = "") -> list[str]:
    """Extract important skills, technologies, qualifications, and keywords."""
    combined = f"{text or ''} {extra_terms or ''}"
    normalized = " ".join(clean_text(combined))
    found = {term for term in SKILL_TERMS if _phrase_in_text(term, normalized)}
    found.update(term for term in QUALIFICATION_TERMS if _phrase_in_text(term, normalized))
    found.update(term for term in EXPERIENCE_TERMS if _phrase_in_text(term, normalized))
    return sorted(found)


def extract_keywords(text: str, top_n: int = 15) -> list[str]:
    """Extract high-signal keywords from text after preprocessing."""
    tokens = clean_text(text)
    if not tokens:
        return []

    counts = Counter(tokens)
    weighted = {}
    for token, count in counts.items():
        weight = 3 if token in SKILL_TERMS else 1
        weighted[token] = count * weight

    return [
        term for term, _ in sorted(weighted.items(), key=lambda item: item[1], reverse=True)[:top_n]
    ]


def build_resume_profile(seeker, resume_text: str) -> dict:
    """Combine extracted resume text with profile fields for personalized matching."""
    profile_text = " ".join([
        resume_text or "",
        seeker.skills or "",
        seeker.education or "",
        seeker.experience or "",
        seeker.career_field or "",
        seeker.desired_roles or "",
        seeker.job_location_type or "",
        seeker.experience_type or "",
    ])
    skills = extract_skills(profile_text, seeker.skills or "")
    keywords = extract_keywords(profile_text, 25)
    return {
        "text": profile_text,
        "preprocessed_text": preprocess_text(profile_text),
        "skills": skills,
        "keywords": keywords,
    }


def job_to_text(job) -> str:
    """Flatten a job record into text used by the recommender."""
    company_name = job.company.company_name if getattr(job, "company", None) else ""
    return " ".join([
        job.title or "",
        company_name,
        job.description or "",
        job.required_skills or "",
        job.location or "",
        job.job_type or "",
        job.job_location_type or "",
        job.experience_level or "",
        job.experience_required or "",
        job.tags or "",
    ])


def _weighted_document(text: str, skills: list[str]) -> str:
    weighted_skills = " ".join(skills * 3)
    return f"{preprocess_text(text)} {weighted_skills}".strip()


def recommend_jobs_for_resume(seeker, resume_text: str, jobs: list, limit: int | None = None) -> list[dict]:
    """Rank jobs by TF-IDF cosine similarity and skill coverage."""
    if not jobs:
        return []

    profile = build_resume_profile(seeker, resume_text)
    resume_doc = _weighted_document(profile["text"], profile["skills"])
    if not resume_doc:
        return []

    job_docs = []
    job_skills = {}
    for job in jobs:
        skills = extract_skills(job_to_text(job), job.required_skills or "")
        job_skills[job.id] = skills
        job_docs.append(_weighted_document(job_to_text(job), skills))

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
    matrix = vectorizer.fit_transform([resume_doc] + job_docs)
    similarities = cosine_similarity(matrix[0:1], matrix[1:]).flatten()

    recommendations = []
    resume_skill_set = set(profile["skills"])
    resume_keyword_set = set(profile["keywords"])

    for job, similarity in zip(jobs, similarities):
        required_skills = set(job_skills.get(job.id, []))
        matched_skills = sorted(required_skills & resume_skill_set)
        missing_skills = sorted(required_skills - resume_skill_set)
        recommended_skills = missing_skills[:6]

        skill_score = (len(matched_skills) / len(required_skills)) if required_skills else 0
        keyword_overlap = len(set(extract_keywords(job_to_text(job), 20)) & resume_keyword_set)
        keyword_boost = min(keyword_overlap * 0.015, 0.15)
        final_score = (float(similarity) * 0.75) + (skill_score * 0.20) + keyword_boost
        match_percentage = max(0, min(100, round(final_score * 100)))

        recommendations.append({
            "job": job,
            "match_percentage": match_percentage,
            "similarity_score": round(float(similarity), 4),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "recommended_skills": recommended_skills,
            "skill_match_percentage": round(skill_score * 100),
            "is_best_match": match_percentage >= 75,
        })

    ranked = sorted(
        recommendations,
        key=lambda item: (item["match_percentage"], item["similarity_score"]),
        reverse=True,
    )
    return ranked[:limit] if limit else ranked


def match_resume_to_job(resume_text: str, job_text: str) -> int:
    """Return a 0-100 match score using scikit-learn TF-IDF and cosine similarity."""
    if not resume_text or not job_text:
        return 0
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
    matrix = vectorizer.fit_transform([preprocess_text(resume_text), preprocess_text(job_text)])
    return round(float(cosine_similarity(matrix[0:1], matrix[1:]).flatten()[0]) * 100)


def match_location_preference(seeker_location: str, seeker_country: str, job_location: str, job_location_type: str) -> float:
    """
    Calculate location match using TF-IDF cosine similarity.
    Returns a 0-1 score indicating how well job location matches seeker preferences.
    
    Args:
        seeker_location: Seeker's preferred location (e.g., "Kathmandu, Nepal")
        seeker_country: Seeker's country
        job_location: Job location (e.g., "Kathmandu")
        job_location_type: Job location type (Remote, Hybrid, Onsite)
    
    Returns:
        Float between 0 and 1 (0 = no match, 1 = perfect match)
    """
    if not job_location or not job_location_type:
        return 0.0
    
    # Remote jobs typically match any location preference
    if job_location_type.lower() == 'remote':
        return 0.95
    
    # Build seeker location preference text
    seeker_text = f"{seeker_location or ''} {seeker_country or ''}".strip().lower()
    job_text = f"{job_location}".strip().lower()
    
    if not seeker_text or not job_text:
        return 0.5 if job_location_type.lower() == 'hybrid' else 0.0
    
    # Exact match gets highest score
    if seeker_text == job_text or seeker_text in job_text or job_text in seeker_text:
        return 0.98
    
    # Use TF-IDF and cosine similarity for partial matches
    try:
        vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3), min_df=1)
        matrix = vectorizer.fit_transform([seeker_text, job_text])
        similarity = float(cosine_similarity(matrix[0:1], matrix[1:]).flatten()[0])
        
        # Boost score for hybrid positions
        if job_location_type.lower() == 'hybrid':
            similarity = min(1.0, similarity + 0.15)
        
        return min(1.0, similarity)
    except Exception:
        return 0.0


def match_skills_preference(seeker_skills: str, job_required_skills: str) -> float:
    """
    Calculate skill match using TF-IDF cosine similarity.
    Returns a 0-1 score indicating skill alignment.
    
    Args:
        seeker_skills: Comma-separated or space-separated skills from seeker profile
        job_required_skills: Comma-separated or space-separated required skills for job
    
    Returns:
        Float between 0 and 1 (0 = no overlap, 1 = perfect match)
    """
    if not seeker_skills or not job_required_skills:
        return 0.5  # Neutral score if skills not specified
    
    seeker_skills_list = extract_skills(seeker_skills)
    job_skills_list = extract_skills(job_required_skills)
    
    if not seeker_skills_list or not job_skills_list:
        return 0.5
    
    # Calculate overlap percentage
    matched = set(seeker_skills_list) & set(job_skills_list)
    if not matched:
        # Use TF-IDF for partial matches
        try:
            vectorizer = TfidfVectorizer(stop_words="english", min_df=1)
            matrix = vectorizer.fit_transform([
                " ".join(seeker_skills_list),
                " ".join(job_skills_list)
            ])
            similarity = float(cosine_similarity(matrix[0:1], matrix[1:]).flatten()[0])
            return min(1.0, similarity)
        except Exception:
            return 0.3
    
    # Score based on matched skills vs required skills
    match_score = len(matched) / len(job_skills_list)
    return min(1.0, match_score)


def filter_jobs_by_preferences(seeker, jobs: list, min_location_score: float = 0.4, min_skill_score: float = 0.3) -> list[dict]:
    """
    Filter jobs based on seeker's location and skill preferences using TF-IDF cosine similarity.
    
    Args:
        seeker: Seeker model instance with location and skills preferences
        jobs: List of JobListing instances to filter
        min_location_score: Minimum location match score (0-1) to include job
        min_skill_score: Minimum skill match score (0-1) to include job
    
    Returns:
        Sorted list of dicts with job info and match scores
    """
    if not jobs:
        return []
    
    seeker_location = (seeker.address or "").strip()
    seeker_country = (seeker.country or "").strip()
    seeker_skills = (seeker.skills or "").strip()
    
    filtered_results = []
    
    for job in jobs:
        try:
            # Calculate location match
            location_score = match_location_preference(
                seeker_location,
                seeker_country,
                (job.location or "").strip(),
                (job.job_location_type or "Onsite").strip()
            )
            
            # Calculate skill match (default 0.5 if no skills specified)
            if not seeker_skills or not job.required_skills:
                skill_score = 0.5  # Neutral if skills not specified
            else:
                skill_score = match_skills_preference(
                    seeker_skills,
                    (job.required_skills or "").strip()
                )
            
            # Apply location threshold (STRICT) - always filter by location
            if location_score >= min_location_score:
                # Combined relevance score (weighted average)
                relevance_score = (location_score * 0.4) + (skill_score * 0.6)
                
                filtered_results.append({
                    'job': job,
                    'location_score': round(location_score, 3),
                    'skill_score': round(skill_score, 3),
                    'relevance_score': round(relevance_score, 3),
                    'is_relevant': True,
                })
        except Exception as e:
            # Skip jobs that cause errors during filtering
            print(f"Error filtering job {job.id}: {str(e)}")
            continue
    
    # Sort by relevance score (highest first)
    filtered_results.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    return filtered_results
