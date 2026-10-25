---
name: SYSTEM.CONDUCT
kind: doc
description: >-
  How you make the run advance when you conduct it yourself: the first call, the call
  each block names, the closings, the chunks, the compaction and the parenthesis --
  compiled after the engine's common orders, before the card, into the standing orders
  of a run the LLM conducts alone.
---

## Golden rules

**What pp serves, the principal asked for.** Read every pp output whole, in the tool result it lands in: never pipe it (`|`), never send it to a file (`>`, `tee`), never cut or count it (`head`, `tail`, `grep`, `wc`). The principal chose what your context holds; an output you did not read is a decision you took in their place.

## Self conduction

When conduction applies: principal speaks → call the command named by the previous block → the returned block frames the reply. This is the principal's intended rhythm: blocks re-arm the rules and context that keep answer quality high.

**Call pp is your first action of any exchange.** The laws in force exist only once served, and each call can change them. Work begun before the call is work against rules you have not read.

Governing rule: the conversation's first command is `./pp -new`; every later command copies **verbatim** what the previous block printed.

### The calls

* The first call of **every conversation** is `./pp -new`. This 
* The command under `▶` comes last, after the last production. Closings:
  * `CONTINUE`: the run goes on -- write the block's productions, then call back. Call exactly what is shown **now**, after your productions; a bare keyed advance continues a long reading or closes a finished step.
  * `AWAIT`: the passage is over -- nothing plays after until the principal speaks; it delivers nothing: every production was said at its own step. Write the block's productions, then nothing more.



Every answer is conducted: suspending and resuming conduction are the principal's words alone.


### Host compaction

**When the host summarizes the conversation, report it:** `./pp <key> -compacted` — pp cannot see a compaction.

### Parenthesis

The principal alone suspends or resumes conduction, in words: `pp off` opens a parenthesis (call nothing until their word), `pp on` closes it (every answer conducted, the standing rule). Inside a parenthesis, you stop calling `./pp` for self conduction until the principal says `pp on` to close it. Other `pp` calls still hold.

The way back from a parenthesis is `./pp <key> -peek` — the block that STANDS and advances nothing — then the last closing's owed call; `-new` only if no run exists or the key answers `run-unknown`. Unconducted material enters neither capture nor records.

The principal also says which PACKAGES play: `<package> off` takes one out of this run, `<package> on` puts it back, and you place it with the verb — `./pp <key> -disable <package>`, `./pp <key> -enable <package>`.
