# =============================================================================
#  models.py  –  CareerSwipe Database Models
#  All tables are defined here and managed via Flask-Migrate / Alembic.
#  PostgreSQL is the only supported database in production (Render).
# =============================================================================

from extensions import db
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
#  SEEKERS  (job-seeker accounts)
# ─────────────────────────────────────────────────────────────────────────────
class Seeker(db.Model):
    __tablename__ = 'seekers'

    id                = db.Column(db.Integer, primary_key=True)

    # Core identity
    first_name        = db.Column(db.String(100), nullable=False)
    last_name         = db.Column(db.String(100), nullable=False)
    email             = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash     = db.Column(db.String(255), nullable=False)

    # Contact & location
    phone             = db.Column(db.String(30))
    address           = db.Column(db.String(500))

    # Professional background
    education         = db.Column(db.String(255))
    experience        = db.Column(db.Text)
    skills            = db.Column(db.Text)
    resume_path       = db.Column(db.String(500))

    # Demographics
    gender            = db.Column(db.String(20))
    dob               = db.Column(db.String(20))

    # Job preferences
    experience_type   = db.Column(db.String(50))      # fresher / experienced
    career_field      = db.Column(db.String(100))     # IT / Marketing / Finance etc
    job_status        = db.Column(db.String(50))      # searching / employed / open to offers
    job_location_type = db.Column(db.String(50))      # remote / onsite / hybrid
    shift_preference  = db.Column(db.String(50))      # day / night / flexible
    desired_roles     = db.Column(db.String(255))
    salary_expectation= db.Column(db.String(100))
    availability      = db.Column(db.String(100))

    # Account status
    verification_token= db.Column(db.String(100))
    is_verified       = db.Column(db.Boolean, default=False)
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    swipes = db.relationship(
        'JobSwipe',
        backref='seeker',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        """Serialize seeker to a safe JSON-friendly dict (no password hash)."""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'education': self.education,
            'skills': self.skills,
            'career_field': self.career_field,
            'job_status': self.job_status,
            'job_location_type': self.job_location_type,
            'desired_roles': self.desired_roles,
            'salary_expectation': self.salary_expectation,
            'availability': self.availability,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ─────────────────────────────────────────────────────────────────────────────
#  EMPLOYERS  (company / employer accounts)
#  NOTE: The legacy "companies" table is kept as Company for backwards
#  compatibility with existing routes. The new canonical name is "employers".
# ─────────────────────────────────────────────────────────────────────────────
class Company(db.Model):
    """
    Employer / Company account.
    Table name: 'employers'  (renamed from 'companies' per new schema).
    Legacy alias kept so existing routes need no changes.
    """
    __tablename__ = 'employers'

    id             = db.Column(db.Integer, primary_key=True)
    company_name   = db.Column(db.String(255), nullable=False)
    email          = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash  = db.Column(db.String(255), nullable=False)

    # Company details
    phone          = db.Column(db.String(30))
    company_address= db.Column(db.String(500))
    description    = db.Column(db.Text)
    industry       = db.Column(db.String(150))
    website        = db.Column(db.String(300))
    logo_path      = db.Column(db.String(500))

    # Account status
    verification_token = db.Column(db.String(100))
    is_verified    = db.Column(db.Boolean, default=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    jobs = db.relationship(
        'JobListing',
        backref='company',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'email': self.email,
            'phone': self.phone,
            'company_address': self.company_address,
            'industry': self.industry,
            'website': self.website,
            'logo_path': self.logo_path,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ─────────────────────────────────────────────────────────────────────────────
#  JOBS  (job listings posted by employers)
#  Table name: 'jobs'  (previously 'job_listings')
# ─────────────────────────────────────────────────────────────────────────────
class JobListing(db.Model):
    """
    Job posting by a company/employer.
    Table name: 'jobs'  (renamed for clarity).
    """
    __tablename__ = 'jobs'

    id               = db.Column(db.Integer, primary_key=True)
    company_id       = db.Column(
        db.Integer,
        db.ForeignKey('employers.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Job details
    title            = db.Column(db.String(255), nullable=False)
    description      = db.Column(db.Text, nullable=False)
    required_skills  = db.Column(db.Text)
    location         = db.Column(db.String(255))
    job_type         = db.Column(db.String(50), default='Full-time')      # Full-time / Part-time / Contract
    job_location_type= db.Column(db.String(50), default='Onsite')         # Onsite / Remote / Hybrid
    experience_level = db.Column(db.String(50), default='Entry Level')    # Entry / Mid / Senior / Expert
    min_experience   = db.Column(db.Integer, default=0)                   # years
    experience_required = db.Column(db.String(100))                       # human-readable (e.g. "2-3 years")
    salary           = db.Column(db.String(100))
    max_salary       = db.Column(db.Integer)
    tags             = db.Column(db.Text)                                  # comma-separated keywords
    is_boosted       = db.Column(db.Boolean, default=False)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    swipes = db.relationship(
        'JobSwipe',
        backref='job_listing',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'employer_id': self.company_id,
            'title': self.title,
            'description': self.description,
            'required_skills': self.required_skills,
            'location': self.location,
            'job_type': self.job_type,
            'job_location_type': self.job_location_type,
            'experience_level': self.experience_level,
            'experience_required': self.experience_required,
            'salary': self.salary,
            'is_boosted': self.is_boosted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ─────────────────────────────────────────────────────────────────────────────
#  APPLICATIONS  (job applications / swipes)
#  Table name: 'applications'  (previously 'job_swipes')
# ─────────────────────────────────────────────────────────────────────────────
class JobSwipe(db.Model):
    """
    A seeker's swipe/application on a job listing.
    Table name: 'applications'  (renamed for clarity).
    """
    __tablename__ = 'applications'

    id         = db.Column(db.Integer, primary_key=True)
    seeker_id  = db.Column(
        db.Integer,
        db.ForeignKey('seekers.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    job_id     = db.Column(
        db.Integer,
        db.ForeignKey('jobs.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Swipe direction and application status
    direction  = db.Column(db.String(10), nullable=False)             # left / right
    status     = db.Column(db.String(20), default='pending')          # pending / shortlisted / rejected / interview / accepted

    # AI-generated scores
    ats_score      = db.Column(db.Float, default=0.0)
    match_score    = db.Column(db.Float, default=0.0)
    ai_rank_score  = db.Column(db.Float, default=0.0)

    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)      # alias for compatibility

    def to_dict(self):
        return {
            'id': self.id,
            'seeker_id': self.seeker_id,
            'job_id': self.job_id,
            'direction': self.direction,
            'status': self.status,
            'ats_score': self.ats_score,
            'match_score': self.match_score,
            'ai_rank_score': self.ai_rank_score,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
        }


# ─────────────────────────────────────────────────────────────────────────────
#  NOTIFICATIONS
# ─────────────────────────────────────────────────────────────────────────────
class Notification(db.Model):
    __tablename__ = 'notifications'

    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, nullable=False, index=True)
    user_type = db.Column(db.String(20), nullable=False, index=True)  # 'seeker' or 'company'
    message   = db.Column(db.Text, nullable=False)
    type      = db.Column(db.String(50), default='system')            # application / accepted / rejected / interview / system
    is_read   = db.Column(db.Boolean, default=False)
    created_at= db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
