---
name: LEDGER
kind: proc
description: >-
  The active steps still to do at the start of the run -- the old ones archived first, then one line each -- served at boot and after a declared compaction.
mount: boot.initialize
exec: sweep
provides: steering-ledger
with: pp-steering list
payloads: steering-ledger
---

# LEDGER — the steps still to do

`steering-ledger` lists the active steps still to do, the most recently touched first, one
line each: the step's name and id, whether it waits and why, its labels, its
key, its age, then its work.

Take step ids from here. A step you add later gives its id in the output of the call that
adds it. Do not list the steps again during the run: rely on what the run did.
