# **10 – Expressions in Jinja2 (Math, Logic, Comparisons, Membership)**

Expressions allow you to perform simple logic, arithmetic, comparisons, and string manipulation inside a Jinja2 template.  
They are extremely useful in network automation for generating dynamic values such as VNIs, route-targets, loopback IPs, VLAN lists, ACL rules, and conditional configuration.

Expressions appear inside:

- **Variables**: `{{ ... }}`
- **If-statements**: `{% if ... %}`
- **Loops**: `{% for ... %}`

---

# **10.1 What Are Expressions?**

Expressions *evaluate to a value*.

Examples:

```jinja2
{{ vlan.id + 100 }}
{{ intf.name | upper }}
{{ ip_list | length }}
{{ v.id in allowed_vlans }}
```

Expressions provide intelligence inside templates without becoming real programming logic.

---

# **10.2 Categories of Expressions**

Jinja2 supports several expression types:

- Math
- Comparisons
- Boolean logic
- Membership (`in`)
- Length
- String operations
- Combined/complex expressions

Each category has real network examples below.

---

# **10.3 Math Expressions**

Supported operators:

| Operator | Meaning |
|----------|---------|
| `+` | addition |
| `-` | subtraction |
| `*` | multiplication |
| `/` | division |
| `//` | integer division |
| `%` | modulo |

### **Example — Derive VNI automatically from VLAN ID**

```jinja2
vn-segment {{ vlan.id + 10000 }}
```

### **Example — Auto-generate loopback IP**

```jinja2
ip address 10.255.{{ loopback_id }}.{{ device_id }}
```

### **Example — Generate numeric BGP passwords**

```jinja2
password 9 {{ asn * 12345 }}
```

---

# **10.4 Comparison Expressions**

Used heavily in `{% if %}` blocks.

| Operator | Meaning |
|----------|---------|
| `==` | equal |
| `!=` | not equal |
| `<` | less than |
| `<=` | less or equal |
| `>` | greater than |
| `>=` | greater or equal |

### **Example — Replication mode decision**

```jinja2
{% if fabric.replication == 'multicast' %}
  mcast-group {{ vlan.mcast_group }}
{% else %}
  ingress-replication protocol bgp
{% endif %}
```

### **Example — Shutdown inactive ports**

```jinja2
{% if intf.active == false %}
  shutdown
{% endif %}
```

---

# **10.5 Boolean Logic**

| Operator | Meaning |
|----------|---------|
| `and` | both true |
| `or` | at least one true |
| `not` | negation |

### **Example — Configure loopback only on leaf & with IP defined**

```jinja2
{% if role == 'leaf' and loopbacks.lo1_ip is defined %}
interface loopback1
  ip address {{ loopbacks.lo1_ip }}/32
{% endif %}
```

### **Example — Apply ACL on firewalls or border leaves**

```jinja2
{% if role == 'firewall' or role == 'border-leaf' %}
  < ACL BLOCK >
{% endif %}
```

---

# **10.6 Membership Expressions (`in`)**

Used to check if an item exists in a list.

### **Example — Allow only permitted VLANs on trunk**

```jinja2
{% if vlan.id in allowed_vlans %}
  switchport trunk allowed vlan add {{ vlan.id }}
{% endif %}
```

### **Example — Enable feature only if listed**

```jinja2
{% if 'ospf' in features %}
  feature ospf
{% endif %}
```

---

# **10.7 Length Expressions**

Use `|length` to count items.

### **Example — Count VLANs**

```jinja2
# VLAN count: {{ vlans | length }}
```

### **Example — Detect missing VLAN definitions**

```jinja2
{% if vlans | length == 0 %}
# ERROR: No VLANs defined
{% endif %}
```

---

# **10.8 String Expressions**

Common string tools:

- `'abc' in x` → substring check  
- `x | upper` → uppercase  
- `x | replace(' ','_')` → substitution  
- `x ~ y` → concatenation  

### **Example — Construct hostname**

```jinja2
hostname {{ site | upper }}-{{ device_id }}
```

### **Example — Generate interface names**

```jinja2
interface Ethernet{{ leaf_id }}/{{ port }}
```

---

# **10.9 Combined Expressions (Real Network Examples)**

### **Example — BGP RR cluster-ID**

```jinja2
cluster-id {{ fabric.asn * 2 + 1 }}
```

### **Example — Auto-generate multicast groups**

```jinja2
mcast-group 239.1.{{ vlan.id // 256 }}.{{ vlan.id % 256 }}
```

### **Example — Detect remote leafs from hostname**

```jinja2
{% if hostname.startswith('LEAF') and hostname[-1] | int > 20 %}
# remote leaf
{% endif %}
```

---

# **10.10 Expressions Mixed With Filters**

Filters + expressions = extremely powerful.

### **Example — Clean trunk VLAN formatting**

```jinja2
switchport trunk allowed vlan {{ intf.allowed_vlans | unique | sort | join(',') }}
```

Pipeline:

```
list → unique → sort → join → printed
```

Deterministic NX-OS output every time.

---

# **10.11 Best Practices for Expressions**

- Keep expressions short.
- Move complex logic to Python, not templates.
- Use filters for formatting.
- Avoid heavy nested expressions.
- Always ensure output is deterministic.
- Test expressions across multiple device types.

---

Expressions give your templates intelligence without making them complex.  
Used correctly, they allow simple YAML/CSV data to generate highly dynamic network configurations.

