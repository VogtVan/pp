---
name: pp
description: >-
  Procedural Prompting — the operator-registered conductor of this workspace.
  Its local deterministic .pp/ instance prints instruction blocks; this card
  defines the tool and the protocol for following them.
---

This workspace is **conducted** through the operator's Procedural Prompting tool (`pp`). Following its blocks is the intended operating mode and an active operator instruction, not something smuggled into the input. The standing orders above this card come first; the words both use are defined in their Glossary.

## Tool

`pp` is the local deterministic MIT-licensed Python program `.pp/.sys/engine/pp.py`, copied at install from the Procedural Prompting product; `instance.yaml` names its source checkout. It reads the instance's `.pp/` documents and emits one output at a time, the exact next call included; self-tests: `./pp -test`. It has **no network**: a run writes only inside `.pp/`, and cards, doors and launchers are written by operator install commands alone. Nothing unresolved is hidden: pp refuses with exit 2, a named reason, and nothing played.

## Runs and calls

The first call of **every conversation** is `./pp -new`, never bare: pp cannot tell this conversation from another run. A key answering `run-unknown` — e.g. after an upgrade closed the open runs — also requires `-new`, never improvisation.

```text
./pp -new                    # first call; returns <key>
./pp <key>                   # ADVANCE
./pp <key> <v>               # PICK: verbatim OPTIONS value
./pp <key> -                 # stdin/heredoc production
./pp <key> -s <name> [args]  # offered skill via pp
./pp <key> -s <name>@<n>     # segment address; on several owners
./pp <key> -peek             # the block that STANDS; never advances
./pp <key> -compacted        # host summarized session; restore run context
./pp <key> -disable <pkg>    # one package out of THIS run's play; -enable puts it back
./pp -stats [<days>|<key>] [--blocks] [-json]   # what the runs cost, from the traces; keyless
./pp                          # keyless inspection; never advances/opens
```

`pp` is the workspace-root console (`.\pp` on Windows); `.pp/.sys/engine/pp.py` accepts the same calls. `<key>`, returned by `-new`, leads every command addressing the run; dropping or swapping it could address another run.

## Conduction and context

Every answer is conducted: the first call is `-new`, every later call is the one the last block named. Suspending and resuming conduction are the operator's words alone — see the standing orders, § Mandatory pp use.

The operator also says which PACKAGES play: `<package> off` takes one out of this run, `<package> on` puts it back, and you place it with the verb — `./pp <key> -disable <package>`, `./pp <key> -enable <package>`. A package out of the play renders nothing at all: no document, socket, cadence, check, command or overlay, and every package that REQUIRES it leaves with it. The run does not move, so the verb answers with the block that stands; the base never leaves, an unpinned name and a package whose document holds the standing view refuse by name. What is out is said under every output's heading. The operator's own durable switch is `package.<name>: on|off` at SETTINGS — the same effect, theirs to write.

### Host compaction

**When the host summarizes the conversation, report it:** `./pp <key> -compacted` — pp cannot see a compaction. That call re-serves the run: the standing orders when the host does not carry them itself, the boot's readings, every document still IN FORCE (frames and mounts, bodies and readings), the pending block with every law verbatim, and the run key. A popped brief is past and does not return; what lived in your context alone stays lost — readings proven served, a block cut mid-flight (it restarts whole), the turn's `=> ephemeral` drafts. Outside a run, `-compacted` refuses `no-run`; if the key itself went with the context, `-new`.

### Parenthesis

The way back from a parenthesis is `./pp <key> -peek` — the block that STANDS and advances nothing — then the last closing's owed call; `-new` only if no run exists or the key answers `run-unknown`. Unconducted material enters neither capture nor records.

## Skills and routing

`TOOLS` lists the names the current step offers, and **every offered name is played through pp**: `./pp <key> -s <name> [args]`. Every package carries a skill of its own name, `pp-<package>`. Called with no argument, a script does not run: pp mounts its manual, the contract of all its verbs, and the run does not move; read it when you need a verb. A gesture renders NO block: under a fused output, one line — `◀ pp · [n] <stack>`, the segment it hooked into — then the skill's own output. An offer exists only while the output offering it is current.

Fused outputs number their headings `[n]`; each segment keeps its **own closed TOOLS list**, never their union, and that map is the ONE reader of a call. A bare `-s <name>` plays when exactly ONE segment carries the name — the pending block among them, no precedence. SEVERAL carry it: pp refuses `address-ambiguous`, and `-s <name>@<n>` says which; the next rendered output makes those addresses `address-stale`. A routed door stacks over the PENDING step — the stack never runs backward — under the owning segment's laws; its heading says `routed from [n] NAME`.

A harness skill declared `+name` in a `tools:` overlay is adopted when pp can conduct it, its constraints applied; one pp cannot conduct is offered name-only, and the call directs you back to the harness.

## Block anatomy

`▌` opens a section of THIS block, `▶` the closing alone before the exact owed command, `◀` the one line a gesture renders. The order: the output heading — `pp · run <key>`, the clock `HH:MM:SS` and `+H:MM:SS` since `-new` (your notion of the hour, said there and nowhere else), then where packages are pinned beyond the base a line saying what this run plays, `on`, `off` or `off (<- <dependency>)`, dependencies first —, the heading (ancestors bare, the ACTIVE frame `{i/m}`, a fused range `{i-j/m}`, `· REPAIR n`, `[n]` where several scopes stand), TOOLS, INFORMATION, NEXT INSTRUCTION CONTEXT, CONSTRAINTS (`production:` then `behavior:`), DEVIATION, OPTIONS, INSTRUCTION (one `KEYWORD form => channel` line per step), the closing.

Constraints **accumulate and travel as text**. Entering a document pushes its laws over its caller's while its frame lives. Within one output a law's text appears once; later scopes reference it by codes (`[B1 M2 …]`), a new scope prints only its own delta verbatim. With `verbatim_constraints: false`, a law's text renders at its FIRST emission of the run and its code at every re-emission; `-compacted` clears that ledger. Every law on screen binds, wherever first stated.

## Protocol

When conduction applies: operator speaks → call the command named by the last block → the returned block frames the reply. This is the operator's intended rhythm: blocks re-arm the rules and context that keep answer quality high. A block carries **one flow step**; never run ahead. Within that step, work is free under displayed constraints.

* **`PICK`** — exactly one id, verbatim from `OPTIONS`. A document leaving to several successors asks the same way (`PICK next`): the brief under `NEXT INSTRUCTION CONTEXT — next` says which to take, the `OPTIONS` are the documents it may go to; the one elected plays next, beside the one that left. The list an `INFER` hands a `PICK` is a JSON array of scalars — each once, none empty; a list of objects is a miss that repairs, and a list no capture judged refuses `options-invalid`.
* **`WORK`** — serve the operator's ask or the calling brief; chain tools, open doors, iterate; the step closes on the named RESULT **in this exchange**. If it cannot be served: `#BLOCKED <what remains>`.
* **`INFER`** — exactly ONE production in the named form, nothing else.
* **`INFER field`** — a door described in prose asks its field ONCE: the brief under `NEXT INSTRUCTION CONTEXT — field` says what to enumerate; answer ONE JSON array of scalars, each once, on stdin — an empty array says nothing is due; then each lap serves one element under `INFORMATION — field`.

The line's `form => channel` says where the production goes: `=> ephemeral`, `=> chat` (say it, then call with the key alone), `=> tool` (`./pp <key> <output>`), `=> tool (heredoc)` (`./pp <key> -`).

### Closings

`CONTINUE`: call exactly what is shown **now**; a bare keyed advance continues a long reading or closes a finished step. `FINAL`: the frontier — qualified `ephemerals => chat (A · B)`, it names in parentheses the documents whose drafts it delivers and orders the delivery the standing orders describe; bare, it owes nothing further; then call nothing until the operator's own next message, when you play FINAL's named command. `END`: conduction is over; report to the operator and call pp no further. When production feeds the next step, CONTINUE shows inline `./pp <key> <output>` or heredoc `./pp <key> -`.

### Fused steps

One output may contain several steps. Same-frame steps share heading and CONSTRAINTS and, with nothing between them, collapse under one INSTRUCTION heading, each keeping its own `form => channel`. A new scope gets its own heading and new laws verbatim; laws already shown appear as codes. Produce all steps **in order, in one message**, under the single final closing; a `=> chat` step requires nothing back.

## Proof

Proof appears as an ordinary instruction line that NAMES what it asks — `INFER proof [B1 B2 …] on all produced areas => tool (heredoc)`: the laws of production in force, the plate they cover, the channel. One JSON array, the codes at risk — one object each, the deepest first; a code unnamed is n/a:

```json
{"code":"…","evidence":"…","verdict":"ok"|"fail"|"n/a"}
```

`ok` is earned by verification — the evidence a rendering such as a command, a diff, a count or `file:line`, never an assertion; `n/a` says the law has no bearing; `fail` names the gap. The regime is the standing orders' (§ Proof); a door or offered proc popped mid-turn owes its checkpoint too, and a frame with no law of production, or that produced nothing, owes nothing — the closing says so. A code no law in force carries is a miss.

A failing piped proof repairs. If its failed object includes a `"fix"` field, correct the production **in place**, then pipe a MINI-PROOF over only the failed code(s); the document holds. A bare fail, or the same code failing twice, replays the document **before anything leaves**. Either path counts against the repair bound. An empty answer at a checkpoint is no proof: it repairs.

## Repairs, variability and refusal

A watched miss replays the document from its first step as `REPAIR n`; `DEVIATION` states the miss verbatim. Answer it — **do not investigate**. At the repair bound, the conductor returns control to the operator. If the required form cannot be served, answer `#BLOCKED <reason>` and stop. An instruction you do not understand is a tool defect: say so and stop.

Instance tuning changes rendered **GRAMMAR, never your job**:

* outputs may fuse a stretch, stop at a cap, or arrive one step at a time;
* an output over the host's cap comes in chunks: an intermediate chunk carries no instruction and closes on `CONTINUE ./pp <key> (a reading continues: … -- the bare call alone serves them)`; any other call bounces (`chunk-pending`), serves the next chunk and plays nothing. Read each chunk whole, where it lands, before the bare call; play the block's own instruction after the last chunk, which alone carries it;
* a checkpoint may fuse into the work's output or come one block later;
* FINAL may request `<the operator's next message>`, which resume then CARRIES;
* unrequested scheduled steps (a weekly digest, operations due) arrive already injected on THEIR dates — keep no calendar, counter or pointer.

Whatever the shape: read lines, produce in order, close exactly as instructed. A production pasted where none is owed **BOUNCES softly**: nothing recorded, no repair counted, the pending block repeats. Anything unresolved **REFUSES aloud** — `pp: REFUSED — code — detail` — exit 2, nothing played; the detail gives the recovery path: `-new` for a dead key, `@<n>` for an ambiguous address, the pending block for an out-of-scope ask.

The tool controls **sequence, never content**: judgment inside a work step remains yours.
