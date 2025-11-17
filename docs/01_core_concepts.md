01 – Core Concepts of Jinja2 for Network Automation

This document defines the essential concepts required to use Jinja2 to generate deterministic, scalable network configuration files.

1. Jinja2 Template

A template is a text file containing configuration with variable placeholders and optional logic.

Example:

interface mgmt0
  ip address {{ mgmt_ip }}


A template may include:

placeholders ({{ ... }})

logic blocks ({% ... %})

filters (| ...)

loops

conditionals

macros

includes

inheritance

2. Context (Data Model)

The context is a Python dictionary passed to Jinja2 at render time.

Example Python structure:

{
  "hostname": "LEAF1",
  "mgmt_ip": "172.16.10.11/24",
  "vlans": [
    {"id": 10, "name": "SERVERS"},
    {"id": 20, "name": "USERS"}
  ]
}


Templates do not contain data.
Context supplies all device-specific information.

3. Rendering Process

Rendering is the process of combining:

template

context dictionary

Jinja2 engine

to produce the final configuration text.

Conceptual pipeline:

YAML / CSV / JSON / Excel
       ↓ (Python load + validation)
Context dictionary
       ↓ (Python renderer)
Jinja2 template
       ↓
Final configuration output


Render example:

output = template.render(context)

4. Data Sources

Device data usually comes from:

YAML (hierarchical data per device/site)

CSV (flat repetitive tables such as VLANs, firewall objects)

JSON (API or inventory export)

Excel (via pandas)

Python dictionaries (generated programmatically)

All sources must produce a validated dictionary for Jinja2.

5. Deterministic Output

All configuration output must be deterministic:

Lists must be sorted

Whitespace must be controlled

Missing variables must raise errors (StrictUndefined)

Filters should normalize values (sort, unique, join)

This ensures stable Git diffs and prevents configuration drift.

6. Project Structure (Recommended)
project/
  data/
    devices.yml
    fabric.yml
    vlans.csv
    overrides.yml
  templates/
    nxos/
      device_base.j2
      leaf.j2
      spine.j2
      underlay_intf.j2
      underlay_ospf.j2
      overlay_leaf_evpn.j2
    misc/
      macros.j2
  scripts/
    render.py
  build/
    <generated configs>

7. Jinja2 Engine Configuration (Python)

A correct environment definition ensures predictable output:

env = Environment(
    loader=FileSystemLoader("templates"),
    trim_blocks=True,
    lstrip_blocks=True,
    undefined=StrictUndefined
)


Key settings:

trim_blocks: removes trailing newlines after blocks

lstrip_blocks: removes indentation before blocks

StrictUndefined: fail if context data is missing

8. Role of Python

Python performs:

file loading (YAML/CSV/JSON)

data validation and normalization

merging of datasets

construction of the context dictionary

selection of device template

registration of custom filters

writing final configuration to build/

Templates should contain minimal logic.
All complex logic belongs in Python.

9. Purpose of Jinja2 in Network Automation

Jinja2 enables:

consistent configuration generation

elimination of manual errors

reusable configuration components

predictable change control

multi-vendor templating

integration with Git/GitOps

generation of thousands of configs in seconds

It converts data + templates → deployable configurations.
