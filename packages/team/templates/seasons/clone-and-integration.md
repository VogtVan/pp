---
description: one clone per member, the contributions pushed to a shared repository, an integrator who merges them
values: |
  contributors = contributors -- the role of the members who write and deliver the work
  reviewers = reviewers -- the role of the members who review what is delivered
  integrator = integrator -- the role of the member who brings the accepted work together
documents: |
  all seasons/clone-and-integration-summary sources/run-clone remote/bare-remote
  {contributors} contribution/pushed-commits
  {reviewers} review/read-commits
  {integrator} integration/integration-branch
---
