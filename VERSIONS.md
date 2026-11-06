# Versions

This copy of Procedural Prompting carries the engine and the packages below.

| component | version |
|---|---|
| engine | 0.2.1 |
| kit | 0.2.4 |
| agent | 1.0.0 |
| authoring | 0.2.1 |
| continuity | 0.2.1 |
| daneel | 0.1.2 |
| monitoring | 0.1.4 |
| plan | 0.3.0 |
| steering | 1.2.1 |
| team | 1.4.1 |
| ui | 1.3.1 |

Source: commit 7c6e6a80.

## Changes since the release 0.2.0

The release 0.2.0 is the tag `PUB-e0.2.0-ag1.0.0-au0.2.1-c0.2.1-d0.1.2-k0.2.4-m0.1.4-p0.3.0-s1.2.1-t1.0.0-u1.0.0`, on commit 26828eea (2026-11-05).

- 2026-11-06 · #193 · team 1.4.1: a team's timer sleeps outside the house's lock and ticks through the house's console, so it no longer holds other verbs back while it waits
- 2026-11-06 · #192 · ui 1.3.1: no command is shown anywhere at the post -- the status line says in words what a gesture did; a checked line of the delete dialog shows its mark
- 2026-11-06 · #188 · ui 1.2.1: the Tasks tab lists the live recurrences, and the post lays, changes and plans them -- period, text and context limit; a gesture's dialog keeps its foot in sight
- 2026-11-06 · #191 · team 1.4.0: `team recurrence R<n> --message` rewrites the text of the occurrences to come, and `team recurrence --task T<n> --every` makes a task recurrent
- 2026-11-06 · #190 · team 1.3.0: a recurrence by a duration -- `--every 4h`, `30m`, `2d` -- its first occurrence when it is laid, no catching up on missed periods
- 2026-11-06 · #189 · team 1.2.0: `--context <n>%` renews the run of a recurrence when its last measured context reaches the limit, at the first wake-up of a new occurrence
- 2026-11-06 · #187 · team 1.1.0: a member holds one run per task carrier -- a task, a recurrence, a ceremony -- each named after it; `status --json` lists them
- 2026-11-06 · #186 · engine 0.2.1: a space the principal opens or closes hands its output to the agent, its welcome included, and `-peek` shows the addresses a call then accepts
