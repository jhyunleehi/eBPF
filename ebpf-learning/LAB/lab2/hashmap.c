#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

// BPF_HASH 정의
BPF_HASH(ip_pkt_count, u32, u64);

int packet_handler(struct __sk_buff *skb) {
    u32 key = skb->remote_ip4;
    u64 *count = ip_pkt_count.lookup(&key);

    if (count) {
        (*count)++;
    } else {
        u64 new_count = 1;
        ip_pkt_count.update(&key, &new_count);
    }

    return 0;
}