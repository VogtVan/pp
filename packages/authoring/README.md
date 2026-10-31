# authoring

> **Experimental package.** Its procedures, contracts and user-facing behavior
> may change between versions.
>
> **Current version:** `0.2.0`

`authoring` is a package for [Procedural Prompting](../../README.md). It gives a
conducted workspace an author's space: the hall `AUTHOR`, where the agent shapes or
changes the documents that conduct this workspace -- its member, its rules, its
offers, a migration, a new procedure -- with you, over as many messages as it takes.

The package is proposal-first. The agent sketches every document in the chat, amends
it with you, and writes it only on your explicit GO.

## Role

Procedural Prompting separates the deterministic conductor from the documents that
define a workspace. `authoring` lets the agent maintain those documents without
turning their design into an improvised chat task.

It answers five recurring questions:

- What member should tend this workspace, and which readings must it know?
- Which statements deserve the cost and force of a law, and where should each live?
- Which harness skills should be offered to pp, and at which scope?
- How should an existing prompt or instruction system move into pp without a gap?
- Which conducted form fits a new workflow, and how should that procedure be composed?

## Features

### The hall `AUTHOR`

`AUTHOR` is offered at the boot and at every turn. The agent opens it with
`./pp <key> -open AUTHOR`: the hall is a SPACE -- your next messages stay in it until
the agent leaves it with `./pp <key> -close`. It serves the catalogue of the engine's
patterns (`engine/patterns/README.md`), shows its crafts in one table (`AUTHOR-TABLE`),
then takes your ask and opens the craft it needs.

### The five crafts

Each craft is a space opened from the hall with `./pp <key> -open <craft>`; `-close`
brings the agent back to the hall.

| craft | what it does for you | what it reads |
|---|---|---|
| `AUTHOR-MEMBER` | shapes who the agent is here: its role, its character, the readings its role needs and its own laws, in `MEMBER.md` | the patterns `composition/initialize`, `context/serve` |
| `AUTHOR-RULES` | finds a rule its words and its holder -- the member, a plan node, a proc, an overlay -- and writes it as a law | the patterns `rules/laws`, `rules/prove`, `rules/repair` |
| `AUTHOR-OFFERS` | surveys the skills the harness carries and offers each one worth it, at the scope where its work lives | the patterns `composition/door`, `composition/adoption`, `composition/overlay` |
| `AUTHOR-MIGRATE` | brings an existing set of instructions into pp: maps it, keeps what each piece guarantees, places each piece, sequences the steps | the catalogue; it can open the member, rules and offers crafts |
| `AUTHOR-DESIGN` | answers your ask with a conducted document: an overlay, a proc, an offer, a contributor, a workflow | the catalogue |

Every craft runs the same cycle: understand the ask and what the instance holds;
sketch the document's front matter and proc in the chat, naming the patterns it
uses; amend the sketch with you; on your GO, write it with `pp-authoring`; run
`./pp -build` and say what it answers. At the end of each message, the craft's
proof checks what it wrote against its own law.

### `pp-authoring` — the writer of the front matter

The one writer of a document's front matter: `section get`, `set`, `add`, `remove`,
`constrain` (you give the law's text, the script gives its code) and `serve` (the
readings). Only the targeted key moves; every other line stays byte for byte.

### The two signals

The package watches two facts at the boot and points both to the hall:

- `member-bare` -- the member is still the one the install wrote;
- `offers-idle` -- the harness carries skills nothing offers.

## Installation

`authoring` requires the `kit`; the installer pulls it automatically.

For a new workspace:

```sh
uv run pp/engine/pp.py -install <workspace> authoring -<provider>
```

For an existing pp instance, from the workspace root:

```sh
./pp add authoring
```

Then start the configured host as described in the main
[Quick start](../../README.md#quick-start).

## Quick start

Start with the member. Ask the conducted agent:

```text
Open the author's hall and shape this workspace's member.
```

The agent opens `AUTHOR`, then `AUTHOR-MEMBER`, surveys the repository, asks what only
you know, and sketches the member for review. It writes it only on your GO.

Other asks the hall takes:

```text
Open the author's hall: decide where this rule belongs and write it --
every public API change updates the corresponding example.

Open the author's hall: survey the harness skills of this workspace and offer
only those that should be conducted.

Open the author's hall: map our existing instruction files into what pp takes
over, what stays for now and what becomes obsolete.

Open the author's hall: design a release procedure that reads the checklist,
runs the work, proves the release conditions and stops at my approval.
```

One craft is open at a time. Your GO applies only to the sketch it names; when you
are done, the agent closes the craft, then the hall.
