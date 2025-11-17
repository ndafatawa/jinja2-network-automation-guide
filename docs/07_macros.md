# **07 – Jinja2 Macros (Reusable Configuration Blocks)**

Jinja2 **macros** are one of the most powerful features in network automation templates.  
A macro is similar to a function: you define a reusable block of configuration and call it whenever needed.

Macros make templates:

- clean  
- modular  
- reusable  
- consistent  
- easy to maintain  
- vendor-agnostic  

---

## **7.1 What Is a Macro?**

A macro is a reusable block of template code that can accept parameters.

### **Syntax**

```jinja2
{% macro name(param1, param2) %}
  ... body ...
{% endmacro %}
```

### **Calling a macro**

```jinja2
{{ name(arg1, arg2) }}
```

Macros **do not print automatically** — you must call them using `{{ ... }}`.

---

## **7.2 Why Network Engineers Need Macros**

Network engineers use macros to avoid repeating configuration blocks, such as:

- P2P underlay L3 interfaces  
- SVI templates  
- NVE members for VXLAN  
- ACL entries  
- Firewall address objects  
- BGP neighbor sections  
- VRF definitions  
- QoS blocks  
- Reusable service profiles  

Macros ensure:

- consistent formatting  
- less copy/paste  
- reduced errors  
- cleaner templates  
- easy multi-vendor support  

---

## **7.3 Where Macros Are Stored**

Macros are typically stored in:

```
templates/misc/macros.j2
```

This keeps the project structured and easy to navigate.

---

## **7.4 Simple Macro Example**

### **Macro**

```jinja2
{% macro svi(id, name, ip) -%}
interface vlan {{ id }}
  name {{ name }}
  ip address {{ ip }}
  no shutdown
{%- endmacro %}
```

### **Usage**

```jinja2
{{ svi(10, 'Servers', '10.10.10.1/24') }}
```

### **Output**

```
interface vlan 10
  name Servers
  ip address 10.10.10.1/24
  no shutdown
```

---

## **7.5 Macro With Optional Parameters (Default Values)**

```jinja2
{% macro p2p(intf, ip, desc='') -%}
interface {{ intf }}
  description {{ desc }}
  no switchport
  mtu 9216
  ip address {{ ip }}
  no shutdown
{%- endmacro %}
```

Call without description:

```jinja2
{{ p2p('Ethernet1/1', '10.0.0.1/31') }}
```

Call with description:

```jinja2
{{ p2p('Ethernet1/2', '10.0.0.3/31', 'Link to spine-02') }}
```

---

## **7.6 Importing Macros**

Import a macro from a file:

```jinja2
{% from 'misc/macros.j2' import p2p %}
```

Then call it:

```jinja2
{{ p2p(intf.name, intf.ip, intf.description) }}
```

Import multiple macros:

```jinja2
{% from 'misc/macros.j2' import svi, p2p, nve_member %}
```

---

## **7.7 Real-World Examples**

### **7.7.1 Underlay Point-to-Point Interface**

```jinja2
{% macro underlay_intf(intf, ip) -%}
interface {{ intf }}
  no switchport
  mtu 9216
  ip address {{ ip }}
  ip ospf network point-to-point
  no shutdown
{%- endmacro %}
```

Usage:

```jinja2
{{ underlay_intf('Ethernet1/1', '10.0.0.1/31') }}
```

---

### **7.7.2 EVPN NVE Member Block**

```jinja2
{% macro nve_l2vni(vni, mcast_group=None) -%}
  member vni {{ vni }}
    {% if mcast_group is defined %}
    mcast-group {{ mcast_group }}
    {% else %}
    ingress-replication protocol bgp
    {% endif %}
{%- endmacro %}
```

Usage:

```jinja2
{{ nve_l2vni(v.vni, v.mcast_group) }}
```

---

### **7.7.3 FortiGate Address Object**

```jinja2
{% macro fg_addr(name, subnet) -%}
config firewall address
  edit "{{ name }}"
    set subnet {{ subnet | cidr_to_ipmask }}
  next
end
{%- endmacro %}
```

Usage:

```jinja2
{{ fg_addr(obj.name, obj.subnet) }}
```

---

### **7.7.4 VXLAN SVI Anycast Gateway**

```jinja2
{% macro svi_anycast(id, ip) -%}
interface vlan {{ id }}
  ip address {{ ip }}
  fabric forwarding anycast-gateway
  no shutdown
{%- endmacro %}
```

Usage:

```jinja2
{{ svi_anycast(vlan.id, vlan.ip) }}
```

---

## **7.8 Passing Complex Data Structures**

Macros can receive entire objects:

```jinja2
{{ svi(vlan.id, vlan.name, vlan.ip) }}
```

Or full VRFs:

```jinja2
{{ vrf_block(vrf.name, vrf.l3vni, vrf.rt) }}
```

Macros accept lists, dictionaries, nested objects — anything.

---

## **7.9 Combining Macros With Loops**

Example: Generate underlay interfaces:

```jinja2
{% for u in underlay %}
{{ p2p(u.iface, u.ip, u.desc) }}
{% endfor %}
```

Clean and readable.

---

## **7.10 Macro Scoping Rules**

Important behavior:

- Macros **cannot modify** variables outside themselves  
- They see only the parameters passed  
- Macros do **not** inherit template blocks  
- Macros can be stored anywhere and imported  
- Macros behave like pure functions — no side effects  

---

## **7.11 Advanced Macro Usage**

### Return text to a variable

```jinja2
{% set text = p2p('Eth1/1', '10.0.0.1/31') %}
{{ text }}
```

### Macro inside a filter block

```jinja2
{% filter upper %}
{{ p2p('Eth1/2', '10.0.0.3/31') }}
{% endfilter %}
```

---

## **7.12 When to Use Macros vs Includes vs Inheritance**

| Feature      | Use Case |
|--------------|----------|
| **Macro**    | Reusable, parameterized config (SVI, NVE, firewall rules) |
| **Include**  | Paste another file (OSPF block, BGP block) |
| **Inheritance** | Define overall template structure (base → leaf/spine) |

Macros are for **reusable functional blocks**.

---

## **7.13 Best Practices for Macros**

- Store macros in `misc/macros.j2`  
- Keep macros small and focused  
- Use descriptive names  
- Pass all data through parameters  
- Avoid depending on global variables  
- Keep internal logic minimal  
- Prefer tests & filters instead of complex branching  

---

