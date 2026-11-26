# next

> **Experimental package.** Its procedures and user-facing behavior may change
> between versions.
>
> **Current version:** `0.1.2`

`next` is a package for [Procedural Prompting](../../README.md). It ends every answer
with the principal's two best next choices.

## Role

At the end of every exchange, after the work, pp opens the step `NEXT`. The agent
answers it with one table, the form `choices`: the columns `#` and
`your best choice(s)`, two rows at most. Each choice names its work by its full
address -- a step by its name, a plan node by its path -- and says in one sentence what
it unlocks and where it comes from. When one choice alone is due, the table has one
row; when none is due, it has no row. Whatever else the agent owes the principal in
the exchange comes before the table.

## What other packages plug into it

`next` declares `next.begin`, a socket: a named point where another package attaches
one of its documents. A package may mount a document there: its
readings are served in NEXT's block, above NEXT's brief, computed after the work of
the exchange. `plan` mounts `NEXT_MOVE` there, so that the next move of each open plan
reaches the choices. Without `next`, such a document stays idle (the build says
`mount-dormant` once).

`next` requires only the `kit`. `steering` does not require it: an instance may keep
its steps without ending each answer on choices. In a team, a member's wake-up plays
`next` off unless the season or a profile switches it on.

## Installation

`next` requires the `kit`, which the installer pulls automatically.

For a new workspace:

```sh
uv run pp/engine/pp.py -install <workspace> next -<provider>
```

For an existing pp instance, from the workspace root:

```sh
./pp add next
```

To stop ending answers on choices in one run: `./pp <key> -disable next`.
