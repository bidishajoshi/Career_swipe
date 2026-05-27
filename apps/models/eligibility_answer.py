"""
app/models/eligibility_answer.py – Seeker's eligibility question responses.
Table: eligibility_answers
"""

from datetime import datetime
from ..extensions import db


class EligibilityAnswer(db.Model):
    __tablename__ = 'eligibility_answers'

    id                   = db.Column(db.Integer, primary_key=True)
    
    # References
    seeker_id            = db.Column(db.Integer, db.ForeignKey('seekers.id', ondelete='CASCADE'), nullable=False, index=True)
    question_id          = db.Column(db.Integer, db.ForeignKey('eligibility_questions.id', ondelete='CASCADE'), nullable=False)
    job_id               = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Answer value (flexible to store different data types)
    answer_value         = db.Column(db.Text, nullable=False)  # Can be "yes", "30", "["skill1", "skill2"]", etc.
    
    # Validation status
    is_valid             = db.Column(db.Boolean, default=True)
    validation_message   = db.Column(db.Text)  # Error message if validation fails
    
    # Metadata
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at           = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint: one answer per seeker per question per job
    __table_args__       = (db.UniqueConstraint('seeker_id', 'question_id', 'job_id', name='unique_seeker_question_job'),)

    def to_dict(self):
        return {
            'id': self.id,
            'seeker_id': self.seeker_id,
            'question_id': self.question_id,
            'job_id': self.job_id,
            'answer_value': self.answer_value,
            'is_valid': self.is_valid,
            'validation_message': self.validation_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
