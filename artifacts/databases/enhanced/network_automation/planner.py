"""Algorithms that validate requests and produce a deterministic execution plan."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import heapq
from ipaddress import IPv4Network

from .models import Device, LoopbackTask


@dataclass(frozen=True, slots=True)
class PlannedTask:
    """A validated task with forward and rollback commands."""

    task: LoopbackTask
    device: Device
    commands: tuple[str, ...]
    rollback_commands: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AutomationPlan:
    """Immutable plan in dependency-safe order."""

    tasks: tuple[PlannedTask, ...]


def _index_devices(devices: list[Device]) -> dict[str, Device]:
    """Create an O(1) device lookup while rejecting duplicate names."""

    index: dict[str, Device] = {}
    for device in devices:
        if device.name in index:
            raise ValueError(f"Duplicate device name: {device.name}")
        index[device.name] = device
    return index


def _validate_unique_resources(tasks: list[LoopbackTask]) -> None:
    """Reject duplicate task IDs, interfaces, and overlapping IPv4 networks."""

    task_ids: set[str] = set()
    interfaces: set[tuple[str, str]] = set()
    networks: list[tuple[int, int, str, IPv4Network]] = []

    for task in tasks:
        if task.task_id in task_ids:
            raise ValueError(f"Duplicate task id: {task.task_id}")
        task_ids.add(task.task_id)

        resource = (task.device, task.interface)
        if resource in interfaces:
            raise ValueError(f"Duplicate interface request: {task.device}/{task.interface}")
        interfaces.add(resource)

        network = task.address.network
        networks.append(
            (
                int(network.network_address),
                int(network.broadcast_address),
                task.task_id,
                network,
            )
        )

    # Sorting converts all-pairs overlap detection from O(n^2) to O(n log n).
    networks.sort(key=lambda item: (item[0], item[1], item[2]))
    max_end = -1
    max_task = ""
    max_network: IPv4Network | None = None
    for start, end, task_id, network in networks:
        if start <= max_end:
            raise ValueError(
                f"Address conflict: {task_id} ({network}) overlaps "
                f"{max_task} ({max_network})"
            )
        if end > max_end:
            max_end = end
            max_task = task_id
            max_network = network


def _topological_order(tasks: list[LoopbackTask]) -> list[LoopbackTask]:
    """Return dependency-safe order using Kahn's O(V+E) algorithm."""

    task_index = {task.task_id: task for task in tasks}
    adjacency: dict[str, list[str]] = defaultdict(list)
    indegree = {task.task_id: 0 for task in tasks}

    for task in tasks:
        for dependency in task.depends_on:
            if dependency not in task_index:
                raise ValueError(
                    f"Task {task.task_id} depends on unknown task {dependency}"
                )
            adjacency[dependency].append(task.task_id)
            indegree[task.task_id] += 1

    # A heap makes otherwise valid orders deterministic by task id.
    ready = [task_id for task_id, degree in indegree.items() if degree == 0]
    heapq.heapify(ready)
    ordered: list[LoopbackTask] = []

    while ready:
        task_id = heapq.heappop(ready)
        ordered.append(task_index[task_id])
        for neighbor in sorted(adjacency[task_id]):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(ready, neighbor)

    if len(ordered) != len(tasks):
        cyclic = sorted(task_id for task_id, degree in indegree.items() if degree)
        raise ValueError(f"Dependency cycle detected: {cyclic}")
    return ordered


def _commands(task: LoopbackTask) -> tuple[tuple[str, ...], tuple[str, ...]]:
    address = task.address.ip
    netmask = task.address.network.netmask
    forward = (
        "configure terminal",
        f"interface {task.interface}",
        f"description {task.description}",
        f"ip address {address} {netmask}",
        "no shutdown",
        "end",
        "write memory",
    )
    rollback = (
        "configure terminal",
        f"no interface {task.interface}",
        "end",
        "write memory",
    )
    return forward, rollback


def build_plan(devices: list[Device], tasks: list[LoopbackTask]) -> AutomationPlan:
    """Validate all inputs before returning an immutable execution plan."""

    device_index = _index_devices(devices)
    _validate_unique_resources(tasks)
    ordered_tasks = _topological_order(tasks)
    planned: list[PlannedTask] = []

    for task in ordered_tasks:
        if task.device not in device_index:
            raise ValueError(f"Task {task.task_id} references unknown device {task.device}")
        forward, rollback = _commands(task)
        planned.append(
            PlannedTask(
                task=task,
                device=device_index[task.device],
                commands=forward,
                rollback_commands=rollback,
            )
        )

    return AutomationPlan(tasks=tuple(planned))
