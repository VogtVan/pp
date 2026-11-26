"""The `tick` domain, layer `model`: what a tick says to the members it wakes, held as plain values.

A definition belongs here when it is data about the tick and does nothing: the lines that open the message of a woken
member -- who it is, a reminder that it owes an answer, a cycle of two members waiting for each other, the exchanges
left, nothing new, a task stopped or closed --, the words the launcher uses for a vector, or a type that carries one of
them. Nothing here reads the disk, the clock or the environment.
"""
from __future__ import annotations

IDENTITY = "[team {team} · you are {member}]"    # the first line of a WAKE-UP's head: who is launched
RELANCED = ("[nothing new arrived for you, and you still owe an answer: send it now, or send an `info` that says "
            "where you stand]")                  # the line a relance's head says why on, for a debt alone
CYCLED = ("[you and {member} each wait for the other's answer: send yours first, or send an `info` that says "
          "where you stand]")                    # the same, for a member in a cycle of waits
BEAT = ("[you owe an answer on {task}. Exchanges left to send the team a message about it, this one included: "
        "{left}. A message is your answer, a question or an `info`. Once they are spent without a message from "
        "you, the team stops waiting for you and answers in your place]")   # the BEAT a wake-up's head says to a
#                                                  member that owes (row 115)
NOTHING_NEW = "[nothing new]"                    # the head of a relaunch of a standing run nothing arrived for
STOPPED_HEAD = "[the task is stopped: say no act, let your run park]"   # the head of the last launch of a run standing on a stopped task
CLOSED_HEAD = "[the task is closed: no act is awaited]"   # the head of a continuation of a run standing on a resolved task
VECTOR_REFUSED = "vector-refused"                  # the launcher's one code for a vector it refuses, at the head of
#                                                  its refusal (`<launcher>: vector-refused -- <the cause>`), rc 2
EMPTIED = "-"                                    # `--vector -`: the launcher's word for a run that keeps no vector
