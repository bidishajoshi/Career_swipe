# CareerSwipe Notification & Eligibility System - Quick Start Guide

## Installation Steps

### 1. Database Setup

Run database migrations to create the new tables:

```bash
cd c:\Users\VICTUS\Desktop\career-swipe

# Using Flask-Migrate
flask db migrate -m "Add notification and eligibility system"
flask db upgrade

# OR manually create tables
python
>>> from app import app, db
>>> from app.models import *
>>> with app.app_context():
>>>     db.create_all()
>>>     from app.services import EligibilityService
>>>     EligibilityService.create_eligibility_questions()
>>> exit()
```

### 2. Test the API

```bash
# Get unread notification count
curl http://localhost:5000/api/notifications/unread-count

# List notifications
curl http://localhost:5000/api/notifications

# Get eligibility questions
curl http://localhost:5000/api/eligibility/all-questions

# Create a test notification (internal use)
curl -X POST http://localhost:5000/api/notifications/create \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": 1,
    "recipient_type": "seeker",
    "title": "Test Notification",
    "message": "This is a test",
    "notification_type": "system"
  }'
```

### 3. Access Frontend

- **View Notifications**: http://localhost:5000/notifications
- **Eligibility Form**: http://localhost:5000/job/1/eligibility

## Key Features

### For Job Seekers

1. **Notifications**
   - Real-time application status updates
   - Interview invitations
   - New job matches
   - Company messages
   - View all in dedicated page: `/notifications`

2. **Eligibility System**
   - Answer questions before applying
   - Age validation
   - Work authorization check
   - Automatic rejection if ineligible
   - Get feedback on why you're ineligible

### For Companies

1. **Notifications**
   - New applications received
   - Seeker profile updates
   - Interview responses
   - Job posting expiration warnings

2. **Requirements**
   - Set age requirements (min/max)
   - Specify work authorization types
   - Experience requirements
   - Availability requirements
   - Salary expectations
   - Custom validation rules

## Configuration

### Email Setup (Required for notifications)

Add to `.env`:
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@careerswipe.com
```

### Notification Preferences

Users can customize:
- Which notifications to receive
- Email digest frequency (immediate/daily/weekly)
- Quiet hours (no notifications between specific times)
- Archive old notifications

## Integration with Existing Routes

### When a Seeker Applies

```python
# The swipe route should check eligibility first
@app.route("/swipe", methods=["POST"])
def swipe():
    # Check eligibility
    is_eligible, errors = EligibilityService.validate_seeker_eligibility(seeker_id, job_id)
    
    if not is_eligible:
        return jsonify({"error": "Not eligible", "reasons": errors}), 403
    
    # Create application...
    # Send notification to company
    NotificationService.create_notification(...)
    
    # Send email
    EmailService.send_application_submitted(...)
```

### When Company Updates Application

```python
@app.route("/applicant/<int:swipe_id>/<action>")
def update_applicant(swipe_id, action):
    # Update status...
    
    # Create notification & send email
    if action == "accept":
        NotificationService.create_notification(
            recipient_id=seeker.id,
            recipient_type='seeker',
            title="🎉 Application Accepted!",
            message=f"Your application for {job.title} has been accepted!",
            notification_type='app_accepted',
            related_job_id=job.id,
            related_application_id=swipe.id,
            action_url=f'/applications/{swipe.id}'
        )
        EmailService.send_application_accepted(...)
```

## API Reference

### Notification Endpoints

```
GET    /api/notifications                      # List notifications
GET    /api/notifications/unread-count         # Get unread count
POST   /api/notifications/<id>/mark-read       # Mark as read
POST   /api/notifications/mark-all-read        # Mark all as read
POST   /api/notifications/<id>/archive         # Archive
DELETE /api/notifications/<id>                 # Delete
GET    /api/notifications/preferences          # Get preferences
POST   /api/notifications/preferences          # Update preferences
```

### Eligibility Endpoints

```
GET    /api/eligibility/questions/<job_id>     # Get questions for job
GET    /api/eligibility/all-questions          # Get all questions
GET    /api/eligibility/answers/<job_id>       # Get seeker's answers
POST   /api/eligibility/answer                 # Save single answer
POST   /api/eligibility/answers/bulk           # Save multiple answers
GET    /api/eligibility/validate/<job_id>      # Validate eligibility
POST   /api/eligibility/check-age              # Check age eligibility
POST   /api/eligibility/check-work-auth        # Check work auth
```

## Database Schema

### Notifications Table
- id, recipient_id, recipient_type
- title, message, notification_type
- is_read, is_deleted, is_archived
- related_job_id, related_seeker_id, related_company_id, related_application_id
- created_at, read_at, archived_at, updated_at

### Eligibility Questions Table
- id, question_text, question_type
- field_type, field_options (JSON)
- validation_rules (JSON)
- is_mandatory, display_order
- is_active, created_at, updated_at

### Eligibility Answers Table
- id, seeker_id, question_id, job_id
- answer_value, is_valid, validation_message
- created_at, updated_at

### Job Requirements Table
- id, job_id
- min_age, max_age
- min_years_experience, max_years_experience
- allowed_work_auth (CSV)
- required_availability
- relocation_required
- min/max_salary, required_notice_period
- required_skills, legally_eligible_required
- custom_requirements (JSON)

### Notification Preferences Table
- id, user_id, user_type
- notify_app_accepted, notify_app_rejected, notify_interview, etc.
- email_enabled, email_digest
- in_app_enabled
- quiet_hours_enabled, quiet_hours_start, quiet_hours_end

### Interview Invites Table
- id, job_id, seeker_id, company_id, application_id
- interview_type, interview_date, interview_location, interview_link
- status, message_from_company, response_from_seeker
- seeker_responded, seeker_confirmed
- interview_notes, result
- created_at, updated_at

## Testing Checklist

- [ ] Database migrations run successfully
- [ ] All models are accessible
- [ ] API endpoints return correct status codes
- [ ] Notifications appear in database
- [ ] Email notifications send (if configured)
- [ ] Eligibility questions display
- [ ] Eligibility validation works
- [ ] Notification preferences save
- [ ] Navbar bell shows unread count
- [ ] Mark as read updates UI

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| AttributeError: No column named... | Run database migration: `flask db upgrade` |
| 404 on eligibility routes | Check blueprint is registered in app.py |
| Emails not sending | Verify MAIL_* env vars and check Flask-Mail config |
| Notifications not showing | Check recipient_id, recipient_type match session |
| Eligibility validation failing | Ensure seeker has work_authorization set |
| Unread count not updating | Clear browser cache, check API response |

## Next Steps

1. **Integrate with swipe route** - Add eligibility check
2. **Update applicant route** - Send notifications and emails
3. **Add notification bell to navbar** - Show unread count
4. **Test full workflow** - Apply to job with eligibility
5. **Configure email** - Set up SMTP credentials
6. **Customize questions** - Adjust default eligibility questions
7. **Set job requirements** - When posting jobs, set criteria

## Support & Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check logs for:
- Database errors
- Email failures
- API validation issues
- Eligibility validation details

## Resources

- Full Implementation Guide: [NOTIFICATION_SYSTEM_GUIDE.md](./NOTIFICATION_SYSTEM_GUIDE.md)
- API Documentation: See routes in `/app/routes/`
- Service Documentation: See services in `/app/services/`
- Database Schema: Check models in `/app/models/`
