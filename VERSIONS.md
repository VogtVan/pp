# Procedural Prompting 0.3.0

This copy carries the engine and the packages below.

| component | version |
|---|---|
| engine | 0.2.40 |
| kit | 0.2.6 |
| agent | 1.2.1 |
| authoring | 0.2.2 |
| continuity | 0.3.0 |
| daneel | 0.1.3 |
| monitoring | 0.1.5 |
| next | 0.1.2 |
| plan | 0.8.0 |
| steering | 1.4.0 |
| team | 1.36.64 |
| ui | 1.11.4 |

Source: commit a5018a85.

## Changes since the release of 2026-11-23

The release of 2026-11-23 is the tag `PUB-e0.2.39-ag1.1.0-au0.2.2-c0.3.0-d0.1.3-k0.2.6-m0.1.5-n0.1.2-p0.8.0-s1.4.0-t1.35.16-u1.11.0`, on commit 06d9f23a (2026-11-23).

- **Engine 0.2.40**
  - A document can import the documents it stands on (`imports:`): they enter and leave with it, with their laws, offers and readings.
  - An agent of a house reads a house document exactly as the house reads it.
  - The host's `mounts:` table is gone: imports replace it.
- **Team statistics (team 1.36.64, ui 1.11.4)**
  - Three screens at the post: a summary of a team in five lines (spent, work, price, load, watch), the dashboard of a season, and every season at once under [all]; the key `z` opens the dashboard.
  - Each figure is judged against the team's median: good, nominal, watch or alert.
  - The price is the cost of an hour of effort; the dashboard also shows the launches by model and by duration, the cost by slot of the day and the share of context left at the end of each launch.
  - `team stats` gives the same figures as text and JSON; the yield, the cost per task of a season, the roles and the `do` sent again are retired.
- **Teams (team 1.36.64)**
  - The house itself can play a member of its own teams.
  - Inside, pp-team is reorganised by domain; its verbs and its journal are unchanged.
- **Agents (agent 1.2.1)**
  - `--work` also works on the house itself: the clone lives under `<house>/work/<key>`, on the branch `agent/_house/<key>`.
  - Inside, the model and the rules are one concept per module.
- **Terminal post (ui 1.11.4)**
  - The Agents tab names a member the house plays.
  - The building blocks of the statistics screens (judgments, theme colours, rich tables, tiles, bars), shown by `ui --render looks`.
- **Migrations**
  - One frame that every house migration plays.
  - A whole house can be brought from 0.2.0-beta.33 to 0.2.39 in one migration.

74 pull requests merged, #434 to #507.
