---
description: an integrator merges the accepted commits on an integration branch, then moves the main branch to it
values: |
  remote = origin -- the name of the remote the branches are pushed to
  base = main -- the branch every piece of work starts from
  integration = integration -- the branch where the accepted contributions are merged
---
# How you integrate

Bring the accepted contributions together on `{integration}`, then move `{base}` to the result.

1. Fetch `{remote}`. Take only the contributions whose review says `accepted`, each at the exact commit the review names.
2. Write down the commit `{remote}/{base}` points to: it is `<start>` below. Create `{integration}` from it, replacing any earlier one: `git switch -C {integration} <start>`. Merge the accepted commits into it, one at a time. When a contribution is built on another one, merge that one first.
3. Settle each conflict yourself, and write it down. Run the team's checks on the result.
4. Push `{integration}` to `{remote}`, replacing the earlier one: `git push --force {remote} {integration}`. Only you push this branch.
5. Move `{base}` on `{remote}` to the commit of `{integration}`, only if `{base}` still points to `<start>`: `git push --force-with-lease={base}:<start> {remote} {integration}:{base}`. If `{base}` has moved since, start again at step 1.
6. Answer with the commits you merged, the commit `{base}` now points to, the conflicts you settled, and the checks with their results.

The integration is done when `{remote}/{base}` points to the commit you named. To check it, the member who receives your answer fetches `{remote}`, checks that `git rev-parse {remote}/{base}` gives that commit, and that each merged commit is in it (`git merge-base --is-ancestor <commit> {remote}/{base}` succeeds, with each merged commit in place of `<commit>`).
