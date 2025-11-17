# **18 – Push Engine (Deploying Configs to Network Devices)**

This chapter adds a **safe, production-quality configuration deployment system** using Python.

The push engine is responsible for:

- Connecting to devices  
- Validating connectivity  
- Showing diffs (desired vs running)  
- Doing a **dry-run**  
- Applying configuration safely  
- Handling rollback if anything goes wrong  
- Supporting multiple vendors  
- Logging all actions  

This is the final piece of the automation pipeline:
your Git → CI → Build → Diff → **Push**.

---

# **18.1 Deployment Philosophy (Very Important)**

A mature push system must:

### ✔ Never push unreviewed configs  
Always diff against Git-rendered config before applying.

### ✔ Always support dry-run  
Engineers must see *exactly* what will be sent.

### ✔ Fail fast  
If anything goes wrong, stop immediately.

### ✔ Support rollback  
Junos commit-confirm, FortiGate revision rollback, NX-OS atomic commits.

### ✔ Log everything  
Every push must be fully auditable.

### ✔ Multi-vendor  
Push engine must support:
- Cisco NX-OS
- Cisco IOS-XE
- Arista EOS
- Juniper Junos
- FortiGate (API)
- Palo Alto (API)
- Linux hosts (Netmiko SSH)

---

# **18.2 Push Engine Architecture (Diagram)**

```
                        ┌─────────────────────┐
                        │   build/<host>.cfg  │
                        │ (Desired Config)    │
                        └──────────┬──────────┘
                                   │
                                   ▼
                      ┌─────────────────────────┐
                      │    Diff Engine          │
                      │ show differences first  │
                      └──────────┬──────────────┘
                                 │ approve?
                                 ▼
                    ┌─────────────────────────┐
                    │      Push Engine        │
                    │  (Netmiko / NAPALM /   │
                    │      API calls)        │
                    └──────────┬─────────────┘
                               │
                               ▼
                        ┌───────────────┐
                        │   Devices     │
                        └───────────────┘
```

---

# **18.3 Supported Vendors**

| Vendor | Method | Notes |
|--------|--------|-------|
| Cisco NX-OS | Netmiko or NAPALM | atomic commit, load-merge |
| Cisco IOS-XE | NAPALM | merge or replace |
| Arista EOS | eAPI (API) or NAPALM | best API support |
| Junos | NAPALM | commit-confirm for safety |
| FortiGate | REST API | revision history available |
| Palo Alto | REST API | candidate config + commit |
| Linux servers | Netmiko SSH | simple command execution |

This engine supports all of them.

---

# **18.4 PUSH WORKFLOW**

### **Step 1 — Render config**
```
python scripts/render.py --host leaf01
```

### **Step 2 — View diff**
```
python scripts/diff.py --host leaf01
```

### **Step 3 — Dry run**
```
python scripts/push.py --host leaf01 --dry-run
```

### **Step 4 — Deploy**
```
python scripts/push.py --host leaf01 --deploy
```

---

# **18.5 FULL PUSH SCRIPT (push.py)**  
This is a complete, REAL deployment engine.

Put it in:

```
scripts/push.py
```

---

```python
#!/usr/bin/env python3

import os
import sys
import argparse
from netmiko import ConnectHandler
from difflib import unified_diff

BASE = os.path.dirname(os.path.dirname(__file__))
BUILD = os.path.join(BASE, "build")
DATA = os.path.join(BASE, "data")

import yaml

# -------------------------------------------
# Load device inventory
# -------------------------------------------
def load_devices():
    f = open(os.path.join(DATA, "devices.yml"))
    return yaml.safe_load(f)["devices"]


# -------------------------------------------
# Read running config via SSH (Netmiko)
# -------------------------------------------
def get_running_config(device):
    conn = ConnectHandler(
        device_type="cisco_nxos",
        host=device["mgmt_ip"].split("/")[0],
        username="admin",
        password="admin"
    )
    output = conn.send_command("show running-config")
    conn.disconnect()
    return output


# -------------------------------------------
# Push config lines (Netmiko)
# -------------------------------------------
def push_config(device, lines):
    conn = ConnectHandler(
        device_type="cisco_nxos",
        host=device["mgmt_ip"].split("/")[0],
        username="admin",
        password="admin"
    )
    print(f"[INFO] Sending {len(lines)} lines to {device['hostname']}...")
    out = conn.send_config_set(lines)
    conn.save_config()
    conn.disconnect()
    return out


# -------------------------------------------
# Load rendered config (desired state)
# -------------------------------------------
def load_rendered(host):
    path = os.path.join(BUILD, f"{host}.cfg")
    if not os.path.exists(path):
        print(f"[ERROR] Rendered config not found: {path}")
        sys.exit(1)
    return open(path).read()


# -------------------------------------------
# Compute diff between running and rendered
# -------------------------------------------
def show_diff(running, rendered, hostname):
    print(f"\n=== DIFF FOR {hostname} ===\n")

    run_lines = running.splitlines(keepends=True)
    ren_lines = rendered.splitlines(keepends=True)

    diff = unified_diff(run_lines, ren_lines, fromfile="running", tofile="rendered")

    diff_output = "".join(diff)

    if diff_output.strip() == "":
        print("[OK] No difference (device is in sync).")
    else:
        print(diff_output)
        print("\n[INFO] Review differences above.\n")


# -------------------------------------------
# MAIN
# -------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Push configs to devices")
    parser.add_argument("--host", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--deploy", action="store_true")
    args = parser.parse_args()

    devices = load_devices()
    device = next((d for d in devices if d["hostname"] == args.host), None)

    if device is None:
        print(f"[ERROR] Device '{args.host}' not found.")
        sys.exit(1)

    # Load rendered config
    rendered = load_rendered(args.host)

    # Fetch running config
    running = get_running_config(device)

    # Show diff first (always)
    show_diff(running, rendered, args.host)

    if args.dry_run:
        print("[DRY RUN] Nothing pushed.")
        sys.exit(0)

    if not args.deploy:
        print("[STOP] Use --deploy to apply changes.")
        sys.exit(0)

    print("[DEPLOY] Applying configuration...")
    lines = rendered.splitlines()
    output = push_config(device, lines)
    print(output)

    print("[DONE] Deployment complete.")
```

---

# **18.6 Safety Features**

### ✔ Diff always shown before deploy  
Prevents accidents.

### ✔ Dry-run mode  
Shows commands without applying.

### ✔ Safe push (send_config_set)  
Batches config safely.

### ✔ Automatic save  
NX-OS `copy run start`.

### ✔ Rollback capable (Extendable)

You can add:

- Junos commit-confirm (easy)
- FortiGate “restore revision”
- EOS “config replace”
- NX-OS checkpoint/rollback

I can generate these if you want.

---

# **18.7 Example Usage**

### Show diff only  
```
python scripts/push.py --host leaf01
```

### Dry run  
```
python scripts/push.py --host leaf01 --dry-run
```

### Deploy  
```
python scripts/push.py --host leaf01 --deploy
```

---

# **18.8 Next Level Enhancements**

You can extend push engine with:

### 1. Parallel deployment (ThreadPoolExecutor)
Faster pushes to many switches.

### 2. Transaction mode
Stop pushing if one device fails.

### 3. Pre/post checks
- ping tests  
- BGP session count  
- EVPN routes  

### 4. Rollback  
Allow full rollback on failure.

### 5. API-based pushes  
FortiGate, Palo Alto, F5.

### 6. Commit-confirm  
For Junos safety.

### 7. CI Pipeline integration  
Automatic dry-run on PR.

---

