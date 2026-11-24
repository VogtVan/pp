# qualifiers — decide when a contributor plays, and in which rank

## What you write

Two keys in the front matter of a contributor — a proc that attaches to a point, or a
document that mounts there (see `composition/hook` and `composition/mount`):

- `when: "@<DOC>.<field>"` — the contributor plays only when that field is true
  (`when: "@SWITCH.open"`). The field may be in any document, `SETTINGS` included.
- `order: |` then one line `<point> before <package>` or `<point> after <package>` — the
  contributor's rank at that point, against the contributors of that package
  (`crew.yard.open before crew`).

## What you get

- With `when:` false, the contributor does not play: an attached proc is not called, a
  mounted document does not enter. The same holds for a document a host names in its
  `mounts:` line: its own `when:` decides. The other contributors of the point are
  untouched.
- With `when:` true, it plays as if the key were not there.
- Without `order:`, the contributors of a point play in their derived order: those of a
  package before those of your instance, then by name.
- With `order: … before <package>`, the contributor plays just before the first contributor of
  that package at that point; `after` puts it just after the last. Only the contributor that
  writes the line moves: the others keep their derived order.

## When to use it

- Switch a contributor on or off by a setting or a field, without removing it.
- Make your contributor play before a package's own, at a point that package opens.
- A rank names a package, never a document: the contributor states its own place.

## What refuses

- Two contributors whose `order:` each ask to come before the other refuse `order-cycle`,
  both named; nothing plays.
- A preference toward a package that is not in play is ignored.

## The demonstration

- `procs/GATEHOUSE.md` — a host: `HOOK gatehouse.open`, then one `INFER`.
- `procs/PORTER.md` — called at `gatehouse.open` when `@SWITCH.open` is true.
- `procs/LANTERN.md` — mounted at `gatehouse.open` when `@SWITCH.open` is true: its law `QL1`.
- `procs/ATRIUM.md` — a host whose `mounts:` names `CANDLE.md` at `atrium.open`.
- `procs/CANDLE.md` — entering ATRIUM when `@SWITCH.open` is true: its law `QL2`.
- `procs/WICK.md` — mounted at `atrium.open` with no guard: its law `QL3`.
- `procs/SWITCH.md` — the field every guard reads, `open: false`.
- `procs/CLERK.md` — a contributor at `crew.yard.open`, the point of a package named `crew`.
- `procs/EAGER.md` — the same, with `order: crew.yard.open before crew`.

## The test

`tests/patterns/composition/qualifiers.py` plays them, with a package `crew` written by
the test (its host `YARD` hooks `yard.open`, its contributor `HAND` attaches there):
with `SWITCH` shut, PORTER, LANTERN and CANDLE stay out while WICK enters; open, they
play; at the yard, HAND plays before CLERK; EAGER plays before HAND while CLERK keeps its rank
after HAND; two packages that each want to come first refuse `order-cycle`.
