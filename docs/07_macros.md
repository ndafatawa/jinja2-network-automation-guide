07 – Jinja2 Macros (Reusable Configuration Blocks)

This document explains macros in Jinja2.
Macros are one of the most powerful features available in configuration templating because they allow you to define reusable configuration blocks, very similar to functions in programming.

Macros help keep network automation templates:

clean

modular

reusable

consistent across devices

easy to maintain

7.1 What Is a Macro?

A macro is a reusable block of template code that behaves like a function.

You write it once and use it many times.

Syntax:

{% macro name(param1, param2) %}
  ... body ...
{% endmacro %}


To use it:

{{ name(arg1, arg2) }}


Macros do not print automatically.
You must explicitly call them using {{ ... }}.

7.2 Why Network Engineers Need Macros

Macros are used to avoid copy/paste when you have repetitive configuration blocks, such as:

interface templates (L3 P2P interfaces)

SVIs

NVE members

ACL entries

firewall address objects

BGP neighbor stanzas

OSPF interface settings

VRF definitions

reusable service profiles

Macros ensure:

consistent formatting

fewer mistakes

easier updates

cleaner templates

compatibility across vendors

7.3 Where Macros Are Stored

Macros are usually placed in a dedicated file such as:

templates/misc/macros.j2


This keeps project structure clean and logical.

7.4 Simple Macro Example
{% macro svi(id, name, ip) -%}
interface vlan {{ id }}
  name {{ name }}
  ip address {{ ip }}
  no shutdown
{%- endmacro %}


Call this anywhere:

{{ svi(10, 'Servers', '10.10.10.1/24') }}


Rendered output:

interface vlan 10
  name Servers
  ip address 10.10.10.1/24
  no shutdown

7.5 Macro With Optional Parameters (Default Values)

Example:

{% macro p2p(intf, ip, desc='') -%}
interface {{ intf }}
  description {{ desc }}
  no switchport
  mtu 9216
  ip address {{ ip }}
  no shutdown
{%- endmacro %}


Call without description:

{{ p2p('Ethernet1/1', '10.0.0.1/31') }}


Call with description:

{{ p2p('Ethernet1/2', '10.0.0.3/31', 'Link to spine-02') }}

7.6 Importing Macros

To use a macro stored in another file:

{% from 'misc/macros.j2' import p2p %}


Then call:

{{ p2p(intf.name, intf.ip, intf.description) }}


You can import multiple macros:

{% from 'misc/macros.j2' import svi, p2p, nve_member %}

7.7 Real-World Examples
7.7.1 Macro: Point-to-Point Underlay Interface

Underlay interface setup is often repeated:

{% macro underlay_intf(intf, ip) -%}
interface {{ intf }}
  no switchport
  mtu 9216
  ip address {{ ip }}
  ip ospf network point-to-point
  no shutdown
{%- endmacro %}


Use:

{{ underlay_intf('Ethernet1/1', '10.0.0.1/31') }}

7.7.2 Macro: EVPN NVE Member Block
{% macro nve_l2vni(vni, mcast_group=None) -%}
  member vni {{ vni }}
    {% if mcast_group is defined %}
    mcast-group {{ mcast_group }}
    {% else %}
    ingress-replication protocol bgp
    {% endif %}
{%- endmacro %}


Use:

{{ nve_l2vni(v.vni, v.mcast_group) }}

7.7.3 Macro: FortiGate Address Object
{% macro fg_addr(name, subnet) -%}
config firewall address
  edit "{{ name }}"
    set subnet {{ subnet | cidr_to_ipmask }}
  next
end
{%- endmacro %}


Use:

{{ fg_addr(obj.name, obj.subnet) }}

7.7.4 Macro: SVI Anycast Gateway (VXLAN EVPN)
{% macro svi_anycast(id, ip) -%}
interface vlan {{ id }}
  ip address {{ ip }}
  fabric forwarding anycast-gateway
  no shutdown
{%- endmacro %}


Use:

{{ svi_anycast(vlan.id, vlan.ip) }}

7.8 Passing Complex Data Structures

Macro calls can receive entire objects:

{{ svi(vlan.id, vlan.name, vlan.ip) }}


Or for VRF:

{{ vrf_block(vrf.name, vrf.l3vni, vrf.rt) }}


Macros accept any values you pass, including lists, dictionaries, or nested objects.

7.9 Combining Macros With Loops

Example: Create many P2P underlay interfaces:

{% for u in underlay %}
{{ p2p(u.iface, u.ip, u.desc) }}
{% endfor %}


This is cleaner than writing all configuration logic directly in the loop.

7.10 Macro Scoping Rules

Important rules:

Macros cannot modify variables outside themselves.

Macros only see values passed into them.

Macros do not inherit template blocks.

Macros can be stored anywhere and imported.

Macros behave like pure functions: no side effects, no global state modification.

7.11 Advanced Macro Usage
Macro Returning Text Instead of Printing

Macros always return a text string.
You can store it:

{% set text = p2p('Eth1/1', '10.0.0.1/31') %}
{{ text }}

Macro inside a filter block
{% filter upper %}
{{ p2p('Eth1/2', '10.0.0.3/31') }}
{% endfilter %}

7.12 When to Use Macros vs Includes vs Inheritance
Feature	Use Case
Macro	Reusable config function (like SVI, NVE member, firewall rule)
Include	Insert another file, like an OSPF block or BGP block
Inheritance	Overall shape or skeleton of device configs (base → leaf/spine)

Macros are best for parameterized, repeatable blocks.

7.13 Best Practices for Macros

Store macros in a dedicated file (misc/macros.j2).

Keep macros small and focused.

Use descriptive macro names.

Pass all required data as parameters (do not depend on global variables).

Keep logic inside macros minimal—prefer tests and filters rather than deep branching.

Avoid embedding macros inside templates; import them instead.
