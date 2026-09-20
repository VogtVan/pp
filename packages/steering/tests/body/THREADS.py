"""packages/steering/procs/THREADS.md -- the text it keeps: the agent's pass over the threads at
every exchange, a WORK step attached to the turn's end that offers the keeper and then opens NEXT
in a fresh output.

The phrases are matched on a whitespace-FLATTENED copy of the body."""
from __future__ import annotations

import re

import yaml

from tests.harness import SOURCE, kept_document


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "steering", "THREADS").read_text(encoding="utf-8")
    front = text.split("---")[1]
    raw_body = text.split("---", 2)[2]
    body = " ".join(raw_body.split())

    assert re.search(r"^attach: turn\.end$", front, re.M)
    assert re.search(r"^tools: \|\n  pp-steering\n", front, re.M)
    assert re.search(r"^proc: \|\n  WORK\n  §\n  CALL NEXT\.md\n", front, re.M)
    bench.held("THREADS is a WORK step at the turn's end", "attached to `turn.end`, it offers "
               "`pp-steering`, and a `§` opens NEXT in a fresh output after the work")

    # a thread is an initiative of the operator's work, a step an action toward its end
    for phrase in ("A thread is an initiative", "the work the operator conducts with you", "with its why",
                   "You propose the initiatives", "one the operator names comes first",
                   "A step states a problem to solve or a result wanted",
                   "born in the initiative it serves",
                   "an action to take or an intermediate result to reach",
                   "one that brings the thread closer to its end",
                   "Keep discussion, findings and reports in the chat"):
        assert phrase in body, phrase
    bench.held("a thread is an initiative", "seen in the operator's work, proposed by the agent, the "
               "operator's own first; a step a problem or a result wanted, an action toward the end")

    # the pass: the table is the agent's to keep for the operator
    for phrase in ("collect and order the work they ask of you",
                   "grouped by initiatives that may cut across one another",
                   "rely on you to do it for them, so that they never have to think about it",
                   "detect the initiatives, break them into steps and follow their progress",
                   "bring forward the most active ones",
                   "reshape and resequence the initiatives when needed",
                   "always deduced from the work you are asked to do",
                   "a unit of work that cannot be skipped",
                   "the initiative that holds it may change",
                   "`pp-steering move` takes it to the initiative it serves",
                   "Organise the work as it best stands through the life of the exchanges",
                   "you keep and organise the work, they supervise it",
                   "start on your own the initiatives that seem relevant to you",
                   "An initiative's note matters", "how urgent it is",
                   "A step's text describes its work and holds what relates it to the other steps",
                   "Keep it up to date from one exchange to the next",
                   "carry out every operation needed with the `pp-steering` skill",
                   "say briefly how you reshaped the threads",
                   "remind the operator of the top thread",
                   "from the texts of its steps"):
        assert phrase in body, phrase
    bench.held("the pass is the agent's", "detect, break into steps, follow; bring the active forward, "
               "reshape from the work asked; start initiatives; keep the notes; say what was reshaped")

    # the laws of the pass: behavior, never proven
    declared = yaml.safe_load(front)
    assert "constraints.production" not in declared
    behavior = declared["constraints.behavior"]
    laws = {line.split()[0]: " ".join(line.split()[1:]) for line in behavior.splitlines() if line.strip()}
    assert sorted(laws) == ["TH1", "TH10", "TH11", "TH2", "TH3", "TH4", "TH5", "TH7", "TH8", "TH9"], sorted(laws)
    for code, phrase in (("TH1", "the information the boot served, when it served them -- never on the "
                                 "threads read again"),
                         ("TH2", "never change or remove a step's key"),
                         ("TH2", "move a keyed step to the initiative it serves"),
                         ("TH3", "close only a thread whose listed steps are all done or dropped, at least one done"),
                         ("TH4", "say every change of the pass in one line, in the operator's language"),
                         ("TH4", "never replay in the session a change the operator undid"),
                         ("TH5", "the threads conduct the OPERATOR: legibility is their first law"),
                         ("TH7", "you keep the threads on your own"),
                         ("TH8", "are their identity"),
                         ("TH9", "a step's text is the memory of its work"),
                         ("TH10", "no unit of work vanishes"),
                         ("TH11", "close the pass on the top thread")):
        assert phrase in laws[code], (code, phrase)
    for absent in ("operator's request", "approval", "permission",
                   "drop a keyed step to create it again"):
        assert absent not in behavior, absent
    bench.held("the pass has its laws", "TH1-TH11 in `constraints.behavior` -- the sources, the key and "
               "the move, the closing and the drop, the line and the undo, the legibility, the hand that "
               "needs no word, the names, the text, what never vanishes and the top thread -- none asks "
               "an agreement, none is proven")

    # what left the body
    for absent in ("Only on the operator's word", "status --all", "braid", "whether it is urgent",
                   "carry each one into that thread", "At every exchange, without asking",
                   "Do not open a thread per plan", "informations"):
        assert absent not in body, absent
    for absent in ("confederation", "@<member>", "plan:", "lot:", "next move", "trivial"):
        assert absent not in body.lower(), absent
    bench.held("the base names no client", f"{len(raw_body)} c of body, no plan, improvement or "
               "federation vocabulary; the former list of verbs and the braid are gone")
    return 0
