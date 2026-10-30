---
name: pp
description: >-
  Procedural Prompting — the principal-registered conductor of this workspace.
  Its local deterministic .pp/ instance prints instruction blocks; this card is
  the manual of its calls, with an example for every case.
---

# `pp` — the conductor's console

`pp` is the local deterministic program `.pp/.sys/engine/pp.py`, played by the console
`./pp` at the workspace root (`.\pp` on Windows). It has no network and writes only
inside `.pp/`. How to read a block and what to produce are in the standing orders; this
card gives the calls.

## Commands

`<key>` is the six characters that name the run, shown in the heading of every output.
It leads every call that addresses the run: never drop it, never swap it for another.

| Form | Effect |
|---|---|
| `./pp <key> <value>` | Hand a production on the call: a `PICK` choice, a production `=> tool` whose form travels on the call. |
| `./pp <key> - <<'EOF'` … `EOF` | Hand a production piped by a heredoc: a proof, a field, a production `=> tool` whose form travels piped. |
| `./pp <key> -s <name> [<args>]` | Play a name the current `TOOLS` offers. |
| `./pp <key> -s <name>@<n>` | The same, addressed to segment `[n]` when several segments offer the name. |
| `./pp <key> -peek [<name>]` | Show the block that stands, advance nothing; with a name, whether it is offered. |
| `./pp <key> -compacted` | Declare that the harness summarized the conversation: the run is served back. |
| `./pp <key> -disable <package>` | Take a package out of this run's play; `-enable` puts it back. |
| `./pp -stats [<days>\|<key>] [--blocks] [-json]` | What the runs cost, read from the traces; never advances. |
| `./pp` | Say where the run under way stands; never advances, never opens. |

## The closings

| closing | what it says | what you do |
|---|---|---|
| `▶ CONTINUE` | a call is owed now: it stands under the arrow | type it, after your productions, your production in place of the form's name when one is named |
| `▶ AWAIT` | the passage is over: the principal's message is awaited | write nothing more; the call under it, when one stands, is the one that carries that message |
| `▶ MORE` | the output is not complete: the rest comes at your next turn | nothing is due: say `...` and hand back |
| none | the pending step ends when you decide | finish it, then hand back |

Under the closing, or alone at the end, a line between parentheses is a FACT: a gap declared,
a proof with nothing due, a reading that continues (`n characters in m more chunk(s)`). A fact
asks nothing.

## The call under the closing

When a step asks a production `=> tool`, the output closes on `▶ CONTINUE` and the call
to type stands under it. The name of the form due stands where your production goes:
type the call with your production in its place.

A choice travels on the call:

    ▶ CONTINUE
    ./pp 3f9a1c <options>

You type `./pp 3f9a1c revise`.

A proof travels piped:

    ▶ CONTINUE
    ./pp 3f9a1c - <<'EOF'
    <proof>
    EOF

You type the same three lines, your proof in place of `<proof>`.

## Examples

**Choose** at `PICK`: one value of `OPTIONS`, copied exactly:

    ./pp 3f9a1c revise

**Hand a one-line production** to `=> tool`, its form `line`:

    ./pp 3f9a1c "parser/imports.py"

**Pipe a production** to `=> tool` -- a `json`, a `table`, a field:

    ./pp 3f9a1c - <<'EOF'
    ["engine/a.py", "engine/b.py"]
    EOF

**Prove**: the line `INFER proof [B1 M2] … => tool` asks one verdict per code,
in the `proof` form:

    ./pp 3f9a1c - <<'EOF'
    [{"code":"M2","evidence":"pytest tests/parser: 12 passed","verdict":"ok"},
     {"code":"B1","evidence":"no file outside the member written","verdict":"n/a"}]
    EOF

**Answer a fix in place**: after a `fail` that named a `fix`, prove the failed codes alone:

    ./pp 3f9a1c - <<'EOF'
    [{"code":"M2","evidence":"pytest tests/parser: 13 passed","verdict":"ok"}]
    EOF

**Play an offered skill** with its arguments (`pp-notes` stands for any name `TOOLS` lists):

    ./pp 3f9a1c -s pp-notes add "the lexer is next"

**Read a script's manual**: the name alone, no argument -- nothing runs, the run does not
move:

    ./pp 3f9a1c -s pp-notes

**Address a segment**: the name is offered by `[2]` and `[3]`, play it at `[3]`:

    ./pp 3f9a1c -s pp-notes@3 add "the lexer is next"

**Open a door** (a procedure offered in `TOOLS`):

    ./pp 3f9a1c -s REVIEW

**See the block that stands**, advancing nothing:

    ./pp 3f9a1c -peek

**Check an offer** without playing it (exit 2 when the current output does not offer it):

    ./pp 3f9a1c -peek pp-notes

**Declare a compaction** the harness made:

    ./pp 3f9a1c -compacted

**Switch a package** on the principal's word (`steering off`):

    ./pp 3f9a1c -disable steering

## What a call answers

| You see | What it means | What you do |
|---|---|---|
| a block | the step that follows your call, or the view you asked | play it, as the standing orders say |
| `◀ pp · [n] <stack>` then a script's output | a gesture: the skill ran under segment `[n]`, the run did not move | read it; go on with the step that stands |
| `pp: value judged`, `pp: mounted`, `pp: opened`, `pp: closed`, `pp: re-served`, `pp: reopened` | your call was played; the output it serves comes at your next turn | go on with your work if any remains, then hand back; until then a call that moves the run waits, a view or a script plays |
| `pp: not played -- call already done` | nothing was played: an output waits for your next turn | say `...` and hand back; at your next turn, play the call again if it is still due |
| `pp: chunk-pending -- …` | a reading is still cut: your call was not played | the rest comes at your next turn: play your call again then |
| `pp: REFUSED — <code> — <detail>` | nothing was played (exit 2) | follow the detail; see the refusals below |

## Refusals

| Code | Cause | The way out |
|---|---|---|
| `run-unknown` | the key names no run (forgotten by `-reset`, or never handed) | say it to the principal |
| `no-run` | a keyed verb with no run under way | say it to the principal |
| `address-ambiguous` | several segments offer the name | add `@<n>` |
| `address-stale` | an `@<n>` from an output that is no longer current | take the address from the current output |
| `call-busy` | another call on the same run is still playing | play it again once that call has answered |
| `principal-advances` | the bare call plays nothing in this run: an output comes at your next turn | hand back |
| `repair-exhausted` | the step missed as many times as the bound allows: the run stops on it | say it to the principal; the next message takes the step up with its miss |
| `package-unpinned`, `package-base`, `package-in-flight` | `-disable` on a package not pinned, on the base, or on one whose document holds the view | say it to the principal; a held view lets the word play once its frame ends |

A name the current output does not offer plays nothing: the pending block comes back,
its DEVIATION saying so.
