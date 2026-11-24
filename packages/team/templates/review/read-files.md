---
description: a reviewer checks each delivered file against its checksum, then reads it against the task
values: |
  result-folder -- the folder where members deliver their finished work
---
# How you review

Review the work other members deliver to `{result-folder}/<task>/`. `<task>` is the task the answer names.

1. Read the answer that announces the delivery: the task, its files, the checksum of each.
2. Check that every file is there and that its checksum is the one announced. If a file is missing or different, the delivery is incomplete: say so, and do not review it.
3. Read each file against what the task asked. Write down each point that falls short, with its file and its place in the file.
4. Answer with your verdict, the task, and the checksums you read: `accepted`, or `changes needed` with the list of points.

A review is closed when you have answered with a verdict that names the checksums you read. To check a verdict, the member who receives it compares those checksums with the files now in `{result-folder}/<task>/`: a file changed since is not covered by the review.
