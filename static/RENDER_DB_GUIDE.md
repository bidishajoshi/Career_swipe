# 📊 CareerSwipe · Render PostgreSQL Guide

This is your master guide for viewing and managing your Cloud Database.

## 1. Fast Access (In your Browser)
The easiest way to see your data without installing any software:
1.  Login to [Render Dashboard](https://dashboard.render.com/).
2.  Click on your **PostgreSQL service** (`careerswipe db`).
3.  Click the **Data Explorer** tab.
4.  Run this command to see all your jobs:
    ```sql
    SELECT * FROM job_listings;
    ```

---

## 2. Advanced Access (Like Excel)
If you want to browse your data like a spreadsheet, download **[DBeaver](https://dbeaver.io/)**.
- **Host**: `dpg-d7g7fgosfn5c739vios0-a.ohio-postgres.render.com`
- **Database**: `careerswipe_db`
- **User**: `careerswipe_db_user`
- **Password**: `J5Dhc80TPs8hsJfnBnzp6w2esIKoAgeK`
- **Port**: `5432`

---

## 3. Maintenance Commands (From your laptop)
Whenever you want to sync your laptop changes to the cloud, use these terminal commands in VS Code:

| Command | Why use it? |
| :--- | :--- |
| `python test_db.py` | To check if your connection is still active. |
| `flask db upgrade` | To update the database if you change `models.py`. |
| `python seed_db.py` | To delete all data and reset to the "Google/Meta" samples. |

---

## 💡 Important Tips
- **Security**: Never share your `.env` file or your External URI with anyone.
- **Backups**: Render automatically backs up your database daily.
- **Fallsafe**: If you delete the `DATABASE_URL` line from your `.env`, the app will safely switch back to using your local `careerswipe.db` file.
