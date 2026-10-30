# The situations -- the first SET of the campaign, the roots of the conduction sector

Twenty witness roots, one sub-directory of `roots/` each, played by the campaign's launcher
(`tools/campaign/campaign.py`, `tools/campaign/README.md`): under the modelled LLM at every pass of
the bench, under a real harness on the operator's word. `roots/campaign.yaml` is the set's manifest:
per root its door, its message, what to look at, the intention of the model and what one EXPECTS of
the root in counts (`expect:` -- the `words` of the whole exchange, the launches per channel, the
passage parked, the proofs --, judged per exchange by the sheet of response, measured under the
modelled LLM on 2026-10-29, engine `0.2.0-beta.23`), the bound of one wake-up on the relayed channel
(`launches:`) and whether the run is renewed between two launches (`renew:`); for the set its
accessories (`roots/LINES.txt`), its witness skill (`_skills/pp-cyclewit`, the sector's material, never
collected as a scenario) and the zones no root crosses yet (`silent:`, each with the work that owes it,
read by `census.py` -- none since 2026-10-29). Six roots are the patterns of
the engine; fourteen are ORDINARY SITUATIONS of a conducted turn -- each described by what one looks at,
never by the zone it crosses: the zones a root crosses are the coverage's to say, read from the trace.

| root | the documents | what we look at |
|---|---|---|
| `read-lines` | `READ_LINES.md`, the simple step | 4 `words`, 1 launch, the lines said as read |
| `laps` | `LAPS.md`, the described door (`field:`, 3 laps, `PROVE` at every lap) | one `words` per lap, under its header, the proof of LP1 at each lap's exit |
| `cycle` | `CYCLE.md` + `ITEMS.md`, the iterated door, the witness skill `pp-cyclewit` as provider and sink | the same, the sink fed by each production (`cyclewit.done` grows a line per lap) |
| `route` | `ROUTE.md` -> `STAGE.md` -> `LEFT.md` or `RIGHT.md`, the workflow | a silent `PICK next`, one `words` per node |
| `begin` | `BEGIN.md`, a contributor at `turn.begin` | its `words` before the WORK's, its law (BG1) proven at the turn's checkpoint |
| `review` | `REVIEW.md`, offered to the WORK by the root's `TURN.md` overlay | the door's `words` between the WORK's |
| `long-read` | `LONG_READ.md` (`SERVE`, `WORK`) and `BIG.md`, a reading over the floor of a prompt | at the prompt, a first piece that ends on its matter and a second that carries the WORK; by the tool, the pieces under the host's cap with their fact |
| `gesture-while-held` | `REVIEW.md` offered by `TURN.md`, which offers `pp-cyclewit`; the intention opens it, then calls `pp-cyclewit next` | when the house conducts, what pp answers to a script called after `pp: opened` -- the script's own line, played over the held output (beta.20; it bounced on beta.19, s.1160) |
| `two-steps` | `TWO_STEPS.md`, `WORK § WORK` | one `words` per step; at the prompt one launch per step; by the tool the closing at the `§`; the trace says `section` |
| `mounted` | `HELLO.md` and `NOTE.md`, a document of the root; the intention types `-mount NOTE.md` | `pp: mounted` when the house conducts, the block that stands under NOTE's law at the next launch; the block in the tool result when the model conducts |
| `unoffered` | `HELLO.md`; the intention types `-s NOBODY` | the block that stands comes back with its DEVIATION, rc 2, nothing done |
| `bare-call` | `PROOF.md` (`INFER`, `PROVE`, a law PR1); the intention types the bare call where the proof is due | `principal-advances` in the tool result when the house conducts, the empty answer repaired at the next launch; the repair at once by the tool |
| `stubborn` | `STUBBORN.md` (the same shape, a law ST1); the intention hands a wrong form at every proof | one repair after the other up to the bound, then `repair-exhausted`: the refusal that stops the conduction, and what the launcher does with a run neither parked nor standing |
| `stray` | `STRAY.md`, `WORK § WORK`; the intention hands the first production to the tool | the soft catch (`stray` on the trace): a fact, nothing recorded, the first step still standing when the house conducts, the marked step opening with the fact when the model conducts; then the lines said |
| `space` | `HELLO.md`, `ROOM.md` offered by the root's `TURN.md` overlay; the intention types `-open ROOM`, then `-close` | a space opened from the WORK and closed by the agent: the root ROOM while it stands, `opened` and `closed` on the trace; when the house conducts, `pp: opened` and `pp: closed`, each block at the next launch |
| `compacted` | `HELLO.md`; the intention types `-compacted` | the run served back after a declared compaction: when the house conducts, `pp: re-served` and the readings again at the next launch; the re-serve in the tool result when the model conducts |
| `switched` | `HELLO.md`; the intention types `-disable agent`, then `-enable agent` | a package switched off then on for the run: the word on one line and the block that stands, twice, the run never moving |
| `bounded` | `BOUNDED.md`, `WORK § WORK`, `launches: 1` at the manifest | the launcher's bound reached where the two steps take two launches: `launches-spent`, the second step kept pending for the next wake-up, the passage not over by nature (`parked: false` expected); no bound when the model conducts |
| `bouncing` | `PROOF.md`; the intention types the proof's call again after `pp: value judged` | a call that moves the run while an output waits: `pp: not played -- call already done`, nothing lost, the held output served at the next launch; nothing waits when the model conducts |
| `renewed` | `RENEWED.md`, `WORK § WORK`, `renew: true` at the manifest | the run renewed between its two launches, as an upgrade renews it: `renewed` then `reopened` on the trace, the boot served again, the message of the second wake-up unplayed; no renewal on the bare channel |

Three channels, the campaign's: **relayed strict** (the house conducts, one launch per output of
pp), **relayed hybrid** (the output that asks a value comes back in the model's tool result) and
**bare** (the model calls pp itself, one launch for the exchange).

    uv run tools/campaign/campaign.py plan                      # the 60 plans (20 roots x 3 channels), nothing launched
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
`pp: value judged` answered it. The others conform alone.

What the sheet of response found on beta.19 (2026-10-28, 42 exchanges, 161 lines): 153 vert, 5
rouge-conduction -- the first chunk of `long-read` at the prompt (M or R), the gesture bounced in
`gesture-while-held` (twice), the closing at the `§` of `two-steps` by the tool (T or R, the modelled
LLM undecided: the bare exchange never parks) --, 3 rouge-agent (`stray`, the agent's own miss), 0
trou; the six patterns of the engine green on the three channels; the root at its end never handed
when the house conducts (24 texts). On
beta.20 (the same day) the five rouge-conduction are gone: the chunk
at the prompt closes on `▶ MORE` and reads R alone, the gesture plays over the held output, and by the
tool a chunk carries its fact where the closing at a `§` carries none. On beta.23 (2026-10-29,
the twenty roots): 60 exchanges, 58 parked (`bounded` by nature), 220 lines, 215 vert, 0
rouge-conduction, 5 rouge-agent (the three handed lines of `stray`, the proof handed again in `bouncing`:
wanted), 0 trou; every zone crossed on every channel it exists on; the 162 lines of the fourteen roots of
before paired with `2026-10-29T0744-model`, 0 changed.

The bench keeps the set honest (tests/README.md, rule 11): `launcher/plan.py` opens the twenty roots on a
throwaway instance and reads each root's first block; `launcher/relayed.py`, `hybrid.py` and `bare.py` play
the six patterns under the model, one channel each; `launcher/sheet.py` plays `long-read`, `review`,
`gesture-while-held` and `read-lines` and reads their sheet, the expectations judged; `launcher/mask.py`
masks the sheet by zone and compares two campaigns; `launcher/zones.py` writes the census on a throwaway
document; `zones/<zone>.py` plays, per zone of the conduction, the fewest roots that cross it on every
channel the zone exists on (the data's, `semantics.ZONES`); `census.py` holds that every zone is carried by
such a scenario or declared `silent:`, and every root played. The light artifacts of the real campaigns (and of the `model` campaign each is compared to)
are kept under `evidence/campaigns/<date>/` in the source repository, each `campaign.json` saying the engine it
played on (`engine`): the launcher's verb `tools/campaign/campaign.py zones` reads them to write the census of
the zones.
