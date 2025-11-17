# **08 – Includes and Template Inheritance in Jinja2**

This document explains two core Jinja2 features used to build scalable, modular, production-grade network automation templates:

- **Includes**
- **Template inheritance**

These two tools allow you to break massive configuration templates into clean, reusable, maintainable building blocks — essential for large network automation projects such as:

- VXLAN EVPN data-center fabrics  
- Multi-vendor core/edge networks  
- Firewall object and policy generation  
- Multi-site deployments  
- Large L2/L3 underlay/overlay designs  

---

## **8.1 Why This Matters in Network Automation**

In real production environments:

- All switches share **common base config**
- Leaves share **underlay + overlay VXLAN EVPN**
- Spines share **RR + underlay**
- Firewalls share **address-object + policy templates**
- Routers share **WAN templates**

Writing one huge file is not scalable and cannot be reused.

**Includes + Inheritance** give you:

- clean structure  
- reusable building blocks  
- easy maintenance  
- less duplication  
- multi-vendor support  
- templates that scale to 200+ devices  

---

## **8.2 Includes — “paste another template here”**

Includes *insert another file* into the current template.

### **Syntax**

```jinja2
{% include 'path/to/template.j2' %}
```

This is exactly like saying:

> “Paste the generated output of this small template at this location.”

---

## **8.3 Typical Use Cases for Includes**

### **1. Common base configuration**

```jinja2
{% include 'nxos/base_common.j2' %}
```

Contains vendor baseline:

```
feature interface-vlan
feature ospf
no ip domain-lookup
logging server ...
```

---

### **2. Underlay interfaces**

```jinja2
{% include 'nxos/underlay_intf.j2' %}
```

---

### **3. Underlay OSPF**

```jinja2
{% include 'nxos/underlay_ospf.j2' %}
```

---

### **4. VXLAN/EVPN overlay**

```jinja2
{% include 'nxos/overlay_leaf_evpn.j2' %}
```

---

### **5. Vendor-specific logic**

```jinja2
{% if os == 'eos' %}
{% include 'eos/vlan_template.j2' %}
{% endif %}
```

---

## **8.4 Template Inheritance — “skeleton + replaceable blocks”**

Inheritance is the most powerful Jinja2 structuring technique.

It lets you:

- create a **base template**
- define named **blocks**
- create **child templates** that override those blocks

This is how big automation projects stay clean and maintainable.

---

## **8.5 Base Template Example (device_base.j2)**

```jinja2
hostname {{ hostname }}

{% block base %}
{# baseline config goes here #}
{% endblock %}

{% block underlay %}
{# interface + OSPF #}
{% endblock %}

{% block overlay %}
{# VXLAN EVPN #}
{% endblock %}

{% block services %}
{# SNMP, NTP, AAA, syslog #}
{% endblock %}
```

This file defines the **layout** of all device configs.

---

## **8.6 Child Template Example (leaf.j2)**

```jinja2
{% extends 'nxos/device_base.j2' %}

{% block base %}
  {% include 'nxos/base_common.j2' %}
{% endblock %}

{% block underlay %}
  {% include 'nxos/underlay_intf.j2' %}
  {% include 'nxos/underlay_ospf.j2' %}
{% endblock %}

{% block overlay %}
  {% include 'nxos/overlay_leaf_evpn.j2' %}
{% endblock %}
```

This produces:

- the same base skeleton  
- underlay + overlay inserted automatically  
- leaf-specific logic  

---

## **8.7 Why Use Inheritance Instead of Only Includes?**

### **Includes only → messy**

Each device type manually includes 5–10 templates.  
Harder to maintain.

### **Inheritance → clean**

Base defines the structure:

```
base
underlay
overlay
services
```

Each device type just fills in blocks.

This scales to:

- hundreds of devices  
- multiple vendors  
- years of maintenance  

---

## **8.8 Template Selection in Python (render.py)**

```python
if dev["role"] == "leaf":
    template = "nxos/leaf.j2"
else:
    template = "nxos/spine.j2"
```

This produces:

- **leaf.j2 → full underlay + overlay**
- **spine.j2 → underlay + RR**
- **border_leaf.j2 → adds firewall or L3 handoff**
- **edge.j2 → WAN/MPLS templates**

Automatic and scalable.

---

## **8.9 Nested Includes**

Includes can contain includes:

```
leaf.j2
 ├── base_common.j2
 ├── underlay_intf.j2
 ├── underlay_ospf.j2
 └── overlay_leaf_evpn.j2
      └── macros.j2
```

This keeps the entire repo modular and readable.

---

## **8.10 Include vs Macro vs Inheritance (Comparison)**

| Feature | Purpose | Best Use Case |
|--------|----------|----------------|
| **Include** | Paste another template | OSPF block, BGP block, base config |
| **Macro** | Reusable config function | SVI, P2P links, NVE members, FG objects |
| **Inheritance** | Global structure | Base → leaf/spine/border templates |

All three work together.

---

## **8.11 Real Example: How an NX-OS Leaf Config Is Built**

**device_base.j2**
- defines skeleton

**leaf.j2**
- extends skeleton  
- adds underlay + overlay

**base_common.j2**
- features, mgmt, system defaults

**underlay_intf.j2**
- Ethernet interfaces, IPs

**underlay_ospf.j2**
- OSPF Underlay

**overlay_leaf_evpn.j2**
- VXLAN NVE, VNIs, Anycast GW

### Final result:

```
hostname LEAF1

! BASE
feature interface-vlan
feature ospf
...

! UNDERLAY
interface e1/1
  ip address 10.1.1.0/31
interface e1/2
  ip address 10.1.1.2/31
router ospf UNDERLAY
  router-id 10.10.10.1

! OVERLAY
interface nve1
  host-reachability protocol bgp
  source-interface loopback1
  member vni 10100
...
```

Leaves, spines, borders all share the **same skeleton**.

---

## **8.12 Best Practices for Includes & Inheritance**

- Use **inheritance** for overall layout (base → leaf/spine)
- Use **include** for reusable blocks (OSPF, NVE, base config)
- Use **macros** for parameterized reusable sections (SVIs, P2P)
- Keep templates small and focused
- Push logic to Python — keep templates readable
- Use `StrictUndefined` to prevent missing values
- Store vendor-specific templates in folders:  
  `nxos/`, `eos/`, `fortigate/`, `junos/`

---

