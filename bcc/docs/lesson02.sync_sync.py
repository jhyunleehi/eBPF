#!/usr/bin/python
# Copyright (c) PLUMgrid, Inc.
# Licensed under the Apache License, Version 2.0 (the "License")

from bcc import BPF
from bcc.utils import printb

prog="""
int sync(void *cts){
    bpf_trace_printk("sync\\n");
    return 0;
}
"""
b=BPF(text=prog)
b.attach_kprobe(event=b.get_syscall_fnname("sync"), fn_name="sync")
print(f"Tracing sys_sync()... Ctrl-C to end.")

while True:
    try:
        task,pid,cpu,flags,ts,msg=b.trace_fields()
    except ValueError:
        continue
    except KeyboardInterrupt:
        break
    printb(b"%-18.9f %-16s %-6d %s" % (ts, task, pid, msg))
    printb(b"%18.9f %16s %6d %s" % (ts, task, pid, msg))