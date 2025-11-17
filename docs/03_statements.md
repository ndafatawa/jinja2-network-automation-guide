# **03 – Jinja2 Statements (Control Flow and Structure)**

This document explains **statements** in Jinja2.  
Statements do **not print values** — instead, they control template behavior.

Where variables print text:

```jinja2
{{ ... }}
```

Statements perform actions:

```jinja2
{% ... %}
```

Statements are used for:

- loops  
- conditions  
- including files  
- inheritance  
- macros  
- whitespace control  

Statements are essential for building large-scale network automation templates.

---

## **3.1 What Are Statements?**

A statement is a control instruction written inside:

```jinja2
{% statement %}
```

### Examples

```jinja2
{% for vlan in vlans %}{% endfor %}
{% if bgp.asn == 65001 %}{% endif %}
{% include 'nxos/ospf.j2' %}
{% extends 'nxos/device_base.j2' %}
{% from 'misc/macros.j2' import p2p %}
```

Statements **do not print text**.  
They control *what* will be printed.

---

## **3.2 Why Network Engineers Need Statements**

Network configurations contain:

- Repeating blocks (interfaces, VLANs, ACLs)
- Optional features (multicast, anycast gateway, BFD)
- Device roles (leaf, spine, border, firewall)
- Nested sections (VRFs → interfaces → protocols)
- Multi-vendor templates

Statements allow you to:

- Loop through lists
- Conditionally print sections
- Insert reusable blocks
- Structure templates cleanly

This is how you scale from **1 device → 100 devices** automatically.

---

## **3.3 The Most Common Jinja2 Statements**

You will use these daily:

1. `for` – loops  
2. `if / elif / else` – conditions  
3. `include` – insert a file  
4. `extends` + `block` – inheritance  
5. `set` – temporary variable  
6. `from … import` – import macros  
7. `filter` blocks – optional but powerful  

Each is explained below.

---

## **3.4 The for Loop Statement**

### Syntax

```jinja2
{% for item in list %}
... use item ...
{% endfor %}
```

### Network Example

```jinja2
{% for v in vlans %}
vlan {{ v.id }}
  name {{ v.name }}
{% endfor %}
```

This prints VLAN configuration for every VLAN.

### Filter inside loop header

```jinja2
{% for v in vlans if v.vrf == 'PROD' %}
vlan {{ v.id }}
  name {{ v.name }}
{% endfor %}
```

Useful when VLANs belong to different VRFs.

---

## **3.5 The if / elif / else Statement**

### Syntax

```jinja2
{% if condition %}
...
{% elif other %}
...
{% else %}
...
{% endif %}
```

### Network Example

```jinja2
{% if fabric.replication == 'multicast' %}
  mcast-group {{ vlan.mcast_group }}
{% else %}
  ingress-replication protocol bgp
{% endif %}
```

This prints different overlay configuration depending on replication mode.

---

## **3.6 Inline if Expression**

Format:

```jinja2
{{ value_if_true if condition else value_if_false }}
```

### Network Examples

Shutdown logic:

```jinja2
shutdown {{ 'shutdown' if intf.admin_down else 'no shutdown' }}
```

FortiGate:

```jinja2
set status {{ 'enable' if obj.enabled else 'disable' }}
```

---

## **3.7 The set Statement (Temporary Variables)**

Used to simplify repeated logic.

### Example

```jinja2
{% set trunk_list = intf.allowed_vlans | unique | sort | join(',') %}
switchport trunk allowed vlan {{ trunk_list }}
```

Keeps templates clean and readable.

---

## **3.8 The include Statement (Insert Another Template)**

Syntax:

```jinja2
{% include 'path/to/template.j2' %}
```

### Network Examples

```jinja2
{% include 'nxos/underlay_intf.j2' %}
{% include 'nxos/underlay_ospf.j2' %}
```

This prevents repetition across templates.

---

## **3.9 The extends and block Statements (Template Inheritance)**

Used for hierarchical templates.

### Base Template (device_base.j2)

```jinja2
hostname {{ hostname }}

{% block underlay %}{% endblock %}
{% block overlay %}{% endblock %}
{% block services %}{% endblock %}
```

### Leaf Template

```jinja2
{% extends 'nxos/device_base.j2' %}

{% block underlay %}
  {% include 'nxos/underlay_intf.j2' %}
  {% include 'nxos/underlay_ospf.j2' %}
{% endblock %}

{% block overlay %}
  {% include 'nxos/overlay_leaf_evpn.j2' %}
{% endblock %}
```

### Spine Template

```jinja2
{% extends 'nxos/device_base.j2' %}

{% block overlay %}
  {% include 'nxos/overlay_spine_rr.j2' %}
{% endblock %}
```

This matches real DC architecture:

**Base → Underlay → Overlay → Services**

---

## **3.10 The from … import Statement (Macros)**

Import macros (reusable config blocks):

```jinja2
{% from 'misc/macros.j2' import p2p %}
```

Use macro:

```jinja2
{{ p2p(intf.name, intf.ip, intf.desc) }}
```

---

## **3.11 The filter Block (wrap entire sections)**

Example:

```jinja2
{% filter upper %}
hostname {{ hostname }}
{% endfilter %}
```

Used for large text transformations.

---

## **3.12 Comments in Templates**

Jinja2 comment:

```jinja2
{# This is a comment #}
```

Does not appear in final config.

---

## **3.13 Combining Statements**

### Example — Print L3VNI only if defined

```jinja2
{% if vrf.l3vni is defined %}
interface nve1
  member vni {{ vrf.l3vni }} associate-vrf
{% endif %}
```

### Example — Only generate anycast SVIs for L2VNIs

```jinja2
{% for v in vlans if v.l2vni %}
interface vlan {{ v.id }}
  fabric forwarding anycast-gateway
{% endfor %}
```

---

## **3.14 Putting It All Together (Real Template)**

```jinja2
{% extends 'nxos/device_base.j2' %}

{% block underlay %}
  {% include 'nxos/underlay_intf.j2' %}
  {% include 'nxos/underlay_ospf.j2' %}
{% endblock %}

{% block overlay %}
interface nve1
  no shutdown
  host-reachability protocol bgp
  source-interface loopback{{ fabric.nve_src_loopback }}

  {% for v in vlans if v.l2vni %}
  member vni {{ v.vni }}
    {% if fabric.replication == 'multicast' %}
    mcast-group {{ v.mcast_group }}
    {% else %}
    ingress-replication protocol bgp
    {% endif %}
  {% endfor %}
{% endblock %}
```

This resembles real VXLAN EVPN automation logic.

---

## **3.15 Best Practices**

- Keep templates simple  
- Move complex logic into Python  
- Use `include` to avoid repetition  
- Use inheritance for structure  
- Use `if is defined` to avoid broken configs  
- Avoid deeply nested statements  
- Keep templates readable and maintainable  

---
