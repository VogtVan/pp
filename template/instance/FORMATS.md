---
name: FORMATS
kind: doc
description: >-
  This instance's OUTPUT formats -- the operator's own file, seeded at install,
  never re-synced. Redeclare a name here to customize it: the instance's
  definition overrides the packages' and engine's.
---

# FORMATS — customize the forms your agent answers in

Declare a `formats:` key in the front matter above, one format per line:

```
formats: |
  table  stdin  a titled markdown table -- your house style here
```

* dialect: `name  inline|stdin  definition` — MODE says how captured
  production travels (`inline` on the call, `stdin` piped);
* redeclaring a name HERE overrides packages' and engine definitions —
  customize by redeclaring at home, never editing a bundle;
* duplicate names at ONE level refuse (`format-doubled`);
* the catalog (`tools.md`) teaches the effective enumeration at every boot —
  rebuild it after edits (`./pp -build`).

## Three examples, ready to paste — orthogonal on purpose

```
formats: |
  table  stdin   markdown table opened by a bold one-line takeaway; named columns, max 12 words/cell
  theme  stdin   one-line bold theme, then 2-4 short sections with headings tuned to it
  brief  inline  at most three 15-word bullets, verdict first
```

* `table` REDECLARES a kit format: the same name then serves YOUR
  house style everywhere it is requested — supersession is the point.
* `theme` and `brief` are NEW: once pasted, any `output: theme` in your
  proc is served and enforced exactly like built-ins.
* The three are deliberately orthogonal — visual form, narrative structure,
  density: distinct levers on the same answer.
