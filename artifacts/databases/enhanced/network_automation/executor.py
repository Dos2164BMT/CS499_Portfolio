"""Dry-run and Paramiko execution adapters."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import os
import time
from typing import Protocol

from .planner import AutomationPlan, PlannedTask


@dataclass(frozen=True, slots=True)
class TaskResult:
    task_id: str
    device: str
    status: str
    commands_sent: int
    message: str
    timestamp: str

    def to_dict(self) -> dict:
        return asdict(self)


class TaskExecutor(Protocol):
    def execute(self, planned: PlannedTask) -> TaskResult:
        """Execute one planned task."""


class DryRunExecutor:
    """Safe default that reports the plan without changing a router."""

    def execute(self, planned: PlannedTask) -> TaskResult:
        return TaskResult(
            task_id=planned.task.task_id,
            device=planned.device.name,
            status="planned",
            commands_sent=0,
            message=" | ".join(planned.commands),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


class ParamikoExecutor:
    """Apply a plan over SSH with strict known-host verification."""

    def __init__(self, username: str, password: str, command_delay: float = 0.25):
        self.username = username
        self.password = password
        self.command_delay = command_delay

    @classmethod
    def from_environment(cls) -> "ParamikoExecutor":
        username = os.getenv("NETWORK_USERNAME")
        password = os.getenv("NETWORK_PASSWORD")
        if not username or not password:
            raise ValueError(
                "NETWORK_USERNAME and NETWORK_PASSWORD are required with --apply"
            )
        return cls(username=username, password=password)

    def execute(self, planned: PlannedTask) -> TaskResult:
        try:
            import paramiko
        except ImportError as error:
            raise RuntimeError("Install requirements.txt before using --apply") from error

        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
        try:
            client.connect(
                hostname=planned.device.host,
                port=planned.device.port,
                username=self.username,
                password=self.password,
                look_for_keys=False,
                allow_agent=False,
                timeout=10,
            )
            shell = client.invoke_shell()
            for command in planned.commands:
                shell.send(command + "\n")
                time.sleep(self.command_delay)
            return TaskResult(
                task_id=planned.task.task_id,
                device=planned.device.name,
                status="applied",
                commands_sent=len(planned.commands),
                message="Configuration commands sent successfully",
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        finally:
            client.close()


def execute_plan(plan: AutomationPlan, executor: TaskExecutor) -> list[TaskResult]:
    """Execute in topological order and stop after the first failed task."""

    results: list[TaskResult] = []
    for planned in plan.tasks:
        try:
            result = executor.execute(planned)
        except Exception as error:  # boundary converts runtime failures into report data
            result = TaskResult(
                task_id=planned.task.task_id,
                device=planned.device.name,
                status="failed",
                commands_sent=0,
                message=str(error),
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            results.append(result)
            break
        results.append(result)
    return results
