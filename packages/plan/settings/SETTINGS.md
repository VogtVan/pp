---
name: SETTINGS
kind: fragment
package: plan
description: >-
  The plan package's own settings -- the principal's involvement in the
  Choices of the implementation. Composed into the instance's SETTINGS under
  the `plan_` prefix, read by the plan's procs and its script.
plan_implementation_care: asked
plan_implementation_control: architecture | contracts
plan_serve_budget: 40000
types: |
  plan_implementation_care  one_of[none|traced|told|asked|total]
  plan_implementation_control  piped[architecture|contracts|naming|data|flow]
  plan_serve_budget  free
---

## Plan — the principal's involvement in the implementation

The plan's keys carry the `plan_` prefix; the PLAN proc and the templates of its levels
read them. The principal's GO always prevails over these settings.

- `plan_implementation_care` — how much the principal takes part in the choices of the
  implementation (the Choices a framing wrote to the node).

  | Value | Effect |
  |---|---|
  | `none` | the agent decides, nothing written |
  | `traced` | written to the plan alone |
  | `told` | said when the agent reports, played without waiting |
  | `asked` | PROPOSED before coding, in the watched sectors |
  | `total` | each choice waits its GO |

- `plan_implementation_control` — the sectors `asked` watches, separated by `|`: a choice
  in a named sector is PROPOSED before coding; outside them the agent decides and writes it
  down.

  | Sector | What it covers |
  |---|---|
  | `architecture` | the shape of the solution — components, boundaries, the mechanism chosen over the others |
  | `contracts` | what the pieces promise each other — interfaces, signatures, formats, keys and their words |
  | `naming` | the names that will be read — slugs, keys, identifiers, files |
  | `data` | what is kept and how — schemas, records, their fields and the rules they keep |
  | `flow` | the order things happen in — sequences, gates, what waits for what |

## Plan — the weight of a serve row

- `plan_serve_budget` — the number of characters a file may weigh to be served WHOLE by a
  row (`40000` by default). `pp-plan serve` refuses `serve-heavy`, and writes nothing, when a
  token without a range names a heavier file, read in the plan's material; a range on the
  file's function or section tags serves it. `0` lifts the limit.
