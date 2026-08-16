"""Original artifact: configure one hard-coded Cisco IOS loopback with Paramiko."""

import paramiko


router = {
    "host": "192.168.1.1",
    "username": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD",
}

commands = [
    "enable",
    "configure terminal",
    "interface loopback0",
    "ip address 1.1.1.1 255.255.255.255",
    "no shutdown",
    "end",
    "write memory",
]

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(
    hostname=router["host"],
    username=router["username"],
    password=router["password"],
)

shell = client.invoke_shell()
for command in commands:
    shell.send(command + "\n")

client.close()
