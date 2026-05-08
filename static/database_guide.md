# CareerSwipe · Database Guide (PostgreSQL)

This guide provides instructions for managing your database both locally and on Render.

## 1. Local PostgreSQL Setup

To use PostgreSQL locally instead of SQLite, follow these steps:

1.  **Install PostgreSQL**: Download and install from [postgresql.org](https://www.postgresql.org/download/).
2.  **Create a Database**: Open the "pgAdmin" tool (installed with PostgreSQL) or use the command line:
    ```bash
    createdb careerswipe
    ```
3.  **Update `.env`**: Add your connection string to the `.env` file:
    ```bash
    DATABASE_URL=postgresql://postgres:your_password@localhost:5432/careerswipe
    ```
4.  **Restart App**: The application will automatically detect `DATABASE_URL` and switch from SQLite to PostgreSQL.

---

## 2. Viewing Data (Tools)

### pgAdmin (Recommended for PostgreSQL)
1.  Open **pgAdmin 4**.
2.  Connect to your server (usually "PostgreSQL 16" or similar).
3.  Navigate to: `Databases` > `careerswipe` > `Schemas` > `public` > `Tables`.
4.  Right-click any table and select **View/Edit Data** > **All Rows**.

### DBeaver (Multi-database tool)
1.  Open **DBeaver**.
2.  Click **New Connection** > **PostgreSQL**.
3.  Enter host (`localhost`), database (`careerswipe`), username, and password.
4.  Open the connection to browse all tables and data.

### Terminal (psql)
```bash
# Connect to the database
psql -U postgres -d careerswipe

# List all tables
\dt

# View all users
SELECT * FROM seeker;
```

---

## 3. Render Deployment (Production)

On Render, the migration is handled automatically:
1.  **DATABASE_URL**: Render provides this automatically when you link a PostgreSQL database to your Web Service.
2.  **Configuration**: Our `config.py` automatically converts `postgres://` to `postgresql://` and enables SSL mode for security.
3.  **Requirements**: `psycopg2-binary` and `Flask-Migrate` are included in `requirements.txt` to ensure the production server can connect.

---

## 4. Maintenance Commands

If you change your models in `models.py`, run these commands to update your database without losing data:

```bash
# 1. Capture changes
flask db migrate -m "Added new field to seeker"

# 2. Apply changes
flask db upgrade
```
