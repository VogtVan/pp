# Versions

This copy of Procedural Prompting carries the engine and the packages below.

| component | version |
|---|---|
| engine | 0.2.0 |
| kit | 0.2.4 |
| agent | 1.0.0 |
| authoring | 0.2.1 |
| continuity | 0.2.1 |
| daneel | 0.1.2 |
| monitoring | 0.1.4 |
| plan | 0.3.0 |
| steering | 1.2.1 |
| team | 1.0.0 |
| ui | 1.0.0 |

Source: commit 26828eea.

## Changes since the release 0.2.0-beta.34

The release 0.2.0-beta.34 is the tag `PUB-e0.2.0-beta.34-ag0.33.0-au0.2.1-c0.2.1-d0.1.2-k0.2.4-m0.1.4-p0.2.2-s1.2.1-t0.46.4-u0.56.3`, on commit 6b714947 (2026-11-02).

- 2026-11-05 · #184 · ui 0.69.0: every zone of the post is framed and labelled -- a round frame from 70 columns and 30 rows, one thin label line below that
- 2026-11-05 · #185 · team 0.54.1: a member whose run still stands on a task is continued -- relaunched with its debts at its head -- instead of being reminded
- 2026-11-05 · #183 · ui 0.68.0: the post opens a space by the name the offer gives, nothing composed
- 2026-11-05 · #182 · ui 0.67.0: the season shown as a set of packages, recurring tasks posted, shown, changed and stopped from the post, and each member's context in a `ctx` column
- 2026-11-05 · #180 · team 0.54.0: the season decides every member's packages -- one switch per package, the member's own SETTINGS out of play; `team recurrence` changes the hour of a recurring task; the end of each wake-up keeps the member's context, which `team status --json` reads at rest
- 2026-11-05 · #181 · engine 0.2.0-beta.37: opening a space the run already holds refuses `space-open`, the offer names each space once, and a bare `-open` opens the space at the pending step
- 2026-11-05 · #178 · the bench: a team whose members advance one shared plan, played on a throwaway house
- 2026-11-05 · #177 · plan 0.3.0: a plan can be shared by every run opened under one root of documents (`--shared`), each run reading and advancing the same plan
- 2026-11-04 · #176 · ui 0.63.0: each member's season on the Teams tab, a discreet turn zone, the space buttons in relief
- 2026-11-04 · #175 · engine 0.2.0-beta.36, agent 0.37.0, ui 0.62.0: the spaces a run holds open and may open are said at its flow, and the principal opens and closes them from the chat (`agent open`, `agent close`) or with buttons above the message line
- 2026-11-04 · #174 · team 0.51.0, agent 0.36.0, ui 0.61.0: the living post -- each member's activity live in a task's sequence, infos in the inbox, the agents with their season, teams renamed (`team rename`) and deleted with their agents (`agent remove`, `team delete --agent`), a schedule in hours, copy and select-all in the message line, the turn shown beside it
- 2026-11-03 · #173 · engine 0.2.0-beta.35, agent 0.35.0, team 0.49.0: a run's own package switches win over the agent's SETTINGS from its first block, and the launcher composes the run when it opens it
- 2026-11-03 · #172 · team 0.47.0: `info`, a fourth act of a member or a principal -- a message that owes no answer and waits for nothing; it replaces the note
