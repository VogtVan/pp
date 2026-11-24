---
description: one branch per plan, kept and delivered by the member who holds the plan, on a plain shared repository
values: |
  contributors = contributors -- the role of the members who hold plans and deliver their work
  reviewers = reviewers -- the role of the members who review what is delivered
documents: |
  all seasons/plan-branch-summary sources/plan-branch remote/bare-remote
  {contributors} contribution/pushed-commits
  {reviewers} review/read-commits
---
