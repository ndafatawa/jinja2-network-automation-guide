import yaml, os
from netmiko import ConnectHandler

BASE = os.path.dirname(os.path.dirname(__file__))

def load_dev(host):
    devices = yaml.safe_load(open(f"{BASE}/data/devices.yml"))["devices"]
    return next(d for d in devices if d["hostname"] == host)

def load_config(host):
    return open(f"{BASE}/build/{host}.cfg").read().splitlines()

def get_running(host, ip):
    conn = ConnectHandler(
        device_type="cisco_nxos",
        ip=ip,
        username="admin",
        password="admin"
    )
    running = conn.send_command("show running-config")
    conn.disconnect()
    return running.splitlines()

def deploy(host, dry=True):
    dev = load_dev(host)
    desired = load_config(host)
    running = get_running(host, dev["mgmt_ip"])

    to_push = [line for line in desired if line not in running]

    print("Commands to push:")
    for cmd in to_push:
        print(cmd)

    if dry:
        print("\nDry run only.")
        return

    conn = ConnectHandler(
        device_type="cisco_nxos",
        ip=dev["mgmt_ip"],
        username="admin",
        password="admin"
    )
    conn.send_config_set(to_push)
    conn.save_config()
    conn.disconnect()

if __name__ == "__main__":
    import sys
    host = sys.argv[1]
    mode = "--deploy" in sys.argv
    deploy(host, dry=not mode)

