---
slug: {slug}
kind: batch
plan: {plan}
phase: {phase}
status: todo
created: {created}
---

# BATCH `{slug}` — phase `{phase}`, plan `{plan}`

## Context

{prose}

## Ground

The zoom-out, measured on-piece and dated: the pieces the batch touches, the code around them, the upstream VERIFIED, and their DEPENDENTS in a last paragraph — every piece a change here would break. *e.g. `storage.py` `list()` l.30-41 at `a1b2c3d`; dependents: `cli.py` l.12.*

## Target

What the pieces become — from scratch, a new piece with its shape and its contract; a refactor, what breaks and what moves — and what stays out. *e.g. `search(word)` beside `list()`, same store, no new file; the CLI wiring is the next batch.*

## Expected

What is TRUE when the batch closes, each line with the rendering that shows it. *e.g. `search("x")` returns the notes holding x — the test's output cited.*

## Tests

What proves the expected: the bench scenarios to run or to write, the renderings to cite, the operator's gate when a live run is the only proof. *e.g. `tests/test_storage.py::test_search`, written first, red then green, on a mktemp store — never the operator's own file.*

## Arbitrations

Every architecture or choice the implementation will meet: the options, the recommendation, what returns to the operator's GO. *e.g. case-sensitive or not — reco insensitive, said at the GO.*

## Items

The todos, one line each `- slug -- text`, each named by its own meaningful slug and precise enough to act on; checked off as they land, never in an end sweep. *e.g. `- search-function -- search(word) in storage.py, the linear scan`*

## Delivery

The log of the implementation, appended: what landed, the proof by RENDERING (bench, diff, grep) on a DISPOSABLE path, the rows re-aligned, what was left out and said; a rework appends its own dated log.
