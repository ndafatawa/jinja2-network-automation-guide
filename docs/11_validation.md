
# **11 – Data Validation in Jinja2 Network Automation**

Validation ensures that all data used for rendering configuration is complete, correct, and safe.  
Without strong validation, templates can render broken or incomplete configs that may cause outages.

In real network automation, **validation is as important as the template itself**.

This chapter explains how to validate data before rendering configurations.

---

# **11.1 Why Validation Matters**

Networks break when data is wrong.

Common problems caused by missing or invalid data:

- Missing VLAN IDs  
- Invalid IP addresses  
- Wrong OSPF area formats  
- Incorrect VRF names  
- Missing BGP ASNs  
- Inconsistent VLAN/VNI mappings  
- Duplicate VLANs on the same device  

Validation prevents:

- bad configs
- silent template failures
- deployment outages
- hard-to-debug issues
- inconsistent configurations between devices

A validated data model = reliable configurations.

---

# **11.2 Where Validation Happens**

Validation occurs **before** Jinja2 renders anything.

Typical validation flow:

```
YAML / CSV / JSON / Excel  
→ Python loader  
→ Validation checks  
→ Build final context dictionary  
→ Render Jinja2 template  
→ Write final config
```

Jinja2 templates should not do heavy validation.  
Python should.

---

# **11.3 Validation Examples from Real Projects**

Most automation frameworks validate:

- required fields  
- data types  
- IP address formats  
- duplicates  
- relationships (e.g., VNI ↔ VLAN ↔ VRF)  
- missing blocks  
- allowed values  

Below are examples you will use in real deployments.

---

# **11.4 Required Fields Validation**

Devices MUST have:

- hostname  
- role  
- os (nxos, eos, fortigate, etc.)  
- mgmt_ip  
- loopbacks  
- BGP ASN (if needed)  

Python example:

```python
required = ["hostname", "role", "os", "mgmt_ip"]
for field in required:
    if field not in dev:
        raise ValueError(f"Missing required field: {field} in device {dev}")
```

---

# **11.5 IP Address Validation**

Python provides built-in validation using `ipaddress`:

```python
import ipaddress

try:
    ipaddress.ip_interface(dev["mgmt_ip"])
except:
    raise ValueError(f"Invalid mgmt_ip for {dev['hostname']}")
```

This catches:

- non-CIDR IPs  
- typos  
- invalid masks  
- missing addresses  

---

# **11.6 Duplicate VLAN Validation**

Networks often break because of duplicated VLAN entries.

Python:

```python
vlan_ids = [v["id"] for v in dev["vlans"]]
if len(vlan_ids) != len(set(vlan_ids)):
    raise ValueError(f"Duplicate VLAN IDs on {dev['hostname']}")
```

This ensures:

- no repeated VLAN IDs  
- deterministic trunk lists  
- consistent VLAN → VNI mappings  

---

# **11.7 VNI Validation**

L2VNIs and L3VNIs must be unique.

Example:

```python
vnis = [v["vni"] for v in dev["vlans"] if "vni" in v]
if len(vnis) != len(set(vnis)):
    raise ValueError(f"Duplicate VNI values detected on {dev['hostname']}")
```

---

# **11.8 VRF Validation**

Each VRF must have:

- name  
- rd  
- route-target definitions  
- valid VNI (for L3 VRFs)  

Example:

```python
if "vrfs" in dev:
    for vrf in dev["vrfs"]:
        if "name" not in vrf or "vni" not in vrf:
            raise ValueError(f"Invalid VRF definition on {dev['hostname']}")
```

---

# **11.9 Optional Field Validation (is defined)**

In Jinja2:

```jinja2
{% if vrf.l3vni is defined %}
...
{% endif %}
```

But Python should detect when optional fields are missing so that templates don’t break.

Example:

```python
if "l3vni" in vrf and vrf["l3vni"] is None:
    raise ValueError("VRF l3vni defined but empty")
```

---

# **11.10 Conditional Validation (Based on Device Role)**

Spines must NOT have:

- VLANs  
- SVIs  
- L2VNIs  

Leaves MUST have:

- L2VNIs  
- loopback1 (VTEP)  

Example:

```python
if dev["role"] == "spine" and "vlans" in dev:
    raise ValueError("Spines must not have VLANs")
```

---

# **11.11 CSV Validation (Common Problems)**

CSV input often contains:

- empty lines  
- duplicate entries  
- accidental spaces  
- incorrect types  

Worst case: breaks templating silently.

Validate CSV:

```python
row["vlan"] = int(row["vlan"])
row["name"] = row["name"].strip()
```

Remove duplicates:

```python
unique_rows = {row["vlan"]: row for row in rows}.values()
```

---

# **11.12 Cross-File Validation**

Your automation must check relationships:

1. VLAN in CSV but not in YAML  
2. VRF references VLAN that doesn’t exist  
3. L3VNI defined but VNI missing  
4. BGP neighbors referencing unknown loopbacks  

Example:

```python
if v["id"] not in vlan_table:
    raise ValueError(f"VLAN {v['id']} referenced but not defined")
```

This prevents broken EVPN configs.

---

# **11.13 StrictUndefined (Template Validation Layer)**

In Jinja2 environment:

```python
undefined=StrictUndefined
```

This makes missing variables throw errors like:

```
UndefinedError: 'vlan_name' is undefined
```

Prevents:

- empty route-targets  
- missing interface names  
- partial configs  
- silent failure  

This is essential for production automation.

---

# **11.14 Real Validation Example (VXLAN Fabric)**

Your automation should validate:

- All VLANs have VNIs  
- All VNIs are unique  
- Every VRF has an L3VNI  
- Loopback0 exists (router ID)  
- Loopback1 exists (VTEP)  
- Spine neighbors exist  
- IP addresses are valid  
- BGP ASN consistent across fabric  

Otherwise, rendered configs will break the fabric.

---

# **11.15 Best Practices for Validation**

- Validate early (Python), not in templates.
- Reject missing values using StrictUndefined.
- Fail fast — stop rendering on invalid input.
- Validate cross-references (VLAN ↔ VRF ↔ VNI).
- Test with multiple devices to ensure consistency.
- Keep validation separate from templating logic.
- Validate CSV inputs aggressively.

A validated data model =  
**clean, predictable, safe, production-ready configuration generation.**

