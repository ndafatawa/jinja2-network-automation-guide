10 – Expressions in Jinja2 (Math, Logic, Comparisons, Membership)

Expressions allow you to perform simple logic or transformations inside a Jinja2 template.
They are used for generating dynamic network configuration such as VNI calculations, structured lists, conditional interface config, VLAN ranges, etc.

10.1 What Are Expressions?

Expressions are pieces of logic that evaluate to a value.

Examples:

{{ vlan.id + 100 }}
{{ intf.name | upper }}
{{ ip_list | length }}
{{ v.id in allowed_vlans }}


Expressions appear inside:

variables ({{ ... }})

conditions ({% if ... %})

loops ({% for ... in ... %})

10.2 Categories of Jinja2 Expressions

Expressions fall into:

Math

Comparisons

Boolean logic

Membership (in)

Length

String manipulation

Combined/complex expressions

Each category is shown below with network examples.

10.3 Math Expressions

Supported operators:

Operator	Meaning
+	addition
-	subtraction
*	multiplication
/	division
//	integer division
%	modulo
Example — Derive VNI from VLAN ID
vn-segment {{ vlan.id + 10000 }}

Example — Auto-generate loopback IP
ip address 10.255.{{ loopback_id }}.{{ device_id }}

Example — Create numeric BGP passwords
password 9 {{ asn * 12345 }}

10.4 Comparison Expressions

Used in if statements.

Operator	Meaning
==	equal
!=	not equal
<	less than
<=	less or equal
>	greater than
>=	greater or equal
Example — Multicast vs BGP replication
{% if fabric.replication == 'multicast' %}
  mcast-group {{ vlan.mcast_group }}
{% else %}
  ingress-replication protocol bgp
{% endif %}

Example — Shut down unused ports
{% if intf.active == false %}
  shutdown
{% endif %}

10.5 Boolean Logic Expressions
Operator	Meaning
and	both must be true
or	at least one true
not	negation
Example — Configure loopback only on leaf with IP defined
{% if role == 'leaf' and loopbacks.lo1_ip is defined %}
interface loopback1
  ip address {{ loopbacks.lo1_ip }}/32
{% endif %}

Example — Apply ACL on firewalls or border leaves
{% if role == 'firewall' or role == 'border-leaf' %}
  < ACL BLOCK >
{% endif %}

10.6 Membership Expressions (in)

Used to check list membership.

Example — Allow only permitted VLANs on trunk
{% if vlan.id in allowed_vlans %}
  switchport trunk allowed vlan add {{ vlan.id }}
{% endif %}

Example — Check for feature enablement
{% if 'ospf' in features %}
  feature ospf
{% endif %}

10.7 Length Expressions

| length returns size of a list or string.

Example — Count VLANs
# VLAN count: {{ vlans | length }}

Example — Error if no VLANs
{% if vlans | length == 0 %}
# ERROR: No VLANs defined
{% endif %}

10.8 String Expressions

Common functions:

'abc' in x → substring check

x | upper → uppercase

x | replace(' ','_') → substitute

x ~ y → concatenate

Example — Construct hostname
hostname {{ site | upper }}-{{ device_id }}

Example — Generate interface names
interface Ethernet{{ leaf_id }}/{{ port }}

10.9 Combined Expressions (Real Network Examples)
Example — BGP RR cluster-ID
cluster-id {{ fabric.asn * 2 + 1 }}

Example — Auto-generate multicast groups
mcast-group 239.1.{{ vlan.id // 256 }}.{{ vlan.id % 256 }}

Example — Detect remote leaf from hostname
{% if hostname.startswith('LEAF') and hostname[-1] | int > 20 %}
  # remote leaf
{% endif %}

10.10 Expressions Mixed With Filters
Example — Trunk VLAN formatting
switchport trunk allowed vlan {{ intf.allowed_vlans | unique | sort | join(',') }}


Pipeline:

list → unique

unique → sort

sort → join

Produce stable NX-OS output.

10.11 Best Practices

Keep expressions short.

Push complex logic to Python.

Use filters for transformations.

Avoid nested expressions.

Ensure deterministic output.

Test expressions on multiple devices.
