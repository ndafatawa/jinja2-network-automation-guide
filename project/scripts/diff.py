import difflib, os
from netmiko import ConnectHandler
import yaml

BASE = os.path.dirname(os.path.dirname(__file__))

def get_running(host, mgmt_ip):
    conn = ConnectHandler(
        device_type="cisco_nxos",
        ip=mgmt_ip,
        username="admin",
        password="admin"
    )
    output = conn.send_command("show running-config")
    conn.disconnect()

    path = f"{BASE}/backups/{host}-running.cfg"
    with open(path, "w") as f:
        f.write(output)
    return output

def diff(host):
    devices = yaml.safe_load(open(f"{BASE}/data/devices.yml"))["devices"]
    dev = next(d for d in devices if d["hostname"] == host)

    running = get_running(host, dev["mgmt_ip"])
    desired = open(f"{BASE}/build/{host}.cfg").read()

    print("\n".join(
        difflib.unified_diff(
            running.splitlines(),
            desired.splitlines(),
            fromfile="running",
            tofile="desired",
            lineterm=""
        )
    ))

if __name__ == "__main__":
    import sys
    diff(sys.argv[1])

