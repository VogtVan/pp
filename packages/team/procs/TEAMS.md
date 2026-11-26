---
name: TEAMS
kind: proc
description: >-
  The teams space -- open it (`-open TEAMS`) to see the teams of the house, their members and the templates at a glance, then write a team or a recurring task from there; `-close` gives the turn back.
serve: |
  TEAM_WORK.md
  TEAMS_CHEATSHEET.md
tools: |
  pp-team
proc: |
  SERVE
  WORK
  PROVE
constraints.behavior: |
  TS1  write a team, its season, a recurring task or a description only with a `pp-team` verb and on the principal's word, never with an editor; never start or stop a team: propose `team start` or `team stop`, the principal plays it
  TS2  write a team from a template that `team templates` lists, with its description; give a recurring task its own description
  TS3  say a member without a description to the principal with the path of its `MEMBER.md`, and never write that file from here
  TS4  close the space only on the principal's word
---

# TEAMS — the teams, at a glance

This space is where the principal looks at the teams of the house and writes them. The cheat sheet
served with it says the files of a team; the words used here:

- a TEMPLATE is a file named `<directory>/<name>` (`teams/lead-reviewers`); `team templates` lists
  them. A PRESET gives ready-made lines for a values file -- a team preset also gives the members and
  who reports to whom; a DOCUMENT is a text that members receive;
- `TEAM.md` and `SEASON.md` are the VALUES FILES of a team, in `teams/<name>/`, the principal's own.
  Both say their documents the same way: `documents:`, one line per key, `<key> <document> ...` --
  the key `all` for every member, or a role key for the members who hold it. `TEAM.md` names the
  team's preset, its members, its role keys and its documents, and lasts with the team; `SEASON.md`
  adds documents and values for one season, and may name a preset of its own;
- a ROLE KEY is a word the principal chooses and gives to members: it decides which documents each
  member receives, and gives no right;
- a SEASON runs from a `team start` to a `team stop`; `start` renders the team's documents from both
  files. Between a stop and the next start the team is OFF SEASON: no member is woken. `team declare`
  writes `TEAM.md` and `SEASON.md` before the first start or off season -- in season it refuses
  `season-running`. A change
  of a key -- a line of the front matter of either file -- reaches the members at the next start; a
  change to the body of `TEAM.md` or `SEASON.md` reaches them at their next exchange;
- the VERDICT of `team declaration` is `ok`, or the refusal the next `team start` would make.

**What the principal sees when the space opens.** The board, said as tables: the teams and their state, what
each one does, the members whose description is missing, and the templates.

**What the principal can ask for next.** Any view of the teams, with `pp-team`:

- one team whole, its members, its tasks and its recurring tasks: `team status <name>`;
- its preset, its role keys, its documents and the season's, what each member receives (`--json`),
  whether it is in season (`started.state`, `running` or `stopped`), and what a new start would
  change: `team declaration <name>`;
- the templates, with the values each one asks: `team templates`.

**Set up a team.** Ask the principal, one question at a time, only what is still unknown: what the
team does; its members and the agent of each; its team preset (`teams/<name>`); its role keys and
their members; the documents of its first season and the role key that receives each one -- a season
preset (`seasons/<name>`) gives them ready-made --, or none; the values that the presets and the
documents declare without a default (`team templates`). Then write it, and nothing else:

```
team declare alpha --template teams/lead-reviewers --description "Writes the house's notes and has them reviewed." --member lead agents/alpha/lead --member reviewer-1 agents/alpha/reviewer-1 --role writers lead --role readers reviewer-1
team declare alpha --season --template seasons/files --value contributors=writers --value reviewers=readers --value source-folder=notes/sources --value draft-folder=notes/drafts --value result-folder=notes/results
team declaration alpha
```

Say the verdict of `team declaration <name>`, and the documents each member will receive, read from
`team declaration <name> --json` (`declared.views`). When `team declare` refuses, nothing is written:
it judges `TEAM.md` and `SEASON.md` together, as the next `start` would, and refuses only a fault that
its own write would bring; its message names the value or the line to fix, in either file. Ask the
principal, then write again. When `team declare` writes but its verdict is refused, the fault was
there before the call -- for example a rendered document edited by hand, or words written in the body
of `TEAM-<name>.md`: say it to the principal, with what the verdict names. When the verdict is ok,
propose `team start <name>`: the principal plays it.

**Change a team.** Read `team declaration <name>` first. When the team is in season, nothing can be
written: say so, and propose `team stop <name>` -- it stops the open tasks and silences the recurring
tasks, which it names; the principal plays it. Out of season, ask only about what changes, and write only
those keys -- `team declare` leaves every other line as it stands:

```
team declaration alpha
team declare alpha --member reviewer-2 agents/alpha/reviewer-2 --role readers reviewer-1 reviewer-2
team declaration alpha
```

Say the verdict and the `pending` keys, the keys a new start would change: the change reaches the members at the next `team start`,
which you propose.

To change the documents of a key, write its whole line:
`team declare <name> --document "<key> <document> ..."` writes it in `TEAM.md`, and with `--season`
in `SEASON.md`, and leaves one line for the key even when it stood on several; `--no-document <key>` takes out every line of the key. A document is a template, `<directory>/<name>`, or a file `<name>.md` written in
the team's directory.

**A recurring task.** `team post <name> --every "<when>" --message <text> --description <text>`;
change it with `team recurrence <name> R<n>`, stop it with `team stop <name> --recurrence R<n>`.

The space writes in the house, wherever it is opened from: the team under `teams/<name>/`, its
recurring tasks in the house's records. It never writes in the instance of the agent that opened it.

**A member without a description.** The description of a member is the `description:` of its
agent's `MEMBER.md`. When it is missing, say so to the principal with the path of that file; the
agent's owner writes it there.

**How it ends.** Each message worked here ends on the proof of the laws in force. When the
principal is done, `-close` gives the turn back.
