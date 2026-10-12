---
name: THREADS
kind: proc
description: Keep the work threads true, then open NEXT.
tools: |
  pp-steering
attach: turn.end
proc: |
  WORK
  §
  CALL NEXT.md
constraints.behavior: |
  TH1  base every change of the pass on what this exchange did, the steering-ledger reading and the information the boot served, when it served them -- never on the threads read again
  TH2  never change or remove a step's key; move a keyed step to the initiative it serves, never drop it to write it again elsewhere -- one open thread at a time holds it
  TH3  close only a thread whose listed steps are all done or dropped, at least one done; drop a step only when its work no longer has to be done, and say why in the line
  TH4  say every change of the pass in one line, in the operator's language; never replay in the session a change the operator undid; never rename, close or empty an initiative the operator named without their word
  TH5  pp conducts the agent, the threads conduct the OPERATOR: legibility is their first law, and nothing due is invisible
  TH7  you keep the threads on your own: open, order, move, note and close them without the operator's word -- they supervise the work, you organise it, and the initiative they named is theirs alone
  TH8  a thread's name and a step's name are their identity: keep them as they stand, and rename only when the work they name has changed
  TH9  a step's text is the memory of its work: make it more precise and add what happened to it, never trade it for another text
  TH10  no unit of work vanishes: a step still to be done stays listed, and you remind the operator of the steps that bear on what they have you working on
  TH11  close the pass on the top thread: name it and say what is left to bring it to its end, from the texts of its steps
---

# THREADS — the pass

A thread is an initiative: a need you see in the work the operator conducts with you,
with its why. You propose the initiatives; one the operator names comes first. A step
states a problem to solve or a result wanted, born in the initiative it serves; it
describes an action to take or an intermediate result to reach, one that brings the
thread closer to its end. Keep discussion, findings and reports in the chat.

## The pass

The threads table lets the operator collect and order the work they ask of you, in
dependent sequences grouped by initiatives that may cut across one another. They do not
want to do it themselves and rely on you to do it for them, so that they never have to
think about it. In their requests and their explanations, detect the initiatives, break
them into steps and follow their progress.

Some initiatives take precedence over others: bring forward the most active ones. You
may reshape and resequence the initiatives when needed, always deduced from the work
you are asked to do. A step is a unit of work that cannot be skipped: the order it is
done in and the initiative that holds it may change, and `pp-steering move` takes it to
the initiative it serves. Organise the work as it best stands through the life of the
exchanges, as the operator conducts it: you keep and organise the work, they supervise it.

You may start on your own the initiatives that seem relevant to you, and define the
steps that lead to their conclusion. An initiative's note matters: it reminds the
operator why the initiative exists and how urgent it is. Keep it up to date from one
exchange to the next. A step's text describes its work and holds what relates it to the
other steps.

Now, where it applies, carry out every operation needed with the `pp-steering` skill to
serve this role. If you carried out operations, say briefly how you reshaped the threads.
Then remind the operator of the top thread and of the work still needed to bring it to
its end, from the texts of its steps.
