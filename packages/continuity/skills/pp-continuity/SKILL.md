---
name: pp-continuity
description: Append operations and weekly digests; read operations by period and digests by count. The local writer of the instance's two continuity records.
---

# `pp-continuity` — record reference

## Entities and lifecycle

The instance keeps two records in its store, the database
`.sys/records/records.db`. A record is created by its first entry; until then
it reads as empty.

| Entity | Record | Body |
|---|---|---|
| Operation | `operations` | `entry` |
| Weekly digest | `history` | `synthesis` |

The store dates each entry when it writes it (`at`, UTC); the reads print that
time to the second, followed by `Z`. `entry` and `synthesis` are text. The script
collapses whitespace to single spaces before storing it. A digest stores its
paragraph and its time; its coverage has no separate field.

This script is the records' only writer. Each successful add appends one entry,
repeated text included; there is no edit or delete verb. Every read is a bounded
query of the store: no verb reads a whole record. Operations print oldest first,
digests newest first.

To find operations by their text, query the record through the console:
`./pp records search '"<exact words>"' --records operations [--since <date|7d>] [--until <date>]`.
Words between double quotes match that exact text; words without quotes must each appear.
`./pp records count operations --match '"<words>"' --group day` counts the matches day by day.
The section "Records — find a fact" of the card gives the other forms.

## Commands

Prefix each form with `./pp <key> -s pp-continuity`:

    ./pp <key> -s pp-continuity recall last 7

| Form | Effect |
|---|---|
| `recall` | The 40 latest operations of the configured recall period, oldest first. When older operations of the period are left, a last line says how many and the call that reads them: `recall last <days> --skip 40`. Silent when the period is empty or the recall is disabled. |
| `recall last <days> [--skip <k>]` | Operations with `at >= now UTC - days`; days is an integer >= 1. ONE page of 40 at most: the 40 latest after the `<k>` latest skipped (none by default), the oldest first. When older operations of the period are left, a last line says how many and the call that reads the next page: `pp-continuity: <m> older operation(s) of the last <days> day(s) left -- read them with recall last <days> --skip <k>.`; a `--skip` at or past the total says `none past the <k> latest`. The skipped operations are passed a bounded page at a time, never by reading the whole period. |
| `register <text...>` | Append one operation; report `consigned --` and its text. |
| `history add <text...>` | Append one digest; report `consigned --` and its first 60 characters. |
| `history add -` | Same append, reading text from stdin. |
| `history last [n]` | The n latest digests, newest first; n is an integer >= 1, default 1. At most `records_read_limit` digests come back (SETTINGS, 100 by default): when more were asked and more exist, a last line says how many were shown out of the total and the bound. |

Reads print the time, then the text. Explicit reads report an empty result with exit 0.
`register -` records a literal hyphen; stdin belongs to `history add -`.

## Effective settings

| Key | Default | Effect |
|---|---:|---|
| `continuity_recall_days` | 7 | Days for bare `recall`; values below 1 silence it. |
| `continuity_entry_budget` | 500 | Maximum characters in a normalized operation. |
| `continuity_digest_budget` | 1500 | Maximum characters in a normalized digest. |

A zero budget lifts its limit. Budgets count characters, not bytes.
The standing orders say when to record an operation; HISTORY says when to write
a digest, on its weekly due. An add tests neither.

## Refusals

Refusals exit 2. Validation before an add writes nothing: empty text, an
exceeded budget, or an unreadable integer setting. The message names the field
or gives the character count and limit.

Reads refuse an invalid day, count or skip argument. A record not written yet
is no refusal: it reads as empty. When the store itself refuses -- the database
still busy after its wait (`store-busy`), or damaged (`store-corrupt`) -- the
script says the store's refusal, code included, and writes nothing. An absent
installed instance refuses. An unsupported command prints usage and exits 2.
