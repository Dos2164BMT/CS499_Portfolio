#!/usr/bin/env python3
"""CLI for validated, persistent, and auditable loopback automation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from network_automation.executor import DryRunExecutor, ParamikoExecutor, execute_plan
from network_automation.database import AutomationDatabase
from network_automation.io import load_devices, load_tasks, write_report
from network_automation.planner import build_plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plan and audit Cisco IOS loopback changes")
    parser.add_argument("--database", type=Path, default=Path("automation.db"))
    parser.add_argument("--history", type=int, metavar="LIMIT")
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--requests", type=Path)
    parser.add_argument("--report", type=Path, default=Path("automation-report.json"))
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes. Without this flag, the program performs a dry run.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    with AutomationDatabase(args.database) as database:
        database.initialize()
        if args.history is not None:
            print(json.dumps(database.recent_runs(args.history), indent=2))
            return 0
        if not args.inventory or not args.requests:
            print("--inventory and --requests are required unless --history is used", file=sys.stderr)
            return 2
        try:
            devices = load_devices(args.inventory)
            tasks = load_tasks(args.requests)
            plan = build_plan(devices, tasks)
            database.store_intent(devices, tasks)
            mode = "apply" if args.apply else "dry-run"
            run_id = database.start_run(mode, len(plan.tasks))
            executor = ParamikoExecutor.from_environment() if args.apply else DryRunExecutor()
            results = execute_plan(plan, executor)
            database.record_results(run_id, results)
            failed_tasks = sum(result.status == "failed" for result in results)
            database.finish_run(run_id, failed_tasks)
            write_report(args.report, results)
        except (ValueError, RuntimeError) as error:
            print(f"Automation error: {error}", file=sys.stderr)
            return 2
    print(f"{mode}: {len(results)} task(s); run: {run_id}; report: {args.report}")
    return 1 if failed_tasks else 0


if __name__ == "__main__":
    raise SystemExit(main())
