---
name: LEDGER
kind: proc
description: >-
  The open threads at the start of the session: each thread's id, name and note, and the steps still to do -- served at boot and after a declared compaction, never re-read in between.
mount: boot.ready
provides: steering-ledger
with: pp-steering status --all --open
payloads: steering-ledger
---

# LEDGER — the open threads at the start of the session

`steering-ledger` lists the open threads: each one's id, name and note, then its steps
still to do (open, reopened, waiting) with their id, name, text, the reason in
parentheses for a waiting step, and key.

It is served now, and again after a declared compaction. Take thread and step ids from
here. A thread or a step you create later gives its id in the output of the call that
created it. Do not read the threads again during the session: rely on what the session
did. When no thread is open, the section says so.
