#!/usr/bin/python
#
# bitehist.py	Block I/O size histogram.
#		For Linux, uses BCC, eBPF. Embedded C.
#

from __future__ import print_function
from bcc import BPF
from time import sleep

# load BPF program
prog="""
#include <uapi/linux/ptrace.h>
#include <linux/blk-mq.h>

BPF_HISTOGRAM(dist);
BPF_HISTOGRAM(latency);
BPF_HASH(start, struct request *);


void trace_req_start(struct pt_regs *ctx, struct request *req) {
	// stash start timestamp by request ptr
	u64 ts = bpf_ktime_get_ns();

	start.update(&req, &ts);
}

void trace_req_done(struct pt_regs *ctx, struct request *req){
    u64 *tsp, delta;    
   	tsp = start.lookup(&req);
	if (tsp != 0) {
		delta = bpf_ktime_get_ns() - *tsp;		
        latency.increment(bpf_log2l(delta / 1000000));    
		start.delete(&req);
	} 
    dist.increment(bpf_log2l(req->__data_len / 1024));        
}
"""
b = BPF(text=prog)
b.attach_kprobe(event="blk_mq_start_request", fn_name="trace_req_start")
b.attach_kprobe(event="blk_account_io_merge_bio", fn_name="trace_req_done")

# header
print("Tracing... Hit Ctrl-C to end.")

# trace until Ctrl-C
try:
    sleep(99999999)
except KeyboardInterrupt:
    print()

# output
print("log2 histogram")
print("~~~~~~~~~~~~~~")
b["dist"].print_log2_hist("kbytes")
b["latency"].print_log2_hist("ms")
