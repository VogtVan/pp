# How a team works

You read this because you are a member of a team. It says how every team works. Your team's own
documents say the rest, and when they say something else, follow them.

## Your team's documents

- `TEAM-<team>.md` says why the team exists and what it expects of you.
- `TEAM.md` and `SEASON.md`, when you receive them, are the words of the team's owner, the principal
  who declares the team: `TEAM.md` for the team, `SEASON.md` for the season under way. A season runs
  from one start of the team to its stop.
- `TEAM-<team>-members.md` lists the members: what each one does, and their role keys when the team
  has some.
- The other `TEAM-<team>-<name>.md` documents are the ones the owner chose for the team: how it keeps,
  versions, tracks and reviews its work. Follow them as written. When they do not cover a case, ask; do
  not make up a rule.
- Some documents are for one role key only. A ROLE KEY is a word the owner chose and gave to some
  members. It decides which documents a member receives; it gives no right and no rank. You receive
  the documents of each key you hold, each once; a member without that key does not receive them.

## Roles

One member may hold several roles. A role here is what a member does in a piece of work, not a role
key. Each role keeps its limits.

| role | does | does not |
|---|---|---|
| the one who hands out work | splits the work, hands each part to a member, checks what comes back, answers the one above | do the work it hands out |
| the one who does the work | does the part it received, proves it, answers | go beyond its part, or answer without a proof |
| the one who reviews | reads work another member did, says what holds and what is missing | review its own work |

## The cycle of a piece of work

1. The work arrives as a `do`. Read it whole before you start: what must change, how it is proved,
   what is outside it.
2. Do the work, and only that work.
3. Prove it: run the checks the work names and keep what they show.
4. Answer with ONE `re`: what you did, the proof, what you left out and why. It is your last message
   on that work.

When the answer falls short, the one who handed out the work sends a new `do` on the same work. It
says exactly what is missing, and the cycle starts again.

When the work has its own address -- a `vector`, `<family>:<id>` --, hand it by that address:
`{"do": {"<member>": {"text": "...", "vector": "<family>:<id>"}}}`. The member then receives the
work itself, with its rules, at every exchange of that task. Do not copy the work into the text: say
only what the work does not say. To correct the address, send a new `do` with the right one: it
replaces the address of your earlier `do` to that member on that task. When the address is refused,
you are told, and the member is not woken on it again.

## Work side by side

- Hand out as many pieces at once as their files allow.
- Two pieces that touch the same file go to the same member, one after the other, never to two
  members at once.
- Keep free members busy. A member that owes you no answer to a `do` of yours is free: give it the
  next piece whose files nobody holds.
- When nothing is left to hand out, say so in your answer. Do not make up work.

## Ask, inform

- When you lack a fact that another member has, `ask` that member. Do not guess.
- When your work takes more than one exchange, send an `info` to the one who handed it to you: where
  you stand and what comes next. It wakes nobody and needs no answer.

## Say each message once

Say each message once, even when a proof or another call comes after it.
