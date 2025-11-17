# **17 – Full Automation Blueprint (End-to-End Architecture & Workflow)**

This chapter ties everything together:
- data modeling  
- templates  
- rendering  
- CI/CD  
- diff  
- push  
- drift detection  
- multi-vendor handling  
- compliance  

This is the **full automation blueprint** you would present to a senior engineer, architect, or employer to demonstrate complete production-grade network automation mastery.

---

# **17.1 High-Level Architecture Diagram**

Below is a clear ASCII architecture diagram showing how all pieces interact:

```
                           ┌─────────────────────────┐
                           │        Git Repo         │
                           │  (Templates + Data +    │
                           │   Python Render Code)   │
                           └───────────┬─────────────┘
                                       │
                         Commit/PR     │
                            ▼          │
                   ┌─────────────────────────┐
                   │      CI Pipeline        │
                   │  YAML Lint, CSV Check,  │
                   │  Tests, Dry Render      │
                   └───────────┬─────────────┘
                               │  OK?
                               ▼
                     ┌─────────────────┐
                     │   Build System  │
                     │ (Render Engine) │
                     └───────┬─────────┘
                             │
                    Renders All Devices 
                             │
                             ▼
                   ┌────────────────────┐
                   │   build/<host>.cfg │
                   └───────┬────────────┘
                           │   diff
                   ┌──────────────────────┐
                   │  Diff / Drift Engine │
                   └───────┬─────────────┘
                           │
                       Push OK? 
                           │
                           ▼
             ┌────────────────────────────┐
             │ Deployment / Push Pipeline │
             │ (Netmiko, NAPALM, APIs)    │
             └────────────┬──────────────┘
                          │
                          ▼
                 ┌────────────────┐
                 │   Network      │
                 │ (Switches, FW) │
                 └────────────────┘
```

---

# **17.2 End-to-End Workflow Summary**

The full automation pipeline follows **10 steps**:

1. **Engineer updates YAML/CSV data**  
2. **Engineer updates Jinja templates (if needed)**  
3. **Commit → GitHub Pull Request**  
4. **CI runs:**  
   - YAML lint  
   - CSV schema validation  
   - Python unit tests  
   - Jinja dry-run render  
   - whitespace check  
5. **Reviewer approves PR**  
6. **CI merges to develop or main**  
7. **Render.py generates full configs**  
8. **Diff engine compares with running configs**  
9. **If clean, push.py deploys to devices**  
10. **Drift engine checks devices nightly**

This ensures:  
- stability  
- auditability  
- compliance  
- predictability  
- safety  

---

# **17.3 Detailed Blueprint Components**

Deep breakdown of each component in the blueprint.

---

# **17.3.1 Source of Truth (YAML + CSV + JSON)**

### **Purpose**  
Central truth for all device variables.

### **Structure**
```
data/
  devices.yml
  fabric.yml
  vlans.csv
  tenants/
    tenantA.yml
    tenantB.yml
  underlay.csv
  overrides.yml
```

### **Examples**

**devices.yml**
```yaml
devices:
  - hostname: leaf01
    os: nxos
    role: leaf
    mgmt_ip: 172.16.10.11/24
    asn: 65001
    loopbacks:
      lo0: 10.0.0.11/32
      lo1: 10.1.0.11/32
```

**vlans.csv**
```
device,vlan_id,name,vni,ip
leaf01,10,Servers,10100,10.10.10.1/24
leaf02,20,Users,10200,10.10.20.1/24
```

---

# **17.3.2 Template Engine (Jinja2)**

### **Purpose**
Convert SoT data → final configurations.

### **Location**
```
templates/
```

### **Structure**
```
templates/
  nxos/
    device_base.j2
    leaf.j2
    spine.j2
    underlay_intf.j2
    overlay_leaf_evpn.j2
  misc/
    macros.j2
```

### **Macro example**
```jinja2
{{ svi(vlan.id, vlan.name, vlan.ip) }}
```

---

# **17.3.3 Rendering Engine (Python)**

### **Purpose**
Glue logic: data → templates → configs.

### **Key functions**
- load YAML/CSV  
- merge context  
- validate  
- choose template  
- register filters  
- write build files  

### **Commands**
```bash
python scripts/render.py --host leaf01
python scripts/render.py --target devices
```

---

# **17.3.4 Validation Layer**

### **Purpose**
Prevent invalid configurations.

### **Checks**
- required fields  
- IP format  
- VLAN range  
- VNI uniqueness  
- required loopbacks  
- leaf-only VTEP  
- multicast mode rules  

### **Command**
```bash
python scripts/validate.py
```

---

# **17.3.5 Build System (Output Factory)**

### **Folder**
```
build/
  leaf01.cfg
  leaf02.cfg
  spine01.cfg
  firewall01.conf
```

These files are:  
- version-controlled  
- diffed  
- approved  

---

# **17.3.6 Diff Engine (Drift Checker)**

### **Purpose**
Compare *desired state* vs *running state*.

### **Sample diff**
```diff
- switchport access vlan 10
+ switchport access vlan 20
```

### **Commands**
```
python scripts/diff.py --host leaf01
python scripts/diff.py --all
```

---

# **17.3.7 Push Pipeline (Deployment Engine)**

### **Purpose**
Deploy safely using:  
- Netmiko  
- NAPALM  
- Paramiko  
- REST APIs  

### **Commands**
```
python scripts/push.py --host leaf01
python scripts/push.py --dry-run
```

### **Dry-run**
Shows exactly what will change.

---

# **17.3.8 Drift Detection (Nightly Compliance)**

### **Purpose**
Ensure devices remain aligned.

### **Workflow**
1. Pull running configs  
2. Render fresh configs  
3. Diff  
4. Label drift  
5. Notify teams  

### **Reasons for drift**
- manual edits  
- TAC interventions  
- partial rollbacks  
- outages  

---

# **17.3.9 CI/CD Pipeline (Full Automation)**

### **Purpose**
Guarantee quality & consistency.

### **Checks**
1. YAML syntax  
2. CSV schema  
3. Unit tests  
4. Jinja smoke render  
5. Whitespace lint  
6. Template lint  
7. Security scans  

### **Flow**
```
Commit → PR → CI Tests → Review → Merge → Auto Render
```

---

# **17.3.10 Multi-Vendor Strategy**

### **Supported vendors**

**Switches**
- NX-OS  
- EOS  
- Junos  

**Firewalls**
- FortiGate  
- Palo Alto  
- Checkpoint  

**LBs**
- F5  
- HAProxy  

**Cloud**
- AWS  
- Azure  
- GCP  

### **Strategy**
- template folders per vendor  
- shared YAML  
- vendor-specific filters  
- dispatch logic in Python  

---

# **17.4 End-to-End Example (Leaf Switch)**

```
1. Read devices.yml → leaf01
2. Read vlans.csv → VLAN rows
3. Merge → context dictionary
4. Validate context fields
5. Choose template → nxos/leaf.j2
6. Render config
7. Write → build/leaf01.cfg
8. Diff running config
9. Push if approved
10. Save final config in Git
```

---

# **17.5 Example End-to-End Timeline (Real Automation Team)**

```
Day 1:
  - Engineer updates CSV/YAML
  - Opens PR

Day 2:
  - Peer reviews
  - CI validates
  - Merge to develop

Day 3:
  - Render + diff
  - Push to devices

Nightly:
  - Drift engine runs
  - Zero drift → clean network
```

---

# **17.6 Maturity Levels Comparison**

| Level | Name | Description |
|------|------|-------------|
| 0 | Manual | CLI typing |
| 1 | Semi-Automated | Python scripts only |
| 2 | Template-Driven | Jinja2 + SoT |
| 3 | Validated | Validation + diff |
| 4 | CI/CD | PR workflow + pipelines |
| 5 | Autonomous | Drift detection + remediation |

**Level 5 is the target for enterprise automation.**
