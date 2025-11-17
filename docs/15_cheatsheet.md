# **15 – Jinja2 Network Automation Cheatsheet (Compact Reference)**

This is a fast, practical reference guide for writing Jinja2 templates in network automation projects.  
Use it during troubleshooting, template creation, and reviews.

---

# **15.1 Syntax Summary**

### **Variables**
Print values from context:
```jinja2
{{ variable }}
{{ intf.name }}
{{ vlan.id }}
```

### **Statements**
Control flow (do not print):
```jinja2
{% if ... %}
{% for ... %}
{% include ... %}
{% block ... %}
{% endblock %}
```

### **Comments**
```jinja2
{# this is ignored #}
```

---

# **15.2 Loops**

Loop through lists:
```jinja2
{% for v in vlans %}
vlan {{ v.id }}
  name {{ v.name }}
{% endfor %}
```

Filter inside header:
```jinja2
{% for v in vlans if v.vrf == 'PROD' %}
```

Loop index helpers:
```jinja2
loop.index     # 1-based
loop.index0    # 0-based
loop.first
loop.last
```

---

# **15.3 Conditions**

Basic if:
```jinja2
{% if fabric.replication == 'multicast' %}
```

If/elif/else:
```jinja2
{% if A %}
{% elif B %}
{% else %}
{% endif %}
```

Inline if:
```jinja2
shutdown {{ 'shutdown' if intf.admin_down else 'no shutdown' }}
```

---

# **15.4 Tests (Boolean Checks)**

Check if defined:
```jinja2
{% if vrf.l3vni is defined %}
```

Not defined:
```jinja2
{% if intf.description is not defined %}
```

Membership:
```jinja2
{% if vlan.id in allowed_vlans %}
```

Grouping:
```jinja2
{% if loop.index is divisibleby(5) %}
```

Type:
```jinja2
{% if asn is number %}
```

---

# **15.5 Filters**

### **Sorting, joining, formatting**
```jinja2
{{ vlans | map(attribute='id') | unique | sort | join(',') }}
```

### **String filters**
```jinja2
{{ hostname | upper }}
{{ name | replace(' ', '_') }}
```

### **Defaults**
```jinja2
{{ intf.ip | default('0.0.0.0/32') }}
```

### **Casting**
```jinja2
{{ asn | int }}
```

### **Custom filters**
Defined in `render.py`, for example:

```python
env.filters['vni_rt'] = vni_rt
env.filters['cidr_to_ipmask'] = cidr_to_ipmask
```

Use:
```jinja2
route-target import {{ vrf.l3vni | vni_rt(fabric.asn) }} evpn
```

---

# **15.6 Macros (Reusable Blocks)**

Define:
```jinja2
{% macro p2p(intf, ip) -%}
interface {{ intf }}
  no switchport
  ip address {{ ip }}
{%- endmacro %}
```

Use:
```jinja2
{{ p2p('Ethernet1/1', '10.0.0.1/31') }}
```

Import:
```jinja2
{% from 'misc/macros.j2' import p2p %}
```

---

# **15.7 Includes (Insert Partial Templates)**

```jinja2
{% include 'nxos/underlay_intf.j2' %}
{% include 'nxos/overlay_leaf_evpn.j2' %}
```

---

# **15.8 Template Inheritance (Base + Child Templates)**

Base template:
```jinja2
{% block base %}{% endblock %}
{% block underlay %}{% endblock %}
{% block overlay %}{% endblock %}
```

Child template:
```jinja2
{% extends 'nxos/device_base.j2' %}

{% block underlay %}
{% include 'nxos/underlay_intf.j2' %}
{% endblock %}
```

---

# **15.9 Whitespace Control**

Enable in Python:
```python
trim_blocks=True
lstrip_blocks=True
```

Suppress blank lines in loops:
```jinja2
{% for v in vlans -%}
...
{%- endfor %}
```

Clean includes:
```jinja2
{%- include 'file.j2' -%}
```

---

# **15.10 Expressions**

Math:
```jinja2
{{ vlan.id + 10000 }}
```

Comparison:
```jinja2
{% if asn == 65001 %}
```

Boolean logic:
```jinja2
{% if role == 'leaf' and loopbacks.lo1_ip is defined %}
```

Membership:
```jinja2
{% if 'ospf' in features %}
```

String operations:
```jinja2
{{ site ~ '-' ~ hostname }}
```

Length:
```jinja2
{{ vlans | length }}
```

---

# **15.11 Data Modeling (YAML/CSV/Dicts)**

### YAML Hierarchy Example
```yaml
hostname: LEAF1
mgmt_ip: 172.16.10.11/24
vlans:
  - { id: 10, name: SERVERS }
```

### CSV Example
```
id,name,vrf
10,SERVERS,PROD
20,USERS,PROD
```

### Python Context
```python
ctx = {
  "hostname": "LEAF1",
  "vlans": [...],
  "fabric": {...},
}
```

---

# **15.12 Template Selection (Multi-Vendor)**

```python
if dev['os'] == 'nxos':
    return env.get_template('nxos/leaf.j2')
if dev['os'] == 'eos':
    return env.get_template('eos/leaf_vlan_demo.j2')
if dev['os'] == 'fortigate':
    return env.get_template('fortigate/addr_objects.j2')
```

---

# **15.13 Validation Rules (Before Rendering)**

```python
required = ['hostname', 'os', 'role', 'mgmt_ip']
```

Also validate:

- IP format  
- Duplicate VLAN IDs  
- Missing mandatory VNIs  
- VLANs in correct ranges  
- VRF has required fields  

---

# **15.14 Best Practices**

### **Keep templates clean**
Use includes, macros, inheritance.

### **Keep logic in Python**
Templates = presentation, Python = logic.

### **Sort and deduplicate lists**
Always use:
```jinja2
unique | sort
```

### **Use StrictUndefined**
Never allow missing values to silently render.

### **Test on multiple devices**
Catch edge cases early.

### **Always inspect Git diffs**
Ensure deterministic output.

---

# **15.15 Typical Patterns You Will Use Daily**

### VLAN-to-VNI mapping
```jinja2
vn-segment {{ vlan.id + 10000 }}
```

### Trunk formatting
```jinja2
{{ intf.allowed | unique | sort | join(',') }}
```

### BGP neighbors
```jinja2
{% for n in bgp.neighbors %}
neighbor {{ n.ip }} remote-as {{ n.asn }}
{% endfor %}
```

### NVE members
```jinja2
{% for v in vlans if v.l2vni %}
member vni {{ v.vni }}
{% endfor %}
```

### SVI anycast gateway
```jinja2
fabric forwarding anycast-gateway
```

---

# **15.16 Final Advice**

This cheat sheet is for **daily use**.  
When writing templates:

- Start simple  
- Use includes for structure  
- Use macros for repeated blocks  
- Use filters to clean data  
- Validate all inputs  
- Render early, render often  
- Watch whitespace closely  

With these patterns, you can generate:
- NX-OS VXLAN EVPN fabrics  
- EOS L2/L3 configurations  
- FortiGate address objects  
- Junos routing policies  
- Palo Alto rules  
- Multi-vendor DC topologies  

This is the foundation of **expert-level network automation**.
