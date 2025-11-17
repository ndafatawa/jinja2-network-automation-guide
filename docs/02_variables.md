# **02 – Variables in Jinja2**

This section explains how variables work inside Jinja2 templates and how they connect your structured data (YAML/CSV/JSON/Python dicts) to dynamically generated network configuration.

---

## **2.1 What Is a Variable?**

A **variable** is a placeholder inside a template.  
It represents a value coming from your data model.

### **Template**

```jinja2
hostname {{ hostname }}
```

### **Data**

```yaml
hostname: leaf01
```

### **Rendered Output**

```
hostname leaf01
```

Variables make templates reusable across many devices.

---

## **2.2 How to Write Variables in Templates**

### **Syntax**

```jinja2
{{ variable_name }}
```

Everything inside `{{ ... }}` is evaluated and printed.

---

## **2.3 Variables Come From the Context**

### Python Context

```python
template.render(
    hostname="leaf01",
    mgmt_ip="172.16.10.10",
    vlans=[{"id": 10, "name": "Servers"}]
)
```

### Template Example

```jinja2
hostname {{ hostname }}
ip address {{ mgmt_ip }}
```

---

## **2.4 Dot Notation vs Bracket Notation**

### **Dot Notation**

```jinja2
{{ vlan.id }}
{{ device.hostname }}
{{ interface.description }}
```

### **Bracket Notation**

```jinja2
{{ vlan['id'] }}
{{ device['hostname'] }}
{{ interface['description'] }}
```

Both work — but dot notation is cleaner.

---

## **2.5 How Dot Notation Works**

Expression:

```jinja2
{{ vlan.id }}
```

Jinja checks in this order:

1. Does object have attribute `id`?  
2. If not, does object have dictionary key `"id"`?

For YAML → Python dicts, Jinja resolves dictionary keys automatically.

---

## **2.6 How Bracket Notation Works**

Bracket notation explicitly refers to a dictionary key:

```jinja2
{{ vlan['id'] }}
```

Use this when the key contains symbols (rare).

---

## **2.7 Recommended Style**

Use **dot notation** everywhere.

Example:

```jinja2
switchport access vlan {{ interface.vlan }}
```

And keep YAML objects as dictionaries.

---

## **2.8 Examples of Variables in Network Templates**

### **VLAN Example**

**YAML**

```yaml
vlans:
  - id: 10
    name: Servers
```

**Template**

```jinja2
vlan {{ vlan.id }}
  name {{ vlan.name }}
```

**Output**

```
vlan 10
  name Servers
```

---

### **Interface Example**

**YAML**

```yaml
interfaces:
  - name: Ethernet1/1
    mode: access
    vlan: 10
```

**Template**

```jinja2
interface {{ intf.name }}
  switchport mode {{ intf.mode }}
  switchport access vlan {{ intf.vlan }}
```

---

### **BGP Example**

**YAML**

```yaml
bgp:
  asn: 65001
  router_id: 10.1.1.1
```

**Template**

```jinja2
router bgp {{ bgp.asn }}
  router-id {{ bgp.router_id }}
```

---

## **2.9 Nested Variables**

**YAML**

```yaml
device:
  hostname: leaf01
  loopbacks:
    lo0: 10.1.1.1/32
    lo1: 10.1.2.1/32
```

**Template**

```jinja2
hostname {{ device.hostname }}

interface loopback0
  ip address {{ device.loopbacks.lo0 }}
```

---

## **2.10 Missing Variables and StrictUndefined**

### **Default Jinja behavior (dangerous)**

```jinja2
hostname {{ hostname }}
```

If `hostname` is missing → output becomes:

```
hostname 
```

This is extremely risky for network configs.

### **Correct behavior**

This project uses:

```python
undefined = StrictUndefined
```

Which produces an error:

```
UndefinedError: 'hostname' is undefined
```

This prevents silent failures.

---

## **2.11 Variable Transformations (Filters)**

Examples:

```jinja2
{{ hostname | upper }}
{{ vlan_list | join(',') }}
{{ vrf.asn | int }}
```

(See **04_filters.md** for full details.)

---

## **2.12 Common Variable Patterns in Network Templates**

### Hostname

```jinja2
hostname {{ hostname }}
```

### Interface

```jinja2
interface {{ intf.name }}
description {{ intf.description }}
```

### SVI

```jinja2
ip address {{ svi.ip }}
```

### VLAN

```jinja2
switchport access vlan {{ intf.vlan }}
```

---

## **2.13 Best Practices**

- Use lowercase variable names  
- Keep all YAML structured consistently  
- Avoid deep nested objects  
- Validate required variables in Python  
- Use `StrictUndefined` to catch missing data immediately  

---
