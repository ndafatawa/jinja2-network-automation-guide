# **09 – Whitespace Control in Jinja2**

Whitespace control is one of the most overlooked but most important aspects of building stable and predictable network configuration templates.  
This chapter explains **what whitespace control is**, **why it matters**, and **how to use it correctly** in network automation.

---

# **9.1 Why Whitespace Matters in Network Automation**

Uncontrolled whitespace in generated configs can cause:

- random blank lines  
- misaligned configuration  
- inconsistent indentation  
- noisy Git diffs  
- configuration drift  
- failing compliance checks  

Network automation requires configs to be:

- **deterministic**  
- **clean**  
- **consistent**  
- **diff-friendly**  

Whitespace control ensures your configs are predictable across all devices.

---

# **9.2 How Jinja2 Handles Whitespace by Default (Not Good)**

By default, Jinja2:

- preserves indentation  
- keeps blank lines  
- inserts newlines around `{% block %}`  
- inserts newlines around loops  
- inserts newlines around if-statements  
- prints whitespace literally  

This **produces messy configs** full of random blank lines.

---

# **9.3 Enabling Whitespace Control in Python (`render.py`)**

A proper renderer must enable:

```python
env = Environment(
    loader=FileSystemLoader(str(TPL)),
    trim_blocks=True,
    lstrip_blocks=True,
    undefined=StrictUndefined
)
```

### What these do:

**trim_blocks=True**  
Removes the newline after a Jinja block.

**lstrip_blocks=True**  
Removes leading indentation before Jinja statements.

Together, they produce **clean**, **predictable**, **production-ready** configs.

---

# **9.4 Using “-%}” to Control Whitespace Inside Templates**

Sometimes, you must remove whitespace *inside* a template manually.

Use:

```
-%}
```

instead of:

```
%}
```

Example:

```jinja2
{% for v in vlans -%}
vlan {{ v.id }}
  name {{ v.name }}
{%- endfor %}
```

Output:

```
vlan 10
  name PROD
vlan 20
  name USERS
```

✔ No blank lines  
✔ Perfect diff output  

---

# **9.5 Clean Loop Example (Before vs After)**

### **Without whitespace control**

Template:

```jinja2
{% for v in vlans %}
vlan {{ v.id }}
  name {{ v.name }}
{% endfor %}
```

Output:

```
vlan 10
  name PROD

vlan 20
  name USERS
```

Blank line appears between entries.

### **With whitespace control**

```jinja2
{% for v in vlans -%}
vlan {{ v.id }}
  name {{ v.name }}
{%- endfor %}
```

Output:

```
vlan 10
  name PROD
vlan 20
  name USERS
```

Perfect, stable formatting.

---

# **9.6 Clean Conditional Blocks**

Problem:

```jinja2
{% if vrf.l3vni %}
router bgp 65001
  address-family l2vpn evpn
{% endif %}
```

If the condition is false, a **blank line** appears.

Solution:

```jinja2
{% if vrf.l3vni -%}
router bgp 65001
  address-family l2vpn evpn
{%- endif %}
```

If condition is false → **no output at all**.

---

# **9.7 Avoiding Blank Lines at Start/End of Files**

Wrap inheritance tightly:

```jinja2
{%- extends 'nxos/device_base.j2' -%}
```

or:

```jinja2
{%- block base -%}
...
{%- endblock %}
```

This prevents leading/trailing blank lines in generated configs.

---

# **9.8 Whitespace Control for Includes**

Default include:

```jinja2
{% include 'nxos/underlay_intf.j2' %}
```

Often creates extra blank lines.

Correct:

```jinja2
{%- include 'nxos/underlay_intf.j2' -%}
```

✔ Removes whitespace before and after include  
✔ Produces consistent output  

---

# **9.9 Best Practices for Whitespace Control**

1. **Always enable** `trim_blocks` and `lstrip_blocks` in Python.  
2. Use `-%}` in loops, conditionals, blocks, and includes.  
3. Avoid trailing spaces in templates.  
4. Keep indentation consistent.  
5. Render multiple sample configs to verify consistency.  
6. Maintain deterministic output (important for Git).  

---

# **9.10 Real Project Examples**

### **VXLAN L2VNI Members**

```jinja2
{% for v in l2_vnis -%}
member vni {{ v.vni }}
  mcast-group {{ v.mcast_group }}
{%- endfor %}
```

---

### **ACL Entries**

```jinja2
{% for rule in rules -%}
{{ rule.action }} {{ rule.src }} {{ rule.dst }} eq {{ rule.port }}
{%- endfor %}
```

---

### **BGP Neighbors**

```jinja2
router bgp {{ asn }}
{% for n in neighbors -%}
  neighbor {{ n.ip }} remote-as {{ n.asn }}
{%- endfor %}
```

---

# **9.11 Common Mistakes (Avoid These)**

| Mistake | Result |
|--------|--------|
| Missing `-%}` | Extra blank lines everywhere |
| No `trim_blocks` / `lstrip_blocks` | Messy spacing |
| Logic-heavy templates | Hard to maintain |
| Using tabs instead of spaces | Misaligned configs |
| Blank lines between includes | Unstable Git diffs |

---

Whitespace control is not optional — it is essential for clean, predictable, production-ready network automation templates.

