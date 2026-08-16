import unittest

from network_automation.models import Device, LoopbackTask


class ModelTests(unittest.TestCase):
    def test_device_rejects_invalid_port(self):
        with self.assertRaisesRegex(ValueError, "Invalid SSH port"):
            Device(name="r1", host="192.0.2.1", port=70000)

    def test_task_parses_ipv4_interface(self):
        task = LoopbackTask.from_dict(
            {
                "id": "task-a",
                "device": "r1",
                "interface": "Loopback0",
                "address": "1.1.1.1/32",
                "description": "Management",
            }
        )
        self.assertEqual(str(task.address), "1.1.1.1/32")

    def test_task_rejects_non_loopback_interface(self):
        with self.assertRaisesRegex(ValueError, "invalid interface"):
            LoopbackTask.from_dict(
                {
                    "id": "task-a",
                    "device": "r1",
                    "interface": "GigabitEthernet0/1",
                    "address": "1.1.1.1/32",
                    "description": "Management",
                }
            )


if __name__ == "__main__":
    unittest.main()
