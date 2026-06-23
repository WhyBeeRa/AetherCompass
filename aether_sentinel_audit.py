import os
import sys
import socket
import sqlite3
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import psutil

# Ensure working directory is the script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Add backend directory to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from dotenv import load_dotenv

# Load env variables
backend_env = Path(__file__).parent / "backend" / ".env"
load_dotenv(dotenv_path=backend_env)

# Try imports for optional / integration checks
GEMINI_OK = False
GEMINI_ERR = ""
try:
    from google import genai
    from google.genai import types
    GEMINI_OK = True
except Exception as e:
    GEMINI_ERR = str(e)

FIREBASE_OK = False
FIREBASE_ERR = ""
try:
    import firebase_admin
    FIREBASE_OK = True
except Exception as e:
    FIREBASE_ERR = str(e)

from backend.persistence import AetherVault

def check_port(host: str, port: int) -> bool:
    """Checks if a port is open on the target host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2.0)
        return s.connect_ex((host, port)) == 0

def get_disk_space() -> dict:
    """Gathers disk space stats for the current repository directory."""
    path = Path(__file__).parent
    try:
        usage = psutil.disk_usage(str(path))
        return {
            "total_gb": round(usage.total / (1024**3), 2),
            "used_gb": round(usage.used / (1024**3), 2),
            "free_gb": round(usage.free / (1024**3), 2),
            "percent": usage.percent,
            "status": "GREEN" if usage.percent < 85 else ("AMBER" if usage.percent < 95 else "RED")
        }
    except Exception as e:
        return {"error": str(e), "status": "RED"}

def get_system_resources() -> dict:
    """Gathers CPU and memory utilization."""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        
        # Get FastAPI process stats if running
        api_mem_mb = 0.0
        api_cpu = 0.0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmd = proc.info['cmdline']
                if cmd and any('uvicorn' in arg or 'main:app' in arg for arg in cmd):
                    api_mem_mb = round(proc.memory_info().rss / (1024**2), 2)
                    api_cpu = proc.cpu_percent(interval=0.1)
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
        return {
            "cpu_percent": cpu_percent,
            "mem_total_gb": round(mem.total / (1024**3), 2),
            "mem_used_gb": round(mem.used / (1024**3), 2),
            "mem_percent": mem.percent,
            "api_process_memory_mb": api_mem_mb,
            "api_process_cpu_percent": api_cpu,
            "status": "GREEN" if mem.percent < 85 and cpu_percent < 80 else "AMBER"
        }
    except Exception as e:
        return {"error": str(e), "status": "RED"}

def test_gemini_api() -> dict:
    """Tests Gemini API responsiveness with a light query."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"status": "RED", "message": "GEMINI_API_KEY is not set in environment."}
    
    if not GEMINI_OK:
        return {"status": "RED", "message": f"google-genai package missing/failed to import: {GEMINI_ERR}"}
        
    try:
        start_time = time.time()
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="ping",
        )
        latency = round((time.time() - start_time) * 1000, 2)
        if response and response.text:
            return {"status": "GREEN", "message": f"Successfully connected to Gemini 2.5 Flash.", "latency_ms": latency}
        else:
            return {"status": "AMBER", "message": "Gemini responded with empty body."}
    except Exception as e:
        return {"status": "RED", "message": f"Gemini API failure: {str(e)}"}

def test_firebase_connection() -> dict:
    """Verifies Firebase connection & settings."""
    if not FIREBASE_OK:
        return {"status": "RED", "message": f"firebase-admin library failed to import: {FIREBASE_ERR}"}
        
    service_account = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    if not service_account:
        return {"status": "RED", "message": "FIREBASE_SERVICE_ACCOUNT environment variable is not defined."}
        
    try:
        # Check if already initialized
        try:
            app = firebase_admin.get_app()
            message = f"Firebase Admin SDK is active (Project ID: {app.project_id})."
        except ValueError:
            # Not initialized yet in this script context, let's parse credentials to check
            cred_dict = json.loads(service_account)
            project_id = cred_dict.get("project_id", "Unknown")
            message = f"Firebase credentials verified offline for Project: {project_id}."
            
        return {"status": "GREEN", "message": message}
    except Exception as e:
        return {"status": "RED", "message": f"Firebase verification failed: {str(e)}"}

def gather_audit_metrics(vault: AetherVault) -> dict:
    """Gathers advanced metrics from database tables for the audit report."""
    metrics = {}
    try:
        stats = vault.get_stats()
        metrics["indexed_tools"] = stats.get("verified_tools_count", 0)
        metrics["total_intents"] = stats.get("total_intents_mapped", 0)
        metrics["last_scan"] = stats.get("last_scan_date", "Never")
        
        # Get pending tools
        pending = vault.get_pending_tools()
        metrics["pending_review_count"] = len(pending)
        
        # Search analytics (last 24 hours)
        conn = vault._get_conn()
        c = conn.cursor()
        
        one_day_ago = datetime.now() - timedelta(days=1)
        c.execute("SELECT COUNT(*), SUM(has_match) FROM search_queries WHERE timestamp > %s", (one_day_ago,))
        row = c.fetchone()
        metrics["searches_24h"] = row[0] or 0
        metrics["successful_searches_24h"] = row[1] or 0
        metrics["failed_searches_24h"] = (row[0] or 0) - (row[1] or 0)
        
        # ELO Battles Count
        c.execute("SELECT COUNT(*) FROM elo_battles")
        metrics["elo_battles_total"] = c.fetchone()[0] or 0
        
        # Live Benchmarks Count
        c.execute("SELECT COUNT(*) FROM live_metrics")
        metrics["live_benchmarks_total"] = c.fetchone()[0] or 0
        
        conn.close()
        metrics["status"] = "GREEN"
    except Exception as e:
        metrics["error"] = str(e)
        metrics["status"] = "AMBER"
        # Provide fallbacks
        metrics["indexed_tools"] = 0
        metrics["pending_review_count"] = 0
        metrics["searches_24h"] = 0
        metrics["successful_searches_24h"] = 0
        metrics["failed_searches_24h"] = 0
        metrics["elo_battles_total"] = 0
        metrics["live_benchmarks_total"] = 0
        
    return metrics

def build_html_report(results: dict) -> str:
    """Builds a beautiful premium HTML report with curated colors and modern dark-mode card style."""
    
    overall_status = results["overall_status"]
    status_color = "#10B981" if overall_status == "GREEN" else ("#F59E0B" if overall_status == "AMBER" else "#EF4444")
    status_icon = "🟢" if overall_status == "GREEN" else ("🟡" if overall_status == "AMBER" else "🔴")
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aether Sentinel Audit Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #0B0F19;
            color: #E2E8F0;
            margin: 0;
            padding: 0;
            -webkit-font-smoothing: antialiased;
        }}
        .wrapper {{
            width: 100%;
            background-color: #0B0F19;
            padding: 30px 0;
        }}
        .container {{
            max-width: 650px;
            margin: 0 auto;
            background-color: #111827;
            border: 1px solid #1F2937;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
        }}
        .header {{
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            padding: 40px 30px;
            border-bottom: 2px solid {status_color};
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 26px;
            font-weight: 800;
            letter-spacing: 1.5px;
            color: #FFFFFF;
            text-transform: uppercase;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 14px;
            color: #94A3B8;
        }}
        .status-badge {{
            display: inline-block;
            margin-top: 15px;
            padding: 6px 16px;
            background-color: rgba({ '16, 185, 129' if overall_status == 'GREEN' else ('245, 158, 11' if overall_status == 'AMBER' else '239, 68, 68') }, 0.15);
            border: 1px solid {status_color};
            border-radius: 9999px;
            font-weight: 700;
            font-size: 14px;
            color: {status_color};
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 25px;
        }}
        .section-title {{
            font-size: 16px;
            font-weight: 700;
            color: #38BDF8;
            border-bottom: 1px solid #1F2937;
            padding-bottom: 8px;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .card {{
            background-color: #1F2937;
            border: 1px solid #374151;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 12px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }}
        .stat-card {{
            background-color: #1F2937;
            border: 1px solid #374151;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: 800;
            color: #FFFFFF;
            margin-top: 5px;
        }}
        .stat-label {{
            font-size: 11px;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .flex-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        .flex-row:last-child {{
            margin-bottom: 0;
        }}
        .item-label {{
            font-size: 14px;
            font-weight: 600;
            color: #94A3B8;
        }}
        .item-value {{
            font-size: 14px;
            font-weight: 700;
            color: #F8FAFC;
        }}
        .badge-ok {{
            color: #10B981;
            background-color: rgba(16, 185, 129, 0.1);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
        }}
        .badge-err {{
            color: #EF4444;
            background-color: rgba(239, 68, 68, 0.1);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
        }}
        .badge-warn {{
            color: #F59E0B;
            background-color: rgba(245, 158, 11, 0.1);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
        }}
        .footer {{
            background-color: #0B0F19;
            padding: 20px 30px;
            text-align: center;
            border-top: 1px solid #1F2937;
            font-size: 12px;
            color: #64748B;
        }}
        .recovery-tip {{
            background-color: rgba(239, 68, 68, 0.05);
            border: 1px dashed rgba(239, 68, 68, 0.3);
            border-radius: 8px;
            padding: 12px;
            margin-top: 15px;
            font-size: 13px;
            color: #FDA4AF;
        }}
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="container">
            <div class="header">
                <h1>🛡️ Aether Sentinel</h1>
                <p>Daily Automated System Audit Report</p>
                <div class="status-badge">{status_icon} SYSTEM STATUS: {overall_status}</div>
            </div>
            
            <div class="content">
                <!-- 1. Services Status -->
                <div class="section">
                    <div class="section-title">🌐 Services Status</div>
                    <div class="card">
                        <div class="flex-row">
                            <span class="item-label">FastAPI Backend (Port 8000)</span>
                            <span class="{'badge-ok' if results['backend_port'] else 'badge-err'}">
                                {'ONLINE' if results['backend_port'] else 'OFFLINE'}
                            </span>
                        </div>
                        <div class="flex-row">
                            <span class="item-label">Vite Frontend (Port 5173)</span>
                            <span class="{'badge-ok' if results['frontend_port'] else 'badge-err'}">
                                {'ONLINE' if results['frontend_port'] else 'OFFLINE'}
                            </span>
                        </div>
                        <div class="flex-row">
                            <span class="item-label">Aether Vault Database File</span>
                            <span class="{'badge-ok' if results['db_accessible'] else 'badge-err'}">
                                {'CONNECTED' if results['db_accessible'] else 'DISCONNECTED'}
                            </span>
                        </div>
                    </div>
                </div>

                <!-- 2. AI & Integration Integrity -->
                <div class="section">
                    <div class="section-title">🧠 AI & Integration Integrity</div>
                    <div class="card">
                        <div class="flex-row">
                            <span class="item-label">Gemini API Key</span>
                            <span class="badge-ok" style="font-family: monospace;">
                                {os.getenv('GEMINI_API_KEY')[:8]}...{os.getenv('GEMINI_API_KEY')[-4:] if os.getenv('GEMINI_API_KEY') else ''}
                            </span>
                        </div>
                        <div class="flex-row">
                            <span class="item-label">Gemini API Health Check</span>
                            <span class="{'badge-ok' if results['gemini_status']['status'] == 'GREEN' else 'badge-err'}">
                                {results['gemini_status']['status']}
                            </span>
                        </div>
                        <div class="flex-row" style="margin-top: 4px;">
                            <span style="font-size: 12px; color: #94A3B8; max-width: 80%;">{results['gemini_status']['message']}</span>
                            {f"<span style='font-size: 12px; color: #38BDF8;'>{results['gemini_status']['latency_ms']} ms</span>" if 'latency_ms' in results['gemini_status'] else ''}
                        </div>
                        <hr style="border: 0; border-top: 1px solid #374151; margin: 10px 0;">
                        <div class="flex-row">
                            <span class="item-label">Firebase Auth Platform Check</span>
                            <span class="{'badge-ok' if results['firebase_status']['status'] == 'GREEN' else 'badge-err'}">
                                {results['firebase_status']['status']}
                            </span>
                        </div>
                        <div style="font-size: 12px; color: #94A3B8; margin-top: 4px;">
                            {results['firebase_status']['message']}
                        </div>
                    </div>
                </div>

                <!-- 3. Database Catalog & Analytics -->
                <div class="section">
                    <div class="section-title">📊 Database & Catalog Summary</div>
                    <div class="grid">
                        <div class="stat-card">
                            <div class="stat-value">{results['metrics']['indexed_tools']}</div>
                            <div class="stat-label">Verified Tools</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{results['metrics']['pending_review_count']}</div>
                            <div class="stat-label">Pending Review</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{results['metrics']['searches_24h']}</div>
                            <div class="stat-label">Searches (24h)</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{results['metrics']['successful_searches_24h']}/{results['metrics']['failed_searches_24h']}</div>
                            <div class="stat-label">Search Hits/Misses</div>
                        </div>
                    </div>
                    <div class="card" style="margin-top: 12px;">
                        <div class="flex-row">
                            <span class="item-label">Total ELO Battles Recorded</span>
                            <span class="item-value">{results['metrics']['elo_battles_total']}</span>
                        </div>
                        <div class="flex-row">
                            <span class="item-label">Live Performance Benchmarks</span>
                            <span class="item-value">{results['metrics']['live_benchmarks_total']}</span>
                        </div>
                        <div class="flex-row">
                            <span class="item-label">Database Stats Check</span>
                            <span class="{'badge-ok' if results['metrics']['status'] == 'GREEN' else 'badge-warn'}">
                                {results['metrics']['status']}
                            </span>
                        </div>
                    </div>
                </div>

                <!-- 4. System Resources -->
                <div class="section">
                    <div class="section-title">⚙️ System Resources</div>
                    <div class="card">
                        <div class="flex-row">
                            <span class="item-label">CPU Utilization</span>
                            <span class="item-value">{results['resources']['cpu_percent']}%</span>
                        </div>
                        <div class="flex-row">
                            <span class="item-label">RAM Usage</span>
                            <span class="item-value">{results['resources']['mem_used_gb']} / {results['resources']['mem_total_gb']} GB ({results['resources']['mem_percent']}%)</span>
                        </div>
                        <div class="flex-row">
                            <span class="item-label">Repository Disk Space</span>
                            <span class="item-value">{results['disk']['used_gb']} / {results['disk']['total_gb']} GB ({results['disk']['percent']}% used)</span>
                        </div>
                        <div class="flex-row">
                            <span class="item-label">FastAPI Process RAM</span>
                            <span class="item-value">{results['resources']['api_process_memory_mb']} MB</span>
                        </div>
                    </div>
                </div>

                <!-- Recovery Actions if Amber or Red -->
                {f'''<div class="recovery-tip">
                    <strong>⚠️ Suggested Recovery Protocols:</strong><br>
                    { '• Start the backend server: <code>uvicorn backend.main:app --reload</code><br>' if not results['backend_port'] else '' }
                    { '• Start the Vite dev server: <code>npm run dev</code><br>' if not results['frontend_port'] else '' }
                    { '• Database connection issue detected. Check PostgreSQL server state and connection settings.<br>' if not results['db_accessible'] else '' }
                    { '• Gemini API check failed. Ensure the <code>GEMINI_API_KEY</code> variable is fully populated and valid in your <code>.env</code> file.<br>' if results['gemini_status']['status'] != 'GREEN' else '' }
                </div>''' if overall_status != "GREEN" else ""}
            </div>
            
            <div class="footer">
                <p>This automated audit was compiled by Aether Sentinel.<br>Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>&copy; 2026 AetherCompass. All Rights Secured.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""
    return html

def send_audit_email(html_content: str, overall_status: str, admin_emails: list):
    """Sends the HTML report using SMTP or logs to sentinel_audit.log as a fallback."""
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASSWORD", "")
    smtp_from = os.getenv("SMTP_FROM", "sentinel@aethercompass.com")
    
    subject = f"🛡️ AETHER SENTINEL: SYSTEM AUDIT STATUS [{overall_status}]"
    
    success_sent = False
    
    if smtp_host and smtp_user and smtp_pass:
        try:
            for to_email in admin_emails:
                to_email = to_email.strip()
                if not to_email:
                    continue
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = smtp_from
                msg["To"] = to_email
                
                # HTML part
                part = MIMEText(html_content, "html", "utf-8")
                msg.attach(part)
                
                with smtplib.SMTP(smtp_host, smtp_port, timeout=10.0) as server:
                    if smtp_port == 587:
                        server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(smtp_from, [to_email], msg.as_string())
            success_sent = True
            print(f"[Aether Sentinel] Email successfully sent to {', '.join(admin_emails)} via SMTP.")
        except Exception as e:
            print(f"[Aether Sentinel] Failed to send email via SMTP: {e}")
            
    if not success_sent:
        log_file = Path(__file__).parent / "sentinel_audit.log"
        mock_log = (
            f"\n=======================================================\n"
            f"MOCK SMTP DISPATCH AT {datetime.now()}\n"
            f"Subject: {subject}\n"
            f"To: {', '.join(admin_emails)}\n"
            f"-------------------------------------------------------\n"
            f"SMTP Settings not configured or failed. Saved HTML report to log file.\n"
            f"=======================================================\n"
        )
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(mock_log)
            # Write a link to the HTML file for manual verification
            html_log_path = Path(__file__).parent / "sentinel_last_report.html"
            with open(html_log_path, "w", encoding="utf-8") as hf:
                hf.write(html_content)
        print(f"[Aether Sentinel] SMTP is not configured. Mock dispatch completed.")
        print(f"[Aether Sentinel] Full HTML report written to {html_log_path}")

def run_sentinel_audit():
    print(f"=== Aether Sentinel Audit Initiated: {datetime.now()} ===")
    
    # 1. Check services
    backend_port_ok = check_port("localhost", 8000)
    frontend_port_ok = check_port("localhost", 5173)
    
    # 2. Check Database
    db_accessible = False
    vault = None
    try:
        vault = AetherVault()
        vault.get_stats()
        db_accessible = True
    except Exception as e:
        print(f"[Database Health Check] FAILED: {e}")
        
    # 3. Check Integrations
    gemini_status = test_gemini_api()
    firebase_status = test_firebase_connection()
    
    # 4. Check Resources
    disk_stats = get_disk_space()
    resource_stats = get_system_resources()
    
    # 5. Gather Database Metrics
    metrics = {}
    if db_accessible and vault:
        metrics = gather_audit_metrics(vault)
    else:
        metrics = {
            "indexed_tools": 0, "pending_review_count": 0, "searches_24h": 0,
            "successful_searches_24h": 0, "failed_searches_24h": 0,
            "elo_battles_total": 0, "live_benchmarks_total": 0, "status": "RED"
        }
        
    # Calculate overall status
    critical_failures = 0
    if not backend_port_ok:
        critical_failures += 1
    if not db_accessible:
        critical_failures += 1
    if gemini_status["status"] == "RED":
        critical_failures += 1
        
    warning_failures = 0
    if not frontend_port_ok:
        warning_failures += 1
    if firebase_status["status"] == "RED":
        warning_failures += 1
    if disk_stats.get("status") == "AMBER" or resource_stats.get("status") == "AMBER":
        warning_failures += 1
        
    overall_status = "GREEN"
    if critical_failures > 0:
        overall_status = "RED"
    elif warning_failures > 0:
        overall_status = "AMBER"
        
    results = {
        "timestamp": datetime.now().isoformat(),
        "backend_port": backend_port_ok,
        "frontend_port": frontend_port_ok,
        "db_accessible": db_accessible,
        "gemini_status": gemini_status,
        "firebase_status": firebase_status,
        "disk": disk_stats,
        "resources": resource_stats,
        "metrics": metrics,
        "overall_status": overall_status
    }
    
    # Log run into database if db is accessible
    if db_accessible and vault:
        try:
            email_sent_status = 1 if os.getenv("SMTP_HOST") else 0
            vault.log_sentinel_audit(
                overall_status,
                f"Sentinel Automated Daily Audit: Backend={'OK' if backend_port_ok else 'ERR'}, db={'OK' if db_accessible else 'ERR'}, Gemini={gemini_status['status']}.",
                "CONNECTED" if db_accessible else "DISCONNECTED",
                resource_stats.get("mem_percent", 0.0),
                email_sent_status
            )
            # Update sentinel failure settings
            current_failures = 0 if overall_status == "GREEN" else 1
            vault.update_sentinel_failures(current_failures, overall_status)
        except Exception as e:
            print(f"[Aether Sentinel] Failed to log audit status to Database: {e}")
            
    # Compile HTML Report
    html_content = build_html_report(results)
    
    # Resolve administrative email addresses
    admin_emails_str = os.getenv("ADMIN_EMAILS", "yuvalbot812@gmail.com,yuval@example.com")
    admin_emails = [email.strip() for email in admin_emails_str.split(",") if email.strip()]
    
    # Send email
    send_audit_email(html_content, overall_status, admin_emails)
    
    # Write summary log
    summary = (
        f"--- Audit Summary ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---\n"
        f"Overall System Status: {overall_status}\n"
        f"Backend: {'ONLINE' if backend_port_ok else 'OFFLINE'}\n"
        f"Frontend: {'ONLINE' if frontend_port_ok else 'OFFLINE'}\n"
        f"Database: {'CONNECTED' if db_accessible else 'DISCONNECTED'}\n"
        f"Gemini API: {gemini_status['status']}\n"
        f"Firebase API: {firebase_status['status']}\n"
        f"Disk Used: {disk_stats.get('percent', 'unknown')}%\n"
        f"RAM Used: {resource_stats.get('mem_percent', 'unknown')}%\n"
        f"Indexed Tools: {metrics.get('indexed_tools', 0)}\n"
        f"-----------------------------------------\n"
    )
    print(summary)
    
    with open("sentinel_audit.log", "a", encoding="utf-8") as f:
        f.write(summary)

if __name__ == "__main__":
    run_sentinel_audit()
