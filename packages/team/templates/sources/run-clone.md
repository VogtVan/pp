---
description: one Git repository, and one clone of it for each member, used by no one else
values: |
  repository -- the address of the Git repository each member clones
  remote = origin -- the name of the shared remote in each clone
  base = main -- the branch every piece of work starts from
---
# Where the work is

Work in your own clone of `{repository}`. Never work in another member's clone. In your own clone, create the branches you need.

- For each piece of work, fetch `{remote}` and create the branch `<task>` from the latest `{remote}/{base}`.
- Never copy files from another member's clone. Take what another member delivers only from `{remote}`.
- When `{base}` has new commits, fetch them and start your next piece of work from them.

`<task>` is the name of the task you hold. Your clone is in order when `git remote get-url {remote}` gives `{repository}` and `git status` shows only the changes you made on purpose. Give in your answer the commit your work starts from. The member who receives your work checks that this commit is on `{base}`: `git merge-base --is-ancestor <start> {remote}/{base}` succeeds, with that commit in place of `<start>`.
