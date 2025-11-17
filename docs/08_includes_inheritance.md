
08 – Includes and Template Inheritance in Jinja2

This document explains two of the most important Jinja2 features for building clean, scalable network automation templates:

Includes

Template inheritance

These features allow you to build modular, maintainable configuration templates for large network environments (e.g., multi-vendor fabrics, multi-site projects, VXLAN EVPN deployments, security devices, etc.).

8.1 Why This Matters in Network Automation

In a real project:

All switches share common base configuration

Leaves share overlay and underlay patterns

Spines share route-reflector patterns

Firewalls share address object and policy structures

Routers share WAN template blocks

Writing a single giant template is not scalable.
Instead, you break everything into logical, reusable building blocks.

Templates become:

easier to read

easier to test

easier to extend

shared across vendors

maintainable over years

Includes and inheritance are how you achieve this.

8.2 Includes — “paste another template here”

Includes allow you to pull another file into your current template exactly where you need it.

Syntax:

{% include 'path/to/partial_template.j2' %}


Think of include as:

"Insert the output of this other template at this exact location."

This is similar to pasting a reusable piece of configuration text.

8.3 Typical Use Cases for Includes
1. Common base config for all switches
{% include 'nxos/base_common.j2' %}


Examples inside base_common:

feature interface-vlan
feature ospf
no ip domain-lookup

2. Underlay interface configuration
{% include 'nxos/underlay_intf.j2' %}

3. Underlay OSPF config
{% include 'nxos/underlay_ospf.j2' %}

4. Overlay EVPN config
{% include 'nxos/overlay_leaf_evpn.j2' %}

5. Vendor-specific optional blocks
{% if os == 'eos' %}
{% include 'eos/vlan_template.j2' %}
{% endif %}

8.4 Template Inheritance — “page skeleton + override sections”

Inheritance is the most powerful Jinja2 structuring tool.

It allows you to define:

a base template (the master layout)

child templates that extend the base

blocks inside the base that child templates override

This is exactly how web frameworks build pages — and it works perfectly for network configs.

8.5 Base Template Example (device_base.j2)

This is the skeleton for all switches:

{# templates/nxos/device_base.j2 #}

hostname {{ hostname }}

{% block base %}
{# base config goes here #}
{% endblock %}

{% block underlay %}
{# underlay config here #}
{% endblock %}

{% block overlay %}
{# overlay (EVPN, VXLAN) #}
{% endblock %}

{% block services %}
{# SNMP, AAA, logging, NTP #}
{% endblock %}


It defines named blocks that child templates can replace.

8.6 Child Template Example (leaf.j2)
{% extends 'nxos/device_base.j2' %}

{% block base %}
{% include 'nxos/base_common.j2' %}
{% endblock %}

{% block underlay %}
{% include 'nxos/underlay_intf.j2' %}
{% include 'nxos/underlay_ospf.j2' %}
{% endblock %}

{% block overlay %}
{% include 'nxos/overlay_leaf_evpn.j2' %}
{% endblock %}


This gives you:

a clean structure

predictable layout

reusable building blocks

Child templates do not recreate everything; they simply fill in the blocks.

8.7 Why Use Inheritance Instead of Many Includes?

Inheritance is better when:

you want a standard structure for all devices

you want different device types to override specific areas

you want clean separation (base → underlay → overlay → services)

Before:

leaf.j2 → include 5 things
spine.j2 → include 5 other things
edge.j2 → include 3 things


Hard to manage.

After using inheritance:

device_base.j2 → defines structure
leaf.j2        → fills blocks
spine.j2       → fills blocks
edge.j2        → fills blocks


Clean, predictable, scalable.

8.8 How Templates Are Selected (from render.py)

Python chooses which template to render based on device role:

if dev['role'] == 'leaf':
    template = 'nxos/leaf.j2'
else:
    template = 'nxos/spine.j2'


This makes large network generation easy:

leaf.j2 → extends base + overlay + underlay  
spine.j2 → extends base + underlay only  

8.9 Nested Includes

Includes can also include other includes:

leaf.j2
 ├── base_common.j2
 ├── underlay_intf.j2
 ├── underlay_ospf.j2
 └── overlay_leaf_evpn.j2
      └── includes macros.j2


This means your project can grow without losing readability.

8.10 Include vs. Macro vs. Inheritance (Summary)
Feature	Purpose	Best Use Case
Include	Insert another file	Insert static or generic template blocks
Macro	Reusable template function	SVIs, NVE members, interfaces, firewall rules
Inheritance	Ensure clean structure	Base → leaf → spine → firewall → etc.

Together, they form the backbone of a maintainable Jinja2 automation project.

8.11 Real Network Example: NX-OS Leaf Config Assembly

Using the building blocks:

device_base.j2

leaf.j2

base_common.j2

underlay_intf.j2

underlay_ospf.j2

overlay_leaf_evpn.j2

The final rendered leaf config is assembled like this:

hostname LEAF1

### BASE ###
(feature commands, mgmt, system)

### UNDERLAY ###
interface e1/1
  ip address...
interface e1/2
  ip address...
router ospf UNDERLAY
  router-id...

### OVERLAY ###
interface nve1
  source-interface loopback1
  member vni ...
router bgp 65001
  l2vpn evpn...


With different blocks depending on role:

leaf → full VXLAN EVPN

spine → only RR + underlay

border leaf → optional blocks

8.12 Best Practices for Using Includes and Inheritance

Use inheritance for overall config layout.

Use include for large reusable pieces (underlay, base).

Use macros for parameterized reusable blocks (SVIs, interfaces).

Keep templates small and readable.

Avoid putting business logic in templates. Push logic to Python.

Use StrictUndefined to catch missing values.

Use directories per vendor (nxos, eos, fortigate, junos, etc.).
