# **16 – Production-Grade Project Structure & CI/CD Workflow**

This chapter explains how to take your automation from “lab level” to real enterprise production standards.

It covers:

- directory layout
- data modeling
- template organization
- validation
- rendering pipeline
- Git workflow
- CI/CD
- compliance and drift detection
- deployment (dry-run + push)
- multi-vendor scalability

This is the blueprint used by actual automation teams in Fortune 500 networks.

---

# **16.1 Core Principles of a Production Automation Repository**

A production project must follow these rules:

### **1. Predictable structure**
Everything has a clear home (templates, data, scripts, build).

### **2. Data separation**
Templates never store device-specific data — YAML/CSV/JSON/Excel do.

### **3. Deterministic output**
Every run must produce identical results given identical input.

### **4. Version control**
Every config is stored in Git. All changes are diffable.

### **5. Validation**
Bad inputs must be caught before generating configs.

### **6. Idempotent rendering**
Regenerate 100 times → output is identical 100 times.

### **7. Vendor scalability**
Project must support NX-OS, EOS, Junos, FortiOS, Palo Alto, etc.

### **8. CI/CD integration**
Automation should run tests on every commit.

---

# **16.2 Recommended Production Directory Structure**

```
project/
│
├── data/
│   ├── devices.yml
│   ├── fabric.yml
│   ├── vlans.csv
│   ├── underlay.csv
│   ├── overrides.yml
│   └── tenants/
│       └── tenantA.yml
│
├── templates/
│   ├── nxos/
│   │   ├── device_base.j2
│   │   ├── leaf.j2
│   │   ├── spine.j2
│   │   ├── underlay_intf.j2
│   │   ├── underlay_ospf.j2
│   │   ├── overlay_leaf_evpn.j2
│   │   └── overlay_spine_rr.j2
│   │
│   ├── eos/
│   │   └── leaf_vlan_demo.j2
│   │
│   ├── fortigate/
│   │   ├── addr.j2
│   │   └── policy.j2
│   │
│   └── misc/
│       └── macros.j2
│
├── scripts/
│   ├── render.py
│   ├── validate.py
│   ├── push.py
│   └── diff.py
│
├── build/
│   └── <generated device configs>
│
├── tests/
│   ├── test_vlan_ids.py
│   ├── test_vrf_names.py
│   └── test_interfaces.py
│
├── requirements.txt
└── README.md
```

This structure supports:

- multi-vendor  
- multi-site  
- scalable templates  
- CI/CD  
- validation  
- safe deployments  

---

# **16.3 Data Modeling Strategy**

Data must be clean, deterministic, normalized.

## **YAML for structured inventory**

Example **devices.yml**:

```
devices:
  - hostname: leaf01
    os: nxos
    role: leaf
    mgmt_ip: 172.16.10.11/24
    loopbacks:
      lo0: 10.0.0.11/32
      lo1: 10.1.0.11/32
```

---

## **CSV for large tables**

Example **vlans.csv**:

```
device,vlan_id,name,vni,ip
leaf01,10,Servers,10100,10.10.10.1/24
leaf01,20,Users,10200,10.10.20.1/24
```

Use CSV when:

- many rows (hundreds/thousands)
- data comes from Excel/CMDB
- team edits spreadsheets

---

## **Overrides**
Used for one-off device changes.

---

# **16.4 Template Organization (Production Standards)**

Templates must be:

✔ modular  
✔ small  
✔ testable  
✔ vendor-isolated  

### **Separation of concerns**

- `device_base.j2` → structure  
- `leaf.j2` / `spine.j2` → device roles  
- `underlay_intf.j2` → underlay  
- `overlay_leaf_evpn.j2` → EVPN overlay  
- `macros.j2` → reusable blocks  

Avoid giant templates.  
**Small templates = maintainable templates.**

---

# **16.5 Python Rendering Pipeline (Production-Grade)**

A real renderer must:

1. Load YAML/CSV/JSON/Excel  
2. Merge data using hostname  
3. Validate required fields  
4. Register custom filters  
5. Select template (os/role)  
6. Render  
7. Write to build directory  
8. (Optional) Push to device/API  

### Example pipeline:

```python
env = Environment(
    loader=FileSystemLoader("templates"),
    trim_blocks=True,
    lstrip_blocks=True,
    undefined=StrictUndefined
)

env.filters['cidr_to_ipmask'] = cidr_to_ipmask
env.filters['vni_rt'] = vni_rt

devices = load_yaml("data/devices.yml")["devices"]
fabric = load_yaml("data/fabric.yml")
vlans = load_csv("data/vlans.csv")

for dev in devices:
    context = merge_data(dev, fabric, vlans)
    validate(context)
    tpl_name = pick_template(context)
    tpl = env.get_template(tpl_name)
    output = tpl.render(context)
    write(f"build/{dev['hostname']}.cfg", output)
```

This is **real-world enterprise automation**.

---

# **16.6 Validation Pipeline (Critical)**

Validation is what separates a safe automation from a dangerous one.

### **Check required attributes**
```python
assert 'hostname' in dev
assert 'mgmt_ip' in dev
assert 'role' in dev
```

### **Check VLAN IDs**
```
assert 1 <= vlan['id'] <= 4094
```

### **Check VNI ranges**
```
assert 10000 <= vlan['vni'] <= 50000
```

### **Check IPs using ipaddress module**

### **Check duplicates**
```python
seen = set()
for v in vlans:
    assert v['id'] not in seen
    seen.add(v['id'])
```

Validation prevents destructive configs.

---

# **16.7 Git Workflow (Production Method)**

### **Branching model**
```
main
 └── dev
      └── feature/<something>
```

### **Typical flow**
1. Developer makes change in `feature/vlan-update`  
2. Commit + push  
3. CI runs validation + tests  
4. Reviewer approves PR  
5. Merge into `dev`  
6. Render configs in staging  
7. Approve change  
8. Merge into `main`  
9. Auto-render + push to production devices  

---

# **16.8 CI/CD Workflow (Enterprise Grade)**

Use GitHub Actions or GitLab CI.

CI must run:

- YAML syntax check  
- CSV validation  
- Python unit tests  
- Jinja render smoke test  
- Whitespace consistency test  

### Example GitHub Action:

```yaml
name: validate

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install -r requirements.txt
      - run: yamllint data/
      - run: pytest tests/
      - run: python scripts/render.py --dry-run
```

CI prevents broken templates from reaching production.

---

# **16.9 Diff Checking (Before Pushing Config)**

Before deploying configs:

```
python scripts/diff.py --host leaf01
```

### Typical diff.py:
```python
import difflib
running = get_running_config(host)
generated = open(f"build/{host}.cfg").read()

for line in difflib.unified_diff(
        running.splitlines(),
        generated.splitlines(),
        fromfile='running',
        tofile='generated'):
    print(line)
```

If diff is empty → safe to push.

---

# **16.10 Deployment Workflow (Safe Production Push)**

### Dry-run first:
```
python scripts/push.py --host leaf01 --dry-run
```

### If safe, push:
```
python scripts/push.py --host leaf01
```

### Typical push logic:
```python
if not dry_run:
    conn.send_config_set(config.splitlines())
```

Supports:

- NX-OS (Netmiko)  
- FortiGate (API)  
- Junos (PyEZ)  
- Palo Alto (REST)  
- EOS (eAPI)  

---

# **16.11 Compliance and Drift Detection**

A production automation system must detect drift.

```
python scripts/diff.py --all
```

If a device config differs from generated config:

- mark device as drifted  
- alert the team  
- require remediation  

This ensures configs match the Source of Truth.

---

# **16.12 Multi-Vendor Strategy**

Production automation must support multiple vendors.

### Recommended approach:
- Put templates in folders per vendor:  
  - `templates/nxos/`  
  - `templates/eos/`  
  - `templates/fortigate/`  
  - `templates/junos/`  
  - `templates/panos/`  
- Keep vendor-neutral data in YAML  
- Use vendor-specific filters  
- Python chooses template by OS  

---

# **16.13 Production-Ready Features to Add Over Time**

✔ SNMP/AAA/logging templates  
✔ Syslog & telemetry templates  
✔ QoS profiles  
✔ ACL/PBR/NAT  
✔ BGP templates for WAN routers  
✔ Firewall services + objects + rules  
✔ Automated rollback  
✔ Golden config testing  
✔ Excel integration (pandas)  
✔ REST API server for generating configs  

This is the roadmap to **full enterprise automation**.

---

# **16.14 Summary**

A production-ready automation system must include:

- Strong data modeling  
- Validated YAML/CSV/JSON  
- Deterministic, stable templates  
- Custom filters  
- Inheritance + modular structure  
- Automated rendering pipeline  
- Dry-run + diff checks  
- Safe push to devices  
- CI/CD automation  
- Compliance + drift detection  
- Multi-vendor support  
