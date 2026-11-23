---
name: KEYS
kind: proc
description: called once at the office's entry; its law stays after it ends.
attach: office.initialize
constraints.production: |
  IN2  you open no door the keys do not open.
proc: |
  INFER
---

List the doors the keys open.
