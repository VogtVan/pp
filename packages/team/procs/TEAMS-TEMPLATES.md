---
name: TEAMS-TEMPLATES
kind: doc
description: >-
  The templates read for the welcome of the teams space: one object per template, provided as the reading `team-templates`.
provides: team-templates
with: pp-team templates --json
---

# TEAMS-TEMPLATES — the templates, for the teams space

`team-templates` is what `pp-team templates --json` says: one object per template the house sees,
with its `template` (its name, `<directory>/<name>`), its `kind`, its `origin` (`house` or
`package`), its `description` and the `values` it asks (`name`, `description`, `default`: `null` when
the principal must give it). A `preset` gives ready-made lines for `TEAM.md` or `SEASON.md`: its
`documents` (`key`, `documents`); a team preset also gives its `form`, its `members`, its `root`, its
`reports` and, when it has some, its `roles`. A `document` is a text the members receive. A template
that names packages says them under `requires`. A template that cannot be read has a `refusal`
instead.
