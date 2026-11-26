"""The `declaration` domain, layer `faces`: how a declared team is put into words.

A definition belongs here when it turns what a declaration says into the text a user reads, and gives that text
back without printing it. A face reads nothing: the name a team is shown by comes to it as an argument, read by the
verb through the act `team_name`.
"""
from __future__ import annotations


def labelled(shown: str, name: str) -> str:
    """-> how a text says a team: its name `shown` (`team_name`), the directory's name after it when they differ."""
    return name if shown == name else f"{shown} ({name})"
