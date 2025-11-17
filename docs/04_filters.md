# **04 – Jinja2 Filters (Transforming Data Before Printing)**

Jinja2 **filters** allow you to modify, clean, sort, format, or transform data *before* it is printed in the final configuration.  
Filters are one of the most powerful features in network automation templates.

---

## **4.1 What Is a Filter?**

A filter takes a value and transforms it into another value.

### Syntax

```jinja2
{{ value | filter_name }}
```

With arguments:

```jinja2
{{ value | filter_name(arg1, arg2) }}
```

Filters clean and normalize data flowing from **YAML → Python → Jinja2 → final config**.

---

## **4.2 Why Network Engineers Use Filters**

Filters are used daily to:

- generate deterministic (sorted) VLAN lists  
- join lists into comma-separated strings  
- convert CIDR → IP + subnet mask  
- sanitize names (uppercase, replace spaces)  
- remove duplicates from CSV data  
- cast values to integers for routing features  
- build EVPN Route-Targets from VNIs  

Filters reduce complexity and improve the consistency of generated configs.

---

## **4.3 Default Filters (Most Useful for Networking)**

Below are the default Jinja2 filters heavily used in network automation.

---

### **4.3.1 `join`**

Convert a list → comma-separated string.

**YAML**

```yaml
vlans: [10, 20, 30]
```

**Template**

```jinja2
switchport trunk allowed vlan {{ vlans | join(',') }}
```

**Output**

```
switchport trunk allowed vlan 10,20,30
```

---

### **4.3.2 `sort`**

Sort a list numerically or alphabetically.

```jinja2
{% for v in vlans | sort(attribute='id') %}
vlan {{ v.id }}
{% endfor %}
```

Ensures consistent output across devices.

---

### **4.3.3 `unique`**

Remove duplicates.

```jinja2
{{ vlans | unique | sort | join(',') }}
```

---

### **4.3.4 `upper` / `lower`**

Normalize names.

```jinja2
hostname {{ hostname | upper }}
```

**Output**

```
hostname LEAF01
```

---

### **4.3.5 `replace`**

Replace characters.

```jinja2
{{ vrf_name | replace('-', '_') }}
```

Great for vendors that disallow spaces or hyphens.

---

### **4.3.6 `default(value)`**

Fallback value when variable is undefined.

```jinja2
ip address {{ intf.ip | default("0.0.0.0/32") }}
```

Useful for optional interface IPs.

---

### **4.3.7 `int`, `float`**

Cast strings to numbers.

```jinja2
router bgp {{ asn | int }}
```

Used for:

- BGP ASN  
- OSPF priorities  
- timers  

---

## **4.4 Map + Attribute + Filters (EXTREMELY Important)**

The combination of **map → attribute → list/unique/sort → join** is used constantly.

**YAML**

```yaml
vlans:
  - { id: 10, name: Servers }
  - { id: 20, name: Users }
```

Extract only VLAN IDs:

```jinja2
{{ vlans | map(attribute='id') | list }}
```

Result:

```
[10, 20]
```

Full trunk example:

```jinja2
switchport trunk allowed vlan {{ vlans | map(attribute='id') | unique | sort | join(',') }}
```

---

## **4.5 Custom Filters (Created in Python)**

Large network automation projects rely on custom filters.

Custom filters are defined in `render.py`.

### Example: EVPN Route-Target generator

```python
def vni_rt(vni: int, asn: int):
    return f"{asn}:{int(vni)}"
```

### Convert CIDR → IP + Mask

```python
def cidr_to_ipmask(cidr: str):
    import ipaddress
    ip = ipaddress.ip_interface(cidr)
    return f"{ip.ip} {ip.network.netmask}"
```

### Sanitize names (uppercase + underscores)

```python
def safe_name(s: str):
    return s.upper().replace(" ", "_").replace("-", "_")
```

### Register filters

```python
env.filters['vni_rt'] = vni_rt
env.filters['cidr_to_ipmask'] = cidr_to_ipmask
env.filters['safe_name'] = safe_name
```

---

## **4.6 Network Examples Using Custom Filters**

### **4.6.1 EVPN Route-Target from VNI**

**Template**

```jinja2
route-target import {{ vrf.l3vni | vni_rt(fabric.asn) }} evpn
```

**Data**

```yaml
vrf:
  l3vni: 10001
fabric:
  asn: 65000
```

**Output**

```
route-target import 65000:10001 evpn
```

---

### **4.6.2 FortiGate Subnet Conversion**

**Template**

```jinja2
set subnet {{ obj.subnet | cidr_to_ipmask }}
```

**Input**

```
10.10.10.1/32
```

**Output**

```
set subnet 10.10.10.1 255.255.255.255
```

---

### **4.6.3 Sanitize Names**

**Template**

```jinja2
vlan {{ v.id }}
  name {{ v.name | safe_name }}
```

**Data**

```
Prod-Web Servers
```

**Output**

```
name PROD_WEB_SERVERS
```

---

## **4.7 Real Example: Trunk Allowed VLANs**

**YAML**

```yaml
interfaces:
  - name: Ethernet1/1
    mode: trunk
    allowed_vlans: [20, 10, 10, 30]
```

**Template**

```jinja2
{% set vl = intf.allowed_vlans | unique | sort | join(',') %}
switchport trunk allowed vlan {{ vl }}
```

**Output**

```
switchport trunk allowed vlan 10,20,30
```

---

## **4.8 Filters Combined With Loops**

Example:

```jinja2
{% for addr in addresses | unique | sort %}
set allowed-address {{ addr }}
{% endfor %}
```

Used for:

- prefix-lists  
- firewall address lists  
- route-maps  
- service objects  

---

## **4.9 Filter Blocks**

Transform entire blocks:

```jinja2
{% filter upper %}
hostname {{ hostname }}
{% endfilter %}
```

Output block becomes UPPERCASE.

Rarely used — but useful for normalizing vendor syntax.

---

## **4.10 Best Practices for Filters**

- Always sort lists before joining  
- Always `unique` when reading CSV/Excel  
- Keep heavy logic in Python  
- Register custom filters once  
- Use filters for *formatting*, not *validation*  
- Avoid ultra-long filter chains inside templates  
- Keep templates readable  

---

