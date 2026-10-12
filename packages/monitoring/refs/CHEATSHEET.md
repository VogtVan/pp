---
name: CHEATSHEET
kind: doc
description: >-
  The campaign method, whole and in ONE place: the from-zero cahier, the
  sessions protocol, the depouillement and the archive. It is the DRIVING
  instance's method, applied in reference; monitoring rides a measured repo as
  capture and stamp alone, transparent to the surface under test. A reference,
  never played.
---

# The campaign cheat sheet — validate a package while measuring it

A campaign plays a package's validation cahier in REAL conducted sessions and
collects the traces: one pass renders BOTH the conformity verdict and the
effort map (volume by subject and package, agent time by function). Its home
is the package's WITNESS batch — reopenable at will, it keeps the cahier, the
coverage register and every campaign's artifacts (KMN7). Campaigns chain in
dependency order: kit first, then the requires topology (KMN8).

## The from-zero cahier

1. **Sweep the code** — the package's own pieces, and for the kit the engine
   too: every module, every document, every console verb. From the sweep,
   derive the ANCHOR REGISTER: the grain is the FEATURE OBSERVABLE IN PP
   OUTPUT. A feature without pp output is SAID so and backed by the bench
   (`./pp -test`), never silently dropped.
2. **The conduction doctrine** — the cahier covers CONDUCTION mechanisms:
   what the agent and the operator live through blocks, closings, proofs,
   repairs, doors, settings and life-cycle cuts. The engine's unit guards
   (console refusals, unknown verbs, invalid input forms) live at the BENCH;
   a refusal enters the cahier only when its subject is the conducted
   reaction it triggers (REPAIR, DEVIATION, resume after a cut).
3. **Write the cahier** — scenarios grouped by SESSION (one session chains
   everything its state allows; a new session only where a setting read at
   boot, a reset or an upgrade demands it). Every row: an id that NAMES the
   row, the operator gesture exactly as it will be typed — never prefixed
   by the id: the play is deterministic, in table order — the expected read
   in PP OUTPUT, and its SOURCE in today's product (the code file, the card
   section) — never a past witness. Mechanical expecteds are REPLAYED in pp
   output on a disposable repo BEFORE being written.
4. **Count the coverage** — the register maps anchor ↔ scenario(s); 100 %
   is COUNTED before the first session; reported anchors are said, never
   hidden. Replacing an old cahier is a CLEAN replacement: no strikethrough,
   git keeps the history.

## The sessions protocol

- **The campaign repo** — disposable, installed from the source (the
  package's composition + monitoring), `monitoring_capture: true`, the
  harness link wired (`wire claude` — the Stop hook stamps `turn-end`),
  fixtures posed, then PHOTOGRAPHED by a git commit before any session.
- **One gesture per session** — the agent writes `session.sh` at the repo
  root: `v1` returns to the photo (the neutral state), the other cases pose
  a session's fixtures and rebuild. The operator only plays.
- **The roadmap** — handed before play: each session, its gesture, the rule
  (type the cahier's gestures EXACTLY, in order — no marker: the sequence
  is deterministic), the end words (end-of-session, then done).
- **Stumbles** — a stumble mid-campaign is treated at its CAUSE, consigned,
  and the state re-verified on the spot; stamps are checked as sessions
  land, so a silent hook is caught before the next one.

## The depouillement

- **Header first** — every result (report, conduite, analysis) opens on:
  the measured packages' VERSIONS (the instance's pins and source), the
  **LLM** and its **effort level**, and the **settings** played (the base
  file plus the per-session swaps). The LLM is read from the paired
  transcripts; `unknown` is said, never guessed.
- **Pairing** — every typed operator message is paired to its exchange BY
  ORDER (the play is deterministic — table order, sessions in book order);
  each session's event profile (stamps, repairs, refusals, routed,
  compacted) is confronted to the cahier's program: nothing missing,
  nothing doubled — or said.
- **The two tables** — `pp-monitoring report` renders BOTH, always: the
  **by-function** table (subject → volume, agent seconds, engine ms, the
  governing setting) for the totals, and the **by-turn** table (one row per
  stamped turn: the operator message, the functions the turn touched, its
  volume and agent seconds) which LOCALIZES the cost turn by turn where the
  by-function table averages it.
- **Deviations** — what the campaign uncovers REOPENS its faulty batch
  (`pp-plan reopen`), never a twin lot; an expected is never rewritten to
  absorb a gap.

## The archive — the MANDATORY documents, at the package's witness batch

Every campaign leaves the SAME set under `<batch>/campaigns/`, nowhere else —
a report without its conduite, or traces without their report, is an
incomplete restitution:

- `campaigns/<date>-<name>.md` — the REPORT: the header, the validation
  (pairing, verdict), the two tables, the levers for the distribution;
- `campaigns/<date>-<name>-conduite.md` — the CONDUITE+CHAT: a DETERMINISTIC
  concatenation of conduction and chat in transcript order (`pp-monitoring
  conduite`) — the operator messages, the `pp` calls and their FULL output
  (a large served document arrives in cut chunks each closed by a bare
  `CONTINUE`, all shown, never truncated), the agent's chat — verbatim, NO
  headings, no numbering, no prose, no interpretation: what a script emits,
  not what an author writes;
- `campaigns/<date>-traces/` — the raw traces (`.jsonl`), the effort data,
  with `transcripts/` (the harness sessions the traces' window pairs to) and
  the `SETTINGS.md` and `instance.yaml` played beside them — what `report`
  reads BACK at any later date: `setup <name> <batch>/campaigns/<date>-traces`
  then `report <name>`, the same tables as on the live window, the header
  saying what the archive did not keep; the by-turn table keeps the
  operator's messages only where the transcripts travelled;
- the cahier and its coverage live at the batch itself (`SCENARIOS.md`,
  `coverage.md`), the campaign's SUBJECT — not under `campaigns/`.
