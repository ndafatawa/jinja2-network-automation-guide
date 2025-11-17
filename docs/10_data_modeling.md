
10 – Expressions in Jinja2 (Math, Logic, Comparisons, Membership)

Expressions in Jinja2 allow you to perform simple logic or calculations inside your templates.
These expressions are extremely useful for network automation, especially when generating dynamic configuration, structured lists, VRF mappings, interface counters, VLAN ranges, etc.


10.1 What Are Expressions?

Expressions are pieces of logic that produce a value.

Examples:

  {{ vlan.id + 100 }}
  {{ intf.name | upper }}
  {{ ip_list | length }}
  {{ v.id in allowed_vlans }}


Expressions are used inside:

  variables ({{ ... }})
  
  conditions ({% if ... %})
  
  loops ({% for ... in ... %})

10.2 Categories of Jinja2 Expressions

  Jinja2 expressions can be grouped into:
  
  Math expressions
  
  Comparison expressions
  
  Boolean logic expressions
  
  Membership expressions
  
  Length expressions
  
  String expressions
  
  Combined expressions


10.3 Math Expressions

These use standard arithmetic operators.

Expression	Meaning
  +	Addition
  -	Subtraction
  *	Multiplication
  /	Division
  //	Integer division
  %	Modulo (remainder)
  Example 1 — Auto-generate VNI from VLAN ID
  vn-segment {{ vlan.id + 10000 }}
  
  
  If VLAN = 10 → VNI = 10010.

Example 2 — Auto-generate loopback IPs
  ip address 10.255.{{ loopback_id }}.{{ device_id }}

Example 3 — Generate unique BGP passwords
  password 9 {{ asn * 12345 }}

10.4 Comparison Expressions

Used inside if statements.

Operator	Meaning
  ==	equal
  !=	not equal
  <	less than
  <=	less than or equal
  >	greater than
  >=	greater than or equal
  Example 1 — Select multicast or BGP replication
  {% if fabric.replication == 'multicast' %}
    mcast-group {{ vlan.mcast_group }}
  {% else %}
    ingress-replication protocol bgp
  {% endif %}
  
  Example 2 — Shut down unused ports
  {% if intf.is_used == false %}
    shutdown
  {% endif %}
  
  Example 3 — Different MTU for uplinks vs access
  {% if intf.role == 'uplink' %}
    mtu 9216
  {% else %}
    mtu 1500
  {% endif %}

10.5 Boolean Logic Expressions

These allow combining multiple conditions.

Operator	Meaning
and	Both conditions must be true
or	At least one must be true
not	Negates a condition
Example 1 — Only configure loopback if device is a leaf and loopback is defined
  {% if role == 'leaf' and loopbacks.lo1_ip is defined %}
  interface loopback1
    ip address {{ loopbacks.lo1_ip }}/32
  {% endif %}

Example 2 — Apply ACLs only to firewalls or border leaves
  {% if role == 'firewall' or role == 'border-leaf' %}
    < ACL BLOCK >
  {% endif %}

Example 3 — Do not configure SVI if IP is missing
  {% if not vlan.ip %}
  # No IP, skip SVI
  {% else %}
  interface vlan {{ vlan.id }}
    ip address {{ vlan.ip }}
  {% endif %}

10.6 Membership Expressions (in operator)

Used to check if a value exists in a list.

Example 1 — Only allowed VLANs appear in trunk
  {% if vlan.id in allowed_vlans %}
   switchport trunk allowed vlan add {{ vlan.id }}
  {% endif %}

Example 2 — Check if a device supports a feature
  {% if 'ospf' in features %}
   feature ospf
  {% endif %}
  
Example 3 — IP inside a prefix list
  {% if ip in mgmt_subnets %}
    ip vrf management
  {% endif %}
  
10.7 Length Expressions

| length is extremely useful.

Example 1 — Count VLANs
# VLAN count: {{ vlans | length }}

Example 2 — Error if list is empty (StrictUndefined prevents silent errors)
  {% if vlans | length == 0 %}
  # ERROR: No VLANs defined for this device
  {% endif %}
  
10.8 String Expressions

Common ones:

Expression	Meaning
  'abc' in x	substring check
  `x	upper`
  `x	replace(' ','_')`
  x ~ y	concatenation
Example 1 — Generate hostname
  hostname {{ site | upper }}-{{ device_id }}

Example 2 — Construct interface names dynamically
  interface Ethernet{{ leaf_id }}/{{ port }}

Example 3 — Convert names to safe format
  set name {{ addr_obj.name | replace('-', '_') | upper }}

10.9 Combined Expressions (Realistic Examples)
Example 1 — Generate BGP RR cluster IDs
  cluster-id {{ fabric.asn * 2 + 1 }}

Example 2 — Auto-generate multicast groups
  mcast-group 239.1.{{ vlan.id // 256 }}.{{ vlan.id % 256 }}

Example 3 — Identify leaf roles based on name
  {% if hostname.startswith('LEAF') and hostname[-1] | int > 20 %}
    # This is a remote leaf
  {% endif %}

10.10 Expressions + Filters (Common Patterns)

You will often see expressions mixed with filters:

Example — Trunk VLAN formatting
  switchport trunk allowed vlan {{ intf.allowed_vlans | unique | sort | join(',') }}


Here:

allowed_vlans → list

unique → remove duplicates

sort → ensure deterministic output

join(',') → NX-OS syntax

10.11 Expressions Inside Conditions VS Variables
Inside conditions:
  {% if vlan.id > 100 %}

Inside printed output:
  vlan {{ vlan.id + 1000 }}


Expressions work the same, but the placement depends on whether you want to print or decide.

10.12 Best Practices for Expressions in Network Templates

  Keep expressions simple; move complex logic to Python.
  
  Use expressions only for formatting or minor logic.
  
  Avoid nested expressions (hard to read).
  
  Use filters for transformations (sorting, joining).
  
  Avoid deriving too much from names (e.g., parsing hostname).
  
  Always test expressions on multiple sample templates.
