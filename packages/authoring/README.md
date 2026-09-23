# authoring

> **Experimental package.** Its procedures, contracts and user-facing behavior
> may change between versions.
>
> **Current version:** `0.1.12`

`authoring` is a package for [Procedural Prompting](../../README.md). It gives a
conducted workspace an authoring surface: five guided doors for shaping its member,
placing rules, registering harness skills, migrating an existing instruction system
and designing new procedures.

The package is proposal-first. It analyses what exists, produces complete changes
for review and waits for the operator's explicit GO before those changes are placed.

## Role

Procedural Prompting separates the deterministic conductor from the documents that
define a workspace. `authoring` helps the agent maintain those documents without
turning their design into an improvised chat task.

It provides a method for answering five recurring questions:

- What member should tend this workspace, and which references must it know?
- Which statements deserve the cost and force of constraints, and where should
  each one live?
- Which harness skills should be exposed to pp, and only in which scope?
- How should an existing prompt or instruction system move into pp without a gap?
- Which conducted form fits a new workflow, and how should that procedure be
  composed?

## Features

### `PP-MEMBER` — shape the member

Builds a complete `MEMBER.md` proposal from the workspace as it actually stands.
It surveys the repository before proposing anything, distinguishes a single project
from a multi-project solution, asks one round of questions only the operator can
answer, and identifies the minimal reference ground the member's role requires.

The resulting proposal keeps identity and house invariants short, avoids restating
the kit's turn discipline, and places role-required readings in the member's own
`serve:` section.

### `PP-RULES` — give rules words and scope

Turns an intended rule into an inventory entry and, when justified, a ready-to-place
constraint. It separates descriptive material from imperative laws, distinguishes
production constraints from behavior constraints, and chooses one holder for each
rule: member, plan node, procedure, overlay, kit or dead.

A rule already enforced by a mechanism is retired rather than restated. A proposed
constraint must oppose a real observed failure mode, remain short and be provable at
the scope where it lives.

### `PP-OFFERS` — register harness skills

Surveys the workspace's harness skill homes, reads each candidate and classifies it
as conductible, one edit away, superseded or harness-native. Every proposed offer
names its scope: the member for a session-wide capability, or the procedure that
needs it for a local one.

Skills remain in their native harness location. The package proposes adoption by
name instead of copying them into the instance, then uses the compiled catalog as
the receipt for what pp can conduct.

### `PP-MIGRATE` — move an existing instruction system

Produces a migration sheet before anything is retired. Existing material is divided
between what pp takes over, what temporarily stays and what becomes obsolete because
a named mechanism replaces it.

The migration captures each workflow by its essence — guarantees, prohibitions and
productions — checks names, roles and constraint codes for collisions, and sequences
steps so the replacement is in force before the previous instruction disappears.
Member design, rule placement and skill offers are handed to their dedicated doors.

### `PP-DESIGN` — compose conducted documents

The author's role, in four steps: read the operator's ask against the theory
(`CONDUCTION`), choose the mechanism at the served catalog (`PP_CHEATSHEET`: every form,
front-matter key, setting and package figure, with worked examples the package's own
bench installs and plays), propose the complete document with `pp-authoring`, and
install it on the operator's GO alone, proven played.

The method optimizes for fewer model initiatives, explicit mechanical guarantees and
documents that describe the present state rather than their editing history. The
authored document is proposed first and installed only on the operator's GO.

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
[Quick start](../../README.md#quick-start). The package adds its doors to the boot
surface and keeps `PP-DESIGN` available during ordinary turns.

## Quick start

Start with the member. Ask the conducted agent:

```text
Open PP-MEMBER. Analyse this whole workspace and propose its MEMBER.md.
```

The door surveys the repository, asks one compact set of operator-only questions and
returns a complete file for review. Place the proposal only when its role, character,
workspace shape, constraints and reference ground are right.

Open one of the other doors when its concern appears:

```text
Open PP-RULES. Decide where this rule belongs and propose its exact wording:
every public API change updates the corresponding example.

Open PP-OFFERS. Survey the harness skills in this workspace and propose only the
offers that should be conducted.

Open PP-MIGRATE. Map our existing instruction files into what pp takes over,
what stays for now and what becomes obsolete.

Open PP-DESIGN. Design a release procedure that reads the checklist, runs the work,
proves the release conditions and stops at the operator's approval.
```

Each door keeps one authoring concern in scope. Finish or leave that door before
opening another; the operator's GO applies only to the proposal it names.
