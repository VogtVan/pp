---
name: BOOT
kind: boot
description: >-
  The witness base's bootstrap: the boot socket, then the turn -- no member, no
  contract, no law; a scenario that needs one writes it at run time, and that is what
  it proves.
proc: |
  HOOK boot.ready
  CALL TURN.md
---
