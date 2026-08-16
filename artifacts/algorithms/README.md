# CS 499 Milestone Three: Algorithms and Data Structures

## Artifact

This submission enhances a small Cisco IOS Loopback0 automation artifact. The
`original` directory preserves the initial hard-coded Paramiko script and
Ansible playbook. The `enhanced` directory contains the refined Python
implementation.

## Enhancement highlights

- Dataclasses model devices and configuration tasks.
- A dictionary provides constant-time device lookup.
- Sets detect duplicate task identifiers and interface assignments.
- Sorted IPv4 intervals detect overlapping address space in O(n log n) time.
- An adjacency list, indegree dictionary, and min-heap implement deterministic
  topological sorting in O(V + E) time.
- Immutable command and rollback plans separate validation from execution.
- JSON input supports multiple devices and reusable tasks.
- Dry-run mode is the safe default.
- Apply mode reads credentials from environment variables and rejects unknown
  SSH host keys.
- Structured JSON reports make results auditable.
- Unit tests exercise validation, conflicts, ordering, cycles, and rollback.

## Run the tests

From the `enhanced` directory:

```bash
python3 -m unittest discover -s tests -v
```

## Run a safe dry run

From the `enhanced` directory:

```bash
python3 run.py \
  --inventory data/inventory.json \
  --requests data/requests.json \
  --report automation-report.json
```

The sample inventory uses the documentation-only `192.0.2.0/24` range and will
not contact a real router in dry-run mode.

## Apply to authorized equipment

Install the dependency, add the target router SSH host keys to `known_hosts`,
and set credentials without storing them in source:

```bash
python3 -m pip install -r ../requirements.txt
export NETWORK_USERNAME="authorized-user"
export NETWORK_PASSWORD="authorized-password"
python3 run.py \
  --inventory data/inventory.json \
  --requests data/requests.json \
  --report automation-report.json \
  --apply
```

Only use `--apply` on equipment you are authorized to configure. Review the
dry-run report and maintain an out-of-band recovery path before applying any
change.
