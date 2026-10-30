---
name: TAGGED
kind: proc
description: rows of tokens with blanks, cut between two tags.
serve: |
  GLOSSARY.md[draft --..finding --] NOTES.md
  GLOSSARY.md[draft --..finding --]
  GLOSSARY.md[nowhere --..finding --]
  GLOSSARY.md[draft --..nowhere --]
proc: |
  SERVE
  SERVE GLOSSARY.md[..draft --]
  INFER
---

Read the words between the tags.
