# CareerSwipe Backend - API Quick Reference

## Quick Start

### Test Backend Health
```bash
curl http://localhost:5000/api/health
```

## Authentication (Seeders & Employers)

### 1. Register a Seeker
```bash
curl -X POST http://localhost:5000/api/auth/register/seeker \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "phone": "555-1234",
    "career_field": "IT",
    "experience_type": "fresher"
  }'
```

### 2. Register an Employer
```bash
curl -X POST http://localhost:5000/api/auth/register/employer \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Tech Solutions Inc",
    "email": "tech@example.com",
    "password": "CompanyPass123",
    "phone": "555-5000",
    "industry": "Information Technology"
  }'
```

### 3. Login as Seeker
```bash
curl -X POST http://localhost:5000/api/auth/login/seeker \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

### 4. Login as Employer
```bash
curl -X POST http://localhost:5000/api/auth/login/employer \
  -H "Content-Type: application/json" \
  -d '{
    "email": "tech@example.com",
    "password": "CompanyPass123"
  }'
```

## Job Management (Employer)

### 1. Post a New Job
```bash
curl -X POST http://localhost:5000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "employer_id": 1,
    "title": "Senior Python Developer",
    "description": "We are looking for an experienced Python developer with 5+ years of experience...",
    "location": "New York, NY",
    "salary": "$120,000 - $150,000",
    "job_type": "Full-time",
    "experience_required": "Senior"
  }'
```

### 2. Get All Jobs
```bash
# Get first 20 jobs
curl http://localhost:5000/api/jobs?limit=20&offset=0

# Get with pagination (e.g., next 20 jobs)
curl http://localhost:5000/api/jobs?limit=20&offset=20
```

### 3. Get Specific Job
```bash
curl http://localhost:5000/api/jobs/1
```

### 4. Get Employer's Jobs
```bash
curl http://localhost:5000/api/jobs/employer/1?limit=20&offset=0
```

### 5. Update Job
```bash
curl -X PUT http://localhost:5000/api/jobs/1 \
  -H "Content-Type: application/json" \
  -d '{
    "employer_id": 1,
    "title": "Senior Python Developer (Updated)",
    "salary": "$130,000 - $160,000"
  }'
```

### 6. Delete Job
```bash
curl -X DELETE http://localhost:5000/api/jobs/1 \
  -H "Content-Type: application/json" \
  -d '{"employer_id": 1}'
```

## Job Applications (Seekers)

### 1. Apply to a Job
```bash
curl -X POST http://localhost:5000/api/applications \
  -H "Content-Type: application/json" \
  -d '{
    "seeker_id": 1,
    "job_id": 1
  }'
```

### 2. Get My Applications (as Seeker)
```bash
# Get all applications for a seeker
curl http://localhost:5000/api/applications/seeker/1?limit=20&offset=0
```

### 3. View Application Details
```bash
curl "http://localhost:5000/api/applications/1?user_id=1&user_type=seeker"
```

## Application Management (Employer)

### 1. View Applications for a Job
```bash
# View all applications for job_id=1, employer must provide employer_id
curl "http://localhost:5000/api/applications/job/1?employer_id=1&limit=20&offset=0"
```

### 2. Update Application Status
```bash
# Shortlist an applicant
curl -X PUT http://localhost:5000/api/applications/1/status \
  -H "Content-Type: application/json" \
  -d '{
    "employer_id": 1,
    "job_id": 1,
    "status": "shortlisted"
  }'
```

Valid statuses: `pending`, `shortlisted`, `rejected`, `interview`, `accepted`

### 3. Send Interview Notification
```bash
curl -X PUT http://localhost:5000/api/applications/1/status \
  -H "Content-Type: application/json" \
  -d '{
    "employer_id": 1,
    "job_id": 1,
    "status": "interview"
  }'
```

### 4. Accept Application
```bash
curl -X PUT http://localhost:5000/api/applications/1/status \
  -H "Content-Type: application/json" \
  -d '{
    "employer_id": 1,
    "job_id": 1,
    "status": "accepted"
  }'
```

## Response Format

All API responses follow this format:

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "error": "Additional error details"
}
```

## Status Codes

- `200` - OK (successful GET/PUT/DELETE)
- `201` - Created (successful POST for creation)
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (authentication failed)
- `404` - Not Found (resource doesn't exist)
- `405` - Method Not Allowed (wrong HTTP method)
- `500` - Internal Server Error (server error)

## Testing Tips

1. **Use Postman or Insomnia**: GUI tools make testing easier
2. **Save Variables**: Store IDs from responses for reuse
3. **Check Response Status**: Always verify HTTP status code
4. **Monitor Server Logs**: Watch backend console for errors
5. **Test Edge Cases**: Try invalid inputs, duplicates, etc.

## Common Errors

### "Invalid email format"
- Ensure email is properly formatted: `user@example.com`

### "Email already registered"
- The email already exists in the system
- Use a different email for testing

### "Password must be at least 8 characters"
- Use a stronger password

### "Job not found"
- Verify the job_id exists
- Check if job was deleted

### "Unauthorized - not the job owner"
- Use the correct employer_id
- Ensure you own the job you're trying to modify

### "You have already applied to this job"
- Duplicate applications are not allowed
- Each seeker can apply only once per job

## API Base URL

- **Local Development**: `http://localhost:5000/api`
- **Render Production**: `https://careerswipe-backend.onrender.com/api`
