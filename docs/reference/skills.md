# Skills and the author's hall

This file covers how an offered skill plays through pp, how its output and scope resolve, how a `+name` is adopted, and the author's hall of the `authoring` package.

- [Offered skills — one rule, and adoption](#offered-skills--one-rule-and-adoption)
- [The author's hall](#the-authors-hall)

## Offered skills — one rule, and adoption

**Every offered name is played through pp** (`./pp <key> -s <name>`). The invocation IS a `CALL`:

- a frame opens on the skill's contract;
- its `constraints:` enter force, on top of the turn's, gone when the frame closes;
- its body is served.

What plays inside the frame is the contract's own affair:

| The contract has | What plays |
|---|---|
| a **`proc:`** | the declared flow, exactly as any procedure |
| **no `proc:`** | the implicit flow: one `WORK`, the served body as its brief. The work is free (your judgment, your harness's tools), and the keyed call (`./pp <key>`) closes the step — the caller's flow resumes. |
| a **script** beside the contract | the deterministic step runs, the gesture's block carrying the skill's own constraints |

### What a script prints

What the script prints leaves through the seam of every output:

- under the host's cap, exactly as written;
- over it, in chunks, each opening on the output's heading, the rest waiting at the run. The bare call serves the rest, any other call bounces (`chunk-pending`), and the run does not move.

A `::mount` printed by the script joins the same output: one cut, one rest.

The trace weighs it: the `gesture` line carries the `chars` and `tokens` of the text, then `cut` and one `chunk` per bare call.

An output with no run key (`-stats`, a package's command, `doctor`) has no run to hold a rest and is never cut.

#### Called bare

Called BARE — no argument — the script does not run. Its contract is its **manual**: the `SKILL.md` the skill's NAME addresses, wherever its package lives (the instance or its vendor).

That body alone is MOUNTED into the current view through the one reader. It is cut at the host's cap, proven by its hash, recorded in the ledger (`-stats --blocks`, origin `mount`), and swept with the exchange. The standing block renders under it, and the run is untouched.

### The scope resolves pending first, then the output's segments

A fused output numbers its headings (`[n]`), and each segment keeps its OWN closed list — never their union.

A bare `-s <name>` that the pending block does not offer routes to the ONE segment of the current output whose own list carries the name. The gesture plays AS that step's: its block is re-shown under its snapshotted laws, and the trace is attributed (`gesture`/`routed`, with `segment` and `frame`).

#### Several owners, stale addresses

Several owners refuse (`address-ambiguous`), and `-s <name>@<n>` settles it — the only time the number is owed. A later output retires the addresses (`address-stale`).

#### Routed doors

A routed `proc:` door still stacks over the pending step; the stack never runs backward. The door inherits the owning segment's laws, and its entry heading notes `routed from [n] NAME`.

A door routed from a FREE step (the turn's WORK) takes that step with it. When the door's frame falls, the step is consumed by the door's production: one production for the ask, never two (traced `consumed-by-door`).

What rides a door's call as an argument (`-s ROUTE 7`) is ignored. This is said on the first line of the tool return (`pp: argument ignored: 7 -- …`) and traced `door-argument`. A door opens on its own documents and reads nothing from the call.

#### Offered by no segment

When no segment offers the name, the pending block answers and nothing plays.

### Adoption — the offer is the consent

A `+name` in a `tools:` may resolve nowhere in the instance: nothing it composes owns the name, a switched-off package included. It is then looked up in two places, the nearer first:

1. the workspace's harness skill homes (`.claude/skills/` · `.agents/skills/` · `.cursor/skills/`);
2. for an instance installed under another one whose machine it borrows (an agent under its house), the house's own `procs/<name>.md`.

#### A proc of the house

A proc of the house is written for the instances under it. Adopted, it plays as one of theirs: its laws, its readings, its `@SETTINGS` keys and its CALLs resolve in the instance that offered it. Its `attach:` or `mount:` never plays there: the offer opens a door, it plugs nothing into the instance's turn.

A `+name` written in a document that is not an overlay (a document mounted at a socket, a node of a plan) offers `name` the same way.

A name the instance carries itself is never looked up in the house. `-build` warns `house-shadowed` when that name is a proc of the house no pinned package carries. The house's root, its overlays and the procs nobody offers stay the house's.

The catalog says where each adopted contract came from, `(harness)` or `(house)`.

#### What adoption grants

- A contract pp can conduct — a readable front matter and a `description:` — is **adopted**: full entry in the catalog, its constraints in the registry, played like any skill of the instance.
- One it cannot conduct stays a name-only offer, indifferent to pp, and `-build` warns (`offered-not-conductible`) with what it lacks.
- An **unoffered** copy in a harness directory stays invisible: pp never sweeps those homes. Offering is what grants the read.

## The author's hall

With the `authoring` package pinned, the hall `AUTHOR` is offered at the boot and at every turn.

The agent opens it with `./pp <key> -open AUTHOR`. It is a SPACE (see [`OPEN <doc>`](language.md#open-doc)): your next messages stay in it until `./pp <key> -close`.

The hall serves the catalogue of the patterns, shows its crafts in one table, and opens the craft your ask needs, a space of its own:

- `AUTHOR-MEMBER`
- `AUTHOR-RULES`
- `AUTHOR-OFFERS`
- `AUTHOR-MIGRATE`
- `AUTHOR-DESIGN`

A craft sketches every document in the agent's words and writes it with `pp-authoring` on your word alone: your word is the gate, in the hall's own law. One craft is open at a time.

The package's signals `member-bare` and `offers-idle` point to `AUTHOR`.

## See also

- [front-matter.md](front-matter.md) — the `tools:` key, overlays and your own procedures.
- [language.md](language.md) — `CALL`, `WORK`, `OPEN <doc>` and the other keywords.
- [agent-face.md](agent-face.md) — the `./pp <key> -s <name>` and `-open` commands.
- [block.md](block.md) — the block, its channels and the delivery.
