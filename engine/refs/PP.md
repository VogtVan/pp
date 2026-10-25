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

`<key>` is the six characters `-new` returns. It leads every call that addresses the
run: never drop it, never swap it for another.

| Form | Effect |
|---|---|
| `./pp -new [<message>]` | Open a run; the words after it are the principal's message. |
| `./pp <key>` | Advance: the next block, the next chunk of a reading, the resume of a parked run. |
| `./pp <key> <value>` | Advance with a value on the call: a `PICK` choice, a production `=> tool`. |
| `./pp <key> -` | Advance with a production piped on standard input: `=> tool (heredoc)`. |
| `./pp <key> -s <name> [<args>]` | Play a name the current `TOOLS` offers. |
| `./pp <key> -s <name>@<n>` | The same, addressed to segment `[n]` when several segments offer the name. |
| `./pp <key> -peek [<name>]` | Show the block that stands, advance nothing; with a name, whether it is offered. |
| `./pp <key> -skip` | Drop the rest of a cut reading: its closing comes at once, the dropped part unread. |
| `./pp <key> -compacted` | Declare that the harness summarized the conversation: the run is served back. |
| `./pp <key> -disable <package>` | Take a package out of this run's play; `-enable` puts it back. |
| `./pp -stats [<days>\|<key>] [--blocks] [-json]` | What the runs cost, read from the traces; never advances. |
| `./pp` | Say where the run under way stands; never advances, never opens. |

## Examples

**Open the conversation's run**, with the principal's first message:

    ./pp -new "fix the failing import in the parser"

**Advance**: the closing shows `▶ CONTINUE` and the command, with no value owed:

    ./pp 3f9a1c

**Choose** at `PICK`: one value of `OPTIONS`, copied exactly:

    ./pp 3f9a1c revise

**Hand a one-line production** to `=> tool`:

    ./pp 3f9a1c "parser/imports.py"

**Pipe a production** to `=> tool (heredoc)` -- a `json`, a `table`, a field:

    ./pp 3f9a1c - <<'EOF'
    ["engine/a.py", "engine/b.py"]
    EOF

**Prove**: the line `INFER proof [B1 M2] … => tool (heredoc)` asks one verdict per code,
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

**Open a door** (a procedure offered in `TOOLS`): its first block follows:

    ./pp 3f9a1c -s REVIEW

**Come back after a parenthesis**: see the block that stands, then play its owed call:

    ./pp 3f9a1c -peek

**Check an offer** without playing it (exit 2 when the current output does not offer it):

    ./pp 3f9a1c -peek pp-notes

**Declare a compaction** the harness made:

    ./pp 3f9a1c -compacted

**Switch a package** on the principal's word (`steering off`):

    ./pp 3f9a1c -disable steering

**Read the rest of a cut reading**: the closing says `a reading continues`; only the bare
call serves it:

    ./pp 3f9a1c

**Drop the rest of a cut reading**: the block's closing comes at once:

    ./pp 3f9a1c -skip

**Resume a parked run** when the closing `▶ AWAIT` asks for the principal's message:

    ./pp 3f9a1c "now the tests for the lexer"

## What a call answers

| You see | What it means |
|---|---|
| a block | the run moved, or a view was asked |
| `◀ pp · [n] <stack>` then a script's output | a gesture: the skill ran under segment `[n]`, the run did not move |
| `pp: value judged`, `pp: mounted`, `pp: opened`, `pp: re-served`, `pp: reopened` | in a run your principal conducts, the call moved the run; the next block comes at your next prompt |
| `pp: an answer is held for your principal's call` | an output already waits for the principal: your call was not played |
| `pp: chunk-pending -- …` | a reading is still cut: your call was not played |
| `pp: REFUSED — <code> — <detail>` | nothing was played (exit 2) |

## Refusals

| Code | Cause |
|---|---|
| `run-unknown` | the key names no run (forgotten by `-reset`, or never handed) |
| `no-run` | a keyed verb with no run under way |
| `address-ambiguous` | several segments offer the name |
| `address-stale` | an `@<n>` from an output that is no longer current |
| `call-busy` | another call on the same run is still playing |
| `principal-advances` | your bare call, in a run your principal conducts |
| `package-unpinned`, `package-base`, `package-in-flight` | `-disable` on a package not pinned, on the base, or on one whose document holds the view |

A name the current output does not offer plays nothing: the pending block comes back,
its DEVIATION saying so.
