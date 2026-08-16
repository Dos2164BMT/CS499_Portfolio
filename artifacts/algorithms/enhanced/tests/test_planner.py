import unittest

from network_automation.models import Device, LoopbackTask
from network_automation.planner import build_plan


def task(task_id, address, depends_on=(), device="r1", interface="Loopback0"):
    return LoopbackTask.from_dict(
        {
            "id": task_id,
            "device": device,
            "interface": interface,
            "address": address,
            "description": f"Task {task_id}",
            "depends_on": list(depends_on),
        }
    )


class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.devices = [
            Device(name="r1", host="192.0.2.1"),
            Device(name="r2", host="192.0.2.2"),
        ]

    def test_topological_order_respects_dependency(self):
        tasks = [
            task("second", "1.1.1.2/32", ("first",), "r2"),
            task("first", "1.1.1.1/32", (), "r1"),
        ]
        plan = build_plan(self.devices, tasks)
        self.assertEqual([item.task.task_id for item in plan.tasks], ["first", "second"])

    def test_independent_tasks_are_deterministic(self):
        tasks = [
            task("z-task", "1.1.1.3/32", (), "r2"),
            task("a-task", "1.1.1.1/32", (), "r1"),
        ]
        plan = build_plan(self.devices, tasks)
        self.assertEqual([item.task.task_id for item in plan.tasks], ["a-task", "z-task"])

    def test_cycle_is_rejected(self):
        tasks = [
            task("a", "1.1.1.1/32", ("b",), "r1"),
            task("b", "1.1.1.2/32", ("a",), "r2"),
        ]
        with self.assertRaisesRegex(ValueError, "cycle"):
            build_plan(self.devices, tasks)

    def test_unknown_dependency_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown task"):
            build_plan(
                self.devices,
                [task("a", "1.1.1.1/32", ("missing",), "r1")],
            )

    def test_overlapping_addresses_are_rejected(self):
        tasks = [
            task("a", "10.0.0.1/24", (), "r1"),
            task("b", "10.0.0.2/25", (), "r2"),
        ]
        with self.assertRaisesRegex(ValueError, "Address conflict"):
            build_plan(self.devices, tasks)

    def test_duplicate_interface_is_rejected(self):
        tasks = [
            task("a", "1.1.1.1/32", (), "r1", "Loopback0"),
            task("b", "1.1.1.2/32", (), "r1", "Loopback0"),
        ]
        with self.assertRaisesRegex(ValueError, "Duplicate interface"):
            build_plan(self.devices, tasks)

    def test_commands_and_rollback_are_generated(self):
        plan = build_plan(
            self.devices,
            [task("a", "1.1.1.1/32", (), "r1")],
        )
        planned = plan.tasks[0]
        self.assertIn("ip address 1.1.1.1 255.255.255.255", planned.commands)
        self.assertIn("no interface Loopback0", planned.rollback_commands)


if __name__ == "__main__":
    unittest.main()
