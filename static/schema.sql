-- PostgreSQL Schema for CareerSwipe Job Portal
-- This schema defines all tables, relationships, and indexes for the application
-- Database: careerswipe
-- Created for Render PostgreSQL deployment

-- ============================================================================
-- SEEKERS TABLE - Job seekers/candidates
-- ============================================================================
CREATE TABLE IF NOT EXISTS seekers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(30),
    address VARCHAR(500),
    education VARCHAR(255),
    experience TEXT,
    skills TEXT,
    resume_path VARCHAR(500),
    gender VARCHAR(20),
    dob VARCHAR(20),
    experience_type VARCHAR(50),           -- fresher / experienced
    career_field VARCHAR(100),              -- IT / Marketing / Finance etc
    job_status VARCHAR(50),                 -- searching / employed / open to offers
    job_location_type VARCHAR(50),          -- remote / onsite / hybrid
    shift_preference VARCHAR(50),           -- day / night / flexible
    desired_roles VARCHAR(255),
    salary_expectation VARCHAR(100),
    availability VARCHAR(100),
    verification_token VARCHAR(100),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast email lookups
CREATE INDEX IF NOT EXISTS idx_seekers_email ON seekers(email);
CREATE INDEX IF NOT EXISTS idx_seekers_created_at ON seekers(created_at);


-- ============================================================================
-- EMPLOYERS TABLE - Companies posting jobs
-- ============================================================================
CREATE TABLE IF NOT EXISTS employers (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(30),
    company_address VARCHAR(500),
    industry VARCHAR(150),
    verification_token VARCHAR(100),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast email lookups
CREATE INDEX IF NOT EXISTS idx_employers_email ON employers(email);
CREATE INDEX IF NOT EXISTS idx_employers_created_at ON employers(created_at);


-- ============================================================================
-- JOBS TABLE - Job listings posted by employers
-- ============================================================================
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    employer_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(255),
    salary VARCHAR(100),
    job_type VARCHAR(50) DEFAULT 'Full-time',    -- Full-time / Part-time / Contract / Internship
    experience_required VARCHAR(50),              -- Entry / Mid / Senior / Expert
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employer_id) REFERENCES employers(id) ON DELETE CASCADE
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_jobs_employer_id ON jobs(employer_id);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);


-- ============================================================================
-- APPLICATIONS TABLE - Job applications from seekers
-- ============================================================================
CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
    seeker_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',        -- pending / shortlisted / rejected / interview / accepted
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seeker_id) REFERENCES seekers(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    UNIQUE(seeker_id, job_id)                    -- Prevent duplicate applications
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_applications_seeker_id ON applications(seeker_id);
CREATE INDEX IF NOT EXISTS idx_applications_job_id ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_applied_at ON applications(applied_at);


-- ============================================================================
-- NOTIFICATIONS TABLE - User notifications
-- ============================================================================
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    user_type VARCHAR(20) NOT NULL,              -- 'seeker' or 'employer'
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'system',           -- application / accepted / rejected / interview / system
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, user_type);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);


-- ============================================================================
-- SAMPLE DATA (for testing - optional)
-- ============================================================================
-- Uncomment below to seed test data

/*
INSERT INTO seekers (first_name, last_name, email, password_hash, phone, address, career_field, job_status, experience_type)
VALUES 
    ('John', 'Doe', 'john.doe@example.com', '$2b$12$...', '555-0001', '123 Main St', 'IT', 'searching', 'fresher'),
    ('Jane', 'Smith', 'jane.smith@example.com', '$2b$12$...', '555-0002', '456 Oak Ave', 'IT', 'searching', 'experienced');

INSERT INTO employers (company_name, email, password_hash, phone, company_address, industry)
VALUES 
    ('Tech Corp', 'tech@example.com', '$2b$12$...', '555-1001', '789 Tech Blvd', 'Information Technology');

INSERT INTO jobs (employer_id, title, description, location, salary, job_type, experience_required)
VALUES 
    (1, 'Senior Developer', 'Looking for experienced developers', 'New York, NY', '$120,000 - $150,000', 'Full-time', 'Senior');
*/
