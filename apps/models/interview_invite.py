"""
app/models/interview_invite.py – Interview invitation management.
Table: interview_invites
"""

from datetime import datetime
from ..extensions import db


class InterviewInvite(db.Model):
    __tablename__ = 'interview_invites'

    id                   = db.Column(db.Integer, primary_key=True)
    
    # References
    job_id               = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False, index=True)
    seeker_id            = db.Column(db.Integer, db.ForeignKey('seekers.id', ondelete='CASCADE'), nullable=False, index=True)
    company_id           = db.Column(db.Integer, db.ForeignKey('employers.id', ondelete='CASCADE'), nullable=False, index=True)
    application_id       = db.Column(db.Integer, db.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Interview details
    interview_type       = db.Column(db.String(50), default='video')  # phone, video, in_person, hybrid
    interview_date       = db.Column(db.DateTime)
    interview_location   = db.Column(db.String(500))  # Address or meeting link
    interview_link       = db.Column(db.String(500))  # Zoom/Google Meet link
    round_number         = db.Column(db.Integer, default=1)
    
    # Status
    status               = db.Column(db.String(50), default='pending')  
    # pending, confirmed, completed, cancelled, no_show
    
    # Communication
    message_from_company = db.Column(db.Text)
    response_from_seeker = db.Column(db.Text)  # Seeker's confirmation/rejection message
    
    # Response tracking
    seeker_responded     = db.Column(db.Boolean, default=False)
    seeker_response_at   = db.Column(db.DateTime)
    seeker_confirmed     = db.Column(db.Boolean)  # True=accept, False=reject
    
    # Interview result
    interview_notes      = db.Column(db.Text)  # Notes from interviewer
    result               = db.Column(db.String(50))  # selected, rejected, pending, hold
    
    # Metadata
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at           = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'seeker_id': self.seeker_id,
            'company_id': self.company_id,
            'application_id': self.application_id,
            'interview_type': self.interview_type,
            'interview_date': self.interview_date.isoformat() if self.interview_date else None,
            'interview_location': self.interview_location,
            'interview_link': self.interview_link,
            'round_number': self.round_number,
            'status': self.status,
            'message_from_company': self.message_from_company,
            'seeker_responded': self.seeker_responded,
            'seeker_confirmed': self.seeker_confirmed,
            'result': self.result,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
