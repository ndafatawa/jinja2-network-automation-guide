5. Deterministic Output

Network automation must be stable and predictable.
Deterministic config ensures:

Clean Git diffs

Reproducible output

No randomness

No missing variables

Achieved using:

unique | sort | join to make lists stable

Whitespace trimming

StrictUndefined to reject missing values

Minimal logic inside templates

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
│   │   ├

Voice chat ended
