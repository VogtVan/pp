"""execution.judgment -- the judgment: the checkpoint's one regime, the checks of an answer. A mixin of the facade: no state of its own."""
from __future__ import annotations

import json
from ..core import deviation, document as documents, language
from ..state import instance, settings
from ..core.errors import Refusal
from ..core.model import Frame, Instruction, Stack


class Judging:
    """The judgment: the checkpoint's one regime, the checks of an answer -- a mixin of the facade."""

    def _armed(self, frame: Frame) -> bool:
        """-> whether `frame` owes its exit checkpoint: every frame does -- the base
        document, a written CALL, a door the agent opened -- except one a SOCKET
        opened (a contributor at a hook, a cadence): its laws bind its block, and the
        turn's own checkpoint proves the turn. No key arms a document any more.

        documentary: the proof has ONE regime (operator word 2026-09-05) -- owed wherever
        a law of production is in force, in front of each FINAL and at a frame's exit;
        the engine decides, the agent never judges whether to prove. A document that
        still carries a `prove:` key refuses at its opening (`prove-gone`)."""
        if "prove" in frame.document.front:
            raise Refusal("prove-gone",
                          f"{frame.document.name}: `prove:` is gone -- the proof has no "
                          "switch: it is owed wherever a law of production is in force")
        return not (frame.caller is not None and frame.caller.socket)

    def _production_in_force(self, frame: Frame) -> bool:
        """-> whether ONE law of production binds `frame` (its chain and the mounts):
        the proof asks the production laws alone, so none in force means no
        checkpoint at all -- a behavior law binds the block, never the proof."""
        return any(one.section == "production" for one in self._in_force(frame))

    def _exit_due(self, frame: Frame, at_frontier: bool = False) -> bool:
        """-> whether this frame owes a checkpoint NOW: armed (not socket-opened),
        with productions standing unproven since the last played checkpoint and a
        law of production in force -- the one predicate frontier and exit share.
        At a frontier every yield of the frame counts (the FINAL delivers the turn
        under every law on screen); at a frame's EXIT they count only when the
        frame carries a law of production of its OWN -- the law that leaves the
        screen with it: a door's pop proves its laws, a callee under inherited laws
        alone lets its productions go to the frontier where those laws still stand."""
        if not self._armed(frame) or not self._production_in_force(frame):
            return False
        return self._unproven(frame, at_frontier)

    def _own_production(self, frame: Frame) -> bool:
        """-> whether `frame`'s OWN document declares a law of production -- a law
        that LEAVES the screen with the frame, so the exit must prove under it."""
        return any(one.section == "production"
                   for one in documents.constraints(frame.document))

    def _unproven(self, frame: Frame, at_frontier: bool) -> bool:
        """-> whether YIELDING productions stand unproven since the last played
        checkpoint: a played checkpoint clears the slate, any later production
        reopens the debt -- multi-frontier documents prove each segment before ITS
        delivery. At a frame's exit (no frontier) the debt exists only under a law
        of production of the frame's OWN -- the boot's table, a callee's feed, are
        proven by the turn that delivers them, where the inherited laws still stand."""
        if not at_frontier and not self._own_production(frame):
            return False
        fresh = False
        for one in frame.procedure.instructions:
            if one.injected and one.keyword == "PROVE" and one.done:
                fresh = False
                continue
            if (one.done and not one.injected
                    and one.keyword in language.YIELDING and one.given != "off"):
                fresh = True
        return fresh

    def _exit_coming(self, frame: Frame, instruction: Instruction) -> str:
        """-> `obliged` when a checkpoint is CERTAIN to follow `instruction` -- its
        frame's last step, or the step a frontier sits right behind -- '' when
        none will come: the `_exit_due` conditions, one step ahead."""
        if not self._armed(frame) or not self._production_in_force(frame):
            return ""
        at = frame.procedure.instructions.index(instruction)
        following = frame.procedure.instructions[at + 1:at + 2]
        frontier = bool(following) and following[0].keyword == "FINAL"
        if not frontier and not self._own_production(frame):
            return ""
        if instruction.keyword in language.YIELDING or self._unproven(frame, frontier):
            return "obliged"
        return ""

    def _fusion_cap(self, frame: Frame) -> int:
        """-> the yields-per-output cap in force for `frame`'s steps: the document's
        own `fusion:` when declared, the instance's otherwise. 0 = unlimited."""
        declared = frame.document.front.get("fusion")
        if declared is not None:
            return settings.fusion_of(declared)
        return self._settings.fusion

    def _check(self, stack: Stack, frame: Frame, instruction: Instruction,
               answer: str) -> str:
        """-> what the answer missed, or "" when it arrives. One checker per keyword, by name."""
        checker = getattr(self, f"_check_{instruction.keyword.lower()}", None)
        return checker(stack, frame, instruction, answer) if checker else ""

    def _check_pick(self, stack: Stack, frame: Frame, instruction: Instruction,
                    answer: str) -> str:
        return "" if answer in instruction.options else deviation.wrong_answer(instruction, answer)

    def _check_prove(self, stack: Stack, frame: Frame, instruction: Instruction,
                     answer: str) -> str:
        """The proof is machine-checked: valid JSON, the declared shape, the codes AT
        RISK -- at least one, every one a law of production in force; a code unnamed
        is n/a (operator word 2026-09-05: the form spares the 41 % of objects the
        campaigns wrote as n/a) -- and any `fail` verdict reopens the whole document.
        `n/a` says a law without bearing on this production: neither earned nor
        failed, it repairs nothing -- `ok` is reserved for the VERIFIED."""
        try:
            proof = json.loads(answer)
        except ValueError as wrong:
            return f"the PROOF is not one valid JSON value -- {wrong}."
        if (not isinstance(proof, list)
                or not all(isinstance(one, dict) and {"code", "evidence", "verdict"} <= set(one)
                           for one in proof)):
            return ('the PROOF is not a JSON array of {"code", "evidence", "verdict"} '
                    "objects.")
        odd = [one for one in proof if one["verdict"] not in ("ok", "fail", "n/a")]
        if odd:
            return f"a verdict is `ok`, `fail` or `n/a` -- not {odd[0]['verdict']!r}."
        if instruction.refit:
            # the MINI-PROOF: the repaired codes alone come back, verified -- a code
            # failing twice loses the cheap branch, the document replays
            expected = set(instruction.refit)
            if {one["code"] for one in proof} != expected:
                # the ask stands: the mini-proof re-presents, the document never
                # reopens on a coverage slip -- the bound still counts the try
                self._inplace = instruction.refit
                return ("the mini-proof covers exactly the repaired code(s): "
                        f"{', '.join(instruction.refit)}.")
            relapsed = [one for one in proof if one["verdict"] == "fail"]
            instruction.refit = ()
            if relapsed:
                return ("the repaired code failed AGAIN -- the cheap branch closes: "
                        + " · ".join(f"{one['code']}: {one['evidence']}" for one in relapsed))
            return ""
        covered = [one["code"] for one in proof]
        # a behavior law never enters the proof: it binds the block, the judge asks
        # the production laws alone (an object offered for a behavior law is not a miss);
        # a code no law in force carries is a miss -- the proof judges what stands --
        # and a proof naming no law of production proves nothing
        in_force = {one.code: one.section for one in self._in_force(frame)}
        foreign = [code for code in covered if code not in in_force]
        if foreign:
            return f"the PROOF names law(s) not in force: {', '.join(foreign)}."
        if not any(in_force[code] == "production" for code in covered):
            return "the PROOF names no law of production -- the codes at risk, at least one."
        failed = [one for one in proof if one["verdict"] == "fail"]
        if failed:
            fixed = [one for one in failed if str(one.get("fix", "")).strip()]
            if len(fixed) == len(failed):
                # every fail NAMES its fix: the repair plays IN PLACE -- the agent
                # corrects the production and re-proves the failed codes alone
                self._inplace = tuple(one["code"] for one in failed)
                return ("your proof failed and NAMES its fixes -- repair the "
                        "production IN PLACE, then pipe a mini-proof over the failed "
                        "code(s) alone: "
                        + " · ".join(f"{one['code']}: {one['fix']}" for one in failed))
            return ("your own proof failed -- "
                    + " · ".join(f"{one['code']}: {one['evidence']}" for one in failed))
        return ""

    def _check_infer(self, stack: Stack, frame: Frame, instruction: Instruction,
                     answer: str) -> str:
        """A CAPTURED production validates against its format -- the mechanical seed
        of the convergence: `json` must parse; a consumed empty is no production."""
        consumed, _ = self._consumer(stack, frame, instruction)
        if consumed and not answer.strip():
            return "an empty production -- the next step consumes it; hand it over."
        if self._output_of(frame) == "json" and answer.strip():
            try:
                json.loads(answer)
            except ValueError as wrong:
                return f"not one valid JSON value -- {wrong}."
        return ""

    def _owes_proof(self, frame: Frame, wait_at: Instruction) -> bool:
        """-> whether the exchange this FINAL opens carries a PROVE -- said on the
        FINAL's closing, so the agent weighs the proof from the operator's message
        on, not when the proof block arrives. An idle lap (nothing produced) earns
        no checkpoint; with no law of production in force the lap owes nothing, and
        the closing says so."""
        return self._armed(frame) and self._production_in_force(frame)
