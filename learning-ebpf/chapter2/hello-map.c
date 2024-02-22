#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

BPF_HASH(counter_table);

int hello(void *ctx) {
   __u64 uid;
   __u64 counter = 0;
   __u64 *p;

   uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
   p = counter_table.lookup(&uid);
   if (p != 0) {
      counter = *p;
   }
   counter++;
   counter_table.update(&uid, &counter);
   return 0;
}