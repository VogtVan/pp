---
name: pp-continuity
description: Append operations and weekly digests; read operations by period and digests by count. The local writer of the instance's two continuity records.
---

# `pp-continuity` — record reference

## Entities and lifecycle

The instance owns two JSONL records under `.sys/records/`, seeded at install.
Each nonblank line holds one object:

| Entity | File | Fields |
|---|---|---|
| Operation | `operations.jsonl` | `at`, `entry` |
| Weekly digest | `history.jsonl` | `at`, `synthesis` |

`at` is the recording time: ISO 8601 UTC, to the second. `entry` and `synthesis`
are text. The script collapses whitespace to single spaces before storing it.
A digest stores its paragraph and timestamp; its coverage has no separate field.

This local script is the records' writer. Creation appends one object; reading
leaves it in place. There is no edit or delete verb. Each successful add appends,
including repeated text. Reads retain file order, reversed for digests.

## Commands

Prefix each form with `./pp <key> -s pp-continuity`:

    ./pp <key> -s pp-continuity recall last 7

| Form | Effect |
|---|---|
| `recall` | Operations in the configured recall period; silent when empty or disabled. |
| `recall last <days>` | Operations with `at >= now UTC - days`; days is an integer >= 1. |
| `register <text...>` | Append one operation; report `consigned --` and its text. |
| `history add <text...>` | Append one digest; report `consigned --` and its first 60 characters. |
| `history add -` | Same append, reading text from stdin. |
| `history last [n]` | Last n digests in reverse file order; n is an integer >= 1, default 1. |

Reads print `at` then text. Explicit reads report an empty result with exit 0.
`register -` records a literal hyphen; stdin belongs to `history add -`.

## Effective settings

| Key | Default | Effect |
|---|---:|---|
| `continuity_recall_days` | 7 | Days for bare `recall`; values below 1 silence it. |
| `continuity_entry_budget` | 500 | Maximum characters in a normalized operation. |
| `continuity_digest_budget` | 1500 | Maximum characters in a normalized digest. |

A zero budget lifts its limit. Budgets count characters, not bytes.
OPERATIONS and HISTORY describe when to write; their frequency and weekly due
are scheduled outside these commands. An add does not test that schedule.

## Refusals

Refusals exit 2. Validation before an append leaves the file untouched:
empty text, an exceeded budget, or an unreadable integer setting. The message
names the field or gives the character count and limit.

Reads refuse an invalid day/count argument, a missing record, or unparseable
JSON/date or missing fields, naming the line. Missing-record messages point
to `./pp doctor`. Appends create an absent file when its directory exists;
they do not validate earlier lines. An absent installed instance refuses.
An unsupported command prints usage and exits 2.
