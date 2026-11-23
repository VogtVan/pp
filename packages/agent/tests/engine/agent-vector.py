"""Scenario `agent-vector` -- the vectors a wake-up names, mounted by the launcher at every exchange of the run,
on a house pinning `agent` and `plan`, the agent's run opened under a root of documents that holds a shared plan
whose batch carries a law:
- the vector: `--vector <family>:<id>`, repeated, on `run` and `start` -- the launcher has every vector verified
  by the script its family's manifest names, then plays `-s <script> mount <id>` as the principal:
  after the `-new` at an opening, after the message at a resume. Two vectors at an opening both mount, each
  gesture naming its script alone; the first exchange shows the batch's law on its block and asks it
  at its proof; the second (`--run <key>`, no flag) too: the vectors are kept with the run; the agent typed no
  gesture; each `opened` of the run's flow says the vectors
- the refusals: every refusal of a vector says ONE code, `vector-refused`, first on stderr and as the `code`
  of a `refused` event, its cause in the detail -- a family nobody declares, a family whose package the wake-up
  switches off (`family-unknown`), the form (`vector-invalid`): nothing opened; a dry run says the gesture and
  opens nothing; a conversation whose first message meets a family nobody declares opens nothing either
- an address the family's verifier refuses at a resume leaves the run as it was -- nothing launched nor
  recorded, the exchange not opened, the kept set as it was --, its flow saying `refused`
- `--vector` at a resume REPLACES the set the run keeps; `--vector -` empties it
- the lines the run left at `vectors.jsonl`, whole: each says every key in its order with its value, the hour
  apart -- the two vectors of its opening, the one that replaced them, the set emptied; a line read there and
  back (`Keeping`) is the same JSON text, for the lines the cases wrote, a line of the writer's order and a line
  of a form of before
- two vectors, the second refused: nothing is mounted, nothing kept, and the next exchange shows no law of the
  first
- the first prompt of an exchange that mounts vectors is rendered ONCE, after the last mount: read at the flow's
  `conduction` (its `blocks`), at the run's trace and at the prompt -- no block before the first mount nor
  between two, every block after the last, the block that stands named once, each step's line once; the first
  proof deposited at a resume names every code in force, nothing repaired; the matter of each mount served in
  the order of the mounts (the blocks' ledgers); every block a conduction of the run names is a `block` event
  of its trace, whole -- its stack, its command, its wait -- and in the trace's order
- a mount refused after the message opened the exchange renders nothing: no block at the trace, the output left
  OPEN at the run, the message's line at `messages.jsonl`, the run standing at `agent status`; the run taken up
  with vectors: its mounts are posed on that exchange and the first prompt is rendered once, each step's line
  once
- what the vectors mount makes no segment: in the first prompt of the opening and of the resume, no segment
  stands without a step -- the resume reads as ONE segment --, the laws of the segment of the first step name
  the batch's law, the WORK's line stands once and the proof is asked on one line, once at most; at the opening
  the readings of the mount -- the method `PLAN`, the template and the document of the phase and of the batch --
  stand before the line of the first step (a resume spares a reading its run already proved)
(the conversation's cases: `agent-vector-chat`, on the same house -- `Vectored` of the support module)
"""
from __future__ import annotations

import dataclasses
import json
import re

from conductor.core import language
from tests.harness import support, titled

A = support(__file__, "agent")
STEP = A.STEP_LINE                                     # the line of a step
WORK = re.compile(r"^WORK\b.*\(TURN\)$")              # the line of the turn's WORK
PROOF = re.compile(r"^INFER proof \[")                 # the line that asks a proof


def _context_first(prompt: str, code: str, names: list[str]) -> dict:
    """What a first prompt says of the vectors' mount, read against the line of its FIRST step: how many
    segments it counts and how many of them ask no step; whether the readings `names` of the mount stand
    before that line, whether the laws of the segment that carries it name `code`; how many lines say the
    WORK and ask a proof."""
    mark = "▌ "
    lines = prompt.splitlines()
    first = next((rank for rank, one in enumerate(lines) if STEP.match(one)), -1)
    headings = [rank for rank, one in enumerate(lines) if one.startswith(mark)
                and not language.section_of(one.removeprefix(mark))[0] and ("▸" in one or "{" in one)]
    ends = headings[1:] + [len(lines)]
    stepless = [rank for rank, end in zip(headings, ends) if not any(STEP.match(one) for one in lines[rank:end])]
    opened = max((rank for rank in headings if rank < first), default=-1)       # the heading of the first step
    laws = titled(language.CONSTRAINTS)
    said = lines[opened:first] if 0 <= opened < first else []
    section = said[said.index(laws) + 1:] if laws in said else []
    section = section[:next((rank for rank, one in enumerate(section) if one.startswith(mark)), len(section))]
    readings = [titled(language.INFORMATION, name) for name in names]
    return {"segments": len(headings), "stepless": len(stepless),
            "readings": bool(readings) and first >= 0
                        and all(one in lines and lines.index(one) < first for one in readings),
            "law": bool(re.search(rf"\b{re.escape(code)}\b", "\n".join(section))),
            "works": len([one for one in lines if WORK.match(one)]),
            "proofs": len([one for one in lines if PROOF.match(one)])}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    v = A.Vectored(bench)
    h, keys, counted, fresh = v.h, v.h.keys, v.h.counted, v.fresh
    shared, code, law_text, asks = v.shared, v.code, v.law_text, v.asks
    vector, phase, ghost_vector = v.vector, v.phase, v.ghost_vector
    prompts, gestures, flow, mounts = v.prompts, v.gestures, v.flow, v.mounts
    refused, opened_vectors, resume, turns = v.refused, v.opened_vectors, v.resume, v.turns
    _first_prompt, _once = v.first_prompt, v.once

    known, seen, typed = set(keys()), prompts(), gestures()
    woke = h.wake("un", "play", "--documents", str(shared), "--vector", phase, "--vector", vector)
    key_v = fresh(known)
    first = "\n".join(text for name, text in prompts().items() if name not in seen)
    first_opening = _first_prompt(seen, prompts())
    seen = prompts()
    again = h.call("agent", "run", "agents/ag1", "--run", key_v, "--message", "deux", *h.harnessed("play")) \
        if key_v else None
    second = "\n".join(text for name, text in prompts().items() if name not in seen)
    first_resume = _first_prompt(seen, prompts())
    kept_vectors = [one.get("vectors") for one in flow(key_v) if one.get("kind") == "opened"]
    if (code and woke.returncode == 0 and key_v and again is not None and again.returncode == 0
            and f"{code}  {law_text}" in first and asks.search(first) and asks.search(second)
            and mounts(key_v) == 2 and gestures() == typed and kept_vectors == [[phase, vector], [phase, vector]]):
        held("(e) the vectors mount their nodes at every exchange", f"run {key_v}: two vectors at the opening, "
             f"each gesture naming its script alone -- the law {code} on the first exchange's block and at its "
             f"proof; `--run {key_v}` without the flag asks it at its proof again; the batch mounted twice at the "
             "trace, no gesture typed by the agent, each `opened` of the flow says the vectors")
    else:
        failures.append(f"  ✗ (e) the vector             code={code!r} rc={woke.returncode}/"
                        f"{again.returncode if again else None} key={key_v!r} law={f'{code}  {law_text}' in first} "
                        f"asks={bool(asks.search(first))}/{bool(asks.search(second))} mounts={mounts(key_v)} "
                        f"typed={gestures() - typed} kept={kept_vectors} {woke.stderr[-300:]!r}")

    # --- the first prompt carries the block that stands ONCE, after the last mount ----------------------------
    firsts, traced = v.first_prompts(key_v), v.exchanges_traced(key_v)
    standing = [v.standing_blocks(one) for one in firsts]
    heads = [v.before_answer(one) for one in traced]
    after = [v.blocks_after_mounts(one) for one in heads]
    ahead = [v.blocks_before_mounts(one) for one in heads]
    proved = [v.proofs(one) for one in traced]
    repaired = [[one.get("kind") for one in events if str(one.get("kind", "")).startswith("repair")] for events in traced]
    matter = [v.mount_matter(one) for one in heads]
    batch_doc, phase_doc = v.node.rsplit("/", 1)[-1], "PHASE.md"
    ordered = [phase_doc in one and batch_doc in one and one.index(phase_doc) < one.index(batch_doc) for one in matter[:1]]
    named = [block for one in flow(key_v) if one.get("kind") == "conduction" for block in one.get("blocks") or []]
    rendered = iter([{"stack": str(one.get("stack", "")), "command": str(one.get("command", "")),
                      "wait": bool(one.get("wait"))} for one in h.trace(key_v) if one.get("kind") == "block"])
    as_traced = all(any(block == other for other in rendered) for block in named)
    if (len(firsts) == 2 and len(traced) == 2 and standing == [1, 1] and ahead == [0, 0]
            and [between for between, _ in after] == [0, 0] and all(behind >= 1 for _, behind in after)
            and _once(first_opening) and _once(first_resume)
            and proved[0][:1] and code in proved[0][0] and proved[1][:1] == proved[0][:1]
            and repaired == [[], []] and ordered == [True]
            and as_traced and any(one["command"] for one in named) and any(one["stack"] for one in named)):
        held("(l) the first prompt is rendered once, after the last mount", f"run {key_v}: at the opening with two "
             "vectors and at the resume with the kept set, no block is rendered before the first mount nor between "
             f"two -- {[behind for _, behind in after]} after the last --, the first prompt's conduction names the "
             "block that stands once and each step's line stands once; the first proof the agent deposits at the resume "
             f"names every code the opening's did ({len(proved[0][0])}, {code} among them) and nothing is repaired; "
             f"the matter of the phase's mount is served before the batch's; the {len(named)} blocks its "
             "prompts name are block events of its trace, whole and in order")
    else:
        failures.append(f"  ✗ (l) the first prompt once     firsts={len(firsts)} traced={len(traced)} standing={standing} "
                        f"ahead={ahead} after={after} once={_once(first_opening)}/{_once(first_resume)} proved={[[sorted(one) for one in each] for each in proved]} repaired={repaired} "
                        f"matter={matter} ordered={ordered} as_traced={as_traced} named={named}")

    # --- what the vectors mount stands before the steps of its exchange, the proof asked on one line ----------
    at_opening, at_resume = (_context_first(one, code, v.readings) for one in (first_opening, first_resume))
    if (at_opening["segments"] >= 1 and at_opening["stepless"] == 0 and at_opening["readings"]
            and at_opening["law"] and at_opening["works"] == 1 and at_opening["proofs"] <= 1
            and at_resume["segments"] == 1 and at_resume["stepless"] == 0
            and at_resume["law"] and at_resume["works"] == 1 and at_resume["proofs"] == 1):
        held("(o) the vectors' mount makes no segment", f"run {key_v}: the first prompt of the opening reads in "
             f"{at_opening['segments']} segment(s), the resume's in one, none without a step; the laws of the "
             f"first step's segment name {code}; the readings of the mount ({', '.join(v.readings)}) stand before "
             "that step at the opening; the WORK's line stands once, the proof is asked on one line at the resume "
             f"({at_opening['proofs']} at the opening)")
    else:
        failures.append(f"  ✗ (o) the mount and the segments opening={at_opening} resume={at_resume} "
                        f"{[one for one in first_resume.splitlines() if one.startswith('▌ ')]}")

    # --- every output the two wake-ups served: one that carries a step has no segment without a step ---------
    served = [str(one.get("text") or "") for one in flow(key_v) if one.get("kind") == "conduction"]
    stepped = [one for one in served if any(STEP.match(line) for line in one.splitlines())]
    read = [_context_first(one, code, v.readings) for one in served]
    hollow = [(rank, said["segments"], said["stepless"])
              for rank, (one, said) in enumerate(zip(served, read)) if one in stepped and said["stepless"]]
    if len(served) >= 2 and len(stepped) >= 2 and not hollow:
        held("(r) no served output that carries a step has a segment without one", f"run {key_v}: {len(served)} "
             f"outputs served over the two wake-ups, {len(stepped)} of them carrying a step: every segment of "
             "those asks a step -- the closing of a passage played under the vectors' mount stands in the segment "
             "of its steps")
    else:
        failures.append(f"  ✗ (r) a segment without a step  served={len(served)} stepped={len(stepped)} "
                        f"hollow(rank, segments, stepless)={hollow}")

    before_keys, before_counts = sorted(keys()), counted()
    unknown = h.wake("never", "play", "--vector", "nowhere:x")
    formless = h.wake("never", "play", "--vector", "plan")
    off = h.wake("never", "play", "--documents", str(shared), "--vector", vector, "--package", "plan=off", "--json")
    events = [json.loads(line) for line in off.stderr.splitlines() if line.strip().startswith("{")]
    refused_off = [one for one in events if one.get("event") == "refused" or one.get("kind") == "refused"]
    dry = h.wake("never", "play", "--documents", str(shared), "--vector", vector, "--dry-run")
    chatted = h.call("agent", "chat", "agents/ag1", "--vector", "nowhere:x", *h.harnessed("play"), stdin="un\n")
    if (refused(unknown, "family-unknown") and refused(formless, "vector-invalid") and refused(off, "family-unknown")
            and [one.get("code") for one in refused_off] == ["vector-refused"]
            and "family-unknown" in str(refused_off[0].get("detail")) and refused_off[0].get("vector") == vector
            and dry.returncode == 0 and re.search(r"-s pp-plan mount job/ph/bt\b", dry.stdout)
            and refused(chatted, "family-unknown")
            and sorted(keys()) == before_keys and counted() == before_counts):
        held("(f) a vector refused opens nothing", "a family nobody declares, a family whose package the wake-up "
             "switches off, a vector without an id: rc 2, `vector-refused` first, the cause in the detail "
             "(family-unknown, vector-invalid), a `refused` event of that one code; the dry run says the gesture; "
             "a conversation on a family nobody declares -- no run opened, the records as they were")
    else:
        failures.append(f"  ✗ (f) a vector refused       unknown={unknown.returncode}:{unknown.stderr[-120:]!r} "
                        f"formless={formless.returncode}:{formless.stderr[-120:]!r} off={off.returncode}:"
                        f"{off.stderr[-160:]!r} events={refused_off} dry={dry.returncode}:{dry.stdout[-200:]!r} "
                        f"chat={chatted.returncode}:{chatted.stderr[-120:]!r} "
                        f"keys={sorted(set(keys()) - set(before_keys))} counts={before_counts}/{counted()}")

    # --- an address refused at a resume: the run as it was ---------------------------------------------------
    before_counts, before_turns = counted(), turns(key_v)
    ghost = resume(key_v, "trois", "--vector", ghost_vector)
    said = [one for one in flow(key_v) if one.get("kind") == "refused"]
    if (refused(ghost, "path-unknown") and [one.get("code") for one in said] == ["vector-refused"]
            and said[0].get("vector") == ghost_vector and "path-unknown" in str(said[0].get("detail"))
            and counted() == before_counts and turns(key_v) == before_turns and mounts(key_v) == 2):
        held("(g) an address refused leaves the run as it was", f"run {key_v} resumed with a vector its family's "
             "verifier refuses: `vector-refused`, path-unknown in the detail, the flow's `refused` names the vector; "
             "nothing mounted, launched nor recorded, the exchange not opened")
    else:
        failures.append(f"  ✗ (g) an address refused     rc={ghost.returncode if ghost else None} said={said} "
                        f"counts={before_counts}/{counted()} turns={before_turns}/{turns(key_v)} "
                        f"mounts={mounts(key_v)} {(ghost.stderr[-300:] if ghost else '')!r}")

    # --- a resume's vectors REPLACE the kept set; `-` empties it ----------------------------------------------
    seen = prompts()
    swapped = resume(key_v, "trois", "--vector", vector)
    kept_after_swap, mounted_after_swap = opened_vectors(key_v)[-1:], mounts(key_v)
    seen_swap = prompts()
    emptied = resume(key_v, "quatre", "--vector", "-")
    last = "\n".join(text for name, text in prompts().items() if name not in seen_swap)
    dry_kept = resume(key_v, "cinq", "--dry-run")
    if (swapped is not None and swapped.returncode == 0 and kept_after_swap == [[vector]] and mounted_after_swap == 3
            and asks.search("\n".join(text for name, text in seen_swap.items() if name not in seen))
            and emptied is not None and emptied.returncode == 0 and opened_vectors(key_v)[-1:] == [None]
            and not asks.search(last) and code not in last and mounts(key_v) == 3
            and dry_kept is not None and dry_kept.returncode == 0 and " mount " not in dry_kept.stdout):
        held("(h) a resume's vectors replace the kept set", f"run {key_v} kept two vectors: resumed with "
             f"`--vector {vector}` it keeps that one alone; resumed with `--vector -` it keeps none -- the exchange "
             f"mounts nothing, no law {code} on its block, a dry run names no gesture")
    else:
        failures.append(f"  ✗ (h) the set replaced       rc={swapped.returncode if swapped else None}/"
                        f"{emptied.returncode if emptied else None} kept={kept_after_swap}/{opened_vectors(key_v)[-1:]} "
                        f"mounts={mounted_after_swap}/{mounts(key_v)} law={code in last} "
                        f"{(emptied.stderr[-300:] if emptied else '')!r}")

    # --- the lines of vectors.jsonl, whole, and there and back ---------------------------------------------
    Keeping = A.skill().Keeping

    def text(one: dict) -> str:
        return json.dumps(one, ensure_ascii=False)
    lines = A.lines(h.records / "vectors.jsonl")
    wrote = [[(name, "<at>" if name == "at" and value else value) for name, value in one.items()]
             for one in lines if one.get("run") == key_v]
    owed = [[("at", "<at>"), ("agent", "agents/ag1"), ("run", key_v), ("vectors", vectors)]
            for vectors in ([phase, vector], [vector], [])]
    whole = {"at": "2026-10-01T09:00:00+00:00", "agent": "agents/ag1", "run": "abc123", "vectors": ["plan:job"]}
    before = {"run": "abc123", "vectors": ["plan:job", "plan:other"], "agent": "agents/ag1", "mounted": 2}
    strays = [Keeping.of(one).json() for one in lines + [whole, before] if text(Keeping.of(one).json()) != text(one)]
    anew = dataclasses.replace(Keeping.of(whole), keys=None, kept=())      # composed, as its writer does
    old = Keeping.of(before)
    if (wrote == owed and not strays and text(anew.json()) == text(whole)
            and (old.at, old.run, old.vectors) == (None, "abc123", ["plan:job", "plan:other"])):
        held("(n) the lines of vectors.jsonl, whole and there and back", f"run {key_v}: its {len(owed)} lines say "
             "every key in its order with its value -- two vectors, the one that replaced them, the set emptied; "
             f"{len(lines)} lines as the cases wrote them, a line of the writer's order, a line of a form of "
             "before: the same JSON text each, composed anew the same")
    else:
        failures.append(f"  ✗ (n) the lines of vectors    wrote={wrote} strays={strays} anew={anew.json()} "
                        f"old={old}")

    # --- two vectors, the second refused: nothing mounted, nothing kept ------------------------------------
    known = set(keys())
    plain = h.wake("un", "play", "--documents", str(shared))
    key_p = fresh(known)
    both = resume(key_p, "deux", "--vector", vector, "--vector", ghost_vector)
    mounted_then, seen = mounts(key_p), prompts()
    following = resume(key_p, "deux")
    shown = "\n".join(text for name, text in prompts().items() if name not in seen)
    if (plain.returncode == 0 and key_p and refused(both, "path-unknown") and mounted_then == 0
            and following is not None and following.returncode == 0 and mounts(key_p) == 0
            and code not in shown and opened_vectors(key_p)[-1:] == [None]):
        held("(i) one vector refused, none mounted", f"run {key_p} resumed with two vectors, the second refused: "
             f"`vector-refused`, the first never mounted nor kept; the next exchange shows no law {code}")
    else:
        failures.append(f"  ✗ (i) two vectors, one refused rc={plain.returncode}/{both.returncode if both else None}/"
                        f"{following.returncode if following else None} key={key_p!r} mounts={mounted_then}/"
                        f"{mounts(key_p)} law={code in shown} kept={opened_vectors(key_p)[-1:]} "
                        f"{(both.stderr[-300:] if both else '')!r}")

    # --- an output left open by a mount refused after the message, the run taken up with vectors: the block once
    own = f"agent-run:./{key_p}"                           # verified by pp-agent, which no block of TURN offers
    stopped = resume(key_p, "trois", "--vector", own)
    left = bool((v.slot(key_p).get("held") or {}).get("open"))
    rendered_o = [one.get("kind") for one in v.exchanges_traced(key_p)[-1] if one.get("kind") == "block"]
    sent = [one for one in h.messages() if one.get("run") == key_p and one.get("message") == "trois"]
    face = h.face(key_p).get("state")
    seen = prompts()
    taken = resume(key_p, "quatre", "--vector", phase, "--vector", vector)
    prompt_o = _first_prompt(seen, prompts())
    last_prompt = v.first_prompts(key_p)[-1:]
    last_head = [v.before_answer(one) for one in v.exchanges_traced(key_p)[-1:]]
    standing_o = [v.standing_blocks(one) for one in last_prompt]
    after_o = [v.blocks_after_mounts(one) for one in last_head]
    ahead_o = [v.blocks_before_mounts(one) for one in last_head]
    if (refused(stopped, "offer-absent") and left and not rendered_o and len(sent) == 1 and face == "standing"
            and taken is not None and taken.returncode == 0
            and standing_o == [1] and ahead_o == [0] and [between for between, _ in after_o] == [0]
            and all(behind >= 1 for _, behind in after_o) and _once(prompt_o)
            and not (v.slot(key_p).get("held") or {}).get("open")
            and [one.get("standing") for one in flow(key_p) if one.get("kind") == "opened"][-1:] == [True]):
        held("(m) a mount refused renders nothing, the run taken up renders once", f"run {key_p}: {own} refused "
             "offer-absent once the message opened the exchange -- no block at the trace, the output left open "
             "at the run, the message on record, the run standing; `--run` with two vectors takes it up standing "
             "-- the mounts are posed on that exchange, no block before the last of them, and the first prompt "
             "names the block that stands once, each step's line once")
    else:
        failures.append(f"  ✗ (m) a mount refused, taken up rc={stopped.returncode if stopped else None}/"
                        f"{taken.returncode if taken else None} left={left} rendered={rendered_o} sent={len(sent)} "
                        f"state={face!r} standing={standing_o} ahead={ahead_o} after={after_o} once={_once(prompt_o)} "
                        f"{(stopped.stderr[-200:] if stopped else '')!r} {(taken.stderr[-300:] if taken else '')!r}")
    return 0
