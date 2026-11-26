"""The `net` domain, layer `faces`: how the net is put into words -- no definition stands here now.

The face of the net -- its step, whether a timer is armed, whether the relaunch entry stands and why the system refused
it -- reads the timer's mark and the relaunch entry, so it is an act: `schedule_face`, in `net/acts.py`. A face reads
nothing; this module stays for the face of the net that would compose from values alone.
"""
from __future__ import annotations
