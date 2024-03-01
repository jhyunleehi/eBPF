#!/usr/bin/python
#
# bitehist.py	Block I/O size histogram.
#		For Linux, uses BCC, eBPF. Embedded C.
#

from __future__ import print_function
from bcc import BPF
from time import sleep

# load BPF program
b = BPF(text="""
#include <uapi/linux/ptrace.h>
#include <linux/blk-mq.h>

BPF_HISTOGRAM(dist);
BPF_HISTOGRAM(dist_linear);

int trace_req_done(struct pt_regs *ctx, struct request *req)
{
    dist.increment(bpf_log2l(req->__data_len / 1024));
    dist_linear.increment(req->__data_len / 1024);
    return 0;
}
""")

if BPF.get_kprobe_functions(b'__blk_account_io_done'):
    b.attach_kprobe(event="__blk_account_io_done", fn_name="trace_req_done")
else:
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

print("\nlinear histogram")
print("~~~~~~~~~~~~~~~~")
b["dist_linear"].print_linear_hist("kbytes")
