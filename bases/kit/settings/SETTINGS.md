---
name: SETTINGS
kind: fragment
package: kit
description: >-
  The kit's own settings -- the convenience of the interactive turn: whether the
  AWAIT closing's resume asks for the operator's next message itself, and whether
  the boot presents the catalog of skills. Composed into the instance's SETTINGS
  bare (the base's keys wear no prefix).
capture_prompt: false
capabilities: true
types: |
  capture_prompt  flag
  capabilities  flag
effort: |
  capture_prompt  light=false medium=true full=true
---

## Kit — the interactive turn

The kit's two keys are bare: the base package wears no prefix.

- `capture_prompt` — when `true`, the AWAIT closing's resume asks for the
  operator's next message itself (`./pp <key> <the principal's next message>`)
  and the trace keeps it, read back by `./pp -stats`; when `false`, the
  closing is the bare `./pp <key>` and the operator's words reach the agent
  through the chat alone. It shapes the closing of an exchange, never what the
  run takes in — a text handed with the call that opens or resumes a run is the
  principal's message and is traced `prompt` whatever this key says. The effort
  presets it (medium and full → `true`).
- `capabilities` — when `true`, the boot plays `CAPABILITIES`: the agent
  presents itself and its capabilities to the operator in one table; when
  `false`, the boot goes straight to the turn, without that table — the agent
  can still play `CAPABILITIES` on demand. The key never touches the two
  readings the boot serves first, the skills (`tools.md`) and the formats
  (`output.md`): every run receives them. The member's `CALL CAPABILITIES.md ^
  @SETTINGS.capabilities` reads it. No effort presets it: it chooses a profile,
  not a weight, and the value written here rules at every effort.
