# 🚀 CareerSwipe · Full Supabase Setup Guide

This guide will help you connect your laptop to a professional **PostgreSQL** database hosted in the cloud (Supabase), so you don't have to download any database software locally.

## 📋 Prerequisites
1.  A free [Supabase](https://supabase.com/) account.
2.  Your project opened in VS Code.

---

## 🛠️ Phase 1: Create the Database
1.  Log in to **Supabase** and click **New Project**.
2.  **Organization**: Choose your name.
3.  **Name**: `careerswipe-db`.
4.  **Database Password**: ⚠️ **IMPORTANT** ⚠️ Create a strong password and **copy it somewhere safe**. You will need this for your code!
5.  **Region**: Choose the one closest to you (e.g., Mumbai, Singapore, US East).
6.  Click **Create New Project**. It will take 1-2 minutes to provision.

---

## 🔗 Phase 2: Link Your Laptop
1.  In Supabase, go to **Project Settings** (gear icon) -> **Database**.
2.  Scroll down to the **Connection string** section.
3.  Click the **URI** tab. It will look like this:
    `postgresql://postgres.[PROJECT-ID]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres`
4.  **Copy this URI**.
5.  Open your **[.env](file:///c:/Users/VICTUS/Desktop/career-swipe/.env)** file in VS Code.
6.  Replace the current `DATABASE_URL` with your copied URI.
7.  **CRITICAL**: Replace `[YOUR-PASSWORD]` in the middle of the string with the actual password you created in Phase 1.

---

## ✅ Phase 3: Verify & Initialize
I have provided two tools to make sure everything is perfect:

### 1. Test the Connection
Run this command in your terminal. It will check if your password and URI are correct:
```powershell
python test_db.py
```

### 2. Create the Tables
Once the test passes, run this command to "upload" the database structure to Supabase:
```powershell
flask db upgrade
```

---

## 📊 Phase 4: See Your Data
You don't need a laptop app to see your data! 
1.  In Supabase, click the **Table Editor** icon (the grid icon on the left sidebar).
2.  Ensure the schema is set to `public`.
3.  You will see tables like `seeker`, `job_listing`, and `job_swipe`. 
4.  You can add, edit, or delete data directly in this browser view!

---

## 💡 Troubleshooting
*   **Connection Timeout**: Ensure you are using the **Pooler** URI (port 6543) as it is more stable for cloud connections.
*   **Password Error**: If `test_db.py` fails, double-check your password. 
*   **Special Characters**: If your password starts with a `#` (like `#Careerswipe1`), you **MUST** replace it with `%23` in the URI (e.g., `%23Careerswipe1`).
*   **Avoid `@` or `:`**: These symbols in your database password can confuse the URI format and should be avoided if possible.
