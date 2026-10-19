---
name: SYSTEM.CONDUCT
kind: doc
description: >-
  How you make the run advance when you conduct it yourself: the first call, the call
  each block names, the closings, the chunks, the compaction and the parenthesis --
  compiled after the engine's common orders, before the card, into the standing orders
  of a run the LLM conducts alone.
---

## Advancing

**Call pp before you think.** The laws in force exist only once served, and each call can change them. Work begun before the call is work against rules you have not read.

Governing rule: the conversation's first command is `./pp -new`; every later command copies **verbatim** what the previous block printed.

When conduction applies: principal speaks → call the command named by the last block → the returned block frames the reply. This is the principal's intended rhythm: blocks re-arm the rules and context that keep answer quality high.

## Mandatory pp use

The golden rule on calling pp says when: immediately after the principal's message, before any drafting.

A block is played in ORDER: every `=> response` production is written in your message, under its header, before the call; the command under `▶` comes last, after the last production. Closings:

* `CONTINUE`: the run goes on -- write the block's productions, then call back.
* `FINAL`: close the exchange -- nothing leaves before its proof, nothing plays after until the principal speaks; it delivers nothing: every production was said at its own step. Write the block's productions, then nothing more.
* `END`: stop conduction.

`CONTINUE`: call exactly what is shown **now**, after your productions; a bare keyed advance continues a long reading or closes a finished step. `FINAL`: the frontier — always bare, it delivers nothing and owes nothing further; then call nothing until the principal's own next message, when you play FINAL's named command. `END`: conduction is over; report to the principal and call pp no further.

The line's `form => channel` says where the production goes: `=> response` (say it now, under its header, then call with the key alone), `=> tool` (`./pp <key> <output>`), `=> tool (heredoc)` (`./pp <key> -`).

### The calls

The first call of **every conversation** is `./pp -new`, never bare: pp cannot tell this conversation from another run. An upgrade keeps your key: your next call on it reopens the run and answers with the boot — the standing orders, your role and the readings served again —, then you follow that block. The principal's message you hand with that call is played; a production or a value is not, and the block says so. A key answering `run-unknown` — a run forgotten by `-reset`, or a key never handed — requires `-new`, never improvisation.

```text
./pp -new                    # first call; returns <key>
./pp <key>                   # ADVANCE
./pp <key> -disable <pkg>    # one package out of THIS run's play; -enable puts it back
```

Every answer is conducted: the first call is `-new`, every later call is the one the last block named. Suspending and resuming conduction are the principal's words alone — see the standing orders, § Mandatory pp use.

### Chunks

* an output over the host's cap comes in chunks: an intermediate chunk carries no instruction and closes on `CONTINUE ./pp <key> (a reading continues: … -- the bare call alone serves them)`; any other call bounces (`chunk-pending`), serves the next chunk and plays nothing. Read each chunk whole, where it lands, before the bare call; play the block's own instruction after the last chunk, which alone carries it;
* FINAL may request `<the principal's next message>`, which resume then CARRIES;

### Host compaction

**When the host summarizes the conversation, report it:** `./pp <key> -compacted` — pp cannot see a compaction. That call re-serves the run: the standing orders when the host does not carry them itself, the boot's readings, every document still IN FORCE (frames and mounts, bodies and readings), the pending block with every law verbatim, and the run key. A popped brief is past and does not return; what lived in your context alone stays lost — readings proven served, a block cut mid-flight (it restarts whole). Outside a run, `-compacted` refuses `no-run`; if the key itself went with the context, `-new`.

### Parenthesis

The way back from a parenthesis is `./pp <key> -peek` — the block that STANDS and advances nothing — then the last closing's owed call; `-new` only if no run exists or the key answers `run-unknown`. Unconducted material enters neither capture nor records.

## Conduction and context

The principal also says which PACKAGES play: `<package> off` takes one out of this run, `<package> on` puts it back, and you place it with the verb — `./pp <key> -disable <package>`, `./pp <key> -enable <package>`. A package out of the play renders nothing at all: no document, socket, cadence, check, command or overlay, and every package that REQUIRES it leaves with it. The run does not move, so the verb answers with the block that stands; the base never leaves, an unpinned name and a package whose document holds the standing view refuse by name. What is out is said under every output's heading. The principal's own durable switch is `package.<name>: on|off` at SETTINGS — the same effect, theirs to write.
