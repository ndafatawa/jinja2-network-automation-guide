09 – Whitespace Control in Jinja2

Whitespace control is one of the most overlooked but most important parts of building stable and predictable network configuration templates.
This document explains what whitespace control is, why it matters, and how to use it properly.

9.1 Why Whitespace Matters in Network Automation

When generating network configurations using Jinja2, uncontrolled whitespace can cause:

    blank lines in unexpected places

    extra spaces

    differences in indentation

    unstable diffs in Git

    inconsistent output across devices

    “noisy” reviews during change approval

This leads to:

    mistakes

    misalignment

    failing compliance checks

    configuration drift

Whitespace control ensures that generated configs are:

    deterministic

    clean

    consistent

    diff-friendly

For large deployments, this becomes extremely important.

9.2 How Jinja2 Handles Whitespace by Default

By default, Jinja2:

    keeps your indentation

    keeps blank lines

    prints a newline around every {% block %} and {% endblock %}

    prints newlines around logic statements

    does not strip empty lines created by loops

    treats spaces literally

This is NOT what we want for network configs.

9.3 Enabling Whitespace Control in Python (render.py)

A proper renderer sets:

    env = Environment(
        loader=FileSystemLoader(str(TPL)),
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=StrictUndefined,
    )


These two flags are critical:

    trim_blocks=True

Removes newline after Jinja2 blocks:

    {% if ... %}  <-- no blank line inserted
Actual config line here

    lstrip_blocks=True

Strips indentation before a control block:

      {% for x in xs %}
no leading spaces on this line


These two settings produce clean, predictable output.

9.4 Controlling Whitespace Directly Inside Templates Using “-%}”

Sometimes you want to suppress whitespace for a particular line.
Use:

    -%}


instead of:

    %}


Example:

    {% for v in vlans -%}
    vlan {{ v.id }}
      name {{ v.name }}
    {%- endfor %}
    

This produces:

    vlan 10
      name PROD
    vlan 20
      name USERS


Notice:

    no blank lines between entries

    clean spacing

    deterministic config

9.5 Clean Loop Example (Before vs After)
Without whitespace control:

Template:

    {% for v in vlans %}
    vlan {{ v.id }}
      name {{ v.name }}
    {% endfor %}


Output:

    vlan 10
      name PROD
    
    vlan 20
      name USERS
    


There are blank lines between entries.

With whitespace control:
    {% for v in vlans -%}
    vlan {{ v.id }}
      name {{ v.name }}
    {%- endfor %}


Output:

    vlan 10
      name PROD
    vlan 20
      name USERS


Exactly what you want.

9.6 Clean Conditional Blocks

Uncontrolled conditional blocks often produce empty lines:

    {% if vrf.l3vni %}
    router bgp 65001
      address-family l2vpn evpn
    {% endif %}


If vrf.l3vni is not defined, the template prints a blank line.

Fix using -%}:
    {% if vrf.l3vni -%}
    router bgp 65001
      address-family l2vpn evpn
    {%- endif %}


Now nothing is printed if condition is false.

9.7 Avoiding Extra Blank Lines at the Start or End of Files

Wrap top-level blocks tightly:

    {%- extends 'nxos/device_base.j2' -%}


or:

    {%- block base -%}
    ...
    {%- endblock %}
    

The leading/trailing whitespace is eliminated.

9.8 Whitespace Control for Multiline Jinja Blocks

Consider a large include:

    {% include 'nxos/underlay_intf.j2' %}


It may result in unwanted blank lines above/below the included text.

Use:

    {%- include 'nxos/underlay_intf.j2' -%}


This trims whitespace before and after the include.

9.9 Best Practices for Whitespace Control in Network Templates
1. Always enable trim_blocks and lstrip_blocks in the Python renderer.
2. Use -%} for loops, if-else, includes, and blocks wherever blank lines are not wanted.
3. Avoid adding trailing spaces in templates.
4. Keep indentation consistent.
5. Use linters or diff tools to enforce clean output.
6. Render a sample of multiple devices to confirm whitespace consistency.
9.10 Examples from Real Projects
VXLAN VNI list
    {% for v in l2_vnis -%}
    member vni {{ v.vni }}
      mcast-group {{ v.mcast_group }}
    {%- endfor %}

ACL entries
    {% for rule in rules -%}
    {{ rule.action }} {{ rule.src }} {{ rule.dst }} eq {{ rule.port }}
    {%- endfor %}

BGP neighbors
    router bgp {{ asn }}
    {% for nbr in neighbors -%}
      neighbor {{ nbr.ip }} remote-as {{ nbr.asn }}
    {%- endfor %}


All clean, no extra whitespace.

9.11 Common Mistakes to Avoid
Mistake	Result
Missing -%}	Extra blank lines
Using tabs instead of spaces	Misaligned configs
Adding empty lines between blocks	Unstable diffs
No trim/lstrip in renderer	Hard-to-read output
Putting logic-heavy structures inside templates	Loss of readability
