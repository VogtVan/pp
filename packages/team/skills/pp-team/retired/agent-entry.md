---
name: team-entry
description: The decider of the team documents of this instance (`procs/TEAM-<team>.md`) -- the engine plays it when such a document leaves, and it prints the document this exchange plays next, asked of the house (`team entry <team> --run <key>`). Laid by the team package's `team start`; you never call it.
---

# `team-entry` — the decider of a team's entries

The team package lays this skill at each agent that plays an entry of a team, beside
`procs/TEAM-<team>.md` and `procs/TEAM-IDLE.md`. You never call it: the engine plays it at the
exit of `TEAM-<team>.md` (`decide: team-entry <team>`), at every exchange.

| Call | Effect |
|---|---|
| `team-entry <team>` | Run by the engine with `PP_RUN` (the run's key) and `PP_HOME` (this instance): finds the house -- the first instance above this one that carries the machine this one borrows (`.sys/engine/pp.py`) -- and prints what `team entry <team> --run <key>` prints there: the entry the trigger of the wake-up under way names, or `TEAM-IDLE.md`. It writes nothing. Without `PP_RUN` or `PP_HOME`, or without a house above: exit 2, the reason on stderr. |
