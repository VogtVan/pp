---
name: SETTINGS
kind: fragment
package: plan
description: >-
  The plan package's own settings -- the operator's involvement in the
  implementation arbitrations. Composed into the instance's SETTINGS under
  the `plan_` prefix, read by the plan's procs.
plan_implementation_care: asked
plan_implementation_control: architecture | contracts
types: |
  plan_implementation_care  one_of[none|traced|told|asked|total]
  plan_implementation_control  piped[architecture|contracts|naming|data|flow]
---

## Plan — the operator's involvement in the implementation

The plan's keys wear the `plan_` prefix; the PLAN, PHASE and BATCH procs
read them. The operator's GO always supersedes these settings.

- `plan_implementation_care` — the operator's involvement in the
  implementation arbitrations (the choices a framing wrote to the node).

  | Value | Effect |
  |---|---|
  | `none` | the agent decides, nothing written |
  | `traced` | written to the plan alone |
  | `told` | said at the restitution, played without waiting |
  | `asked` | PROPOSED before coding on the controlled sectors |
  | `total` | each arbitration waits its GO |

- `plan_implementation_control` — the sectors `asked` watches, piped: an
  arbitration in a named sector is PROPOSED before coding; outside them the
  agent decides and traces.

  | Sector | What it covers |
  |---|---|
  | `architecture` | the shape of the solution — components, boundaries, the mechanism chosen over its alternatives |
  | `contracts` | what the pieces promise each other — interfaces, signatures, formats, keys and their vocabulary |
  | `naming` | the names that will be read — slugs, keys, identifiers, files |
  | `data` | what persists and how — schemas, records, their fields and invariants |
  | `flow` | the order things happen in — sequences, gates, what waits on what |
