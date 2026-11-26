---
name: TEAM-ACT
kind: doc
description: >-
  The form of a team act: the OUTPUT format `team-act`, which the turn of a team's runs asks for and which any document of the house and of its agents may name -- a message to a team is one JSON value given alone, on the channel its step's line names, `[]` says that there is no message, and a message no team sent is answered in everyday words.
formats: |
  team-act  words  what you send your team. A run is a team's when the message that woke you in it carries the line `[team <name> · you are <member>]`; the messages that follow in the same exchange do not repeat that line. In a team's run, give one JSON value alone, nothing before or after it -- one element, or a list of elements, each `{"do": {...}}`, `{"ask": {"to": ..., "text": ...}}`, `{"re": <id>, "text": ...}` or `{"info": {"to": ..., "text": ...}}` --, or give `[]` when you have no message for the team; hand it by its print call: the team reads nothing else you write. In a run where no message carried that line, no team reads you: answer in everyday words, without JSON
---

# TEAM-ACT — the form of a team act

A team reads the `words` of its members' runs: each production pp took by a print call, and nothing else. A `words` that is one `team-act` value is an act: the team routes it as soon as it reads it. A text a member writes outside a print call -- before a call, or as the last message of its launch -- is no `words`: the team does not read it.

`team start` writes `TURN.md` in the team's directory: an overlay of the kit's turn that carries `output: team-act` and nothing else. Every run opened under that directory therefore asks for this form on the WORK line of its turn: `WORK team-act => terminal`, handed by its print call. An entry's step may name the form too (`INFER team-act => terminal`).

When a step asks for `team-act`, what you give depends on who reads you in the run:

| your case | how you recognize it | what you give |
|---|---|---|
| the run is a team's, and you have one or several messages for it | the message that woke you in the run carries the line `[team <name> · you are <member>]`; the messages that follow in the same exchange do not repeat it | one JSON value alone, nothing before or after it: one element, or a list of elements |
| the run is a team's, and you have no message for it | the same line, at the message that woke you | `[]` |
| no team reads you | no message of the run carried that line: a principal talks to you in a run opened under the team's directory | everyday words, without JSON |

The format is declared here once, for the house and every agent it holds. The contract of the acts -- the four kinds of message, what you owe, sending each message once -- is the package's part of the standing orders (`system/SYSTEM.md`).
