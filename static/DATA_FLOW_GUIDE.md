# CareerSwipe Data Flow & Visualization Guide

## 📊 WHERE DATA COMES FROM

### **1. SEEKERS Table** 
**Data Entry Points:**
- `/upload-resume` → Resume upload & parsing
- `/register/seeker` → Manual registration form
- `/profile/seeker` → Profile updates

**Data Captured:**
```
first_name, last_name, email, phone, address, 
education, experience, skills, resume_path,
gender, dob, job_status, career_field, desired_roles, 
salary_expectation, availability, etc.
```

---

### **2. COMPANIES Table**
**Data Entry Points:**
- `/register/company` → Company registration form

**Data Captured:**
```
company_name, email, password_hash, description, 
industry, website, logo_path, is_verified, created_at
```

---

### **3. JOB_LISTINGS Table**
**Data Entry Points:**
- `/jobs/post` → Company posts a job (from POST form)
- Stored in company dashboard (visible in screenshot)

**Data Captured:**
```
company_id (FK), title, description, required_skills,
location, job_type, job_location_type, salary, max_salary,
experience_level, min_experience, tags, is_boosted, created_at
```

**Example from your screenshot:**
- Job: "jma" in Kathmandu, 500000/month, Full-time, Onsite
- Job: "React" in Kathmandu, 500000/month, Full-time, Onsite

---

### **4. JOB_SWIPES Table** (Applications)
**Data Entry Points:**
- `/swipe` (POST API) → Seeker swipes left/right on job

**Data Captured:**
```
seeker_id (FK), job_id (FK), direction (left/right),
status (pending/shortlisted/interview/accepted/rejected),
match_score, ats_score, ai_rank_score, created_at
```

**Flow:**
1. Seeker swipes RIGHT → Application created
2. Email sent to company + seeker
3. Company sees applicant in dashboard
4. Company updates status → Seeker gets notification

---

### **5. NOTIFICATIONS Table**
**Data Entry Points:**
- Triggered by events:
  - `/swipe` → "New applicant" notification for company
  - `/applicant/<id>/accept|reject|interview` → Status update notification

**Data Captured:**
```
user_id, user_type (seeker/company), message, 
type (application/accepted/rejected/interview/system),
is_read, created_at
```

---

## 🎨 VISUALIZATION OPTIONS

### **Option 1: HTML Dashboard (Ready Now!)**
- **File:** `static/dashboard.html`
- **What it shows:** 
  - Total seekers, companies, jobs, applications
  - Application status distribution (pie chart)
  - Platform overview (bar chart)
- **How to use:** Open in browser, auto-refreshes
- **Pros:** No database access needed, visual charts
- **Cons:** Shows summary only, schema errors hidden

---

### **Option 2: Flask Shell (Interactive)**
```bash
flask shell
>>> from models import *
>>> Seeker.query.all()
>>> Company.query.all()
>>> JobSwipe.query.filter_by(direction='right').all()
```
**What you can do:**
- Query any table directly
- Filter by conditions
- Export data to CSV

---

### **Option 3: SQL Viewer Tools**

#### **For SQLite (Local):**
```bash
# Install
pip install sqlitebrowser

# Open database
sqlitebrowser careerswipe.db
```

#### **For PostgreSQL (Render):**
```bash
# Install pgAdmin
# Or use web-based tools:
# - pgAdmin4 (online)
# - DBeaver (desktop)
# - adminer.org (simple web interface)
```

---

### **Option 4: Python Pandas Analysis**
Create `analyze_db.py`:
```python
import pandas as pd
from app import app
from models import *

with app.app_context():
    # Query data
    seekers_df = pd.read_sql_table('seekers', db.engine)
    jobs_df = pd.read_sql_table('job_listings', db.engine)
    swipes_df = pd.read_sql_table('job_swipes', db.engine)
    
    # Analyze
    print(seekers_df.describe())
    print("Top skills:")
    print(seekers_df['skills'].value_counts().head(10))
    
    # Export
    swipes_df.to_csv('applications.csv', index=False)
```

Run: `python analyze_db.py`

---

### **Option 5: Add Database Admin Panel to Flask**

Install Flask-Admin:
```bash
pip install flask-admin
```

Add to `app.py`:
```python
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

admin = Admin(app, name='CareerSwipe Admin', template_mode='bootstrap4')
admin.add_view(ModelView(Seeker, db.session))
admin.add_view(ModelView(Company, db.session))
admin.add_view(ModelView(JobListing, db.session))
admin.add_view(ModelView(JobSwipe, db.session))
admin.add_view(ModelView(Notification, db.session))
```

Then visit: `http://localhost:5000/admin`

---

## 🔧 FIX SCHEMA MISMATCH

Your error: `column seekers.address does not exist`

This means your production database is outdated.

### **Solution:**
```bash
# 1. Generate migration
flask db migrate -m "sync schema"

# 2. Review migrations/versions/latest_file.py

# 3. Apply migration
flask db upgrade
```

Or manually in SQL:
```sql
ALTER TABLE seekers ADD COLUMN address VARCHAR(500);
ALTER TABLE seekers ADD COLUMN gender VARCHAR(20);
-- etc for all missing columns
```

---

## 📈 RECOMMENDED SETUP FOR MONITORING

**For Development:**
```bash
python visualize_db.py    # Generate dashboard
flask shell              # For quick queries
```

**For Production:**
Install both:
```bash
pip install flask-admin flask-marshmallow
```

Then set up admin panel in Flask app.

---

## 📊 SAMPLE QUERIES

```python
# Most applied jobs
top_jobs = db.session.query(
    JobListing.title, 
    func.count(JobSwipe.id).label('applications')
).join(JobSwipe).group_by(JobListing.id).order_by(desc(func.count(JobSwipe.id))).limit(10)

# Acceptance rate by company
acceptance_rate = db.session.query(
    Company.company_name,
    func.count(JobSwipe.id).label('total'),
    func.count(JobSwipe.status == 'accepted').label('accepted')
).join(JobListing).join(JobSwipe).group_by(Company.id)

# Seekers by career field
seekers_by_field = Seeker.query.with_entities(
    Seeker.career_field, 
    func.count(Seeker.id)
).group_by(Seeker.career_field)
```

---

## 🚀 NEXT STEPS

1. ✅ **View dashboard:** Open `static/dashboard.html`
2. **Fix schema:** Run `flask db upgrade`
3. **Set up admin:** Add Flask-Admin for easy management
4. **Monitor data:** Use cron job to generate dashboard daily
