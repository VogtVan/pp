---
name: PLANS-TEMPLATES
kind: doc
description: >-
  The templates a plan may be born on, served when PLAN is opened and last at every mount: one object per template the tree sees, provided as the reading `plan-templates`.
provides: plan-templates
with: pp-plan templates --json
payloads: plan-templates
mount: plan.plan.initialize
---

# PLANS-TEMPLATES — the templates, for the birth of a plan

`plan-templates` is what `pp-plan templates --json` says: one object per template the tree
sees — the tree's own (`plans/_templates/`) first, then the shared root's, then the
product's. Each object gives its `name`, its `origin` (`tree`, `shared` or `product`), its
`description`, `leaf` (its items are todos), the `chain` it opens from itself down to its
leaf, and its `sections` in their order. A product template that the tree replaces with its
own says `shadowed`. A template that cannot serve carries a `refusal` instead.

A plan is born on the template that `--template <name>` names, and on `plan` without it.
Choose the template here; never guess one.
