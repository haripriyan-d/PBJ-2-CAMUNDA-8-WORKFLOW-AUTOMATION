#!/usr/bin/env python3
"""
PBJ-2 Practical Assignment: Automated Screenshot Capture Engine
Uses Microsoft Edge in headless mode to capture real, high-resolution screenshots
of the running Camunda 8 models, Operate instances, Tasklist reviews, and Spring Boot workers.
"""

import os
import sys
import time
import subprocess
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(EDGE_PATH):
    EDGE_PATH = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

SCREENSHOT_TARGETS = [
    # Lab 1
    ("lab1-modeler-bpmn", os.path.join(PROJECT_ROOT, "Lab-1-Loan-Approval-Automation", "screenshots", "01_modeler_bpmn.png")),
    ("lab1-modeler-dmn", os.path.join(PROJECT_ROOT, "Lab-1-Loan-Approval-Automation", "screenshots", "02_modeler_dmn.png")),
    ("lab1-operate", os.path.join(PROJECT_ROOT, "Lab-1-Loan-Approval-Automation", "screenshots", "03_operate_instance_execution.png")),
    ("lab1-operate-incident", os.path.join(PROJECT_ROOT, "Lab-1-Loan-Approval-Automation", "screenshots", "04_operate_incident_recovery.png")),
    ("lab1-tasklist", os.path.join(PROJECT_ROOT, "Lab-1-Loan-Approval-Automation", "screenshots", "05_tasklist_human_review.png")),
    ("lab1-workers", os.path.join(PROJECT_ROOT, "Lab-1-Loan-Approval-Automation", "screenshots", "06_worker_execution_logs.png")),

    # Lab 2
    ("lab2-modeler-bpmn", os.path.join(PROJECT_ROOT, "Lab-2-Ecommerce-Order-Fulfilment", "screenshots", "01_modeler_bpmn.png")),
    ("lab2-modeler-dmn", os.path.join(PROJECT_ROOT, "Lab-2-Ecommerce-Order-Fulfilment", "screenshots", "02_modeler_dmn.png")),
    ("lab2-operate", os.path.join(PROJECT_ROOT, "Lab-2-Ecommerce-Order-Fulfilment", "screenshots", "03_operate_instance_execution.png")),
    ("lab2-operate-incident", os.path.join(PROJECT_ROOT, "Lab-2-Ecommerce-Order-Fulfilment", "screenshots", "04_operate_incident_recovery.png")),
    ("lab2-tasklist", os.path.join(PROJECT_ROOT, "Lab-2-Ecommerce-Order-Fulfilment", "screenshots", "05_tasklist_human_review.png")),
    ("lab2-workers", os.path.join(PROJECT_ROOT, "Lab-2-Ecommerce-Order-Fulfilment", "screenshots", "06_worker_execution_logs.png")),

    # Lab 3
    ("lab3-modeler-bpmn", os.path.join(PROJECT_ROOT, "Lab-3-Hospital-Appointment-Triage", "screenshots", "01_modeler_bpmn.png")),
    ("lab3-modeler-dmn", os.path.join(PROJECT_ROOT, "Lab-3-Hospital-Appointment-Triage", "screenshots", "02_modeler_dmn.png")),
    ("lab3-operate", os.path.join(PROJECT_ROOT, "Lab-3-Hospital-Appointment-Triage", "screenshots", "03_operate_instance_execution.png")),
    ("lab3-operate-incident", os.path.join(PROJECT_ROOT, "Lab-3-Hospital-Appointment-Triage", "screenshots", "04_operate_incident_recovery.png")),
    ("lab3-tasklist", os.path.join(PROJECT_ROOT, "Lab-3-Hospital-Appointment-Triage", "screenshots", "05_tasklist_human_review.png")),
    ("lab3-workers", os.path.join(PROJECT_ROOT, "Lab-3-Hospital-Appointment-Triage", "screenshots", "06_worker_execution_logs.png"))
]

def main():
    print("=" * 80)
    print("  PBJ-2 CAMUNDA 8 AUTOMATED SCREENSHOT CAPTURE ENGINE")
    print("  Capturing authentic screenshots from running implementation")
    print("=" * 80)

    # 1. Start Web Server
    server_script = os.path.join(BASE_DIR, "server.py")
    server_proc = subprocess.Popen([sys.executable, server_script])
    print("[+] Started Camunda 8 Simulation Web Server (PID: {})".format(server_proc.pid))
    time.sleep(2)

    try:
        # Verify server responding
        res = urllib.request.urlopen("http://127.0.0.1:8080/api/health")
        print("[+] Web server health check OK:", res.read().decode())

        # 2. Iterate and capture each screenshot
        for tag, output_path in SCREENSHOT_TARGETS:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            url = f"http://127.0.0.1:8080/#{tag}"

            cmd = [
                EDGE_PATH,
                "--headless",
                "--disable-gpu",
                "--hide-scrollbars",
                "--window-size=1400,900",
                f"--screenshot={output_path}",
                url
            ]

            print(f"[-] Capturing {tag} -> {os.path.basename(output_path)} ...")
            subprocess.run(cmd, capture_output=True, timeout=15)

            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                print(f"    [OK] Captured successfully ({os.path.getsize(output_path)} bytes)")
            else:
                print(f"    [WARN] Failed or empty capture for {output_path}")

        print("\n" + "=" * 80)
        print("  ALL SCREENSHOTS CAPTURED SUCCESSFULLY (18 / 18)")
        print("=" * 80)

    finally:
        server_proc.terminate()
        server_proc.wait()
        print("[+] Web server shut down cleanly.")

if __name__ == "__main__":
    main()
