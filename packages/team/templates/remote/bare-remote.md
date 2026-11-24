---
description: a plain shared Git repository that holds the main branch and the delivered branches
values: |
  remote = origin -- the name of the shared remote
  base = main -- the branch every piece of work starts from
---
# The shared repository

`{remote}` is a plain Git repository that the whole team can read and push to. It holds `{base}` and the branches the team delivers. It has no review requests: announce each delivery in your answer.

- Fetch `{remote}` before you start a piece of work, and before you read someone else's.
- Push only your own branches. Never force a push on a branch another member pushed.
- Never push to `{base}` yourself: it moves only by the integration that the documents you receive describe, or outside the team when none describes one.

A branch is shared when `git ls-remote {remote} <branch>`, with your branch in place of `<branch>`, shows the commit you pushed. The member who receives your answer runs the same command to check it.
