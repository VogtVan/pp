---
name: CITED
kind: proc
description: a review whose laws cite the brief, the member and the settings.
constraints.production: |
  TG1  review in @BRIEF.mode mode, for @BRIEF.owner.
  TG2  sign your review as @MEMBER.name, in a @MEMBER.character tone.
  TG3  a served body rides @SETTINGS.proc_body_serve.
proc: |
  INFER
---

Write the review.
