"""
app/models/job_swipe.py – Job application / swipe model.
Table: applications (renamed from job_swipes in migration 001_full_schema)
"""

from datetime import datetime
from ..extensions import db


class JobSwipe(db.Model):
    """
    A seeker's swipe/application on a job listing.
    Table name: 'applications' (renamed for clarity).
    Class kept as 'JobSwipe' for backwards compatibility with routes.
    """
    __tablename__ = 'applications'

    id            = db.Column(db.Integer, primary_key=True)
    seeker_id     = db.Column(
        db.Integer,
        db.ForeignKey('seekers.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    job_id        = db.Column(
        db.Integer,
        db.ForeignKey('jobs.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    # Swipe direction and application status
    direction     = db.Column(db.String(10), nullable=False)        # left / right
    status        = db.Column(db.String(20), default='pending')     # pending / shortlisted / interview / accepted / rejected

    # AI-generated scores
    ats_score     = db.Column(db.Float, default=0.0)
    match_score   = db.Column(db.Float, default=0.0)
    ai_rank_score = db.Column(db.Float, default=0.0)

    applied_at    = db.Column(db.DateTime, default=datetime.utcnow)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)  # alias for compatibility

    def to_dict(self):
        return {
            'id':            self.id,
            'seeker_id':     self.seeker_id,
            'job_id':        self.job_id,
            'direction':     self.direction,
            'status':        self.status,
            'ats_score':     self.ats_score,
            'match_score':   self.match_score,
            'ai_rank_score': self.ai_rank_score,
            'applied_at':    self.applied_at.isoformat() if self.applied_at else None,
        }
