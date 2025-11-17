'''
2.1 What is a Variable?

A variable is a placeholder inside a template.
It is a value provided by your data (YAML, CSV, Python dictionaries).

Template:

hostname {{ hostname }}


Data:

hostname: leaf01


Rendered output:

hostname leaf01


Variables allow templates to become dynamic, meaning one template can produce configuration for many different devices.

2.2 How to Write Variables in Templates

Syntax:

{{ variable_name }}


Everything inside the {{ ... }} is evaluated and printed.

2.3 Variables Come From the Context

Python:

template.render(
    hostname="leaf01",
    mgmt_ip="172.16.10.10",
    vlans=[{"id":10, "name":"Servers"}]
)


Template:

hostname {{ hostname }}
ip address {{ mgmt_ip }}

2.4 Dot Notation vs Bracket Notation

Dot notation:

{{ vlan.id }}
{{ device.hostname }}
{{ interface.description }}


Bracket notation:

{{ vlan['id'] }}
{{ device['hostname'] }}
{{ interface['description'] }}

2.5 How Dot Notation Works
{{ vlan.id }}


Jinja checks:

Does object have attribute id?

If not, does it have a dictionary key id?

For YAML → Python dicts, it normally resolves dictionary keys.

2.6 How Bracket Notation Works

Explicit:

{{ vlan['id'] }}


Always refers to dictionary key "id".

2.7 Recommended Style

Use dot notation in templates, and keep YAML as dictionaries.

Example:

switchport access vlan {{ interface.vlan }}

2.8 Examples of Variables in Network Templates
VLAN Example

YAML:

vlans:
  - id: 10
    name: Servers


Template:

vlan {{ vlan.id }}
  name {{ vlan.name }}


Output:

vlan 10
  name Servers

Interface Example

YAML:

interfaces:
  - name: Ethernet1/1
    mode: access
    vlan: 10


Template:

interface {{ intf.name }}
  switchport mode {{ intf.mode }}
  switchport access vlan {{ intf.vlan }}

BGP Example

YAML:

bgp:
  asn: 65001
  router_id: 10.1.1.1


Template:

router bgp {{ bgp.asn }}
  router-id {{ bgp.router_id }}

2.9 Nested Variables

YAML:

device:
  hostname: leaf01
  loopbacks:
    lo0: 10.1.1.1/32
    lo1: 10.1.2.1/32


Template:

hostname {{ device.hostname }}

interface loopback0
  ip address {{ device.loopbacks.lo0 }}

2.10 Missing Variables and StrictUndefined

Bad behavior (default Jinja):

hostname {{ hostname }}


Missing variable produces:

hostname 


This is dangerous for production configs.

Correct approach used in this repository:

undefined = StrictUndefined


This makes missing variables throw an error:

UndefinedError: 'hostname' is undefined

2.11 Variable Transformations (Filters)

Examples:

{{ hostname | upper }}
{{ vlan_list | join(',') }}
{{ vrf.asn | int }}


Filters are explained fully in 04_filters.md.

2.12 Common Variable Patterns in Network Templates
Hostname
hostname {{ hostname }}

Interface
interface {{ intf.name }}
description {{ intf.description }}

SVI
ip address {{ svi.ip }}

VLAN
switchport access vlan {{ intf.vlan }}

2.13 Best Practices

Use lowercase variable names.

Keep YAML consistent across devices.

Avoid overly deep nesting.

Validate required variables in Python.
'''
