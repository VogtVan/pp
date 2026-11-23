---
description: deliver by copying the finished files to the results folder, each copy checked by its checksum
values: |
  draft-folder -- the folder where members write their work in progress
  result-folder -- the folder where members deliver their finished work
---
# How you deliver

`<task>` is the name of the task you hold.

1. Finish the work of the task in `{draft-folder}/<task>/`.
2. Copy the finished files to `{result-folder}/<task>/`: every file the task asks for, and nothing else.
3. Check the copy: compute the checksum of each file in `{result-folder}/<task>/` (for example with `sha256sum`) and compare it with the checksum of its draft. They must be the same.
4. Answer the member who gave you the task with the list of the files you delivered and the checksum of each.

Your work counts as delivered only when every file you list is in `{result-folder}/<task>/` with the checksum you give. A partial copy is not a delivery: say what is missing instead.

To check a delivery, the member who receives it computes the checksum of each listed file in `{result-folder}/<task>/` and compares it with the answer. A file missing or a checksum that differs means the work is not delivered.
