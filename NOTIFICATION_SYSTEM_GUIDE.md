# CareerSwipe Notification & Eligibility System - Implementation Guide

## Overview

This guide covers the complete implementation of a professional notification and eligibility system for the CareerSwipe job portal using Flask + PostgreSQL.

## What's Been Implemented

### 1. **Database Models** ✅
Enhanced relational database schema with the following models:

#### Core Models
- **Notification** (Enhanced)
  - Comprehensive notification tracking for both seekers and companies
  - Fields: recipient_id, recipient_type, title, message, notification_type
  - Related objects tracking: related_job_id, related_seeker_id, related_application_id, related_company_id
  - Status tracking: is_read, is_deleted, is_archived
  - Methods: mark_as_read(), archive()

#### New Models
- **EligibilityQuestion**
  - Template questions for job applications
  - Configurable field types (text, number, select, checkbox, textarea)
  - Validation rules support (JSON)
  - Display ordering and mandatory flags

- **EligibilityAnswer**
  - Stores seeker responses to eligibility questions
  - Links seeker, question, and job
  - Validation status tracking
  - Unique constraint: one answer per seeker per question per job

- **JobRequirements**
  - Job-specific eligibility criteria
  - Age requirements (min/max)
  - Experience requirements
  - Work authorization types (citizen, permanent_resident, visa_sponsored, remote_international)
  - Availability requirements
  - Salary expectations
  - Notice period
  - Skill requirements
  - Custom validation rules (JSON)

- **InterviewInvite**
  - Tracks interview invitations and responses
  - Interview details: type, date, location, meeting link
  - Communication: company message, seeker response
  - Result tracking: selected, rejected, pending, hold
  - Multi-round interview support

- **NotificationPreference**
  - User-configurable notification settings
  - Separate preferences for seekers and companies
  - Email digest options (immediate, daily, weekly)
  - Quiet hours support
  - Unique constraint: one preference per user

### 2. **Service Layer** ✅
Professional service classes abstracting business logic:

#### NotificationService
```python
# Key Methods:
- create_notification()           # Create new notification
- get_notifications()             # Fetch with pagination
- get_unread_count()             # Quick unread count
- mark_as_read()                 # Mark single notification
- mark_all_as_read()             # Batch operation
- archive_notification()         # Archive for later
- delete_notification()          # Soft/hard delete
- get_preferences()              # User preferences
- update_preferences()           # Modify settings
- should_notify()                # Check notification eligibility
```

#### EligibilityService
```python
# Key Methods:
- get_eligible_questions()               # Get questions for job
- save_eligibility_answer()              # Store single answer
- save_bulk_answers()                   # Batch save answers
- get_seeker_answers()                  # Fetch answers
- validate_seeker_eligibility()         # Comprehensive validation
- check_age_eligibility()               # Age range validation
- check_work_auth_eligibility()         # Work authorization check
- create_eligibility_questions()        # Initialize defaults
- get_job_requirements()                # Fetch job criteria
- create_job_requirements()             # Create new criteria
- update_job_requirements()             # Modify criteria
```

#### EmailService
```python
# Professional email methods with styled HTML templates:
- send_application_submitted()           # Both seeker & company
- send_application_accepted()           # Acceptance notification
- send_application_rejected()           # Rejection with feedback
- send_interview_invitation()           # Interview details
- send_new_job_match()                 # Job matching notification
- send_generic_notification()          # Flexible emails
- send_bulk_emails()                   # Batch operations
```

### 3. **API Routes** ✅

#### Notification Routes (`/app/routes/notifications.py`)
```
Page Routes:
  GET  /notifications                    # Notification history page
  GET  /notifications/preferences        # Preferences settings page

Notification API:
  GET    /api/notifications              # List with pagination
  GET    /api/notifications/unread-count # Get unread count
  POST   /api/notifications/<id>/mark-read
  POST   /api/notifications/mark-all-read
  POST   /api/notifications/<id>/archive
  DELETE /api/notifications/<id>
  POST   /api/notifications/create       # Internal use

Preferences API:
  GET    /api/notifications/preferences
  POST   /api/notifications/preferences
```

#### Eligibility Routes (`/app/routes/eligibility.py`)
```
Page Routes:
  GET  /job/<id>/eligibility             # Eligibility form before apply

Questions API:
  GET  /api/eligibility/questions/<job_id>
  GET  /api/eligibility/all-questions

Answers API:
  GET    /api/eligibility/answers/<job_id>
  POST   /api/eligibility/answer         # Single answer
  POST   /api/eligibility/answers/bulk   # Batch answers

Validation API:
  GET  /api/eligibility/validate/<job_id>
  POST /api/eligibility/check-age
  POST /api/eligibility/check-work-auth

Job Requirements API:
  GET  /api/job-requirements/<job_id>
  POST /api/job-requirements/<job_id>

Admin API:
  POST /api/admin/initialize-questions
```

### 4. **Frontend Templates** ✅

#### `templates/notifications.html`
- Professional notification history page
- Filter tabs (All, Unread)
- Action buttons (Mark all as read, Refresh)
- Real-time unread count badge
- Notification items with dropdown actions (Mark read, Archive, Delete)
- Time ago display
- Action links for related objects
- Auto-refresh every 30 seconds
- Toast notifications for user feedback
- Responsive design

#### `templates/eligibility_form.html`
- Job preview card with details
- Requirements display
- Dynamic form rendering based on question types
- Real-time progress bar
- Multiple field types support:
  - Text inputs
  - Number inputs
  - Checkboxes
  - Select dropdowns
  - Textareas
- Form validation
- Loading spinner
- Error display
- Eligibility validation before submission

### 5. **Seeker Model Enhancement** ✅
Added new field:
- `work_authorization`: Storage for work status (citizen, permanent_resident, visa_sponsored, remote_international)

## Integration Points

### In Existing Routes

Update the swipe/application submission to include eligibility check:

```python
@app.route("/swipe", methods=["POST"])
def swipe():
    # Existing code...
    
    # NEW: Check eligibility before allowing application
    is_eligible, errors = EligibilityService.validate_seeker_eligibility(
        seeker_id, job_id
    )
    
    if not is_eligible:
        return jsonify({"error": "Not eligible", "reasons": errors}), 403
    
    # Continue with existing swipe logic...
```

### In Applicant Update Routes

When company updates application status:

```python
@app.route("/applicant/<int:swipe_id>/<action>")
def update_applicant(swipe_id, action):
    # Update application status...
    
    # NEW: Create notification and send email
    if action == "accept":
        NotificationService.create_notification(
            recipient_id=seeker.id,
            recipient_type='seeker',
            title="Application Accepted! 🎉",
            message=f"Your application for {job.title} has been accepted!",
            notification_type='app_accepted',
            related_job_id=job.id,
            related_company_id=company.id,
            related_application_id=swipe.id,
            action_url=f'/applications/{swipe.id}'
        )
        
        EmailService.send_application_accepted(
            seeker.email,
            seeker.first_name,
            job.title,
            company.company_name,
        )
```

## Database Migration

To apply schema changes, run:

```bash
# Create migration
flask db migrate -m "Add notification and eligibility system"

# Apply migration
flask db upgrade
```

Alternatively, if not using migrations:

```python
with app.app_context():
    db.create_all()
    EligibilityService.create_eligibility_questions()
```

## Frontend Integration: Notification Bell

Add to your base navbar template:

```html
<!-- In templates/base.html navbar -->
<div class="navbar-icons">
    <a href="/notifications" class="nav-icon position-relative">
        <i class="bi bi-bell-fill"></i>
        <span id="notification-badge" class="badge bg-danger position-absolute top-0 start-100 translate-middle" style="display: none;">0</span>
    </a>
</div>

<script>
// Update notification badge every 60 seconds
function updateNotificationBadge() {
    fetch('/api/notifications/unread-count')
        .then(r => r.json())
        .then(data => {
            const badge = document.getElementById('notification-badge');
            if (data.unread_count > 0) {
                badge.textContent = data.unread_count;
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        });
}

setInterval(updateNotificationBadge, 60000);
updateNotificationBadge(); // Call on page load
</script>
```

## Usage Examples

### Create a Notification

```python
from app.services import NotificationService

# For seeker
NotificationService.create_notification(
    recipient_id=seeker_id,
    recipient_type='seeker',
    title='New Job Match!',
    message='We found 3 jobs matching your profile',
    notification_type='new_job_match',
    related_job_id=job_id,
    action_url=f'/job/{job_id}'
)

# For company
NotificationService.create_notification(
    recipient_id=company_id,
    recipient_type='company',
    title='New Application',
    message=f'{seeker_name} applied for {job_title}',
    notification_type='new_application',
    related_job_id=job_id,
    related_seeker_id=seeker_id,
    related_application_id=application_id,
    action_url=f'/applicant/{application_id}'
)
```

### Check Eligibility

```python
from app.services import EligibilityService

# Validate seeker eligibility for job
is_eligible, errors = EligibilityService.validate_seeker_eligibility(
    seeker_id=123,
    job_id=456
)

if not is_eligible:
    print("Reasons for ineligibility:", errors)
    # ["Minimum age requirement: 21 years", "Work authorization not eligible..."]
```

### Send Email Notification

```python
from app.services import EmailService

EmailService.send_application_accepted(
    seeker_email='john@example.com',
    seeker_name='John Doe',
    job_title='Senior Developer',
    company_name='Tech Corp',
    next_steps='We will contact you within 48 hours with interview details.'
)
```

### Update User Preferences

```python
from app.services import NotificationService

NotificationService.update_preferences(
    user_id=123,
    user_type='seeker',
    notify_app_accepted=True,
    notify_interview=True,
    notify_new_jobs=False,
    email_enabled=True,
    email_digest='daily',
    quiet_hours_enabled=True,
    quiet_hours_start='22:00',
    quiet_hours_end='08:00'
)
```

## Configuration

Update your `config.py` with email settings:

```python
class Config:
    # ... existing config ...
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', True)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@careerswipe.com')
```

## Next Steps

### Phase 2: Enhanced Features

1. **Real-time Notifications (WebSocket)**
   - Use Flask-SocketIO for real-time updates
   - Live notification count updates
   - Instant notifications for new applications

2. **Notification Templates**
   - Create reusable notification templates
   - Custom HTML email templates
   - Template variables for dynamic content

3. **Admin Dashboard**
   - Monitor notification metrics
   - View all notifications across platform
   - Analytics on application flow

4. **Mobile App Support**
   - Push notifications
   - Mobile-friendly notification UI
   - Notification preferences for mobile

### Phase 3: Analytics & Optimization

1. **Notification Analytics**
   - Track notification open rates
   - Monitor email delivery
   - Analyze user engagement

2. **Performance Optimization**
   - Database query optimization
   - Caching for frequently accessed data
   - Background job processing (Celery)

3. **A/B Testing**
   - Test notification copy variations
   - Optimize email subject lines
   - Personalization strategies

## Troubleshooting

### Notifications not appearing
- Check that notification preferences are enabled
- Verify user_id and user_type are correct
- Check database for notification records

### Eligibility validation failing
- Verify all required questions are answered
- Check work authorization field is set on seeker
- Review job requirements for accuracy

### Emails not sending
- Verify MAIL_SERVER and credentials in config
- Check MAIL_DEFAULT_SENDER is set
- Review Flask-Mail initialization
- Check email exception logs

## Best Practices

1. **Always use services** - Don't create notifications directly; use NotificationService
2. **Check preferences** - Use NotificationService.should_notify() before creating notifications
3. **Batch operations** - Use bulk methods for multiple operations
4. **Error handling** - All service methods include error handling; check return values
5. **Email throttling** - Consider rate limiting for bulk emails
6. **Database indexing** - Ensure indexes on frequently queried fields:
   - notifications.recipient_id
   - notifications.recipient_type
   - notifications.created_at
   - eligibility_answers.seeker_id
   - eligibility_answers.job_id

## Files Modified/Created

### New Files
- `app/models/eligibility_question.py`
- `app/models/eligibility_answer.py`
- `app/models/job_requirements.py`
- `app/models/interview_invite.py`
- `app/models/notification_preference.py`
- `app/routes/eligibility.py`
- `templates/eligibility_form.html`

### Modified Files
- `app/models/notification.py` (Enhanced)
- `app/models/seeker.py` (Added work_authorization)
- `app/services/notification_service.py` (Refactored)
- `app/services/email_service.py` (Enhanced)
- `app/routes/notifications.py` (Refactored)
- `templates/notifications.html` (Redesigned)
- `app.py` (Blueprint registration)

## Support

For issues or questions:
1. Check the implementation logs
2. Verify database migrations have run
3. Test API endpoints using curl or Postman
4. Review error messages in terminal output
