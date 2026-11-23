---
description: a review service -- one review request per delivered branch, its commands given as values, the merge done outside the team
values: |
  remote = origin -- the name of the remote of the review service
  open-request -- the command that opens a review request for a branch, `<branch>` standing for the branch
  show-request -- the command that shows a review request, `<request>` standing for its number
---
# The review service

The branches are pushed to `{remote}`, a review service.

- When you deliver a branch, open its review request: run `{open-request}`, with the branch in place of `<branch>`. Give the number of the request in your answer.
- To see where a request stands, run `{show-request}`, with its number in place of `<request>`.
- Never merge a request yourself: merging is done outside the team.

A request is open when `{show-request}` shows it open, on the branch and at the commit the delivery names. The member who receives your answer runs `{show-request}` with the number you give to check it.
