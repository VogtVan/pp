---
name: LEDGERED
kind: proc
description: offers the ledger's one writer -- every entry goes through it.
tools: |
  pp-ledger
proc: |
  WORK
---

Record each entry of the message in the ledger with `pp-ledger add <entry>`, one call per
entry; read it back with `pp-ledger read`.
