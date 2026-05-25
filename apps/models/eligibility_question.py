"""
app/models/eligibility_question.py – Eligibility question templates.
Table: eligibility_questions
"""

from datetime import datetime
from ..extensions import db


class EligibilityQuestion(db.Model):
    __tablename__ = 'eligibility_questions'

    id                   = db.Column(db.Integer, primary_key=True)
    
    # Question content
    question_text        = db.Column(db.String(500), nullable=False, unique=True)
    question_type        = db.Column(db.String(50), nullable=False)  
    # Types: yes_no, age_range, availability, experience, relocation, salary, notice_period, skills_confirmation
    
    # Description/help text
    description          = db.Column(db.Text)
    
    # Field type for form rendering
    field_type           = db.Column(db.String(50), default='text')  
    # text, number, select, checkbox, date, textarea
    
    # Possible values for select/checkbox types (JSON format)
    field_options        = db.Column(db.Text)  # JSON array: ["option1", "option2"]
    
    # Validation rules (stored as JSON)
    validation_rules     = db.Column(db.Text)  # {"min": 18, "max": 65, "pattern": "regex"}
    
    # Whether this is mandatory for all jobs or optional
    is_mandatory         = db.Column(db.Boolean, default=True)
    
    # Ordering
    display_order        = db.Column(db.Integer, default=0)
    
    # Status
    is_active            = db.Column(db.Boolean, default=True)
    
    # Metadata
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at           = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'description': self.description,
            'field_type': self.field_type,
            'field_options': json.loads(self.field_options) if self.field_options else [],
            'validation_rules': json.loads(self.validation_rules) if self.validation_rules else {},
            'is_mandatory': self.is_mandatory,
            'display_order': self.display_order,
        }
