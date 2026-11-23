---
description: deliver by committing on your branch and pushing it, the delivery named by its commit
values: |
  remote = origin -- the name of the remote the branches are pushed to
---
# How you deliver

1. Commit your work on your branch, under your own name. Before you commit, check with `git status` that every file the work needs is included, and nothing else.
2. Push your branch to `{remote}`.
3. Answer the member who gave you the work with your branch, the full id of the commit you delivered, the commit your work starts from, and each check you ran with its result.

Your work counts as delivered only when your branch on `{remote}` points to the commit you name in your answer. Work that is only on your disk is not delivered: push first, answer after.

To check a delivery, the member who receives it fetches `{remote}` and checks that `git rev-parse {remote}/<branch>`, with the branch the answer names in place of `<branch>`, gives the commit named in the answer. A different commit, or no branch, means the work is not delivered.
