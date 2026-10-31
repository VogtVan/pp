---
name: PP.CONDUCT
kind: doc
description: >-
  The calls that make the run advance when you conduct it yourself -- opening the run,
  the bare call, a cut reading, a parked run, the way back from a parenthesis --
  compiled after the common card into the standing orders of a run the LLM conducts
  alone, and joined to the card a harness receives.
---

## The calls that advance the run

| Form | Effect |
|---|---|
| `./pp -new [<message>]` | Open a run; the words after it are the principal's message. `-new` returns the run's key. |
| `./pp <key>` | Advance: the next block, the next chunk of a reading, the resume of a parked run. |
| `./pp <key> "<message>"` | Resume a parked run with the principal's message. |
| `./pp <key> -skip` | Drop the rest of a cut reading: its closing comes at once, the dropped part unread. |

**Open the conversation's run**, with the principal's first message:

    ./pp -new "fix the failing import in the parser"

**Advance**: the closing shows `▶ CONTINUE` and the bare call, no value owed:

    ./pp 3f9a1c

**Read the rest of a cut reading**: the closing says `a reading continues`; only the bare
call serves it:

    ./pp 3f9a1c

**Drop the rest of a cut reading**: the block's closing comes at once:

    ./pp 3f9a1c -skip

**Come back after a parenthesis**: see the block that stands, then play its owed call:

    ./pp 3f9a1c -peek

**Open a run again** when a keyed call refuses `run-unknown` or `no-run`:

    ./pp -new
