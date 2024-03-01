#!/usr/bin/python

from __future__ import print_function
from bcc import BPF
from bcc.utils import printb

REQ_WRITE = 1		# from include/linux/blk_types.h

# load BPF program
prog="""
#include <uapi/linux/ptrace.h>
#include <linux/blk-mq.h>

BPF_HASH(start, int);

TRACEPOINT_PROBE(block,block_rq_issue) {
	// stash start timestamp by request ptr
	u64 ts = bpf_ktime_get_ns();
	//start.update(args->common_pid, &ts);
    u32 dev = args->dev;
    u64 sector = args->sector;
    u32 nr_sector = args->nr_sector;
    bpf_trace_printk("rq_issue [%u] [%llu] [%u]\\n",dev, sector, nr_sector);
	return 0;
}

TRACEPOINT_PROBE(block,block_rq_complete) {
	u64 *tsp, delta;
	//tsp = start.lookup(args->common_pid);
    u32 dev = args->dev;
    u64 sector = args->sector;
    u32 nr_sector = args->nr_sector;
    bpf_trace_printk("rq_complete [%u] [%llu] [%u]\\n",dev, sector, nr_sector);
    /* 
	if (tsp != 0) {
		delta = bpf_ktime_get_ns() - *tsp;
		//bpf_trace_printk("%d %c %d\\n", args->common_pid, args->common_flags, delta / 1000);
  		bpf_trace_printk("[%d]\\n", delta / 1000);
		start.delete(args->common_pid);
	}
    */
	return 0;
}
"""
b=BPF(text=prog)
# header
print("%-18s %-2s %-7s %8s" % ("TIME(s)", "T", "BYTES", "LAT(ms)"))

b.trace_print()

# format output
while 1:
	try:
		(id, dev, sector, nr_sector) = b.trace_fields()		
	
		print(id, dev, sector, nr_sector)
	except KeyboardInterrupt:
		exit()
