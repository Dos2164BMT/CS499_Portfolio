from pathlib import Path
import sqlite3
import tempfile
import unittest
from network_automation.database import AutomationDatabase
from network_automation.executor import TaskResult
from network_automation.models import Device, LoopbackTask

class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "automation.db"
        self.database = AutomationDatabase(self.path)
        self.database.initialize()
        self.devices = [Device(name="router-a", host="192.0.2.10")]
        self.tasks = [LoopbackTask.from_dict({"id": "task-a", "device": "router-a", "interface": "Loopback0", "address": "10.10.10.1/32", "description": "Management"})]
    def tearDown(self):
        self.database.close(); self.temp.cleanup()
    def test_schema_and_foreign_keys_are_enabled(self):
        enabled = self.database.connection.execute("PRAGMA foreign_keys").fetchone()[0]
        tables = {row[0] for row in self.database.connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertEqual(1, enabled); self.assertTrue({"devices", "task_requests", "execution_runs", "task_results", "audit_events"} <= tables)
    def test_configuration_intent_persists(self):
        self.database.store_intent(self.devices, self.tasks); self.database.close(); self.database = AutomationDatabase(self.path)
        self.assertEqual(1, self.database.connection.execute("SELECT COUNT(*) FROM task_requests").fetchone()[0])
    def test_run_results_and_audit_events_are_recorded(self):
        self.database.store_intent(self.devices, self.tasks); run_id = self.database.start_run("dry-run", 1)
        self.database.record_results(run_id, [TaskResult("task-a", "router-a", "planned", 0, "preview", "2026-08-03T12:00:00+00:00")]); self.database.finish_run(run_id, 0)
        self.assertEqual("completed", self.database.recent_runs(1)[0]["status"]); self.assertEqual(2, len(self.database.audit_events(run_id)))
    def test_recent_run_limit_is_bounded(self):
        for _ in range(3):
            run_id = self.database.start_run("dry-run", 0); self.database.finish_run(run_id, 0)
        self.assertEqual(1, len(self.database.recent_runs(1))); self.assertEqual(3, len(self.database.recent_runs(999)))
    def test_unknown_device_rolls_back_entire_transaction(self):
        bad = LoopbackTask.from_dict({"id": "bad", "device": "missing", "interface": "Loopback1", "address": "10.10.10.2/32", "description": "Invalid"})
        with self.assertRaises(ValueError): self.database.store_intent(self.devices, [self.tasks[0], bad])
        counts = (self.database.connection.execute("SELECT COUNT(*) FROM devices").fetchone()[0], self.database.connection.execute("SELECT COUNT(*) FROM task_requests").fetchone()[0])
        self.assertEqual((0, 0), counts)
    def test_database_constraints_reject_invalid_results(self):
        self.database.store_intent(self.devices, self.tasks); run_id = self.database.start_run("dry-run", 1)
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.connection:
                self.database.connection.execute("INSERT INTO task_results(run_id, task_id, device_name, status, commands_sent, message, recorded_at) VALUES (?, ?, ?, ?, ?, ?, ?)", (run_id, "task-a", "router-a", "invalid", -1, "bad", "now"))

if __name__ == "__main__": unittest.main()
