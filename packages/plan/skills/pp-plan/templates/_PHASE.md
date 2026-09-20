---
slug: {slug}
kind: phase
plan: {plan}
status: todo
created: {created}
---

# PHASE `{slug}` — plan `{plan}`

## Context

{prose}

## Ground

The zoom-out, measured on-piece and dated: the sources to read whole, the code the phase will touch, and its DEPENDENTS in a last paragraph — spotted now so they enter the perimeter. *e.g. `memo/storage.py` (54 l., `add`, `list`) at `a1b2c3d`; dependents: `memo/cli.py` calls `list`.*

## Target

What the component becomes, from scratch or a refactor, and what stays out. *e.g. the store gains `search`; the CLI stays as it is.*

## Expected

What is TRUE when the phase closes, each line with the rendering that shows it. *e.g. `pytest tests/test_storage.py` green, 6 cases.*

## Arbitrations

The open questions of the framing: the options, the recommendation, what returns to the operator's GO. *e.g. a linear scan or an index — reco the scan: a notebook, not a database.*

## Items

The batches prepared, one line each `- slug -- brief`, the brief saying the work, its exit and its proof in a sentence; the operator amends a line until « frame » names it. *e.g. `- search -- a word looked up in every note; exit: `memo search x` prints the matching notes; proof: the test cited`*
