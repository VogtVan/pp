---
name: GATED
kind: doc
description: mounted where LOOP opens, only while GATE is open.
mount: loop.open
when: "@GATE.open"
exec: pp-stamp stamp gated
---

The gate is open.
