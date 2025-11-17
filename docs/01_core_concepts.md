01 — Core Concepts of Jinja2 for Network Automation

1.1 What Is a Template?

A template is a configuration file that contains:

  normal device CLI

  placeholders (variables)

  small pieces of logic (loops, conditions)

Example:

    hostname {{ hostname }}
  
    interface Ethernet1/1
      ip address {{ loopback0 }}


Templates allow you to generate many configs from one template.

1.2 What Is Rendering?

  Rendering is the process of combining:
  
    Template (structure)
  
    Context (data)
  
  To produce:
  
    Final configuration text
  
  Rendering is simply:
  
  Template + Data → Final Config
  
  
  Example:
  
  Template:
  
      hostname {{ hostname }}
  
  
  Context:
  
      hostname: leaf01
  
  
  Rendered output:
  
      hostname leaf01

1.3 The Automation Pipeline (Important Mental Model)

This is the most important diagram in this entire repository.
  
    YAML / CSV                      ← Your data (per device, per fabric, per VLAN, per VRF)
          ↓
    Python loader                   ← Reads YAML/CSV into Python dictionaries
          ↓
    Context dict                    ← Clean, validated data passed to the template
          ↓
    Jinja2 template                 ← NX-OS/EOS/FortiGate/Arista template
          ↓
    Rendered config                 ← build/<device>.cfg


You must understand this pipeline clearly.
Everything in this repository follows this exact flow.

1.4 Why Network Engineers Use Templates

  1. Consistency
  Every device receives identical structure and style.
  
  2. Scale
  Hundreds of devices can be generated at once.
  
  3. Speed
  A full VXLAN/DC fabric can be generated in seconds.
  
  4. Change control
  Small changes in YAML ripple through all configs safely.
  
  5. Reduce errors
  Templates prevent typos and missing fields.
  
  1.5 What Is “Context”?
  
  Context is simply the data passed into the template.

Example YAML:

    hostname: leaf01
    role: leaf
    vlans:
      - { id: 10, name: Servers }
      - { id: 20, name: Users }


The Jinja template can access this as:

    hostname {{ hostname }}
  
    {% for v in vlans %}
      vlan {{ v.id }}
        name {{ v.name }}
    {% endfor %}

1.6 Why YAML and CSV?

YAML is used for:

    Per-device data
  
    Per-fabric data
  
    Hierarchical settings

CSV is used for:

    Long flat lists
  
    VLAN tables
  
    Address objects
  
    Firewall rules
  
    Services

This separation is standard across automation projects.

1.7 Where Python Fits

Python:

  Loads the YAML/CSV
  
  Validates data
  
  Applies custom filters
  
  Selects templates per role (leaf/spine/firewall)
  
  Renders the final config
  
  Writes files to /build/
  
  This glue logic lives in scripts/render.py.

1.8 Jinja2’s Purpose in Network Automation

Jinja2 solves three key problems:

1. Configuration repetition

Instead of writing 20 similar VLAN blocks, you write:

  {% for v in vlans %}
  vlan {{ v.id }}
    name {{ v.name }}
  {% endfor %}

2. Conditional logic

Access vs trunk, multicast vs ingress replication:

  {% if fabric.replication == 'multicast' %}
    mcast-group {{ v.mcast_group }}
  {% else %}
    ingress-replication protocol bgp
  {% endif %}

3. Transform data smoothly

Filters convert raw data into vendor-ready syntax.

Example:

  switchport trunk allowed vlan {{ vlans | join(',') }}
