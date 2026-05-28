"""
app/services/eligibility_service.py – Eligibility validation and answer management.
Handles eligibility questions, answers, and job requirement validation.
"""

from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json
from ..extensions import db
from ..models import (
    EligibilityQuestion, EligibilityAnswer, JobRequirements,
    Seeker, JobListing
)


class EligibilityService:
    """Service layer for eligibility operations"""

    @staticmethod
    def get_eligible_questions(job_id: int) -> List[EligibilityQuestion]:
        """Get all eligible questions for a specific job"""
        try:
            # Get job requirements
            requirements = JobRequirements.query.filter_by(job_id=job_id).first()

            # For now, return all active mandatory questions
            # In the future, can filter based on job requirements
            return EligibilityQuestion.query.filter_by(
                is_active=True,
                is_mandatory=True,
            ).order_by(EligibilityQuestion.display_order).all()
        except Exception as e:
            print(f'[EligibilityService] Error getting questions: {e}')
            return []

    @staticmethod
    def save_eligibility_answer(
        seeker_id: int,
        question_id: int,
        job_id: int,
        answer_value: str,
    ) -> Optional[EligibilityAnswer]:
        """Save or update an eligibility answer"""
        try:
            # Check if answer already exists
            answer = EligibilityAnswer.query.filter_by(
                seeker_id=seeker_id,
                question_id=question_id,
                job_id=job_id,
            ).first()

            if answer:
                answer.answer_value = answer_value
                answer.updated_at = datetime.utcnow()
            else:
                answer = EligibilityAnswer(
                    seeker_id=seeker_id,
                    question_id=question_id,
                    job_id=job_id,
                    answer_value=answer_value,
                )
                db.session.add(answer)

            db.session.commit()
            return answer
        except Exception as e:
            print(f'[EligibilityService] Error saving answer: {e}')
            db.session.rollback()
            return None

    @staticmethod
    def save_bulk_answers(
        seeker_id: int,
        job_id: int,
        answers: Dict[int, str],
    ) -> Tuple[bool, List[str]]:
        """
        Save multiple eligibility answers at once.

        Args:
            seeker_id: ID of seeker
            job_id: ID of job
            answers: Dict of {question_id: answer_value}

        Returns:
            Tuple of (success: bool, errors: List[str])
        """
        errors = []
        try:
            for question_id, answer_value in answers.items():
                result = EligibilityService.save_eligibility_answer(
                    seeker_id, question_id, job_id, answer_value
                )
                if not result:
                    errors.append(f'Failed to save answer for question {question_id}')

            if not errors:
                return True, []
            return False, errors
        except Exception as e:
            print(f'[EligibilityService] Error saving bulk answers: {e}')
            return False, [str(e)]

    @staticmethod
    def get_seeker_answers(seeker_id: int, job_id: int) -> Dict[int, str]:
        """Get all answers provided by a seeker for a specific job"""
        try:
            answers = EligibilityAnswer.query.filter_by(
                seeker_id=seeker_id,
                job_id=job_id,
            ).all()

            return {answer.question_id: answer.answer_value for answer in answers}
        except Exception as e:
            print(f'[EligibilityService] Error getting answers: {e}')
            return {}

    @staticmethod
    def validate_seeker_eligibility(seeker_id: int, job_id: int) -> Tuple[bool, List[str]]:
        """
        Comprehensive eligibility check for a seeker applying to a job.

        Returns:
            Tuple of (is_eligible: bool, validation_errors: List[str])
        """
        errors = []

        try:
            seeker = Seeker.query.get(seeker_id)
            job = JobListing.query.get(job_id)
            requirements = JobRequirements.query.filter_by(job_id=job_id).first()

            if not seeker or not job:
                return False, ['Seeker or job not found']

            # Check legal eligibility
            if requirements and requirements.legally_eligible_required:
                if not seeker.legally_eligible:
                    errors.append('You must confirm legal eligibility to work')

            # Check work authorization
            if requirements and requirements.allowed_work_auth:
                allowed_auths = requirements.allowed_work_auth.split(',')
                if seeker.work_authorization not in allowed_auths:
                    errors.append(
                        f'Your work authorization status does not match job requirements. '
                        f'Required: {", ".join(allowed_auths)}'
                    )

            # Check age requirements
            if seeker.dob and requirements:
                from dateutil import parser
                try:
                    dob = parser.parse(seeker.dob)
                    from datetime import datetime
                    today = datetime.utcnow()
                    age = (today - dob).days // 365

                    if requirements.min_age and age < requirements.min_age:
                        errors.append(f'Minimum age requirement: {requirements.min_age} years')

                    if requirements.max_age and age > requirements.max_age:
                        errors.append(f'Maximum age requirement: {requirements.max_age} years')
                except Exception as age_err:
                    print(f'[EligibilityService] Error calculating age: {age_err}')

            # Check experience
            if requirements and requirements.min_years_experience:
                # This would need to be parsed from seeker.experience
                pass

            # Get and validate eligibility answers
            answers = EligibilityService.get_seeker_answers(seeker_id, job_id)
            questions = EligibilityQuestion.query.filter_by(is_mandatory=True).all()

            for question in questions:
                if question.id not in answers:
                    errors.append(f'Answer required for: {question.question_text}')

            return len(errors) == 0, errors
        except Exception as e:
            print(f'[EligibilityService] Error validating eligibility: {e}')
            return False, [f'Eligibility validation error: {str(e)}']

    @staticmethod
    def check_age_eligibility(dob: str, min_age: Optional[int], max_age: Optional[int]) -> Tuple[bool, str]:
        """
        Check if age falls within requirements.

        Args:
            dob: Date of birth as string
            min_age: Minimum age requirement
            max_age: Maximum age requirement

        Returns:
            Tuple of (is_eligible: bool, message: str)
        """
        try:
            from dateutil import parser
            from datetime import datetime

            dob_date = parser.parse(dob)
            today = datetime.utcnow()
            age = (today - dob_date).days // 365

            if min_age and age < min_age:
                return False, f'Minimum age requirement is {min_age} years'

            if max_age and age > max_age:
                return False, f'Maximum age requirement is {max_age} years'

            return True, f'Age {age} is within requirements'
        except Exception as e:
            return False, f'Error validating age: {str(e)}'

    @staticmethod
    def check_work_auth_eligibility(
        seeker_work_auth: str,
        allowed_work_auth: str,
    ) -> Tuple[bool, str]:
        """Check if seeker's work authorization is in allowed list"""
        try:
            if not allowed_work_auth:
                return True, 'No work authorization restrictions'

            allowed_list = [auth.strip() for auth in allowed_work_auth.split(',')]

            if seeker_work_auth in allowed_list:
                return True, 'Work authorization is eligible'

            return False, f'Work authorization not eligible. Required: {", ".join(allowed_list)}'
        except Exception as e:
            return False, f'Error validating work authorization: {str(e)}'

    @staticmethod
    def create_eligibility_questions() -> bool:
        """Create default set of eligibility questions"""
        try:
            default_questions = [
                {
                    'question_text': 'Are you legally eligible to work in your country?',
                    'question_type': 'yes_no',
                    'field_type': 'checkbox',
                    'display_order': 1,
                    'is_mandatory': True,
                },
                {
                    'question_text': 'Are you at least 18 years old?',
                    'question_type': 'yes_no',
                    'field_type': 'checkbox',
                    'display_order': 2,
                    'is_mandatory': True,
                },
                {
                    'question_text': 'Are you available for the required job type?',
                    'question_type': 'yes_no',
                    'field_type': 'checkbox',
                    'display_order': 3,
                    'is_mandatory': True,
                },
                {
                    'question_text': 'Do you have relevant work experience for this position?',
                    'question_type': 'yes_no',
                    'field_type': 'checkbox',
                    'display_order': 4,
                    'is_mandatory': True,
                },
                {
                    'question_text': 'Would you be willing to relocate if required?',
                    'question_type': 'yes_no',
                    'field_type': 'checkbox',
                    'display_order': 5,
                    'is_mandatory': True,
                },
                {
                    'question_text': 'I confirm I have the required skills for this position',
                    'question_type': 'yes_no',
                    'field_type': 'checkbox',
                    'display_order': 6,
                    'is_mandatory': True,
                },
            ]

            for q_data in default_questions:
                existing = EligibilityQuestion.query.filter_by(
                    question_text=q_data['question_text']
                ).first()

                if existing:
                    existing.question_type = q_data['question_type']
                    existing.field_type = q_data['field_type']
                    existing.display_order = q_data['display_order']
                    existing.is_mandatory = q_data['is_mandatory']
                    existing.description = q_data.get('description')
                    existing.field_options = q_data.get('field_options')
                else:
                    question = EligibilityQuestion(**q_data)
                    db.session.add(question)

            db.session.commit()
            return True
        except Exception as e:
            print(f'[EligibilityService] Error creating default questions: {e}')
            db.session.rollback()
            return False

    @staticmethod
    def get_job_requirements(job_id: int) -> Optional[JobRequirements]:
        """Get requirements for a specific job"""
        try:
            return JobRequirements.query.filter_by(job_id=job_id).first()
        except Exception as e:
            print(f'[EligibilityService] Error getting job requirements: {e}')
            return None

    @staticmethod
    def create_job_requirements(job_id: int, **kwargs) -> Optional[JobRequirements]:
        """Create job requirements"""
        try:
            requirements = JobRequirements(job_id=job_id, **kwargs)
            db.session.add(requirements)
            db.session.commit()
            return requirements
        except Exception as e:
            print(f'[EligibilityService] Error creating job requirements: {e}')
            db.session.rollback()
            return None

    @staticmethod
    def update_job_requirements(job_id: int, **kwargs) -> bool:
        """Update job requirements"""
        try:
            requirements = JobRequirements.query.filter_by(job_id=job_id).first()

            if not requirements:
                EligibilityService.create_job_requirements(job_id, **kwargs)
                return True

            for key, value in kwargs.items():
                if hasattr(requirements, key):
                    setattr(requirements, key, value)

            db.session.commit()
            return True
        except Exception as e:
            print(f'[EligibilityService] Error updating job requirements: {e}')
            db.session.rollback()
            return False
