---
description: one Git repository, and one branch with its own worktree for each batch of work
values: |
  repository -- the path of the clone of the code the worktrees are made from
  worktrees -- the folder where each batch gets its worktree
  remote = origin -- the name of the remote the branches are pushed to
  base = main -- the branch every batch starts from
---
# Where the work is

The code is in the Git repository `{repository}`. Each batch of work gets its own branch and its own worktree, so two batches never share files on disk.

When you receive a batch:

1. Fetch in `{repository}` (`git -C {repository} fetch {remote}`) and start from `{remote}/{base}`.
2. Create the branch `<batch>` from it, in a new worktree: `git -C {repository} worktree add -b <batch> {worktrees}/<batch> {remote}/{base}`.
3. Work only in `{worktrees}/<batch>`. Never change the files of `{repository}` itself, nor those of another batch's worktree.

`<batch>` is the name of the batch you received. Your worktree is ready when `git -C {worktrees}/<batch> status` shows the branch `<batch>`. Write down the commit of `{remote}/{base}` you started from, and give it in your answer as the start of your work. The member who receives your work checks that this commit is on `{remote}/{base}`: `git -C {repository} merge-base --is-ancestor <start> {remote}/{base}` succeeds, with that commit in place of `<start>`.
