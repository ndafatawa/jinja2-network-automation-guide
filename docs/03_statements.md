03 – Jinja2 Statements (Control Flow and Structure)

This document explains statements in Jinja2.
Statements do not print values.
Statements control logic, structure, and flow within the template.

Where variables print text:

{{ ... }}


Statements perform actions:

{% ... %}


Statements are used for:

loops

conditions

including files

inheritance

macros

whitespace control

Statements are central to writing large network automation templates.

3.1 What Are Statements?

A statement is a control instruction inside:

{% statement %}


Examples:

{% for vlan in vlans %}
{% endfor %}

{% if bgp.asn == 65001 %}
{% endif %}

{% include 'nxos/ospf.j2' %}
{% extends 'nxos/device_base.j2' %}

{% from 'misc/macros.j2' import p2p %}


Statements do not print text.
They control what will be printed.

3.2 Why Network Engineers Need Statements

Network configurations have:

repeating sections (interfaces, VLANs)

optional features (multicast, anycast gateway)

device roles (leaf, spine, border)

nested config blocks

multiple vendors

Statements enable you to:

loop through lists

conditionally include sections

insert reusable configuration blocks

structure templates cleanly

This is how you scale from 1 device to 200 devices.

3.3 The Most Common Jinja2 Statements

The statement types you will use daily:

for – loops

if / elif / else – conditional branching

include – insert another file

extends and block – template inheritance

set – create temporary variable

from … import – import macros

filter blocks (rare but useful)

Each is explained below.

3.4 The for Loop Statement

Syntax:

{% for item in list %}
... use item ...
{% endfor %}


Network example:

{% for v in vlans %}
vlan {{ v.id }}
  name {{ v.name }}
{% endfor %}


This loop prints a VLAN configuration block for each VLAN.

Filtering inside loop header (Jinja feature)
{% for v in vlans if v.vrf == 'PROD' %}
vlan {{ v.id }}
  name {{ v.name }}
{% endfor %}


This is useful when VLANs belong to different VRFs or tenants.

3.5 The if / elif / else Statement

Syntax:

{% if condition %}
...
{% elif other_condition %}
...
{% else %}
...
{% endif %}


Network example:

{% if fabric.replication == 'multicast' %}
  mcast-group {{ vlan.mcast_group }}
{% else %}
  ingress-replication protocol bgp
{% endif %}


This prints different overlay configs depending on the replication mode.

3.6 Inline if Expression (one-line conditional)

Syntax:

{{ value_if_true if condition else value_if_false }}


Network example (shutdown vs no shutdown):

shutdown {{ 'shutdown' if intf.admin_down else 'no shutdown' }}


Or for FortiGate:

set status {{ 'enable' if obj.enabled else 'disable' }}

3.7 The set Statement (temporary variables)

Used to simplify complex expressions.

Example:

{% set trunk_list = intf.allowed_vlans | unique | sort | join(',') %}
switchport trunk allowed vlan {{ trunk_list }}


This reduces duplication and improves readability.

3.8 The include Statement (insert another template)

Syntax:

{% include 'path/to/template.j2' %}


Network examples:

{% include 'nxos/underlay_intf.j2' %}
{% include 'nxos/underlay_ospf.j2' %}


This avoids copy/paste across templates and keeps things modular.

3.9 The extends and block Statements (template inheritance)

Inheritance allows creating:

a base template

role-specific templates that extend it

Example:

Base template (device_base.j2):
hostname {{ hostname }}

{% block underlay %}{% endblock %}
{% block overlay %}{% endblock %}
{% block services %}{% endblock %}

Leaf template:
{% extends 'nxos/device_base.j2' %}

{% block underlay %}
  {% include 'nxos/underlay_intf.j2' %}
  {% include 'nxos/underlay_ospf.j2' %}
{% endblock %}

{% block overlay %}
  {% include 'nxos/overlay_leaf_evpn.j2' %}
{% endblock %}

Spine template:
{% extends 'nxos/device_base.j2' %}

{% block overlay %}
  {% include 'nxos/overlay_spine_rr.j2' %}
{% endblock %}


This mirrors real DC fabric hierarchy:
Base → Underlay → Overlay → Services

3.10 The from … import Statement (import macros)

Macros are reusable configuration blocks.

Importing macros:

{% from 'misc/macros.j2' import p2p %}


Using the macro:

{{ p2p(intf.name, intf.ip, intf.desc) }}


More on macros in 07_macros.md.

3.11 The filter Block (less common)

Allows wrapping an entire block of text with a filter:

{% filter upper %}
hostname {{ hostname }}
{% endfilter %}


Useful for normalizing large outputs.

3.12 Comments in Templates

Jinja comments:

{# This is a comment #}


Comments do not appear in the final config.

Use comments to document logic inside templates.

3.13 Combining Statements

Real templates combine statements for powerful behavior.

Example: Only print L3VNI if VRF defines one:

{% if vrf.l3vni is defined %}
interface nve1
  member vni {{ vrf.l3vni }} associate-vrf
{% endif %}


Example: Generate anycast gateway only for L2VNI VLANs:

{% for v in vlans if v.l2vni %}
interface vlan {{ v.id }}
  fabric forwarding anycast-gateway
{% endfor %}

3.14 Putting It All Together (Example Template)

Full example using all important statements:

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


This is a shortened version of what you would use in a real VXLAN EVPN automation project.

3.15 Best Practices for Statements

Keep logic simple. Push complex logic to Python.

Use include to avoid repeating configuration blocks.

Group related configuration using inheritance.

Use if is defined to prevent printing incomplete configs.

Combine statements only when necessary; avoid unreadable templates.
