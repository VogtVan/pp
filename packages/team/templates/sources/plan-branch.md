---
description: one Git repository, and one branch for each plan, kept by the member who holds the plan
values: |
  repository -- the address of the Git repository of the code
  remote = origin -- the name of the remote the branches are pushed to
  base = main -- the branch every plan starts from
---
# Where the work is

The code is in the Git repository `{repository}`. Each plan has its own branch, `<plan>`, named after the plan.

- When you start a plan, fetch `{remote}` in your own clone of `{repository}` and create the branch `<plan>` from `{remote}/{base}`.
- Keep that branch for as long as the plan runs: put every delivery of the plan on it.
- Commit only on the branch of the plan you hold. Never commit on another member's plan branch, nor on `{base}`.
- For each delivery, your work starts from your previous delivery on `<plan>`, or from the commit of `{remote}/{base}` you created it from for the first one.
- Before each delivery, fetch `{remote}`; if `{remote}/{base}` has new commits, merge `{remote}/{base}` into your branch and settle the conflicts yourself.

`<plan>` is the name of the plan you hold. Your branch is in order when `git log {remote}/{base}..<plan>` shows only the commits of your plan. The member who receives your delivery runs `git fetch {remote}` then `git log {remote}/{base}..{remote}/<plan>` to check it.
