---
name: SETTINGS
kind: fragment
package: greeter
description: the greeter's own settings -- one prefixed key, as a package declares them
greeter_word: hello
types: |
  greeter_word  free
---

## Greeter — the witness's word

- `greeter_word` — the word the greeter says; the bench reads it back from the
  composed SETTINGS, in the greeter's own section.
