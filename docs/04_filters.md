04 – Jinja2 Filters (Transforming Data Before Printing)

This document provides a complete, network-focused explanation of filters in Jinja2.
Filters allow you to modify, clean, sort, transform, or format values before they are printed in the final configuration.

4.1 What Is a Filter?

A filter takes a value and transforms it into another value.

Syntax:

{{ value | filter_name }}


Or with arguments:

{{ value | filter_name(arg1, arg2) }}


Filters let you clean and normalize data as it flows from YAML to CLI configuration.

4.2 Why Network Engineers Use Filters

Filters are used every day to:

produce deterministic, sorted VLAN lists

join lists into comma-separated strings

convert network formats (CIDR → IP + mask)

uppercase or sanitize names

remove duplicates from CSV data

type-cast strings into integers for routing features

build EVPN route-targets from VNIs

Filters improve configuration consistency and reduce complexity in templates.

4.3 Default Filters (Most Useful for Networking)

Below are the core Jinja filters that are frequently used in network automation.

4.3.1 join

Convert a list → comma-separated string.

YAML:

vlans: [10, 20, 30]


Template:

switchport trunk allowed vlan {{ vlans | join(',') }}


Output:

switchport trunk allowed vlan 10,20,30

4.3.2 sort

Sort a list alphabetically or numerically.

Template:

{% for v in vlans | sort(attribute='id') %}
vlan {{ v.id }}
{% endfor %}


This ensures consistent output across devices.

4.3.3 unique

Remove duplicates.

Example (CSV with repeated VLAN definitions):

{{ vlans | unique | sort | join(',') }}

4.3.4 upper / lower

Used for hostname normalization.

hostname {{ hostname | upper }}


Output:

hostname LEAF01

4.3.5 replace

Replace part of a string.

{{ vrf_name | replace('-', '_') }}


Example: VRF names normalized for N9K.

4.3.6 default(value)

Print fallback when variable is undefined:

ip address {{ intf.ip | default("0.0.0.0/32") }}


Useful for optional values.

4.3.7 int, float

Convert strings to numbers.

Used for:

BGP ASN

timers

priority values

Example:

router bgp {{ asn | int }}

4.4 Map + Attribute + Filters (Very Powerful Pattern)

You will use this frequently for network lists.

Example YAML (list of VLAN objects):

vlans:
  - { id: 10, name: Servers }
  - { id: 20, name: Users }


Extract only VLAN IDs:

{{ vlans | map(attribute='id') | list }}


Result:

[10, 20]


Full trunk example:

switchport trunk allowed vlan {{ vlans | map(attribute='id') | unique | sort | join(',') }}

4.5 Custom Filters (Defined in Python)

In large automation projects, you create your own filters for network needs.

Custom filters live in render.py:

def vni_rt(vni: int, asn: int):
    return f"{asn}:{int(vni)}"

def cidr_to_ipmask(cidr: str):
    # 10.10.10.1/32 → 10.10.10.1 255.255.255.255
    import ipaddress
    ip = ipaddress.ip_interface(cidr)
    return f"{ip.ip} {ip.network.netmask}"

def safe_name(s: str):
    return s.upper().replace(" ", "_").replace("-", "_")


Register them:

env.filters['vni_rt'] = vni_rt
env.filters['cidr_to_ipmask'] = cidr_to_ipmask
env.filters['safe_name'] = safe_name

4.6 Network Examples Using Custom Filters
4.6.1 EVPN Route-Target from VNI

Template:

route-target import {{ vrf.l3vni | vni_rt(fabric.asn) }} evpn


Data:

vrf:
  l3vni: 10001
fabric:
  asn: 65000


Output:

route-target import 65000:10001 evpn

4.6.2 FortiGate Subnet Conversion

Template:

set subnet {{ obj.subnet | cidr_to_ipmask }}


Example row:

10.10.10.1/32


Output:

set subnet 10.10.10.1 255.255.255.255

4.6.3 Sanitizing Names for NX-OS/EOS

Template:

vlan {{ v.id }}
  name {{ v.name | safe_name }}


Data:

"Prod-Web Servers"


Output:

name PROD_WEB_SERVERS

4.7 Complex Real-World Example: Trunk Allowed VLANs

YAML:

interfaces:
  - name: Ethernet1/1
    mode: trunk
    allowed_vlans: [20, 10, 10, 30]


Template:

{% set vl = intf.allowed_vlans | unique | sort | join(',') %}
switchport trunk allowed vlan {{ vl }}


Output:

switchport trunk allowed vlan 10,20,30


This ensures stable, clean diffs in Git.

4.8 Filters Combined With Loops

Example:

{% for addr in addresses | unique | sort %}
set allowed-address {{ addr }}
{% endfor %}


Used in firewall rules and prefix-lists.

4.9 Filter Blocks

Used to transform entire configuration blocks:

{% filter upper %}
hostname {{ hostname }}
{% endfilter %}


Output is entirely uppercase.

Rare but useful for normalizing vendor config.

4.10 Best Practices for Filters

Always sort lists before joining them.

Always remove duplicates.

Never put complex logic inside the template; keep it in Python.

Register custom filters only once in render.py.

Use filters for formatting, not for data validation.

Keep templates readable—avoid long filter chains inline.
