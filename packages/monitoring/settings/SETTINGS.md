---
name: SETTINGS
kind: fragment
package: monitoring
description: >-
  The monitoring package's own settings. Composed into the instance's SETTINGS
  under the `monitoring_` prefix, read by its skill.
monitoring_capture: false
types: |
  monitoring_capture  one_of[true|false]
---

## Monitoring — the measure, exploited

The package's keys wear the `monitoring_` prefix; `pp-monitoring` reads them by
name at the instance's `SETTINGS.md`.
