import json
import os
import sys
import unittest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from app.routes import USERS
from app.logging_config import LOG_FILE_PATH



class TestPatientApi(unittest.TestCase):
    """Test suite for SentinelOps Patient application."""

    def setUp(self):
        # raise_server_exceptions=False allows testing HTTP 500 error responses and log capture
        self.client = TestClient(app, raise_server_exceptions=False)


    def test_health_endpoint_returns_200(self):
        """1. /api/health returns HTTP 200 and healthy status."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "sentinelops-patient")

    def test_get_users_returns_200(self):
        """2. /api/users returns HTTP 200 and complete list of users."""
        response = self.client.get("/api/users")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 3)
        self.assertEqual(data[0]["name"], "Alice Johnson")

    def test_valid_user_lookup_succeeds(self):
        """3. Valid user lookup (/api/user/1) works cleanly."""
        response = self.client.get("/api/user/1")
        self.assertEqual(response.status_code, 200)
        user = response.json()
        self.assertEqual(user["id"], 1)
        self.assertEqual(user["name"], "Alice Johnson")
        self.assertEqual(user["email"], "alice@example.com")

    def test_broken_request_reproduces_intentional_indexerror(self):
        """
        4. The intentionally broken request (/api/user/999) reproduces IndexError.
        Verifies that:
        - HTTP 500 is returned
        - Exception type is IndexError
        - Exception is logged to logs/app.log
        """
        # Ensure log file existence
        initial_log_count = 0
        if os.path.exists(LOG_FILE_PATH):
            with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
                initial_log_count = len(f.readlines())

        response = self.client.get("/api/user/999")
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertEqual(data["exception_type"], "IndexError")
        self.assertIn("list index out of range", data["message"])

        # Check log file contains the structured JSON error entry
        self.assertTrue(os.path.exists(LOG_FILE_PATH))
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            self.assertGreater(len(lines), initial_log_count)
            last_entry = json.loads(lines[-1])
            self.assertEqual(last_entry["exception_type"], "IndexError")
            self.assertEqual(last_entry["path"], "/api/user/999")
            self.assertIn("Traceback", last_entry["traceback"])

    def test_server_remains_healthy_after_exception(self):
        """Verifies that the server does not crash and /api/health still returns 200."""
        # Trigger failure first
        self.client.get("/api/user/999")

        # Health endpoint must remain fully functional
        health_resp = self.client.get("/api/health")
        self.assertEqual(health_resp.status_code, 200)
        self.assertEqual(health_resp.json()["status"], "healthy")

    def test_manual_fix_simulation(self):
        """
        5. Demonstrates the expected behavior once the bug is resolved:
        Using a safe lookup guard returns a 404 or None instead of an IndexError.
        """
        user_id = 999
        matching = [u for u in USERS if u["id"] == user_id]
        # Fixed logic:
        fixed_result = matching[0] if matching else None
        self.assertIsNone(fixed_result)


if __name__ == "__main__":
    unittest.main()
