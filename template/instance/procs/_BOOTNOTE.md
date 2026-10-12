---
name: BOOTNOTE
kind: proc
description: a one-line house note served at every boot
readme: |
  An ATTACH example, inert while the file name starts with `_`. Arm it by
  renaming to `BOOTNOTE.md`: it then attaches to the kit's `boot.ready` socket
  and its body -- your standing note, nothing else -- rides every boot. Its own
  `bootnote.read` socket is a further extension point.
attach: boot.ready
proc: |
  HOOK bootnote.read
---

Today's focus: —
