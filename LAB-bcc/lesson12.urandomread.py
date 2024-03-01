#!/usr/bin/python

from __future__ import print_function
from bcc import BPF
from bcc.utils import printb

# load BPF program
#b = BPF(text="lesson12.urandomread.c")
# load BPF program
b = BPF(text="""
TRACEPOINT_PROBE(syscalls, sys_enter_clone) {
    // args is from /sys/kernel/debug/tracing/events/random/urandom_read/format
    bpf_trace_printk("%d\\n", args->parent_tidptr);
    return 0;
}
""")


# header
print("%-18s %-16s %-6s %s" % ("TIME(s)", "COMM", "PID", "GOTBITS"))

# format output
while 1:
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
    except ValueError:
        continue
    except KeyboardInterrupt:
        exit()
    printb(b"%-18.9f %-16s %-6d %s" % (ts, task, pid, msg))
