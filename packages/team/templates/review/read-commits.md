---
description: a reviewer reads the exact commit a delivery names, and the verdict names that commit
values: |
  remote = origin -- the name of the remote the branches are pushed to
---
# How you review

Review the commits other members deliver.

1. Fetch `{remote}`. Check that the branch of the delivery points to the commit the answer names. If it does not, the delivery is incomplete: say so, and do not review it.
2. Read the changes between the commit the work starts from and the delivered commit (`git diff <start>..<commit>`, with the start the answer names in place of `<start>` and the delivered commit in place of `<commit>`), and nothing else: not the branch as it is later, not your own copy.
3. Run the checks the work names, on that exact commit.
4. Answer with your verdict and the commit you read: `accepted`, or `changes needed` with each point, its file and its line.

A review is closed when you have answered with a verdict that names the commit you read. A new commit on the branch needs a new review: your verdict covers only the commit it names. To check a verdict, the member who receives it compares that commit with the one the delivery names.
