---
name: SYSTEM.CONDUCT
kind: doc
description: >-
  The kit's conducted turn, for a run the LLM conducts: the three steps, the
  parenthesis, the closings that make it call pp.
---

## Conducted turn

Every pp turn:

1. operator sends a chat message;
2. run the exact pp command shown;
3. follow pp instructions until told to stop.

After calling pp, follow its instructions. Call it again only when instructed; otherwise wait for the next operator message.

The operator alone suspends or resumes conduction, in words: `pp off` opens a parenthesis (call nothing until their word), `pp on` closes it (every answer conducted, the standing rule). A parenthesis is never a closure: the run and its key survive; resume with `-peek`, then the owed call, as the standing orders' **“Parenthesis”** says. No setting carries this: you are told.

Closings:

* `CONTINUE`: call back now.
* `END`: stop conduction.
