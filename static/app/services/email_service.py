"""
app/services/email_service.py – Email notification helpers.
Wraps Flask-Mail so routes don't contain raw mail logic.
"""

from flask_mail import Message
from ..extensions import mail

import os


def send_application_emails(
    seeker_email: str,
    seeker_name: str,
    company_email: str,
    company_name: str,
    job_title: str,
    resume_path: str,
) -> None:
    """
    Send application notification emails to both the company and the seeker.
    Failures are silently caught so they never break the application flow.
    """
    # ── To Company ────────────────────────────────────────────────────────────
    msg_company = Message(
        subject=f'New applicant for {job_title}',
        recipients=[company_email],
    )
    msg_company.html = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:auto;background:#0f172a;
                padding:2rem;border-radius:16px;color:#fff">
      <h2 style="color:#3b82f6;margin-bottom:0.5rem">CareerSwipe</h2>
      <p style="color:#94a3b8;margin-bottom:1.5rem">New Application Received</p>
      <p><b style="color:#fff">{seeker_name}</b>
         <span style="color:#94a3b8"> has applied for </span>
         <b style="color:#3b82f6">{job_title}</b></p>
      <p style="color:#94a3b8;margin-top:1rem">Resume is attached to this email.</p>
      <div style="margin-top:2rem;padding-top:1rem;border-top:1px solid rgba(255,255,255,0.1);
                  font-size:12px;color:#64748b">
        CareerSwipe · Smart Job Matching
      </div>
    </div>"""

    if resume_path and os.path.exists(resume_path):
        with open(resume_path, 'rb') as fp:
            msg_company.attach(
                os.path.basename(resume_path),
                'application/octet-stream',
                fp.read(),
            )
    try:
        mail.send(msg_company)
    except Exception:
        pass

    # ── To Seeker ─────────────────────────────────────────────────────────────
    msg_seeker = Message(
        subject=f'Application sent to {company_name}',
        recipients=[seeker_email],
    )
    msg_seeker.html = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:auto;background:#0f172a;
                padding:2rem;border-radius:16px;color:#fff">
      <h2 style="color:#3b82f6">CareerSwipe</h2>
      <p style="color:#94a3b8">Application Confirmation</p>
      <p>Your application for <b style="color:#3b82f6">{job_title}</b>
         at <b style="color:#fff">{company_name}</b> was sent successfully! &#x2705;</p>
    </div>"""
    try:
        mail.send(msg_seeker)
    except Exception:
        pass


def send_status_update_email(
    seeker_email: str,
    seeker_name: str,
    job_title: str,
    company_name: str,
    action_text: str,
) -> None:
    """Notify a seeker that their application status has changed."""
    msg = Message(
        subject=f'Update on your application: {job_title}',
        recipients=[seeker_email],
    )
    msg.html = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:auto;background:#0f172a;
                padding:2rem;border-radius:16px;color:#fff">
      <h2 style="color:#3b82f6">CareerSwipe</h2>
      <p>Hi <b>{seeker_name}</b>,</p>
      <p>Your application for <b style="color:#3b82f6">{job_title}</b>
         at <b>{company_name}</b> has been
         <b style="color:#10b981">{action_text}</b>.</p>
      <p style="color:#94a3b8;margin-top:1rem">
        Login to your dashboard to see more details.</p>
    </div>"""
    try:
        mail.send(msg)
    except Exception:
        pass
