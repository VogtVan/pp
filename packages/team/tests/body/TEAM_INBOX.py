"""packages/team/procs/TEAM_INBOX.md -- the text it keeps: what the `team-inbox` section renders,
in everyday words, and no call -- the gestures live in `pp-team`'s SKILL.md, named by the skill."""
from __future__ import annotations

from tests.harness import SOURCE, body_of, kept_document


def scenario(bench) -> int:
    doc = kept_document(SOURCE / "packages" / "team", "TEAM_INBOX")
    raw = doc.read_text(encoding="utf-8")
    front = raw.split("\n---\n", 1)[0]
    body = body_of(doc)
    text = " ".join(body.split())         # a kept phrase is a sentence, never a line of it

    calls = [line for line in body.splitlines() if "./pp" in line]
    assert not calls, calls
    bench.held("TEAM_INBOX teaches no call", "no line of the body writes ./pp")

    for phrase in ("one line for each team where something waits for the owner",
                   "the questions an agent of the team asked them that nobody has answered yet",
                   "the tasks finished and the messages that came back to them undelivered",
                   "since they last marked their inbox as seen",
                   "When nothing waits in any team, the section is absent",
                   "use the skill `pp-team`"):
        assert phrase in text, phrase
    bench.held("TEAM_INBOX says what its section renders",
               "one line per team, the questions without an answer, the tasks finished and the posts "
               "returned since the inbox was seen, no section when nothing waits; the gestures at pp-team")

    for line in ("mount: turn.begin", "provides: team-inbox", "with: pp-team inbox", "payloads: team-inbox"):
        assert f"\n{line}\n" in f"\n{front}\n", line
    bench.held("TEAM_INBOX keeps its contribution", "mount turn.begin · provides and payloads team-inbox · "
               "with pp-team inbox")
    return 0
