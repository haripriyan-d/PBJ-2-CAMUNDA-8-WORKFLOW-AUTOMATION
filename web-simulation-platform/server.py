#!/usr/bin/env python3
"""
Camunda 8 Workflow Simulation & Monitoring HTTP Server
PBJ-2 Practical Assignment: Labs 1, 2, and 3
"""

import os
import sys
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

class CamundaPlatformHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/models":
            self.serve_models()
        elif path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"UP","version":"Camunda-8.5"}')
        else:
            super().do_GET()

    def serve_models(self):
        def read_file(rel_path):
            full_path = os.path.join(PROJECT_ROOT, rel_path)
            if os.path.exists(full_path):
                with open(full_path, "r", encoding="utf-8") as f:
                    return f.read()
            return ""

        data = {
            "lab1": {
                "bpmn": read_file("Lab-1-Loan-Approval-Automation/loan-approval-process.bpmn"),
                "dmn": read_file("Lab-1-Loan-Approval-Automation/loan-approval-rules.dmn")
            },
            "lab2": {
                "bpmn": read_file("Lab-2-Ecommerce-Order-Fulfilment/ecommerce-order-process.bpmn"),
                "dmn": read_file("Lab-2-Ecommerce-Order-Fulfilment/order-priority-rules.dmn")
            },
            "lab3": {
                "bpmn": read_file("Lab-3-Hospital-Appointment-Triage/hospital-appointment-process.bpmn"),
                "dmn": read_file("Lab-3-Hospital-Appointment-Triage/patient-triage-rules.dmn")
            }
        }
        resp = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(resp)))
        self.end_headers()
        self.wfile.write(resp)

def run():
    server = HTTPServer(("127.0.0.1", PORT), CamundaPlatformHandler)
    print(f"Camunda 8 Simulation Platform running on http://127.0.0.1:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    run()
