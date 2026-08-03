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
 # CareerSwipe Backend Setup & Deployment Guide

## 📋 Table of Contents
1. [Backend Architecture](#backend-architecture)
2. [Local Setup (Development)](#local-setup-development)
3. [Render Deployment](#render-deployment)
4. [Database Configuration](#database-configuration)
5. [API Endpoints](#api-endpoints)
6. [Database Verification (DBeaver)](#database-verification-dbeaver)
7. [Troubleshooting](#troubleshooting)

---

## 🏗️ Backend Architecture

The backend follows a professional **MVC (Model-View-Controller)** pattern:

```
backend/
├── app.py              # Main Flask application
├── config.py           # Configuration management
├── models/             # Database models
│   ├── __init__.py
│   ├── seeker.py       # Job seekers
│   ├── employer.py     # Companies
│   ├── job.py          # Job listings
│   ├── application.py  # Job applications
│   └── notification.py # Notifications
├── controllers/        # Business logic
│   ├── __init__.py
│   ├── auth_controller.py
│   ├── job_controller.py
│   └── application_controller.py
└── routes/             # API endpoints
    ├── __init__.py
    ├── auth_routes.py
    ├── job_routes.py
    └── application_routes.py
```

### Technology Stack
- **Framework**: Flask
- **Database**: PostgreSQL (production) / SQLite (development)
- **ORM**: SQLAlchemy
- **Migrations**: Flask-Migrate
- **Authentication**: Bcrypt password hashing
- **Server**: Gunicorn (production)

---

## 🚀 Local Setup (Development)

### Prerequisites
- Python 3.8+
- PostgreSQL (optional for local dev, SQLite works too)
- pip or poetry
- Git

### Step 1: Clone & Setup Virtual Environment

```bash
cd c:\Users\VICTUS\Desktop\career-swipe

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
# For local development, you can use SQLite (default)
# Or setup local PostgreSQL
```

**For SQLite (simplest for development):**
```
# In .env, leave DATABASE_URL commented or not set
# It will default to sqlite:///careerswipe.db
```

**For PostgreSQL (recommended for production-like testing):**
```sql
-- Create database (run in PostgreSQL):
CREATE DATABASE careerswipe_db;
CREATE USER careerswipe_user WITH PASSWORD 'password123';
ALTER ROLE careerswipe_user SET client_encoding TO 'utf8';
ALTER ROLE careerswipe_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE careerswipe_user SET default_transaction_deferrable TO on;
ALTER ROLE careerswipe_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE careerswipe_db TO careerswipe_user;
```

Then in `.env`:
```
DATABASE_URL=postgresql://careerswipe_user:password123@localhost:5432/careerswipe_db
```

### Step 4: Initialize Database

```bash
# Create all tables
flask db upgrade

# Or if not using migrations:
python -c "from backend.app import app; app.app_context().push(); from extensions import db; db.create_all()"
```

### Step 5: Run Backend Server

```bash
python backend/app.py
```

You should see:
```
╔════════════════════════════════════════════════════╗
║           CareerSwipe Backend Server               ║
╠════════════════════════════════════════════════════╣
║ Environment: development                           ║
║ Database: sqlite:///careerswipe.db                 ║
║ Debug Mode: True                                   ║
║ API Base URL: http://localhost:5000/api             ║
║ Health Check: http://localhost:5000/api/health     ║
╚════════════════════════════════════════════════════╝
```

### Step 6: Test the Backend

```bash
# In another terminal/PowerShell:
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "CareerSwipe Backend",
  "version": "1.0.0"
}
```

---

## 🎯 Render Deployment

### Step 1: Prepare Render PostgreSQL Database

1. Go to [Render.com](https://render.com)
2. Create a new PostgreSQL database:
   - Name: `careerswipe-db`
   - Plan: Free tier (for testing) or paid
   - Region: Choose closest to you
3. Wait for database to be created
4. Copy the **Internal Database URL** (for connections within Render)

### Step 2: Create a Render Web Service

1. Click **New +** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `careerswipe-backend`
   - **Environment**: Python 3
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     gunicorn backend.app:app
     ```
   - **Plan**: Free tier or paid

### Step 3: Add Environment Variables

In Render dashboard, go to Environment:

```
FLASK_ENV=production
SECRET_KEY=<generate-strong-random-key>
DATABASE_URL=postgresql://user:password@dpg-xxxxx.postgres.render.com:5432/careerswipe_db
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
```

### Step 4: Deploy

1. Push code to GitHub
2. Render automatically deploys
3. Check deployment logs in Render dashboard
4. Access at: `https://careerswipe-backend.onrender.com`

### Step 5: Run Database Migrations (if needed)

```bash
# In Render shell or via SSH:
flask db upgrade
```

---

## 🗄️ Database Configuration

### PostgreSQL Connection Details

**Local Development:**
```
Host: localhost
Port: 5432
Database: careerswipe_db
User: careerswipe_user
Password: your_password
```

**Render Production:**
- **Internal URL** (for services within Render):
  ```
  postgresql://user:password@dpg-xxxxx.postgres.render.com:5432/careerswipe_db
  ```
- **External URL** (for external tools like DBeaver):
  - Found in Render dashboard → Database → "External Database URL"
  - Uses: `dpg-xxxxx.c.postgres.render.com` (external host)

### Database Tables

All tables are automatically created on first run. Tables include:

1. **seekers** - Job seekers/candidates
2. **employers** - Companies
3. **jobs** - Job listings
4. **applications** - Job applications
5. **notifications** - User notifications

See `schema.sql` for complete schema with all columns.

---

## 🔌 API Endpoints

### Authentication APIs

#### Register Seeker
```http
POST /api/auth/register/seeker
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "password": "password123",
  "phone": "555-0001",
  "career_field": "IT"
}
```

Response:
```json
{
  "success": true,
  "message": "Seeker registered successfully",
  "seeker_id": 1
}
```

#### Register Employer
```http
POST /api/auth/register/employer
Content-Type: application/json

{
  "company_name": "Tech Corp",
  "email": "tech@example.com",
  "password": "password123",
  "phone": "555-1001",
  "industry": "IT"
}
```

#### Login Seeker
```http
POST /api/auth/login/seeker
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "success": true,
  "message": "Login successful",
  "seeker": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    ...
  }
}
```

### Job APIs

#### Create Job (Employer only)
```http
POST /api/jobs
Content-Type: application/json

{
  "employer_id": 1,
  "title": "Senior Developer",
  "description": "Looking for experienced developers...",
  "location": "New York, NY",
  "salary": "$120,000 - $150,000",
  "job_type": "Full-time",
  "experience_required": "Senior"
}
```

#### Get All Jobs
```http
GET /api/jobs?limit=20&offset=0
```

#### Get Job by ID
```http
GET /api/jobs/1
```

#### Get Employer's Jobs
```http
GET /api/jobs/employer/1?limit=20&offset=0
```

#### Update Job
```http
PUT /api/jobs/1
Content-Type: application/json

{
  "employer_id": 1,
  "title": "Updated Title",
  ...
}
```

#### Delete Job
```http
DELETE /api/jobs/1
Content-Type: application/json

{
  "employer_id": 1
}
```

### Application APIs

#### Apply to Job
```http
POST /api/applications
Content-Type: application/json

{
  "seeker_id": 1,
  "job_id": 1
}
```

#### Get Seeker's Applications
```http
GET /api/applications/seeker/1?limit=20&offset=0
```

#### Get Job's Applications (Employer only)
```http
GET /api/applications/job/1?employer_id=1&limit=20&offset=0
```

#### Update Application Status
```http
PUT /api/applications/1/status
Content-Type: application/json

{
  "employer_id": 1,
  "job_id": 1,
  "status": "shortlisted"
}
```

Valid statuses: `pending`, `shortlisted`, `rejected`, `interview`, `accepted`

#### Get Application Details
```http
GET /api/applications/1?user_id=1&user_type=seeker
```

---

## 🔍 Database Verification (DBeaver)

### Step 1: Download DBeaver
- Download from [dbeaver.io](https://dbeaver.io)
- Install and open

### Step 2: Create New Connection

1. File → New Database Connection
2. Select **PostgreSQL**
3. Click **Next**

### Step 3: Configure Connection

**For Local Development:**
```
Server Host: localhost
Port: 5432
Database: careerswipe_db
Username: careerswipe_user
Password: [your_password]
```

Click **Test Connection** → Should say "Connected"

**For Render Production:**
```
Server Host: dpg-xxxxx.c.postgres.render.com
Port: 5432
Database: careerswipe_db
Username: [render_user]
Password: [render_password]
```

Get these from Render → Database → "External Database URL"

Example External URL format:
```
postgresql://user:password@dpg-xxxxx.c.postgres.render.com:5432/careerswipe_db
```

### Step 4: Verify Tables

1. After connecting, expand the database in left panel
2. Navigate to: **careerswipe_db** → **Schemas** → **public** → **Tables**
3. You should see:
   - `seekers`
   - `employers`
   - `jobs`
   - `applications`
   - `notifications`

### Step 5: Query Tables

Right-click any table → **SQL** → **SELECT Rows**

Example:
```sql
SELECT * FROM seekers;
SELECT * FROM employers;
SELECT * FROM jobs;
SELECT * FROM applications;
```

### Step 6: Check Data Types

Right-click table → **Properties** to verify:
- All expected columns exist
- Data types are correct
- Constraints are in place (PRIMARY KEY, FOREIGN KEY, UNIQUE)

---

## 🆘 Troubleshooting

### Issue: Database Connection Error

**Error**: `FATAL: password authentication failed`

**Solution**:
1. Check DATABASE_URL in .env is correct
2. Verify username and password
3. For Render: Use **Internal URL** from database, not external

### Issue: Table Does Not Exist

**Error**: `relation "seekers" does not exist`

**Solution**:
```bash
# Reinitialize database:
python -c "from backend.app import app; app.app_context().push(); from extensions import db; db.create_all()"

# Or using migrations:
flask db upgrade
```

### Issue: Render Deployment Fails

**Solution**:
1. Check build logs in Render dashboard
2. Verify `requirements.txt` has all dependencies
3. Ensure `start command` is correct: `gunicorn backend.app:app`
4. Check environment variables are set

### Issue: Cannot Connect from DBeaver

**Error**: `Connection refused` or `timeout`

**Solution**:
1. For local: Ensure PostgreSQL service is running
2. For Render: Make sure database is in **Available** state
3. Use **External URL** for remote connections (not Internal URL)
4. Check firewall/network settings

### Issue: "No Module Named Backend"

**Error**: `ModuleNotFoundError: No module named 'backend'`

**Solution**:
1. Ensure `backend/` folder exists at root level
2. Add `__init__.py` to all directories
3. Run from project root: `python backend/app.py`

### Issue: Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Kill process on port 5000:
# Windows:
netstat -ano | findstr :5000
taskkill /PID [pid_number] /F

# macOS/Linux:
lsof -ti:5000 | xargs kill -9
```

---

## 📝 Summary Checklist

- [ ] Virtual environment created and activated
- [ ] Requirements installed: `pip install -r requirements.txt`
- [ ] .env file configured with database URL
- [ ] Database created and accessible
- [ ] Backend server runs locally: `python backend/app.py`
- [ ] Health check responds: `curl http://localhost:5000/api/health`
- [ ] DBeaver can connect to database
- [ ] All 5 tables visible in DBeaver
- [ ] Render PostgreSQL database created
- [ ] Render web service configured with correct environment variables
- [ ] Backend deployed to Render: `https://[app-name].onrender.com`
- [ ] API endpoints tested with sample registration/login

---

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review Render logs: Render Dashboard → Your App → Logs
3. Verify database connectivity with DBeaver
4. Check Flask debug output for error messages

---

**Last Updated**: April 2026
**Version**: 1.0.0
//done