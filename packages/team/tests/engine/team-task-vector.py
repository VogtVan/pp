"""Scenario `team-task-vector` -- 8 case(s): the NODE a task carries (team 1.14.5, batch
travail-en-equipe/le-plan-d-equipe-monte/la-tache-qui-porte-son-noeud): a VECTOR, an opaque `<family>:<id>`, on the
task and on a `do`, passed to the launcher at every launch of a run on that task. One house pinning `agent` and
`team`; one team, `nodes`: `na` the root, `nb` and `nc` its delegates. The LAUNCHER'S WITNESS (`launcher_witness`,
the area's support) stands in the house's `pp-agent` script: it writes each line it is called with and answers as
the launcher's contract says -- a vector of the family `refused` refused `vector-refused` (rc 2), a line carrying a
vector of the family `busy` refused once by the house (rc 2, another code), any other vector accepted.
- (h) the task's vector: `team post nodes --vector refused:t` writes `vectors` on the event `task`; na's launch
  line on T2 carries `--vector refused:t`
- (i) two members, two vectors: na's `do` gives nb `{text, vector: refused:b}` and nc `{text, vector:
  refused:c}`; nb's launch line carries `--vector refused:b` alone, nc's `--vector refused:c` alone, na's on T1
  `--vector -` alone: the whole set said at every launch, empty
- (j) the launcher's refusal told to the task: each refused launch is a final `wake-failed` of the house, its
  `do` answered by the tick, na resolves T1; nb, nc and na on T2 are launched once each, never again
- (o) the vector comes back: na's head hands back each `do` the tick answered in nb's and nc's place -- the text
  na wrote and the vector the `do` carried, `refused:b` and `refused:c`
- (l) a refusal of the house is no vector's refusal: T3 posted to nb (`--vector busy:t`), nb's launch refused rc 2
  under another code is a `wake-failed` of the house, NOT final; the next tick launches nb again, with its vector,
  and nb resolves T3
- (m) a corrected `do`: on T4 na hands nb `node:1`, then, nb answered, `node:2`; nb's first launch line carries
  `--vector node:1`, its second `--vector node:2` alone
- (n) a do corrected after its refusal: on T5 na hands nc `refused:x` -- refused `vector-refused`, nc's final
  failure, the do answered by the tick --, then `node:9` to nc on the same task; nc is launched again with
  `--vector node:9` alone and answers, T5 resolved
- (k) last, the team at rest: a malformed vector -- no `:` -- refuses `vector-invalid` on `post`, nothing
  written, and in a `do` (`act_formed`); a `do` with a formed vector is formed
T2 is posted beside T1; T3, T4 and T5 are posted together and play side by side (`parallel: 3`): nb holds T3
and T4, nc T5.
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    by_kind, all_ended = T.by_kind, T.all_ended
    h = T.House(bench, script={
        "na": {"T1": [{"body": {"do": {"nb": {"text": "frame b", "vector": "refused:b"},
                                       "nc": {"text": "frame c", "vector": "refused:c"}}}},
                      {"body": {"done": "the nodes were handed"}}],
               "T4": [{"body": {"do": {"nb": {"text": "frame", "vector": "node:1"}}}},
                      {"body": {"do": {"nb": {"text": "frame again", "vector": "node:2"}}}},
                      {"body": {"done": "the node was corrected"}}],
               "T5": [{"body": {"do": {"nc": {"text": "frame", "vector": "refused:x"}}}},
                      {"body": {"do": {"nc": {"text": "frame the right node", "vector": "node:9"}}}},
                      {"body": {"done": "the refused node was corrected"}}]},
        "nb": {"T3": [{"body": {"done": "the house let me through"}}],
               "T4": [{"body": {"done": "framed"}}, {"body": {"done": "framed again"}}]},
        "nc": {"T5": [{"body": {"done": "framed the right node"}}]}})
    launches = T.launcher_witness(bench, h)
    h.declare("nodes", "---\nagents: |\n  na agents/na\n  nb agents/nb\n  nc agents/nc\nreports: |\n"
                       "  nb nc -> na\nroot: na\nparallel: 3\nschedule: off\n---\nHand the nodes.\n")
    opened = h.call("team", "start", "nodes", "--message", "hand the nodes", *h.harnessed)
    posted = h.call("team", "post", "nodes", "--message", "frame the node", "--vector", "refused:t")   # T2, beside T1
    handed = h.settled("nodes", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)

    # --- (h) the task's vector ----------------------------------------------------------------------------
    told = h.settled("nodes", lambda found: bool(by_kind(found, "wake-failed", agent="na", task="T2"))
                     and all_ended(found), timeout=60)
    found = h.events("nodes")
    task = next(iter(by_kind(found, "task", task="T2")), {})
    on_t2 = T.starts(launches, "na-T2-")
    if (opened.returncode == 0 and posted.returncode == 0 and task.get("vectors") == ["refused:t"]
            and len(on_t2) == 1 and T.vectors_on(on_t2[0]) == ["refused:t"]):
        held("(h) the task's vector", "`post --vector refused:t`: the event task T2 carries vectors ['refused:t']; "
             "na's launch line on T2 carries --vector refused:t, read on the launcher's witness")
    else:
        failures.append(f"  ✗ (h) the task's vector         rc={opened.returncode}/{posted.returncode} "
                        f"vectors={task.get('vectors')} lines={[T.vectors_on(one) for one in on_t2]} "
                        f"{posted.stderr.strip()[-200:]!r}")

    # --- (i) two members, two vectors -----------------------------------------------------------------------
    b, c, a = T.starts(launches, "nb-T1-"), T.starts(launches, "nc-T1-"), T.starts(launches, "na-T1-")
    dos = [(one.get("to"), one.get("vector")) for one in by_kind(found, "post", verb="do", task="T1")
           if one.get("from") == "na"]
    if (handed and sorted(dos) == [("nb", "refused:b"), ("nc", "refused:c")] and b and c and a
            and all(T.vectors_on(one) == ["refused:b"] for one in b) and all(T.vectors_on(one) == ["refused:c"] for one in c)
            and all(T.vectors_on(one) == ["-"] for one in a)):
        held("(i) two members, two vectors", f"na's do carries {sorted(dos)}; nb's launch line --vector refused:b "
             f"alone, nc's --vector refused:c alone, na's on T1 ({len(a)} launch(es)) --vector - alone")
    else:
        failures.append(f"  ✗ (i) two members, two vectors  handed={handed} dos={dos} nb={[T.vectors_on(one) for one in b]} "
                        f"nc={[T.vectors_on(one) for one in c]} na={[T.vectors_on(one) for one in a]}")

    # --- (j) the launcher's refusal told to the task, never relaunched ----------------------------------------
    h.call("team", "tick", "nodes")                           # one more tick: nobody is launched again -- a launch
    #                                                           writes its line at the witness inside the tick's call
    found = h.events("nodes")
    refused = {(one.get("agent"), one.get("task")): one for one in by_kind(found, "wake-failed")}
    answered = [one for one in by_kind(found, "post", verb="re", task="T1") if one.get("by") == "tick"]
    again = (len(T.starts(launches, "nb-T1-")), len(T.starts(launches, "nc-T1-")), len(T.starts(launches, "na-T2-")))
    if (told and all(refused.get(slot, {}).get("final") and refused.get(slot, {}).get("house")
                     for slot in (("nb", "T1"), ("nc", "T1"), ("na", "T2")))
            and len(answered) == 2 and T.result_of(found, "T1") == "the nodes were handed" and again == (1, 1, 1)):
        held("(j) the refusal told to the task", f"nb, nc on T1 and na on T2: a final wake-failed of the house "
             f"({refused[('nb', 'T1')].get('reason', '')[:60]!r}); na's two dos answered by the tick, T1 resolved; "
             f"launched once each {again}, a tick later too")
    else:
        failures.append(f"  ✗ (j) the refusal told          told={told} "
                        f"failed={ {slot: (one.get('final'), one.get('house')) for slot, one in refused.items()} } "
                        f"answered={len(answered)} result={T.result_of(found, 'T1')!r} launches={again}")

    # --- (o) the vector comes back in the author's head -----------------------------------------------------------
    module = h.module()
    back = {}                                         # what na's heads hand back to it, by the message's id
    for one in h.prompts_of("na"):
        back.update(T.handed_back(module, one))
    cited = {one.get("re"): one.get("from") for one in answered}
    handed_back = sorted((cited.get(key), one.get("how"), one.get("vector"), one.get("text")) for key, one in back.items())
    if handed_back == [("nb", "failed", "refused:b", "frame b"), ("nc", "failed", "refused:c", "frame c")]:
        held("(o) the vector comes back", f"na's head hands back its two dos answered by the tick: {handed_back}")
    else:
        failures.append(f"  ✗ (o) the vector comes back     back={back} cited={cited}")

    # --- (l) a refusal of the house: not final, relaunched at the next tick ------------------------------------
    busy = h.call("team", "post", "nodes", "--message", "a node the house holds back", "--vector", "busy:t",
                  "--to", "nb")
    corrected = h.call("team", "post", "nodes", "--message", "hand one node, then correct it")       # T4, beside
    after = h.call("team", "post", "nodes", "--message", "hand a node, correct it once refused")    # T5, beside
    h.settled("nodes", lambda found: bool(by_kind(found, "wake-failed", agent="nb", task="T3"))
              and all_ended(found), timeout=60)
    h.call("team", "tick", "nodes")                           # the next tick: nb launched again
    through = h.settled("nodes", lambda found: bool(by_kind(found, "done", task="T3")) and all_ended(found), timeout=60)
    found = h.events("nodes")
    fails = by_kind(found, "wake-failed", agent="nb", task="T3")
    on_t3 = T.starts(launches, "nb-T3-")
    if (busy.returncode == 0 and through and len(fails) == 1 and fails[0].get("final") is False and fails[0].get("house")
            and len(on_t3) == 2 and all(T.vectors_on(one) == ["busy:t"] for one in on_t3)
            and T.result_of(found, "T3") == "the house let me through"):
        held("(l) a refusal of the house", f"nb on T3 refused rc 2 under house-busy: wake-failed final=False of the "
             f"house ({fails[0].get('reason', '')[:50]!r}); the next tick launches it again with --vector busy:t, "
             "T3 resolved")
    else:
        failures.append(f"  ✗ (l) a refusal of the house    rc={busy.returncode} through={through} "
                        f"fails={[(one.get('final'), one.get('house'), one.get('reason')) for one in fails]} "
                        f"lines={[T.vectors_on(one) for one in on_t3]} result={T.result_of(found, 'T3')!r}")

    # --- (m) a corrected do: the new vector alone ------------------------------------------------------------
    done_t4 = h.settled("nodes", lambda found: bool(by_kind(found, "done", task="T4")) and all_ended(found), timeout=60)
    found = h.events("nodes")
    on_t4 = [T.vectors_on(one) for one in T.starts(launches, "nb-T4-")]
    dos = [one.get("vector") for one in by_kind(found, "post", verb="do", task="T4") if one.get("from") == "na"]
    if corrected.returncode == 0 and done_t4 and dos == ["node:1", "node:2"] and on_t4 == [["node:1"], ["node:2"]]:
        held("(m) a corrected do", "na's dos on T4 carry node:1 then node:2; nb's launch lines carry --vector node:1, "
             "then --vector node:2 alone; T4 resolved")
    else:
        failures.append(f"  ✗ (m) a corrected do            rc={corrected.returncode} done={done_t4} dos={dos} "
                        f"lines={on_t4}")

    # --- (n) a do corrected after its refusal: the new vector alone -------------------------------------------
    done_t5 = h.settled("nodes", lambda found: bool(by_kind(found, "done", task="T5")) and all_ended(found), timeout=60)
    found = h.events("nodes")
    on_t5 = [T.vectors_on(one) for one in T.starts(launches, "nc-T5-")]
    fell = [(one.get("final"), one.get("house")) for one in by_kind(found, "wake-failed", agent="nc", task="T5")]
    ended = by_kind(found, "wake-ended", agent="nc")
    if (after.returncode == 0 and done_t5 and fell == [(True, True)] and on_t5 == [["refused:x"], ["node:9"]]
            and T.result_of(found, "T5") == "the refused node was corrected" and ended):
        held("(n) a do corrected after its refusal", "nc on T5: refused:x refused vector-refused, a final failure of "
             "the house; na's corrected do launches nc again with --vector node:9 alone, nc answers, T5 resolved")
    else:
        failures.append(f"  ✗ (n) corrected after refusal   rc={after.returncode} done={done_t5} fell={fell} "
                        f"lines={on_t5} result={T.result_of(found, 'T5')!r}")

    # --- (k) a malformed vector, the team at rest ----------------------------------------------------------------
    before = h.journal_of("nodes").read_text(encoding="utf-8") if h.journal_of("nodes").is_file() else ""
    bare = h.call("team", "post", "nodes", "--message", "a node", "--vector", "bare", "--no-tick")
    after = h.journal_of("nodes").read_text(encoding="utf-8") if h.journal_of("nodes").is_file() else ""
    module = h.module()
    try:
        module.act_formed([{"do": {"nb": {"text": "frame", "vector": "bare"}}}])
        act = ""
    except module.Refused as refusal:
        act = str(refusal)
    try:
        module.act_formed([{"do": {"nb": {"text": "frame", "vector": "refused:b"}}}])
        formed = True
    except module.Refused:
        formed = False
    if (bare.returncode == 2 and "vector-invalid" in bare.stderr and before == after and before
            and "vector-invalid" in act and formed):
        held("(k) a malformed vector refused", f"`post --vector bare` refuses vector-invalid, the journal unchanged; "
             f"a do carrying it refuses: {act[:80]!r}; a do carrying refused:b is formed")
    else:
        failures.append(f"  ✗ (k) a malformed vector         rc={bare.returncode} {bare.stderr.strip()[-200:]!r} "
                        f"unchanged={before == after} act={act!r} formed={formed}")
    return 0
