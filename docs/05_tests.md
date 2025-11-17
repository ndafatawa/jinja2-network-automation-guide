# **05 – Jinja2 Tests (Boolean Checks for Conditional Logic)**

Jinja2 **tests** are yes/no checks used inside statements.  
They determine *when* a configuration block should be printed.

Tests are essential for network automation because devices often require:

- optional sections  
- conditional features  
- different behavior per device role  
- checks for missing or undefined values  
- structured output (spacing/grouping)  

Tests return **True or False** and are used only inside:

```jinja2
{% ... %}
```

---

## **5.1 What Is a Test?**

A test evaluates a property of a value and returns boolean.

### Syntax

```jinja2
{% if variable is testname %}
```

With arguments:

```jinja2
{% if variable is testname(arg1, arg2) %}
```

Tests **do not print text** — they control logic flow.

---

## **5.2 Why Network Engineers Need Tests**

Network configs require decision logic:

- only configure loopbacks if defined  
- print multicast settings only if replication is multicast  
- print trunk settings only if interface is trunk  
- apply RR-client only on leafs  
- create spacing every N VLANs  

Tests allow templates to make decisions **without** becoming complex.

---

## **5.3 The Most Important Jinja2 Tests**

These are used constantly:

- `is defined` — does variable exist?  
- `is not defined` — missing variable  
- `is none` / `is not none` — null value  
- `is iterable` — can be looped?  
- `is divisibleby(n)` — spacing/grouping output  
- `is string`, `is number` — type checks  

Examples follow.

---

## **5.4 Test: `is defined`**

Prevents errors when using optional values.

```jinja2
{% if loopbacks.lo1_ip is defined %}
interface loopback{{ fabric.nve_source_loopback }}
  ip address {{ loopbacks.lo1_ip }}/32
{% endif %}
```

If `lo1_ip` does not exist, nothing prints — no crash.  
Critical when spines/leaves have different data models.

---

## **5.5 Test: `is not defined`**

Used for fallback defaults.

```jinja2
{% if interface.description is not defined %}
  description DEFAULT-DESCRIPTION
{% endif %}
```

Ensures every interface has a description.

---

## **5.6 Test: `is iterable`**

Check if something can be looped.

```jinja2
{% if vlan_list is iterable %}
  switchport trunk allowed vlan {{ vlan_list | join(',') }}
{% endif %}
```

Prevents errors if someone puts a single VLAN value instead of a list.

---

## **5.7 Test: `is divisibleby(n)`**

Great for structured output.

### Example — spacing every 5 VLANs

```jinja2
{% for vlan in vlans %}
vlan {{ vlan.id }}
  name {{ vlan.name }}

{% if loop.index is divisibleby(5) %}
! ----- spacing -----
{% endif %}

{% endfor %}
```

Useful in very large configurations.

---

## **5.8 Type Tests: `is number`, `is string`, etc.**

```jinja2
{% if bgp.asn is number %}
router bgp {{ bgp.asn }}
{% endif %}

{% if hostname is string %}
hostname {{ hostname | upper }}
{% endif %}
```

---

## **5.9 Combining Tests With Conditions**

Example:

```jinja2
{% if fabric.replication == 'multicast' and vlan.mcast_group is defined %}
  mcast-group {{ vlan.mcast_group }}
{% else %}
  ingress-replication protocol bgp
{% endif %}
```

Allows rich conditional behavior.

---

## **5.10 Real-World Examples**

### **1. Configure SVI only if IP exists**

```jinja2
{% for v in vlans %}
{% if v.ip is defined %}
interface vlan {{ v.id }}
  ip address {{ v.ip }}
{% endif %}
{% endfor %}
```

---

### **2. Configure L3VNI only when defined**

```jinja2
{% if vrf.l3vni is defined %}
interface nve1
  member vni {{ vrf.l3vni }} associate-vrf
{% endif %}
```

Protects VRFs that are L2-only.

---

### **3. RR-Client only for leaf devices**

```jinja2
{% if role == 'leaf' %}
  route-reflector-client
{% endif %}
```

---

### **4. Optional interface descriptions**

```jinja2
interface {{ intf.name }}
{% if intf.description is defined %}
  description {{ intf.description }}
{% endif %}
```

---

### **5. Only print VLANs that belong to a VRF**

```jinja2
{% for v in vlans if v.vrf is defined %}
vlan {{ v.id }}
  name {{ v.name }}
{% endfor %}
```

Filtering directly in the loop header is a Jinja feature.

---

## **5.11 Edge Case: `defined` vs `none`**

They are different concepts.

### **undefined** → the variable does not exist  
Example: `v.ip` was never defined.

### **none** → the variable exists but is null  
Example: `ip: null` in YAML.

Check undefined:

```jinja2
{% if vrf.rd is defined %}
```

Check not-none:

```jinja2
{% if vrf.rt is not none %}
```

Both matter in data modeling.

---

## **5.12 Practical Use Case: Optional Underlay Interfaces**

**YAML**

```yaml
underlay_interfaces:
  - { name: Ethernet1/1, ip: 10.0.0.1/31 }
  - { name: Ethernet1/2 }
```

**Template**

```jinja2
interface {{ underlay.name }}
{% if underlay.ip is defined %}
  ip address {{ underlay.ip }}
{% else %}
  no ip address
{% endif %}
```

---

## **5.13 Best Practices for Using Tests**

- Always use `is defined` for optional fields  
- Use tests for logic—not empty strings  
- Keep conditions simple  
- Move complex decisions to Python  
- Avoid nested `if` blocks  
- Use tests to prevent generating invalid vendor configs  

---

