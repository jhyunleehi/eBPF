#!/usr/bin/python
#
# sync_timing.py    Trace time between syncs.
#                   For Linux, uses BCC, eBPF. Embedded C.
#
# Written as a basic example of tracing time between events.
#
# Copyright 2016 Netflix, Inc.
# Licensed under the Apache License, Version 2.0 (the "License")

from __future__ import print_function
from bcc import BPF
from bcc.utils import printb

# load BPF program
b = BPF(text="""
#include <uapi/linux/ptrace.h>

BPF_HASH(last);

int do_trace(struct pt_regs *ctx) {
    u64 ts, *tsp, delta,  *cnt, count;
    u64  key1 = 0, key2=1;

    // attempt to read stored timestamp
    tsp = last.lookup(&key1);
    if (tsp != NULL) {
        cnt = last.lookup(&key2);
        if (cnt == NULL){
            count=1;
            last.update(&key2, &count);    
        } else {
            count=*cnt+1;
            last.update(&key2, &count);    
        }
        delta = bpf_ktime_get_ns() - *tsp;             
        bpf_trace_printk("[%d] ms age [%d] count \\n", delta / 1000000 , count);
        last.delete(&key1);
    }    
    // update stored timestamp
    ts = bpf_ktime_get_ns();
    last.update(&key1, &ts);
    return 0;
}
""")

b.attach_kprobe(event=b.get_syscall_fnname("sync"), fn_name="do_trace")
print("Tracing for quick sync's... Ctrl-C to end")

# format output
start = 0
while 1:
    try:
        (task, pid, cpu, flags, ts, ms) = b.trace_fields()
        if start == 0:
            start = ts
        ts = ts - start
        printb(b"At time %.2f s: multiple syncs detected, last %s" % (ts, ms))
    except KeyboardInterrupt:
        exit()
