# **Network Automation Project – Jinja2 + Python + Netmiko (Cisco NX-OS VXLAN)**

This project is a complete, production-grade network automation framework for generating, validating, diffing, and deploying Cisco NX-OS VXLAN/EVPN configurations using:

- **Jinja2 templates**
- **YAML + CSV Source-of-Truth (SoT)**
- **Python rendering engine**
- **Diff engine (desired vs running)**
- **Netmiko deployment engine**
- **Automatic backups**
- **Deterministic config generation**

The goal is to allow ANY network engineer (beginner or advanced) to clone the repo, edit YAML/CSV, generate configs, validate diffs, and deploy safely.

---

# **1. Project Folder Structure**

```
project/
│
├── templates/                 # Jinja2 templates
│   ├── nxos/
│   │   ├── device_base.j2
│   │   ├── leaf.j2
│   │   ├── spine.j2
│   │   ├── underlay_intf.j2
│   │   └── overlay_leaf_evpn.j2
│   └── misc/
│       └── macros.j2
│
├── data/                      # Source of Truth (SoT)
│   ├── devices.yml
│   ├── fabric.yml
│   ├── vlans.csv
│   └── overrides.yml
│
├── build/                     # Generated configs (desired state)
│   ├── leaf01.cfg
│   ├── leaf02.cfg
│   ├── spine01.cfg
│   └── spine02.cfg
│
├── backups/                   # Automatic device backups before deploy
│
├── scripts/                   # Python automation scripts
│   ├── render.py
│   ├── diff.py
│   ├── push.py
│   └── helpers.py
│
└── README.md
```

---

# **2. Lab Topology – Cisco VXLAN EVPN**

```
                 ┌───────────────┐
                 │    Spine01     │
                 │   ASN 65000    │
                 └───────┬────────┘
                         │
                 ┌───────┴────────┐
                 │    Spine02      │
                 │   ASN 65000     │
                 └───────┬────────┘
                         ││
     ┌───────────────────┘└───────────────────┐
     │                                        │

      ┌───────────────┐         ┌───────────────┐
      │    Leaf01      │         │    Leaf02      │
      │   ASN 65001    │         │   ASN 65002    │
      │ VTEP 10.1.1.1  │         │ VTEP 10.1.1.2  │
      └───────────────┘         └───────────────┘
```

---

# **3. Requirements**

Install dependencies:

```
pip install -r requirements.txt
```

Includes:

- **jinja2**  
- **pyyaml**  
- **netmiko**  
- **rich**  

---

# **4. Rendering Configurations**

### **Render a single device**

```
python scripts/render.py --host leaf01
```

### **Render all devices**

```
python scripts/render.py --target devices
```

Generated configs appear in:

```
build/<hostname>.cfg
```

---

# **5. Diff (Desired vs Running Config)**

### **Diff one device**

```
python scripts/diff.py --host leaf01
```

### **Diff all devices**

```
python scripts/diff.py --all
```

Example diff:

```diff
- switchport access vlan 10
+ switchport access vlan 20
```

---

# **6. Deployment (Netmiko Push Engine)**

### **Dry-run preview (safe)**

```
python scripts/push.py --host leaf01 --dry-run
```

### **Deploy to device**

```
python scripts/push.py --host leaf01 --deploy
```

Automatic backups stored to:

```
backups/<hostname>_DATE.cfg
```

---

# **7. Credentials Handling**

### **Recommended method — environment variables**

```
export NXOS_USER=admin
export NXOS_PASS=Password123
```

### **Optional — .env file**

```
NXOS_USER=admin
NXOS_PASS=Password123
```

---

# **8. End-to-End Workflow**

1. Update YAML/CSV in `/data`
2. Render configs
3. Review diffs
4. Run dry-run push
5. Deploy to devices
6. Automatic backups saved
7. Git tracks desired state in `/build`

---

# **9. Summary**

This project provides a complete network automation pipeline:

- Fully structured **Source-of-Truth**
- Clean templating using **Jinja2**
- Python rendering engine
- Deterministic config generation
- Netmiko deployment engine
- Automated backups
- Config diffing for safety
- Production-grade folder layout
- Vendor-scalable design

Anyone can clone the repo, edit data, generate configs, validate them, and deploy safely across Cisco NX-OS VXLAN/EVPN fabrics.

