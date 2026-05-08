# Render Deployment Checklist for CareerSwipe Backend

## Pre-Deployment (Local Testing)

- [ ] Clone project and create virtual environment
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Configure `.env` file with test database
- [ ] Run migrations: `flask db upgrade`
- [ ] Start backend: `python backend/app.py`
- [ ] Test health endpoint: `curl http://localhost:5000/api/health`
- [ ] Test register endpoint: Create a test seeker/employer
- [ ] Test login endpoint: Login with created account
- [ ] Verify database tables exist: `db.create_all()`
- [ ] Commit all changes to GitHub

## Render Setup (First Time)

### 1. Create Render Account
- [ ] Go to [render.com](https://render.com)
- [ ] Sign up with GitHub account
- [ ] Authorize Render to access your repositories

### 2. Create PostgreSQL Database
- [ ] Click **New +** → **PostgreSQL**
- [ ] Configure:
  - Name: `careerswipe-postgres` or similar
  - Database: `careerswipe_db`
  - User: `careerswipe_user`
  - Region: Choose closest to you
  - Plan: Free (for testing) or paid
- [ ] Create database
- [ ] Wait for **"Available"** status (2-3 minutes)
- [ ] Copy **Internal Database URL** (for connections within Render)
- [ ] Copy **External Database URL** (for DBeaver, local testing)

### 3. Create Web Service
- [ ] Click **New +** → **Web Service**
- [ ] Select GitHub repository
- [ ] Configure:
  - **Name**: `careerswipe-backend`
  - **Environment**: Python
  - **Branch**: `main` (or your primary branch)
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `gunicorn backend.app:app`
  - **Plan**: Free (for testing) or paid
  - **Instance Type**: Standard
- [ ] Click **Create Web Service**

### 4. Add Environment Variables
- [ ] Go to Web Service → **Environment**
- [ ] Add variables:

```
FLASK_ENV=production
SECRET_KEY=[generate strong random key - at least 32 characters]
DATABASE_URL=[Paste Internal PostgreSQL URL from step 2]
DEBUG=False
```

**How to generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Deploy
- [ ] Check the **Logs** tab for build status
- [ ] Wait for "Your service is live" message
- [ ] Copy the URL: `https://careerswipe-backend.onrender.com`
- [ ] Test: Visit `https://careerswipe-backend.onrender.com/api/health`

## Post-Deployment Verification

### 1. Test Backend Health
```bash
curl https://careerswipe-backend.onrender.com/api/health
```

Expected: `{"status": "healthy", "service": "CareerSwipe Backend", "version": "1.0.0"}`

### 2. Test Database Connection
The backend should automatically create tables on first run. Check Render logs:
1. Go to Web Service → **Logs**
2. Look for: `✓ Database tables created/verified successfully`

### 3. Run Database Migrations (if needed)
```bash
# SSH into Render (if available) or use Render Shell:
flask db upgrade
```

### 4. Connect with DBeaver (External Access)
1. Open DBeaver
2. Create New Connection → PostgreSQL
3. Use **External Database URL** from Render PostgreSQL dashboard
4. Test connection
5. Verify tables exist: seekers, employers, jobs, applications, notifications

### 5. Test API Endpoints
```bash
# Register seeker
curl -X POST https://careerswipe-backend.onrender.com/api/auth/register/seeker \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","email":"john@test.com","password":"Password123"}'

# Register employer
curl -X POST https://careerswipe-backend.onrender.com/api/auth/register/employer \
  -H "Content-Type: application/json" \
  -d '{"company_name":"Test Corp","email":"corp@test.com","password":"Password123"}'

# Get jobs
curl https://careerswipe-backend.onrender.com/api/jobs?limit=10
```

## Maintenance & Monitoring

### Regular Checks
- [ ] **Weekly**: Review Render logs for errors
- [ ] **Weekly**: Test critical endpoints
- [ ] **Monthly**: Backup database
- [ ] **Monthly**: Review application security logs

### Monitoring Dashboard
- Visit: `https://dashboard.render.com`
- Monitor:
  - Web Service status
  - Resource usage (CPU, memory)
  - Build logs
  - Network metrics
  - Database availability

### Update Database
To update database (e.g., add columns):
1. Create new migration: `flask db migrate -m "description"`
2. Edit migration file in `migrations/versions/`
3. Push to GitHub
4. Render auto-deploys
5. Migrations apply on startup (if configured)

## Troubleshooting Checklist

### Deployment Won't Complete
- [ ] Check build logs for errors
- [ ] Ensure `requirements.txt` has all dependencies
- [ ] Verify `gunicorn` is installed: `pip install gunicorn`
- [ ] Check start command syntax: `gunicorn backend.app:app`

### Database Connection Fails
- [ ] Verify DATABASE_URL format is correct
- [ ] Check Internal URL is used (not External) in environment
- [ ] Confirm PostgreSQL database is in **Available** status
- [ ] Check username and password are correct

### Tables Don't Exist
- [ ] Check web service logs: `✓ Database tables created/verified`
- [ ] Manually run: `flask db upgrade`
- [ ] Or execute `schema.sql` against database

### API Endpoints Return 500 Error
- [ ] Check web service logs for stack trace
- [ ] Verify all model imports are correct
- [ ] Ensure database connection is working
- [ ] Check for missing required environment variables

### Can't Connect with DBeaver
- [ ] Use **External Database URL** (not Internal)
- [ ] Check PostgreSQL status is **Available**
- [ ] Verify firewall allows connections
- [ ] Test with: `psql -U user -h host -d database`

### Memory or CPU Issues
- [ ] Check Render metrics dashboard
- [ ] Consider upgrading from free to paid plan
- [ ] Optimize database queries
- [ ] Add database indexes

## Monitoring Script (Optional)

Create a `monitor.sh` to check service health:

```bash
#!/bin/bash
BACKEND_URL="https://careerswipe-backend.onrender.com"
HEALTH_ENDPOINT="$BACKEND_URL/api/health"

# Check health
response=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_ENDPOINT)

if [ $response -eq 200 ]; then
    echo "[$(date)] ✓ Backend is healthy"
else
    echo "[$(date)] ✗ Backend returned status $response"
    # Send alert (email, Slack, etc.)
fi
```

Run with cron:
```bash
# Check every 5 minutes
*/5 * * * * /path/to/monitor.sh >> /var/log/monitor.log 2>&1
```

## Emergency Procedures

### Service Down
1. Check Render dashboard status
2. View logs for error messages
3. Verify database is still available
4. Restart web service: Dashboard → Web Service → "Deploy latest commit"
5. If database is down, wait for Render to recover or contact support

### Database Issues
1. Create backup of data (if possible)
2. Check Render PostgreSQL dashboard
3. Review PostgreSQL logs
4. Consider restoring from backup
5. Contact Render support if persistent

### Security Incident
1. Rotate `SECRET_KEY` immediately
2. Rotate database password
3. Review access logs
4. Update environment variables on Render
5. Deploy updated code

## Scaling Preparation

When ready to scale (move from free to paid):

- [ ] Upgrade Web Service plan
- [ ] Upgrade PostgreSQL plan
- [ ] Enable automated backups
- [ ] Add CDN for static files
- [ ] Implement caching strategy
- [ ] Monitor performance metrics
- [ ] Plan for high availability

## Success Indicators

Your deployment is successful when:

✓ Health check returns 200 status
✓ All 5 database tables are created
✓ Register/login endpoints work
✓ Data persists in PostgreSQL
✓ DBeaver can connect and see data
✓ No 500 errors in logs
✓ Response times are < 500ms

---

**Last Updated**: April 2026
