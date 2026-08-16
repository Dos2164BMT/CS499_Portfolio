"""SQLite repository for persistent network-automation intent and evidence."""
from __future__ import annotations
from contextlib import contextmanager
from datetime import datetime, timezone
import os
from pathlib import Path
import sqlite3
from typing import Iterable, Iterator
from .executor import TaskResult
from .models import Device, LoopbackTask

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

class AutomationDatabase:
    """Owns schema initialization and parameterized persistence operations."""
    def __init__(self, path: Path | str, schema_path: Path | str | None = None):
        self.path = Path(path)
        self.schema_path = Path(schema_path) if schema_path else Path(__file__).parents[1] / "schema.sql"
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

    def close(self) -> None: self.connection.close()
    def __enter__(self) -> "AutomationDatabase": return self
    def __exit__(self, exc_type, exc, traceback) -> None: self.close()

    def initialize(self) -> None:
        self.connection.executescript(self.schema_path.read_text(encoding="utf-8"))
        self.connection.commit()
        if self.path != Path(":memory:"):
            try: os.chmod(self.path, 0o600)
            except OSError: pass

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        try:
            self.connection.execute("BEGIN")
            yield self.connection
        except Exception:
            self.connection.rollback()
            raise
        else:
            self.connection.commit()

    def store_intent(self, devices: Iterable[Device], tasks: Iterable[LoopbackTask]) -> None:
        device_list, task_list = list(devices), list(tasks)
        with self.transaction() as connection:
            for device in device_list:
                connection.execute("""INSERT INTO devices(name, host, port, platform) VALUES (?, ?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET host=excluded.host, port=excluded.port, platform=excluded.platform""",
                    (device.name, device.host, device.port, device.platform))
            device_ids = {row["name"]: row["device_id"] for row in connection.execute("SELECT device_id, name FROM devices")}
            for task in task_list:
                if task.device not in device_ids:
                    raise ValueError(f"Unknown device in database transaction: {task.device}")
                connection.execute("""INSERT INTO task_requests(task_id, device_id, interface, address, description)
                    VALUES (?, ?, ?, ?, ?) ON CONFLICT(task_id) DO UPDATE SET device_id=excluded.device_id,
                    interface=excluded.interface, address=excluded.address, description=excluded.description""",
                    (task.task_id, device_ids[task.device], task.interface, str(task.address), task.description))
            task_ids = {task.task_id for task in task_list}
            for task in task_list:
                connection.execute("DELETE FROM task_dependencies WHERE task_id = ?", (task.task_id,))
                for dependency in task.depends_on:
                    if dependency not in task_ids:
                        raise ValueError(f"Unknown dependency in database transaction: {dependency}")
                    connection.execute("INSERT INTO task_dependencies(task_id, depends_on_task_id) VALUES (?, ?)", (task.task_id, dependency))

    def start_run(self, mode: str, total_tasks: int) -> int:
        with self.connection:
            cursor = self.connection.execute("INSERT INTO execution_runs(started_at, mode, status, total_tasks) VALUES (?, ?, 'running', ?)", (utc_now(), mode, total_tasks))
            run_id = int(cursor.lastrowid)
            self._add_audit_event(run_id, "run_started", f"{mode} run started")
        return run_id

    def record_results(self, run_id: int, results: Iterable[TaskResult]) -> None:
        with self.connection:
            for result in results:
                self.connection.execute("""INSERT INTO task_results(run_id, task_id, device_name, status, commands_sent, message, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""", (run_id, result.task_id, result.device, result.status, result.commands_sent, result.message, result.timestamp))

    def finish_run(self, run_id: int, failed_tasks: int) -> None:
        status = "failed" if failed_tasks else "completed"
        with self.connection:
            self.connection.execute("UPDATE execution_runs SET finished_at = ?, status = ?, failed_tasks = ? WHERE run_id = ?", (utc_now(), status, failed_tasks, run_id))
            self._add_audit_event(run_id, "run_finished", f"run finished with status {status}")

    def recent_runs(self, limit: int = 10) -> list[dict]:
        safe_limit = max(1, min(int(limit), 100))
        rows = self.connection.execute("""SELECT run_id, started_at, finished_at, mode, status, total_tasks, failed_tasks
            FROM execution_runs ORDER BY run_id DESC LIMIT ?""", (safe_limit,)).fetchall()
        return [dict(row) for row in rows]

    def audit_events(self, run_id: int) -> list[dict]:
        rows = self.connection.execute("SELECT event_type, message, created_at FROM audit_events WHERE run_id = ? ORDER BY event_id", (run_id,)).fetchall()
        return [dict(row) for row in rows]

    def _add_audit_event(self, run_id: int, event_type: str, message: str) -> None:
        self.connection.execute("INSERT INTO audit_events(run_id, event_type, message, created_at) VALUES (?, ?, ?, ?)", (run_id, event_type, message, utc_now()))
