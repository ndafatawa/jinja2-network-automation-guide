06 – Jinja2 Loops (Iterating Over Lists in Network Templates)

This document explains loops in Jinja2, how they function, how they relate to YAML/CSV data, and how real network engineers use them in VXLAN EVPN, interface configuration, firewall rules, and template generation.

Loops are one of the most important mechanisms in network automation because almost all network configurations contain repetitive blocks.

6.1 What Is a Loop?

A loop allows you to repeat a block of configuration for each item in a list.

Syntax:

{% for item in list %}
  ... do something with item ...
{% endfor %}


Loops generate dynamic, scalable configuration blocks.

6.2 Why Network Engineers Use Loops

Network devices often require repeating structures:

VLAN definitions

SVI interfaces

EVPN VNIs

VRF definitions

BGP neighbors

Underlay interfaces

Trunk allowed VLAN lists

Address objects (FortiGate)

Without loops, you would need to copy/paste dozens or hundreds of configuration blocks manually.

Loops eliminate repetition and errors.

6.3 Basic Loop Example (VLAN List)

YAML:

vlans:
  - { id: 10, name: Servers }
  - { id: 20, name: Users }
  - { id: 30, name: DMZ }


Template:

{% for v in vlans %}
vlan {{ v.id }}
  name {{ v.name }}
{% endfor %}


Rendered output:

vlan 10
  name Servers
vlan 20
  name Users
vlan 30
  name DMZ

6.4 Loop With Nested Values

YAML:

interfaces:
  - name: Ethernet1/1
    mode: access
    vlan: 10
  - name: Ethernet1/2
    mode: trunk
    allowed: [10,20,30]


Template:

{% for intf in interfaces %}
interface {{ intf.name }}
  switchport mode {{ intf.mode }}

  {% if intf.mode == 'access' %}
  switchport access vlan {{ intf.vlan }}
  {% else %}
  switchport trunk allowed vlan {{ intf.allowed | join(',') }}
  {% endif %}
{% endfor %}

6.5 Filtering Inside Loop Header

Jinja2 allows filtering directly in the loop header.

Example: Only print VLANs belonging to a specific VRF:

{% for v in vlans if v.vrf == 'PROD' %}
vlan {{ v.id }}
  name {{ v.name }}
{% endfor %}


Example: Only print L3VNI VLANs:

{% for v in vlans if v.l3vni %}
...
{% endfor %}


This is more readable than writing an if block inside the loop.

6.6 Loop Index (Very Useful)

Every loop exposes loop.index, loop.index0, and other attributes.

Example:

{% for v in vlans %}
! VLAN number {{ loop.index }} in the list
vlan {{ v.id }}
{% endfor %}


Attributes:

loop.index → starts at 1

loop.index0 → starts at 0

loop.first → True for first iteration

loop.last → True for last iteration

Useful for numbering interface descriptions, comments, or groupings.

6.7 Grouping Output Using divisibleby

This is extremely useful for readable configurations.

Example: Add a blank line after every 5 VLANs:

{% for v in vlans %}
vlan {{ v.id }}
  name {{ v.name }}

{% if loop.index is divisibleby(5) %}
! -------- spacing --------
{% endif %}

{% endfor %}


Used in:

firewall addresses

prefix-lists

VLAN tables

static routes

6.8 Nested Loops

Nested loops operate exactly like nested Python loops.

Example: VRFs and VLANs inside each VRF.

YAML:

vrfs:
  - name: PROD
    vlans: [10, 20]
  - name: GUEST
    vlans: [30]


Template:

{% for vrf in vrfs %}
vrf context {{ vrf.name }}

{% for v in vrf.vlans %}
  vlan {{ v }}
{% endfor %}

{% endfor %}

6.9 Looping Over Dictionaries

Sometimes YAML has dictionary structures:

loopbacks:
  lo0: 10.1.1.1/32
  lo1: 10.1.2.1/32


Template:

{% for name, ip in loopbacks.items() %}
interface {{ name }}
  ip address {{ ip }}
{% endfor %}

6.10 Looping Over CSV Data

If CSV is loaded into Python as a list of dicts:

addresses = [
  {"name": "Server01", "subnet": "10.1.1.1/32"},
  {"name": "Server02", "subnet": "10.1.1.2/32"},
]


Template:

{% for obj in addresses %}
config firewall address
  edit "{{ obj.name }}"
    set subnet {{ obj.subnet | cidr_to_ipmask }}
  next
{% endfor %}

6.11 Loop Controls: break and continue

Jinja2 supports loop control similar to Python but more limited.

Skip one item:
{% for v in vlans %}
  {% if v.id == 999 %}
    {% continue %}
  {% endif %}
vlan {{ v.id }}
{% endfor %}

Stop the loop early:
{% for v in vlans %}
  {% if v.id > 200 %}
    {% break %}
  {% endif %}
vlan {{ v.id }}
{% endfor %}


Used rarely, but sometimes helpful.

6.12 Real-World Example: NVE Members for L2VNIs

Template:

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


This is typical in VXLAN-EVPN automation.

6.13 Real-World Example: BGP Neighbors

YAML:

bgp_neighbors:
  - { ip: 10.1.0.1, asn: 65000 }
  - { ip: 10.1.0.2, asn: 65000 }


Template:

{% for n in bgp_neighbors %}
neighbor {{ n.ip }} remote-as {{ n.asn }}
  update-source loopback0
  address-family ipv4 unicast
  send-community both
{% endfor %}

6.14 Loop Performance Considerations

Loops are extremely fast.
Even hundreds of entries render in milliseconds.

Bottlenecks occur only when:

deep nested loops with heavy transformations

loops combine many filters inline

templates are overly complex

Best practice:
Move heavy processing into Python before rendering.

6.15 Best Practices for Using Loops

Keep loop logic simple.

Use filtering in the loop header where possible.

Combine with tests (is defined, divisibleby) for clean output.

Use intermediate variables (set) for readability.

Avoid too many nested loops; flatten data if needed.
