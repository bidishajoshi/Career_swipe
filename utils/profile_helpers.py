"""Profile completion and draft helpers for seeker/company wizards."""


def _filled(value):
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return bool(str(value).strip())


def calculate_seeker_completion(seeker):
    """Return profile completion percentage (0–100) for a seeker."""
    checks = [
        seeker.first_name,
        seeker.last_name,
        seeker.email,
        seeker.phone,
        seeker.address,
        seeker.country,
        seeker.education,
        seeker.experience,
        seeker.skills,
        seeker.resume_path,
        seeker.desired_roles,
        seeker.job_location_type,
        seeker.salary_expectation,
        seeker.linkedin or seeker.portfolio,
    ]
    if not checks:
        return 0
    done = sum(1 for c in checks if _filled(c))
    return min(100, round((done / len(checks)) * 100))


def calculate_company_completion(company):
    """Return profile completion percentage (0–100) for a company."""
    checks = [
        company.company_name,
        company.email,
        company.phone,
        company.industry,
        company.company_size,
        company.website,
        company.company_address or company.headquarters,
        company.logo_path,
        company.description,
        company.mission or company.culture,
        company.perks,
        company.open_positions or company.hiring_categories,
        company.work_mode,
        company.linkedin_url,
        company.business_registration or company.verification_document,
    ]
    if not checks:
        return 0
    done = sum(1 for c in checks if _filled(c))
    return min(100, round((done / len(checks)) * 100))


def update_seeker_completion(seeker):
    pct = calculate_seeker_completion(seeker)
    seeker.profile_completion = pct
    return pct


def update_company_completion(company):
    pct = calculate_company_completion(company)
    company.profile_completion = pct
    return pct
