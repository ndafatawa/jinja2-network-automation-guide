01 – Core Concepts of Jinja2 for Network Automation

This document explains the essential building blocks used when generating network configuration using Jinja2 and Python.

1. Jinja2 Template

A template is a text file containing configuration with placeholders and optional logic.

Example:

interface mgmt0
  ip address {{ mgmt_ip }}


Templates can contain:

Variables ( {{ ... }} )

Logic ({% ... %})

Filters (| ...)

Loops

Conditionals

Macros

Includes

Inheritance

2. Context (Data Model)

The context is a Python dictionary passed to Jinja2 when rendering.

Example:

{
  "hostname": "LEAF1",
  "mgmt_ip": "172.16.10.11/24",
  "vlans": [
    {"id": 10, "name": "SERVERS"},
    {"id": 20, "name": "USERS"}
  ]
}


Templates do not contain data.
Context provides all variable values.

3. Rendering Process

Rendering combines:

Template

Context

Jinja2 engine

to produce final configuration.

Pipeline:

YAML / CSV / JSON / Excel
↓
Python loads + validates
↓
Context dictionary
↓
Jinja2 renders using templates
↓
Final configuration text


Example:

output = template.render(context)

4. Data Sources

Data is usually stored in:

YAML (device/fabric inventory)

CSV (VLAN tables, firewall objects)

JSON (API exports)

Excel (via pandas)

Python dicts

All data becomes a validated dictionary.

5. Deterministic Output

Config must be deterministic:

Lists sorted

Whitespace controlled

Missing values rejected (StrictUndefined)

Filters normalize data

This ensures stable Git diffs and prevents drift.

6. Recommended Project Structure
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

7. Jinja2 Environment Configuration

Correct renderer configuration:

env = Environment(
    loader=FileSystemLoader("templates"),
    trim_blocks=True,
    lstrip_blocks=True,
    undefined=StrictUndefined
)


Meaning:

trim_blocks: removes trailing newlines

lstrip_blocks: strips indentation before blocks

StrictUndefined: no silent failures

8. Role of Python

Python performs:

Loading data (YAML/CSV/JSON)

Normalizing and validating

Merging datasets

Building the context

Choosing templates

Registering filters

Writing final configs

Templates should contain minimal logic.
Python handles complexity.

9. Purpose of Jinja2 in Network Automation

Jinja2 enables:

Consistent config generation

Reduction of manual errors

Multi-vendor support

Template reuse

Git-based change control

High-volume config generation

It converts structured data → deployable configs.
