# **14 – Hands-On Labs for Jinja2 Network Automation**

This chapter contains practical exercises that teach you how to use your automation framework step-by-step.  
Each lab produces real device configuration output.  
These labs should be performed **in order**.

---

# **14.1 Lab 1 — Render Your First Device (Change Hostname)**

## **Goal**
Learn how a Jinja2 template reads values from `devices.yml`.

## **Steps**

### 1. Edit `data/devices.yml`
Change:

```yaml
hostname: LEAF1
```

to:

```yaml
hostname: LEAF1-DEMO
```

### 2. Render only this device
Run:

```bash
python3 render.py --host LEAF1-DEMO
```

### 3. View output
Open:

```
build/LEAF1-DEMO.cfg
```

You should see your hostname printed correctly.

---

# **14.2 Lab 2 — Add Your First VLAN (YAML)**

## **Goal**
Add VLAN data using YAML and confirm that the template renders the VLAN block.

### 1. Add a VLAN inside the device entry
Edit `data/devices.yml`:

```yaml
vlans:
  - id: 10
    name: SERVERS
```

### 2. Render the device

```bash
python3 render.py --host LEAF1
```

### 3. Verify output
You should see:

```
vlan 10
  name SERVERS
```

---

# **14.3 Lab 3 — Add VLANs Using CSV (Device-Independent)**

## **Goal**
Merge VLANs from CSV into device contexts.

### 1. Edit `data/vlans.csv`

```
id,name,vrf
20,USERS,PROD
30,DMZ,PROD
40,APP,GUEST
```

### 2. Render one or all devices

```bash
python3 render.py
```

### 3. Verify VLANs in output

```
vlan 20
vlan 30
vlan 40
```

CSV VLANs should appear on all devices that use VLAN data.

---

# **14.4 Lab 4 — Try Multicast vs. BGP Replication**

## **Goal**
Test conditional logic in overlay templates.

### 1. Change replication mode in `data/fabric.yml`

Multicast:

```yaml
replication: multicast
```

OR BGP:

```yaml
replication: bgp
```

### 2. Render a leaf device
```bash
python3 render.py --host LEAF1
```

### 3. Inspect overlay config

Multicast example:

```
mcast-group 239.1.1.10
```

BGP example:

```
ingress-replication protocol bgp
```

---

# **14.5 Lab 5 — Create and Use a Custom Filter**

## **Goal**
Understand how to extend Jinja2 with Python.

### 1. Add to `render.py`:

```python
def masklen(cidr):
    import ipaddress
    return ipaddress.ip_network(cidr, strict=False).prefixlen

env.filters['masklen'] = masklen
```

### 2. Use in a template (example: in an SVI block)

```jinja2
# mask length = {{ svi.ip | masklen }}
```

### 3. Render device and verify output

---

# **14.6 Lab 6 — Build FortiGate Address Objects from CSV**

## **Goal**
Use CSV + custom filters to generate address objects.

### 1. Edit `data/addr_objects.csv`

```
name,subnet
WEB01,10.10.1.10/32
APP01,10.10.2.10/32
```

### 2. Render:

```bash
python3 render.py --target fortigate-addrobj
```

### 3. Verify output:

```
config firewall address
  edit "WEB01"
    set subnet 10.10.1.10 255.255.255.255
  next
end
```

---

# **14.7 Lab 7 — EOS VLAN Demo (Simple Vendor Template)**

## **Goal**
Learn multi-vendor template handling.

### 1. Render:

```bash
python3 render.py --target eos-leaf-demo
```

### 2. Inspect:

```
build/EOS-LEAF1.cfg
```

You should see sorted VLAN output using:

```jinja2
{{ vlans | sort(attribute='id') }}
```

---

# **14.8 Lab 8 — Using Macros for Underlay P2P Links**

## **Goal**
Learn how macros reduce repetition.

### 1. Edit `templates/misc/macros.j2`

```jinja2
{% macro p2p(intf, ip) -%}
interface {{ intf }}
  no switchport
  mtu 9216
  ip address {{ ip }}
  no shutdown
{%- endmacro %}
```

### 2. Use macro inside `underlay_intf.j2`

```jinja2
{% from 'misc/macros.j2' import p2p %}
{% for u in underlay %}
{{ p2p(u.iface, u.ip) }}
{% endfor %}
```

### 3. Render and verify P2P output.

---

# **14.9 Lab 9 — Test Whitespace Control**

## **Goal**
Understand `-%}` and clean formatting.

### 1. Modify a loop

```jinja2
{% for v in vlans -%}
vlan {{ v.id }}
  name {{ v.name }}
{%- endfor %}
```

### 2. Render the device  
Verify there are **no blank lines** between VLANs.

---

# **14.10 Lab 10 — Add Device-Specific Overrides**

## **Goal**
Understand how per-device data is merged.

### 1. Edit `data/overrides.yml`

```yaml
LEAF1:
  loopbacks:
    lo0: 10.10.10.10/32
```

### 2. Render:

```bash
python3 render.py --host LEAF1
```

Overrides should appear in final config.

---

# **14.11 Lab 11 — Automatic Template Selection**

## **Goal**
Understand how Python chooses templates.

### 1. Add different roles in devices.yml

```yaml
- hostname: SPINE1
  os: nxos
  role: spine
```

### 2. Render:

```bash
python3 render.py --host SPINE1
```

It should use:

```
templates/nxos/spine.j2
```

---

# **14.12 Lab 12 — Generate Full Fabric Configs**

## **Goal**
Render **every device** in the project.

### 1. Run:

```bash
python3 render.py
```

### 2. Inspect build directory:

```
build/
  LEAF1.cfg
  LEAF2.cfg
  SPINE1.cfg
  SPINE2.cfg
```

---

# **14.13 Lab 13 — Validate and Catch Errors**

## **Goal**
Test StrictUndefined behavior.

### 1. Remove a required field from devices.yml

```yaml
mgmt_ip: 
```

OR delete a variable referenced in templates.

### 2. Render:

```bash
python3 render.py --host LEAF1
```

### 3. You should see:

```
UndefinedError: 'mgmt_ip' is undefined
```

This protects against invalid production configs.

---

# **14.14 Lab 14 — Build a Complete VXLAN EVPN Template**

## **Goal**
Combine everything learned.

Your final template uses:

- loops  
- tests  
- filters  
- macros  
- inheritance  
- includes  
- whitespace control  

Render a complete VXLAN fabric and verify:

- underlay P2P links  
- OSPF  
- BGP EVPN  
- NVE1 interface  
- L2VNIs  
- L3VNIs  
- SVI anycast gateways  

This is identical to what real DC automation frameworks do.

---

# **14.15 Best Practice: Render Before Every Git Commit**

Get into the habit:

```bash
python3 render.py
git diff build/
```

Check:

- clean whitespace  
- stable ordering  
- consistent indentation  
- expected changes only  

This is how mature automation engineers maintain **deterministic** output.

---

# **End of Hands-On Labs**
These labs give you the full workflow required for real production automation with Jinja2 and Python.
