05 – Jinja2 Tests (Boolean Checks for Conditional Logic)

This document explains Jinja2 tests, which allow templates to ask yes/no questions about data.
Tests are essential in network automation because network devices often require:

optional configuration blocks

conditional features

different behaviors per device role

checks for missing or undefined fields

structured output (e.g., adding spacing every N items)

Tests operate inside Jinja2 statements ({% ... %}), and they behave like validators or filters that return True or False.

5.1 What Is a Test?

A test evaluates a property of a value and returns a boolean result.

Syntax:

{% if variable is testname %}


With arguments:

{% if variable is testname(arg1, arg2) %}


Tests do not print text.
They are only used to determine when to print configuration sections.

5.2 Why Network Engineers Need Tests

Network configurations require decision-making:

Only configure loopbacks if defined

Print multicast settings only if replication mode is multicast

Print trunk configuration only if mode is trunk

Apply route-reflector-client only on spine devices

Generate spacing every N items (e.g., 5 VLANs per block)

Tests give templates intelligence without making them complicated.

5.3 The Most Important Tests

These are the tests you will use frequently:

is defined – Check if a variable exists

is not defined – Check if a variable does not exist

is sameas – Identity comparison

is iterable – Whether value can be looped

is divisibleby(n) – Useful for grouping output

is string, is number, etc. – Type checking

You will see concrete examples below.

5.4 Test: is defined

This test prevents errors by checking if a variable exists before using it.

Example in a VXLAN leaf device:

{% if loopbacks.lo1_ip is defined %}
interface loopback{{ fabric.nve_source_loopback }}
  ip address {{ loopbacks.lo1_ip }}/32
{% endif %}


If lo1_ip is missing, this block is skipped.

This is extremely important when not all devices have the same data (e.g., spines do not have VTEP loopbacks).

5.5 Test: is not defined

Used to provide fallback behavior.

Example:

{% if interface.description is not defined %}
  description DEFAULT-DESCRIPTION
{% endif %}


Useful for ensuring every interface has at least some description.

5.6 Test: is iterable

Useful for checking if an object can be looped.

Example:

{% if vlan_list is iterable %}
  switchport trunk allowed vlan {{ vlan_list | join(',') }}
{% endif %}


Prevents crashes when vlan_list is accidentally a single integer.

5.7 Test: is divisibleby(n)

This is extremely useful for creating structured and readable output.

Example: Add a spacing line every 5 VLANs.

{% for vlan in vlans %}
vlan {{ vlan.id }}
  name {{ vlan.name }}

{% if loop.index is divisibleby(5) %}
! -------- spacing --------
{% endif %}

{% endfor %}


This helps generate clean configuration in large fabric deployments.

5.8 Test: is number, is string, etc.

Examples:

{% if bgp.asn is number %}
router bgp {{ bgp.asn }}
{% endif %}

{% if hostname is string %}
hostname {{ hostname | upper }}
{% endif %}

5.9 Combining Tests With Conditions

Example: Only generate multicast configuration if all conditions match:

{% if fabric.replication == 'multicast' and vlan.mcast_group is defined %}
  mcast-group {{ vlan.mcast_group }}
{% else %}
  ingress-replication protocol bgp
{% endif %}


Complex nested behavior is possible but should remain readable.

5.10 Real-World Examples
1. Configure SVI only if IP exists
{% for v in vlans %}
{% if v.ip is defined %}
interface vlan {{ v.id }}
  ip address {{ v.ip }}
{% endif %}
{% endfor %}

2. Configure L3VNI only for VRFs with l3vni defined
{% if vrf.l3vni is defined %}
interface nve1
  member vni {{ vrf.l3vni }} associate-vrf
{% endif %}


Without this check, templates would generate invalid configs for VRFs that only provide Layer 2 services.

3. Configure BGP RR-client only for leafs
{% if role == 'leaf' %}
  route-reflector-client
{% endif %}

4. Configure interface description only if provided
interface {{ intf.name }}
{% if intf.description is defined %}
  description {{ intf.description }}
{% endif %}

5. Print tenant VLANs only if they belong to a VRF
{% for v in vlans if v.vrf is defined %}
vlan {{ v.id }}
  name {{ v.name }}
{% endfor %}


This design uses a Jinja feature: filtering directly inside the loop header.

5.11 Edge Case: defined vs none

These two are different:

undefined → variable does not exist

none → variable exists but set to null

Check for undefined:

{% if vrf.rd is defined %}


Check for none:

{% if vrf.rt is not none %}


Both are useful in data modeling.

5.12 Practical Use Case: Optional Underlay Interfaces

YAML:

underlay_interfaces:
  - { name: Ethernet1/1, ip: 10.0.0.1/31 }
  - { name: Ethernet1/2 }


Template:

interface {{ underlay.name }}
{% if underlay.ip is defined %}
  ip address {{ underlay.ip }}
{% else %}
  no ip address
{% endif %}

5.13 Best Practices for Using Tests

Always use is defined for optional fields.

Use tests for logic—never rely on empty strings.

Keep conditions simple; move complex logic to Python.

Avoid deeply nested if statements.

Use tests to avoid generating invalid configurations.
