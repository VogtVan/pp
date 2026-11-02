---
name: SETTINGS
kind: fragment
package: keeper
description: keeper's keys
keeper_care: asked
keeper_depth: 2
types: |
  keeper_care   one_of[asked|total]
  keeper_depth  natural
effort: |
  keeper_depth  light=1 medium=2 full=3
---
## Keeper — how far the keeper looks

- `keeper_care` — `asked` waits for the operator's word, `total` asks at every step.
- `keeper_depth` — how many levels the keeper reads; the effort presets it.
