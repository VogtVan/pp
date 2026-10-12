---
name: SETTINGS
kind: fragment
package: kit
description: >-
  The kit's own setting -- the convenience of the interactive turn: whether the
  FINAL closing's resume asks for the operator's next message itself. Composed
  into the instance's SETTINGS bare (the base's keys wear no prefix), read by
  the engine's rendering alone: the message reaches the run at any value.
capture_prompt: false
types: |
  capture_prompt  flag
effort: |
  capture_prompt  light=false medium=true full=true
---

## Kit — the interactive turn

The kit's one key is bare: the base package wears no prefix. It shapes the
closing of an exchange, never what the run takes in — a text handed with the
call that opens or resumes a run is the principal's message and is traced
`prompt` whatever this key says.

- `capture_prompt` — when `true`, the FINAL closing's resume asks for the
  operator's next message itself (`./pp <key> <the principal's next message>`)
  and the trace keeps it, read back by `./pp -stats`; when `false`, the
  closing is the bare `./pp <key>` and the operator's words reach the agent
  through the chat alone. The effort presets it (medium and full → `true`).
