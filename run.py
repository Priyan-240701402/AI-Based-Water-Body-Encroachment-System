"""
JalRaksha - Water Body Encroachment Complaint & Monitoring System
Root-Level Application Launcher.

Run from any directory: python run.py
"""

import os
import sys
from pathlib import Path

# Always set working directory to project root
project_root = Path(__file__).resolve().parent
os.chdir(project_root)

# Ensure project root is in Python path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"\n{'='*60}")
    print(f"  JalRaksha Water Body Encroachment System")
    print(f"  Running at: http://127.0.0.1:{port}")
    print(f"{'='*60}")
    print(f"  Demo Logins:")
    print(f"    Citizen : citizen1@example.com  / Password@123")
    print(f"    Officer : officer.revenue@waterbodies.gov.in / Password@123")
    print(f"    Admin   : admin@waterbodies.gov.in / Password@123")
    print(f"{'='*60}\n")
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
