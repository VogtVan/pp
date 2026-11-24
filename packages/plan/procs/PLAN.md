---
name: PLAN
kind: proc
description: >-
  Conducts the work of a plan -- a tree of nodes, each an instance of a template that says its sections, its statuses, its place in the chain and the method of its level -- on the principal's GO: mount the node, write one section per call, deliver the items, the closing rising by the script.
output: free
serve: |
  PLAN_CHEATSHEET.md
tools: |
  pp-plan
constraints.production: |
  PN12  a plan law MAY exist: it is written only when it applies to EVERY leaf of the plan -- what does not apply to all descends to the node it applies to; a thesis, a decision or a provenance goes to the body, one dated line (principal's word 2026-08-27)
  PN3  a secret is named by its path and its contract in every artifact and document of the plan.
  PN9  a framing establishes on its node, beside the constraints, the DOCUMENTS TO SERVE -- the readings every future mount of that node carries; one rule, every node alike.
constraints.behavior: |
  PN1  every production under the plan serves its THESIS; outside the frame is a NEW step -- said, and played on its own GO only.
  PN2  a node closes only on OBSERVABLE exit criteria, proof in hand -- nothing is done without its proof.
  PN4  the record follows the act: a status moves by the script in the very turn the work arrives.
  PN5  a framing is an EXCHANGE: the principal's direction is challenged and perspectives opened, the global vision in hand -- drafted, then restituted.
  PN6  a proposed action is ONE decision point of the plan's next move; the deterministic plays in the turn its condition falls -- combining steps is the principal's GO alone.
  PN7  a node is `doing` once a `doing` section of its template is written and `done` once all its items are -- the script deduces the status from the writing, no GO and no verb owed.
  PN10  an implementation plays only on a GO that NAMES it -- the principal's text without a GO is material for a framing.
  PN11  the framing GENERATES the Choices with the constraints -- an architecture or choice the implementation will need is SAID and written to the node's Choices; a deferred one RETURNS to the GO as the involvement settings say, and on a combined GO it is OWED TO THE PLAN, decided in the open.
  PN13  the plan's laws and readings are posed LAST at the framing -- after the sections that frame it and its items proposed, from what the framing read; a law written before is a guess.
  PN14  the body of a plan document is written by the script alone -- `pp-plan section`, one named section per call, a section its template carries; the agent's prose goes through it, and no plan document is opened in an editor.
  PN15  a law is retired or amended only when a rework has changed the context and has introduced a conflict or a miss after a principal request.
---

# PLAN — a tree of levels

A plan is a TREE of nodes under `plans/<slug>/`. Each node names its TEMPLATE (`template:` in its front matter). The template's front matter says the node's SECTIONS in their order, which ones make it `doing` and which reopen it (`statuses`), whether its items are nodes on another template (`next:`) or todos (`leaf: yes`), and its laws and readings. The template's BODY is the method of its level: follow it when you work on a node of that level. The script `pp-plan` alone writes the plan: never open a plan document in an editor.

## What a mount shows you

Mount the node you work on first: `pp-plan mount <address>`.

| document | what you read |
|---|---|
| this proc | how a tree of levels is kept |
| the template of the node you work on | the method of its level, and its laws |
| the template of each node above it | its laws alone |
| each node above it | the sections its template names in `shown:` |
| the node you work on | its whole body, except the sections its template marks `unserved` |
| `PLANS-TEMPLATES`, last | the reading `plan-templates`: the templates the tree sees, also served as soon as this proc opens |

## Writing

- Write ONE section per call: `pp-plan section <address> <Name>`, the prose on stdin. A section the template does not carry is refused (`section-unknown`).
- A plan is born by the first section of its template. Choose the template from the reading `plan-templates`, on screen as soon as this proc opens, and name it with `--template <name>`; without it, the plan is born on `plan`.
- A node under the plan is PREPARED by a line `- <slug> -- <brief>` in its parent's Items. It is born by the first section you write on it, on its parent's `next:` template. Its Items line is not copied into it.
- On a LEAF, deliver each todo as it lands: `pp-plan section <address> Delivery --item <todo>`, what landed and its proof. On a node whose items are nodes, Delivery is a journal.

## The old form

A plan written before the current templates may hold sections they no longer carry: Target, Arbitrations, Survey, Protocol, Decisions, or a Context on a node under the plan. The script reads them, serves them and keeps them, but refuses to write them. When you take up such a node, write in the current form: its Choices before its Items.

## Statuses

- A node is `doing` once a `doing` section of its template is written.
- A node is `done` once ALL its items are `done`; the closing rises to the plan, and the script says each closing. No word closes a node.
- A `redo` section rewritten on a `done` node reopens it, and its ancestors with it.
- `block <address> <reason>` says a stop; the next section you write lifts it.
- `done <address>` closes by hand: a todo, a node with todos left open, a prepared item.

## The work, on the GO

- The principal's GO names the step it approves: a GO on a framing settles its choices, a GO on an implementation lets it start. A question, a challenge or a defect is answered, never coded.
- « frame X/n » gives a prepared item its birth by its first section and frames it in the same turn. Nothing is created before its framing.
- Your involvement in the implementation follows `plan_implementation_care`: `none` (you decide, nothing written), `traced` (the choices written to the plan alone), `told` (said when you report, played without waiting), `asked` (PROPOSED before coding, in the watched sectors), `total` (each choice waits its GO). Without the setting, `asked` applies.
- `plan_implementation_control` lists the sectors `asked` watches: `architecture | contracts | naming | data | flow`. Without the setting, `architecture | contracts`.
- The principal's GO always prevails over the settings. A GO that names no sector approves everything in its own scope.
- When every child of a plan is still only prepared, propose nothing here: the work goes on at the node the plan's next move names, mounted first.
- Do not let a plan close before the project's whole test suite is green: its last node of work runs that suite once.

## What the plan asks next

After every call that writes, the script pushes the plan's NEXT MOVE: the deepest node that waits for something, and the GO it waits for. One line is held per plan, replaced by the next one, cleared when the plan is done. When the package next is there, the line comes in NEXT's block at the end of the answer, under `INFORMATION — plan-next-move`, and a choice of NEXT may carry it to the principal. Without next, `pp-plan next-move` reads it back. The GO it names is the principal's: never play it in the turn.
