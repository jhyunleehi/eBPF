#include <linux/bpf.h>
#include <linux/blk-mq.h>
#include <bpf/bpf_helpers.h>
#include <uapi/linux/ptrace.h>

TRACEPOINT_PROBE(syscalls, sys_enter_clone) {
    // args is from /sys/kernel/debug/tracing/events/random/urandom_read/format
    bpf_trace_printk("%d\\n", args->parent_tidptr);
    return 0;
}