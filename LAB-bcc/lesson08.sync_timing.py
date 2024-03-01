#!/usr/bin/python

from __future__ import print_function
from bcc import BPF
from bcc.utils import printb


prog="""
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

BPF_HASH(last);

struct data_t {
    int pid;
    int uid;
    u64 ts;
    u64 delta;
    char comm[TASK_COMM_LEN];
};

BPF_PERF_OUTPUT(events);

int do_trace(struct pt_regs *ctx) {
    u64 ts, *tsp, delta, key = 0;
    
    struct data_t data={};
    data.pid = bpf_get_current_pid_tgid() >> 32;
    data.uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
    data.ts=bpf_ktime_get_ns();
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    
    // attempt to read stored timestamp
    tsp = last.lookup(&key);
    if (tsp != NULL) {
        data.delta = bpf_ktime_get_ns() - *tsp;                    
        //bpf_trace_printk("%d\\n", delta / 1000000);
        events.perf_submit(ctx, &data, sizeof(data));         
        last.delete(&key);
    }

    // update stored timestamp
    ts = bpf_ktime_get_ns();
    last.update(&key, &ts);
    return 0;
}
"""
b = BPF(text=prog)
b.attach_kprobe(event=b.get_syscall_fnname("sync"), fn_name="do_trace")
print("Tracing for quick sync's... Ctrl-C to end")

# format output
start = 0
def print_event(cpu, data, size):
    global start
    event = b["events"].event(data)
    if start == 0:
        start = event.ts
    time_s = (float(event.ts - start)) / 1000000000
    printb(b"[%-18.9f] [%-6d] [%-6d] [%-6d] [%s]" % (time_s, event.pid, event.uid, event.delta, event.comm))
    #printb(b"%-18.9f %-16s %-6d %s" % (time_s, event.comm, event.pid, b"Hello, perf_output!"))

# loop with callback to print_event
b["events"].open_perf_buffer(print_event)
while 1:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        exit()