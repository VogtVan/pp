---
name: PLAYBOOK
kind: doc
description: >-
  The grammar of a scenario PLAYBOOK -- the one codified format the measure
  plays, for the kit and every package alike: the required composition, the
  ordered sessions, their fixtures and their gesture tables. A reference,
  never played.
---

# The PLAYBOOK — one format for every scenario book

A playbook is a plain markdown file the OPERATOR owns. `pp-monitoring run` plays
it on a DERIVED disposable repo — never on the instance itself — and traces;
the `expected` column stays the human or agent judge's, the run never
evaluates. The mold is the steering witness's book (S1: the surface).

## The grammar

- **the composition line**, before the first session:
  `composition: kit steering` — the packages the playbook requires; a derived
  repo whose pins lack one refuses `composition-short`;
- **a session**: a `## S<n>` heading — each session is played as its OWN run
  (`-new`, then the gestures in table order);
- **a fixture**, optional, one line before the session's table:
  `shell: touch seed.txt` — executed in the derived repo's workspace before
  the session; a failing fixture stops the run (`fixture-failed`);
- **the gesture table**: `| id | gesture | expected |` — one row per exchange;
  the id NAMES the row (the address expecteds, coverage and analyses cite);
  the gesture IS the operator message, exactly as typed — it never carries the
  id: the play is DETERMINISTIC, the operator types the gestures in table
  order and the sessions in book order, so any analysis pairs an exchange to
  its row by that order alone;
- everything else is prose for the humans who play or read the book.

## Example, minimal

    composition: kit

    ## S1 — the bare surface

    shell: touch seed.txt

    | id | gesture | expected |
    |---|---|---|
    | S1.01 | hello | the boot renders the catalog |
    | S1.02 | end of session | — |
