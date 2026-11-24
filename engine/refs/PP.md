---
name: pp
description: >-
  Procedural Prompting — the principal-registered conductor of this workspace.
  Its local deterministic .pp/ instance prints instruction blocks; this card is
  the manual of its calls, with an example for every case.
---

# `pp` — the conductor's console

`pp` is the local deterministic program `.pp/.sys/engine/pp.py`, played by the console
`./pp`, that you always call in your working directory (`.\pp` on Windows). It has no network and writes only
inside `.pp/`. How to read a block and what to produce are in the standing orders; this
card gives the calls.

A law that the engine's `system/SYS.md` or the instance's `.pp/system/SYS.md` declares is in
force at every block of every run. Every conduction gives its full text once, never its code
alone.

## Commands

`<key>` is the six characters that name the run, shown in the heading of every conduction.
It leads every call that addresses the run: never drop it, never swap it for another.

| Form | Effect |
|---|---|
| `./pp <key> <value>` | Hand a production `=> tool`, on the call: a `PICK` choice, a one-line form. |
| `./pp <key> - <<'EOF'` … `EOF` | Hand a production `=> tool_heredoc`, piped by a heredoc: a proof, a field, a list, a JSON value. |
| `./pp <key> -print <DOCUMENT> - <<'EOF'` … `EOF` | Hand a production `=> terminal`, piped by a heredoc: `<DOCUMENT>` is the name the step's line shows in brackets. pp keeps it for the principal and answers one line. |
| `./pp <key> -s <name> [<args>]` | Play a name the current `TOOLS` offers. |
| `./pp <key> -s <name>@<n>` | The same, addressed to block `[n]` when several blocks offer the name. |
| `./pp <key> -open <name>` | Open a SPACE on a procedure the current `TOOLS` offers: the principal's next messages go to it until you leave it with `-close`. The bare name opens it even when several blocks offer it; `-open <name>@<n>` opens it under block `[n]`. |
| `./pp <key> -close` | Leave the deepest space: what was there before it takes up where it stood. |
| `./pp <key> -peek [<name>]` | Show the block that stands, advance nothing; from then on, the `@<n>` that count are the ones it shows; with a name, whether it is offered. |
| `./pp <key> -compacted` | Declare that the harness summarized the conversation: the run is served back. |
| `./pp <key> -disable <package>` | Take a package out of this run's play; `-enable` puts it back. |
| `./pp -stats [<days>\|<key>] [--blocks] [-json]` | What the runs cost, read from the traces; never advances. |
| `./pp` | Say where the run under way stands; never advances, never opens. |

## A result in pieces

A text that comes back in your call's result -- a view (`-peek`), a script's manual, the block
of a step that asks you a value -- and is too long for one tool return comes in pieces: each
piece but the last ends on `▶ CONTINUE`, the bare call `./pp <key>` under it, and the fact
`(pp: a reading continues: n characters in m more chunk(s))`. Type that call at once to read
the next piece; it advances nothing else. Every piece stays within the size of the first cut,
and within the size the call that serves it allows.

While a piece waits, the bare call serves it, and `-peek` alone plays beside it. Any other
call -- a gesture (`-s`), a `-print`, a value -- bounces: pp answers the one line
``pp: chunk-pending: `<your call>` was not played — hand back``, plays nothing and keeps nothing.
When the pieces are your own view -- a `-peek` or a script's manual you asked for --, read them
to the end with the bare call, then type your call again. Otherwise the pieces are the
principal's to read: hand back, as the line says; your bare call would refuse
`principal-advances`.

## Examples

**Choose** at `PICK`: one value of `OPTIONS`, copied exactly:

    ./pp 3f9a1c revise

**Hand a one-line production** to `=> tool`, its form `line`:

    ./pp 3f9a1c "parser/imports.py"

**Pipe a production** to `=> tool_heredoc` -- a `json`, a `table`, a field:

    ./pp 3f9a1c - <<'EOF'
    ["engine/a.py", "engine/b.py"]
    EOF

**Print a production** to `=> terminal` -- the line `INFER table => terminal  (REPORT)` names
its document in brackets; pp keeps the production for the principal and answers one line:

    ./pp 3f9a1c -print REPORT - <<'EOF'
    **🧪 The parser tests**

    | test | verdict |
    |---|---|
    | imports | ✅ 12 passed |
    EOF

**Prove**: the line `INFER proof [B1 M2] … => tool_heredoc` asks one verdict per code,
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

**Address a block**: the name is offered by `[2]` and `[3]`, play it at `[3]`:

    ./pp 3f9a1c -s pp-notes@3 add "the lexer is next"

**Open a door** (a procedure offered in `TOOLS`; it closes by itself when its steps are done):

    ./pp 3f9a1c -s REVIEW

**Open a space** (a procedure offered in `TOOLS`; the next messages stay in it):

    ./pp 3f9a1c -open REVIEW

**Leave the space** once its work is settled:

    ./pp 3f9a1c -close

**See the block that stands**, advancing nothing:

    ./pp 3f9a1c -peek

**Check an offer** without playing it (exit 2 when the current conduction does not offer it):

    ./pp 3f9a1c -peek pp-notes

**Declare a compaction** the harness made:

    ./pp 3f9a1c -compacted

**Switch a package** on the principal's word (`steering off`):

    ./pp 3f9a1c -disable steering

## Records — find a fact

The records of an instance (the operations of continuity, its weekly digests…) live in its
store. Read them with `./pp records`, never under `.sys/`: it only reads, every answer is one
page, and its last line gives the call that reads the next page. It reads the instance where
you call it.

| Form | Effect |
|---|---|
| `./pp records list` | Every record of the instance, its number of entries, its first and last dates. |
| `./pp records search <text> --records <record>` | The entries whose text holds `<text>`. |
| `./pp records read <record> [filters]` | The entries of one record, the latest first. |
| `./pp records count <record> [filters] [--group day]` | How many entries match; by day with `--group day`. |

Filters: `--match <text>`, `--since` and `--until` (a date `2026-11-20`, or a span `7d`),
`--last <n>` (the page size), `--order asc` (oldest first), `--json` (one object: `rows`,
`total`, `bound`, `next`). Text between double quotes matches that exact text; words without
quotes must each appear somewhere in the entry; each word holds 3 characters or more
(`match-short` otherwise). Quote the whole text for the shell: `'"…"'`.

**Find an exact text**:

    ./pp records search '"pp-plan"' --records operations --last 5

**Find entries that hold several words**, anywhere and in any order:

    ./pp records count operations --match 'migration copie'

**Read a period**, the latest first:

    ./pp records read operations --since 2026-11-20 --until 2026-11-21 --last 10

**See when a fact was recorded**, day by day:

    ./pp records count operations --match '"plan 0.8.0"' --group day

**Read the first mentions**, the oldest first:

    ./pp records read operations --match '"T66"' --order asc --last 3

**Read the next page**: type the call the last line gives, as it stands:

    ./pp records read operations --since 7d --last 2 --before 2596
