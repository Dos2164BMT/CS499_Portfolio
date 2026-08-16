#!/usr/bin/env python3
"""Command-line entry point for the enhanced network automation artifact."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from network_automation.executor import DryRunExecutor, ParamikoExecutor, execute_plan
from network_automation.io import load_devices, load_tasks, write_report
from network_automation.planner import build_plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and configure Cisco IOS loopback interfaces"
    )
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--requests", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=Path("automation-report.json"))
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes. Without this flag, the program performs a dry run.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        devices = load_devices(args.inventory)
        tasks = load_tasks(args.requests)
        plan = build_plan(devices, tasks)
        executor = ParamikoExecutor.from_environment() if args.apply else DryRunExecutor()
        results = execute_plan(plan, executor)
        write_report(args.report, results)
    except ValueError as error:
        print(f"Validation error: {error}", file=sys.stderr)
        return 2

    failed = any(result.status == "failed" for result in results)
    mode = "apply" if args.apply else "dry-run"
    print(f"{mode}: {len(results)} task(s); report: {args.report}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
