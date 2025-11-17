# **06 – Jinja2 Loops (Iterating Over Lists in Network Templates)**

Loops are one of the most important features in Jinja2.  
Almost every network configuration contains repeated blocks: VLANs, interfaces, VRFs, BGP neighbors, firewall objects, etc.  
Loops allow these sections to be generated dynamically from structured data.

---

## **6.1 What Is a Loop?**

A loop repeats a block of configuration for each item in a list.

### Syntax

```jinja2
{% for item in list %}
  ... do something with item ...
{% endfor %}
```

Loops generate scalable dynamic configuration.

---

## **6.2 Why Network Engineers Use Loops**

Network configs contain repeating structures:

- VLAN definitions  
- SVI interfaces  
- EVPN VNIs  
- VRF definitions  
- BGP neighbors  
- Underlay links  
- Trunk VLAN lists  
- Firewall address objects  

Without loops: **copy/paste hell**.

With loops: **clean, scalable templates**.

---

## **6.3 Basic Loop Example (VLAN List)**

### **YAML**

```yaml
vlans:
  - { id: 10, name: Servers }
  - { id: 20, name: Users }
  - { id: 30, name: DMZ }
```

### **Template**

```jinja2
{% for v in vlans %}
vlan {{ v.id }}
  name {{ v.name }}
{% endfor %}
```

### **Output**

```
vlan 10
  name Servers
vlan 20
  name Users
vlan 30
  name DMZ
```

---

## **6.4 Loop With Nested Values**

### **YAML**

```yaml
interfaces:
  - name: Ethernet1/1
    mode: access
    vlan: 10
  - name: Ethernet1/2
    mode: trunk
    allowed: [10,20,30]
```

### **Template**

```jinja2
{% for intf in interfaces %}
interface {{ intf.name }}
  switchport mode {{ intf.mode }}

  {% if intf.mode == 'access' %}
  switchport access vlan {{ intf.vlan }}
  {% else %}
  switchport trunk allowed vlan {{ intf.allowed | join(',') }}
  {% endif %}
{% endfor %}
```

---

## **6.5 Filtering Inside Loop Header**

Filter items directly in the loop statement.

### VLANs for a single VRF

```jinja2
{% for v in vlans if v.vrf == 'PROD' %}
vlan {{ v.id }}
  name {{ v.name }}
{% endfor %}
```

### Only L3VNI VLANs

```jinja2
{% for v in vlans if v.l3vni %}
...
{% endfor %}
```

More readable than using an internal `if` block.

---

## **6.6 Loop Index (Very Useful)**

Jinja2 exposes loop metadata:

- `loop.index` → starts at 1  
- `loop.index0` → starts at 0  
- `loop.first` → True for first item  
- `loop.last` → True for last item  

### Example

```jinja2
{% for v in vlans %}
! VLAN number {{ loop.index }}
vlan {{ v.id }}
{% endfor %}
```

---

## **6.7 Grouping Output Using `divisibleby`**

Used for formatting readable output.

### Example — spacing every 5 VLANs

```jinja2
{% for v in vlans %}
vlan {{ v.id }}
  name {{ v.name }}

{% if loop.index is divisibleby(5) %}
! ----- spacing -----
{% endif %}

{% endfor %}
```

Used for:

- prefix-lists  
- firewall objects  
- route-maps  
- VLAN groups  

---

## **6.8 Nested Loops**

Loops inside loops.

### **YAML**

```yaml
vrfs:
  - name: PROD
    vlans: [10, 20]
  - name: GUEST
    vlans: [30]
```

### **Template**

```jinja2
{% for vrf in vrfs %}
vrf context {{ vrf.name }}

{% for v in vrf.vlans %}
  vlan {{ v }}
{% endfor %}

{% endfor %}
```

---

## **6.9 Looping Over Dictionaries**

YAML may contain dictionaries:

```yaml
loopbacks:
  lo0: 10.1.1.1/32
  lo1: 10.1.2.1/32
```

### Template

```jinja2
{% for name, ip in loopbacks.items() %}
interface {{ name }}
  ip address {{ ip }}
{% endfor %}
```

---

## **6.10 Looping Over CSV Data**

CSV loaded into Python becomes a list of dicts:

```python
addresses = [
  {"name": "Server01", "subnet": "10.1.1.1/32"},
  {"name": "Server02", "subnet": "10.1.1.2/32"},
]
```

### Template

```jinja2
{% for obj in addresses %}
config firewall address
  edit "{{ obj.name }}"
    set subnet {{ obj.subnet | cidr_to_ipmask }}
  next
{% endfor %}
```

---

## **6.11 Loop Controls: `break` and `continue`**

Skip an item:

```jinja2
{% for v in vlans %}
  {% if v.id == 999 %}
    {% continue %}
  {% endif %}
vlan {{ v.id }}
{% endfor %}
```

Stop early:

```jinja2
{% for v in vlans %}
  {% if v.id > 200 %}
    {% break %}
  {% endif %}
vlan {{ v.id }}
{% endfor %}
```

Used rarely but helpful.

---

## **6.12 Real-World Example: NVE Members (L2VNIs)**

```jinja2
interface nve1
  no shutdown
  host-reachability protocol bgp
  source-interface loopback1

{% for v in vlans if v.l2vni %}
  member vni {{ v.vni }}
    {% if fabric.replication == 'multicast' %}
    mcast-group {{ v.mcast_group }}
    {% else %}
    ingress-replication protocol bgp
    {% endif %}
{% endfor %}
```

Standard in VXLAN EVPN templates.

---

## **6.13 Real-World Example: BGP Neighbors**

### YAML

```yaml
bgp_neighbors:
  - { ip: 10.1.0.1, asn: 65000 }
  - { ip: 10.1.0.2, asn: 65000 }
```

### Template

```jinja2
{% for n in bgp_neighbors %}
neighbor {{ n.ip }} remote-as {{ n.asn }}
  update-source loopback0
  address-family ipv4 unicast
  send-community both
{% endfor %}
```

---

## **6.14 Loop Performance Considerations**

Loops are extremely fast — even hundreds of items render in milliseconds.

Performance issues occur only when:

- deep nested loops  
- many filters inline  
- too much logic in the template  

Best practice: **move heavy processing to Python.**

---

## **6.15 Best Practices for Loops**

- Keep loop logic simple  
- Filter inside loop header when possible  
- Combine loops with `is defined` and `divisibleby`  
- Use `set` for complex filter chains  
- Avoid over-nested loops; flatten data in Python  
- Keep templates readable and maintainable  

---

