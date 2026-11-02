# initialize — act once when a proc starts, and hold it while it lives

## What you write

Nothing in the proc itself: every proc has an entry point named `<proc>.initialize`
(`office.initialize` for OFFICE). A contributor names it in its front matter, with one
of the two verbs of `composition/hook` and `composition/mount`:

- `attach: office.initialize` — a proc called once at the entry;
- `mount: office.initialize` — a document mounted at the entry.

## What you get

- Before the proc's first step, its entry plays once: what attaches is called, what
  mounts is mounted, in the same order as at any point.
- Their laws stay on screen for as long as the proc's frame lives: after the called
  contributor is done, and at every passage of a proc that is the run's root.
- Their bodies are served once, at the entry; they are not served again.
- When the proc ends, what its entry brought leaves with it.

## When to use it

- Give a proc laws or readings for all of its life, played once instead of at every
  passage — a member's identity, for instance.
- Prepare a proc before its first step without writing a step for it.

## What refuses

- A proc that writes `HOOK <proc>.initialize` refuses `socket-reserved` when the
  instance is built: the entry point exists without a line.

## The demonstration

- `procs/OFFICE.md` — the proc: one `WORK`.
- `procs/BADGE.md` — mounted at `office.initialize`: its law `IN1`.
- `procs/KEYS.md` — called at `office.initialize`: its law `IN2`, one `INFER`.
- `procs/VISIT.md` — calls `ROOM.md`, then one `WORK`.
- `procs/ROOM.md` — the called proc: one `INFER`.
- `procs/GUEST.md` — mounted at `room.initialize`: its law `IN3`.
- `procs/RESERVED.md` — writes `HOOK reserved.initialize`: it refuses.

## The test

`tests/patterns/composition/initialize.py` plays them: OFFICE opens on KEYS's step with
BADGE's and KEYS's bodies and laws once; `IN1` and `IN2` stay after KEYS ends and at the
next passage, nothing served again, under both conductions; `IN3` binds ROOM's step and
leaves with ROOM; RESERVED refuses `socket-reserved`.
