---
description: the summary of the season worktree-and-requests
values: |
  contributors = contributors -- the role of the members who write and deliver the work
  reviewers = reviewers -- the role of the members who review what is delivered
---
# How the team {team} works

Do each batch in its own branch and worktree.

- If you have the role `{contributors}`, do a batch and deliver it as a pushed commit, with a review request.
- If you have the role `{reviewers}`, read the exact commit delivered.
- Never merge a request: requests are merged outside the team.

A batch is done when its commit is delivered, its review says `accepted`, and its review request is open on that commit.
