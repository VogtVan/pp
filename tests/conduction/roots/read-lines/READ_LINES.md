---
name: READ_LINES
kind: proc
output: any
description: the simple step -- one WORK, four lines read one at a time, each said as it is read
proc: |
  WORK
---

# READ_LINES

The file `LINES.txt` in your working directory holds four lines. Read them ONE at a time
with your file tool -- one read per line, never the whole file at once. After each read,
say in your message the line you read, as one sentence: « Line n: … ». When the four are
said, say « done ».
