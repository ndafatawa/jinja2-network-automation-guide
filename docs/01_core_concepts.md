# **01 – Core Concepts of Jinja2 for Network Automation**

This document explains the essential building blocks used when generating network configuration using **Jinja2** and **Python**.

---

## **1. Jinja2 Template**

A **template** is a plain text file that contains configuration mixed with:

- static text  
- placeholders for values  
- optional logic  

### Example

```jinja2
interface mgmt0
  ip address {{ mgmt_ip }}
```

Templates may contain:

- Variables (`{{ ... }}`)
- Logic blocks (`{% ... %}`)
- Filters (`| ...`)
- Loops
- Conditionals
- Macros
- Includes
- Inheritance

A template does **not** contain device data — only structure.

---

## **2. Context (Data Model)**

The **context** is a Python dictionary passed into the template at render time.  
It provides *all* the values used by the template.

### Example Context

```python
{
  "hostname": "LEAF1",
  "mgmt_ip": "172.16.10.11/24",
  "vlans": [
    {"id": 10, "name": "SERVERS"},
    {"id": 20, "name": "USERS"}
  ]
}
```

Key principles:

- Templates do not store data  
- **Context contains all actual values**  
- Comes from YAML, CSV, JSON, Excel, or direct Python dicts  

---

## **3. Rendering Process**

Rendering = Template + Context + Jinja2 Engine → Final Config

### **Rendering Pipeline**

```
YAML / CSV / JSON / Excel
        ↓
Python loads + validates data
        ↓
Context dictionary
        ↓
Jinja2 renders template
        ↓
Final configuration text (CLI/API)
```

### **Python Example**

```python
output = template.render(context)
```

---

## **4. Data Sources**

Network automation uses structured inputs such as:

### **YAML**
Best for hierarchical layouts: device inventory, fabric settings, overlays.

### **CSV**
Best for large flat tables: VLAN lists, firewall objects, routes.

### **JSON**
API outputs (ACI, NSX-T, Fortinet, etc.)

### **Excel**
Customer migration tables via pandas.

### **Python dictionaries**
After validation, all data becomes a dictionary.

---

## **5. Deterministic Output**

Automated configs must be stable:

- Clean Git diffs  
- Reproducible output  
- No randomness  
- No silent missing values  

Achieved by:

- Sorting lists (`unique | sort | join`)
- Whitespace trimming
- `StrictUndefined` enforcing missing data detection
- Keeping heavy logic in Python, not templates

---

## **6. Recommended Project Structure**

```
project/
│
├── data/
│   ├── devices.yml
│   ├── fabric.yml
│   ├── vlans.csv
│   └── overrides.yml
│
├── templates/
│   ├── nxos/
│   │   ├── device_base.j2
│   │   ├── leaf.j2
│   │   ├── spine.j2
│   │   ├── underlay_intf.j2
│   │   ├── underlay_ospf.j2
│   │   └── overlay_leaf_evpn.j2
│   └── misc/
│       └── macros.j2
│
├── scripts/
│   └── render.py
│
└── build/
    └── <generated configs>
```

---

## **7. Jinja2 Environment Configuration**

Correct Jinja2 setup:

```python
env = Environment(
    loader=FileSystemLoader("templates"),
    trim_blocks=True,
    lstrip_blocks=True,
    undefined=StrictUndefined
)
```

**Meaning**

- `trim_blocks=True` → removes blank lines  
- `lstrip_blocks=True` → removes indentation before `{% %}`  
- `StrictUndefined` → fails loudly on missing values  

---

## **8. Role of Python**

Python handles:

- Loading YAML / CSV / JSON / Excel  
- Normalization and validation  
- Merging datasets  
- Building the final context  
- Selecting templates  
- Registering filters  
- Rendering configs  
- Writing output files  

Templates remain simple; Python handles logic.

---

## **9. Purpose of Jinja2 in Network Automation**

Jinja2 provides:

- Consistent repetitive config  
- Vendor-neutral rendering  
- Template reuse  
- Git-based workflows  
- High-scale deployment (VXLAN EVPN, firewall rules, routing)  

It converts **structured data → deployable network configuration**.

---
