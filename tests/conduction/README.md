# The situations -- the first SET of the campaign, the roots of the conduction sector

Twenty witness roots, one sub-directory of `roots/` each, played by the campaign's launcher
(`tools/campaign/campaign.py`, `tools/campaign/README.md`): under the modelled LLM at every pass of
the bench, under a real harness on the operator's word. `roots/campaign.yaml` is the set's manifest:
per root its door, its message, what to look at, the intention of the model and what one EXPECTS of
the root in counts (`expect:` -- the `words` of the whole exchange, every production printed and the `...`
that ends each launch, the launches, the passage parked, the proofs --, judged per exchange by the sheet of
response, measured under the modelled LLM on 2026-11-21, engine `0.2.24`), the bound of one wake-up
(`launches:`) and whether the run is renewed between two launches (`renew:`); for the set its
accessories (`roots/LINES.txt`), its witness skill (`_skills/pp-cyclewit`, the sector's material, never
collected as a scenario) and the zones no root crosses yet (`silent:`, each with the work that owes it,
read by `census.py` -- none since 2026-10-29). Six roots are the patterns of
the engine; fifteen are ORDINARY SITUATIONS of a conducted turn -- each described by what one looks at,
never by the zone it crosses: the zones a root crosses are the coverage's to say, read from the trace.

| root | the documents | what we look at |
|---|---|---|
| `read-lines` | `READ_LINES.md`, the simple step | 4 `words`, 1 launch, the lines said as read |
| `laps` | `LAPS.md`, the described door (`field:`, 3 laps, `PROVE` at every lap) | one `words` per lap, under its header, the proof of LP1 at each lap's exit |
| `cycle` | `CYCLE.md` + `ITEMS.md`, the iterated door, the witness skill `pp-cyclewit` as provider and sink | the same, the sink fed by each production (`cyclewit.done` grows a line per lap) |
| `route` | `ROUTE.md` -> `STAGE.md` -> `LEFT.md` or `RIGHT.md`, the workflow | a silent `PICK next`, one `words` per node |
| `begin` | `BEGIN.md`, a contributor at `turn.begin` | its `words` before the WORK's, its law (BG1) proven at the turn's checkpoint |
| `review` | `REVIEW.md`, offered to the WORK by the root's `TURN.md` overlay | the door's `words` between the WORK's |
| `long-read` | `LONG_READ.md` (`SERVE`, `WORK`, then the fork of its `next:` to `LAST.md` or `FIRST.md`) and `BIG.md`, a reading longer than one prompt holds; the WORK and the fork each have a long brief, and the two do not fit together in one tool result | at the prompt, a first piece that carries no step of the door and closes on `▶ MORE`, then a second that carries the WORK and the fork; the WORK's production is printed only once the last piece is read |
| `gesture-while-held` | `REVIEW.md` offered by `TURN.md`, which offers `pp-cyclewit`; the intention opens it, then calls `pp-cyclewit next` | what pp answers to a script called after `pp: opened — hand back` -- the script's own line, played over the held output (beta.20; it bounced on beta.19, s.1160) |
| `two-steps` | `TWO_STEPS.md`, `WORK § WORK` | one production per step, one launch per step; the trace says `section` |
| `mounted` | `HELLO.md` and `NOTE.md`, a document of the root; the intention types `-mount NOTE.md` | `pp: mounted — hand back`, the block that stands under NOTE's law at the next launch |
| `unoffered` | `HELLO.md`; the intention types `-s NOBODY` | the block that stands comes back with its DEVIATION, rc 2, nothing done |
| `bare-call` | `PROOF.md` (`INFER`, `PROVE`, a law PR1); the intention types the bare call where the proof is due | `principal-advances` in the tool result, the empty answer repaired at the next launch |
| `stubborn` | `STUBBORN.md` (the same shape, a law ST1); the intention hands a wrong form at every proof | one repair after the other up to the bound, then `repair-exhausted`: the refusal that stops the conduction, and what the launcher does with a run neither parked nor standing |
| `stray` | `STRAY.md`, `WORK § WORK`; the intention hands the first production by the value call | the block that stands comes back with its deviation naming the print (`stray` on the trace), nothing recorded, no repair; then the production printed, the run moving on |
| `unprinted` | `UNPRINTED.md`, one `INFER`; the intention writes the productions asked on `terminal` in its message, no print call typed | its advance comes back with the block that stands and the prints due, the agent prints, then hands back |
| `space` | `HELLO.md`, `ROOM.md` offered by `HELLO.md` and by the root's `TURN.md` overlay, two segments; the intention types `-open ROOM` (refused `address-ambiguous`, which asks for `-open ROOM@<n>`), `-open ROOM@1`, then `-close` | a space opened from the WORK and closed by the agent: the root ROOM while it stands, `opened` and `closed` on the trace; `pp: opened — hand back` and `pp: closed — hand back`, each block at the next launch |
| `compacted` | `HELLO.md`; the intention types `-compacted` | the run served back after a declared compaction: `pp: re-served — hand back` and the readings again at the next launch |
| `switched` | `HELLO.md`; the intention types `-disable agent`, then `-enable agent` | a package switched off then on for the run: the word on one line and the block that stands, twice, the run never moving |
| `bounded` | `BOUNDED.md`, `WORK § WORK`, `launches: 1` at the manifest | the launcher's bound reached where the two steps take two launches: `launches-spent`, the second step kept pending for the next wake-up, the passage not over by nature (`parked: false` expected) |
| `bouncing` | `PROOF.md`; the intention types the proof's call again after `pp: value judged — hand back` | a call that moves the run while an output waits: `pp: not played — hand back`, nothing lost, the held output served at the next launch |
| `renewed` | `RENEWED.md`, `WORK § WORK`, `renew: true` at the manifest | the run renewed between its two launches, as an upgrade renews it: `renewed` then `reopened` on the trace, the boot served again, the message of the second wake-up unplayed |
| `rewritten` | `REWRITTEN.md`, one WORK, `TURN.md` offering `pp-memberwit`; the intention calls `pp-memberwit grow`; `again:` at the manifest | a document of the run rewritten during the passage (the member's `SERVE` step and a `serve:` row, as the member craft writes them): the passage ends on the steps it began with, no refusal; the next message takes the run up `reseated`, nothing of the boot replayed; the set's `keep:` puts the member back before the next exchange |

One channel, the campaign's: the house conducts, one launch per output that moves the run on; the output
that asks a value comes back in the model's tool result.

    uv run tools/campaign/campaign.py plan                      # the 26 plans, one per root, nothing launched
    uv run tools/campaign/campaign.py play --provider model     # the campaign under the model: the coverage and the sheet written
    uv run tools/campaign/campaign.py sheet <date>              # the sheet of response of a campaign, replayed from its artifacts
    uv run tools/campaign/campaign.py play --provider claude    # on a real harness, on the operator's word
    uv run tools/campaign/campaign.py prepare                   # TWENTY houses, one per root -- the operator's bench
    uv run tools/campaign/campaign.py runsheet                  # the run sheet of that bench (also written at <houses>/RUNSHEET.md)

What the modelled LLM is told of each root (`model:` at the manifest): `read-lines` reads
`LINES.txt` and says one `words` per line (`read:`); `laps` answers the field
`[alpha, beta, gamma]`; `cycle` echoes the element `cyclewit-items` serves, so that the sink reads
it; `route` picks `LEFT`; `review` and `gesture-while-held` open the door `REVIEW` during the WORK;
`gesture-while-held`, `mounted` and `unoffered` type a gesture (`-s pp-cyclewit next`, `-mount NOTE.md`,
`-s NOBODY`); `bare-call` types the bare call where the proof is due; `stubborn` persists in a wrong
form; `stray` hands its first line to the tool; `space` types `-open ROOM` then, at the next launch,
`-close` (a gesture that moves the run waits while an output is held); `compacted` types `-compacted`;
`switched` types `-disable agent` then `-enable agent`; `bouncing` types its proof's call again once
`pp: value judged — hand back` answered it. The others conform alone.

What the sheet of response found on beta.19 (2026-10-28, 42 exchanges, 161 lines): 153 vert, 5
rouge-conduction -- the first chunk of `long-read` at the prompt (M or R), the gesture bounced in
`gesture-while-held` (twice), the closing at the `§` of `two-steps` by the tool (T or R, the modelled
LLM undecided: the exchange the model conducted itself never parks) --, 3 rouge-agent (`stray`, the agent's
own miss), 0 trou; the six patterns of the engine green on the three channels of then; the root at its end never handed
when the house conducts (24 texts). On
beta.20 (the same day) the five rouge-conduction are gone: the chunk
at the prompt closes on `▶ MORE` and reads R alone, the gesture plays over the held output, and by the
tool a chunk carries its fact where the closing at a `§` carries none. On beta.23 (2026-10-29,
the twenty roots): 60 exchanges, 58 parked (`bounded` by nature), 220 lines, 215 vert, 0
rouge-conduction, 5 rouge-agent (the three handed lines of `stray`, the proof handed again in `bouncing`:
wanted), 0 trou; every zone crossed on every channel it existed on; the 162 lines of the fourteen roots of
before paired with `2026-10-29T0744-model`, 0 changed.
On beta.29 (2026-10-31, twenty-one roots): 63 exchanges, 61 parked, 232 lines, 227 vert, 0
rouge-conduction, the same 5 rouge-agent, 0 trou; against `2026-10-29T0853-model`, 220 lines paired, 0
changed, 12 appeared (`rewritten`, and `space` asked for its segment's number).
On 0.2.24 (2026-11-21, twenty-six roots, the one channel): 26 exchanges, 25 parked (`bounded` by nature), 203
lines, 200 vert, 0 rouge-conduction, 3 rouge-agent (the handed line of `stray`, the line `unprinted` writes,
the proof handed again in `bouncing`: wanted), 0 trou, every expectation held.

The bench keeps the set honest (tests/README.md, rule 11): `launcher/plan.py` opens the twenty-six roots on a
throwaway instance and reads each root's first block; `launcher/relayed.py` plays the six patterns
under the model; `launcher/sheet.py` plays `long-read`, `review`,
`gesture-while-held` and `read-lines` and reads their sheet, the expectations judged; `launcher/mask.py`
masks the sheet by zone and compares two campaigns; `launcher/zones.py` writes the census on a throwaway
document; `zones/<zone>.py` plays, per zone of the conduction, the fewest roots that cross it; `census.py`
holds that every zone is carried by such a scenario or declared `silent:`, every root played, and no zone
and no root declaring a channel. The light artifacts of the real campaigns (and of the `model` campaign each is compared to)
are kept under `evidence/campaigns/<date>/` in the source repository, each `campaign.json` saying the engine it
played on (`engine`): the launcher's verb `tools/campaign/campaign.py zones` reads them to write the census of
the zones.
