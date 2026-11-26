"""Scenario `ui-sequence-load` -- the sequence of a long task under the load of its watch (plan pp-fixes, batch
la-sequence-qui-suit-sans-figer): T3's thread of 425 rows and 10 columns, on the bench's `pp-team` witness, the post
played under Textual's pilot at 180x50, `palette.sequence_text` and `palette.sequence_head` counted and the rows the
body draws (`SequenceBody.drawn`) read -- on the Tasks tab, then on the Teams tab, `lead` under the cursor:
- 20 activities of `lead`'s wake-up: no `sequence_text`, the head drawn once each, no row of the body drawn again
- then 1 post: no `sequence_text`, the body drawn once -- the row added and the rows of the cursor --, the head not
  drawn again
- what the view shows is what palette draws: the lines of the body in sight at the end, in the middle and at the top,
  and the head, equal in text and in styles to those of `palette.sequence_text`
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

ACTS = 20
WATCH = ([{"sleep": 5.0}] + [one for n in range(ACTS) for one in ({"sleep": 0.05}, T.lead_act(n))]
         + [{"sleep": 1.0}, T.long_post(T.LONG, "lead", "reviewer")])
PROBE = """
def delta(after, before):
    return after - before if after is not None and before is not None else None


async def probe(app, pilot, view, out):
    out["read"] = await until(pilot, lambda: len(view.shown) >= ROWS)
    out["early"] = app.saw("team:activity")
    await pilot.pause()
    counts, rows = dict(COUNTS), drawn(view)
    out["acted"] = await until(pilot, lambda: app.saw("team:activity") >= %d)
    await pilot.pause()
    await pilot.pause()
    out["activities"] = [COUNTS["text"] - counts["text"], COUNTS["head"] - counts["head"], delta(drawn(view), rows)]
    out["between"] = app.saw("team:post")
    counts, rows = dict(COUNTS), drawn(view)
    out["posted"] = await until(pilot, lambda: app.saw("team:post") >= 1)
    await app.pane_settled()
    await pilot.pause()
    await pilot.pause()
    out["post"] = [COUNTS["text"] - counts["text"], COUNTS["head"] - counts["head"], delta(drawn(view), rows)]
    out["rows"] = len(view.shown)
    out["columns"] = len(view.sequence.columns)
    body = body_of(view)
    for where, y in (("end", None), ("middle", ROWS // 2), ("top", 0)):
        if body is not None:
            body.scroll_end(animate=False) if y is None else body.scroll_to(y=y, animate=False)
        await pilot.pause()
        out[where] = [as_palette(view), round(body.scroll_y) if body is not None else None]
""" % ACTS


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-sequence-load", T.long_script(WATCH))
    panes = ("tasks", "teams")
    for pane, (rc, said, err) in zip(panes, T.piloted(bench, house, "ui-sequence-load", PROBE, *panes)):
        if rc != 0 or not said:
            failures.append(f"  ✗ {pane} probe                 rc={rc} {err[-1500:]!r}")
            continue
        if (not all(said.get(one) for one in ("read", "acted", "posted")) or said.get("early")
                or said.get("rows") != T.LONG + 1 or said.get("columns") != 10):
            failures.append(f"  ✗ {pane} thread                read={said.get('read')} acted={said.get('acted')} "
                            f"posted={said.get('posted')} early={said.get('early')} rows={said.get('rows')} "
                            f"columns={said.get('columns')}")
            continue

        # --- an activity draws the head alone, once ------------------------------------------------------------
        texts, heads, rows = said["activities"]
        if texts == 0 and heads == ACTS and rows == 0:
            held(f"{pane}: an activity draws the head alone", f"{ACTS} activities on {T.LONG} rows: sequence_text "
                 f"{texts}, sequence_head {heads}, rows of the body drawn +{rows}")
        else:
            failures.append(f"  ✗ {pane} activities            sequence_text={texts} sequence_head={heads} "
                            f"drawn={rows} (want 0, {ACTS}, 0)")

        # --- a post draws the body once: the row added and the cursor's -----------------------------------------
        texts, heads, rows = said["post"]
        if texts == 0 and heads == 0 and rows is not None and 1 <= rows <= 3 and said.get("between") == 0:
            held(f"{pane}: a post draws the rows it changed", f"sequence_text {texts}, sequence_head {heads}, rows of "
                 f"the body drawn +{rows}")
        else:
            failures.append(f"  ✗ {pane} post                  sequence_text={texts} sequence_head={heads} "
                            f"drawn={rows} (want 0, 0, 1 to 3); posts before it {said.get('between')} (want 0)")

        # --- what the view shows is what palette draws ----------------------------------------------------------
        sights = {where: said.get(where) or [False, None] for where in ("end", "middle", "top")}
        if all(one[0] for one in sights.values()):
            held(f"{pane}: the view draws palette's lines", "body and head equal to sequence_text in text and styles "
                 f"at scroll {', '.join(f'{where} {one[1]}' for where, one in sights.items())}")
        else:
            failures.append(f"  ✗ {pane} lines                 {sights}")
    return 0
