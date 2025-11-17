# **13 – Rendering Script (`render.py`) — Full Line-By-Line Explanation**

The rendering script is the **engine** of your automation project.
It performs all major tasks:

- loads YAML / CSV / JSON / Excel  
- validates the data model  
- merges inputs into a Python dictionary (context)  
- selects the correct Jinja2 template  
- registers custom filters  
- renders configurations for all devices  
- writes files into the `build/` directory  

This chapter explains how a proper `render.py` is structured and how every part works.

---

# **13.1 High-Level Pipeline**

A rendering script performs these steps:

```
YAML / CSV / JSON / Excel
        ↓
Python loads + validates
        ↓
Context dictionary
        ↓
Template selected (NX-OS, EOS, FortiGate, etc.)
        ↓
Jinja2 renders template
        ↓
Output saved to build/<device>.cfg
```

This is the **core of all automation systems** (Ansible, Salt, Nornir, custom frameworks).

---

# **13.2 Basic Project Structure**

```
project/
│
├── data/
│   ├── devices.yml
│   ├── fabric.yml
│   ├── vlans.csv
│   ├── overrides.yml
│
├── templates/
│   ├── nxos/
│   ├── eos/
│   ├── fortigate/
│   ├── misc/macros.j2
│
├── scripts/
│   └── render.py
│
└── build/
```

---

# **13.3 Importing Required Modules**

```python
import yaml
import csv
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined
```

**Purpose:**

- `yaml` → load YAML device/fabric data  
- `csv` → load CSV lists (VLANs, address objects, rules)  
- `Path` → clean path operations  
- `Environment` / `FileSystemLoader` → Jinja2 engine  
- `StrictUndefined` → prevent missing variables from silently rendering  

---

# **13.4 Loading YAML Files**

```python
def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)
```

Key points:

- `safe_load()` prevents insecure parsing
- returns dict/list depending on the YAML structure

Used for:

- devices.yml  
- fabric.yml  
- overrides.yml  

---

# **13.5 Loading CSV Files**

```python
def load_csv(path):
    with open(path) as f:
        reader = csv.DictReader(f)
        return list(reader)
```

Why:

- CSV rows become a list of dictionaries  
- perfect for VLANs, objects, services, rules

Example row:

```
{ "id": "10", "name": "SERVERS" }
```

---

# **13.6 Building the Jinja2 Environment**

```python
env = Environment(
    loader=FileSystemLoader("templates"),
    trim_blocks=True,
    lstrip_blocks=True,
    undefined=StrictUndefined
)
```

**trim_blocks / lstrip_blocks** → ensures clean deterministic output  
(no blank lines, perfect indentation)

**StrictUndefined** → renders **error** if variable is missing  
(prevents invalid configs entering production)

---

# **13.7 Registering Custom Filters**

Example:

```python
def vni_rt(vni, asn):
    return f"{asn}:{int(vni)}"

def cidr_to_ipmask(cidr):
    import ipaddress
    ip = ipaddress.ip_interface(cidr)
    return f"{ip.ip} {ip.network.netmask}"

env.filters['vni_rt'] = vni_rt
env.filters['cidr_to_ipmask'] = cidr_to_ipmask
```

Custom filters are essential for:

- EVPN route-target calculations  
- converting CIDR → subnet mask (FortiGate)  
- name normalization

These reduce template complexity.

---

# **13.8 Loading All Data**

```python
DEVICES = load_yaml("data/devices.yml")
FABRIC  = load_yaml("data/fabric.yml")
VLANS   = load_csv("data/vlans.csv")
OVERRIDES = load_yaml("data/overrides.yml")
```

Data is now Python dictionaries/lists.

---

# **13.9 Merging Data Into Per-Device Context**

Each device receives:

- its own YAML entry  
- fabric-wide values  
- global VLANs  
- CSV-based lists  
- device-specific overrides  

Example merge:

```python
def build_context(device):
    ctx = {}

    # Base device data
    ctx.update(device)

    # Fabric-wide values
    ctx['fabric'] = FABRIC

    # All VLANs
    ctx['vlans'] = VLANS

    # Apply device overrides (optional)
    if device['hostname'] in OVERRIDES:
        for k,v in OVERRIDES[device['hostname']].items():
            ctx[k] = v

    return ctx
```

**ctx (context)** = dictionary passed to Jinja2

---

# **13.10 Validating Required Data Fields**

Before rendering, validate fields:

```python
def validate(device):
    required = ['hostname', 'os', 'role', 'mgmt_ip']
    for r in required:
        if r not in device:
            raise ValueError(f"Missing required field {r} in {device}")
```

Validation prevents:

- mistakes
- incomplete configs
- mis-typed YAML keys

---

# **13.11 Selecting Template per Device**

```python
def select_template(device):
    if device['os'] == 'nxos':
        if device['role'] == 'leaf':
            return env.get_template('nxos/leaf.j2')
        if device['role'] == 'spine':
            return env.get_template('nxos/spine.j2')

    if device['os'] == 'eos':
        return env.get_template('eos/leaf_vlan_demo.j2')

    if device['os'] == 'fortigate':
        return env.get_template('fortigate/addr_objects.j2')

    raise ValueError(f"No template for device {device['hostname']} (os={device['os']})")
```

This allows multi-vendor rendering without rewriting logic.

---

# **13.12 Rendering and Writing Output**

```python
def render_device(device):
    validate(device)
    ctx = build_context(device)
    tpl = select_template(device)
    output = tpl.render(ctx)

    outfile = Path("build") / f"{device['hostname']}.cfg"
    outfile.write_text(output)

    print(f"[OK] Rendered {outfile}")
```

**Steps:**

1. validate  
2. build context  
3. select correct template  
4. render the configuration  
5. save output into `build/hostname.cfg`  

---

# **13.13 Rendering All Devices**

```python
def main():
    for dev in DEVICES:
        render_device(dev)
```

---

# **13.14 Rendering a Single Device (CLI Option)**

Useful for debugging.

```python
import argparse

p = argparse.ArgumentParser()
p.add_argument("--host", help="Render only one device")
args = p.parse_args()

if args.host:
    for d in DEVICES:
        if d['hostname'] == args.host:
            render_device(d)
            exit()
    print("Device not found.")
else:
    main()
```

Example:

```
python3 render.py --host LEAF1
```

---

# **13.15 How to Extend the Rendering Script**

### **Add Excel Support**
Load using pandas:

```python
import pandas as pd
df = pd.read_excel("data/services.xlsx")
SERVICES = df.to_dict(orient="records")
```

---

### **Add JSON Imports**

```python
import json
with open("data/api_export.json") as f:
    DATA = json.load(f)
```

---

### **Add More Filters**

- safe_name  
- masklen  
- net_prefix  
- prefix_sort  

Just define function → register with `env.filters`.

---

### **Add More Vendor Templates**

```
templates/
  junos/
  paloalto/
  checkpoint/
```

Add template selection in `select_template(device)`.

---

# **13.16 Best Practices for a Production-Grade Renderer**

- **Never** embed logic in templates; do it in Python.  
- **Always** use StrictUndefined.  
- Validate **every** YAML/CSV field.  
- Keep paths consistent.  
- Use Git to track rendered output changes.  
- Avoid complex, nested filters inside templates.  
- Break templates into clean blocks using includes + inheritance.  
- Use macros for reusable structured config.  
- Test on multiple devices before deployment.  

---

Your `render.py` is the beating heart of your automation system.

It combines all data, logic, filters, and templates into clean, deterministic, production-ready configurations.
