import yaml, csv, os
from jinja2 import Environment, FileSystemLoader, StrictUndefined

BASE = os.path.dirname(os.path.dirname(__file__))

def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)

def load_csv(path):
    rows = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def build_context(device):
    fabric = load_yaml(f"{BASE}/data/fabric.yml")
    vlan_rows = load_csv(f"{BASE}/data/vlans.csv")

    vlans = []
    for row in vlan_rows:
        if row["device"] == device["hostname"]:
            vlans.append({
                "id": int(row["vlan_id"]),
                "name": row["name"],
                "vni": int(row["vni"]),
                "ip": row["ip"],
            })

    ctx = {
        **device,
        "fabric": fabric,
        "vlans": vlans,
        "underlay_links": fabric["underlay_links"]
    }

    return ctx

def main(host=None):
    devices = load_yaml(f"{BASE}/data/devices.yml")["devices"]

    env = Environment(
        loader=FileSystemLoader(f"{BASE}/templates"),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True
    )

    for dev in devices:
        if host and dev["hostname"] != host:
            continue

        template = f"nxos/{dev['role']}.j2"
        t = env.get_template(template)

        ctx = build_context(dev)
        output = t.render(**ctx)

        out_path = f"{BASE}/build/{dev['hostname']}.cfg"
        with open(out_path, "w") as f:
            f.write(output)

        print(f"Rendered {out_path}")

if __name__ == "__main__":
    import sys
    host = sys.argv[2] if len(sys.argv) == 3 else None
    main(host)

