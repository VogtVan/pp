# Versions

This copy of Procedural Prompting carries the engine and the packages below.

| component | version |
|---|---|
| engine | 0.2.0-beta.18 |
| kit | 0.2.2 |
| agent | 0.29.0 |
| authoring | 0.2.0 |
| continuity | 0.1.4 |
| daneel | 0.1.2 |
| monitoring | 0.1.4 |
| plan | 0.1.50 |
| steering | 1.0.0 |
| team | 0.40.2 |
| ui | 0.51.0 |

Source: commit d6145a25.

## Changes since the release 0.1.0-beta.14

The release 0.1.0-beta.14 is the tag `PUB-e0.1.0-beta.14-a0.1.12-c0.1.0-d0.1.0-k0.1.107-m0.1.0-p0.1.40-s0.7.3`, on commit 966643ea (2026-09-23).

- **Engine 0.2.0**: every procedure has an `initialize` entry, where a document attached to it plays once when the procedure starts; spaces are opened and closed (`-open`, `-close`); a document names what it mounts (`mounts:`); the tools and the output formats are served at every boot.
- **The engine's patterns**: `engine/patterns/` -- 46 patterns in 8 categories, each with its README, its demonstration procedures and its test, and one catalogue (`engine/patterns/README.md`).
- **The conduction handed to the principal**: a production is a message said at its own step, what only shows answers the tool call; `./pp -purge` removes the runs left behind.
- **agent, team and ui -- new**: a house wakes agents and talks with them through the four harnesses, without an editor; it runs teams of agents that coordinate by messages; and it opens a terminal post for both.
- **steering 1.0.0**: steps of work with labels, archived by age and under a cap, and the STEERING space.
- **authoring 0.2.0**: the author's hall `AUTHOR` and its five crafts.
- **plan 0.1.50**: steering is optional; a plan whose code lives in another tree names its material.
- **The adapters**: Claude Code, Codex, Gemini and Cursor behind one provider abstraction -- the launch policy, the events and the reader of the stream.
- **The bench**: cut by half; no test guards a text; an area marked `opt-in` plays only when a selection names it.

112 pull requests merged, #25 to #142.
