#!/usr/bin/env python3
"""
Database Visualization Dashboard Generator
Generates HTML dashboards with charts
"""
import os
from datetime import datetime
from app import app, db

def get_db_stats():
    """Get statistics from database safely"""
    stats = {
        "seekers": 0,
        "companies": 0,
        "jobs": 0,
        "applications": 0,
        "notifications": 0,
        "accepted": 0,
        "pending": 0,
        "rejected": 0,
        "error": None
    }
    
    with app.app_context():
        try:
            from models import Seeker, Company, JobListing, JobSwipe, Notification
            
            stats["seekers"] = Seeker.query.count()
            stats["companies"] = Company.query.count()
            stats["jobs"] = JobListing.query.count()
            
            swipes = JobSwipe.query.all()
            stats["applications"] = len(swipes)
            stats["accepted"] = sum(1 for s in swipes if s.status == "accepted")
            stats["pending"] = sum(1 for s in swipes if s.status == "pending")
            stats["rejected"] = sum(1 for s in swipes if s.status == "rejected")
            
            stats["notifications"] = Notification.query.count()
            
        except Exception as e:
            stats["error"] = str(e)
    
    return stats

def generate_html_dashboard(stats):
    """Generate HTML dashboard"""
    
    error_alert = f"""
    <div style="background:#fee; border:1px solid #f99; padding:15px; border-radius:8px; margin-bottom:20px;">
        <strong>⚠️ Database Schema Issue:</strong> {stats['error'][:100]}
        <p style="margin-top:10px; font-size:12px;">This usually means your production database needs migration. Run: <code>flask db upgrade</code></p>
    </div>
    """ if stats.get('error') else ""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CareerSwipe - Database Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            h1 {{ color: white; margin-bottom: 30px; text-align: center; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 8px 16px rgba(0,0,0,0.1); }}
            .card h3 {{ color: #667eea; font-size: 14px; text-transform: uppercase; margin-bottom: 10px; }}
            .card .number {{ font-size: 32px; font-weight: bold; color: #333; }}
            .chart-container {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 8px 16px rgba(0,0,0,0.1); margin-bottom: 20px; position: relative; height: 400px; }}
            .error-box {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 CareerSwipe Database Dashboard</h1>
            <p style="color: white; text-align: center; margin-bottom: 30px;">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            {error_alert}
            
            <div class="grid">
                <div class="card">
                    <h3>👥 Total Seekers</h3>
                    <div class="number">{stats['seekers']}</div>
                </div>
                <div class="card">
                    <h3>🏢 Total Companies</h3>
                    <div class="number">{stats['companies']}</div>
                </div>
                <div class="card">
                    <h3>📋 Job Listings</h3>
                    <div class="number">{stats['jobs']}</div>
                </div>
                <div class="card">
                    <h3>💼 Total Applications</h3>
                    <div class="number">{stats['applications']}</div>
                </div>
                <div class="card">
                    <h3>✅ Accepted</h3>
                    <div class="number" style="color: #10b981;">{stats['accepted']}</div>
                </div>
                <div class="card">
                    <h3>⏳ Pending</h3>
                    <div class="number" style="color: #f59e0b;">{stats['pending']}</div>
                </div>
                <div class="card">
                    <h3>❌ Rejected</h3>
                    <div class="number" style="color: #ef4444;">{stats['rejected']}</div>
                </div>
                <div class="card">
                    <h3>🔔 Notifications</h3>
                    <div class="number">{stats['notifications']}</div>
                </div>
            </div>
            
            <div class="chart-container">
                <canvas id="statusChart"></canvas>
            </div>
            
            <div class="chart-container">
                <canvas id="usersChart"></canvas>
            </div>
        </div>
        
        <script>
            // Application Status Chart
            new Chart(document.getElementById('statusChart'), {{
                type: 'doughnut',
                data: {{
                    labels: ['Accepted', 'Pending', 'Rejected'],
                    datasets: [{{
                        data: [{stats['accepted']}, {stats['pending']}, {stats['rejected']}],
                        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                        borderColor: 'white',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{ display: true, text: 'Application Status Distribution', font: {{ size: 16 }} }},
                        legend: {{ position: 'bottom' }}
                    }}
                }}
            }});
            
            // Users & Jobs Chart
            new Chart(document.getElementById('usersChart'), {{
                type: 'bar',
                data: {{
                    labels: ['Seekers', 'Companies', 'Job Listings', 'Applications'],
                    datasets: [{{
                        label: 'Count',
                        data: [{stats['seekers']}, {stats['companies']}, {stats['jobs']}, {stats['applications']}],
                        backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#4facfe'],
                        borderRadius: 8,
                        borderSkipped: false
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{ display: true, text: 'Platform Overview', font: {{ size: 16 }} }},
                        legend: {{ display: false }}
                    }},
                    scales: {{
                        y: {{ beginAtZero: true }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    stats = get_db_stats()
    html = generate_html_dashboard(stats)
    
    output_path = "static/dashboard.html"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ Dashboard generated: {output_path}")
    print(f"Open in browser: file://{os.path.abspath(output_path)}")
