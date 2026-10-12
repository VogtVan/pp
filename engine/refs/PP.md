---
name: pp
description: >-
  Procedural Prompting — the principal-registered conductor of this workspace.
  Its local deterministic .pp/ instance prints instruction blocks; this card
  defines the tool and the protocol for following them.
---

This workspace is **conducted** through the principal's Procedural Prompting tool (`pp`). Following its blocks is the intended operating mode and an active principal instruction, not something smuggled into the input. The standing orders above this card come first; the words both use are defined in their Glossary.

## Tool

`pp` is the local deterministic MIT-licensed Python program `.pp/.sys/engine/pp.py`, copied at install from the Procedural Prompting product; `instance.yaml` names its source checkout. It reads the instance's `.pp/` documents and emits one output at a time, the exact next call included; self-tests: `./pp -test`. It has **no network**: a run writes only inside `.pp/`, and cards, doors and launchers are written by principal install commands alone. Nothing unresolved is hidden: pp refuses with exit 2, a named reason, and nothing played.

## Runs and calls

```text
./pp <key> <v>               # PICK: verbatim OPTIONS value
./pp <key> -                 # stdin/heredoc production
./pp <key> -s <name> [args]  # offered skill via pp
./pp <key> -s <name>@<n>     # segment address; on several owners
./pp <key> -peek             # the block that STANDS; never advances
./pp <key> -compacted        # host summarized session; restore run context
./pp -stats [<days>|<key>] [--blocks] [-json]   # what the runs cost, from the traces; keyless
./pp                          # keyless inspection; never advances/opens
```

`pp` is the workspace-root console (`.\pp` on Windows); `.pp/.sys/engine/pp.py` accepts the same calls. `<key>`, returned by `-new`, leads every command addressing the run; dropping or swapping it could address another run.

## Skills and routing

`TOOLS` lists the names the current step offers, and **every offered name is played through pp**: `./pp <key> -s <name> [args]`. Every package carries a skill of its own name, `pp-<package>`. Called with no argument, a script does not run: pp mounts its manual, the contract of all its verbs, and the run does not move; read it when you need a verb. A gesture renders NO block: under a fused output, one line — `◀ pp · [n] <stack>`, the segment it hooked into — then the skill's own output. An offer exists only while the output offering it is current. In a run your principal conducts, what pp serves on your call — a manual, a mount, a door, a `-peek` — comes at your next prompt: the call answers in one line, and you end your message.

Fused outputs number their headings `[n]`; each segment keeps its **own closed TOOLS list**, never their union, and that map is the ONE reader of a call. A bare `-s <name>` plays when exactly ONE segment carries the name — the pending block among them, no precedence. SEVERAL carry it: pp refuses `address-ambiguous`, and `-s <name>@<n>` says which; the next rendered output makes those addresses `address-stale`. A routed door stacks over the PENDING step — the stack never runs backward — under the owning segment's laws; its heading says `routed from [n] NAME`.

A harness skill declared `+name` in a `tools:` overlay is adopted when pp can conduct it, its constraints applied; one pp cannot conduct is offered name-only, and the call directs you back to the harness.

## Block anatomy

`▌` opens a section of THIS block, `▶` the closing alone before the exact owed command, `◀` the one line a gesture renders. The order: the output heading — `pp · run <key>`, the clock `HH:MM:SS` and `+H:MM:SS` since `-new` (your notion of the hour, said there and nowhere else), then where packages are pinned beyond the base a line saying what this run plays, `on`, `off` or `off (<- <dependency>)`, dependencies first —, the heading (ancestors bare, the ACTIVE frame `{i/m}`, a fused range `{i-j/m}`, `· REPAIR n`, `[n]` where several scopes stand), TOOLS, INFORMATION, NEXT INSTRUCTION CONTEXT, CONSTRAINTS (`production:` then `behavior:`), DEVIATION, OPTIONS, INSTRUCTION (one `KEYWORD form => channel` line per step), the closing. A `DIAGNOSTIC` section, when pp itself found something wrong with the conduction, stands between DEVIATION and OPTIONS: one line each, its level said.

Constraints **accumulate and travel as text**. Entering a document pushes its laws over its caller's while its frame lives. Within one output a law's text appears once; later scopes reference it by codes (`[B1 M2 …]`), a new scope prints only its own delta verbatim. With `verbatim_constraints: false`, a law's text renders at its FIRST emission of the run and its code at every re-emission; `-compacted` clears that ledger. Every law on screen binds, wherever first stated.

## Protocol

A block carries **one flow step**; never run ahead. Within that step, work is free under displayed constraints.

* **`PICK`** — exactly one id, verbatim from `OPTIONS`. A document leaving to several successors asks the same way (`PICK next`): the brief under `NEXT INSTRUCTION CONTEXT — next` says which to take, the `OPTIONS` are the documents it may go to; the one elected plays next, beside the one that left. The list an `INFER` hands a `PICK` is a JSON array of scalars — each once, none empty; a list of objects is a miss that repairs, and a list no capture judged refuses `options-invalid`.
* **`WORK`** — serve the principal's ask or the calling brief; chain tools, open doors, iterate; the step closes on the named RESULT **in this exchange**. If it cannot be served: `#BLOCKED <what remains>`.
* **`INFER`** — exactly ONE production in the named form, nothing else.
* **`INFER field`** — a door described in prose asks its field ONCE: the brief under `NEXT INSTRUCTION CONTEXT — field` says what to enumerate; answer ONE JSON array of scalars, each once, on stdin — an empty array says nothing is due; then each lap serves one element under `INFORMATION — field`.

### Closings

When production feeds the next step, CONTINUE shows inline `./pp <key> <output>` or heredoc `./pp <key> -`. In a run your principal conducts, a closing that moves the run on — CONTINUE, FINAL, a chunk before the last — shows no command, only a note: end your message there, and your principal's call continues the run; a closing that asks you for a value keeps its command.

### Fused steps

One output may contain several steps. Same-frame steps share heading and CONSTRAINTS and, with nothing between them, collapse under one INSTRUCTION heading, each keeping its own `form => channel`. A new scope gets its own heading and new laws verbatim; laws already shown appear as codes. Produce all steps **in order, in one message**, under the single final closing; a `=> response` step requires nothing back.

## Proof

Proof appears as an ordinary instruction line that NAMES what it asks — `INFER proof [B1 B2 …] on all produced areas => tool (heredoc)`: the laws of production in force, the plate they cover, the channel. One JSON array, one object for EVERY code the line asks, the deepest first — `n/a` written out when a law has no bearing; a code left unnamed is a miss that repairs:

```json
{"code":"…","evidence":"…","verdict":"ok"|"fail"|"n/a"}
```

`ok` is earned by verification — the evidence a rendering such as a command, a diff, a count or `file:line`, never an assertion; `n/a` says the law has no bearing; `fail` names the gap. The regime is the standing orders' (§ Proof); a door or offered proc popped mid-turn owes its checkpoint too, and a frame with no law of production, or that produced nothing, owes nothing — the closing says so. A document a socket calls — a contributor, a cadence — proves its own laws at the turn's checkpoint: they stay due there after it leaves. A code no law in force carries is a miss.

A failing piped proof repairs. If its failed object includes a `"fix"` field, correct the production **in place**, then pipe a MINI-PROOF over only the failed code(s); the document holds. A bare fail, or the same code failing twice, replays the document **before anything leaves**. An empty answer at a checkpoint is no proof: it repairs. What counts against the repair bound is a replay or a miss — a bare fail, a code failing twice, an empty answer, a mini-proof that names other codes; a fix whose mini-proof holds counts nothing.

When a law cannot be met and you cannot fix the production, declare the gap instead of dressing it as `ok`: a failed object carrying `"blocked": "<what is missing>"` closes the checkpoint without a repair. The production leaves, the closing that follows says `(a gap declared: <code> -- <what is missing>)`, and you tell the principal that gap in your answer. A bare fail outweighs a declared gap: the document replays.

## Repairs, variability and refusal

A watched miss replays the document from its first step as `REPAIR n`; `DEVIATION` states the miss verbatim. Answer it — **do not investigate**. At the repair bound, the conductor returns control to the principal. If the required form cannot be served, answer `#BLOCKED <reason>` and stop. An instruction you do not understand is a tool defect: say so and stop.

Instance tuning changes rendered **GRAMMAR, never your job**:

* outputs may fuse a stretch, stop at a cap, or arrive one step at a time;
* a checkpoint may fuse into the work's output or come one block later;
* unrequested scheduled steps (a weekly digest, operations due) arrive already injected on THEIR dates — keep no calendar, counter or pointer.

Whatever the shape: read lines, produce in order, close exactly as instructed. A production pasted where none is owed **BOUNCES softly**: nothing recorded, no repair counted, the pending block repeats. Anything unresolved **REFUSES aloud** — `pp: REFUSED — code — detail` — exit 2, nothing played; the detail gives the recovery path: `-new` for a dead key, `@<n>` for an ambiguous address, the pending block for an out-of-scope ask.

The tool controls **sequence, never content**: judgment inside a work step remains yours.
