# house-ground — one ground the agents of a house take

## What you write

At the house, a document in its `procs/`, `HOUSE.md`: the laws, the offers and the readings
every agent of the house shares. Its `serve:` rows that name no tree read what the house
reads (see `context/material`).

At each agent that takes it, one line in an overlay of its `TURN`, `procs/TURN.md`:

```yaml
imports: |
  HOUSE.md
```

## What you get

- From the agent's first block, HOUSE's laws, its offers and its body are there, and its
  readings are served (see `composition/import`).
- A row of HOUSE's `serve:` that names no tree reads what the house reads. A path is read in
  the house's workspace: when the agent holds a file of the same path, the agent's file stays
  unread. A path the house reads in its machine's copy (`engine/patterns/...`) is read there.
- A file the agent alone holds is not served, and the block says so.
- A row that names a tree (`@<name>`) reads that tree: the house's file of the same path stays
  unread.
- TURN's frame holds HOUSE: at the park its offers stand, for the agent's call and for the
  principal's; at the next exchange its laws and offers hold, its body and its readings are not
  served again.
- An agent without the line has nothing of HOUSE: the line is its consent.

## When to use it

- Give every agent of a house the same laws, the same doors and the same references, written
  once at the house.

## What refuses

- What `composition/import` refuses: a cycle, an address found nowhere, a value badly written.

## The demonstration

- `procs/HOUSE.md` — the ground: its law `HG1`, the offer `+SALON`, the row `notes/charter.md`.
- `procs/SALON.md` — the house's door: its law `HG2`, one `WORK`.
- `procs/TURN.ground.md` — the agent's overlay of `TURN`, importing `HOUSE.md`; placed at
  `.pp/procs/TURN.md` of the agent.

## The test

`tests/patterns/packaging/house-ground.py` plays one house and two agents: the agent that
imports has HG1, SALON and HOUSE's body at its first block; the house's charter is read where
the agent holds its own, the agent's own `notes/visitor.md` is not served and said, a row
`@shelf` reads the shelf and not the house's file, a row of the machine's copy is read there; at
the park the agent's `-s SALON` opens SALON on its run, the principal's on another run; the next
exchange keeps HG1 and SALON, nothing served again; the agent without the line has nothing. The
rows of the visitor, the shelf and the machine's copy are added to HOUSE by the test.
