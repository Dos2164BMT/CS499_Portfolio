"""JSON input and output functions."""

from __future__ import annotations

import json
from pathlib import Path

from .executor import TaskResult
from .models import Device, LoopbackTask


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"File not found: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in {path}: {error}") from error


def load_devices(path: Path) -> list[Device]:
    raw = _load_json(path)
    if not isinstance(raw, list):
        raise ValueError("Inventory must be a JSON array")
    return [Device(**item) for item in raw]


def load_tasks(path: Path) -> list[LoopbackTask]:
    raw = _load_json(path)
    if not isinstance(raw, list):
        raise ValueError("Requests must be a JSON array")
    return [LoopbackTask.from_dict(item) for item in raw]


def write_report(path: Path, results: list[TaskResult]) -> None:
    payload = {
        "summary": {
            "total": len(results),
            "planned": sum(result.status == "planned" for result in results),
            "applied": sum(result.status == "applied" for result in results),
            "failed": sum(result.status == "failed" for result in results),
        },
        "results": [result.to_dict() for result in results],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
