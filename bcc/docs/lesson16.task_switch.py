#!/usr/bin/python
# Copyright (c) PLUMgrid, Inc.
# Licensed under the Apache License, Version 2.0 (the "License")

from bcc import BPF
from time import sleep

b = BPF(src_file="lesson16.task_switch.c")
b.attach_kprobe(event="finish_task_switch.isra.0", fn_name="count_sched")
#b.attach_kprobe(event="finish_task_reaping", fn_name="count_sched")

# generate many schedule events
for i in range(0, 100): sleep(0.1)

for k, v in b["stats"].items():
    print("task_switch[%5d->%5d]=%u" % (k.prev_pid, k.curr_pid, v.value))
