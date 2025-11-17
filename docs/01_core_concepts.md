01 – Core Concepts of Jinja2 for Network Automation

This document introduces the foundational ideas behind using Jinja2 templates and Python to generate network configuration.
These concepts apply to all network vendors (Cisco NX-OS, EOS, IOS-XE, FortiGate, Palo Alto, Juniper, etc.).

1. What Is a Jinja2 Template?

A template is simply a text file (CLI, JSON, XML, API payload) containing:

Static configuration

Placeholders for variables: {{ variable }}

Logic blocks: {% ... %}

Optional loops, conditionals, filters, macros, includes, inheritance

Example
interface mgmt0
  ip address {{ mgmt_ip }}


Templates are not data.
They only describe how configuration should be shaped.

2. Context (Your Data Model)

The context is a Python dictionary that provides all data the template will use.

Example Context
{
  "hostname": "LEAF1",
  "mgmt_ip": "172.16.10.11/24",
  "vlans": [
    {"id": 10, "name": "SERVERS"},
    {"id": 20, "name": "USERS"}
  ]
}


Key points:

Templates contain no actual values.

All values come from the context.

Context usually originates from YAML/CSV/JSON/Excel.

3. Rendering Process (How Config Is Generated)

Rendering = Template + Context + Jinja2 Engine → Final Config

The Pipeline
YAML / CSV / JSON / Excel
        ↓
Python loads + validates data
        ↓
Python builds context dictionary
        ↓
Jinja2 renders templates
        ↓
Final configuration text (CLI/API)

Python Example
output = template.render(context)

4. Data Sources Used in Network Automation

Your configuration data usually comes from:

YAML

Device inventory

Fabric settings

Underlay/overlay values

Per-device overrides

CSV

VLAN lists

Firewall objects

Routes / services

JSON

API outputs (NSX-T, ACI, Fortinet, etc.)

Excel

Using pandas (xlrd, openpyxl)

Python dictionaries

After validation and merging

All data becomes a structured Python dictionary.

5. Deterministic Output (Why It Matters)

Network automation must produce stable, predictable configuration.

Determinism ensures:

Git diffs are clean

No random ordering of lists

No silent missing values

Repeatable output

Achieved through:

unique | sort | join

Whitespace control

StrictUndefined enforcing missing variables

Templates containing minimal logic

6. Recommended Project Structure
project/
│
├── data/
│   ├── devices.yml
│   ├── fabric.yml
│   ├── vlans.csv
│   └── overrides.yml
│
├── templates/
│   ├── nxos/
│   │   ├── device_base.j2
│   │   ├── leaf.j2
│   │   ├── spine.j2
│   │   ├── underlay_intf.j2
│   │   ├── underlay_ospf.j2
│   │   └── overlay_leaf_evpn.j2
│   └── misc/
│       └── macros.j2
│
├── scripts/
│   └── render.py
│
└── build/
    └── <generated configs>


This structure is used by professional automation teams and NetDevOps shops.

7. Jinja2 Environment Configuration

Your Python renderer must create a Jinja2 Environment with strict options:

env = Environment(
    loader=FileSystemLoader("templates"),
    trim_blocks=True,
    lstrip_blocks=True,
    undefined=StrictUndefined
)

Meaning
Setting	Purpose
trim_blocks=True	Removes extra blank lines created by Jinja blocks
lstrip_blocks=True	Removes indentation before {% %}
StrictUndefined	Fails if a variable is missing (prevents broken configs)
8. Role of Python in Network Automation

Python does the heavy lifting:

Loads YAML / CSV / JSON / Excel

Validates structure

Normalizes values

Merges per-device overrides

Builds final context dictionary

Registers custom filters

Selects templates

Writes output files

Jinja2 should contain minimal logic — only what shapes the config.

Python handles complexity. Jinja2 handles layout.

9. Purpose of Jinja2 in Network Automation

Jinja2 provides:

Consistent configuration generation

Error reduction vs manual CLI typing

Vendor-neutral config creation

Reusable templates for thousands of devices

Git-controlled changes (pull requests, diffs)

High-scale deployment (DC VXLAN EVPN, firewalls, routing)

Ultimately:

Structured data → Templates → Automated configs

This is the foundation of modern network automation.
