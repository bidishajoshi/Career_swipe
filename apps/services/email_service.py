"""
app/services/email_service.py – Professional email notification service.
Handles all email communications integrated with notification system.
"""

from flask_mail import Message
from typing import List, Optional
import os
from ..extensions import mail


class EmailService:
    """Service layer for email operations"""

    # Email templates with professional styling
    BASE_TEMPLATE = """
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: auto; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0; border-radius: 12px; overflow: hidden; color: #fff; box-shadow: 0 10px 40px rgba(0,0,0,0.1)">
        <div style="background: #2d3748; padding: 2rem; border-bottom: 4px solid #667eea;">
            <h1 style="margin: 0; color: #fff; font-size: 28px;">CareerSwipe</h1>
            <p style="margin: 0.5rem 0 0 0; color: #cbd5e0; font-size: 14px;">Smart Job Matching Platform</p>
        </div>
        <div style="padding: 2rem; background: #fff; color: #2d3748;">
            {content}
        </div>
        <div style="background: #2d3748; padding: 1rem 2rem; text-align: center; font-size: 12px; color: #a0aec0; border-top: 1px solid #4a5568;">
            <p style="margin: 0;">© 2026 CareerSwipe. All rights reserved.</p>
            <p style="margin: 0.5rem 0 0 0; color: #718096;">
                <a href="#" style="color: #667eea; text-decoration: none;">Privacy Policy</a> | 
                <a href="#" style="color: #667eea; text-decoration: none;">Terms of Service</a>
            </p>
        </div>
    </div>
    """

    @staticmethod
    def send_application_submitted(
        seeker_email: str,
        seeker_name: str,
        company_email: str,
        company_name: str,
        job_title: str,
        resume_path: Optional[str] = None,
    ) -> bool:
        """Send application submission emails to both seeker and company"""
        try:
            # Email to company
            company_content = f"""
            <h2 style="margin-top: 0; color: #667eea;">New Application Received! 🎉</h2>
            <p style="font-size: 16px; line-height: 1.6;">
                <strong>{seeker_name}</strong> has applied for:
            </p>
            <div style="background: #f7fafc; padding: 1rem; border-left: 4px solid #667eea; margin: 1rem 0;">
                <h3 style="margin: 0; color: #2d3748;">{job_title}</h3>
            </div>
            <p style="color: #4a5568; font-size: 14px;">
                Review the application in your <a href="#dashboard" style="color: #667eea; text-decoration: none;"><strong>dashboard</strong></a>.
            </p>
            """
            
            company_html = EmailService.BASE_TEMPLATE.format(content=company_content)
            msg_company = Message(
                subject=f'New Application: {job_title}',
                recipients=[company_email],
                html=company_html,
            )

            if resume_path and os.path.exists(resume_path):
                try:
                    with open(resume_path, 'rb') as fp:
                        msg_company.attach(
                            os.path.basename(resume_path),
                            'application/octet-stream',
                            fp.read(),
                        )
                except Exception as e:
                    print(f'[EmailService] Error attaching resume: {e}')

            mail.send(msg_company)

            # Email to seeker
            seeker_content = f"""
            <h2 style="margin-top: 0; color: #667eea;">Application Submitted ✅</h2>
            <p style="font-size: 16px; line-height: 1.6;">
                Hi <strong>{seeker_name}</strong>,
            </p>
            <p style="color: #4a5568; line-height: 1.8;">
                Your application for <strong>{job_title}</strong> at <strong>{company_name}</strong> has been successfully submitted!
            </p>
            <p style="color: #4a5568; font-size: 14px; line-height: 1.8;">
                The company will review your profile and get back to you soon. You'll be notified once they respond.
            </p>
            """

            seeker_html = EmailService.BASE_TEMPLATE.format(content=seeker_content)
            msg_seeker = Message(
                subject=f'Application Sent: {company_name}',
                recipients=[seeker_email],
                html=seeker_html,
            )

            mail.send(msg_seeker)
            return True
        except Exception as e:
            print(f'[EmailService] Error sending application emails: {e}')
            return False

    @staticmethod
    def send_application_accepted(
        seeker_email: str,
        seeker_name: str,
        job_title: str,
        company_name: str,
        next_steps: Optional[str] = None,
    ) -> bool:
        """Notify seeker that their application was accepted"""
        try:
            content = f"""
            <h2 style="margin-top: 0; color: #10b981;">Application Accepted! 🎊</h2>
            <p style="font-size: 16px; line-height: 1.6;">
                Hi <strong>{seeker_name}</strong>,
            </p>
            <p style="color: #4a5568; line-height: 1.8;">
                Great news! <strong>{company_name}</strong> has accepted your application for <strong>{job_title}</strong>.
            </p>
            {f'<div style="background: #ecfdf5; padding: 1rem; border-left: 4px solid #10b981; margin: 1rem 0;"><p style="margin: 0; color: #065f46;"><strong>Next Steps:</strong><br>{next_steps}</p></div>' if next_steps else ''}
            <p style="color: #4a5568; font-size: 14px;">
                Check your <a href="#dashboard" style="color: #667eea; text-decoration: none;"><strong>dashboard</strong></a> for more details and to respond.
            </p>
            """

            html = EmailService.BASE_TEMPLATE.format(content=content)
            msg = Message(
                subject=f'Application Accepted: {company_name}',
                recipients=[seeker_email],
                html=html,
            )
            mail.send(msg)
            return True
        except Exception as e:
            print(f'[EmailService] Error sending acceptance email: {e}')
            return False

    @staticmethod
    def send_application_rejected(
        seeker_email: str,
        seeker_name: str,
        job_title: str,
        company_name: str,
        feedback: Optional[str] = None,
    ) -> bool:
        """Notify seeker that their application was rejected"""
        try:
            content = f"""
            <h2 style="margin-top: 0; color: #f56565;">Application Update</h2>
            <p style="font-size: 16px; line-height: 1.6;">
                Hi <strong>{seeker_name}</strong>,
            </p>
            <p style="color: #4a5568; line-height: 1.8;">
                Thank you for applying to <strong>{job_title}</strong> at <strong>{company_name}</strong>. 
                While your profile was impressive, they've decided to move forward with other candidates at this time.
            </p>
            {f'<div style="background: #fff5f5; padding: 1rem; border-left: 4px solid #f56565; margin: 1rem 0;"><p style="margin: 0; color: #742a2a;"><strong>Feedback:</strong><br>{feedback}</p></div>' if feedback else ''}
            <p style="color: #4a5568; font-size: 14px;">
                Don't be discouraged! Continue exploring other opportunities on <a href="#" style="color: #667eea; text-decoration: none;"><strong>CareerSwipe</strong></a>.
            </p>
            """

            html = EmailService.BASE_TEMPLATE.format(content=content)
            msg = Message(
                subject=f'Application Update: {company_name}',
                recipients=[seeker_email],
                html=html,
            )
            mail.send(msg)
            return True
        except Exception as e:
            print(f'[EmailService] Error sending rejection email: {e}')
            return False

    @staticmethod
    def send_interview_invitation(
        seeker_email: str,
        seeker_name: str,
        job_title: str,
        company_name: str,
        interview_type: str,
        interview_date: Optional[str] = None,
        interview_link: Optional[str] = None,
        message: Optional[str] = None,
    ) -> bool:
        """Send interview invitation to seeker"""
        try:
            content = f"""
            <h2 style="margin-top: 0; color: #667eea;">Interview Invitation 📅</h2>
            <p style="font-size: 16px; line-height: 1.6;">
                Hi <strong>{seeker_name}</strong>,
            </p>
            <p style="color: #4a5568; line-height: 1.8;">
                Congratulations! <strong>{company_name}</strong> would like to conduct an interview for the position of <strong>{job_title}</strong>.
            </p>
            <div style="background: #edf2f7; padding: 1rem; border-left: 4px solid #667eea; margin: 1rem 0;">
                <p style="margin: 0; color: #2d3748;"><strong>Interview Details:</strong></p>
                <p style="margin: 0.5rem 0 0 0; color: #4a5568;">
                    <strong>Type:</strong> {interview_type}
                    {f'<br><strong>Scheduled:</strong> {interview_date}' if interview_date else ''}
                    {f'<br><strong>Link:</strong> <a href="{interview_link}" style="color: #667eea;">{interview_link}</a>' if interview_link else ''}
                </p>
            </div>
            {f'<p style="color: #4a5568; line-height: 1.8; background: #f7fafc; padding: 1rem; border-radius: 8px;"><strong>From {company_name}:</strong><br>{message}</p>' if message else ''}
            <p style="color: #4a5568; font-size: 14px;">
                Please confirm your availability in your <a href="#dashboard" style="color: #667eea; text-decoration: none;"><strong>dashboard</strong></a>.
            </p>
            """

            html = EmailService.BASE_TEMPLATE.format(content=content)
            msg = Message(
                subject=f'Interview Invitation: {company_name}',
                recipients=[seeker_email],
                html=html,
            )
            mail.send(msg)
            return True
        except Exception as e:
            print(f'[EmailService] Error sending interview invitation: {e}')
            return False

    @staticmethod
    def send_new_job_match(
        seeker_email: str,
        seeker_name: str,
        job_title: str,
        company_name: str,
        match_percentage: int,
        job_url: Optional[str] = None,
    ) -> bool:
        """Send notification about a new matching job"""
        try:
            content = f"""
            <h2 style="margin-top: 0; color: #667eea;">Perfect Match Found! 🎯</h2>
            <p style="font-size: 16px; line-height: 1.6;">
                Hi <strong>{seeker_name}</strong>,
            </p>
            <p style="color: #4a5568; line-height: 1.8;">
                We found a job that matches your profile!
            </p>
            <div style="background: #edf2f7; padding: 1rem; border-left: 4px solid #667eea; margin: 1rem 0; border-radius: 8px;">
                <h3 style="margin: 0; color: #2d3748;">{job_title}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #4a5568;">
                    <strong>{company_name}</strong>
                </p>
                <p style="margin: 0.5rem 0 0 0; font-size: 14px; color: #667eea;">
                    <strong>{match_percentage}% Match</strong>
                </p>
            </div>
            <p style="text-align: center; margin: 1.5rem 0;">
                <a href="{job_url or '#'}" style="background: #667eea; color: white; padding: 0.75rem 1.5rem; text-decoration: none; border-radius: 8px; display: inline-block;"><strong>View Job</strong></a>
            </p>
            """

            html = EmailService.BASE_TEMPLATE.format(content=content)
            msg = Message(
                subject=f'New Job Match: {job_title}',
                recipients=[seeker_email],
                html=html,
            )
            mail.send(msg)
            return True
        except Exception as e:
            print(f'[EmailService] Error sending job match email: {e}')
            return False

    @staticmethod
    def send_generic_notification(
        recipient_email: str,
        recipient_name: str,
        subject: str,
        title: str,
        message: str,
        action_url: Optional[str] = None,
        action_text: Optional[str] = None,
    ) -> bool:
        """Send a generic notification email"""
        try:
            content = f"""
            <h2 style="margin-top: 0; color: #667eea;">{title}</h2>
            <p style="font-size: 16px; line-height: 1.6;">
                Hi <strong>{recipient_name}</strong>,
            </p>
            <p style="color: #4a5568; line-height: 1.8;">
                {message}
            </p>
            {f'<p style="text-align: center; margin: 1.5rem 0;"><a href="{action_url}" style="background: #667eea; color: white; padding: 0.75rem 1.5rem; text-decoration: none; border-radius: 8px; display: inline-block;"><strong>{action_text}</strong></a></p>' if action_url and action_text else ''}
            """

            html = EmailService.BASE_TEMPLATE.format(content=content)
            msg = Message(
                subject=subject,
                recipients=[recipient_email],
                html=html,
            )
            mail.send(msg)
            return True
        except Exception as e:
            print(f'[EmailService] Error sending generic email: {e}')
            return False

    @staticmethod
    def send_bulk_emails(recipients_data: List[dict]) -> int:
        """
        Send emails to multiple recipients.

        Args:
            recipients_data: List of dicts with email data

        Returns:
            Number of successfully sent emails
        """
        sent_count = 0
        try:
            for recipient in recipients_data:
                if EmailService.send_generic_notification(
                    recipient_email=recipient.get('email'),
                    recipient_name=recipient.get('name'),
                    subject=recipient.get('subject'),
                    title=recipient.get('title'),
                    message=recipient.get('message'),
                    action_url=recipient.get('action_url'),
                    action_text=recipient.get('action_text'),
                ):
                    sent_count += 1
            return sent_count
        except Exception as e:
            print(f'[EmailService] Error sending bulk emails: {e}')
            return sent_count


# ── Module-level wrapper functions for backward compatibility ──────────────────
def send_application_emails(seeker_email: str, seeker_name: str, company_email: str, company_name: str, job_title: str, resume_path: Optional[str] = None) -> None:
    """Send application notification emails to both company and seeker."""
    EmailService.send_application_submitted(
        seeker_email=seeker_email,
        seeker_name=seeker_name,
        company_email=company_email,
        company_name=company_name,
        job_title=job_title,
        resume_path=resume_path,
    )


def send_status_update_email(company_email: str, company_name: str, seeker_name: str, job_title: str, new_status: str) -> None:
    """Send status update email to company."""
    EmailService.send_application_accepted(
        company_email=company_email,
        company_name=company_name,
        seeker_name=seeker_name,
        job_title=job_title,
    ) if new_status == 'accepted' else EmailService.send_application_rejected(
        company_email=company_email,
        company_name=company_name,
        seeker_name=seeker_name,
        job_title=job_title,
    )
