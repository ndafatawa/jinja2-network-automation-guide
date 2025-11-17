# **12 – Vendor-Specific Jinja2 Examples (NX-OS, EOS, FortiGate, JunOS)**

This chapter shows **real-world Jinja2 template examples** for major network vendors used in automation projects:

- Cisco NX-OS (VXLAN EVPN fabrics)
- Arista EOS
- FortiGate Firewalls
- JunOS (optional WAN/PE examples)

These examples demonstrate how the concepts from the previous chapters are applied to actual device configuration templates.

---

# **12.1 Cisco NX-OS Examples**

Cisco NX-OS is the most common use case for Jinja2 in data-center automation, especially for **VXLAN EVPN underlay + overlay** generation.

---

## **12.1.1 NX-OS – VLAN Definition**

**YAML**

```yaml
vlans:
  - { id: 10, name: SERVERS }
  - { id: 20, name: USERS }
```

**Template**

```jinja2
{% for v in vlans -%}
vlan {{ v.id }}
  name {{ v.name | upper }}
{%- endfor %}
```

---

## **12.1.2 NX-OS – SVI Interface with Anycast Gateway**

```jinja2
{% for v in vlans if v.ip is defined -%}
interface vlan {{ v.id }}
  ip address {{ v.ip }}
  fabric forwarding anycast-gateway
  no shutdown
{%- endfor %}
```

---

## **12.1.3 NX-OS – Underlay P2P Interfaces**

Using a macro:

```jinja2
{% from 'misc/macros.j2' import p2p %}

{% for u in underlay -%}
{{ p2p(u.iface, u.ip, u.desc) }}
{%- endfor %}
```

---

## **12.1.4 NX-OS – Underlay OSPF**

```jinja2
router ospf UNDERLAY
  router-id {{ loopbacks.lo0_ip }}
  {% for u in underlay -%}
  network {{ u.ip }} area 0.0.0.0
  {%- endfor %}
```

---

## **12.1.5 NX-OS – NVE Interface (VXLAN EVPN)**

```jinja2
interface nve1
  no shutdown
  host-reachability protocol bgp
  source-interface loopback{{ fabric.nve_source_loopback }}

{% for v in vlans if v.l2vni -%}
  member vni {{ v.vni }}
    {% if fabric.replication == 'multicast' -%}
    mcast-group {{ v.mcast_group }}
    {% else -%}
    ingress-replication protocol bgp
    {%- endif %}
{%- endfor %}
```

---

## **12.1.6 NX-OS – BGP EVPN**

```jinja2
router bgp {{ fabric.asn }}
  router-id {{ loopbacks.lo0_ip }}

  {% for rr in route_reflectors -%}
  neighbor {{ rr.ip }} remote-as {{ fabric.asn }}
    update-source loopback0
    address-family l2vpn evpn
    route-reflector-client
  {%- endfor %}
```

---

# **12.2 Arista EOS Examples**

EOS is often used for leaf/spine fabrics.

---

## **12.2.1 Simple VLAN Template**

```jinja2
{% for v in vlans | sort(attribute='id') -%}
vlan {{ v.id }}
  name {{ v.name | upper }}
{%- endfor %}
```

---

## **12.2.2 EOS SVI Template**

```jinja2
{% for v in vlans if v.ip is defined -%}
interface vlan {{ v.id }}
  ip address {{ v.ip }}
{%- endfor %}
```

---

## **12.2.3 EOS Underlay Interfaces**

```jinja2
{% for u in underlay -%}
interface {{ u.name }}
  mtu 9216
  ip address {{ u.ip }}
  no shutdown
{%- endfor %}
```

---

# **12.3 FortiGate Examples**

FortiGate templates often receive data from CSV files (objects, groups, firewall rules).

---

## **12.3.1 FortiGate Address Objects**

CSV (loaded into Python):

```
name,subnet
Server01,10.1.1.1/32
Server02,10.1.1.2/32
```

Template:

```jinja2
{% for obj in addr_objects -%}
config firewall address
  edit "{{ obj.name }}"
    set subnet {{ obj.subnet | cidr_to_ipmask }}
  next
end
{%- endfor %}
```

---

## **12.3.2 FortiGate Service Objects**

```jinja2
{% for svc in services -%}
config firewall service custom
  edit "{{ svc.name }}"
    set tcp-portrange {{ svc.port }}
  next
end
{%- endfor %}
```

---

## **12.3.3 FortiGate Firewall Policies**

```jinja2
{% for rule in rules -%}
config firewall policy
  edit 0
    set name "{{ rule.name }}"
    set srcintf "{{ rule.src_intf }}"
    set dstintf "{{ rule.dst_intf }}"
    set srcaddr "{{ rule.src_addr }}"
    set dstaddr "{{ rule.dst_addr }}"
    set service "{{ rule.service }}"
    set action {{ rule.action }}
  next
end
{%- endfor %}
```

---

## **12.3.4 FortiGate VIP (Port Forwarding)**

```jinja2
{% for vip in vips -%}
config firewall vip
  edit "{{ vip.name }}"
    set extip {{ vip.ext_ip }}
    set mappedip "{{ vip.int_ip }}"
    set portforward enable
    set extport {{ vip.ext_port }}
    set mappedport {{ vip.int_port }}
  next
end
{%- endfor %}
```

---

# **12.4 JunOS Examples (Optional)**

Juniper is common in WAN/PE/MPLS automation projects.

---

## **12.4.1 Interfaces**

```jinja2
{% for intf in interfaces -%}
interfaces {
  {{ intf.name }} {
    description "{{ intf.desc }}";
    unit 0 {
      family inet {
        address {{ intf.ip }};
      }
    }
  }
}
{%- endfor %}
```

---

## **12.4.2 BGP Peers**

```jinja2
protocols {
  bgp {
    group EBGP {
      type external;
      local-as {{ asn }};
      {% for n in neighbors -%}
      neighbor {{ n.ip }} {
        peer-as {{ n.asn }};
      }
      {%- endfor %}
    }
  }
}
```

---

# **12.5 Multi-Vendor Example: VLAN Structure**

Same YAML for all vendors:

```yaml
vlans:
  - { id: 10, name: PROD }
  - { id: 20, name: USERS }
```

**NX-OS**

```jinja2
vlan {{ v.id }}
  name {{ v.name }}
```

**EOS**

```jinja2
vlan {{ v.id }}
   name {{ v.name }}
```

**FortiGate**

```jinja2
config firewall addrgrp
  edit "{{ v.name }}"
    set member "{{ v.id }}"
  next
end
```

Shows how **one data model** can drive **multiple vendor configs**.

---

# **12.6 Best Practices for Vendor Templates**

- Reuse a single YAML/CSV data model; avoid vendor-specific data duplication.
- Put vendor templates into separate directories:
  ```
  templates/
    nxos/
    eos/
    fortigate/
    junos/
  ```
- Use inheritance for NX-OS/EOS.
- Use macros for repetitive blocks (SVIs, interface templates, VIPs).
- Keep all transformation logic in Python, not templates.
- Always use StrictUndefined for safe rendering.
- Validate vendor-specific structures (Forti policies, VIPs, VNIs, etc.).

---

Vendor templates bring everything together:  
**data → context → templates → final multi-vendor configurations.**
