---
name: PROVIDER
kind: doc
description: >-
  The Claude Code link of the measure: the Stop hook that stamps every turn's
  end -- what it does, how it is wired, and its limits. A provider reference,
  never played.
---

# The Claude Code provider — the turn-end link

Claude Code's **Stop hook** fires when the agent finishes its answer — the
exact end-turn moment. Wired, it runs `./pp monitoring-stamp`: a command this package
declares, whose skill stays SILENT while `monitoring_capture` is false and
plays the engine's `-et` when it is true — the switch is the runtime
interrupter, the hook never changes.

## Wiring

`pp-monitoring wire claude` writes `.claude/settings.json` when it is ABSENT —
the hook alone, nothing else. When the file exists it touches NOTHING, prints
the exact snippet and says the skip: merging into your own settings is your
edit. The snippet is `hook.json`, beside this reference.

## Limits, said

- the stamp lands on the MOST RECENTLY written run trace: with several live
  runs it is indicative, not attributed;
- without the hook, the operator's top in a spare console is the fallback:
  `./pp -et` after each answer, imprecise by the operator's own delay;
- turning `monitoring_capture` off stops the stamps at once; the hook may
  stay.
