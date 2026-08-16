"""Domain models and input validation for the enhanced artifact."""

from __future__ import annotations

from dataclasses import dataclass, field
from ipaddress import IPv4Interface, ip_interface
import re


INTERFACE_PATTERN = re.compile(r"^Loopback([0-9]|[1-9][0-9]{1,3})$")
HOST_PATTERN = re.compile(r"^[A-Za-z0-9.-]+$")


@dataclass(frozen=True, slots=True)
class Device:
    """A managed Cisco IOS device."""

    name: str
    host: str
    port: int = 22
    platform: str = "cisco_ios"

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Device name cannot be empty")
        if not HOST_PATTERN.fullmatch(self.host):
            raise ValueError(f"Invalid device host: {self.host}")
        if not 1 <= self.port <= 65535:
            raise ValueError(f"Invalid SSH port: {self.port}")
        if self.platform != "cisco_ios":
            raise ValueError(f"Unsupported platform: {self.platform}")


@dataclass(frozen=True, slots=True)
class LoopbackTask:
    """A requested loopback-interface configuration."""

    task_id: str
    device: str
    interface: str
    address: IPv4Interface
    description: str
    depends_on: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, raw: dict) -> "LoopbackTask":
        required = {"id", "device", "interface", "address", "description"}
        missing = required - raw.keys()
        if missing:
            raise ValueError(f"Task is missing fields: {sorted(missing)}")

        task_id = str(raw["id"]).strip()
        device = str(raw["device"]).strip()
        interface = str(raw["interface"]).strip()
        description = str(raw["description"]).strip()
        dependencies = tuple(str(value).strip() for value in raw.get("depends_on", []))

        if not task_id:
            raise ValueError("Task id cannot be empty")
        if not device:
            raise ValueError(f"Task {task_id} has no device")
        if not INTERFACE_PATTERN.fullmatch(interface):
            raise ValueError(f"Task {task_id} has invalid interface {interface}")
        if not description or len(description) > 80:
            raise ValueError(f"Task {task_id} description must contain 1-80 characters")

        parsed = ip_interface(str(raw["address"]))
        if not isinstance(parsed, IPv4Interface):
            raise ValueError(f"Task {task_id} requires an IPv4 address")

        return cls(
            task_id=task_id,
            device=device,
            interface=interface,
            address=parsed,
            description=description,
            depends_on=dependencies,
        )
