# CareerSwipe Backend - Complete Implementation Guide

> **Built for Production on Render with PostgreSQL**

## 📊 Database Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │    SEEKERS       │      │   EMPLOYERS      │            │
│  ├──────────────────┤      ├──────────────────┤            │
│  │ id (PK)          │      │ id (PK)          │            │
│  │ first_name       │      │ company_name     │            │
│  │ last_name        │      │ email (UNIQUE)   │            │
│  │ email (UNIQUE)   │      │ password_hash    │            │
│  │ password_hash    │      │ phone            │            │
│  │ phone            │      │ company_address  │            │
│  │ address          │      │ industry         │            │
│  │ career_field     │      │ created_at       │            │
│  │ experience_type  │      │ ... (5 more)     │            │
│  │ ... (11 more)    │      └──────────────────┘            │
│  └────────┬─────────┘            │                         │
│           │                      │ (1:N)                   │
│           │                      ▼                         │
│           │            ┌──────────────────┐               │
│           │            │      JOBS        │               │
│           │            ├──────────────────┤               │
│           │            │ id (PK)          │               │
│           │            │ employer_id (FK) │               │
│           │            │ title            │               │
│           │            │ description      │               │
│           │            │ location         │               │
│           │            │ salary           │               │
│           │            │ job_type         │               │
│           │            │ experience_req   │               │
│           │            │ created_at       │               │
│           │            └────────┬─────────┘               │
│           │                     │                         │
│           │ (N:N via APPS)      │ (1:N)                   │
│           │                     │                         │
│           └─────────┬───────────┘                         │
│                     │                                     │
│                     ▼                                     │
│          ┌──────────────────────┐                        │
│          │    APPLICATIONS      │                        │
│          ├──────────────────────┤                        │
│          │ id (PK)              │                        │
│          │ seeker_id (FK)       │                        │
│          │ job_id (FK)          │                        │
│          │ status               │                        │
│          │ applied_at           │                        │
│          │ UNIQUE(seeker, job)  │                        │
│          └──────────────────────┘                        │
│                                                         │
│          ┌──────────────────────┐                        │
│          │   NOTIFICATIONS      │                        │
│          ├──────────────────────┤                        │
│          │ id (PK)              │                        │
│          │ user_id              │                        │
│          │ user_type            │                        │
│          │ message              │                        │
│          │ type                 │                        │
│          │ is_read              │                        │
│          │ created_at           │                        │
│          └──────────────────────┘                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 🏗️ Folder Structure

```
career-swipe/
├── backend/                          # NEW: Backend application
│   ├── __init__.py                   # Package initialization
│   ├── app.py                        # Flask application factory
│   ├── config.py                     # Configuration management
│   ├── requirements.txt              # Backend dependencies
│   │
│   ├── models/                       # Database models (SQLAlchemy ORM)
│   │   ├── __init__.py
│   │   ├── seeker.py                 # Seeker model
│   │   ├── employer.py               # Employer model
│   │   ├── job.py                    # Job listing model
│   │   ├── application.py            # Job application model
│   │   └── notification.py           # Notification model
│   │
│   ├── controllers/                  # Business logic
│   │   ├── __init__.py
│   │   ├── auth_controller.py        # Authentication logic
│   │   ├── job_controller.py         # Job management logic
│   │   └── application_controller.py # Application logic
│   │
│   └── routes/                       # API endpoints
│       ├── __init__.py
│       ├── auth_routes.py            # /api/auth/* endpoints
│       ├── job_routes.py             # /api/jobs/* endpoints
│       └── application_routes.py     # /api/applications/* endpoints
│
├── wsgi.py                           # NEW: WSGI entry for production
├── schema.sql                        # NEW: PostgreSQL schema
├── .env.example                      # NEW: Environment template
├── render.yaml                       # NEW: Render deployment config
│
├── BACKEND_SETUP.md                  # NEW: Setup instructions
├── RENDER_DEPLOYMENT_CHECKLIST.md    # NEW: Deployment guide
├── API_QUICK_REFERENCE.md            # NEW: API examples
│
├── requirements.txt                  # Main requirements
├── app.py                            # Main Flask app (keep for legacy)
├── extensions.py                     # Extensions (db, migrate, mail)
├── models.py                         # Legacy models (updated)
├── config.py                         # Legacy config
│
├── migrations/                       # Database migrations
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│
├── templates/                        # HTML templates (unchanged)
├── static/                           # Static files (CSS, JS)
└── utils/                            # Utility modules
```

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment
```bash
cp .env.example .env
# Edit .env with your database URL
```

### 3. Initialize Database
```bash
python -c "from backend.app import app; app.app_context().push(); from extensions import db; db.create_all()"
```

### 4. Run Backend
```bash
python backend/app.py
```

### 5. Test API
```bash
curl http://localhost:5000/api/health
```

## 📡 API Architecture

### RESTful Endpoints

```
Authentication
├── POST   /api/auth/register/seeker     → Register job seeker
├── POST   /api/auth/register/employer   → Register company
├── POST   /api/auth/login/seeker        → Seeker login
└── POST   /api/auth/login/employer      → Employer login

Jobs
├── POST   /api/jobs                     → Create job (employer)
├── GET    /api/jobs                     → List all jobs
├── GET    /api/jobs/:id                 → Get job details
├── GET    /api/jobs/employer/:id        → Get employer's jobs
├── PUT    /api/jobs/:id                 → Update job
└── DELETE /api/jobs/:id                 → Delete job

Applications
├── POST   /api/applications             → Apply to job (seeker)
├── GET    /api/applications/seeker/:id  → Get seeker's applications
├── GET    /api/applications/job/:id     → Get job applications (employer)
├── GET    /api/applications/:id         → Get application details
└── PUT    /api/applications/:id/status  → Update status (employer)

System
└── GET    /api/health                   → Health check
```

### Request/Response Format

**Success Response**
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

**Error Response**
```json
{
  "success": false,
  "message": "Error description",
  "error": "Additional details"
}
```

## 🔐 Security Features

- ✅ **Password Hashing**: Bcrypt with salt
- ✅ **Email Validation**: Regex pattern validation
- ✅ **Unique Constraints**: Email, seeker-job combination
- ✅ **CORS Protection**: Configured for specific origins
- ✅ **SQL Injection Prevention**: SQLAlchemy ORM
- ✅ **Error Handling**: Generic error messages
- ✅ **Authorization**: User ownership verification
- ✅ **SSL/TLS**: Configured for production

## 📊 Database Indexes

For optimal query performance:

```sql
-- Seekers
CREATE INDEX idx_seekers_email ON seekers(email);
CREATE INDEX idx_seekers_created_at ON seekers(created_at);

-- Employers
CREATE INDEX idx_employers_email ON employers(email);
CREATE INDEX idx_employers_created_at ON employers(created_at);

-- Jobs
CREATE INDEX idx_jobs_employer_id ON jobs(employer_id);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);

-- Applications
CREATE INDEX idx_applications_seeker_id ON applications(seeker_id);
CREATE INDEX idx_applications_job_id ON applications(job_id);
CREATE INDEX idx_applications_status ON applications(status);

-- Notifications
CREATE INDEX idx_notifications_user ON notifications(user_id, user_type);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
```

## 🔄 Data Flow Examples

### User Registration Flow
```
User Form → Frontend → API POST /auth/register/seeker
   ↓
Backend validates input
   ↓
Hash password with bcrypt
   ↓
Insert into seekers table
   ↓
Return success + seeker_id
   ↓
Frontend stores user session
```

### Job Application Flow
```
Seeker views job → Click "Apply"
   ↓
Frontend POST /applications
   ↓
Backend validates seeker & job exist
   ↓
Check for duplicate application
   ↓
Insert into applications table
   ↓
Create notification for employer
   ↓
Return success
   ↓
Frontend shows confirmation
   ↓
Employer sees notification on dashboard
```

### Application Status Update Flow
```
Employer reviews applications
   ↓
Click "Shortlist" button
   ↓
Frontend PUT /applications/:id/status
   ↓
Backend validates employer owns job
   ↓
Update status in database
   ↓
Create notification for seeker
   ↓
Return success
   ↓
Seeker receives notification
```

## 🛠️ Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Backend** | Flask | 3.0.3 |
| **ORM** | SQLAlchemy | 2.0+ |
| **Database** | PostgreSQL | 14+ |
| **Server** | Gunicorn | 22+ |
| **Security** | Bcrypt | 4.1+ |
| **Deployment** | Render | - |
| **DevOps** | Docker (optional) | - |

## 📈 Performance Considerations

### Queries Optimization
```python
# ❌ Bad: N+1 query problem
jobs = Job.query.all()
for job in jobs:
    employer = Employer.query.get(job.employer_id)  # Extra query!

# ✅ Good: Join query
jobs = Job.query.join(Employer).all()
```

### Connection Pool
```python
# Configured in config.py:
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_size": 10,
    "max_overflow": 20
}
```

### Indexing Strategy
- All foreign keys are indexed
- All frequently-searched columns (email) are indexed
- Compound indexes for common queries

## 🔍 Debugging

### Enable SQL Logging
```python
# In config.py:
SQLALCHEMY_ENGINE_OPTIONS = {
    "echo": True  # Prints all SQL queries
}
```

### Check Flask Debug Mode
```python
app.run(debug=True)  # Enables auto-reload and better errors
```

### View Database
```bash
# Using DBeaver
# Connect to External PostgreSQL URL
# Browse schema → public → tables
```

## 🧪 Testing Checklist

- [ ] Register seeker with valid data
- [ ] Register seeker with invalid email (should fail)
- [ ] Register seeker with duplicate email (should fail)
- [ ] Login with correct credentials
- [ ] Login with wrong password (should fail)
- [ ] Employer posts job
- [ ] List all jobs
- [ ] Seeker applies to job
- [ ] Seeker applies again (should fail - duplicate)
- [ ] Employer views applications
- [ ] Employer updates application status
- [ ] Verify notifications are created

## 📚 Additional Resources

### Documentation Files
- **[BACKEND_SETUP.md](./BACKEND_SETUP.md)** - Setup instructions
- **[RENDER_DEPLOYMENT_CHECKLIST.md](./RENDER_DEPLOYMENT_CHECKLIST.md)** - Deployment guide
- **[API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md)** - API examples
- **[schema.sql](./schema.sql)** - Database schema

### External Links
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Render Docs](https://render.com/docs)
- [DBeaver Tutorial](https://dbeaver.com/docs/dbeaver)

## 🎯 Next Steps

1. **Local Testing**: Set up locally and test all endpoints
2. **Database**: Verify with DBeaver all tables exist
3. **Deployment**: Follow RENDER_DEPLOYMENT_CHECKLIST.md
4. **Frontend Integration**: Update frontend to call new API
5. **Monitoring**: Set up alerts and logging
6. **Scaling**: Plan for growth (caching, load balancing, etc.)

## 📞 Common Questions

**Q: Can I use SQLite in production?**
A: No, use PostgreSQL on Render. SQLite is only for local development.

**Q: How do I access the database from outside Render?**
A: Use the **External Database URL** from Render PostgreSQL dashboard in DBeaver.

**Q: Do I need to run migrations manually?**
A: No, `db.create_all()` runs automatically on startup. Use Flask-Migrate for schema changes.

**Q: How do I reset the database?**
A: Drop all tables: `db.drop_all()` then `db.create_all()`

**Q: Can I modify existing tables?**
A: Yes, create a migration: `flask db migrate -m "description"` then `flask db upgrade`

---

## ✅ Deployment Success Checklist

Before going live:

- [ ] Backend runs locally without errors
- [ ] All endpoints tested with sample data
- [ ] Database tables created and visible
- [ ] Environment variables configured
- [ ] DBeaver can connect to database
- [ ] Render web service deployed
- [ ] Health check endpoint working
- [ ] No database errors in logs
- [ ] API responses are fast (< 500ms)
- [ ] Frontend integrated with backend API

---

**Version**: 1.0.0
**Last Updated**: April 2026
**Status**: ✅ Production Ready
